"""Rebuild analytical tables from the exact, all-row Kaggle column projection.

Revenue remains a purchase-event sum, not verified order accounting or profit.
Observed purchase activity and a conservative ordered funnel are separate.
"""
from pathlib import Path
from decimal import Decimal
import collections, csv, gzip, hashlib, json, os
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
STAGES=['view_item','add_to_cart','begin_checkout','purchase']
CONTROL_EVENTS=['first_visit','session_start','page_view','user_engagement',*STAGES,'add_shipping_info','add_payment_info','refund']
TABLES={'FactSessions':'fact_sessions','FactPurchases':'fact_purchases','DimDate':'dim_date',
        'DimChannel':'dim_channel','DimDevice':'dim_device','DimGeo':'dim_geo'}

def require(condition,message):
    if not bool(condition):raise ValueError(message)

def sha256(path):
    d=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):d.update(b)
    return d.hexdigest()

def channel(source,medium):
    """Declared grouping of FIRST-USER source/medium; unknowns stay visible."""
    s=source.lower().strip();m=medium.lower().strip()
    masked={'','<other>','(not set)','not set','(data deleted)'}
    if s in masked or m in masked:return 'Unknown / masked'
    if s=='(direct)' and m in {'(none)','none'}:return 'Direct'
    if m=='organic':return 'Organic Search'
    if m=='email':return 'Email'
    if m in {'cpc','ppc','paidsearch'}:return 'Paid Search'
    if m in {'display','cpm','banner'}:return 'Display'
    if m in {'social','social-network','social-media'}:return 'Social'
    if m=='affiliate':return 'Affiliates'
    if m=='referral':return 'Referral'
    return 'Other observed'

def ordered_times(events):
    """Earliest eligible event at each stage, strictly after the prior stage.

    Same-time events cannot establish step order. No missing events are inferred.
    Sessions can be observed without a session_start event in this window.
    """
    previous=None;result={}
    for stage in STAGES:
        candidates=events.loc[events.event_name.eq(stage),['session_id','timestamp']]
        if previous is not None:
            candidates=candidates.join(previous.rename('previous'),on='session_id')
            candidates=candidates.loc[candidates.timestamp.gt(candidates.previous)]
        current=candidates.groupby('session_id',sort=False).timestamp.min()
        result[stage]=current;previous=current
    return result

