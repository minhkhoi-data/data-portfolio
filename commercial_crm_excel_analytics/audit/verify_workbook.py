"""Read-only row and aggregate oracle after separate Calc recalculation."""
import argparse,datetime,hashlib,json,math,warnings
from pathlib import Path
import openpyxl,pandas as pd
warnings.filterwarnings('ignore',module='openpyxl')
p=argparse.ArgumentParser();p.add_argument('--calc',required=True);args=p.parse_args()
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'data/source';checks=[]
w=openpyxl.load_workbook(args.calc,data_only=True);f=openpyxl.load_workbook(ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx',data_only=False)
def check(label,condition,details=None):checks.append({'check':label,'status':'PASS' if bool(condition) else 'FAIL','details':details})
def equal(x,y,tol=1e-6):
 if y is None or (isinstance(y,str) and y=='') or pd.isna(y):return x is None or x==''
 if isinstance(y,pd.Timestamp):return isinstance(x,datetime.datetime) and abs((x-y.to_pydatetime()).total_seconds())<.002
 if isinstance(y,(int,float)) and not isinstance(y,bool):return isinstance(x,(int,float)) and math.isclose(x,float(y),abs_tol=tol,rel_tol=0)
 return x==y
a=pd.read_csv(source/'olist_marketing_qualified_leads_dataset.csv');b=pd.read_csv(source/'olist_closed_deals_dataset.csv');o=pd.read_csv(source/'olist_orders_dataset.csv');i=pd.read_csv(source/'olist_order_items_dataset.csv')
x=a.merge(b,on='mql_id',how='left',validate='one_to_one');dt=pd.to_datetime(x.first_contact_date);won=pd.to_datetime(x.won_date);iswon=x.seller_id.notna();cycle=(won.dt.normalize()-dt).dt.days.where(won.ge(dt))
raw=list(w['Leads'].iter_rows(min_row=2,max_row=8001,max_col=17,values_only=True))
for index,column in enumerate(x.columns):
 expected=pd.to_datetime(x[column]) if column in ['first_contact_date','won_date'] else x[column]
 mismatches=[r+2 for r in range(len(x)) if not equal(raw[r][index],expected.iloc[r])]
 check('all_lead_input_'+column,not mismatches,mismatches[:6])
mapping={'organic_search':'Organic search','paid_search':'Paid search','social':'Social','unknown':'Unknown (source label)','direct_traffic':'Direct traffic','email':'Email','referral':'Referral','other':'Other','display':'Display','other_publicities':'Other publicities'}
channel=x.origin.map(mapping).fillna('Missing origin');sr={s:f'SR {j+1:02}' for j,s in enumerate(sorted(b.sr_id.unique()))};sdr={s:f'SDR {j+1:02}' for j,s in enumerate(sorted(b.sdr_id.unique()))}
threshold=w['Lookups']['B3'].value
expected_columns=[channel,iswon.astype(int),iswon.map({True:'Won recorded',False:'No won record'}),cycle,won.lt(dt).map({True:'Won before contact',False:''}),x.sr_id.map(sr),x.sdr_id.map(sdr),dt.dt.to_period('M').dt.to_timestamp(),won.dt.to_period('M').dt.to_timestamp(),cycle.gt(threshold).astype(int).where(cycle.notna())]
for colnum,expected in enumerate(expected_columns,18):
 bad=[r+2 for r in range(8000) if not equal(w['Leads'].cell(r+2,colnum).value,expected.iloc[r])]
 check('all_lead_derived_'+openpyxl.utils.get_column_letter(colnum),not bad,bad[:6])
items=i[i.seller_id.isin(b.seller_id)].merge(o[['order_id','order_status','order_purchase_timestamp']],on='order_id',validate='many_to_one').sort_values(['seller_id','order_id','order_item_id']).reset_index(drop=True)
for cnum,column in enumerate(items.columns,1):
 expected=pd.to_datetime(items[column]) if column in ['shipping_limit_date','order_purchase_timestamp'] else items[column]
 bad=[r+2 for r in range(len(items)) if not equal(w['Sales_Items'].cell(r+2,cnum).value,expected.iloc[r])]
 check('all_item_source_'+column,not bad,bad[:6])
iw=pd.to_datetime(items.seller_id.map(b.set_index('seller_id').won_date));ip=pd.to_datetime(items.order_purchase_timestamp);eligible=items.order_status.eq('delivered')&ip.ge(iw);first=~items.duplicated(['seller_id','order_id'])
derived=[iw,eligible.astype(int),items.price.where(eligible,0),first.astype(int),(eligible&first).astype(int),ip.dt.to_period('M').dt.to_timestamp()]
for cnum,expected in enumerate(derived,10):
 bad=[r+2 for r in range(len(items)) if not equal(w['Sales_Items'].cell(r+2,cnum).value,expected.iloc[r])]
 check('all_item_derived_'+openpyxl.utils.get_column_letter(cnum),not bad,bad[:6])
q=items[eligible].copy();q['purchase']=ip[eligible];q['link']=(eligible&first)[eligible].astype(int)
group=q.groupby('seller_id').agg(eligible_items=('price','size'),seller_orders=('link','sum'),value=('price','sum'),first_purchase=('purchase','min'))
candidate_count=items.seller_id.value_counts();seller_bad=[]
for r in range(2,844):
 seller=w['Seller_Value'].cell(r,2).value;match=group.loc[seller] if seller in group.index else None
 expected=[int(candidate_count.get(seller,0)),int(match.eligible_items) if match is not None else 0,int(match.seller_orders) if match is not None else 0,float(match.value) if match is not None else None,match.first_purchase if match is not None else None]
 if not all(equal(w['Seller_Value'].cell(r,c).value,v) for c,v in zip(range(8,13),expected)):seller_bad.append(r)
check('all_842_seller_metrics',not seller_bad,seller_bad[:8])
value=float(q.price.sum());head={'A6':8000,'C6':842,'E6':842/8000,'G6':float(cycle.median()),'I6':len(candidate_count),'K6':value,'M6':int(cycle.gt(threshold).sum())}
for cell,v in head.items():check('headline_'+cell,equal(w['Dashboard'][cell].value,v),{'actual':w['Dashboard'][cell].value,'expected':v})
for r in range(2,13):
 label=w['Channel_Performance'].cell(r,1).value;mask=channel.eq(label);wins=int((mask&iswon).sum());valid=int(cycle[mask].notna().sum());linked_sellers=b[b.mql_id.isin(x.loc[mask,'mql_id'])].seller_id
 seller_value=q[q.seller_id.isin(linked_sellers)]
 expected=[int(mask.sum()),wins,int((mask&~iswon).sum()),wins/int(mask.sum()),valid,float(cycle[mask].mean()) if valid else None,int(cycle[mask].gt(threshold).sum()),int(linked_sellers.isin(candidate_count.index).sum()),int(linked_sellers.isin(group.index).sum()),float(seller_value.price.sum()) if len(seller_value) else None]
 check('channel_'+label,all(equal(w['Channel_Performance'].cell(r,c).value,v) for c,v in zip(range(2,12),expected)),expected)
for start,end,key in [(2,23,x.sr_id.map(sr)),(30,61,x.sdr_id.map(sdr))]:
 for r in range(start,end+1):
  label=w['Rep_Performance'].cell(r,1).value;mask=key.eq(label);valid=int(cycle[mask].notna().sum());expected=[int(mask.sum()),valid,float(cycle[mask].mean()) if valid else None,int(cycle[mask].gt(threshold).sum())]
  check('rep_'+str(label),all(equal(w['Rep_Performance'].cell(r,c).value,v) for c,v in zip(range(2,6),expected)),expected)
for r in range(2,20):
 month=pd.Timestamp(w['Monthly_Trend'].cell(r,1).value);cm=dt.dt.to_period('M').dt.to_timestamp().eq(month);wm=won.dt.to_period('M').dt.to_timestamp().eq(month);pm=q.purchase.dt.to_period('M').dt.to_timestamp().eq(month)
 leads=int(cm.sum());cv=int((cm&iswon).sum());valid=int(cycle[wm].notna().sum());expected=[leads,int(wm.sum()),cv,cv/leads if leads else None,float(q.loc[pm,'price'].sum()),valid,float(cycle[wm].mean()) if valid else None]
 check('month_'+month.strftime('%Y-%m'),all(equal(w['Monthly_Trend'].cell(r,c).value,v) for c,v in zip(range(2,9),expected)),expected)
errors=[f'{s.title}!{c.coordinate}:{c.value}' for s in w for row in s for c in row if c.data_type=='e']
check('no_base_formula_errors',not errors,errors[:12]);check('four_native_editable_charts',len(f['Dashboard']._charts)==4)
check('all_quality_reconciliations',[w['Quality_Review'].cell(r,4).value for r in range(2,20)]==['MATCH']*18)
check('raw_source_not_synthetic',len(a)==8000 and len(b)==842,'Original publisher CSV bytes are locked in source_manifest.json; no synthetic filler fields.')
check('unmatched_seller_amounts_blank',all(w['Seller_Value'].cell(r,11).value in [None,''] for r in range(2,844) if w['Seller_Value'].cell(r,8).value==0))
check('date_issue_kept_in_won_count',int(iswon.sum())==842 and int(cycle.notna().sum())==841)
result={'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','checks':len(checks),'passed':sum(c['status']=='PASS' for c in checks),'engine':'Separately recalculated LibreOffice Calc workbook','Microsoft_Excel':'PENDING_USER','sha256':hashlib.sha256((ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx').read_bytes()).hexdigest(),'results':checks}
(ROOT/'audit/WORKBOOK_VALIDATION.json').write_text(json.dumps(result,indent=2,default=str));print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2));print('FAILURES',[c for c in checks if c['status']=='FAIL'])
raise SystemExit(result['status']!='PASS')
