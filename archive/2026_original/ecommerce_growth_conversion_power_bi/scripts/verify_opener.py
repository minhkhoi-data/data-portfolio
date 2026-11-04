"""Exercise actual PowerShell configuration without launching Power BI.

PowerShell 7 on Linux validates file/hash/path behavior. This does not test
Windows PowerShell 5.1, Windows associations, Desktop launch or M execution.
"""
import argparse,hashlib,json,re,shutil,subprocess,tempfile
from pathlib import Path
from pipeline import ROOT,sha256

p=argparse.ArgumentParser();p.add_argument('--pwsh',required=True);p.add_argument('--m-parser');a=p.parse_args()
cases=[]
def snapshot(root):return {f.relative_to(root).as_posix():sha256(f) for f in root.rglob('*') if f.is_file()}
def run(root):
 return subprocess.run([a.pwsh,'-NoLogo','-NoProfile','-File',str(root/'scripts/Open-GA4.ps1'),'-ConfigureOnly'],capture_output=True,text=True)
def assert_case(name,condition):
 if not condition:raise AssertionError(name)
 cases.append({'case':name,'status':'PASS'})
def value(text):
 # Decode the documented M literal escapes once, preserving a source path
 # containing a literal #(lf) sequence after #(#) unescaping.
 token=re.match(r'^expression DataFolder = "((?:[^\"]|\"\")*)" meta ',text).group(1)
 token=token.replace('""','"')
 return re.sub(r'#\((#|cr|lf)\)',lambda m:{'#':'#','cr':'\r','lf':'\n'}[m.group(1)],token)
with tempfile.TemporaryDirectory(prefix='ga4_opener_') as temp:
 root=Path(temp)/"GA4 khoảng trắng #(lf) 'quote' $literal"
 root.mkdir()
 items=['runtime_manifest.json','scripts/Open-GA4.ps1','powerbi/MO_GA4_CSV_13_10.pbip','powerbi/EcommerceGrowth.Model/definition/expressions.tmdl']
 manifest=json.loads((ROOT/'runtime_manifest.json').read_text())
 items += [i['path'] for i in manifest['files']]
 for name in items:
  dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dst)
 parameter=root/'powerbi/EcommerceGrowth.Model/definition/expressions.tmdl'
 before=snapshot(root);result=run(root)
 assert_case('ConfigureOnly_succeeds_spaces_Unicode_hash_apostrophe_dollar',result.returncode==0)
 after=snapshot(root);changed={k for k in before if before[k]!=after[k]}
 assert_case('Only_DataFolder_file_changes',changed=={'powerbi/EcommerceGrowth.Model/definition/expressions.tmdl'})
 assert_case('Parameter_decodes_to_exact_local_data_path',value(parameter.read_text())==str((root/'data').resolve()))
 assert_case('Parameter_keeps_metadata_and_has_no_BOM',parameter.read_text().splitlines()[1:]==(ROOT/'powerbi/EcommerceGrowth.Model/definition/expressions.tmdl').read_text().splitlines()[1:] and not parameter.read_bytes().startswith(b'\xef\xbb\xbf'))
 if a.m_parser:
  expression=parameter.read_text().splitlines()[0].split('expression DataFolder = ',1)[1]
  js='const fs=require("fs");const PQ=require(process.argv[1]);(async()=>{const task=await PQ.TaskUtils.tryLexParse(PQ.DefaultSettings,fs.readFileSync(0,"utf8"));if(PQ.TaskUtils.isError(task))process.exit(1);PQ.TaskUtils.assertIsParseStageOk(task)})().catch(()=>process.exit(1));'
  parsed=subprocess.run(['node','-e',js,str(Path(a.m_parser).resolve())],input=expression,text=True,capture_output=True)
  assert_case('Configured_parameter_official_M_grammar',parsed.returncode==0)
 previous=parameter.stat().st_mtime_ns;result=run(root)
 assert_case('Second_run_idempotent',result.returncode==0 and parameter.stat().st_mtime_ns==previous)
 moved=root.with_name('GA4 relocated to another folder');root.rename(moved);root=moved;parameter=root/'powerbi/EcommerceGrowth.Model/definition/expressions.tmdl'
 result=run(root)
 assert_case('Relocation_updates_DataFolder',result.returncode==0 and value(parameter.read_text())==str((root/'data').resolve()))
 before_parameter=parameter.read_bytes()
 damaged=root/'data/fact_sessions.csv'
 with damaged.open('ab') as f:f.write(b'\nBAD_ROW')
 result=run(root)
 assert_case('Altered_CSV_rejected_before_parameter_write',result.returncode!=0 and 'CSV differs' in result.stderr and parameter.read_bytes()==before_parameter)
 shutil.copy2(ROOT/'data/fact_sessions.csv',damaged)
 missing=root/'data/dim_device.csv';missing.unlink();result=run(root)
 assert_case('Missing_CSV_rejected_before_parameter_write',result.returncode!=0 and 'Missing CSV' in result.stderr and parameter.read_bytes()==before_parameter)
 shutil.copy2(ROOT/'data/dim_device.csv',missing)
 project=root/'powerbi/MO_GA4_CSV_13_10.pbip';project.unlink();result=run(root)
 assert_case('Missing_PBIP_rejected_before_parameter_write',result.returncode!=0 and 'project file is missing' in result.stderr and parameter.read_bytes()==before_parameter)
assert_case('Launcher_ASCII_compatible_source',all(b<128 for b in (ROOT/'scripts/Open-GA4.ps1').read_bytes()))
proof={'status':'PASS','cases':cases,'powershell_version':subprocess.check_output([a.pwsh,'-NoLogo','-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()'],text=True).strip(),'file_sha256':{n:sha256(ROOT/n) for n in ['MO_PROJECT.cmd','scripts/Open-GA4.ps1','runtime_manifest.json']},'scope':'ConfigureOnly filesystem tests on PowerShell 7/Linux. Windows PowerShell 5.1 and native launch association are NOT VERIFIED. No M functions or Desktop executed.'}
(ROOT/'audit/evidence/opener_tests.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