def source_tables():
    source=ROOT/'data/source/ga4_events.csv.gz'
    provenance=json.loads((ROOT/'data/source/provenance.json').read_text())
    require(sha256(source)==provenance['projection_sha256'],'Source projection hash mismatch')
    frames=[];purchase_frames=[];counts=collections.Counter();purchases=collections.Counter()
    refunds=collections.Counter();missing_users=collections.Counter();missing_sessions=collections.Counter()
    revenues=collections.defaultdict(Decimal);event_counts=collections.Counter();rows=0
    for raw in pd.read_csv(source,dtype=str,keep_default_na=False,chunksize=200000):
        require(list(raw.columns)==provenance['retained_columns'],'Source schema mismatch')
        raw['source_row']=np.arange(rows+1,rows+len(raw)+1,dtype='int64');rows+=len(raw)
        require(raw.event_date.str.fullmatch(r'\d{8}').all(),'Invalid event date')
        require(raw.event_date.between('20201101','20210131').all(),'Unexpected source date range')
        require(raw.event_timestamp.str.fullmatch(r'\d+').all(),'Invalid microsecond timestamp')
        require(raw.ga_session_id.str.fullmatch(r'-?\d+').all(),'Missing/altered session identifier')
        require(raw.user_pseudo_id.ne('').all(),'Missing user identifier; quarantine needed')
        event_counts.update(raw.event_name.value_counts().to_dict())
        selected=raw.loc[raw.event_name.isin(CONTROL_EVENTS)]
        counts.update(selected.event_date.str[:6].value_counts().to_dict())
        for month,g in selected.groupby(selected.event_date.str[:6]):
            missing_users[month]+=int(g.user_pseudo_id.eq('').sum())
            missing_sessions[month]+=int(g.ga_session_id.eq('').sum())
            refunds[month]+=int(g.event_name.eq('refund').sum())
        buy=raw.loc[raw.event_name.eq('purchase')].copy()
        for month,g in buy.groupby(buy.event_date.str[:6]):
            purchases[month]+=len(g)
            for value in g.ecommerce_purchase_revenue_in_usd:
                require(value!='','Missing purchase revenue; no zero imputation')
                amount=Decimal(value);require(amount.is_finite(),'Invalid revenue')
                revenues[month]+=amount
        purchase_frames.append(buy)
        e=raw[['source_row','event_date','event_name','event_id','user_pseudo_id','ga_session_id',
               'event_timestamp','traffic_source','traffic_medium','device_category','geo_country',
               'geo_continent','ga_session_number','session_engaged','engagement_time_msec']].copy()
        e.rename(columns={'event_timestamp':'timestamp','user_pseudo_id':'user_id'},inplace=True)
        e['timestamp']=pd.to_numeric(e.timestamp,errors='raise').astype('int64')
        require(e.timestamp.gt(0).all(),'Nonpositive timestamp')
        e['session_id']=e.user_id+'|'+e.ga_session_id
        for column in ['session_engaged','ga_session_number','engagement_time_msec']:
            e[column]=pd.to_numeric(e[column].replace('',np.nan),errors='raise')
        require(e.session_engaged.dropna().isin([0,1]).all(),'Unrecognized session_engaged value')
        require(e.ga_session_number.dropna().gt(0).all(),'Invalid GA4 session number')
        require(e.engagement_time_msec.dropna().ge(0).all(),'Negative recorded engagement')
        frames.append(e)
        print(f'Loaded {rows:,} events',flush=True)
    require(rows==provenance['source_rows'],'Source row count changed')
    controls=pd.read_csv(ROOT/'data/source/bigquery_source_profile.csv',dtype=str,keep_default_na=False)
    comparison=[]
    for _,c in controls.iterrows():
        month=c.source_month
        observed={'exported_events':counts[month],'purchase_events':purchases[month],'refund_events':refunds[month],
                  'missing_user_events':missing_users[month],'missing_session_events':missing_sessions[month]}
        for k,v in observed.items():require(v==int(c[k]),f'Independent BigQuery control mismatch: {month} {k}')
        require(abs(revenues[month]-Decimal(c.purchase_revenue_usd_sum))<=Decimal('0.01'),'Independent revenue mismatch')
        comparison.append({'source_month':month,**observed,'purchase_revenue_usd_sum':str(revenues[month]),'status':'MATCH'})
    (ROOT/'audit/evidence/source_reconciliation.json').write_text(json.dumps(comparison,indent=2))
    pd.DataFrame(comparison).to_csv(ROOT/'outputs/source_reconciliation.csv',index=False)
    e=pd.concat(frames,ignore_index=True);del frames
    buy=pd.concat(purchase_frames,ignore_index=True);del purchase_frames
    # Earliest timestamp is used for session dimensions/date. Tied dimensions
    # use source row order deterministically, never to infer funnel chronology.
    first=e.loc[e.groupby('session_id',sort=False).timestamp.idxmin()].set_index('session_id')
    s=first[['user_id','event_date','traffic_source','traffic_medium','device_category','geo_country','geo_continent']].copy()
    s.rename(columns={'event_date':'session_date','traffic_source':'source','traffic_medium':'medium',
                      'geo_country':'country','geo_continent':'region_group'},inplace=True)
    s['session_date']=pd.to_datetime(s.session_date,format='%Y%m%d').dt.strftime('%Y-%m-%d')
    for stage in STAGES:e[stage]=e.event_name.eq(stage).astype('int8')
    e['pageviews']=e.event_name.eq('page_view').astype('int8')
    e['first_visit']=e.event_name.eq('first_visit').astype('int8')
    e['engagement_known']=e.session_engaged.notna().astype('int8')
    g=e.groupby('session_id',sort=False)
    metrics=g.agg(pageviews=('pageviews','sum'),view_item=('view_item','max'),add_to_cart=('add_to_cart','max'),
                  begin_checkout=('begin_checkout','max'),purchase=('purchase','max'),
                  engagement_known=('engagement_known','max'),engaged_session=('session_engaged','max'),
                  engagement_ms=('engagement_time_msec','sum'),ga_session_number=('ga_session_number','min'),
                  first_visit=('first_visit','max'),event_count=('event_name','size'))
    s=s.join(metrics);s['engagement_seconds']=s.engagement_ms/1000
    s['is_new_user']=np.select([s.first_visit.eq(1)|s.ga_session_number.eq(1),s.ga_session_number.gt(1)],[1,0],default=-1)
    times=ordered_times(e)
    for stage,t in times.items():s['ordered_'+stage]=s.index.isin(t.index).astype('int8')
    diagnostics={'source_rows':rows,'source_event_counts':dict(event_counts),
      'duplicate_source_event_ids':int(e.event_id.duplicated().sum()),
      'duplicate_purchase_event_ids':int(buy.event_id.duplicated().sum()),
      'sessions_spanning_property_dates':int(g.event_date.nunique().gt(1).sum()),
      'sessions_with_dimension_changes':{c:int(g[c].nunique().gt(1).sum()) for c in ['traffic_source','traffic_medium','device_category','geo_country']},
      'sessions_without_session_start_event':int(len(s)-e.loc[e.event_name.eq('session_start'),'session_id'].nunique()),
      'sessions_with_unknown_engagement':int(s.engagement_known.eq(0).sum()),
      'sessions_with_unknown_new_returning_status':int(s.is_new_user.eq(-1).sum()),
      'purchase_sessions_without_complete_strict_path':int((s.purchase.eq(1)&s.ordered_purchase.eq(0)).sum()),
      'unknown_or_masked_first_user_sessions':None,
      'policy':'No deduplication or inferred events. First-observed session dimensions; source property event dates; strictly increasing funnel timestamps.'}
    del e,g,first
    s['channel']=s.apply(lambda r:channel(r.source,r.medium),axis=1)
    diagnostics['unknown_or_masked_first_user_sessions']=int(s.channel.eq('Unknown / masked').sum())
    # Empty/placeholder geography remains one explicit observable category.
    for c in ['country','region_group','device_category']:
        s[c]=s[c].replace({'':'Unknown / masked','<Other>':'Unknown / masked','(not set)':'Unknown / masked'})
    dimensions={}
    for dim,keys,idcol in [('dim_channel',['channel'],'channel_id'),('dim_device',['device_category'],'device_id'),
                           ('dim_geo',['country','region_group'],'geo_id')]:
        d=s[keys].drop_duplicates().sort_values(keys).reset_index(drop=True);d.insert(0,idcol,np.arange(1,len(d)+1))
        s=s.reset_index().merge(d,on=keys,how='left',validate='many_to_one').set_index('session_id');dimensions[dim]=d
    buy['session_id']=buy.user_pseudo_id+'|'+buy.ga_session_id
    p=buy[['source_row','event_id','session_id','user_pseudo_id','event_date','event_timestamp','ecommerce_transaction_id',
           'ecommerce_purchase_revenue_in_usd','ecommerce_total_item_quantity','ecommerce_unique_items','currency']].copy()
    p.rename(columns={'source_row':'purchase_key','event_id':'source_event_id','user_pseudo_id':'user_id',
      'event_date':'purchase_date','event_timestamp':'event_timestamp','ecommerce_transaction_id':'transaction_id',
      'ecommerce_purchase_revenue_in_usd':'purchase_revenue_usd','ecommerce_total_item_quantity':'total_quantity',
      'ecommerce_unique_items':'distinct_products'},inplace=True)
    p['purchase_date']=pd.to_datetime(p.purchase_date,format='%Y%m%d').dt.strftime('%Y-%m-%d')
    p['purchase_revenue_usd']=pd.to_numeric(p.purchase_revenue_usd,errors='raise')
    for c in ['total_quantity','distinct_products']:p[c]=pd.to_numeric(p[c].replace('',np.nan),errors='raise').astype('Int64')
    p['transaction_id_known']=(~p.transaction_id.isin(['','(not set)','<Other>'])).astype('int8')
    diagnostics['purchase_rows_without_known_transaction_id']=int(p.transaction_id_known.eq(0).sum())
    known=p.loc[p.transaction_id_known.eq(1)]
    diagnostics['additional_rows_with_repeated_known_transaction_id']=int(known.transaction_id.duplicated().sum())
    diagnostics['distinct_repeated_known_transaction_ids']=int(known.groupby('transaction_id').size().gt(1).sum())
    diagnostics['known_transaction_ids_shared_by_users']=int(known.groupby('transaction_id').user_id.nunique().gt(1).sum())
    p=p.merge(s[['channel_id','device_id','geo_id']],left_on='session_id',right_index=True,how='left',validate='many_to_one')
    s['session_revenue']=s.index.map(p.groupby('session_id').purchase_revenue_usd.sum()).fillna(0)
    s['purchase_event_count']=s.index.map(p.groupby('session_id').size()).fillna(0).astype('int64')
    s['engaged_session']=s.engaged_session.astype('Int64')
    session_columns=['user_id','session_date','channel_id','device_id','geo_id','source','medium','is_new_user',
       'engagement_known','engaged_session','engagement_seconds','pageviews',*STAGES,
       *['ordered_'+c for c in STAGES],'event_count','purchase_event_count','session_revenue']
    s=s[session_columns].sort_index().reset_index();p=p.sort_values('purchase_key').reset_index(drop=True)
    dt=pd.Series(pd.date_range('2020-11-01','2021-01-31'))
    dates=pd.DataFrame({'date':dt.dt.strftime('%Y-%m-%d'),'year':dt.dt.year,'month_no':dt.dt.month,'month':dt.dt.strftime('%B'),
      'year_month':dt.dt.strftime('%Y-%m'),'week_start':(dt-pd.to_timedelta(dt.dt.dayofweek,unit='d')).dt.strftime('%Y-%m-%d'),
      'day_of_week':dt.dt.strftime('%A'),'day_of_week_no':dt.dt.dayofweek+1,'is_weekend':(dt.dt.dayofweek>=5).astype(int)})
    tables={'fact_sessions':s,'fact_purchases':p,'dim_date':dates,**dimensions}
    (ROOT/'audit/evidence/data_quality.json').write_text(json.dumps(diagnostics,indent=2))
    return tables

