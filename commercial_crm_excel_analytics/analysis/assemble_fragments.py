"""Assemble Artifact Tool-authored fragments without dropping source rows.
Remap styles/shared strings, expand valid shared formulas, and bind source ranges.
"""
from pathlib import Path
from copy import deepcopy,copy
from lxml import etree as E
import json,re,zipfile,os
from openpyxl.formula.translate import Translator
ROOT=Path(__file__).resolve().parents[1];TMP=Path(os.environ.get('OLIST_BUILD_DIR','/tmp/olist_flagship_20261014'))
P=ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx'
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};q=lambda x:'{'+ns['m']+'}'+x
with zipfile.ZipFile(P) as z:parts={n:z.read(n) for n in z.namelist()}
styles=E.fromstring(parts['xl/styles.xml']);strings=E.fromstring(parts['xl/sharedStrings.xml'])
def canonical(x):return E.tostring(x,method='c14n')
string_index={canonical(x):i for i,x in enumerate(strings)}
def append_unique(parent,element,index):
 key=canonical(element)
 if key not in index:index[key]=len(parent);parent.append(deepcopy(element))
 return index[key]
for name in ['fonts','fills','borders','cellStyleXfs','cellXfs','dxfs']:
 if styles.find(q(name)) is None:E.SubElement(styles,q(name),count='0')
indexes={name:{canonical(x):i for i,x in enumerate(styles.find(q(name)))} for name in ['fonts','fills','borders','cellStyleXfs','cellXfs','dxfs']}
nf=styles.find(q('numFmts'))
if nf is None:nf=E.Element(q('numFmts'),count='0');styles.insert(0,nf)
formats={x.get('formatCode'):int(x.get('numFmtId')) for x in nf}
next_format=max([163,*formats.values()])+1
def style_map(root):
 global next_format
 mappings={}
 numbers={}
 for x in root.find(q('numFmts')) or []:
  code=x.get('formatCode')
  if code not in formats:
   formats[code]=next_format;nf.append(E.Element(q('numFmt'),numFmtId=str(next_format),formatCode=code));next_format+=1
  numbers[int(x.get('numFmtId'))]=formats[code]
 for name in ['fonts','fills','borders','dxfs']:
  mappings[name]={i:append_unique(styles.find(q(name)),x,indexes[name]) for i,x in enumerate(root.find(q(name)) or [])}
 for name in ['cellStyleXfs','cellXfs']:
  m={}
  for i,old in enumerate(root.find(q(name))):
   x=deepcopy(old)
   for att,n in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:
    if att in x.attrib:x.set(att,str(mappings[n][int(x.get(att))]))
   if 'numFmtId' in x.attrib:x.set('numFmtId',str(numbers.get(int(x.get('numFmtId')),int(x.get('numFmtId')))))
   if 'xfId' in x.attrib:x.set('xfId',str(mappings.get('cellStyleXfs',{}).get(int(x.get('xfId')),int(x.get('xfId')))))
   m[i]=append_unique(styles.find(q(name)),x,indexes[name])
  mappings[name]=m
 return mappings['cellXfs']
