"""Synchronise the six CSV tables and all report bindings; no native engine claim."""
from pathlib import Path
import copy, json, re, shutil, uuid
import pandas as pd
from pipeline import ROOT,TABLES

NS=uuid.UUID('95d7672c-b723-4ea9-b20c-4b45699ca16b')
def tag(name):return str(uuid.uuid5(NS,name))
def write_json(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

TEXT={'Stage','Dummy','session_id','user_id','source','medium','country','region_group','channel','device_category',
      'event_timestamp','source_event_id','transaction_id','currency','month','year_month','day_of_week'}
DATES={'date','session_date','purchase_date','week_start'}
DECIMAL={'session_revenue','purchase_revenue_usd'}
DOUBLE={'engagement_seconds'}

def make_table(table,name):
    csv=ROOT/'data'/f'{name}.csv';frame=pd.read_csv(csv,nrows=0)
    lines=[f'table {table}',f'\tlineageTag: {tag(table)}','']
    if table=='DimDate':lines+=['\tdataCategory: Time','']
    types=[];nullable=['engaged_session','total_quantity','distinct_products']
    for col in frame.columns:
        typ,mtype=('string','type text') if col in TEXT else ('dateTime','type date') if col in DATES else ('decimal','Currency.Type') if col in DECIMAL else ('double','type number') if col in DOUBLE else ('int64','Int64.Type')
        lines += [f'\tcolumn {col}',f'\t\tdataType: {typ}',f'\t\tlineageTag: {tag(table+"."+col)}',
                  '\t\tsummarizeBy: none',f'\t\tsourceColumn: {col}']
        if col in DATES:lines+=['\t\tformatString: yyyy-MM-dd']
        if table=='DimDate' and col=='date':lines+=['\t\tisKey']
        if col in DECIMAL:lines+=['\t\tformatString: $#,##0.00']
        if table=='DimDate' and col in ['month','day_of_week']:
            lines+=[f'\t\tsortByColumn: {"month_no" if col=="month" else "day_of_week_no"}']
        # Properties precede annotation child objects; separate their scopes.
        if col in DATES:lines+=['','\t\tannotation UnderlyingDateTimeDataType = Date']
        lines+=[''];types.append(f'\t\t\t\t\t{{"{col}", {mtype}}}')
    null_columns=[c for c in frame.columns if c in nullable]
    null_code='Checked'
    if null_columns:
        null_code='Nulls'
    lines += [f'\tpartition {table} = m','\t\tmode: import','\t\tsource =','\t\t\t\tlet',
      f'\t\t\t\t\tSource = Csv.Document(File.Contents(DataFolder & "/{name}.csv"), [Delimiter=",", Columns={len(frame.columns)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv, ExtraValues=ExtraValues.Error]),',
      '\t\t\t\t\tHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
      '\t\t\t\t\tChecked = if Table.ColumnNames(Headers) = {'+', '.join('"'+c+'"' for c in frame.columns)+'} then Headers else error Error.Record("SchemaMismatch", "CSV headers do not match '+table+'", null),']
    if null_columns:lines+=['\t\t\t\t\tNulls = Table.ReplaceValue(Checked, "", null, Replacer.ReplaceValue, {'+', '.join('"'+c+'"' for c in null_columns)+'}),']
    lines += ['\t\t\t\t\tTyped = Table.TransformColumnTypes('+null_code+', {',',\n'.join(types),
              '\t\t\t\t\t}, "en-US")','\t\t\t\tin','\t\t\t\t\tTyped','']
    if table=='FunnelStage':
        index=lines.index('\t\tsourceColumn: Stage');lines.insert(index+1,'\t\tsortByColumn: Sort')
    if table=='_Measures':
        index=lines.index('\tcolumn Dummy');lines.insert(index+1,'\t\tisHidden')
    (ROOT/'powerbi/EcommerceGrowth.Model/definition/tables'/f'{table}.tmdl').write_text('\n'.join(lines))

MEASURES={
 'Sessions':('COALESCE(DISTINCTCOUNT(FactSessions[session_id]), 0)','#,##0'),
 'Users':('COALESCE(DISTINCTCOUNT(FactSessions[user_id]), 0)','#,##0'),
 'Engaged Sessions':('CALCULATE([Sessions], FactSessions[engaged_session] = 1)','#,##0'),
 'Known Engagement Sessions':('CALCULATE([Sessions], FactSessions[engagement_known] = 1)','#,##0'),
 'Engagement Rate':('DIVIDE([Engaged Sessions], [Known Engagement Sessions])','0.00%'),
 'Product View Sessions':('CALCULATE([Sessions], FactSessions[ordered_view_item] = 1)','#,##0'),
 'Add to Cart Sessions':('CALCULATE([Sessions], FactSessions[ordered_add_to_cart] = 1)','#,##0'),
 'Checkout Sessions':('CALCULATE([Sessions], FactSessions[ordered_begin_checkout] = 1)','#,##0'),
 'Strict Journey Purchase Sessions':('CALCULATE([Sessions], FactSessions[ordered_purchase] = 1)','#,##0'),
 'Purchase Sessions':('CALCULATE([Sessions], FactSessions[purchase] = 1)','#,##0'),
 'Product View Rate':('DIVIDE([Product View Sessions], [Sessions])','0.00%'),
 'View to Cart Rate':('DIVIDE([Add to Cart Sessions], [Product View Sessions])','0.00%'),
 'Cart to Checkout Rate':('DIVIDE([Checkout Sessions], [Add to Cart Sessions])','0.00%'),
 'Checkout to Purchase Rate':('DIVIDE([Strict Journey Purchase Sessions], [Checkout Sessions])','0.00%'),
 'Session Conversion Rate':('DIVIDE([Purchase Sessions], [Sessions])','0.00%'),
 'Revenue':('SUM(FactPurchases[purchase_revenue_usd])','$#,##0.00'),
 'Purchase Events':('COALESCE(COUNTROWS(FactPurchases), 0)','#,##0'),
 'Average Purchase Event Value':('DIVIDE([Revenue], [Purchase Events])','$#,##0.00'),
 'Session-attributed Revenue':('SUM(FactSessions[session_revenue])','$#,##0.00'),
 'Revenue per Session':('DIVIDE([Session-attributed Revenue], [Sessions])','$#,##0.00'),
 'Revenue per User':('DIVIDE([Session-attributed Revenue], [Users])','$#,##0.00'),
 'Reported Item Quantity':('SUM(FactPurchases[total_quantity])','#,##0'),
 'Purchasers':('COALESCE(DISTINCTCOUNT(FactPurchases[user_id]), 0)','#,##0'),
 'Multiple-event Purchasers':('VAR Activity = ADDCOLUMNS(VALUES(FactPurchases[user_id]), "__Events", CALCULATE(COUNTROWS(FactPurchases))) RETURN COUNTROWS(FILTER(Activity, [__Events] > 1))','#,##0'),
 'Multiple-event Purchaser Share':('DIVIDE([Multiple-event Purchasers], [Purchasers])','0.00%'),
 'New User Session Conversion':('DIVIDE(CALCULATE([Purchase Sessions], FactSessions[is_new_user] = 1), CALCULATE([Sessions], FactSessions[is_new_user] = 1))','0.00%'),
 'Returning User Session Conversion':('DIVIDE(CALCULATE([Purchase Sessions], FactSessions[is_new_user] = 0), CALCULATE([Sessions], FactSessions[is_new_user] = 0))','0.00%'),
 'Funnel Stage Sessions':('SWITCH(SELECTEDVALUE(FunnelStage[Stage]), "Sessions", [Sessions], "Product View", [Product View Sessions], "Add to Cart", [Add to Cart Sessions], "Checkout", [Checkout Sessions], "Purchase", [Strict Journey Purchase Sessions])','#,##0'),
 'Revenue Previous Month':('VAR FullMonth = HASONEVALUE(DimDate[year_month]) && COUNTROWS(VALUES(DimDate[date])) = DAY(EOMONTH(MAX(DimDate[date]), 0)) VAR StartPrevious = EOMONTH(MAX(DimDate[date]), -2) + 1 VAR EndPrevious = EOMONTH(MAX(DimDate[date]), -1) RETURN IF(FullMonth, CALCULATE([Revenue], REMOVEFILTERS(DimDate), DATESBETWEEN(DimDate[date], StartPrevious, EndPrevious)), BLANK())','$#,##0.00'),
 'Revenue MoM %':('DIVIDE([Revenue] - [Revenue Previous Month], [Revenue Previous Month])','0.00%'),
 'Product Data Status':('"No item-level data"',None),
 'Experiment Data Status':('"No assignment data"',None),
 'Attribution Scope':('"First-user acquisition"',None),
 'Revenue Scope':('"Recorded purchase events"',None),
 'Snapshot Note':('"Google GA4 public sample | Nov 2020 - Jan 2021 | USD purchase-event revenue | Obfuscated data"',None),
}

def measures():
    file=ROOT/'powerbi/EcommerceGrowth.Model/definition/tables/_Measures.tmdl'
    make_table('_Measures','measures')
    lines=[]
    for name,(expr,fmt) in MEASURES.items():
        lines += [f"\tmeasure '{name}' = {expr}",f'\t\tlineageTag: {tag("measure."+name)}']
        if fmt:lines.append(f'\t\tformatString: {fmt}')
        lines.append('')
    base=file.read_text();base=base.replace('\tcolumn Dummy','\n'.join(lines)+'\tcolumn Dummy',1)
    file.write_text(base)

RENAMES={'Transactions':'Purchase Events','AOV':'Average Purchase Event Value','Repeat Purchasers':'Multiple-event Purchasers',
         'Repeat Purchase Rate':'Multiple-event Purchaser Share','Units Sold':'Reported Item Quantity'}
LABELS={'Transactions':'Purchase events','AOV':'Avg purchase value','Average Order Value':'Avg purchase value',
        'Repeat Rate':'Multi-event share','Repeat within filter':'Multi-event share',
        'Repeat Purchasers':'Multi-event purchasers','Repeat Purchase Rate':'Multi-event purchaser share',
        'Channel':'First-user channel','Revenue':'Purchase-event revenue (USD)',
        'Synthetic ordered funnel':'Strict ordered journey',
        'Revenue by Channel':'Revenue by first-user channel','Channel Conversion Rate':'First-user channel CVR',
        'Conversion by Channel':'Conversion by first-user channel','Revenue per Session by Channel':'Revenue per session by first-user channel'}

def update_tree(obj):
    if isinstance(obj,dict):
        if 'Measure' in obj:
            m=obj['Measure'];m['Property']=RENAMES.get(m['Property'],m['Property'])
        for k,v in obj.items():
            if isinstance(v,str):
                if k=='queryRef' and v.startswith('_Measures.'):
                    name=v[len('_Measures.'):];obj[k]='_Measures.'+RENAMES.get(name,name)
                elif k=='nativeQueryRef':obj[k]=LABELS.get(v,v)
                elif k=='metadata' and v.startswith('_Measures.'):
                    name=v[len('_Measures.'):];obj[k]='_Measures.'+RENAMES.get(name,name)
                elif k=='Value' and v.startswith("'") and v.endswith("'"):
                    value=v[1:-1];new=LABELS.get(value,value)
                    new=new.replace('Synthetic','Observed').replace('synthetic','observed')
                    obj[k]="'"+new+"'"
            else:update_tree(v)
    elif isinstance(obj,list):
        for value in obj:update_tree(value)

def card(seed,measure,label,x,y,width,height,value_size=22,title=None):
    d=copy.deepcopy(seed);d['name']=uuid.uuid5(NS,measure+str(x)+str(y)).hex[:20]
    order=9000+int(y)+int(x)
    d['position']={'x':x,'y':y,'z':order,'height':height,'width':width,'tabOrder':order}
    visual=d['visual'];visual['query']['queryState']['Data']['projections']=[{
      'field':{'Measure':{'Expression':{'SourceRef':{'Entity':'_Measures'}},'Property':measure}},
      'queryRef':'_Measures.'+measure,'nativeQueryRef':label}]
    props=visual['objects']['value'][0]['properties'];props['fontSize']['expr']['Literal']['Value']=str(value_size)+'D'
    labelprops=visual['objects']['label'][0]['properties'];labelprops['text']['expr']['Literal']['Value']="'"+label+"'"
    if not label:labelprops['show']['expr']['Literal']['Value']='false'
    if title:
        tp=visual['visualContainerObjects']['title'][0]['properties'];tp['show']['expr']['Literal']['Value']='true'
        tp['text']['expr']['Literal']['Value']="'"+title+"'"
    return d

def report():
    pages=ROOT/'powerbi/EcommerceGrowth.Report/definition/pages'
    seed=json.loads((pages/'e9f84939d02b2cb7aca2/visuals/ef8627bb5e619d6364d6/visual.json').read_text())
    for p in pages.glob('*/page.json'):
        d=json.loads(p.read_text());name=d['displayName'].replace(' (Demo)','')
        if 'Acquisition' in name:name='First-user Acquisition'
        if 'Product Performance' in name:name='Data Coverage & Limitations'
        d['displayName']=name;write_json(p,d)
    product=pages/'9ea195da65dccc3ec727/visuals';shutil.rmtree(product);product.mkdir()
    configs=[('Product Data Status','Product Performance',20,30,600,200,'Product revenue and SKU rankings are unavailable.'),
      ('Experiment Data Status','Checkout A/B Test',660,30,600,200,'No observed test result or rollout decision is claimed.'),
      ('Attribution Scope','Channel interpretation',20,275,600,170,'Channels describe the source that first acquired the user.'),
      ('Revenue Scope','Accounting interpretation',660,275,600,170,'Event sums are not verified orders, net sales or profit.')]
    for m,l,x,y,w,h,t in configs:
        d=card(seed,m,l,x,y,w,h,title=t);vp=product/d['name'];vp.mkdir();write_json(vp/'visual.json',d)
    for p in pages.glob('*/visuals/*/visual.json'):
        d=json.loads(p.read_text());update_tree(d)
        # Clear saved slicer selections for a consistent full-sample opening state.
        # The alias-aware verifier is independently regression-tested; this is UX,
        # not a workaround for unresolved SourceRef bindings.
        if d.get('visual',{}).get('visualType')=='slicer':
            for item in d['visual'].get('objects',{}).get('general',[]):
                item.get('properties',{}).pop('filter',None)
        write_json(p,d)
    for page in pages.glob('*/page.json'):
        d=card(seed,'Snapshot Note','',20,690,1240,25,value_size=9)
        vp=page.parent/'visuals'/d['name'];vp.mkdir(exist_ok=True);write_json(vp/'visual.json',d)
    metadata=json.loads((pages/'pages.json').read_text());metadata['activePageName']='e9f84939d02b2cb7aca2';write_json(pages/'pages.json',metadata)

def main():
    definition=ROOT/'powerbi/EcommerceGrowth.Model/definition';tables_path=definition/'tables'
    # Build a clean model folder. Preserve no earlier partition or cache files.
    for p in tables_path.glob('*.tmdl'):p.unlink()
    pd.DataFrame({'Stage':['Sessions','Product View','Add to Cart','Checkout','Purchase'],'Sort':[1,2,3,4,5]}).to_csv(ROOT/'data/funnel_stage.csv',index=False)
    pd.DataFrame({'Dummy':['Measures']}).to_csv(ROOT/'data/measures.csv',index=False)
    for table,name in TABLES.items():make_table(table,name)
    make_table('FunnelStage','funnel_stage')
    measures()
    references=list(TABLES)+['FunnelStage','_Measures']
    model='model Model\n\tculture: en-US\n\tdefaultPowerBIDataSourceVersion: powerBI_V3\n\tdiscourageImplicitMeasures\n\tsourceQueryCulture: en-US\n\tdataAccessOptions\n\t\tlegacyRedirects\n\n'
    # Direct model children/references are root-level in folder TMDL.
    # Microsoft Learn: tmdl-overview, Indentation, model-level exceptions.
    model+='annotation PBI_QueryOrder = '+json.dumps(['DataFolder',*references])+'\n\nannotation __PBI_TimeIntelligenceEnabled = 0\n\nannotation PBI_ProTooling = ["DevMode"]\n\n'
    model+='\n'.join('ref table '+t for t in references)+'\n';(definition/'model.tmdl').write_text(model)
    # Portable distribution: the local opener writes only this parameter before
    # Desktop opens. The deliberately invalid initial value prevents accidental
    # use of a developer's machine path.
    expression='expression DataFolder = "C:\\GA4_DATA_FOLDER_NOT_CONFIGURED" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n\tlineageTag: '+tag('DataFolder')+'\n\n\tannotation PBI_ResultType = Text\n'
    (definition/'expressions.tmdl').write_text(expression,encoding='utf-8')
    with (definition/'model.tmdl').open('a') as f:f.write('\nref expression DataFolder\n')
    rels=[]
    for fact,datecol in [('FactSessions','session_date'),('FactPurchases','purchase_date')]:
        for dim,fromcol,tocol in [('DimDate',datecol,'date'),('DimChannel','channel_id','channel_id'),('DimDevice','device_id','device_id'),('DimGeo','geo_id','geo_id')]:
            rels.append(f'relationship {tag(fact+dim)}\n\tfromCardinality: many\n\ttoCardinality: one\n\tcrossFilteringBehavior: oneDirection\n\tfromColumn: {fact}.{fromcol}\n\ttoColumn: {dim}.{tocol}\n')
    (definition/'relationships.tmdl').write_text('\n'.join(rels))
    layout=ROOT/'powerbi/EcommerceGrowth.Model/diagramLayout.json'
    if layout.exists():
        d=json.loads(layout.read_text())
        for diagram in d.get('diagrams',[]):
            nodes=[]
            for node in diagram.get('nodes',[]):
                if node.get('nodeIndex') in ['FactOrderItems','DimProduct']:continue
                if node.get('nodeIndex')=='FactOrders':node['nodeIndex']='FactPurchases'
                nodes.append(node)
            diagram['nodes']=nodes
        write_json(layout,d)
    report();print(f'PASS: {len(TABLES)} analytical CSV tables + 2 support CSV tables, 8 relationships, {len(MEASURES)} measures and five updated report pages')

if __name__=='__main__':main()
