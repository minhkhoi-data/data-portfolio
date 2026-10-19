"""Independently recalculate four disposable copies with native typed controls.
Usage: python audit/validate_controls.py --fragment layout_fragment.xlsx --workdir TEMP
The fragment is authored by analysis/repair_layout.mjs, not by this utility.
"""
import argparse,copy,hashlib,json,shutil,subprocess,zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from lxml import etree as E
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
M='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
def load_parts(path):
    with zipfile.ZipFile(path) as z:return {n:z.read(n) for n in z.namelist()}
def sheets(p):
    rels={x.get('Id'):x.get('Target') for x in E.fromstring(p['xl/_rels/workbook.xml.rels'])}
    return {s.get('name'):'xl/'+rels[s.get('{'+R+'}id')].lstrip('/').removeprefix('xl/') for s in E.fromstring(p['xl/workbook.xml']).find('{'+M+'}sheets')}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fragment',required=True);parser.add_argument('--workdir',required=True);args=parser.parse_args()
    wd=Path(args.workdir).resolve();wd.mkdir(parents=True,exist_ok=True)
    book=ROOT/'Olist_CRM_Acquisition_Seller_Value.xlsx';base=load_parts(book);frag=load_parts(args.fragment)
    base_names=sheets(base);frag_names=sheets(frag)
    cases=['Slow14','InvalidSlow','Support1','InvalidSupport'];inputs={}
    for name in cases:
        target=E.fromstring(base[base_names['Lookups']]);source=E.fromstring(frag[frag_names[name]])
        for cell in ['B2','B3']:
            old=target.find('.//{'+M+'}c[@r="'+cell+'"]');new=copy.deepcopy(source.find('.//{'+M+'}c[@r="'+cell+'"]'))
            assert old is not None and new is not None
            if old.get('s') is not None:new.set('s',old.get('s'))
            parent=old.getparent();parent.replace(old,new)
        changed=base.copy();changed[base_names['Lookups']]=E.tostring(target,encoding='utf-8',xml_declaration=True)
        # Offline XML input changes are not Calc UI edits. Clear saved
        # formula caches to force independent full evaluation on import.
        for path,data in list(changed.items()):
            if path.startswith('xl/worksheets/') and path.endswith('.xml'):
                xml=E.fromstring(data)
                for cell in xml.findall('.//{'+M+'}c'):
                    if cell.find('{'+M+'}f') is not None:
                        for child in list(cell):
                            if child.tag in ['{'+M+'}v','{'+M+'}is']:cell.remove(child)
                        cell.attrib.pop('t',None)
                changed[path]=E.tostring(xml,encoding='utf-8',xml_declaration=True)
        candidate=wd/(name+'.xlsx')
        with zipfile.ZipFile(candidate,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for path,data in changed.items():z.writestr(path,data)
        inputs[name]=candidate
    def evaluate(name):
        out=wd/('calc_'+name);out.mkdir(exist_ok=True)
        result=subprocess.run([shutil.which('soffice'),'-env:UserInstallation='+(wd/('profile_'+name)).as_uri(),'--headless','--convert-to','xlsx','--outdir',str(out),str(inputs[name])],capture_output=True,text=True,timeout=60)
        expected=out/(name+'.xlsx')
        if result.returncode!=0 or not expected.exists():raise RuntimeError(name+': Calc failed '+result.stderr)
        return name,openpyxl.load_workbook(expected,data_only=True),{'exit_code':result.returncode,'output':result.stdout.strip()}
    with ThreadPoolExecutor(max_workers=2) as pool:results=dict((name,(w,log)) for name,w,log in pool.map(evaluate,cases))
    checks=[]
    def check(label,condition,detail=None):checks.append({'check':label,'status':'PASS' if condition else 'FAIL','detail':detail})
    w=results['Slow14'][0]
    check('slow14_KPI',w['Dashboard']['M6'].value==414,w['Dashboard']['M6'].value)
    check('slow14_live_action',w['Action_List']['C6'].value=='414 observed wins exceed 14 days',w['Action_List']['C6'].value)
    for cell,expected in [('A6',8000),('C6',842),('K6',664858)]:check('slow14_unchanged_'+cell,w['Dashboard'][cell].value==expected)
    w=results['InvalidSlow'][0]
    check('invalid_slow_exposed',w['Lookups']['B5'].value=='INVALID' and w['Dashboard']['M6'].value=='#N/A' and w['Action_List']['C6'].value=='#N/A')
    check('invalid_slow_source_facts_retained',w['Dashboard']['A6'].value==8000 and w['Dashboard']['C6'].value==842 and w['Dashboard']['K6'].value==664858)
    w=results['Support1'][0]
    check('support1_all_channel_flags',all(w['Channel_Performance'].cell(r,13).value=='Meets review threshold' for r in range(2,13)))
    check('support1_all_SR_flags',all(w['Rep_Performance'].cell(r,10).value=='Meets review threshold' for r in range(2,24)))
    w=results['InvalidSupport'][0]
    check('invalid_support_exposed',w['Lookups']['B6'].value=='INVALID' and all(w['Channel_Performance'].cell(r,13).value=='#N/A' for r in range(2,13)))
    check('invalid_support_does_not_fabricate_new_KPIs',all(w['Dashboard'][c].value==v for c,v in [('A6',8000),('C6',842),('K6',664858),('M6',287)]))
    report={'status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','checks':len(checks),'passed':sum(c['status']=='PASS' for c in checks),'engine':'LibreOffice Calc; four freshly recalculated disposable copies','method':'All formula caches cleared before independent full import evaluation. This is not a UI-interaction test in Calc or Microsoft Excel.','workbook_sha256':hashlib.sha256(book.read_bytes()).hexdigest(),'Microsoft_Excel':'PENDING_USER','results':checks,'logs':{n:v[1] for n,v in results.items()}}
    (ROOT/'audit/SCENARIO_VALIDATION.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k not in ['logs','results']},indent=2))
    raise SystemExit(report['status']!='PASS')
if __name__=='__main__':main()
