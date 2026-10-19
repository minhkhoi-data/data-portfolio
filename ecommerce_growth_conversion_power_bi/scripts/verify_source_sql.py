"""Independent, disk-backed SQL check of every bundled event/session/purchase.

No analytical production functions are imported. Requires requirements-verification.txt.
DuckDB is limited to 1 GB and one thread; temporary tables are not deliverables.
"""
from pathlib import Path
import csv,hashlib,json,tempfile,time
from datetime import datetime,timezone
import duckdb

ROOT=Path(__file__).resolve().parents[1]
STAGES=['view_item','add_to_cart','begin_checkout','purchase']

def main():
    checks=[];start=time.monotonic()
    def check(name,condition,detail):
        checks.append({'check':name,'status':'PASS' if bool(condition) else 'FAIL','evidence':detail})
        if not condition:raise AssertionError(name+': '+str(detail))
    with tempfile.TemporaryDirectory(prefix='ga4_sql_qa_') as temporary:
        con=duckdb.connect(str(Path(temporary)/'qa.duckdb'))
        con.execute("SET memory_limit='1GB'; SET threads=1; SET preserve_insertion_order=true")
        def read(path):
            escaped=str(path).replace("'","''")
            return con.sql("SELECT * FROM read_csv('"+escaped+"',header=true,all_varchar=true,nullstr='__GA4_QA_NULL_SENTINEL__',parallel=false)")
        read(ROOT/'data/source/ga4_events.csv.gz').create_view('input_source')
        con.execute('''CREATE TABLE events AS SELECT row_number() OVER () AS source_row,
          event_date,event_name,event_id,user_pseudo_id AS user_id,
          user_pseudo_id||'|'||ga_session_id AS session_id, CAST(event_timestamp AS BIGINT) AS ts,
          traffic_source AS source,traffic_medium AS medium,device_category,geo_country,geo_continent,
          TRY_CAST(NULLIF(session_engaged,'') AS DOUBLE) AS engaged,
          TRY_CAST(NULLIF(ga_session_number,'') AS DOUBLE) AS session_number,
          TRY_CAST(NULLIF(engagement_time_msec,'') AS DOUBLE) AS engagement_ms,
          ecommerce_transaction_id AS transaction_id,event_timestamp,
          TRY_CAST(NULLIF(ecommerce_purchase_revenue_in_usd,'') AS DECIMAL(20,6)) AS revenue,
          TRY_CAST(NULLIF(ecommerce_total_item_quantity,'') AS BIGINT) AS total_quantity,
          TRY_CAST(NULLIF(ecommerce_unique_items,'') AS BIGINT) AS distinct_products,currency
          FROM input_source''')
        provenance=json.loads((ROOT/'data/source/provenance.json').read_text())
        count=con.execute('SELECT count(*) FROM events').fetchone()[0]
        check('All bundled source rows inspected',count==provenance['source_rows'],count)
        check('Source event IDs unique',con.execute('SELECT count(*)=count(DISTINCT event_id) FROM events').fetchone()[0],count)
        print(f'SQL loaded {count:,} source events',flush=True)
        con.execute('''CREATE TABLE oracle_sessions AS SELECT session_id,
          arg_min(user_id,struct_pack(ts:=ts,row_id:=source_row)) AS user_id,
          strftime(strptime(arg_min(event_date,struct_pack(ts:=ts,row_id:=source_row)),'%Y%m%d'),'%Y-%m-%d') AS session_date,
          arg_min(source,struct_pack(ts:=ts,row_id:=source_row)) AS source,
          arg_min(medium,struct_pack(ts:=ts,row_id:=source_row)) AS medium,
          arg_min(device_category,struct_pack(ts:=ts,row_id:=source_row)) AS device_category,
          arg_min(geo_country,struct_pack(ts:=ts,row_id:=source_row)) AS country,
          arg_min(geo_continent,struct_pack(ts:=ts,row_id:=source_row)) AS region_group,
          CASE WHEN count(engaged)>0 THEN 1 ELSE 0 END AS engagement_known,
          max(engaged) AS engaged_session,coalesce(sum(engagement_ms),0)/1000.0 AS engagement_seconds,
          CASE WHEN bool_or(event_name='first_visit') OR min(session_number)=1 THEN 1 WHEN min(session_number)>1 THEN 0 ELSE -1 END AS is_new_user,
          count(*) FILTER (WHERE event_name='page_view') AS pageviews,
          max(CASE WHEN event_name='view_item' THEN 1 ELSE 0 END) AS view_item,
          max(CASE WHEN event_name='add_to_cart' THEN 1 ELSE 0 END) AS add_to_cart,
          max(CASE WHEN event_name='begin_checkout' THEN 1 ELSE 0 END) AS begin_checkout,
          max(CASE WHEN event_name='purchase' THEN 1 ELSE 0 END) AS purchase,
          count(*) AS event_count,count(*) FILTER (WHERE event_name='purchase') AS purchase_event_count,
          coalesce(sum(revenue) FILTER (WHERE event_name='purchase'),0) AS session_revenue
          FROM events GROUP BY session_id''')
        for i,stage in enumerate(STAGES):
            if i==0:
                con.execute(f"CREATE TABLE stage_{i} AS SELECT session_id,min(ts) AS reached FROM events WHERE event_name=? GROUP BY session_id",[stage])
            else:
                con.execute(f"CREATE TABLE stage_{i} AS SELECT e.session_id,min(e.ts) AS reached FROM events e JOIN stage_{i-1} p ON e.session_id=p.session_id AND e.ts>p.reached WHERE e.event_name=? GROUP BY e.session_id",[stage])
            con.execute(f'ALTER TABLE oracle_sessions ADD COLUMN ordered_{stage} INTEGER')
            con.execute(f'UPDATE oracle_sessions SET ordered_{stage}=CASE WHEN session_id IN (SELECT session_id FROM stage_{i}) THEN 1 ELSE 0 END')
        print('SQL independently reconstructed session aggregates and strict ordered funnel',flush=True)
        con.execute('''ALTER TABLE oracle_sessions ADD COLUMN channel VARCHAR;
          UPDATE oracle_sessions SET channel=CASE
          WHEN lower(trim(source)) IN ('','<other>','(not set)','not set','(data deleted)') OR lower(trim(medium)) IN ('','<other>','(not set)','not set','(data deleted)') THEN 'Unknown / masked'
          WHEN lower(trim(source))='(direct)' AND lower(trim(medium)) IN ('(none)','none') THEN 'Direct'
          WHEN lower(trim(medium))='organic' THEN 'Organic Search'
          WHEN lower(trim(medium))='email' THEN 'Email'
          WHEN lower(trim(medium)) IN ('cpc','ppc','paidsearch') THEN 'Paid Search'
          WHEN lower(trim(medium)) IN ('display','cpm','banner') THEN 'Display'
          WHEN lower(trim(medium)) IN ('social','social-network','social-media') THEN 'Social'
          WHEN lower(trim(medium))='affiliate' THEN 'Affiliates'
          WHEN lower(trim(medium))='referral' THEN 'Referral' ELSE 'Other observed' END;
          UPDATE oracle_sessions SET device_category=CASE WHEN device_category IN ('','<Other>','(not set)') THEN 'Unknown / masked' ELSE device_category END,
          country=CASE WHEN country IN ('','<Other>','(not set)') THEN 'Unknown / masked' ELSE country END,
          region_group=CASE WHEN region_group IN ('','<Other>','(not set)') THEN 'Unknown / masked' ELSE region_group END''')
        for name in ['fact_sessions','fact_purchases','dim_channel','dim_device','dim_geo']:
            read(ROOT/'data'/f'{name}.csv').create_view('delivered_'+name)
        con.execute('''CREATE VIEW delivered_sessions AS SELECT s.*,c.channel,d.device_category,g.country,g.region_group FROM delivered_fact_sessions s
          LEFT JOIN delivered_dim_channel c USING(channel_id) LEFT JOIN delivered_dim_device d USING(device_id) LEFT JOIN delivered_dim_geo g USING(geo_id)''')
        expected_count=con.execute('SELECT count(*) FROM oracle_sessions').fetchone()[0]
        actual_count=con.execute('SELECT count(*) FROM delivered_sessions').fetchone()[0]
        check('Session population and unique keys',expected_count==actual_count and con.execute('SELECT count(*)=count(DISTINCT session_id) FROM delivered_sessions').fetchone()[0],{'expected':expected_count,'actual':actual_count})
        check('Every session key matches raw input',con.execute('SELECT count(*) FROM oracle_sessions o FULL OUTER JOIN delivered_sessions d USING(session_id) WHERE o.session_id IS NULL OR d.session_id IS NULL').fetchone()[0]==0,expected_count)
        text_fields=['user_id','session_date','source','medium','channel','device_category','country','region_group']
        numeric_fields=['engagement_known','engaged_session','engagement_seconds','is_new_user','pageviews',*STAGES,*['ordered_'+s for s in STAGES],'event_count','purchase_event_count','session_revenue']
        for field in text_fields+numeric_fields:
            actual=f'd."{field}"' if field in text_fields else f'TRY_CAST(NULLIF(d."{field}",\'\') AS DOUBLE)'
            expected=f'o."{field}"'
            condition=f'{actual} IS DISTINCT FROM {expected}' if field in text_fields else f'NOT (({actual} IS NULL AND {expected} IS NULL) OR ({actual} IS NOT NULL AND {expected} IS NOT NULL AND abs({actual}-{expected})<=0.000001))'
            mismatches=con.execute(f'SELECT count(*) FROM oracle_sessions o JOIN delivered_sessions d USING(session_id) WHERE {condition}').fetchone()[0]
            check('Every session: '+field,mismatches==0,{'rows':expected_count,'mismatches':mismatches})
        con.execute('''CREATE TABLE oracle_purchases AS SELECT e.source_row AS purchase_key,e.event_id AS source_event_id,e.session_id,e.user_id,
          strftime(strptime(e.event_date,'%Y%m%d'),'%Y-%m-%d') AS purchase_date,e.event_timestamp,e.transaction_id,
          e.revenue AS purchase_revenue_usd,e.total_quantity,e.distinct_products,e.currency,
          CASE WHEN e.transaction_id IN ('','(not set)','<Other>') THEN 0 ELSE 1 END AS transaction_id_known,
          o.channel,o.device_category,o.country,o.region_group FROM events e JOIN oracle_sessions o USING(session_id) WHERE e.event_name='purchase';
          CREATE VIEW delivered_purchases AS SELECT p.*,c.channel,d.device_category,g.country,g.region_group FROM delivered_fact_purchases p
          LEFT JOIN delivered_dim_channel c USING(channel_id) LEFT JOIN delivered_dim_device d USING(device_id) LEFT JOIN delivered_dim_geo g USING(geo_id)''')
        expected_purchase_count=con.execute('SELECT count(*) FROM oracle_purchases').fetchone()[0]
        actual_purchase_count=con.execute('SELECT count(*) FROM delivered_purchases').fetchone()[0]
        check('Purchase population and unique source-row keys',expected_purchase_count==actual_purchase_count and con.execute('SELECT count(*)=count(DISTINCT purchase_key) FROM delivered_purchases').fetchone()[0],{'expected':expected_purchase_count,'actual':actual_purchase_count})
        check('Every purchase key matches raw input',con.execute('SELECT count(*) FROM oracle_purchases o FULL OUTER JOIN delivered_purchases d ON o.purchase_key=TRY_CAST(d.purchase_key AS BIGINT) WHERE o.purchase_key IS NULL OR d.purchase_key IS NULL').fetchone()[0]==0,expected_purchase_count)
        ptext=['source_event_id','session_id','user_id','purchase_date','event_timestamp','transaction_id','currency','channel','device_category','country','region_group']
        pnumeric=['purchase_revenue_usd','total_quantity','distinct_products','transaction_id_known']
        for field in ptext+pnumeric:
            actual=f'd."{field}"' if field in ptext else f'TRY_CAST(NULLIF(d."{field}",\'\') AS DOUBLE)'
            expected=f'o."{field}"'
            condition=f'{actual} IS DISTINCT FROM {expected}' if field in ptext else f'NOT (({actual} IS NULL AND {expected} IS NULL) OR ({actual} IS NOT NULL AND {expected} IS NOT NULL AND abs({actual}-{expected})<=0.000001))'
            mismatches=con.execute(f'SELECT count(*) FROM oracle_purchases o JOIN delivered_purchases d ON o.purchase_key=TRY_CAST(d.purchase_key AS BIGINT) WHERE {condition}').fetchone()[0]
            check('Every purchase: '+field,mismatches==0,{'rows':expected_purchase_count,'mismatches':mismatches})
        print(f'SQL checked all {expected_count:,} sessions and {expected_purchase_count:,} purchases',flush=True)
        summary={'source_events':count,'sessions':expected_count,'purchase_events':expected_purchase_count,'unknown_sessions':con.execute("SELECT count(*) FROM oracle_sessions WHERE channel='Unknown / masked'").fetchone()[0],'strict_funnel':[con.execute(f'SELECT count(*) FROM stage_{i}').fetchone()[0] for i in range(4)],'purchase_revenue_usd':float(con.execute('SELECT sum(purchase_revenue_usd) FROM oracle_purchases').fetchone()[0])}
        con.close()
    record={'status':'PASS','checked_utc':datetime.now(timezone.utc).isoformat(),'checks_passed':len(checks),'checks':checks,'summary':summary,'duckdb_version':duckdb.__version__,'memory_limit':'1GB','threads':1,'elapsed_seconds':round(time.monotonic()-start,1),'production_functions_imported':False,'scope':'Complete bundled source to delivered fact-row validation; does not execute DAX, M or compare the Kaggle projection with a new external download.'}
    (ROOT/'audit/evidence/takeover_sql_validation.json').write_text(json.dumps(record,indent=2))
    print(json.dumps({k:record[k] for k in ['status','checks_passed','summary','elapsed_seconds']},indent=2))

if __name__=='__main__':main()
