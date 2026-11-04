"""Independent checks for the bundled Online Retail II release.

Does not import any pipeline function. SQL re-aggregates invoices; raw-value
cutoffs, customer labels, monthly windows and summaries are checked separately.
This verifies the bundled-source contract, not arbitrary replacement datasets.
"""
import bisect
import hashlib
import json
import math
import re
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    checks = []
    cfg = json.loads((ROOT / 'analysis/config.json').read_text())
    stats = json.loads((ROOT / 'outputs/run_summary.json').read_text())
    source = ROOT / 'data/online_retail_II.csv.gz'
    raw = pd.read_csv(source, dtype={'Invoice': str, 'StockCode': str}, low_memory=False)
    saved = pd.read_csv(ROOT / 'outputs/customer_lifecycle_table.csv', dtype={'RFM_Profile': str})
    saved = saved.set_index('Customer ID').sort_index()

    def check(name, condition, detail):
        if not bool(condition):
            raise AssertionError(name + ': ' + str(detail))
        checks.append({'check': name, 'verdict': 'PASS', 'evidence': detail})

    check('Input bytes match release', hashlib.sha256(source.read_bytes()).hexdigest() == stats['input_sha256'], 'bundled gzip SHA-256')
    check('Config bytes match release', hashlib.sha256((ROOT / 'analysis/config.json').read_bytes()).hexdigest() == stats['config_sha256'], 'config SHA-256')
    check('Raw grain and schema', len(raw) == stats['raw_rows'] and list(raw.columns) == ['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID', 'Country'], len(raw))
    # The supplied source is inspected before this simpler SQL preparation.
    # Strict production parser counterexamples are covered by fixture tests.
    raw['InvoiceDate'] = pd.to_datetime(raw.InvoiceDate, errors='raise')
    keep = raw.dropna(subset=['Customer ID']).copy()
    keep = keep.loc[(keep.Price > 0) & (keep.Quantity != 0)].drop_duplicates()
    check('Bundled numeric domain valid', np.isfinite(keep[['Quantity', 'Price', 'Customer ID']]).all().all() and keep['Customer ID'].between(1, 2**53-1).all() and keep['Customer ID'].mod(1).eq(0).all() and keep.Quantity.mod(1).eq(0).all(), 'no unparsed/out-of-range numeric values in retained bundled data')
    keep['Customer ID'] = keep['Customer ID'].astype(int)
    keep['LineValueGBP'] = keep.Quantity * keep.Price
    purchase = keep.loc[(keep.Quantity > 0) & ~keep.Invoice.str.upper().str.startswith('C')]
    credit = keep.loc[(keep.Quantity < 0) & keep.Invoice.str.upper().str.startswith('C')]
    check('Signed-line domain', len(purchase) + len(credit) == len(keep), 'all retained lines are purchases or C-prefixed negative credits')
    check('Purchase and credit counts', len(purchase) == stats['purchase_lines'] and len(credit) == stats['credit_lines'], [len(purchase), len(credit)])
    for name, expected in [('purchase_lines', purchase), ('credit_lines', credit)]:
        delivered = pd.read_csv(ROOT / f'outputs/{name}.csv.gz', dtype={'Invoice': str, 'StockCode': str}, low_memory=False)
        check(name + ' exact row membership/order', len(delivered) == len(expected) and delivered.Invoice.tolist() == expected.Invoice.tolist() and delivered.StockCode.tolist() == expected.StockCode.tolist() and delivered['Customer ID'].tolist() == expected['Customer ID'].tolist(), len(delivered))
        check(name + ' line values', np.allclose(delivered.LineValueGBP, expected.LineValueGBP, atol=.01, rtol=0), 'GBP .01 absolute tolerance')

    with sqlite3.connect(':memory:') as db:
        db.execute('PRAGMA temp_store=MEMORY')
        keep[['Customer ID', 'Invoice', 'InvoiceDate', 'Quantity', 'Price']].rename(columns={'Customer ID': 'CustomerID'}).to_sql('lines', db, index=False, chunksize=10000)
        db.executescript('''
            CREATE TABLE orders AS SELECT CustomerID,Invoice,MIN(InvoiceDate) AS OrderDate,
                MAX(InvoiceDate) AS LastLineTimestamp,COUNT(*) AS Lines,SUM(Quantity*Price) AS Gross
                FROM lines WHERE Quantity>0 AND UPPER(Invoice) NOT LIKE 'C%' GROUP BY CustomerID,Invoice;
            CREATE TABLE numbered AS SELECT *,ROW_NUMBER() OVER(PARTITION BY CustomerID ORDER BY OrderDate,Invoice) AS rn FROM orders;
            CREATE TABLE credits AS SELECT CustomerID,-SUM(Quantity*Price) AS Credit FROM lines
                WHERE Quantity<0 AND UPPER(Invoice) LIKE 'C%' GROUP BY CustomerID;
        ''')
        oracle = pd.read_sql_query('''SELECT n.CustomerID AS "Customer ID",COUNT(*) AS Orders,
            SUM(n.Gross) AS GrossPurchaseValueGBP,MIN(n.OrderDate) AS FirstObservedPurchase,
            MAX(n.OrderDate) AS LastObservedPurchase,COUNT(DISTINCT substr(n.OrderDate,1,10)) AS PurchaseDays,
            MAX(CASE WHEN rn=2 THEN n.OrderDate END) AS SecondObservedPurchase,
            COALESCE(c.Credit,0) AS CreditValueGBP FROM numbered n
            LEFT JOIN credits c ON n.CustomerID=c.CustomerID GROUP BY n.CustomerID''', db).set_index('Customer ID').sort_index()
        orders = pd.read_sql_query('SELECT * FROM numbered ORDER BY CustomerID,OrderDate,Invoice', db)

    check('Customer keys and population', saved.index.is_unique and oracle.index.equals(saved.index), len(saved))
    delivered_orders = pd.read_csv(ROOT / 'outputs/orders.csv', dtype={'Invoice': str})
    check('All purchase invoice keys/order', len(orders) == len(delivered_orders) and orders.CustomerID.tolist() == delivered_orders['Customer ID'].tolist() and orders.Invoice.tolist() == delivered_orders.Invoice.tolist(), len(orders))
    for field, delivered_field in [('Gross', 'OrderGrossValueGBP'), ('Lines', 'Lines'), ('rn', 'OrderNumber')]:
        check('Order field ' + delivered_field, np.allclose(orders[field], delivered_orders[delivered_field], atol=.01 if field == 'Gross' else 0, rtol=0), len(orders))
    for field in ['OrderDate', 'LastLineTimestamp']:
        check('Order field ' + field, pd.to_datetime(orders[field]).equals(pd.to_datetime(delivered_orders[field])), len(orders))

    end, start = raw.InvoiceDate.max(), raw.InvoiceDate.min()
    snapshot = end.normalize() + pd.Timedelta(days=1)
    for col in ['FirstObservedPurchase', 'LastObservedPurchase', 'SecondObservedPurchase']:
        oracle[col] = pd.to_datetime(oracle[col])
    oracle['NetRecordedValueGBP'] = oracle.GrossPurchaseValueGBP - oracle.CreditValueGBP
    oracle['CreditToGrossRatio'] = oracle.CreditValueGBP / oracle.GrossPurchaseValueGBP
    oracle['AverageGrossOrderValueGBP'] = oracle.GrossPurchaseValueGBP / oracle.Orders
    oracle['RecencyDays'] = (snapshot - oracle.LastObservedPurchase.dt.normalize()).dt.days
    oracle['ObservedTenureDays'] = (end - oracle.FirstObservedPurchase).dt.total_seconds() / 86400
    oracle['RepeatCustomer'] = oracle.Orders.ge(2)
    oracle['RepeatOnAnotherDay'] = oracle.PurchaseDays.ge(2)
    oracle['DaysToSecondOrder'] = (oracle.SecondObservedPurchase - oracle.FirstObservedPurchase).dt.total_seconds() / 86400
    oracle['Eligible90'] = oracle.FirstObservedPurchase.le(end - pd.Timedelta(days=90))
    oracle['SecondOrderWithin90'] = oracle.Eligible90 & oracle.DaysToSecondOrder.le(90)
    orders['OrderDate'] = pd.to_datetime(orders.OrderDate)
    later = orders.join(oracle.FirstObservedPurchase, on='CustomerID')
    later = later.loc[later.OrderDate.dt.date > later.FirstObservedPurchase.dt.date].groupby('CustomerID').OrderDate.min()
    oracle['NextPurchaseDayTimestamp'] = later
    oracle['AnotherPurchaseDayWithin90'] = oracle.Eligible90 & (oracle.NextPurchaseDayTimestamp - oracle.FirstObservedPurchase).le(pd.Timedelta(days=90))
    oracle['FirstObservedCohort'] = oracle.FirstObservedPurchase.dt.strftime('%Y-%m')
    recent_start = snapshot - pd.Timedelta(days=365)
    oracle['OrdersLast365Days'] = orders.loc[orders.OrderDate >= recent_start].groupby('CustomerID').size().reindex(oracle.index, fill_value=0)
    oracle['NetRecordedValueLast365DaysGBP'] = keep.loc[keep.InvoiceDate >= recent_start].groupby('Customer ID').LineValueGBP.sum().reindex(oracle.index, fill_value=0)

    cutoffs = []
    for dim, col in [('R', 'RecencyDays'), ('F', 'Orders'), ('M', 'NetRecordedValueGBP')]:
        values = sorted(oracle[col].tolist())
        cuts = []
        for q in cfg['score_quantiles']:
            pos = (len(values)-1)*q
            lo = math.floor(pos)
            hi = math.ceil(pos)
            cuts.append(values[lo] + (values[hi]-values[lo])*(pos-lo))
        scores = [1 + bisect.bisect_left(cuts, v) for v in oracle[col]]
        oracle[dim + '_Score'] = [6-v if dim == 'R' else v for v in scores]
        cutoffs.extend(cuts)
    check('Independent linear raw quantile cutoffs', np.allclose(cutoffs, pd.read_csv(ROOT/'outputs/rfm_cutoffs.csv').Cutoff, atol=.000001, rtol=0), 'sorted raw values with interpolation; equal-to-cutoff stays lower')
    oracle['RFM_Score'] = oracle.R_Score + oracle.F_Score + oracle.M_Score
    oracle['RFM_Profile'] = oracle.R_Score.astype(str)+oracle.F_Score.astype(str)+oracle.M_Score.astype(str)
    r,f,m = oracle.R_Score,oracle.F_Score,oracle.M_Score
    oracle['RFM Segment'] = np.select([(r>=4)&(f>=4)&(m>=4),(r>=3)&(f>=4),(r>=4)&f.isin([2,3]),(r>=4)&(f==1),(r<=2)&(f>=3),(r<=2)&(f<=2)], ['Champions (relative)','Recent frequent','Recent mid-frequency','Recent low-frequency','Lapsed frequent','Lapsed low-frequency'], default='Intermediate')
    rec = oracle.RecencyDays
    oracle['Lifecycle'] = np.select([(rec<=cfg['active_days'])&(oracle.Orders==1),(rec<=cfg['active_days'])&(oracle.Orders>=2),(rec>cfg['active_days'])&(rec<=cfg['dormant_days'])], ['Recent single-order','Active repeat','At risk'], default='Dormant')
    oracle['ValueTier'] = np.select([m>=cfg['high_value_min_m_score'],m>=3], ['Higher recorded value','Middle recorded value'], default='Lower recorded value')
    oracle['CreditReviewRequired'] = (oracle.NetRecordedValueGBP<=0)|(oracle.CreditToGrossRatio>=cfg['credit_review_ratio'])
    high = oracle.ValueTier.eq('Higher recorded value')
    frequent = f>=cfg['frequent_min_f_score']
    active = oracle.Lifecycle.eq('Active repeat')
    risk = oracle.Lifecycle.eq('At risk')
    oracle['CRM Priority'] = np.select([oracle.CreditReviewRequired,oracle.Lifecycle.eq('Recent single-order'),active&oracle['RFM Segment'].eq('Champions (relative)')&high&frequent,active&high,active,risk&high&frequent,risk&high,risk,high], ['Review credits before outreach','Second-order journey test','Protect frequent higher-value','Develop higher-value repeat','Develop repeat relationship','Win-back frequent higher-value test','Win-back higher-value test','Lower-cost win-back test','Review dormant higher-value'], default='Lower-cost dormant test')
    oracle['ContactReady'] = False
    oracle['AudienceStatus'] = 'Historical test hypothesis; consent/contact/margin checks required'
    check('All customer columns covered', set(oracle.columns)==set(saved.columns), len(saved.columns))
    for col in oracle.columns:
        expected, actual = oracle[col], saved[col]
        if pd.api.types.is_datetime64_any_dtype(expected):
            matches = expected.equals(pd.to_datetime(actual))
        elif pd.api.types.is_numeric_dtype(expected) and not pd.api.types.is_bool_dtype(expected):
            tol = .01 if 'GBP' in col else 1e-7
            matches = np.allclose(expected,actual,atol=tol,rtol=0,equal_nan=True)
        else:
            matches = expected.fillna('').eq(actual.fillna('')).all()
        check('All customers: '+col, matches, len(saved))

    for grouping, name in [('Lifecycle','lifecycle_summary'),('RFM Segment','rfm_segment_summary'),('CRM Priority','crm_priority_summary')]:
        exported = pd.read_csv(ROOT/f'outputs/{name}.csv').set_index(grouping).sort_index()
        grouped = oracle.groupby(grouping)
        expected = grouped.size().sort_index()
        check(name+' counts', exported.index.equals(expected.index) and exported.Customers.eq(expected).all(), int(expected.sum()))
        for col in ['GrossPurchaseValueGBP','CreditValueGBP','NetRecordedValueGBP']:
            check(name+' '+col, np.allclose(exported[col],grouped[col].sum().sort_index(),atol=.01,rtol=0), 'grouped independent customer values')
    cohorts = pd.read_csv(ROOT/'outputs/cohort_counts.csv',index_col=0)
    rates = pd.read_csv(ROOT/'outputs/cohort_retention.csv',index_col=0)
    orders['Cohort'] = orders.CustomerID.map(oracle.FirstObservedCohort)
    orders['Month'] = orders.OrderDate.dt.strftime('%Y-%m')
    active_sets = orders.groupby(['Cohort','Month']).CustomerID.agg(set).to_dict()
    cohort_sizes = oracle.groupby('FirstObservedCohort').size()
    last_complete = end.to_period('M')-1
    first_complete = start.to_period('M')+(0 if start.day==1 else 1)
    comparisons = 0
    for cohort in cohorts.index:
        for age in cohorts.columns:
            target = pd.Period(cohort,freq='M')+int(age)
            observed = pd.Period(cohort,freq='M')>=first_complete and target<=last_complete
            count = len(active_sets.get((cohort,str(target)),set())) if observed else np.nan
            actual = cohorts.loc[cohort,age]
            rate = count/cohort_sizes[cohort] if observed else np.nan
            assert (pd.isna(count) and pd.isna(actual)) or count==actual
            assert np.isclose(rate,rates.loc[cohort,age],atol=1e-7,rtol=0,equal_nan=True)
            comparisons += 1
    check('Every cohort count/rate/window', True, comparisons)
    check('90-day headline denominator/outcome', int(oracle.Eligible90.sum())==stats['eligible90_customers'] and int(oracle.SecondOrderWithin90.sum())==stats['second_order90_customers'], f"{stats['second_order90_customers']}/{stats['eligible90_customers']}")
    for path in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('http://','https://','#')): continue
            assert (path.parent/target.split('#')[0]).exists(),(str(path.relative_to(ROOT)),target)
    check('All delivered Markdown links', True, 'every local target exists')
    report = {'status':'PASS','scope':'bundled-source independent SQL/raw-value customer, order, line, scoring, label, cohort and link checks','checks_passed':len(checks),'checks':checks,'customer_rows':len(saved),'environment':{'python':sys.version.split()[0],'pandas':pd.__version__,'numpy':np.__version__},'tolerance':{'GBP_absolute':.01,'serialized_nonmonetary_absolute':1e-7,'cutoffs_absolute':1e-6,'counts_keys_labels':'exact'},'production_functions_imported':False,'input_sha256':stats['input_sha256'],'config_sha256':stats['config_sha256'],'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'audit/extended_validation.json').write_text(json.dumps(report,indent=2))
    print(f"PASS — {len(checks)} extended independent checks; all {len(saved)} customers and every cohort cell")


if __name__ == '__main__':
    main()
