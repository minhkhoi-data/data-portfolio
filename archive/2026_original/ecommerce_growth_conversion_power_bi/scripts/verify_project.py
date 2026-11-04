"""Analytical and structural checks. Does not execute Power Query or DAX."""
import csv,json,re
import numpy as np
import pandas as pd
from pipeline import ROOT,TABLES,STAGES,ordered_times,sha256
from build_model import MEASURES,TEXT,DATES,DECIMAL,DOUBLE

checks=[]
def check(name,condition,detail=''):
    checks.append({'check':name,'status':'PASS' if bool(condition) else 'FAIL','scope':'analytical/static','detail':str(detail)})

def load(name):
    # Never infer pseudonymous identifiers as floating-point numbers.
    h=pd.read_csv(ROOT/'data'/f'{name}.csv',nrows=0)
    return pd.read_csv(ROOT/'data'/f'{name}.csv',dtype={c:str for c in h if c in TEXT|DATES},keep_default_na=False)

def walk(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values():yield from walk(v)
    elif isinstance(obj,list):
        for v in obj:yield from walk(v)

def scoped_nodes(obj, aliases=None):
    """Resolve query-local From aliases without leaking them to sibling queries."""
    aliases=dict(aliases or {})
    if isinstance(obj,dict):
        for item in obj.get('From',[]):
            if isinstance(item,dict) and 'Name' in item and 'Entity' in item:
                aliases[item['Name']]=item['Entity']
        yield obj,aliases
        for value in obj.values():yield from scoped_nodes(value,aliases)
    elif isinstance(obj,list):
        for value in obj:yield from scoped_nodes(value,aliases)

def field_binding(member, aliases):
    ref=member.get('Expression',{}).get('SourceRef',{})
    entity=ref.get('Entity') or aliases.get(ref.get('Source'))
    return entity,member.get('Property')

def within_bounds(position, width, height, epsilon=1e-7):
    return (position['x']>=-epsilon and position['y']>=-epsilon and
            position['x']+position['width']<=width+epsilon and
            position['y']+position['height']<=height+epsilon)

def main():
    checks.clear()
    (ROOT/'audit/evidence/verification.json').write_text(json.dumps({'status':'RUNNING','outputs_valid':False}))
    s=load('fact_sessions');p=load('fact_purchases');t={v:load(v) for v in TABLES.values()}
    q=json.loads((ROOT/'audit/evidence/data_quality.json').read_text())
    prov=json.loads((ROOT/'data/source/provenance.json').read_text())
    k=pd.read_csv(ROOT/'outputs/kpi_summary.csv').set_index('metric').value
    check('source_projection_sha256',sha256(ROOT/'data/source/ga4_events.csv.gz')==prov['projection_sha256'])
    check('all_source_rows_retained',q['source_rows']==prov['source_rows']==4295584)
    check('source_event_identifiers_unique',q['duplicate_source_event_ids']==0)
    check('session_composite_key_unique',s.session_id.is_unique and s.session_id.str.contains('|',regex=False).all())
    check('sessions_users_totals',len(s)==360129 and s.user_id.nunique()==270154)
    check('purchase_event_grain_keys',len(p)==5692 and p.purchase_key.is_unique and p.source_event_id.is_unique)
    check('purchase_session_lineage',p.session_id.isin(s.session_id).all())
    check('purchase_user_lineage',p.merge(s[['session_id','user_id']],on='session_id',suffixes=('_p','_s'),validate='many_to_one').eval('user_id_p == user_id_s').all())
    check('calendar_contiguous',t['dim_date'].date.tolist()==pd.date_range('2020-11-01','2021-01-31').strftime('%Y-%m-%d').tolist())
    check('revenue_full_snapshot',abs(p.purchase_revenue_usd.sum()-362165)<.0001)
    attributable=p.groupby('session_id').agg(revenue=('purchase_revenue_usd','sum'),events=('purchase_key','size'))
    r=s.set_index('session_id').join(attributable).fillna({'revenue':0,'events':0})
    check('per_session_purchase_sums',np.allclose(r.session_revenue,r.revenue) and np.array_equal(r.purchase_event_count,r.events))
    check('any_purchase_flags',np.array_equal(s.purchase.to_numpy(),s.purchase_event_count.gt(0).astype(int).to_numpy()))
    check('independent_monthly_revenue',p.groupby(p.purchase_date.str[:7]).purchase_revenue_usd.sum().to_dict()=={'2020-11':144260,'2020-12':160555,'2021-01':57350})
    check('independent_monthly_purchase_events',p.groupby(p.purchase_date.str[:7]).size().to_dict()=={'2020-11':2054,'2020-12':2434,'2021-01':1204})
    check('source_controls_reconciled',pd.read_csv(ROOT/'outputs/source_reconciliation.csv').status.eq('MATCH').all())
    check('any_vs_ordered_flags',all((s['ordered_'+x]<=s[x]).all() for x in STAGES))
    check('strict_funnel_nested',all((s['ordered_'+STAGES[i]]<=s['ordered_'+STAGES[i-1]]).all() for i in range(1,4)))
    check('strict_funnel_totals',[int(s['ordered_'+x].sum()) for x in STAGES]==[77020,14380,5187,2778])
    # Independent edge cases: shuffled rows, tied steps, missing predecessors,
    # early cart followed by valid later cart, repeated purchases.
    examples=[('valid','purchase',8),('valid','add_to_cart',4),('valid','view_item',2),('valid','begin_checkout',6),
      ('tie','view_item',2),('tie','add_to_cart',2),('tie','begin_checkout',3),('tie','purchase',4),
      ('missing','view_item',1),('missing','purchase',9),
      ('later','add_to_cart',1),('later','view_item',2),('later','add_to_cart',4),('later','begin_checkout',6),('later','purchase',8),('later','purchase',9)]
    times=ordered_times(pd.DataFrame(examples,columns=['session_id','event_name','timestamp']))
    check('funnel_ties_do_not_establish_order','tie' not in times['add_to_cart'])
    check('funnel_missing_step_not_imputed','missing' not in times['purchase'])
    check('funnel_earliest_eligible_after_predecessor',times['add_to_cart']['later']==4 and times['purchase']['later']==8)
    check('funnel_ignores_input_row_order',set(times['purchase'].index)=={'valid','later'})
    check('unknown_engagement_not_imputed',(s.engagement_known.eq(0).sum()==218) and s.loc[s.engagement_known.eq(0),'engaged_session'].eq('').all())
    engaged=pd.to_numeric(s.engaged_session.replace('',np.nan));check('engagement_known_denominator',np.isclose(k['Engagement Rate'],engaged.sum()/s.engagement_known.sum()))
    check('new_returning_status_domain',s.is_new_user.isin([-1,0,1]).all())
    check('multiple_event_purchasers',p.groupby('user_id').size().gt(1).sum()==775 and np.isclose(k['Multiple-event Purchaser Share'],775/4419))
    check('masked_acquisition_retained',s.merge(t['dim_channel'],on='channel_id').channel.eq('Unknown / masked').sum()==119526)
    masked_sources=s.source.str.strip().str.lower().eq('(data deleted)') | s.medium.str.strip().str.lower().eq('(data deleted)')
    mapped=s.merge(t['dim_channel'],on='channel_id',validate='many_to_one')
    check('data_deleted_acquisition_not_observed_channel',int(masked_sources.sum())==22632 and mapped.loc[masked_sources,'channel'].eq('Unknown / masked').all())
    check('missing_order_identifiers_disclosed',p.transaction_id_known.eq(0).sum()==906 and q['additional_rows_with_repeated_known_transaction_id']==335 and q['distinct_repeated_known_transaction_ids']==326)
    for name in ['channel','device','country']:
        a=pd.read_csv(ROOT/'outputs'/f'{name}_performance.csv')
        check(name+'_aggregate_reconciles',a.sessions.sum()==len(s) and a.purchase_events.sum()==len(p) and np.isclose(a.revenue.sum(),p.purchase_revenue_usd.sum()))
        check(name+'_rates_denominators',np.allclose(a.conversion_rate,a.purchase_sessions/a.sessions) and np.allclose(a.revenue_per_session,a.session_attributed_revenue/a.sessions))
    m=pd.read_csv(ROOT/'outputs/monthly_performance.csv')
    check('monthly_cohort_revenue_reconciles',np.isclose(m.session_attributed_revenue.sum(),p.purchase_revenue_usd.sum()) and np.allclose(m.revenue_per_session,m.session_attributed_revenue/m.sessions))
    definition=ROOT/'powerbi/EcommerceGrowth.Model/definition';columns={}
    parser_file=ROOT/'audit/evidence/tmdl_parser.json'
    if parser_file.exists():
        parser=json.loads(parser_file.read_text())
        current_hashes={f.relative_to(definition).as_posix():sha256(f) for f in sorted(definition.rglob('*.tmdl'))}
        check('official_TMDL_parser_evidence_matches_current_model',parser['status']=='PASS' and parser['current_model_sha256']==current_hashes)
    m_parser_file=ROOT/'audit/evidence/m_syntax_parser.json'
    if m_parser_file.exists():
        mp=json.loads(m_parser_file.read_text())
        check('official_M_syntax_evidence_matches_current_model',mp['status']=='PASS' and len(mp['tables'])==8 and all(sha256(definition/'tables'/f"{item['table']}.tmdl")==item['tmdl_sha256'] for item in mp['tables']) and sha256(definition/'expressions.tmdl')==mp['parameter_sha256'])
    runtime=json.loads((ROOT/'runtime_manifest.json').read_text())
    runtime_tables={**TABLES,'FunnelStage':'funnel_stage','_Measures':'measures'}
    check('runtime_manifest_eight_CSV_files',runtime['release']=='GA4_CSV_REBUILD_2026_10_13' and {i['path'] for i in runtime['files']}=={f'data/{n}.csv' for n in runtime_tables.values()})
    check('runtime_CSV_hashes_and_sizes',all(sha256(ROOT/i['path'])==i['sha256'] and (ROOT/i['path']).stat().st_size==i['bytes'] for i in runtime['files']))
    for table,name in TABLES.items():
        text=(definition/'tables'/f'{table}.tmdl').read_text()
        columns[table]=set(re.findall(r'^\tcolumn (.+)$',text,re.M))
        with (ROOT/'data'/f'{name}.csv').open(encoding='utf-8',newline='') as stream:
            reader=csv.reader(stream);headers=next(reader);expected_rows=list(reader)
        check(table+'_CSV_row_width_and_count',len(expected_rows)==len(t[name]) and all(len(row)==len(headers) for row in expected_rows))
        check(table+'_file_backed_CSV_loader',f'File.Contents(DataFolder & "/{name}.csv")' in text and 'Csv.Document(' in text and 'Table.PromoteHeaders(' in text and 'Encoding=65001' in text and 'ExtraValues=ExtraValues.Error' in text and 'Binary.Decompress(' not in text and 'EmbeddedBase64' not in text and len(text)<20000)
        header_list=re.search(r'Table.ColumnNames\(Headers\) = (\{[^}]+\})',text).group(1)
        check(table+'_runtime_header_validation',re.findall(r'"([^\"]+)"',header_list)==headers)
        del expected_rows
        check(table+'_column_schema_exact',columns[table]==set(t[name].columns))
        typed=dict(re.findall(r'\{"([^\"]+)", ([^}]+)\}',text))
        expected={c:'type text' if c in TEXT else 'type date' if c in DATES else 'Currency.Type' if c in DECIMAL else 'type number' if c in DOUBLE else 'Int64.Type' for c in t[name].columns}
        check(table+'_M_types',typed==expected)
    columns['FunnelStage']={'Stage','Sort'};columns['_Measures']={'Dummy'}
    check('support_tables_import_from_CSV',all(f'File.Contents(DataFolder & "/{name}.csv")' in (definition/'tables'/f'{table}.tmdl').read_text() for table,name in [('FunnelStage','funnel_stage'),('_Measures','measures')]))
    check('no_calculated_partitions',all(' = calculated' not in f.read_text() for f in (definition/'tables').glob('*.tmdl')))
    parameter=(definition/'expressions.tmdl').read_text()
    check('DataFolder_parameter_only',bool(re.match(r'^expression DataFolder = "(?:[^"\n]|"")+" meta \[IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true\]$',parameter,re.M)) and len(re.findall(r'^expression ',parameter,re.M))==1 and (definition/'model.tmdl').read_text().count('ref expression DataFolder')==1)
    check('model_table_reference_closure',set(re.findall(r'^ref table (.+)$',(definition/'model.tmdl').read_text(),re.M))==set(columns))
    check('model_annotations_and_table_refs_at_root_level',all(line==line.lstrip() for line in (definition/'model.tmdl').read_text().splitlines() if line.strip().startswith(('annotation ','ref table '))))
    scope_violations=[]
    for tablefile in (definition/'tables').glob('*.tmdl'):
        in_annotation=False
        for number,line in enumerate(tablefile.read_text().splitlines(),1):
            if not line.strip():in_annotation=False;continue
            if line.startswith('\t\tannotation '):in_annotation=True;continue
            if in_annotation and line.startswith('\t\t') and not line.startswith('\t\t\t'):scope_violations.append((tablefile.name,number))
            if not line.startswith('\t\t'):in_annotation=False
    check('column_properties_do_not_follow_annotation_without_scope_break',not scope_violations,scope_violations)
    date_text=(definition/'tables/DimDate.tmdl').read_text().split('\tcolumn year',1)[0]
    check('date_key_precedes_annotation',date_text.index('\t\tisKey')<date_text.index('\t\tannotation UnderlyingDateTimeDataType'))
    check('obsolete_synthetic_tables_removed',all(not (definition/'tables'/f'{n}.tmdl').exists() for n in ['FactOrders','FactOrderItems','DimProduct']))
    rels=(definition/'relationships.tmdl').read_text().split('relationship ')[1:]
    check('relationship_count',len(rels)==8)
    for i,rel in enumerate(rels):
        f,fc=re.search(r'fromColumn: (\w+)\.(\w+)',rel).groups();d,dc=re.search(r'toColumn: (\w+)\.(\w+)',rel).groups()
        fact=t[TABLES[f]];dim=t[TABLES[d]]
        check(f'{f}_{d}_unique_dimension_and_FK',dim[dc].is_unique and fact[fc].isin(dim[dc]).all())
        properties=dict(re.findall(r'^\s*(\w+): (\w+)\s*$',rel,re.M))
        check(f'{f}_{d}_direction',f.startswith('Fact') and d.startswith('Dim') and properties.get('crossFilteringBehavior','oneDirection')=='oneDirection' and properties.get('toCardinality','one')=='one' and properties.get('fromCardinality','many')=='many')
    actual_measures=(definition/'tables/_Measures.tmdl').read_text()
    for name,(expression,_) in MEASURES.items():
        match=re.search(r"^\tmeasure '"+re.escape(name)+r"' = (.*?)(?=\n\t\tlineageTag:)",actual_measures,re.M|re.S)
        check('DAX_definition_'+name,match is not None and re.sub(r'\s+',' ',match.group(1)).strip()==re.sub(r'\s+',' ',expression).strip())
    check('DAX_qualified_column_references',all(table in columns and col in columns[table] for expr,_ in MEASURES.values() for table,col in re.findall(r'(\w+)\[([^\]]+)\]',expr)))
    unqualified=[]
    for expr,_ in MEASURES.values():
        cleaned=re.sub(r'\w+\[[^\]]+\]','',expr)
        unqualified+=re.findall(r'\[([^\]]+)\]',cleaned)
    check('DAX_measure_reference_closure',set(unqualified)<=set(MEASURES)|{'__Events'})
    # JSON parsing and reference closure; native engine validation remains separate.
    power=ROOT/'powerbi';json_files=list(power.rglob('*.json'))+[power/'MO_GA4_CSV_13_10.pbip',power/'EcommerceGrowth.Report/definition.pbir',power/'EcommerceGrowth.Model/definition.pbism']
    for file in json_files:json.loads(file.read_text())
    check('all_PowerBI_JSON_parse',True,f'{len(json_files)} files parsed')
    pbip=json.loads((power/'MO_GA4_CSV_13_10.pbip').read_text())
    rp=power/pbip['artifacts'][0]['report']['path'];ref=json.loads((rp/'definition.pbir').read_text())['datasetReference']['byPath']['path']
    check('PBIP_relative_paths_resolve',(rp/ref/'definition.pbism').is_file())
    pages=rp/'definition/pages';pagefiles=list(pages.glob('*/page.json'));metadata=json.loads((pages/'pages.json').read_text())
    pageids={x.parent.name for x in pagefiles}
    check('five_pages_and_order',len(pageids)==5 and len(metadata['pageOrder'])==5 and set(metadata['pageOrder'])==pageids and metadata['activePageName'] in pageids)
    unresolved=[];bounds=[];identity=[];allvisuals=[]
    for pagefile in pagefiles:
        page=json.loads(pagefile.read_text());tab=[];names=[]
        for vf in pagefile.parent.glob('visuals/*/visual.json'):
            v=json.loads(vf.read_text());allvisuals.append(v);pos=v['position'];tab.append(pos['tabOrder']);names.append(v['name'])
            if not within_bounds(pos,page['width'],page['height']):bounds.append(str(vf))
            if v['name']!=vf.parent.name:identity.append(str(vf))
            for node,aliases in scoped_nodes(v):
                for kind in ['Measure','Column']:
                    if kind in node:
                        member=node[kind];entity,prop=field_binding(member,aliases)
                        if kind=='Measure' and (entity!='_Measures' or prop not in MEASURES):unresolved.append((entity,prop))
                        if kind=='Column' and (entity not in columns or prop not in columns[entity]):unresolved.append((entity,prop))
        check(page['displayName']+'_tab_order_unique',len(tab)==len(set(tab)))
        check(page['displayName']+'_visual_names_unique',len(names)==len(set(names)))
    check('all_visual_field_bindings_resolve',not unresolved,unresolved)
    check('no_stale_order_or_repeat_labels',not any(any(token in json.dumps(v) for token in ['Repeat within filter','Repeat Rate','_Measures.AOV','_Measures.Transactions']) for v in allvisuals))
    check('visuals_within_page_bounds',not bounds,bounds)
    check('visual_folder_identity_matches',not identity,identity)
    check('coverage_page_and_snapshot_footer',any(json.loads(x.read_text())['displayName']=='Data Coverage & Limitations' for x in pagefiles) and sum('Snapshot Note' in json.dumps(v) for v in allvisuals)==5)
    check('no_developer_machine_path',all('/workspace/' not in f.read_text() and 'EmbeddedBase64' not in f.read_text() for f in definition.rglob('*.tmdl')))
    check('runtime_launcher_present',all((ROOT/f).is_file() for f in ['MO_PROJECT.cmd','scripts/Open-GA4.ps1','runtime_manifest.json']))
    for file in ['report_schema.json','opener_tests.json']:
        evidence=ROOT/'audit/evidence'/file
        if not evidence.exists():continue
        item=json.loads(evidence.read_text())
        if file=='report_schema.json':
            check('report_JSON_schema_evidence_current',item['status']=='PASS' and bool(item['files']) and all(sha256(ROOT/f['file'])==f['sha256'] for f in item['files']))
        else:
            check('opener_config_tests_evidence_current',item['status']=='PASS' and all(sha256(ROOT/f)==h for f,h in item['file_sha256'].items()))
    for file in ['START_HERE_VI.md','docs/METHODOLOGY.md','audit/NATIVE_STATUS.md','outputs/figures/ga4_overview.png']:
        check('required_file_'+file,(ROOT/file).is_file())
    check('pipeline_valid',json.loads((ROOT/'audit/evidence/pipeline_status.json').read_text())['outputs_valid'])
    report=pd.DataFrame(checks);report.to_csv(ROOT/'audit/CHECKS.csv',index=False)
    result={'status':'PASS' if report.status.eq('PASS').all() else 'FAIL','checks':len(report),'passed':int(report.status.eq('PASS').sum()),'failed':int(report.status.eq('FAIL').sum()),'native_power_bi':'NOT_VERIFIED','scope':'Analytical/static checks and current validator evidence; this verifier does not execute native DAX, Windows M or Desktop.'}
    (ROOT/'audit/evidence/verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2));print(report.loc[report.status.eq('FAIL')].to_string(index=False))
    if result['failed']:raise SystemExit(1)

if __name__=='__main__':
    try:main()
    except BaseException as error:
        if not isinstance(error,SystemExit) or error.code:
            status=ROOT/'audit/evidence/verification.json'
            previous=json.loads(status.read_text()) if status.exists() else {}
            previous.update({'status':'FAIL','outputs_valid':False,'error':str(error)})
            status.write_text(json.dumps(previous,indent=2))
        raise
