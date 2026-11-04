"""Canonical descriptive pipeline; no campaign or causal effect is estimated."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAX_EXACT_INTEGER = 2 ** 53 - 1  # Float-parsed IDs/quantities must remain exactly representable.
RAW_COLUMNS = ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID', 'Country']

def load_config(path=None):
    cfg = json.loads(Path(path or ROOT / 'analysis/config.json').read_text())
    if not (0 < cfg['active_days'] < cfg['dormant_days']):
        raise ValueError('Require 0 < active_days < dormant_days')
    if cfg['repeat_window_days'] != 90:
        raise ValueError('This documented release supports the 90-day repeat metric')
    if cfg['score_quantiles'] != [.2, .4, .6, .8]:
        raise ValueError('This release defines quintile scores using .2/.4/.6/.8')
    if not 0 < cfg['credit_review_ratio'] <= 1:
        raise ValueError('Require credit_review_ratio in (0, 1]')
    if not (1 <= cfg['high_value_min_m_score'] <= 5 and 1 <= cfg['frequent_min_f_score'] <= 5):
        raise ValueError('Score thresholds must be in 1..5')
    return cfg

def read_input(path):
    return pd.read_csv(path, dtype={'Invoice': 'string', 'StockCode': 'string', 'Country': 'string'}, low_memory=False)

def clean_transactions(raw, *, retain_exact_duplicates=False):
    missing = set(RAW_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    d = raw[RAW_COLUMNS].copy()
    if d.empty:
        raise ValueError('Input has no rows')
    # Parse explicitly; invalid values are counted and excluded, never invented.
    d['Invoice'] = d.Invoice.astype('string').str.strip()
    d['StockCode'] = d.StockCode.astype('string').str.strip()
    original = d.copy()
    for col in ['Quantity', 'Price', 'Customer ID']:
        d[col] = pd.to_numeric(d[col], errors='coerce')
    date_text = d.InvoiceDate.astype('string')
    iso_date = date_text.str.match(r'^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?)?$', na=False)
    d['InvoiceDate'] = pd.to_datetime(date_text.where(iso_date), format='mixed', errors='coerce')
    if d.InvoiceDate.dt.tz is not None:
        raise ValueError('Expected source-local naive timestamps; timezone-aware input needs an explicit conversion policy')
    valid_dates = d.InvoiceDate.dropna()
    if valid_dates.empty:
        raise ValueError('No valid timestamp available')
    observation_start, observation_end = valid_dates.min(), valid_dates.max()
    d['LineValueGBP'] = d.Quantity * d.Price
    finite = np.isfinite(d[['Quantity', 'Price', 'Customer ID']].astype(float)).all(axis=1)
    cancelled = d.Invoice.str.upper().str.startswith('C', na=False)
    flags = {
        'Missing customer ID': d['Customer ID'].isna(),
        'Invalid customer ID': d['Customer ID'].notna() & ((d['Customer ID'] <= 0) | (d['Customer ID'] % 1 != 0) | (d['Customer ID'] > MAX_EXACT_INTEGER)),
        'Invalid required value/date/key': ~finite | d.InvoiceDate.isna() | d.Invoice.isna() | d.Invoice.eq('') | d.StockCode.isna() | d.StockCode.eq(''),
        'Zero/noninteger quantity': d.Quantity.eq(0) | d.Quantity.mod(1).ne(0) | d.Quantity.abs().gt(MAX_EXACT_INTEGER),
        'Nonpositive price': d.Price.le(0),
        'Inconsistent credit sign': ~((~cancelled & d.Quantity.gt(0)) | (cancelled & d.Quantity.lt(0))),
        'Exact duplicate raw rows': original.duplicated(),
    }
    quality = [{'Check': k, 'Count': int(v.fillna(True).sum()), 'Meaning': 'Overlapping input flag; do not sum as removals'} for k, v in flags.items()]
    for col in ['Quantity', 'Price', 'Customer ID', 'InvoiceDate']:
        failed = original[col].notna() & d[col].isna()
        quality.append({'Check': f'Parsing failures: {col}', 'Count': int(failed.sum()), 'Meaning': 'Nonblank source value failed parsing'})
    quality.append({'Check': 'Missing Description', 'Count': int(d.Description.isna().sum()), 'Meaning': 'Allowed: description is not used to infer buying behaviour'})
    ledger = []
    def state(stage, x):
        return {'Stage': stage, 'RowsAfter': len(x), 'SignedValueAfterGBP': float(x.LineValueGBP.sum()),
                'UnpricedRowsAfter': int(x.LineValueGBP.isna().sum())}
    ledger.append(dict(state('Raw parsed', d), RowsRemoved=0, SignedValueRemovedGBP=0.0))
    # Count mutually exclusive sequential removals; duplicates use the eight raw fields.
    keep = pd.Series(True, index=d.index)
    for name, bad in flags.items():
        if name == 'Exact duplicate raw rows' and retain_exact_duplicates:
            bad = pd.Series(False, index=d.index)
        before = d.loc[keep]
        removed = keep & bad.fillna(True)
        keep &= ~bad.fillna(True)
        row = state(name, d.loc[keep])
        row.update(RowsRemoved=int(removed.sum()), SignedValueRemovedGBP=float(d.loc[removed, 'LineValueGBP'].sum()))
        ledger.append(row)
    signed = d.loc[keep].copy()
    signed['Customer ID'] = signed['Customer ID'].astype('int64')
    purchases = signed.loc[signed.Quantity > 0].copy()
    credits = signed.loc[signed.Quantity < 0].copy()
    if purchases.empty:
        raise ValueError('No valid positive purchase lines remain; no successful outputs published')
    if purchases.groupby('Invoice')['Customer ID'].nunique().gt(1).any():
        raise ValueError('Purchase invoice assigned to multiple customers')
    span = purchases.groupby(['Customer ID', 'Invoice']).InvoiceDate.agg(['min', 'max'])
    if ((span['max'].dt.normalize() - span['min'].dt.normalize()).dt.days > 0).any():
        raise ValueError('Invoice spans multiple calendar dates; reconcile invoice identity before aggregation')
    quality.append({'Check': 'Invoices with multiple within-day timestamps', 'Count': int(span['min'].ne(span['max']).sum()), 'Meaning': 'Earliest timestamp defines order; all lines retained'})
    return purchases, credits, signed, pd.DataFrame(ledger), pd.DataFrame(quality), observation_start, observation_end

def stable_score(values, quantiles, reverse=False):
    """Equal raw values always get equal scores. Ties go to the lower ascending bin."""
    cutoffs = values.quantile(quantiles).to_numpy(dtype=float)
    ascending = 1 + (values.to_numpy()[:, None] > cutoffs).sum(axis=1)
    return pd.Series(6 - ascending if reverse else ascending, index=values.index, dtype=int), cutoffs

def rfm_segment(r, f, m):
    if r >= 4 and f >= 4 and m >= 4: return 'Champions (relative)'
    if r >= 3 and f >= 4: return 'Recent frequent'
    if r >= 4 and f in (2, 3): return 'Recent mid-frequency'
    if r >= 4 and f == 1: return 'Recent low-frequency'
    if r <= 2 and f >= 3: return 'Lapsed frequent'
    if r <= 2 and f <= 2: return 'Lapsed low-frequency'
    return 'Intermediate'

def assign_actions(customers, cfg):
    c = customers.copy()
    rec, orders = c.RecencyDays, c.Orders
    c['Lifecycle'] = np.select(
        [(rec <= cfg['active_days']) & (orders == 1), (rec <= cfg['active_days']) & (orders >= 2),
         (rec > cfg['active_days']) & (rec <= cfg['dormant_days'])],
        ['Recent single-order', 'Active repeat', 'At risk'], default='Dormant')
    c['ValueTier'] = np.select([c.M_Score >= cfg['high_value_min_m_score'], c.M_Score >= 3],
                               ['Higher recorded value', 'Middle recorded value'], default='Lower recorded value')
    c['CreditReviewRequired'] = (c.NetRecordedValueGBP <= 0) | (c.CreditToGrossRatio >= cfg['credit_review_ratio'])
    def action(row):
        if row.CreditReviewRequired: return 'Review credits before outreach'
        if row.Lifecycle == 'Recent single-order': return 'Second-order journey test'
        high = row.ValueTier == 'Higher recorded value'
        frequent = row.F_Score >= cfg['frequent_min_f_score']
        if row.Lifecycle == 'Active repeat':
            if row['RFM Segment'] == 'Champions (relative)' and high and frequent: return 'Protect frequent higher-value'
            if high: return 'Develop higher-value repeat'
            return 'Develop repeat relationship'
        if row.Lifecycle == 'At risk':
            if high and frequent: return 'Win-back frequent higher-value test'
            if high: return 'Win-back higher-value test'
            return 'Lower-cost win-back test'
        return 'Review dormant higher-value' if high else 'Lower-cost dormant test'
    c['CRM Priority'] = c.apply(action, axis=1)
    c['ContactReady'] = False
    c['AudienceStatus'] = 'Historical test hypothesis; consent/contact/margin checks required'
    return c

def build_customers(purchases, credits, observation_end, cfg):
    orders = purchases.groupby(['Customer ID', 'Invoice'], as_index=False).agg(
        OrderDate=('InvoiceDate', 'min'), OrderGrossValueGBP=('LineValueGBP', 'sum'),
        Lines=('Invoice', 'size'), LastLineTimestamp=('InvoiceDate', 'max'))
    orders = orders.sort_values(['Customer ID', 'OrderDate', 'Invoice']).reset_index(drop=True)
    orders['OrderNumber'] = orders.groupby('Customer ID').cumcount() + 1
    c = orders.groupby('Customer ID', as_index=False).agg(
        FirstObservedPurchase=('OrderDate', 'min'), LastObservedPurchase=('OrderDate', 'max'),
        Orders=('Invoice', 'size'), GrossPurchaseValueGBP=('OrderGrossValueGBP', 'sum'))
    purchase_days = orders.assign(Day=orders.OrderDate.dt.normalize()).groupby('Customer ID').Day.nunique()
    c['PurchaseDays'] = c['Customer ID'].map(purchase_days)
    credit_values = -credits.groupby('Customer ID').LineValueGBP.sum()
    c['CreditValueGBP'] = c['Customer ID'].map(credit_values).fillna(0)
    c['NetRecordedValueGBP'] = c.GrossPurchaseValueGBP - c.CreditValueGBP
    c['CreditToGrossRatio'] = c.CreditValueGBP / c.GrossPurchaseValueGBP
    c['AverageGrossOrderValueGBP'] = c.GrossPurchaseValueGBP / c.Orders
    snapshot = observation_end.normalize() + pd.Timedelta(days=1)
    c['RecencyDays'] = (snapshot - c.LastObservedPurchase.dt.normalize()).dt.days
    c['ObservedTenureDays'] = (observation_end - c.FirstObservedPurchase).dt.total_seconds() / 86400
    c['RepeatCustomer'] = c.Orders >= 2
    c['RepeatOnAnotherDay'] = c.PurchaseDays >= 2
    second = orders.loc[orders.OrderNumber == 2, ['Customer ID', 'OrderDate']].rename(columns={'OrderDate': 'SecondObservedPurchase'})
    c = c.merge(second, on='Customer ID', how='left', validate='one_to_one')
    delta = c.SecondObservedPurchase - c.FirstObservedPurchase
    c['DaysToSecondOrder'] = delta.dt.total_seconds() / 86400
    c['Eligible90'] = c.FirstObservedPurchase + pd.Timedelta(days=cfg['repeat_window_days']) <= observation_end
    c['SecondOrderWithin90'] = delta.le(pd.Timedelta(days=cfg['repeat_window_days'])) & c.Eligible90
    first_later_day = orders.merge(c[['Customer ID', 'FirstObservedPurchase']], on='Customer ID', validate='many_to_one')
    first_later_day = first_later_day.loc[first_later_day.OrderDate.dt.normalize() > first_later_day.FirstObservedPurchase.dt.normalize()].groupby('Customer ID').OrderDate.min()
    c['NextPurchaseDayTimestamp'] = c['Customer ID'].map(first_later_day)
    c['AnotherPurchaseDayWithin90'] = c.Eligible90 & (c.NextPurchaseDayTimestamp - c.FirstObservedPurchase).le(pd.Timedelta(days=90))
    cutoff_rows = []
    for name, field, reverse in [('R', 'RecencyDays', True), ('F', 'Orders', False), ('M', 'NetRecordedValueGBP', False)]:
        c[name + '_Score'], thresholds = stable_score(c[field], cfg['score_quantiles'], reverse)
        for q, threshold in zip(cfg['score_quantiles'], thresholds):
            cutoff_rows.append({'Dimension': name, 'RawField': field, 'Quantile': q, 'Cutoff': threshold,
                                'TieRule': 'Ascending bin uses value > cutoff; equal stays lower; R = 6 - ascending'})
    c['RFM_Score'] = c[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)
    c['RFM_Profile'] = c[['R_Score', 'F_Score', 'M_Score']].astype(str).agg(''.join, axis=1)
    c['RFM Segment'] = [rfm_segment(r, f, m) for r, f, m in c[['R_Score', 'F_Score', 'M_Score']].itertuples(index=False, name=None)]
    c['FirstObservedCohort'] = c.FirstObservedPurchase.dt.to_period('M').astype(str)
    # Equal 365-day exposure window is a context check, not an annualised CLV model.
    recent_start = snapshot - pd.Timedelta(days=365)
    recent_orders = orders.loc[orders.OrderDate >= recent_start].groupby('Customer ID').size()
    c['OrdersLast365Days'] = c['Customer ID'].map(recent_orders).fillna(0).astype(int)
    signed_recent = pd.concat([purchases, credits]).loc[lambda x: x.InvoiceDate >= recent_start].groupby('Customer ID').LineValueGBP.sum()
    c['NetRecordedValueLast365DaysGBP'] = c['Customer ID'].map(signed_recent).fillna(0)
    return orders, assign_actions(c, cfg), pd.DataFrame(cutoff_rows), snapshot

def cohort_analysis(orders, start, end, cfg):
    o = orders.copy()
    o['OrderMonth'] = o.OrderDate.dt.to_period('M')
    first = o.groupby('Customer ID').OrderMonth.min()
    o['CohortMonth'] = o['Customer ID'].map(first)
    o['CohortIndex'] = o.OrderMonth.astype('int64') - o.CohortMonth.astype('int64')
    observed = o.groupby(['CohortMonth', 'CohortIndex'])['Customer ID'].nunique().unstack(fill_value=0).sort_index()
    max_age = max(cfg['max_heatmap_month'], int(o.CohortIndex.max()))
    counts = observed.reindex(columns=range(max_age + 1), fill_value=0).astype(float)
    # Conservative source completeness: final transaction month is excluded.
    last_complete = end.to_period('M') - 1
    first_complete = start.to_period('M') + (0 if start.day == 1 else 1)
    for cohort in counts.index:
        for age in counts.columns:
            if cohort < first_complete or cohort + int(age) > last_complete:
                counts.loc[cohort, age] = np.nan
    retention = counts.div(counts[0], axis=0)
    rows = []
    for age in cfg['retention_months']:
        eligible = counts[age].notna() & counts[0].notna()
        denom, num = int(counts.loc[eligible, 0].sum()), int(counts.loc[eligible, age].sum())
        rows.append({'Month': age, 'EligibleCohorts': int(eligible.sum()), 'EligibleCustomers': denom,
                     'ActiveCustomers': num, 'WeightedRetentionRate': num / denom if denom else np.nan})
    return counts, retention, pd.DataFrame(rows), observed, str(last_complete)

def summarize(customers, grouping):
    summary = customers.groupby(grouping, as_index=False, dropna=False).agg(
        Customers=('Customer ID', 'size'), GrossPurchaseValueGBP=('GrossPurchaseValueGBP', 'sum'),
        CreditValueGBP=('CreditValueGBP', 'sum'), NetRecordedValueGBP=('NetRecordedValueGBP', 'sum'),
        AverageRecencyDays=('RecencyDays', 'mean'), AverageOrders=('Orders', 'mean'),
        MedianObservedTenureDays=('ObservedTenureDays', 'median'))
    summary['CustomerSharePct'] = summary.Customers / len(customers) * 100
    summary['GrossValueSharePct'] = summary.GrossPurchaseValueGBP / customers.GrossPurchaseValueGBP.sum() * 100
    return summary.sort_values(['GrossPurchaseValueGBP', grouping], ascending=[False, True]).reset_index(drop=True)

def analyse(raw, cfg):
    purchases, credits, signed, cleaning, quality, start, end = clean_transactions(raw)
    orders, c, cutoffs, snapshot = build_customers(purchases, credits, end, cfg)
    # Every CLI/notebook refresh must recreate this sensitivity artifact.
    alt_p, alt_cr, *_ = clean_transactions(raw, retain_exact_duplicates=True)
    _, alt_c, _, _ = build_customers(alt_p, alt_cr, end, cfg)
    comparison = alt_c.merge(c[['Customer ID', 'CRM Priority']], on='Customer ID',
                            suffixes=('_alternative', '_base'), validate='one_to_one')
    require(len(comparison) == len(c) == len(alt_c), 'duplicate sensitivity population')
    duplicate_sensitivity = pd.DataFrame([{
        'Scenario': 'Retain exact duplicate rows', 'PurchaseLines': len(alt_p),
        'BasePurchaseLines': len(purchases),
        'GrossPurchaseValueGBP': float(alt_c.GrossPurchaseValueGBP.sum()),
        'BaseGrossPurchaseValueGBP': float(c.GrossPurchaseValueGBP.sum()),
        'NetRecordedValueGBP': float(alt_c.NetRecordedValueGBP.sum()),
        'BaseNetRecordedValueGBP': float(c.NetRecordedValueGBP.sum()),
        'CustomersWithChangedAction': int(comparison['CRM Priority_alternative'].ne(comparison['CRM Priority_base']).sum())
    }])
    counts, retention, rkpis, observed_counts, last_complete = cohort_analysis(orders, start, end, cfg)
    eligible = c.loc[c.Eligible90]
    n, k = len(eligible), int(eligible.SecondOrderWithin90.sum())
    cohort90 = c.groupby('FirstObservedCohort', as_index=False).agg(Customers=('Customer ID', 'size'), EligibleCustomers=('Eligible90', 'sum'), SecondOrderCustomers=('SecondOrderWithin90', 'sum'))
    cohort90['Repeat90Rate'] = cohort90.SecondOrderCustomers.div(cohort90.EligibleCustomers.replace(0, np.nan))
    curve = pd.DataFrame([{'Day': day, 'EligibleCustomers': n, 'SecondOrderCustomers': int(eligible.DaysToSecondOrder.le(day).sum()),
                           'CumulativeRepeatRate': float(eligible.DaysToSecondOrder.le(day).sum()) / n if n else np.nan}
                          for day in cfg['repeat_curve_days']])
    fixed_window = c.assign(TenureBand=pd.cut(c.ObservedTenureDays, [-1, 90, 365, np.inf], labels=['0-90 days', '>90-365 days', '>365 days']))
    tenure = fixed_window.groupby('TenureBand', observed=True, as_index=False).agg(Customers=('Customer ID', 'size'), MeanAllHistoryOrders=('Orders', 'mean'), MeanLast365DayOrders=('OrdersLast365Days', 'mean'), MedianAllHistoryNetGBP=('NetRecordedValueGBP', 'median'), MedianLast365DayNetGBP=('NetRecordedValueLast365DaysGBP', 'median'))
    sensitivity = []
    variants = [('base', cfg['active_days'], cfg['dormant_days'], cfg['high_value_min_m_score'], cfg['credit_review_ratio']),
                ('shorter lifecycle', 60, 120, 4, .5), ('longer lifecycle', 120, 240, 4, .5),
                ('higher value stricter', 90, 180, 5, .5), ('credit review earlier', 90, 180, 4, .25), ('credit review later', 90, 180, 4, .75)]
    for variant, active, dormant, m, ratio in variants:
        alt = dict(cfg, active_days=active, dormant_days=dormant, high_value_min_m_score=m, credit_review_ratio=ratio)
        cc = assign_actions(c, alt)
        sensitivity.append({'Variant': variant, 'ActiveDays': active, 'DormantDays': dormant, 'HighValueMinMScore': m, 'CreditReviewRatio': ratio,
                            'ChangedActions': int(cc['CRM Priority'].ne(c['CRM Priority']).sum()), 'AtRiskCustomers': int(cc.Lifecycle.eq('At risk').sum()),
                            'CreditReviewCustomers': int(cc.CreditReviewRequired.sum()), 'HigherValueCustomers': int(cc.ValueTier.eq('Higher recorded value').sum())})
    value_ledger = pd.DataFrame([
        {'Metric': 'Signed identified value (purchase and credit-only customers)', 'GBP': float(signed.LineValueGBP.sum())},
        {'Metric': 'Gross purchases of analysed customers', 'GBP': float(c.GrossPurchaseValueGBP.sum())},
        {'Metric': 'Credits of analysed customers', 'GBP': float(c.CreditValueGBP.sum())},
        {'Metric': 'Net recorded value of analysed customers', 'GBP': float(c.NetRecordedValueGBP.sum())},
        {'Metric': 'Credit-only customer signed value (excluded from purchase population)', 'GBP': float(credits.loc[~credits['Customer ID'].isin(c['Customer ID']), 'LineValueGBP'].sum())}])
    stats = {'version': cfg['version'], 'raw_rows': len(raw), 'purchase_lines': len(purchases), 'credit_lines': len(credits),
             'orders': len(orders), 'customers': len(c), 'gross_purchase_value_gbp': float(c.GrossPurchaseValueGBP.sum()),
             'credit_value_gbp': float(c.CreditValueGBP.sum()), 'net_recorded_value_gbp': float(c.NetRecordedValueGBP.sum()),
             'repeat_customer_rate': float(c.RepeatCustomer.mean()), 'repeat_another_day_rate': float(c.RepeatOnAnotherDay.mean()),
             'eligible90_customers': n, 'second_order90_customers': k, 'repeat90_rate': k / n if n else None,
             'another_day90_rate': float(eligible.AnotherPurchaseDayWithin90.mean()) if n else None,
             'median_days_to_second_among_repeaters': float(c.DaysToSecondOrder.median()) if c.RepeatCustomer.any() else None,
             'credit_review_customers': int(c.CreditReviewRequired.sum()), 'observation_start': str(start), 'observation_end': str(end),
             'snapshot_date': str(snapshot.date()), 'last_complete_month': last_complete, 'currency': 'GBP', 'timestamp_timezone': 'source-local naive; timezone unspecified'}
    tables = {'purchase_lines': purchases, 'credit_lines': credits, 'orders': orders, 'customer_lifecycle_table': c, 'cleaning_reconciliation': cleaning, 'data_quality_summary': quality,
              'value_reconciliation': value_ledger, 'rfm_cutoffs': cutoffs, 'rfm_segment_summary': summarize(c, 'RFM Segment'),
              'lifecycle_summary': summarize(c, 'Lifecycle'), 'crm_priority_summary': summarize(c, 'CRM Priority'),
              'retention_kpis': rkpis, 'repeat_90_by_cohort': cohort90, 'repeat_90_curve': curve, 'tenure_context': tenure,
              'rule_sensitivity': pd.DataFrame(sensitivity), 'duplicate_sensitivity': duplicate_sensitivity,
              'rfm_lifecycle_crosswalk': c.groupby(['RFM Segment', 'Lifecycle', 'ValueTier', 'CRM Priority'], as_index=False).agg(Customers=('Customer ID', 'size'))}
    validate_results(tables, counts, retention, stats, cfg)
    return tables, counts, retention, observed_counts, stats

def require(condition, message):
    if not condition: raise ValueError('Validation failed: ' + message)

def validate_results(tables, counts, retention, stats, cfg):
    c, orders, ledger = tables['customer_lifecycle_table'], tables['orders'], tables['cleaning_reconciliation']
    tol = cfg['money_tolerance_gbp']
    require(c['Customer ID'].is_unique, 'customer key')
    require(not orders.duplicated(['Customer ID', 'Invoice']).any(), 'order key')
    require(int(c.Orders.sum()) == len(orders), 'customer/order counts')
    require(abs(c.GrossPurchaseValueGBP.sum() - orders.OrderGrossValueGBP.sum()) <= tol, 'gross customer/order conservation')
    require(ledger.RowsRemoved.sum() + ledger.iloc[-1].RowsAfter == stats['raw_rows'], 'row reconciliation')
    require(abs(ledger.iloc[0].SignedValueAfterGBP - ledger.iloc[-1].SignedValueAfterGBP - ledger.SignedValueRemovedGBP.sum()) <= tol, 'signed cleaning value reconciliation')
    values = tables['value_reconciliation'].GBP.to_numpy()
    require(abs(values[0] - values[3] - values[4]) <= tol and abs(values[1] - values[2] - values[3]) <= tol, 'credit-only/value bridge')
    for field in ['R_Score', 'F_Score', 'M_Score']:
        require(c[field].between(1, 5).all(), 'score bounds ' + field)
    for raw_field, score in [('RecencyDays', 'R_Score'), ('Orders', 'F_Score'), ('NetRecordedValueGBP', 'M_Score')]:
        require(c.groupby(raw_field)[score].nunique().le(1).all(), 'ties ' + raw_field)
    require(c['CRM Priority'].notna().all(), 'action coverage')
    require(c.loc[c.CreditReviewRequired, 'CRM Priority'].eq('Review credits before outreach').all(), 'credit guard')
    valid = retention.stack()
    require(valid.between(0, 1).all(), 'retention bounds')
    for cohort in counts.index:
        for age in counts.columns:
            if cohort + int(age) > pd.Period(stats['last_complete_month'], freq='M'):
                require(pd.isna(counts.loc[cohort, age]), 'future/partial month is not zero')
    for name in ['lifecycle_summary', 'rfm_segment_summary', 'crm_priority_summary']:
        x = tables[name]
        require(int(x.Customers.sum()) == len(c), name + ' count')
        require(abs(x.NetRecordedValueGBP.sum() - c.NetRecordedValueGBP.sum()) <= tol, name + ' net value')


def fmt_rate(value): return 'not estimable (no eligible customers)' if value is None or pd.isna(value) else f'{value:.1%}'

def create_figures(tables, retention, stats, dest):
    dest.mkdir(parents=True, exist_ok=True)
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    life = tables['lifecycle_summary'].sort_values('Customers')
    axes[0, 0].barh(life.Lifecycle, life.Customers, color='#2A9D8F'); axes[0, 0].set_title('Observed lifecycle at snapshot'); axes[0, 0].set_xlabel('Customers')
    ax = axes[0, 1]; pos = np.arange(len(life))
    ax.barh(pos-.18, life.GrossPurchaseValueGBP/1e6, height=.36, label='Gross purchases', color='#16324F')
    ax.barh(pos+.18, life.NetRecordedValueGBP/1e6, height=.36, label='Net after recorded credits', color='#E9C46A')
    ax.set_yticks(pos, labels=life.Lifecycle); ax.set_title('Recorded value: gross versus net after credits'); ax.set_xlabel('GBP million (history; includes invoice charges)'); ax.legend(fontsize=9)
    curve = tables['repeat_90_curve']; axes[1, 0].plot(curve.Day, curve.CumulativeRepeatRate*100, marker='o', color='#16324F')
    axes[1, 0].set_ylim(0, 100); axes[1, 0].set_xlim(0, int(curve.Day.max()));
    if curve.CumulativeRepeatRate.isna().all():
        axes[1, 0].text(.5, .5, 'N/A — no eligible customers', transform=axes[1, 0].transAxes, ha='center')
    axes[1, 0].set_title(f'Second order within 90 days: same mature audience\nn={stats["eligible90_customers"]:,}; first observed purchase')
    axes[1, 0].set_xlabel('Elapsed days since first observed order'); axes[1, 0].set_ylabel('Cumulative customers with second order (%)')
    action = tables['crm_priority_summary'].sort_values('Customers')
    short = {'Review credits before outreach':'Credit review', 'Second-order journey test':'Second-order test', 'Protect frequent higher-value':'Protect frequent / higher value', 'Develop higher-value repeat':'Develop higher-value repeat', 'Develop repeat relationship':'Develop repeat', 'Win-back frequent higher-value test':'Win-back frequent / higher value', 'Win-back higher-value test':'Win-back higher value', 'Lower-cost win-back test':'Lower-cost win-back', 'Review dormant higher-value':'Review dormant / higher value', 'Lower-cost dormant test':'Lower-cost dormant'}
    axes[1, 1].barh(action['CRM Priority'].map(short), action.Customers, color='#2A9D8F');axes[1, 1].set_title('Historical test audiences — not send-ready');axes[1, 1].set_xlabel('Customers')
    fig.suptitle(f'Customer behaviour → value review → CRM test hypotheses\nSnapshot {stats["snapshot_date"]}; all-history repeat {fmt_rate(stats["repeat_customer_rate"])}; mature 90-day repeat {fmt_rate(stats["repeat90_rate"])}', fontsize=15)
    fig.savefig(dest/'customer_lifecycle_decision_dashboard.png', dpi=160);plt.close(fig)
    display = retention.reindex(columns=range(13)).copy()
    fig, ax = plt.subplots(figsize=(13, 11), constrained_layout=True)
    cmap=plt.get_cmap('Blues').copy();cmap.set_bad('#D8D8D8')
    im=ax.imshow(np.ma.masked_invalid(display.to_numpy()*100), cmap=cmap, vmin=0, vmax=100, aspect='auto')
    ax.set_xticks(range(13), labels=range(13));ax.set_yticks(range(len(display)), labels=[str(x) for x in display.index]);ax.set_xlabel('Calendar months after first observed purchase');ax.set_ylabel('First-observed cohort')
    ax.set_title('Customers purchasing in each month (% of first-observed cohort)\nGrey = incomplete/unobserved window; white/blue = observed rate, including true 0%', fontsize=12)
    fig.colorbar(im, ax=ax, label='Monthly activity (%)');fig.savefig(dest/'cohort_retention_heatmap.png',dpi=160);plt.close(fig)
    rk = tables['retention_kpis'];fig, ax=plt.subplots(figsize=(9, 5),constrained_layout=True)
    ax.bar(rk.Month.astype(str), rk.WeightedRetentionRate*100,color='#16324F');ax.set_ylim(0,100);ax.set_ylabel('Customers active (%)');ax.set_xlabel('Calendar month after first observed purchase')
    ax.set_title('Mature weighted cohort activity — audiences differ by horizon')
    ax.set_xlim(-.5, len(rk)-.5)
    for j,row in enumerate(rk.itertuples()):
        value = row.WeightedRetentionRate
        label = f'n={row.EligibleCustomers:,}' if pd.notna(value) else f'n={row.EligibleCustomers:,}\nN/A — no eligible customers'
        ax.annotate(label, (j, 0 if pd.isna(value) else value*100), xytext=(0, 7), textcoords='offset points', ha='center', fontsize=9)
    fig.savefig(dest/'mature_cohort_rates.png',dpi=160);plt.close(fig)


def write_memo(tables, stats, path):
    k = tables['retention_kpis'].set_index('Month')
    priority = tables['crm_priority_summary']
    rows = '\n'.join(f'| {r["CRM Priority"]} | {int(r["Customers"]):,} | £{r["NetRecordedValueGBP"]:,.0f} |' for _,r in priority.iterrows())
    sens=tables['rule_sensitivity']; max_changed=int(sens.ChangedActions.max())
    median=stats['median_days_to_second_among_repeaters']
    med='not estimable' if median is None else f'{median:.1f} elapsed days'
    text=f'''# Customer Lifecycle & Value Review — generated decision memo

## Decision and evidence

Use lifecycle to select the journey, RFM/value history to differentiate treatment, and mature repeat/cohort activity to set descriptive test references. All audiences are historical hypotheses; no messages have been sent and no causal uplift measured.

- {stats['customers']:,} identified purchase customers; {stats['orders']:,} distinct purchase invoices. All-history repeat: **{fmt_rate(stats['repeat_customer_rate'])}**. Repeat on a different calendar day: **{fmt_rate(stats['repeat_another_day_rate'])}**. A second invoice is not proof of a second visit or a retained sale.
- **{stats['second_order90_customers']:,}/{stats['eligible90_customers']:,} = {fmt_rate(stats['repeat90_rate'])}** placed a second order within exactly 90 elapsed days, among customers with the entire window observed. Different-day repeat in that same window: **{fmt_rate(stats['another_day90_rate'])}**.
- Median time to second order among observed repeaters: **{med}**. This excludes non-repeaters, varies with follow-up and does not identify an optimal campaign day. Use repeat_90_curve.csv (same mature denominator at every point) to frame timing hypotheses.
- Month-1 cohort activity: **{fmt_rate(k.loc[1,'WeightedRetentionRate'])}**; month-3: **{fmt_rate(k.loc[3,'WeightedRetentionRate'])}**. The mature audiences differ; changes between horizons are not a common-population survival curve. Activity in month n need not be continuous activity in earlier months.
- Historical gross purchases: **£{stats['gross_purchase_value_gbp']:,.0f}**; recorded credits: **£{stats['credit_value_gbp']:,.0f}**; net recorded value: **£{stats['net_recorded_value_gbp']:,.0f}**. These include invoice charges and are neither profit nor future CLV.
- **{stats['credit_review_customers']:,}** customers require credit/value review before outreach. Credit-only customers are excluded from purchase segmentation but reconciled separately.
- Alternative analyst-defined rules changed up to **{max_changed:,}** action labels. Thresholds are transparent hypotheses, not validated optima; inspect rule_sensitivity.csv before operational adoption.

## Historical review/test audiences

| Proposed audience | Customers | Net recorded history |
|---|---:|---:|
{rows}

## Conditional next tests

1. CRM analyst first resolves nonpositive net value/high credit burden, checks contact permission, current customer status, product mix and attribution of credits. No automatic discount is supported.
2. For eligible recent single-order customers, propose post-purchase timing tests (for example day 14 versus day 30 versus a no-message holdout); these timings are hypotheses. Define eligibility at assignment, follow all arms for 90 days from first order, and compare second-order rate and net contribution per assigned customer. Do not use current RFM labels to estimate historical acquisition-stage response probabilities.
3. For repeat or win-back audiences, test one permitted treatment against customer-level holdout; stratify using pre-assignment lifecycle/value/frequency and season/cohort. Primary business outcome requires margin and treatment cost not present here; also monitor credits, unsubscribes and complaints. CRM lead owns approval; analyst owns measurement. Define power/sample, stopping rule, reporting windows and acceptable harms before launch. If this cannot be done, collect the missing inputs rather than claim a successful strategy.
4. Month/cohort variation motivates investigation of seasonality, tenure, wholesale mix and acquisition source, not a causal channel ranking. Revenue concentration alone does not prove which treatment has incremental ROI.

## Limits next to the decision

Observation {stats['observation_start']}–{stats['observation_end']}; snapshot {stats['snapshot_date']}; last complete month {stats['last_complete_month']}. The business is one historical UK retailer with wholesale customers; this is not current Vietnam market evidence. First observed purchase is not verified acquisition. Missing IDs and credit-only customers change coverage. Lifetime F/M depend on observation tenure; tenure_context.csv and the 365-day context fields help reveal that exposure difference but do not estimate future value. A credit is not linked back to a specific purchase invoice, so frequency describes positive purchase invoices, not non-returned orders. Exact-row deduplication is an assumption with a retained-duplicates sensitivity check. Source-local timestamps lack timezone metadata. All figures and the memo are static until the pipeline is rerun; the notebook invokes the same implementation.
'''
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')


def run_pipeline(data_path=None, destination=None, config_path=None):
    data_path=Path(data_path or ROOT/'data/online_retail_II.csv.gz').resolve()
    destination=Path(destination or ROOT).resolve()
    cfg=load_config(config_path)
    raw=read_input(data_path)
    tables,counts,retention,observed,stats=analyse(raw,cfg)
    stats['input_sha256']=hashlib.sha256(data_path.read_bytes()).hexdigest()
    stats['config_sha256']=hashlib.sha256(Path(config_path or ROOT/'analysis/config.json').read_bytes()).hexdigest()
    destination.mkdir(parents=True,exist_ok=True)
    # Stage completely before replacing successful outputs. If validation fails,
    # old files remain old; the entrypoint exits nonzero and prints no PASS.
    stage=Path(tempfile.mkdtemp(prefix='.rfm-stage-',dir=destination))
    try:
        (stage/'outputs').mkdir()
        for name,table in tables.items():
            if name == 'duplicate_sensitivity':
                (stage/'outputs/duplicate_sensitivity.json').write_text(
                    json.dumps(table.to_dict(orient='records')[0], indent=2, allow_nan=False), encoding='utf-8')
            elif name in ['purchase_lines', 'credit_lines']:
                table.to_csv(stage/'outputs'/f'{name}.csv.gz', index=False, float_format='%.10g', compression={'method': 'gzip', 'mtime': 0})
            else:
                table.to_csv(stage/'outputs'/f'{name}.csv',index=False,float_format='%.10g')
        for name,table in [('cohort_counts',counts),('cohort_retention',retention),('cohort_activity_observed',observed)]:
            table.rename_axis('CohortMonth').to_csv(stage/'outputs'/f'{name}.csv',float_format='%.10g')
        (stage/'outputs/run_summary.json').write_text(json.dumps(stats,indent=2,allow_nan=False),encoding='utf-8')
        create_figures(tables,retention,stats,stage/'figures')
        write_memo(tables,stats,stage/'memo/business_memo.md')
        for folder in ['outputs','figures','memo']:
            target=destination/folder
            if target.exists():shutil.rmtree(target)
            shutil.move(str(stage/folder),str(target))
    finally:shutil.rmtree(stage,ignore_errors=True)
    print(f'PASS — pipeline validation completed; {stats["customers"]:,} customers, {stats["orders"]:,} purchase invoices')
    print(f'Mature 90-day second-order rate: {fmt_rate(stats["repeat90_rate"])} ({stats["second_order90_customers"]:,}/{stats["eligible90_customers"]:,})')
    return stats


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=ROOT/'data/online_retail_II.csv.gz')
    parser.add_argument('--destination',type=Path,default=ROOT)
    parser.add_argument('--config',type=Path,default=ROOT/'analysis/config.json')
    args=parser.parse_args()
    try:run_pipeline(args.data,args.destination,args.config)
    except (ValueError,KeyError,FileNotFoundError,pd.errors.ParserError) as error:
        print(f'FAIL — {error}; previous outputs, if present, are not a new successful run',file=sys.stderr)
        raise SystemExit(1)

if __name__ == '__main__':main()
