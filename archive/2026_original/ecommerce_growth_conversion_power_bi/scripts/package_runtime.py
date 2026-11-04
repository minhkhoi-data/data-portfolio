"""Package the complete native-opening subset; source/code live in full ZIP."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from pipeline import ROOT,sha256

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if json.loads((ROOT/'audit/evidence/verification.json').read_text())['status']!='PASS':raise ValueError('Refusing failed build')
files=list((ROOT/'powerbi').rglob('*'))
files=[f for f in files if f.is_file() and '.pbi' not in f.parts]
files+=[ROOT/n for n in ['MO_PROJECT.cmd','BAT_DAU.txt','START_HERE_VI.md','runtime_manifest.json','scripts/Open-GA4.ps1','audit/NATIVE_STATUS.md','audit/M_ENGINE_MITIGATION.md','audit/evidence/tmdl_parser.json','audit/evidence/m_syntax_parser.json','audit/evidence/report_schema.json','audit/evidence/opener_tests.json','audit/evidence/m_engine_failure.json']]
files+=[ROOT/i['path'] for i in json.loads((ROOT/'runtime_manifest.json').read_text())['files']]
entries=[{'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':sha256(f)} for f in sorted(files)]
root='GA4_CSV_OPEN_13_10';a.output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(a.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(files):z.write(f,root+'/'+f.relative_to(ROOT).as_posix())
 z.writestr(root+'/MANIFEST.json',json.dumps({'scope':'Native-opening subset: eight CSV files and complete five-page report/model. Full source, rebuild scripts and analytical outputs are in the complete project ZIP.','files':entries},indent=2)+'\n')
with zipfile.ZipFile(a.output) as z:
 if z.testzip():raise ValueError('Archive CRC check failed')
 for item in entries:
  content=z.read(root+'/'+item['path'])
  if hashlib.sha256(content).hexdigest()!=item['sha256'] or len(content)!=item['bytes']:raise ValueError('Archive mismatch: '+item['path'])
print(json.dumps({'status':'PASS','path':str(a.output.resolve()),'bytes':a.output.stat().st_size,'sha256':sha256(a.output),'file_count':len(entries),'native_power_bi':'NOT_VERIFIED'},indent=2))
