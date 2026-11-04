"""Repair only orphan xfComplement metadata using an authored base format.
Usage: python analysis/apply_styles_fragment.py --fragment base-style-fragment.xlsx
Preserves every non-style ZIP part, every cell/style index, font/fill/border and
ordinary number/alignment format. Raw Boolean values remain unchanged.
"""
import argparse,copy,hashlib,json,zipfile
from pathlib import Path
from lxml import etree as E
ROOT=Path(__file__).resolve().parents[1]
M='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
F='http://schemas.microsoft.com/office/spreadsheetml/2022/featurepropertybag'
NS={'m':M,'f':F}
def load(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return {n:z.read(n) for n in z.namelist()}
def apply(fragment,workbook):
    old_hash=hashlib.sha256(workbook.read_bytes()).hexdigest()
    parts=load(workbook);before=dict(parts);authored=load(fragment)
    sheet=E.fromstring(parts['xl/styles.xml']);original=copy.deepcopy(sheet)
    formats=sheet.find('m:cellXfs',NS)
    neutral=E.fromstring(authored['xl/styles.xml']).find('m:cellXfs/m:xf',NS)
    assert neutral is not None and len(neutral)==0
    assert not any('featurepropertybag' in n.lower() for n in parts), 'Feature bag exists; do not flatten a supported checkbox feature.'
    corrected=[];referenced=0
    for index,xf in enumerate(list(formats)):
        if not xf.xpath('.//f:xfComplement',namespaces=NS):continue
        stripped=copy.deepcopy(xf)
        for ext in list(stripped.findall('m:extLst',NS)):stripped.remove(ext)
        assert dict(stripped.attrib)==dict(neutral.attrib) and len(stripped)==0, 'Non-neutral extended style requires a dedicated mapping.'
        formats.replace(xf,copy.deepcopy(neutral));corrected.append(index)
    for name,data in parts.items():
        if name.startswith('xl/worksheets/') and name.endswith('.xml'):
            root=E.fromstring(data)
            for cell in root.findall('.//m:c',NS):
                if int(cell.get('s','0')) in corrected:
                    assert cell.get('t')=='b', (name,cell.get('r'),'Unexpected non-Boolean style user')
                    referenced+=1
    assert corrected,'No orphan style found; abort redundant repair.'
    # Only the known missing extension is removed. Keep all ordinary style
    # records and IDs in their existing positions, including unused records.
    check=copy.deepcopy(original)
    for index in corrected:
        xf=check.find('m:cellXfs',NS)[index]
        for ext in list(xf.findall('m:extLst',NS)):xf.remove(ext)
    def semantic(node):return (node.tag,tuple(sorted(node.attrib.items())),node.text or '',tuple(semantic(c) for c in node))
    assert semantic(check)==semantic(sheet)
    parts['xl/styles.xml']=E.tostring(sheet,encoding='utf-8',xml_declaration=True)
    assert [n for n in parts if parts[n]!=before[n]]==['xl/styles.xml']
    temp=workbook.with_suffix('.style-tmp.xlsx')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)
    with zipfile.ZipFile(temp) as z:assert z.testzip() is None
    temp.replace(workbook)
    report={'status':'PASS','input_workbook_sha256':old_hash,'final_workbook_sha256':hashlib.sha256(workbook.read_bytes()).hexdigest(),'only_changed_part':'xl/styles.xml','replaced_style_indexes':corrected,'boolean_cells_unchanged':referenced,'all_non_style_parts_byte_identical':True,'all_ordinary_style_properties_preserved':True,'source':'Microsoft MS-XLSX 2.4.99 xfComplement requires a Feature Property Bag part; none existed.','spec_url':'https://learn.microsoft.com/en-us/openspecs/office_standards/ms-xlsx/d6ffbc21-ef11-4546-9a07-95885e2fd497','native_Microsoft_Excel':'PENDING_RETEST'}
    (ROOT/'audit/STYLE_REPAIR.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--fragment',required=True);args=p.parse_args()
    apply(Path(args.fragment),ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx')