dimensions={'Leads':(8,8001,'AA'),'Sales_Items':(9,5045,'O')}
for name,(sheet_no,last,letter) in dimensions.items():
 main=E.fromstring(parts[f'xl/worksheets/sheet{sheet_no}.xml']);data=main.find(q('sheetData'))
 for row in list(data):
  if int(row.get('r'))>1:data.remove(row)
 seen=set()
 for file in sorted((TMP/'fragments').glob(name+'_*.xlsx')):
  with zipfile.ZipFile(file) as z:
   smap=style_map(E.fromstring(z.read('xl/styles.xml')))
   local_strings=E.fromstring(z.read('xl/sharedStrings.xml'))
   string_map={i:append_unique(strings,x,string_index) for i,x in enumerate(local_strings)}
   sheet=E.fromstring(z.read('xl/worksheets/sheet1.xml'))
   masters={}
   for c in sheet.findall('.//m:c',ns):
    f=c.find(q('f'))
    if f is not None and f.get('t')=='shared' and f.get('ref'):masters[f.get('si')]=(c.get('r'),f.text)
   for row in sheet.find(q('sheetData')):
    index=int(row.get('r'))
    if index<2 or not len(row):continue
    assert index not in seen,(name,index);seen.add(index)
    row=deepcopy(row)
    for c in row:
     c.set('s',str(smap[int(c.get('s','0'))]))
     if c.get('t')=='s':c.find(q('v')).text=str(string_map[int(c.find(q('v')).text)])
     f=c.find(q('f'))
     if f is not None and f.get('t')=='shared':
      anchor,text=masters[f.get('si')]
      f.text=Translator('='+text,origin=anchor).translate_formula(c.get('r'))[1:];f.attrib.clear()
    data.append(row)
 assert seen==set(range(2,last+1)),(name,len(seen),last-1)
 dim=main.find(q('dimension'))
 if dim is not None:dim.set('ref',f'A1:{letter}{last}')
 parts[f'xl/worksheets/sheet{sheet_no}.xml']=E.tostring(main,encoding='utf-8',xml_declaration=True)
 # Locate the table through the worksheet relationship, not a guessed table index.
 rel=E.fromstring(parts[f'xl/worksheets/_rels/sheet{sheet_no}.xml.rels'])
 targets=[x.get('Target') for x in rel if x.get('Type','').endswith('/table')]
 assert len(targets)==1
 target='xl/'+targets[0].replace('../','').lstrip('/') if not targets[0].startswith('/xl/') else targets[0].lstrip('/')
 table=E.fromstring(parts[target]);table.set('ref',f'A1:{letter}{last}')
 af=table.find(q('autoFilter'))
 if af is not None:af.set('ref',f'A1:{letter}{last}')
 parts[target]=E.tostring(table,encoding='utf-8',xml_declaration=True)
# The small authoring skeleton used one-row source bounds solely to cap engine memory.
# Bind only explicitly named source-range tokens to the verified full population.
for name,content in list(parts.items()):
 if name.endswith('.xml') and (name.startswith('xl/worksheets/') or name.startswith('xl/tables/')):
  root=E.fromstring(content)
  for f in root.iter():
   if E.QName(f).localname in ['f','calculatedColumnFormula'] and f.text:
    f.text=re.sub(r'(Leads!\$([A-Z]+)\$2:\$\2\$)2\b',lambda m:m.group(1)+'8001',f.text)
    f.text=re.sub(r'(Sales_Items!\$([A-Z]+)\$2:\$\2\$)2\b',lambda m:m.group(1)+'5045',f.text)
  for c in root.findall('.//m:c',ns):
   if c.find(q('f')) is not None:
    for child in list(c):
     if child.tag in [q('v'),q('is')]:c.remove(child)
    c.attrib.pop('t',None)
  parts[name]=E.tostring(root,encoding='utf-8',xml_declaration=True)
for element in styles:
 if element.tag in [q(x) for x in ['numFmts','fonts','fills','borders','cellStyleXfs','cellXfs','dxfs']]:element.set('count',str(len(element)))
strings.set('uniqueCount',str(len(strings)));strings.set('count',str(sum(len(E.fromstring(v).xpath('.//m:c[@t="s"]',namespaces=ns)) for k,v in parts.items() if re.fullmatch(r'xl/worksheets/sheet\d+.xml',k))))
parts['xl/styles.xml']=E.tostring(styles,encoding='utf-8',xml_declaration=True);parts['xl/sharedStrings.xml']=E.tostring(strings,encoding='utf-8',xml_declaration=True)
workbook=E.fromstring(parts['xl/workbook.xml']);cp=workbook.find(q('calcPr'))
if cp is None:cp=E.SubElement(workbook,q('calcPr'))
cp.attrib.update({'calcMode':'auto','fullCalcOnLoad':'1','forceFullCalc':'1'});parts['xl/workbook.xml']=E.tostring(workbook,encoding='utf-8',xml_declaration=True)
temp=P.with_suffix('.assembled.xlsx')
with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,content in parts.items():z.writestr(name,content)
with zipfile.ZipFile(temp) as z:assert z.testzip() is None
temp.replace(P)
print('ASSEMBLED full source rows; source ranges bound; styles/shared strings remapped.')
