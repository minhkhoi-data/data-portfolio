"""One controlled rebuild; do not report partial outputs as valid on failure."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from evidence_identity import matches
p=argparse.ArgumentParser(description='Rebuild GA4 tables/model/report and check the produced files.')
p.add_argument('--dotnet-root');p.add_argument('--tom-lib');p.add_argument('--pythonnet-site');p.add_argument('--m-parser');p.add_argument('--schema-cache');p.add_argument('--pwsh')
a=p.parse_args()
if bool(a.dotnet_root)!=bool(a.tom_lib):p.error('Use dotnet-root and tom-lib together')
status=ROOT/'audit/evidence/build_status.json'
status.write_text(json.dumps({'status':'RUNNING','outputs_valid':False}))
step=None
try:
    history=ROOT/'audit/history/pre_remaster';history.mkdir(parents=True,exist_ok=True)
    saved={}
    for evidence in ['tmdl_parser.json','m_syntax_parser.json','report_schema.json','opener_tests.json']:
        stale=ROOT/'audit/evidence'/evidence
        archive=history/evidence
        if stale.exists():
            if not archive.exists():archive.write_bytes(stale.read_bytes())
            stale.unlink()
        if archive.exists():saved[evidence]=json.loads(archive.read_text())
    for step in ['test_verifier.py','test_pipeline.py','pipeline.py','build_model.py','build_docs.py','build_preview.py','build_runtime.py','build_native_contract.py']:
        print('Running '+step,flush=True)
        subprocess.run([sys.executable,str(ROOT/'scripts'/step)],cwd=ROOT,check=True)
    optional={}
    if a.dotnet_root:
        step='verify_tmdl_parser.py';cmd=[sys.executable,str(ROOT/'scripts'/step),'--dotnet-root',a.dotnet_root,'--tom-lib',a.tom_lib]
        if a.pythonnet_site:cmd+=['--pythonnet-site',a.pythonnet_site]
        subprocess.run(cmd,check=True);optional['official_TMDL']='PASS'
    else:optional['official_TMDL']='NOT_RUN'
    if a.m_parser:
        step='verify_m_syntax.cjs';subprocess.run(['node',str(ROOT/'scripts'/step),a.m_parser],check=True);optional['official_M_grammar']='PASS'
    else:optional['official_M_grammar']='NOT_RUN'
    if a.schema_cache:
        step='verify_report_schema.py';subprocess.run([sys.executable,str(ROOT/'scripts'/step),'--cache',a.schema_cache],check=True);optional['report_JSON_schema']='PASS'
    else:optional['report_JSON_schema']='NOT_RUN'
    if a.pwsh:
        step='verify_opener.py';cmd=[sys.executable,str(ROOT/'scripts'/step),'--pwsh',a.pwsh]
        if a.m_parser:cmd+=['--m-parser',a.m_parser]
        subprocess.run(cmd,check=True);optional['local_opener']='PASS'
    else:optional['local_opener']='NOT_RUN'
    for name,key in [('tmdl_parser.json','official_TMDL'),('m_syntax_parser.json','official_M_grammar'),('report_schema.json','report_JSON_schema'),('opener_tests.json','local_opener')]:
        if optional[key]=='NOT_RUN' and name in saved and matches(name,saved[name]):
            item=saved[name];item['evidence_reuse']='Historical execution; SHA256-identical tested inputs verified during this rebuild. No fresh parser execution.'
            (ROOT/'audit/evidence'/name).write_text(json.dumps(item,indent=2))
            optional[key]='PASS_IDENTICAL_INPUT_REUSED'
    (ROOT/'audit/evidence/optional_validators.json').write_text(json.dumps(optional,indent=2))
    step='verify_project.py';subprocess.run([sys.executable,str(ROOT/'scripts'/step)],check=True)
    status.write_text(json.dumps({'status':'PASS','outputs_valid':True,'optional_validators':optional,'native_power_bi':'NOT_VERIFIED'},indent=2))
except Exception as error:
    status.write_text(json.dumps({'status':'FAIL','outputs_valid':False,'failed_step':step,'error':str(error)},indent=2));raise
