"""Transfer Artifact Tool-authored layout properties, preserving the workbook.

Usage: python analysis/apply_layout_fragment.py --fragment layout.xlsx
No alternative workbook authoring library is used. Source cells, formulas,
styles, native chart definitions and table metadata remain unchanged.
"""
import argparse,copy,hashlib,json,re,zipfile
from pathlib import Path
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
M='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
D='http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
for prefix,uri in [('m',M),('xdr',D),('r',R)]:E.register_namespace(prefix,uri)

def parts(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {n:z.read(n) for n in z.namelist()}

def sheet_parts(package):
    book=E.fromstring(package['xl/workbook.xml'])
    rels=E.fromstring(package['xl/_rels/workbook.xml.rels'])
    lookup={r.get('Id'):r.get('Target') for r in rels}
    return {s.get('name'):('xl/'+lookup[s.get('{'+R+'}id')].lstrip('/').removeprefix('xl/'))
            for s in book.find('{'+M+'}sheets')}

def apply(fragment,workbook):
    before_hash=hashlib.sha256(workbook.read_bytes()).hexdigest()
    p=parts(workbook);before=dict(p);g=parts(fragment)
    target_names=sheet_parts(p);source_names=sheet_parts(g)
    drawing='xl/drawings/drawing1.xml'
    a=E.fromstring(p[drawing]);b=E.fromstring(g[drawing])
    target=a.findall('{'+D+'}twoCellAnchor');source=b.findall('{'+D+'}twoCellAnchor')
    assert len(target)==len(source)==4
    for old,new in zip(target,source):
        for tag in ['from','to']:
            old.remove(old.find('{'+D+'}'+tag))
            old.insert(0 if tag=='from' else 1,copy.deepcopy(new.find('{'+D+'}'+tag)))
    p[drawing]=E.tostring(a,encoding='utf-8',xml_declaration=True)
    for name in ['Seller_Value','Leads','Sales_Items']:
        key=target_names[name];x=E.fromstring(p[key]);y=E.fromstring(g[source_names[name]])
        cols=x.find('{'+M+'}cols');assert cols is not None
        for new in y.findall('{'+M+'}cols/{'+M+'}col'):
            lo,hi=int(new.get('min')),int(new.get('max'))
            for col in cols:
                # Existing release has one descriptor per column. Do not
                # silently split or broaden a differently structured file.
                if int(col.get('min'))>=lo and int(col.get('max'))<=hi:
                    col.set('width',new.get('width'));col.set('customWidth','1')
        oldrow=x.find('.//{'+M+'}row[@r="1"]');newrow=y.find('.//{'+M+'}row[@r="1"]')
        assert oldrow is not None and newrow is not None
        for attr in ['ht','customHeight']:
            if newrow.get(attr) is not None:oldrow.set(attr,newrow.get(attr))
        p[key]=E.tostring(x,encoding='utf-8',xml_declaration=True)
    changed=[n for n in p if p[n]!=before[n]]
    assert set(changed)<={drawing,*[target_names[n] for n in ['Seller_Value','Leads','Sales_Items']]}
    # Independent preservation checks across every original cell and chart.
    for n in changed:
        x=E.fromstring(before[n]);y=E.fromstring(p[n])
        if n==drawing:
            for root in [x,y]:
                for anchor in root.findall('{'+D+'}twoCellAnchor'):
                    for tag in ['from','to']:anchor.remove(anchor.find('{'+D+'}'+tag))
        else:
            for root in [x,y]:
                root.remove(root.find('{'+M+'}cols'))
                row=root.find('.//{'+M+'}row[@r="1"]')
                for attr in ['ht','customHeight']:row.attrib.pop(attr,None)
        assert E.tostring(x)==E.tostring(y),(n,'Unintended cell/style/object change')
    temp=workbook.with_suffix('.layout-tmp.xlsx')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for n,data in p.items():z.writestr(n,data)
    with zipfile.ZipFile(temp) as z:assert z.testzip() is None
    temp.replace(workbook)
    record={'status':'PASS','before_sha256':before_hash,
            'workbook_sha256':hashlib.sha256(workbook.read_bytes()).hexdigest(),
            'changed_parts':changed,'all_cell_values_formulas_styles_preserved':True,
            'all_chart_definitions_and_series_preserved':True,'all_tables_preserved':True,
            'Microsoft_Excel':'PENDING_USER'}
    (ROOT/'audit/LAYOUT_REPAIR.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fragment',required=True);args=p.parse_args()
    apply(Path(args.fragment),ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx')
