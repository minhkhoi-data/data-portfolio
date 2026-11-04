"""Check PBIR JSON against Microsoft schemas; no native report rendering."""
import argparse,hashlib,json,urllib.request,urllib.parse
from pathlib import Path
from jsonschema import validators
from referencing import Registry,Resource
from referencing.jsonschema import DRAFT7
from pipeline import ROOT,sha256

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);a=p.parse_args();a.cache.mkdir(parents=True,exist_ok=True)
schemas={}
def fetch(uri):
    uri=uri.split('#')[0]
    if urllib.parse.urlparse(uri).hostname!='developer.microsoft.com':raise ValueError('Unexpected schema provider: '+uri)
    cache=a.cache/(hashlib.sha256(uri.encode()).hexdigest()+'.json')
    if not cache.exists():
        with urllib.request.urlopen(uri,timeout=40) as r:cache.write_bytes(r.read())
    doc=json.loads(cache.read_bytes());schemas[uri]=sha256(cache)
    return doc
def retrieve(uri):return Resource.from_contents(fetch(uri),default_specification=DRAFT7)
registry=Registry(retrieve=retrieve)
results=[];errors=[]
for file in sorted((ROOT/'powerbi').rglob('*.json')):
    doc=json.loads(file.read_text());uri=doc.get('$schema')
    if not uri:continue
    schema=fetch(uri);validator=validators.validator_for(schema)(schema,registry=registry)
    found=sorted(validator.iter_errors(doc),key=lambda e:str(list(e.path)))
    for error in found:errors.append({'file':file.relative_to(ROOT).as_posix(),'path':list(error.path),'error':error.message})
    results.append({'file':file.relative_to(ROOT).as_posix(),'sha256':sha256(file),'schema':uri,'status':'FAIL' if found else 'PASS'})
result={'status':'FAIL' if errors else 'PASS','files':results,'schemas_sha256':schemas,'errors':errors,'scope':'JSON-schema validation of files with explicit Microsoft $schema URIs. Does not render visuals or execute semantic queries.'}
(ROOT/'audit/evidence/report_schema.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'validated_files':len(results),'schema_documents':len(schemas),'errors':errors},indent=2))
if errors:raise SystemExit(1)
