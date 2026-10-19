"""Independent SQL reconciliation, sensitivity and delivery checks for this release."""
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from run_analysis import ROOT, load_config, build_customers

def main():
    cfg=load_config()
    raw=pd.read_csv(ROOT/'data/online_retail_II.csv.gz',low_memory=False)
    saved=pd.read_csv(ROOT/'outputs/customer_lifecycle_table.csv')
    stats=json.loads((ROOT/'outputs/run_summary.json').read_text())
    # Independent native-input preparation; known source schema/dtypes validated separately.
    base=raw.dropna(subset=['Customer ID']).loc[lambda d:(d.Price>0)&(d.Quantity!=0)].copy()
    base['Customer ID']=base['Customer ID'].astype(int)
    base['InvoiceDate']=pd.to_datetime(base.InvoiceDate)
    signed=base.drop_duplicates().copy()
    signed['LineValueGBP']=signed.Quantity*signed.Price
    checks=[]
    def check(name,cond,detail):
        if not bool(cond):raise AssertionError(name+': '+str(detail))
        checks.append({'Check':name,'Verdict':'PASS','Evidence':detail})
    with sqlite3.connect(':memory:') as db:
        db.execute('PRAGMA temp_store=MEMORY')
        signed[['Customer ID','Invoice','InvoiceDate','Quantity','Price']].rename(columns={'Customer ID':'CustomerID'}).to_sql('lines',db,index=False,chunksize=10000)
        db.executescript('''
        CREATE TABLE orders AS SELECT CustomerID,Invoice,MIN(InvoiceDate) AS OrderDate,SUM(Quantity*Price) AS Gross
        FROM lines WHERE Quantity>0 AND UPPER(Invoice) NOT LIKE 'C%' GROUP BY CustomerID,Invoice;
        CREATE TABLE numbered AS SELECT *,ROW_NUMBER() OVER(PARTITION BY CustomerID ORDER BY OrderDate,Invoice) AS rn FROM orders;
        CREATE TABLE credits AS SELECT CustomerID,-SUM(Quantity*Price) AS Credit FROM lines WHERE Quantity<0 AND UPPER(Invoice) LIKE 'C%' GROUP BY CustomerID;
        ''')
        sql=pd.read_sql_query('''SELECT n.CustomerID,COUNT(*) AS Orders,SUM(n.Gross) AS Gross,
          MIN(n.OrderDate) AS FirstDate,MAX(n.OrderDate) AS LastDate,
          MAX(CASE WHEN rn=2 THEN n.OrderDate END) AS SecondDate,
          COALESCE(c.Credit,0) AS Credit
          FROM numbered n LEFT JOIN credits c ON n.CustomerID=c.CustomerID GROUP BY n.CustomerID''',db)
        result=sql.merge(saved,on=None,left_on='CustomerID',right_on='Customer ID',validate='one_to_one')
        check('SQL customer population',len(sql)==len(saved) and len(result)==len(saved),f'{len(saved)} customer rows')
        check('SQL distinct invoice frequency',result.Orders_x.eq(result.Orders_y).all(),f'{int(sql.Orders.sum())} purchase invoices')
        check('SQL gross value',np.allclose(result.Gross,result.GrossPurchaseValueGBP,atol=.01,rtol=0),f'GBP {sql.Gross.sum():.3f}')
        check('SQL credits and net recorded value',np.allclose(result.Credit,result.CreditValueGBP,atol=.01,rtol=0) and np.allclose(result.Gross-result.Credit,result.NetRecordedValueGBP,atol=.01,rtol=0),f'GBP {(sql.Gross-sql.Credit).sum():.3f} net')
        sql90=db.execute('''WITH customer AS (SELECT CustomerID,MIN(OrderDate) FirstDate,
           MAX(CASE WHEN rn=2 THEN OrderDate END) SecondDate FROM numbered GROUP BY CustomerID)
           SELECT SUM(julianday(FirstDate)+90<=julianday(?)),
           SUM(CASE WHEN julianday(FirstDate)+90<=julianday(?) AND julianday(SecondDate)-julianday(FirstDate)<=90 THEN 1 ELSE 0 END)
           FROM customer''',(stats['observation_end'],stats['observation_end'])).fetchone()
        check('SQL exact elapsed 90-day rate',sql90==(stats['eligible90_customers'],stats['second_order90_customers']),f'{sql90[1]}/{sql90[0]}')
        # Calendar period reference implemented in SQL, not the pipeline's pivot/masking.
        rates=pd.read_csv(ROOT/'outputs/retention_kpis.csv')
        for h in rates.Month:
            # Count customers, rather than cohort rows. The target month is
            # eligible only when it is a complete observed calendar month;
            # this mirrors the pipeline's explicit masking of future/partial
            # cohort cells while keeping the reconciliation independent.
            row=db.execute('''WITH first AS (
                SELECT CustomerID,MIN(substr(OrderDate,1,7)) AS Cohort
                FROM orders GROUP BY CustomerID
             ), eligible AS (
                SELECT CustomerID,Cohort,
                       date(Cohort||'-01', ?) AS TargetMonth
                FROM first
                WHERE date(Cohort||'-01', ?)<=date(?||'-01')
             ), active AS (
                SELECT DISTINCT e.CustomerID
                FROM eligible e JOIN orders o ON e.CustomerID=o.CustomerID
                WHERE substr(o.OrderDate,1,7)=strftime('%Y-%m',e.TargetMonth)
             )
             SELECT (SELECT COUNT(*) FROM eligible),(SELECT COUNT(*) FROM active)''',
             (f'+{int(h)} months',f'+{int(h)} months',stats['last_complete_month'])).fetchone()
            actual=rates.set_index('Month').loc[h]
            check(f'SQL month-{h} eligible/active count',row==(actual.EligibleCustomers,actual.ActiveCustomers),f'{row[1]}/{row[0]}')
    # De-duplication is not proof that duplicates were erroneous in the source.
    # Retain all otherwise valid lines as a sensitivity scenario, no source edits.
    base['LineValueGBP']=base.Quantity*base.Price
    p=base.loc[(base.Quantity>0)&(~base.Invoice.astype(str).str.upper().str.startswith('C'))]
    cr=base.loc[(base.Quantity<0)&(base.Invoice.astype(str).str.upper().str.startswith('C'))]
    _, alt,_,_=build_customers(p,cr,pd.Timestamp(stats['observation_end']),cfg)
    compare=alt.merge(saved[['Customer ID','CRM Priority']],on='Customer ID',suffixes=('_alternative','_base'),validate='one_to_one')
    duplicate_sensitivity={'Scenario':'Retain exact duplicate rows', 'PurchaseLines':len(p), 'BasePurchaseLines':stats['purchase_lines'],
        'GrossPurchaseValueGBP':float(alt.GrossPurchaseValueGBP.sum()),'BaseGrossPurchaseValueGBP':stats['gross_purchase_value_gbp'],
        'NetRecordedValueGBP':float(alt.NetRecordedValueGBP.sum()),'BaseNetRecordedValueGBP':stats['net_recorded_value_gbp'],
        'CustomersWithChangedAction':int(compare['CRM Priority_alternative'].ne(compare['CRM Priority_base']).sum())}
    sensitivity_path=ROOT/'outputs/duplicate_sensitivity.json'
    check('Pipeline publishes duplicate sensitivity',sensitivity_path.is_file(),str(sensitivity_path.relative_to(ROOT)))
    published=json.loads(sensitivity_path.read_text())
    check('Duplicate sensitivity reconciles independently',
          set(published)==set(duplicate_sensitivity) and all(
              np.isclose(published[k],v,rtol=0,atol=.01) if isinstance(v,(int,float)) else published[k]==v
              for k,v in duplicate_sensitivity.items()), duplicate_sensitivity)
    check('Duplicate sensitivity population',len(alt)==len(saved),duplicate_sensitivity)
    raw_end=pd.to_datetime(raw.InvoiceDate).max()
    check('Source observation end',str(raw_end)==stats['observation_end'],str(raw_end))
    check('Source hash',hashlib.sha256((ROOT/'data/online_retail_II.csv.gz').read_bytes()).hexdigest()==stats['input_sha256'],stats['input_sha256'])
    for first_name,score in [('RecencyDays','R_Score'),('Orders','F_Score'),('NetRecordedValueGBP','M_Score')]:
        check('Equal values share score: '+score,saved.groupby(first_name)[score].nunique().le(1).all(),'Every observed tie group')
    # Negative CLI tests: destination marker must survive, no new success outputs.
    with tempfile.TemporaryDirectory() as temp:
        temp=Path(temp);bad=temp/'bad.csv';pd.DataFrame({'wrong':[1]}).to_csv(bad,index=False)
        output=temp/'delivery';output.mkdir();marker=output/'marker.txt';marker.write_text('old')
        run=subprocess.run([sys.executable,str(ROOT/'analysis/run_analysis.py'),'--data',str(bad),'--destination',str(output)],capture_output=True,text=True)
        check('Malformed schema fails closed',run.returncode!=0 and 'FAIL' in run.stderr and 'PASS' not in run.stdout and marker.read_text()=='old' and not (output/'outputs').exists(),run.stderr.strip())
        missing=subprocess.run([sys.executable,str(ROOT/'analysis/run_analysis.py'),'--data',str(temp/'missing.csv'),'--destination',str(output)],capture_output=True,text=True)
        check('Missing input fails closed',missing.returncode!=0 and 'PASS' not in missing.stdout and not (output/'outputs').exists(),'nonzero exit, no published outputs')
    # All locally linked portfolio files are real; external source links are separate.
    for path in [ROOT/'README.md',ROOT/'memo/business_memo.md',ROOT/'docs/METHODS.md',ROOT/'docs/LEARNING_GUIDE_VI.md']:
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if '://' not in target and not target.startswith('#'):
                target_path=path.parent/target.split('#')[0]
                # This report is the current validator's own generated output;
                # its successful write immediately below is the existence check.
                generated_here=(target_path==ROOT/'audit/independent_validation.json')
                check('Local link '+str(path.relative_to(ROOT))+' -> '+target,
                      generated_here or target_path.exists(),
                      'generated by this validator' if generated_here else target)
    report={'scope':'independent native-data SQL checks, counterexamples and links; personal HR understanding not assessed','checks':checks,'checks_passed':len(checks),'environment':{'python':sys.version.split()[0],'pandas':pd.__version__,'numpy':np.__version__,'sqlite':sqlite3.sqlite_version}}
    (ROOT/'audit/independent_validation.json').write_text(json.dumps(report,indent=2))
    print(f'PASS — {len(checks)} independent delivery checks')
    print(json.dumps(duplicate_sensitivity,indent=2))

if __name__=='__main__':main()
