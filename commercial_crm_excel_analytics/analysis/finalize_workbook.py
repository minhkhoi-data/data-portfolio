"""Keep the authored native file; import only independently calculated caches.
Synchronize uniform calculated-column metadata to the authored row formulas.
"""
from pathlib import Path
from copy import deepcopy
import re,zipfile,json,warnings,os
from lxml import etree as E
import openpyxl
from openpyxl.formula.translate import Translator
warnings.filterwarnings('ignore',module='openpyxl')
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx'
CALC=Path(os.environ.get('OLIST_BUILD_DIR','/tmp/olist_flagship_20261014'))/'evaluated_final'/P.name
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
q=lambda x:'{'+ns['m']+'}'+x
with zipfile.ZipFile(P) as z:parts={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(CALC) as z:calc_parts={n:z.read(n) for n in z.namelist()}
cached=0
for name in list(parts):
 if re.fullmatch(r'xl/worksheets/sheet\d+.xml',name):
  root=E.fromstring(parts[name]);cal=E.fromstring(calc_parts[name]);cells={c.get('r'):c for c in cal.findall('.//m:c',ns)}
  for cell in root.findall('.//m:c',ns):
   if cell.find(q('f')) is None:continue
   evaluated=cells[cell.get('r')]
   for child in list(cell):
    if child.tag in [q('v'),q('is')]:cell.remove(child)
   t=evaluated.get('t');cell.attrib.pop('t',None)
   if t is not None:cell.set('t',t)
   for child in evaluated:
    if child.tag in [q('v'),q('is')]:cell.append(deepcopy(child))
   cached+=1
  parts[name]=E.tostring(root,encoding='utf-8',xml_declaration=True)
fw=openpyxl.load_workbook(P,data_only=False);synced=0
table_owner={t.name:(s,t) for s in fw for t in s.tables.values()}
for name in list(parts):
 if re.fullmatch(r'xl/tables/table\d+.xml',name):
  table=E.fromstring(parts[name]);sheet,definition=table_owner[table.get('name')]
  start=sheet[definition.ref.split(':')[0]];end=sheet[definition.ref.split(':')[1]].row
  for i,column in enumerate(table.find(q('tableColumns'))):
   anchor=sheet.cell(start.row+1,start.column+i)
   if anchor.data_type!='f':continue
   tr=Translator(anchor.value,origin=anchor.coordinate)
   if not all(sheet.cell(r,start.column+i).value==tr.translate_formula(sheet.cell(r,start.column+i).coordinate) for r in range(start.row+1,end+1)):continue
   old=column.find(q('calculatedColumnFormula'))
   if old is not None:column.remove(old)
   new=E.Element(q('calculatedColumnFormula'));new.text=anchor.value[1:];column.insert(0,new);synced+=1
  parts[name]=E.tostring(table,encoding='utf-8',xml_declaration=True)
def norm(s):return (s or '').replace("'",'').replace('$','').lstrip('=')
calc_refs={}
for name,content in calc_parts.items():
 if re.fullmatch(r'xl/(?:drawings/)?charts/chart\d+.xml',name):
  chart=E.fromstring(content)
  for ref in chart.xpath('.//c:numRef|.//c:strRef',namespaces=ns):
   formula=ref.find('c:f',ns)
   if formula is not None:calc_refs[norm(formula.text)]=ref
chart_caches=0
for name in list(parts):
 if re.fullmatch(r'xl/(?:drawings/)?charts/chart\d+.xml',name):
  chart=E.fromstring(parts[name])
  for ref in chart.xpath('.//c:numRef|.//c:strRef',namespaces=ns):
   formula=ref.find('c:f',ns);evaluated=calc_refs.get(norm(formula.text)) if formula is not None else None
   if evaluated is None:continue
   for child in list(ref):
    if E.QName(child).localname in ['numCache','strCache']:ref.remove(child)
   for child in evaluated:
    if E.QName(child).localname in ['numCache','strCache']:ref.append(deepcopy(child));chart_caches+=1
  parts[name]=E.tostring(chart,encoding='utf-8',xml_declaration=True)
temp=P.with_suffix('.final.xlsx')
with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,content in parts.items():z.writestr(name,content)
with zipfile.ZipFile(temp) as z:assert z.testzip() is None
temp.replace(P)
record={'status':'PASS','formula_caches_imported':cached,'uniform_table_columns_synchronized':synced,'chart_reference_caches_imported':chart_caches,'source_rows_removed':0,'Microsoft_Excel':'PENDING_USER'}
(ROOT/'audit/NATIVE_STRUCTURE.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
