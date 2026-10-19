"""One entry point: rebuild, fixtures, independent checks, then fresh notebook.

Exit 2 means notebook dependencies are unavailable, not a completed notebook run.
No package installation or network is performed by this runner.
"""
import importlib.util,json,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    audit=ROOT/'audit';status=audit/'remaster_execution.json'
    record={'status':'RUNNING','outputs_valid':False,'fresh_notebook':'NOT_RUN','steps':[]}
    status.write_text(json.dumps(record,indent=2))
    commands=[('pipeline',['analysis/run_analysis.py']),('fixture_tests',['-m','unittest','discover','-s','tests']),('pipeline_validator',['analysis/validate_project.py']),('independent_SQL_and_boundaries',['analysis/verify_release.py'])]
    try:
        for name,args in commands:
            with (audit/f'remaster_{name}.log').open('w') as stream:
                subprocess.run([sys.executable,*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
            record['steps'].append({'step':name,'status':'PASS','log':f'audit/remaster_{name}.log'})
            status.write_text(json.dumps(record,indent=2))
        missing=[n for n in ['nbformat','nbclient','ipykernel','jupyter_client','IPython'] if importlib.util.find_spec(n) is None]
        record['input_sha256']=sha(ROOT/'data/online_retail_II.csv.gz')
        record['config_sha256']=sha(ROOT/'analysis/config.json')
        if missing:
            record.update(status='ANALYTICAL_PASS_NOTEBOOK_BLOCKED',outputs_valid=True,fresh_notebook='BLOCKED',missing_dependencies=missing,notebook_execution_note='Bundled historical notebook execution remains historical evidence; not rerun by this command.')
            status.write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));return 2
        with (audit/'remaster_notebook.log').open('w') as stream:
            subprocess.run([sys.executable,'analysis/execute_notebook.py'],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
        record.update(status='PASS',outputs_valid=True,fresh_notebook='PASS')
        record['steps'].append({'step':'fresh_notebook','status':'PASS','log':'audit/remaster_notebook.log'})
    except BaseException as error:
        record.update(status='FAIL',outputs_valid=False,error=str(error));status.write_text(json.dumps(record,indent=2));raise
    record['input_sha256']=sha(ROOT/'data/online_retail_II.csv.gz')
    record['config_sha256']=sha(ROOT/'analysis/config.json')
    status.write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
