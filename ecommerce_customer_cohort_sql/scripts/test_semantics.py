"""Small, hand-checkable fixtures for cohort boundary and grain errors."""
from pathlib import Path
import json
import unittest
import duckdb

ROOT=Path(__file__).resolve().parents[1]


class CohortSemantics(unittest.TestCase):
    def setUp(self):
        self.c=duckdb.connect()
        self.c.execute("SET memory_limit='128MB';SET threads=1")
        self.c.execute('''CREATE TABLE fact_sessions(session_id VARCHAR,user_id VARCHAR,
          session_date DATE,channel_id BIGINT,device_id BIGINT,is_new_user BIGINT);
          CREATE TABLE fact_purchases(user_id VARCHAR,purchase_date DATE,purchase_revenue_usd DECIMAL(20,6));
          CREATE TABLE dim_channel(channel_id BIGINT,channel VARCHAR);
          INSERT INTO dim_channel VALUES(1,'Direct'),(2,'Referral');
          CREATE TABLE dim_device(device_id BIGINT,device_category VARCHAR);
          INSERT INTO dim_device VALUES(1,'desktop');''')
        self.c.executemany('INSERT INTO fact_sessions VALUES(?,?,?,?,?,?)',[
          ('a1','A','2021-01-01',1,1,1),('a2','A','2021-01-08',1,1,0),('a3','A','2021-01-31',1,1,0),
          ('b1','B','2021-01-24',1,1,1),('b2','B','2021-01-31',1,1,0),
          ('c1','C','2021-01-25',1,1,1),('c2','C','2021-01-31',1,1,0),
          ('d_b','D','2021-01-01',2,1,0),('d_a','D','2021-01-01',1,1,0),
          ('e1','E','2021-01-01',2,1,0),('e2','E','2021-01-09',2,1,0)])
        self.c.executemany('INSERT INTO fact_purchases VALUES(?,?,?)',[
          ('A','2021-01-01','10'),('A','2021-01-08','20'),('A','2021-01-31','30'),
          ('B','2021-01-31','5'),('C','2021-01-31','7'),('E','2021-01-09','9')])
        self.build()

    def build(self):
        self.c.execute((ROOT/'sql/01_build_cohorts.sql').read_text())

    def row(self,user,horizon=7):
        return self.c.execute('''SELECT is_eligible,returned_by_horizon,purchased_by_horizon,
          purchase_events_by_horizon,purchase_revenue_by_horizon_usd FROM user_windows
          WHERE user_id=? AND horizon_days=?''',[user,horizon]).fetchone()

    def tearDown(self):
        self.c.close()

    def test_inclusive_day7_and_revenue_no_join_fanout(self):
        self.assertEqual(self.row('A'),(True,True,True,2,30))

    def test_day30_inclusive(self):
        self.assertEqual(self.row('A',30),(True,True,True,3,60))

    def test_exactly_enough_followup(self):
        self.assertEqual(self.row('B'),(True,True,True,1,5))

    def test_observed_outcome_does_not_override_censoring(self):
        self.assertEqual(self.row('C'),(False,None,None,None,None))

    def test_multiple_same_day_sessions_are_not_later_day_return(self):
        self.assertEqual(self.row('D'),(True,False,False,0,0))

    def test_day8_purchase_excluded_at7_included_at14(self):
        self.assertEqual(self.row('E'),(True,False,False,0,0))
        self.assertEqual(self.row('E',14),(True,True,True,1,9))

    def test_anchor_tie_break_is_deterministic_and_flagged(self):
        self.assertEqual(self.c.execute('''SELECT anchor_session_id,anchor_channel_id,
          anchor_day_channel_variants FROM user_cohorts WHERE user_id='D' ''').fetchone(),('d_a',1,2))

    def test_first_observed_user_is_not_automatically_ga4_new(self):
        self.assertEqual(self.c.execute("SELECT anchor_new_user_flag FROM user_cohorts WHERE user_id='E'").fetchone()[0],0)

    def test_lag_collapses_same_day_sessions(self):
        self.assertEqual(self.c.execute("SELECT count(*) FROM user_activity_days WHERE user_id='D'").fetchone()[0],1)
        self.assertEqual(self.c.execute("SELECT gap_days FROM user_activity_days WHERE user_id='A' ORDER BY activity_date").fetchall(),[(None,),(7,),(23,)])

    def test_fixed_population_denominator_and_monotonicity(self):
        data=self.c.execute((ROOT/'sql/08_fixed_population.sql').read_text()).fetchall()
        self.assertEqual([r[1] for r in data],[3,3,3])
        self.assertEqual([r[3] for r in data],[1,2,2])

    def test_channel_sensitivity_removes_varying_users(self):
        rows=self.c.execute((ROOT/'sql/05_channel_sensitivity.sql').read_text()).fetchall()
        all7=sum(r[3] for r in rows if r[0]=='All observed users' and r[2]==7)
        consistent7=sum(r[3] for r in rows if r[0]=='Consistent channel only' and r[2]==7)
        self.assertEqual((all7,consistent7),(5,4))

    def test_negative_purchase_age_remains_detectable(self):
        self.c.execute("INSERT INTO fact_purchases VALUES('D','2020-12-31',3)")
        self.build()
        self.assertEqual(self.c.execute("SELECT days_to_first_purchase FROM user_cohorts WHERE user_id='D'").fetchone()[0],-1)


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CohortSemantics)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    (ROOT/'audit/fixture_tests.json').write_text(json.dumps({
      'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
      'failures':len(result.failures),'errors':len(result.errors),
      'scope':'Hand-calculated synthetic edge cases only; project business findings use audited GA4 data.'},indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
