"""Known-answer fixtures and counterexamples; no fixed native-data magic totals."""
import importlib.util
import itertools
import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pipeline',ROOT/'analysis/run_analysis.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
CFG=m.load_config()

def frame(rows):
    return pd.DataFrame(rows,columns=m.RAW_COLUMNS)

def row(invoice='1',date='2020-01-01 10:00:00',cid=1,qty=1,price=10,stock='A',desc='Product'):
    return [invoice,stock,desc,qty,date,price,cid,'UK']

class KnownAnswers(unittest.TestCase):
    def test_lines_not_orders_and_credit_guard(self):
        r=frame([row(),row(stock='B',qty=2,price=5),row('2','2020-01-01 10:00:00'),row('C2','2020-01-02 10:00:00',qty=-1),row('3','2020-04-10 10:00:00',cid=2)])
        p,cr,si,ledger,q,start,end=m.clean_transactions(r)
        orders,c,cut,snapshot=m.build_customers(p,cr,end,CFG)
        x=c.set_index('Customer ID').loc[1]
        self.assertEqual(x.Orders,2);self.assertEqual(x.PurchaseDays,1)
        self.assertEqual(x.GrossPurchaseValueGBP,30);self.assertEqual(x.CreditValueGBP,10);self.assertEqual(x.NetRecordedValueGBP,20)
        self.assertTrue(x.RepeatCustomer);self.assertFalse(x.RepeatOnAnotherDay)
        self.assertEqual(x.DaysToSecondOrder,0)
    def test_exact_90_day_boundary_and_censoring(self):
        end='2020-04-10 10:00:00'
        r=frame([row('1'),row('2','2020-03-31 10:00:00'),row('3',cid=2),row('4','2020-03-31 10:00:01',cid=2),row('5','2020-01-11 10:00:01',cid=3),row('6',end,cid=4)])
        p,cr,si,l,q,st,en=m.clean_transactions(r)
        o,c,cut,sn=m.build_customers(p,cr,en,CFG);c=c.set_index('Customer ID')
        self.assertTrue(c.loc[1,'Eligible90']);self.assertTrue(c.loc[1,'SecondOrderWithin90'])
        self.assertFalse(c.loc[2,'SecondOrderWithin90'])
        self.assertFalse(c.loc[3,'Eligible90']);self.assertFalse(c.loc[4,'Eligible90'])
    def test_equal_values_permutation_and_collapsed_bins(self):
        x=pd.Series([1,1,1,2,2,3,4,8,8,9])
        score,cut=m.stable_score(x,CFG['score_quantiles'])
        shuffle=x.sample(frac=1,random_state=42);s2,_=m.stable_score(shuffle,CFG['score_quantiles'])
        pd.testing.assert_series_equal(score,s2.sort_index())
        self.assertEqual(score.groupby(x).nunique().max(),1)
        equal,_=m.stable_score(pd.Series([1]*5),CFG['score_quantiles']);self.assertEqual(set(equal),{1})
        reverse,_=m.stable_score(x,CFG['score_quantiles'],True);self.assertTrue((reverse+score).eq(6).all())
    def test_segment_coverage_precedence(self):
        labels=[m.rfm_segment(*scores) for scores in itertools.product(range(1,6),repeat=3)]
        self.assertEqual(len(labels),125);self.assertTrue(all(labels))
        self.assertEqual(m.rfm_segment(5,5,5),'Champions (relative)')
        self.assertEqual(m.rfm_segment(5,5,1),'Recent frequent')
        self.assertNotIn('New Customers',labels)
        from collections import Counter
        self.assertEqual(dict(Counter(labels)), {
            'Champions (relative)': 8, 'Recent frequent': 22,
            'Recent mid-frequency': 20, 'Recent low-frequency': 10,
            'Lapsed frequent': 30, 'Lapsed low-frequency': 20, 'Intermediate': 15})
    def test_lifecycle_value_and_credit_boundaries(self):
        base=pd.DataFrame({'Orders':[1,2,2,2,2,2], 'RecencyDays':[90,90,91,180,181,1], 'M_Score':[5,5,5,1,5,5], 'F_Score':[1,5,5,2,5,5], 'NetRecordedValueGBP':[100]*5+[0], 'CreditToGrossRatio':[0]*5+[1], 'RFM Segment':['Recent low-frequency','Champions (relative)','Lapsed frequent','Intermediate','Lapsed frequent','Champions (relative)']})
        c=m.assign_actions(base,CFG)
        self.assertEqual(c.Lifecycle.tolist(),['Recent single-order','Active repeat','At risk','At risk','Dormant','Active repeat'])
        self.assertEqual(c.loc[1,'CRM Priority'],'Protect frequent higher-value')
        self.assertEqual(c.loc[2,'CRM Priority'],'Win-back frequent higher-value test')
        self.assertEqual(c.loc[4,'CRM Priority'],'Review dormant higher-value')
        self.assertEqual(c.loc[5,'CRM Priority'],'Review credits before outreach')
        # M changes treatment even for the same at-risk R/F, not only Champions.
        low=base.iloc[[2]].copy();low['M_Score']=1
        self.assertEqual(m.assign_actions(low,CFG).iloc[0]['CRM Priority'],'Lower-cost win-back test')
        highcredit=base.iloc[[1]].copy();highcredit['CreditToGrossRatio']=.5
        self.assertEqual(m.assign_actions(highcredit,CFG).iloc[0]['CRM Priority'],'Review credits before outreach')
    def test_future_cohorts_nan_and_observed_zero(self):
        orders=pd.DataFrame({'Customer ID':[1,2,3], 'OrderDate':pd.to_datetime(['2020-01-01','2020-02-01','2020-03-09']), 'Invoice':['1','2','3']})
        counts,retention,kpis,observed,last=m.cohort_analysis(orders,pd.Timestamp('2020-01-01'),pd.Timestamp('2020-03-09'),CFG)
        self.assertEqual(last,'2020-02')
        self.assertEqual(retention.loc[pd.Period('2020-01'),1],0)
        self.assertTrue(pd.isna(retention.loc[pd.Period('2020-02'),1]))
        self.assertTrue(retention.loc[pd.Period('2020-03')].isna().all())
        self.assertTrue(pd.isna(kpis.set_index('Month').loc[12,'WeightedRetentionRate']))
    def test_cleaning_overlap_row_and_value_reconciliation(self):
        r=frame([row(),row(),row('C1',qty=-1),row('2',cid=None),row('3',date='bad date'),row('4',qty=0)])
        p,cr,si,l,q,st,en=m.clean_transactions(r)
        self.assertEqual(len(p),1);self.assertEqual(len(cr),1)
        self.assertEqual(l.RowsRemoved.sum()+len(si),len(r))
        self.assertAlmostEqual(l.iloc[0].SignedValueAfterGBP,l.iloc[-1].SignedValueAfterGBP+l.SignedValueRemovedGBP.sum())
    def test_empty_missing_and_invoice_conflicts(self):
        with self.assertRaisesRegex(ValueError,'Missing required'):m.clean_transactions(pd.DataFrame({'x':[1]}))
        with self.assertRaisesRegex(ValueError,'No valid positive'):m.clean_transactions(frame([row('C1',qty=-1)]))
        with self.assertRaisesRegex(ValueError,'multiple customers'):m.clean_transactions(frame([row(),row(cid=2)]))
        with self.assertRaisesRegex(ValueError,'spans multiple'):m.clean_transactions(frame([row(),row(date='2020-01-02',stock='B')]))
    def test_no_eligible_not_zero(self):
        t,c,r,o,s=m.analyse(frame([row()]),CFG)
        self.assertIsNone(s['repeat90_rate']);self.assertEqual(s['eligible90_customers'],0)
        self.assertTrue(t['repeat_90_curve'].CumulativeRepeatRate.isna().all())
    def test_duplicate_sensitivity_survives_refresh(self):
        # Reproduce the delivery bug: a second pipeline call (as made by the
        # notebook) replaces outputs. The sensitivity must still be present.
        r=frame([row(), row(), row('2','2020-04-10 10:00:00',cid=2)])
        with tempfile.TemporaryDirectory() as td:
            data=Path(td)/'fixture.csv';r.to_csv(data,index=False)
            dest=Path(td)/'release'
            for _ in range(2):
                m.run_pipeline(data_path=data,destination=dest)
                sensitivity=json.loads((dest/'outputs/duplicate_sensitivity.json').read_text())
                self.assertEqual(sensitivity['PurchaseLines'],3)
                self.assertEqual(sensitivity['BasePurchaseLines'],2)
                self.assertEqual(sensitivity['GrossPurchaseValueGBP'],30)
                self.assertEqual(sensitivity['BaseGrossPurchaseValueGBP'],20)

    def test_unrepresentable_identifiers_and_quantities_excluded(self):
        # Large IDs previously wrapped negative on int64 conversion.
        r=frame([row(cid=1e20), row('2',cid=2), row('3',qty=1e20,cid=3)])
        p,cr,si,ledger,q,*_=m.clean_transactions(r)
        self.assertEqual(p['Customer ID'].tolist(),[2])
        self.assertEqual(len(si),1)
        self.assertEqual(int(q.set_index('Check').loc['Invalid customer ID','Count']),1)
        self.assertEqual(int(ledger.RowsRemoved.sum()),2)
    def test_no_eligible_chart_labels_not_zero(self):
        from unittest.mock import patch
        import matplotlib.axes
        r=frame([row()])
        tables,counts,retention,observed,stats=m.analyse(r,CFG)
        captured=[]
        axes=[]
        original=matplotlib.axes.Axes.annotate
        def capture(ax,text,*args,**kwargs):
            captured.append(text)
            axes.append(ax)
            return original(ax,text,*args,**kwargs)
        with tempfile.TemporaryDirectory() as td, patch.object(matplotlib.axes.Axes,'annotate',capture):
            m.create_figures(tables,retention,stats,Path(td))
        self.assertEqual(sum('N/A — no eligible customers' in x for x in captured),4)
        left,right=axes[-1].get_xlim()
        self.assertLessEqual(left,0);self.assertGreaterEqual(right,3)

if __name__=='__main__':unittest.main(verbosity=2)
