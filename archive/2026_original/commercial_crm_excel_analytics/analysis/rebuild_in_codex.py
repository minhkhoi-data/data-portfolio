"""Optional full artifact rebuild in a Codex primary-runtime environment.
Ordinary analytical reproduction needs only run_analysis.py + pandas.
"""
import json,os,shutil,subprocess,sys,tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
node=os.environ.get('CODEX_PRIMARY_RUNTIME_NODE');modules=os.environ.get('CODEX_PRIMARY_RUNTIME_NODE_MODULES');office=shutil.which('soffice')
if not node or not modules or not office:raise SystemExit('Full authoring requires the Codex primary Node runtime, @oai/artifact-tool and LibreOffice. Use run_analysis.py for ordinary source/metric reproduction.')
subprocess.run([sys.executable,str(ROOT/'analysis/run_analysis.py')],check=True)
with tempfile.TemporaryDirectory(prefix='olist-authoring-') as temporary:
 tmp=Path(temporary);(tmp/'node_modules').symlink_to(modules,target_is_directory=True);(tmp/'fragments').mkdir();(tmp/'evaluated_final').mkdir()
 env=dict(os.environ,OLIST_PROJECT_ROOT=str(ROOT),OLIST_BUILD_DIR=str(tmp))
 for name in ['build_workbook.mjs','build_fragment.mjs','repair_layout.mjs','repair_styles.mjs']:shutil.copy2(ROOT/'analysis'/name,tmp/name)
 subprocess.run([node,'--max-old-space-size=2048',str(tmp/'build_workbook.mjs')],env=dict(env,OLIST_BUILD_MODE='skeleton'),check=True)
 data=json.loads((ROOT/'analysis/outputs/workbook_input.json').read_text());jobs=[(kind,start) for kind,key in [('Leads','leads'),('Sales_Items','items')] for start in range(0,len(data[key]),400)]
 def fragment(job):
  kind,start=job;subprocess.run([node,'--max-old-space-size=1024',str(tmp/'build_fragment.mjs'),kind,str(start),'400',str(tmp/'fragments'/f'{kind}_{start:05}.xlsx')],env=env,check=True)
 with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(fragment,jobs))
 subprocess.run([sys.executable,str(ROOT/'analysis/assemble_fragments.py')],env=env,check=True)
 subprocess.run([node,str(tmp/'repair_layout.mjs'),str(tmp/'layout_fragment.xlsx')],env=env,check=True)
 subprocess.run([sys.executable,str(ROOT/'analysis/apply_layout_fragment.py'),'--fragment',str(tmp/'layout_fragment.xlsx')],env=env,check=True)
 subprocess.run([node,str(tmp/'repair_styles.mjs'),str(tmp/'base-style-fragment.xlsx')],env=env,check=True)
 subprocess.run([sys.executable,str(ROOT/'analysis/apply_styles_fragment.py'),'--fragment',str(tmp/'base-style-fragment.xlsx')],env=env,check=True)
 subprocess.run([office,'-env:UserInstallation='+(tmp/'calc_profile').as_uri(),'--headless','--convert-to','xlsx','--outdir',str(tmp/'evaluated_final'),str(ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx')],check=True)
 subprocess.run([sys.executable,str(ROOT/'audit/verify_workbook.py'),'--calc',str(tmp/'evaluated_final/Olist_CRM_Acquisition_Seller_Value.xlsx')],check=True)
 subprocess.run([sys.executable,str(ROOT/'analysis/finalize_workbook.py')],env=env,check=True)
 subprocess.run([sys.executable,str(ROOT/'audit/verify_workbook.py'),'--calc',str(ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx')],check=True)