def aggregate(tables):
    s=tables['fact_sessions'];p=tables['fact_purchases'];out=ROOT/'outputs'
    multiple=int(p.groupby('user_id').size().gt(1).sum()); revenue=float(p.purchase_revenue_usd.sum())
    k={'Sessions':len(s),'Users':s.user_id.nunique(),'Purchase Events':len(p),'Revenue':revenue,
       'Purchase Sessions':int(s.purchase.sum()),'Session Conversion Rate':s.purchase.mean(),
       'Average Purchase Event Value':revenue/len(p),'Engagement Rate':s.engaged_session.sum()/s.engagement_known.sum(),
       'Purchasers':p.user_id.nunique(),'Multiple-event Purchasers':multiple,
       'Multiple-event Purchaser Share':multiple/p.user_id.nunique(),
       'Strict Journey Purchase Sessions':int(s.ordered_purchase.sum()),'Revenue per Session':revenue/len(s)}
    pd.DataFrame(k.items(),columns=['metric','value']).to_csv(out/'kpi_summary.csv',index=False)
    for key,dim,label,filename in [('channel_id','dim_channel','channel','channel'),('device_id','dim_device','device_category','device'),('geo_id','dim_geo','country','country')]:
        a=s.groupby(key).agg(sessions=('session_id','nunique'),users=('user_id','nunique'),purchase_sessions=('purchase','sum'),session_attributed_revenue=('session_revenue','sum'))
        b=p.groupby(key).agg(purchase_events=('purchase_key','size'),revenue=('purchase_revenue_usd','sum'))
        a=a.join(b).fillna({'purchase_events':0,'revenue':0}).reset_index().merge(tables[dim],on=key,validate='one_to_one')
        a['conversion_rate']=a.purchase_sessions/a.sessions;a['revenue_per_session']=a.session_attributed_revenue/a.sessions
        a['average_purchase_event_value']=a.revenue/a.purchase_events.replace(0,np.nan)
        a.sort_values('revenue',ascending=False).to_csv(out/f'{filename}_performance.csv',index=False)
    counts=[len(s)]+[int(s['ordered_'+stage].sum()) for stage in STAGES]
    labels=['Observed sessions','Product view','Add to cart','Checkout','Purchase']
    pd.DataFrame({'stage':labels,'sessions':counts,'rate_from_previous':[1]+[counts[i]/counts[i-1] if counts[i-1] else np.nan for i in range(1,5)],
      'not_observed_at_next_step':[0]+[counts[i-1]-counts[i] for i in range(1,5)]}).to_csv(out/'ordered_funnel.csv',index=False)
    pd.DataFrame({'stage':['Product view','Add to cart','Checkout','Purchase'],'sessions':[int(s[x].sum()) for x in STAGES]}).to_csv(out/'event_presence.csv',index=False)
    m=s.assign(year_month=s.session_date.str[:7]).groupby('year_month').agg(sessions=('session_id','size'),purchase_sessions=('purchase','sum'),session_attributed_revenue=('session_revenue','sum'))
    m=m.join(p.assign(year_month=p.purchase_date.str[:7]).groupby('year_month').agg(revenue=('purchase_revenue_usd','sum'),purchase_events=('purchase_key','size')))
    m['conversion_rate']=m.purchase_sessions/m.sessions;m['revenue_per_session']=m.session_attributed_revenue/m.sessions;m['average_purchase_event_value']=m.revenue/m.purchase_events;m.reset_index().to_csv(out/'monthly_performance.csv',index=False)
    n=s.groupby('is_new_user').agg(sessions=('session_id','size'),purchase_sessions=('purchase','sum')).reset_index()
    n['session_type']=n.is_new_user.map({1:'New-user indication in GA4',0:'Returning-user indication in GA4',-1:'Unknown'})
    n['conversion_rate']=n.purchase_sessions/n.sessions;n.to_csv(out/'new_vs_returning.csv',index=False)
    return k

