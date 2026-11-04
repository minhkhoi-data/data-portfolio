"""Package complete project and independently verify every archived byte hash."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from pipeline import ROOT,sha256

parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--root-name',default='GA4_CSV_REBUILD_13_10');args=parser.parse_args()
if not args.root_name or '/' in args.root_name or '\\' in args.root_name or args.root_name in {'.','..'}:raise ValueError('Invalid archive root')
verification=json.loads((ROOT/'audit/evidence/verification.json').read_text())
if verification['status']!='PASS':raise SystemExit('Refusing to package a failed build')
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(n in {'__pycache__','.pbi'} for n in p.parts) and p.name!='MANIFEST.json' and p.suffix!='.pyc' and not p.name.startswith('.ga4_events.csv.gz.'))
entries=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in files]
manifest=ROOT/'MANIFEST.json';manifest.write_text(json.dumps({'scope':'All packaged project files except this self-referencing manifest','files':entries},indent=2)+'\n')
args.output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for p in [*files,manifest]:
        z.write(p,arcname=args.root_name+'/'+p.relative_to(ROOT).as_posix(),compress_type=zipfile.ZIP_STORED if p.suffix in {'.gz','.png'} else zipfile.ZIP_DEFLATED)
with zipfile.ZipFile(args.output) as z:
    for entry in entries:
        digest=hashlib.sha256();size=0
        with z.open(args.root_name+'/'+entry['path']) as stream:
            for b in iter(lambda:stream.read(1048576),b''):digest.update(b);size+=len(b)
        if digest.hexdigest()!=entry['sha256'] or size!=entry['bytes']:raise ValueError('Archive byte mismatch: '+entry['path'])
    if json.loads(z.read(args.root_name+'/MANIFEST.json'))['files']!=entries:raise ValueError('Manifest mismatch')
print(json.dumps({'status':'PASS','archive':str(args.output.resolve()),'bytes':args.output.stat().st_size,'sha256':sha256(args.output),'verified_project_files':len(entries),'native_power_bi':'NOT_VERIFIED'},indent=2))
