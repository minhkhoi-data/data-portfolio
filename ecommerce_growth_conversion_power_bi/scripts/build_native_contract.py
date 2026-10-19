"""Independent Python expectations for one native DAX query; does not execute DAX."""
import calendar,json
import pandas as pd
from pipeline import ROOT,sha256
from build_model import MEASURES

def main():
    data=ROOT/'data';out=ROOT/'audit/native_contract';out.mkdir(parents=True,exist_ok=True)
    s=pd.read_csv(data/'fact_sessions.csv',dtype={'session_id':str,'user_id':str},keep_default_na=False)
    p=pd.read_csv(data/'fact_purchases.csv',dtype={'session_id':str,'user_id':str},keep_default_na=False)
    dates=pd.date_range('2020-11-01','2021-01-31').strftime('%Y-%m-%d').tolist()
    contexts=[{'name':'all'},*({'name':m,'month':m} for m in ['2020-11','2020-12','2021-01']),{'name':'partial-Jan','start':'2021-01-01','end':'2021-01-15'}, {'name':'two-months','start':'2020-11-01','end':'2020-12-31'}, {'name':'empty-country','country':'__NO_MATCH__'}, {'name':'stage-Purchase','stage':'Purchase'}]
    ch=pd.read_csv(data/'dim_channel.csv');dev=pd.read_csv(data/'dim_device.csv');geo=pd.read_csv(data/'dim_geo.csv')
    contexts += [{'name':'channel:'+str(v),'channel':v} for v in ch.channel]
    contexts += [{'name':'device:'+str(v),'device':v} for v in dev.device_category]
    contexts += [{'name':'country:'+str(v),'country':v} for v in ['United States','Canada']]
    contexts += [{'name':'cross-date-channel-device','month':'2020-12','channel':ch.channel.iloc[0],'device':'mobile'}]
    results=[];queries=[]
    quote=lambda v:'"'+str(v).replace('"','""')+'"'
    for c in contexts:
        ds=dates
        if 'month' in c:ds=[d for d in ds if d[:7]==c['month']]
        if 'start' in c:ds=[d for d in ds if c['start']<=d<=c['end']]
        ss=s.loc[s.session_date.isin(ds)].copy();pp=p.loc[p.purchase_date.isin(ds)].copy();filters=[]
        dim_conditions=[]
        if 'month' in c:filters.append('TREATAS({'+quote(c['month'])+'}, DimDate[year_month])')
        if 'start' in c:filters.append('DATESBETWEEN(DimDate[date], DATE('+c['start'].replace('-',',')+'), DATE('+c['end'].replace('-',',')+'))')
        for key,frame,column,fk,table in [('channel',ch,'channel','channel_id','DimChannel'),('device',dev,'device_category','device_id','DimDevice'),('country',geo,'country','geo_id','DimGeo')]:
            if key not in c:continue
            ids=frame.loc[frame[column].eq(c[key]),fk]
            ss=ss.loc[ss[fk].isin(ids)];pp=pp.loc[pp[fk].isin(ids)];dim_conditions.append((fk,ids))
            filters.append('TREATAS({'+quote(c[key])+'}, '+table+'['+column+'])')
        if 'stage' in c:filters.append('TREATAS({'+quote(c['stage'])+'}, FunnelStage[Stage])')
        count=lambda col:int(pd.to_numeric(ss[col],errors='raise').eq(1).sum())
        div=lambda a,b:None if not b or a is None else a/b
        sum_column=lambda f,col:None if not len(f) else float(pd.to_numeric(f[col].replace('',float('nan')),errors='raise').sum(min_count=1))
        ns=len(ss);nu=ss.user_id.nunique();npe=len(pp);npu=pp.user_id.nunique()
        multiple=int(pp.groupby('user_id').size().gt(1).sum()) or None
        revenue=sum_column(pp,'purchase_revenue_usd');sr=sum_column(ss,'session_revenue');known=count('engagement_known')
        d={'Sessions':ns,'Users':nu,'Engaged Sessions':count('engaged_session') if not ss.engaged_session.eq('').any() else int(pd.to_numeric(ss.engaged_session.replace('',float('nan'))).eq(1).sum()),'Known Engagement Sessions':known,
           'Product View Sessions':count('ordered_view_item'),'Add to Cart Sessions':count('ordered_add_to_cart'),'Checkout Sessions':count('ordered_begin_checkout'),'Strict Journey Purchase Sessions':count('ordered_purchase'),'Purchase Sessions':count('purchase'),
           'Revenue':revenue,'Purchase Events':npe,'Session-attributed Revenue':sr,'Reported Item Quantity':sum_column(pp,'total_quantity'),'Purchasers':npu,'Multiple-event Purchasers':multiple,
           'Product Data Status':'No item-level data','Experiment Data Status':'No assignment data','Attribution Scope':'First-user acquisition','Revenue Scope':'Recorded purchase events','Snapshot Note':'Google GA4 public sample | Nov 2020 - Jan 2021 | USD purchase-event revenue | Obfuscated data'}
        for name,a,b in [('Engagement Rate','Engaged Sessions','Known Engagement Sessions'),('Product View Rate','Product View Sessions','Sessions'),('View to Cart Rate','Add to Cart Sessions','Product View Sessions'),('Cart to Checkout Rate','Checkout Sessions','Add to Cart Sessions'),('Checkout to Purchase Rate','Strict Journey Purchase Sessions','Checkout Sessions'),('Session Conversion Rate','Purchase Sessions','Sessions'),('Average Purchase Event Value','Revenue','Purchase Events'),('Revenue per Session','Session-attributed Revenue','Sessions'),('Revenue per User','Session-attributed Revenue','Users'),('Multiple-event Purchaser Share','Multiple-event Purchasers','Purchasers')]:d[name]=div(d[a],d[b])
        for value,name in [(1,'New User Session Conversion'),(0,'Returning User Session Conversion')]:
            part=ss.loc[ss.is_new_user.eq(value)];d[name]=div(int(part.purchase.eq(1).sum()),len(part))
        stage_map={'Sessions':'Sessions','Product View':'Product View Sessions','Add to Cart':'Add to Cart Sessions','Checkout':'Checkout Sessions','Purchase':'Strict Journey Purchase Sessions'}
        d['Funnel Stage Sessions']=d[stage_map[c['stage']]] if 'stage' in c else None
        months={x[:7] for x in ds};previous=None
        if len(months)==1 and len(ds)==calendar.monthrange(int(ds[0][:4]),int(ds[0][5:7]))[1]:
            prev=(pd.Timestamp(ds[0])-pd.Timedelta(days=1)).strftime('%Y-%m');prevp=p.loc[p.purchase_date.str.startswith(prev)]
            for fk,ids in dim_conditions:prevp=prevp.loc[prevp[fk].isin(ids)]
            previous=sum_column(prevp,'purchase_revenue_usd')
        d['Revenue Previous Month']=previous;d['Revenue MoM %']=None if previous is None or not previous or revenue is None else (revenue-previous)/previous
        results.append({'Context':c['name'],**{m:d[m] for m in MEASURES}})
        row='ROW("Context", '+quote(c['name'])+', '+', '.join(quote(m)+', ['+m+']' for m in MEASURES)+')'
        queries.append('CALCULATETABLE('+row+', '+', '.join(filters)+')' if filters else row)
    pd.DataFrame(results).to_csv(out/'expected.csv',index=False)
    (out/'validate_all_contexts.dax').write_text('// Run in Power BI Desktop DAX query view after refresh. No native execution is claimed.\nEVALUATE\nUNION(\n'+',\n'.join(queries)+'\n)\nORDER BY [Context]\n')
    record={'status':'PREPARED_NOT_NATIVE_EXECUTED','contexts':len(contexts),'measures':len(MEASURES),'numeric_absolute_tolerance':1e-6,'blank_contract':'CSV empty = DAX BLANK, not numeric zero','data_sha256':{f.name:sha256(f) for f in sorted(data.glob('*.csv'))}}
    (out/'contract.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))

if __name__=='__main__':main()