def main():
    status=ROOT/'audit/evidence/pipeline_status.json';status.write_text(json.dumps({'status':'RUNNING','outputs_valid':False}))
    try:
        tables=source_tables()
        for name,df in tables.items():
            target=ROOT/'data'/f'{name}.csv'
            temporary=target.with_suffix('.csv.tmp')
            with temporary.open('w',encoding='utf-8',newline='') as stream:
                df.to_csv(stream,index=False,float_format='%.6f')
                stream.flush()
                os.fsync(stream.fileno())
            with temporary.open(encoding='utf-8',newline='') as stream:
                reader=csv.reader(stream)
                require(next(reader)==list(df.columns),'Serialized CSV headers differ: '+name)
                count=0
                for row in reader:
                    require(len(row)==len(df.columns),'Serialized CSV width differs: '+name)
                    count+=1
            require(count==len(df),'Serialized CSV row count differs: '+name)
            temporary.replace(target)
            print(f'Published {name}: {count:,} rows verified on disk',flush=True)
        metrics=aggregate(tables)
        (ROOT/'scripts/schema.json').write_text(json.dumps({name:{'columns':list(df.columns)} for name,df in tables.items()},indent=2))
        status.write_text(json.dumps({'status':'PASS','outputs_valid':True,'metrics':metrics,'native_power_bi':'NOT_VERIFIED'},indent=2))
        print(json.dumps(metrics,indent=2),flush=True)
    except Exception as error:
        status.write_text(json.dumps({'status':'FAIL','outputs_valid':False,'error':str(error)},indent=2));raise

if __name__=='__main__':main()
