"""Reproduce Olist joins and metrics from unchanged publisher CSVs.
Run: python analysis/run_analysis.py. Does not create or modify an XLSX.
"""
from pathlib import Path
import hashlib,json,sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/source';OUTPUT=ROOT/'analysis/outputs';OUTPUT.mkdir(exist_ok=True)
STATUS=OUTPUT/'RUN_STATUS.json'
STATUS.write_text(json.dumps({'status':'RUNNING'}))
try:
    def read(name,expected):
        frame=pd.read_csv(SOURCE/name,keep_default_na=True)
        assert list(frame.columns)==expected,(name,list(frame.columns))
        return frame
    leads=read('olist_marketing_qualified_leads_dataset.csv',['mql_id','first_contact_date','landing_page_id','origin'])
    deals=read('olist_closed_deals_dataset.csv',['mql_id','seller_id','sdr_id','sr_id','won_date','business_segment','lead_type','lead_behaviour_profile','has_company','has_gtin','average_stock','business_type','declared_product_catalog_size','declared_monthly_revenue'])
    orders=read('olist_orders_dataset.csv',['order_id','customer_id','order_status','order_purchase_timestamp','order_approved_at','order_delivered_carrier_date','order_delivered_customer_date','order_estimated_delivery_date'])
    items=read('olist_order_items_dataset.csv',['order_id','order_item_id','product_id','seller_id','shipping_limit_date','price','freight_value'])
    sellers=read('olist_sellers_dataset.csv',['seller_id','seller_zip_code_prefix','seller_city','seller_state'])
    assert leads.mql_id.is_unique and deals.mql_id.is_unique and deals.seller_id.is_unique
    assert orders.order_id.is_unique and sellers.seller_id.is_unique
    assert not items.duplicated(['order_id','order_item_id']).any()
    assert deals.mql_id.isin(leads.mql_id).all()
    assert items.order_id.isin(orders.order_id).all()
    assert items.seller_id.isin(sellers.seller_id).all()
    assert items.price.ge(0).all() and items.freight_value.ge(0).all()
    joined=leads.merge(deals,on='mql_id',how='left',validate='one_to_one')
    channels={'organic_search':'Organic search','paid_search':'Paid search','social':'Social','unknown':'Unknown (source label)','direct_traffic':'Direct traffic','email':'Email','referral':'Referral','other':'Other','display':'Display','other_publicities':'Other publicities'}
    joined['Channel']=joined.origin.map(channels).fillna('Missing origin')
    assert joined.origin.dropna().isin(channels).all()
    joined['Observed_win']=joined.seller_id.notna().astype(int)
    first=pd.to_datetime(joined.first_contact_date,errors='raise');won=pd.to_datetime(joined.won_date,errors='raise')
    joined['Cycle_days']=(won.dt.normalize()-first).dt.days.where(won.ge(first))
    joined['Date_issue']=won.lt(first)
    joined['Contact_month']=first.dt.to_period('M').astype(str)
    joined['Win_month']=won.dt.strftime('%Y-%m')
    sr_ids=sorted(deals.sr_id.unique());sdr_ids=sorted(deals.sdr_id.unique())
    sr={key:f'SR {i+1:02}' for i,key in enumerate(sr_ids)};sdr={key:f'SDR {i+1:02}' for i,key in enumerate(sdr_ids)}
    joined['SR_label']=joined.sr_id.map(sr);joined['SDR_label']=joined.sdr_id.map(sdr)
    candidate=items[items.seller_id.isin(deals.seller_id)].merge(orders[['order_id','order_status','order_purchase_timestamp']],on='order_id',validate='many_to_one')
    candidate=candidate.sort_values(['seller_id','order_id','order_item_id']).reset_index(drop=True)
    candidate['Won_date']=candidate.seller_id.map(deals.set_index('seller_id').won_date)
    purchase=pd.to_datetime(candidate.order_purchase_timestamp,errors='raise');item_won=pd.to_datetime(candidate.Won_date,errors='raise')
    candidate['Eligible_item']=(candidate.order_status.eq('delivered') & purchase.ge(item_won)).astype(int)
    candidate['Eligible_GMV']=candidate.price*candidate.Eligible_item
    candidate['First_seller_order']=(~candidate.duplicated(['seller_id','order_id'])).astype(int)
    candidate['Eligible_seller_order']=candidate.First_seller_order*candidate.Eligible_item
    candidate['Purchase_month']=purchase.dt.strftime('%Y-%m')
    qual=candidate[candidate.Eligible_item.eq(1)].copy()
    aggregate=qual.groupby('seller_id').agg(eligible_items=('order_id','size'),seller_order_links=('Eligible_seller_order','sum'),linked_item_gmv=('price','sum'),first_purchase=('order_purchase_timestamp','min'))
    sv=deals[['mql_id','seller_id','won_date']].merge(joined[['mql_id','Channel','SR_label','SDR_label']],on='mql_id',validate='one_to_one').merge(sellers[['seller_id','seller_state']],on='seller_id',how='left',validate='one_to_one').merge(aggregate,on='seller_id',how='left',validate='one_to_one')
    sv['candidate_items']=sv.seller_id.map(candidate.seller_id.value_counts()).fillna(0).astype(int)
    sv['eligible_items']=sv.eligible_items.fillna(0).astype(int);sv['seller_order_links']=sv.seller_order_links.fillna(0).astype(int)
    assert len(joined)==len(leads) and len(sv)==len(deals)
    assert abs(sv.linked_item_gmv.sum()-qual.price.sum())<1e-8
    channel=joined.groupby('Channel',sort=False).agg(leads=('mql_id','size'),wins=('Observed_win','sum'),valid_cycles=('Cycle_days','count'),avg_cycle=('Cycle_days','mean'))
    channel['recorded_won_share']=channel.wins/channel.leads
    channel['slow_wins_30d']=joined.assign(slow=joined.Cycle_days.gt(30)).groupby('Channel').slow.sum()
    channel['linked_wins']=sv.assign(linked=sv.candidate_items.gt(0)).groupby('Channel').linked.sum()
    channel['delivered_linked_wins']=sv.assign(linked=sv.eligible_items.gt(0)).groupby('Channel').linked.sum()
    channel['linked_item_gmv']=sv.groupby('Channel').linked_item_gmv.sum()
    channel=channel.fillna({'linked_wins':0,'delivered_linked_wins':0}).sort_values('wins',ascending=False)
    months=pd.period_range(first.min().to_period('M'),won.max().to_period('M'),freq='M').astype(str)
    monthly=pd.DataFrame(index=months)
    monthly['leads']=joined.groupby('Contact_month').size().reindex(months,fill_value=0)
    monthly['calendar_wins']=joined.groupby('Win_month').Observed_win.sum().reindex(months,fill_value=0)
    monthly['cohort_wins']=joined.groupby('Contact_month').Observed_win.sum().reindex(months,fill_value=0)
    monthly['recorded_cohort_share']=(monthly.cohort_wins/monthly.leads).where(monthly.leads.gt(0))
    monthly['linked_item_gmv']=qual.groupby('Purchase_month').price.sum().reindex(months,fill_value=0)
    sr_metrics=joined[joined.Observed_win.eq(1)].groupby('SR_label').agg(wins=('mql_id','size'),valid_cycles=('Cycle_days','count'),avg_cycle=('Cycle_days','mean'))
    sr_metrics['slow_wins_30d']=joined.assign(slow=joined.Cycle_days.gt(30)).groupby('SR_label').slow.sum()
    sr_metrics=sr_metrics.sort_values('wins',ascending=False)
    sdr_metrics=joined[joined.Observed_win.eq(1)].groupby('SDR_label').agg(wins=('mql_id','size'),valid_cycles=('Cycle_days','count'),avg_cycle=('Cycle_days','mean')).sort_values('wins',ascending=False)
    summary={'mqls':len(leads),'observed_wins':len(deals),'recorded_won_share':len(deals)/len(leads),'no_won_record':int(joined.Observed_win.eq(0).sum()),'valid_close_cycles':int(joined.Cycle_days.notna().sum()),'median_calendar_days_to_win':float(joined.Cycle_days.median()),'avg_calendar_days_to_win':float(joined.Cycle_days.mean()),'slow_wins_30d':int(joined.Cycle_days.gt(30).sum()),'slow_wins_14d':int(joined.Cycle_days.gt(14).sum()),'date_anomalies':int(joined.Date_issue.sum()),'missing_origin':int(leads.origin.isna().sum()),'source_unknown_origin':int(leads.origin.eq('unknown').sum()),'won_sellers_with_candidate_items':int(sv.candidate_items.gt(0).sum()),'won_sellers_with_eligible_delivered_items':int(sv.eligible_items.gt(0).sum()),'candidate_items':len(candidate),'eligible_items':len(qual),'eligible_seller_order_links':int(qual.Eligible_seller_order.sum()),'unique_eligible_orders':int(qual.order_id.nunique()),'linked_delivered_item_value_source_units':round(float(qual.price.sum()),2),'declared_revenue_zero':int(deals.declared_monthly_revenue.eq(0).sum()),'declared_revenue_positive':int(deals.declared_monthly_revenue.gt(0).sum())}
    for name,frame in [('channel_metrics',channel),('monthly_metrics',monthly),('sr_metrics',sr_metrics),('sdr_metrics',sdr_metrics),('seller_value',sv)]:frame.to_csv(OUTPUT/(name+'.csv'),index=name!='seller_value')
    joined.to_csv(OUTPUT/'leads_prepared.csv',index=False);candidate.to_csv(OUTPUT/'sales_items_prepared.csv',index=False)
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2))
    sources=[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(SOURCE.glob('*.csv'))]
    (OUTPUT/'source_manifest.json').write_text(json.dumps(sources,indent=2))
    def records(frame):return json.loads(frame.where(frame.notna(),None).to_json(orient='records',date_format='iso'))
    data={'summary':summary,'channels':list(channel.index),'months':list(months),'sr':[[k,sr[k]] for k in sr_ids],'sdr':[[k,sdr[k]] for k in sdr_ids],'channel_map':list(channels.items()),'leads':records(joined.iloc[:,:17]),'lead_prepared':records(joined[['Channel','Observed_win','SR_label','SDR_label','Contact_month','Win_month']]),'items':records(candidate.iloc[:,:9]),'item_prepared':records(candidate[['Won_date','First_seller_order','Purchase_month']]),'sellers':records(sv),'sr_order':list(sr_metrics.index),'sdr_order':list(sdr_metrics.index),'source_manifest':sources}
    (OUTPUT/'workbook_input.json').write_text(json.dumps(data,allow_nan=False))
    print(json.dumps(summary,indent=2))
    STATUS.write_text(json.dumps({'status':'PASS','source_manifest':'source_manifest.json','summary':'summary.json'}))
except BaseException as error:
    STATUS.write_text(json.dumps({'status':'FAIL','error':str(error)}))
    raise
