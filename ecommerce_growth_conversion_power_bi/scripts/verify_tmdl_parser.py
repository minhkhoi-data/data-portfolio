"""Validate metadata with Microsoft's TmdlSerializer, not a DAX/M/Desktop run.

Requires an external .NET 8 runtime, Microsoft TOM NuGet assemblies and
pythonnet. See audit/TMDL_PARSER.md. Does not download or send project data.
"""
import argparse,json,sys,tempfile,shutil
from pathlib import Path
from pipeline import ROOT,sha256

p=argparse.ArgumentParser();p.add_argument('--dotnet-root',type=Path,required=True);p.add_argument('--tom-lib',type=Path,required=True);p.add_argument('--pythonnet-site',type=Path);p.add_argument('--runtime-version',default='8.0.31');a=p.parse_args()
if a.pythonnet_site:sys.path.insert(0,str(a.pythonnet_site.resolve()))
from pythonnet import load
with tempfile.TemporaryDirectory(prefix='ga4_tmdl_') as temp:
 config=Path(temp)/'runtimeconfig.json';config.write_text(json.dumps({'runtimeOptions':{'tfm':'net8.0','framework':{'name':'Microsoft.NETCore.App','version':a.runtime_version}}}))
 load('coreclr',runtime_config=str(config),dotnet_root=str(a.dotnet_root.resolve()))
 import clr
 lib=a.tom_lib.resolve();sys.path.insert(0,str(lib))
 clr.AddReference(str(lib/'Microsoft.AnalysisServices.Core.dll'))
 assembly=clr.AddReference(str(lib/'Microsoft.AnalysisServices.Tabular.dll'))
 from Microsoft.AnalysisServices.Tabular import TmdlSerializer
 definition=ROOT/'powerbi/EcommerceGrowth.Model/definition'
 db=TmdlSerializer.DeserializeDatabaseFromFolder(str(definition))
 measure_count=sum(t.Measures.Count for t in db.Model.Tables)
 if db.Model.Tables.Count!=8 or db.Model.Relationships.Count!=8 or measure_count!=35:raise ValueError('Unexpected parsed model topology')
 if db.Model.Expressions.Count!=1 or next(iter(db.Model.Expressions)).Name!='DataFolder':raise ValueError('Expected one DataFolder M parameter')
 for table in db.Model.Tables:
  if table.Partitions.Count!=1 or str(next(iter(table.Partitions)).Source.GetType().Name)!='MPartitionSource':raise ValueError('Every table must use one M import partition')
 # Negative controls recreate the two actual screenshot failures independently.
 controls=[]
 for name in ['prior_dimdate_scope','prior_indented_model_refs']:
  stage=Path(temp)/name;shutil.copytree(definition,stage)
  if name=='prior_dimdate_scope':
   f=stage/'tables/DimDate.tmdl';text=f.read_text();key='\t\tisKey\n';text=text.replace(key,'',1)
   text=text.replace('\n\n\t\tannotation UnderlyingDateTimeDataType = Date','\n\t\tannotation UnderlyingDateTimeDataType = Date\n\t\tisKey',1);f.write_text(text)
  else:
   f=stage/'model.tmdl';lines=f.read_text().splitlines();f.write_text('\n'.join('\t'+x if x.startswith(('annotation ','ref table ')) else x for x in lines)+'\n')
  try:TmdlSerializer.DeserializeDatabaseFromFolder(str(stage))
  except Exception as error:
   message=str(error)
   expected=('UnknownKeyword',"'isKey'") if name=='prior_dimdate_scope' else ('InvalidLineType','ReferenceObject')
   if not all(token in message for token in expected):raise ValueError('Negative control failed for an unexpected reason: '+name) from error
   controls.append({'case':name,'status':'REJECTED_AS_EXPECTED','error':message})
  else:raise ValueError('Parser failed to reject negative control: '+name)
 result={'status':'PASS','validator':'Microsoft.AnalysisServices.Tabular.TmdlSerializer.DeserializeDatabaseFromFolder','assembly':str(assembly.FullName),'runtime':a.runtime_version,'table_count':int(db.Model.Tables.Count),'m_partition_count':8,'parameter_count':int(db.Model.Expressions.Count),'relationship_count':int(db.Model.Relationships.Count),'measure_count':int(measure_count),'compatibility_level':int(db.CompatibilityLevel),'current_model_sha256':{f.relative_to(definition).as_posix():sha256(f) for f in sorted(definition.rglob('*.tmdl'))},'negative_controls':controls,'scope':'Metadata deserialization only. Does NOT compile/evaluate DAX, execute M/refresh, render PBIR or run Power BI Desktop.','native_desktop':'NOT_VERIFIED'}
 (ROOT/'audit/evidence/tmdl_parser.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({k:v for k,v in result.items() if k not in ['current_model_sha256','negative_controls']},indent=2));print('Both previously observed malformed definitions rejected by official parser')
