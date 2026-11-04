"""Independent Python CSV oracle. Does not reuse cohort SQL or production analytical functions."""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import date, datetime, timezone
from decimal import Decimal
import csv
import json
import math
import threading

import duckdb


def rows(path):
    with Path(path).open(newline='', encoding='utf-8') as f:
        yield from csv.DictReader(f)


def verify(root, database, results):
    checks = []
    def check(name, condition, detail=None):
        checks.append({'check': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})
        if not condition:
            raise AssertionError(name + ': ' + str(detail))

    # Compact per-user state. Ordinal calendar dates avoid timezone conversions.
    # [anchor (date,id), channel, device, new flag, day counts, channels, first purchase,
    #  purchase events [(ordinal, decimal)], session count, anchor-day channel set]
    users = {}
    session_owners = {}
    session_count = event_count = 0
    start = 10**9
    end = 0
    for r in rows(root / 'data/audited/fact_sessions.csv'):
        uid, sid = r['user_id'], r['session_id']
        d = date.fromisoformat(r['session_date']).toordinal()
        anchor = (d, sid)
        ch, dev = int(r['channel_id']), int(r['device_id'])
        check_duplicate = sid in session_owners
        if check_duplicate:
            raise AssertionError('Duplicate session key: ' + sid)
        session_owners[sid] = uid
        if uid not in users:
            users[uid] = [anchor, ch, dev, int(r['is_new_user']), Counter(), set(), None, [], 0, set()]
        u = users[uid]
        if anchor < u[0]:
            if d < u[0][0]:
                u[9] = set()
            u[0:4] = [anchor, ch, dev, int(r['is_new_user'])]
        if d == u[0][0]:
            u[9].add(ch)
        u[4][d] += 1
        u[5].add(ch)
        u[8] += 1
        session_count += 1
        event_count += int(r['event_count'])
        start, end = min(start, d), max(end, d)
    purchase_count = 0
    revenue = Decimal(0)
    purchase_keys = set()
    for r in rows(root / 'data/audited/fact_purchases.csv'):
        uid = r['user_id']
        if uid not in users or session_owners.get(r['session_id']) != uid:
            raise AssertionError('Orphan/mismatched purchase: ' + r['purchase_key'])
        if r['purchase_key'] in purchase_keys:
            raise AssertionError('Duplicate purchase source-row key')
        purchase_keys.add(r['purchase_key'])
        u = users[uid]
        d = date.fromisoformat(r['purchase_date']).toordinal()
        if d < u[0][0] or d > end:
            raise AssertionError('Purchase outside user observation range')
        u[6] = d if u[6] is None else min(u[6], d)
        money = Decimal(r['purchase_revenue_usd'])
        u[7].append((d, money))
        purchase_count += 1
        revenue += money
    del session_owners
    controls = {r['metric']: Decimal(r['value']) for r in rows(root/'audit/upstream_kpi_summary.csv')}
    check('Sessions reconcile with audited Power BI input', session_count == controls['Sessions'], session_count)
    check('Users reconcile with audited Power BI input', len(users) == controls['Users'], len(users))
    check('Purchase events reconcile', purchase_count == controls['Purchase Events'], purchase_count)
    check('Recorded USD revenue reconciles exactly', revenue == controls['Revenue'], str(revenue))
    check('Source event count reconciles with retained provenance',
          event_count == json.loads((root/'data/audited/source/provenance.json').read_text())['source_rows'], event_count)
    check('Session calendar has full 92-day observed range', end-start+1 == 92,
          [date.fromordinal(start).isoformat(), date.fromordinal(end).isoformat()])

    con = duckdb.connect(str(database), read_only=True)
    con.execute("SET memory_limit='256MB'; SET threads=1")
    timer = threading.Timer(90, con.interrupt)
    timer.daemon = True
    timer.start()
    try:
        # Every derived user row, not just aggregate totals.
        cursor = con.execute('''SELECT user_id,first_observed_date,anchor_session_id,anchor_channel_id,
          anchor_device_id,anchor_new_user_flag,observed_sessions,observed_channel_variants,
          anchor_day_sessions,anchor_day_channel_variants,days_to_first_return,
          days_to_first_purchase,observed_purchase_events,observed_purchase_revenue_usd
          FROM user_cohorts''')
        seen = 0
        while True:
            batch = cursor.fetchmany(4000)
            if not batch:
                break
            for actual in batch:
                uid = actual[0]
                u = users[uid]
                a = u[0][0]
                later = [d for d in u[4] if d > a]
                expected = (uid, date.fromordinal(a), u[0][1], u[1], u[2], u[3],
                            u[8], len(u[5]), u[4][a], len(u[9]),
                            min(later)-a if later else None,
                            u[6]-a if u[6] is not None else None,
                            len(u[7]), sum((m for _,m in u[7]), Decimal(0)))
                if actual != expected:
                    raise AssertionError('User-grain mismatch: ' + uid + ' ' + repr((actual, expected)))
                seen += 1
        check('Every user cohort row independently matches CSV oracle', seen == len(users), seen)
        cursor = con.execute('''SELECT user_id,horizon_days,is_eligible,returned_by_horizon,
          purchased_by_horizon,purchase_events_by_horizon,purchase_revenue_by_horizon_usd
          FROM user_windows''')
        window_rows = 0
        while True:
            batch = cursor.fetchmany(4000)
            if not batch:
                break
            for actual in batch:
                uid,h = actual[:2]
                u = users[uid]
                anchor = u[0][0]
                eligible = anchor+h<=end
                later = [d for d in u[4] if anchor<d<=anchor+h]
                pp = [(d,m) for d,m in u[7] if anchor<=d<=anchor+h]
                expected = (uid,h,eligible,bool(later) if eligible else None,
                  bool(pp) if eligible else None,len(pp) if eligible else None,
                  sum((m for _,m in pp),Decimal(0)) if eligible else None)
                if actual != expected:
                    raise AssertionError('User-horizon mismatch: '+repr((actual,expected)))
                window_rows += 1
        check('Every user-horizon outcome independently matches CSV oracle',window_rows==len(users)*3,window_rows)
        check('One unique row per user and horizon', con.execute(
            'SELECT count(*)=count(DISTINCT (user_id,horizon_days)) FROM user_windows').fetchone()[0])
        check('Ineligible users carry NULL outcomes, not zero', con.execute('''SELECT count(*) FROM user_windows
          WHERE NOT is_eligible AND (returned_by_horizon IS NOT NULL OR purchased_by_horizon IS NOT NULL
          OR purchase_revenue_by_horizon_usd IS NOT NULL OR purchase_events_by_horizon IS NOT NULL)''').fetchone()[0] == 0)
        check('No missing channel dimension keys', con.execute('''SELECT count(*) FROM fact_sessions s
          ANTI JOIN dim_channel c USING(channel_id)''').fetchone()[0] == 0)
        check('No missing device dimension keys', con.execute('''SELECT count(*) FROM fact_sessions s
          ANTI JOIN dim_device d USING(device_id)''').fetchone()[0] == 0)
        check('Purchase/session user identities match', con.execute('''SELECT count(*) FROM fact_purchases p
          JOIN fact_sessions s USING(session_id) WHERE p.user_id<>s.user_id''').fetchone()[0] == 0)
    finally:
        timer.cancel()
        con.close()

    channels = {int(r['channel_id']): r['channel'] for r in rows(root/'data/audited/dim_channel.csv')}
    devices = {int(r['device_id']): r['device_category'] for r in rows(root/'data/audited/dim_device.csv')}
    # Counter arrays: cohort, eligible, excluded, returned, buyers, purchase events, revenue.
    def fresh():
        return [0, 0, 0, 0, 0, 0, Decimal(0)]
    aggregates = {k: defaultdict(fresh) for k in ['overall_windows','monthly_cohorts',
        'channel_sensitivity','device_cohorts','daily_cohorts','fixed_population','monthly_fixed_population']}
    timing = Counter()
    gaps = Counter()
    gap_users = defaultdict(set)
    for uid,u in users.items():
        anchor = u[0][0]
        month = date.fromordinal(anchor).replace(day=1).isoformat()
        day = date.fromordinal(anchor).isoformat()
        later = sorted(d for d in u[4] if d > anchor)
        purchase_age = None if u[6] is None else u[6]-anchor
        bucket = 5 if purchase_age is None else 0 if purchase_age == 0 else 1 if purchase_age <= 7 else 2 if purchase_age <= 14 else 3 if purchase_age <= 30 else 4
        timing[bucket] += 1
        dates = sorted(u[4])
        for previous,current in zip(dates,dates[1:]):
            gap = current-previous
            b = 0 if gap<=7 else 1 if gap<=14 else 2 if gap<=30 else 3
            gaps[b] += 1
            gap_users[b].add(uid)
        for h in [7,14,30]:
            eligible = anchor+h <= end
            purchases = [(d,m) for d,m in u[7] if anchor<=d<=anchor+h]
            values = [1, int(eligible), int(not eligible),
                      int(eligible and bool(later) and later[0]<=anchor+h),
                      int(eligible and purchase_age is not None and 0<=purchase_age<=h),
                      len(purchases) if eligible else 0,
                      sum((m for _,m in purchases), Decimal(0)) if eligible else Decimal(0)]
            keys = [('overall_windows',(h,)),('monthly_cohorts',(month,h)),
                    ('device_cohorts',(devices[u[2]],h)),('daily_cohorts',(day,h)),
                    ('channel_sensitivity',('All observed users',channels[u[1]],h))]
            if len(u[5])==1:
                keys.append(('channel_sensitivity',('Consistent channel only',channels[u[1]],h)))
            if anchor+30<=end:
                keys += [('fixed_population',(h,)),('monthly_fixed_population',(month,h))]
            for name,key in keys:
                for i,v in enumerate(values):
                    aggregates[name][key][i] += v
    key_fields = {'overall_windows':['horizon_days'], 'monthly_cohorts':['cohort_month','horizon_days'],
       'channel_sensitivity':['population','anchor_channel','horizon_days'],
       'device_cohorts':['anchor_device','horizon_days'], 'daily_cohorts':['cohort_date','horizon_days'],
       'fixed_population':['horizon_days'], 'monthly_fixed_population':['cohort_month','horizon_days']}
    count_fields = {'cohort_users':0,'eligible_users':1,'excluded_incomplete_followup':2,
                    'returned_users':3,'purchasing_users':4,'purchase_events':5,'purchase_revenue_usd':6}
    cells_checked = 0
    for name, oracle in aggregates.items():
        actual_rows = list(rows(results/(name+'.csv')))
        found = set()
        for r in actual_rows:
            key = tuple(int(r[k]) if k=='horizon_days' else r[k] for k in key_fields[name])
            if key in found or key not in oracle:
                raise AssertionError('Unexpected/duplicate output key: '+name+repr(key))
            found.add(key)
            e = oracle[key]
            for field,index in count_fields.items():
                if field in r:
                    # SQL SUM of an all-NULL group stays NULL, rather than fabricated zero.
                    expected = None if field in ['purchase_events','purchase_revenue_usd'] and e[1]==0 else e[index]
                    actual = None if r[field]=='' else Decimal(r[field])
                    if actual != expected:
                        raise AssertionError(f'{name} {key} {field}: {actual} != {expected}')
                    cells_checked += 1
            for field,num in [('return_rate',3),('first_purchase_rate',4),('purchase_revenue_per_eligible_user_usd',6)]:
                if field in r:
                    expected = None if not e[1] else float(e[num])/e[1]
                    actual = None if not r[field] else float(r[field])
                    if (expected is None) != (actual is None) or (expected is not None and not math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-12)):
                        raise AssertionError(f'{name} {key} {field}: {actual} != {expected}')
                    cells_checked += 1
        check('Every output cell matches independent oracle: '+name, found==set(oracle),
              {'rows':len(actual_rows)})
    for r in rows(results/'purchase_timing.csv'):
        b=int(r['bucket_order'])
        check('Purchase timing bucket '+str(b),int(r['users'])==timing[b],timing[b])
        total = len(users)
        buyers = total-timing[5]
        check('Purchase timing denominator '+str(b),math.isclose(float(r['share_of_all_users']),timing[b]/total,rel_tol=1e-10))
        check('Purchaser timing share '+str(b),
              r['share_of_observed_purchasers']=='' if b==5 else math.isclose(float(r['share_of_observed_purchasers']),timing[b]/buyers,rel_tol=1e-10))
    for r in rows(results/'return_gaps.csv'):
        b=int(r['bucket_order'])
        check('Return gap interval bucket '+str(b),int(r['observed_intervals'])==gaps[b],gaps[b])
        check('Return gap unique users '+str(b),int(r['users_contributing'])==len(gap_users[b]))
        check('Return gap denominator '+str(b),math.isclose(float(r['share_of_intervals']),gaps[b]/sum(gaps.values()),rel_tol=1e-10))
    fixed = list(rows(results/'fixed_population.csv'))
    check('Fixed-population denominators identical across horizons',len({r['eligible_users'] for r in fixed})==1)
    for field in ['returned_users','purchasing_users','purchase_events','purchase_revenue_usd']:
        values = [Decimal(r[field]) for r in fixed]
        check('Fixed-population cumulative outcomes monotone: '+field,values==sorted(values))
    return {'status':'PASS','checked_utc':datetime.now(timezone.utc).isoformat(),
            'checks_passed':len(checks),'checks':checks,'aggregate_cells_compared':cells_checked,
            'all_user_rows_compared':len(users),'independent_oracle':'Python csv/datetime/Decimal; no production SQL reused',
            'all_user_horizon_rows_compared':window_rows,
            'scope':'Bundled audited inputs to new cohort SQL and exported results; not an external source re-download or Windows UI test.'}


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    evidence=verify(root,root/'database/ga4_cohorts.duckdb',root/'results')
    (root/'audit/validation.json').write_text(json.dumps(evidence,indent=2))
    print(json.dumps({k:v for k,v in evidence.items() if k!='checks'},indent=2))
