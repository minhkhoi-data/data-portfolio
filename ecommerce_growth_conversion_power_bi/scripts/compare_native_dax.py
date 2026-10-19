"""Compare a Desktop DAX-query CSV export with the prepared expectation matrix.

Run after refreshing this exact release, using unformatted numeric CSV values.
A passing fixture/self-test is not native DAX evidence.
"""
import argparse,csv,hashlib,json
from decimal import Decimal,InvalidOperation
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        headers=reader.fieldnames or []
        normalized=[h[1:-1] if h.startswith('[') and h.endswith(']') else h for h in headers]
        if len(normalized)!=len(set(normalized)):raise ValueError('Duplicate CSV headers')
        rows=[]
        for row in reader:
            if None in row or any(v is None for v in row.values()):raise ValueError('Malformed CSV row')
            rows.append(dict(zip(normalized,[row[h] for h in headers])))
    if 'Context' not in normalized:raise ValueError('CSV must contain Context or [Context] header')
    if len({r['Context'] for r in rows})!=len(rows):raise ValueError('Duplicate contexts')
    return normalized,{r['Context']:r for r in rows}

def compare(expected,actual):
    eh,er=load(expected);ah,ar=load(actual);errors=[]
    if set(eh)!=set(ah):return [{'error':'CSV columns differ','missing':sorted(set(eh)-set(ah)),'extra':sorted(set(ah)-set(eh))}]
    if set(er)!=set(ar):return [{'error':'Context population differs','missing':sorted(set(er)-set(ar)),'extra':sorted(set(ar)-set(er))}]
    for context,row in er.items():
        for name in eh:
            if name=='Context':continue
            e,a=row[name],ar[context][name]
            if e=='' or a=='':ok=e==a
            else:
                try:
                    en,an=Decimal(e),Decimal(a)
                    ok=en.is_finite() and an.is_finite() and abs(en-an)<=Decimal('0.000001')
                except InvalidOperation:ok=e==a
            if not ok:errors.append({'context':context,'measure':name,'expected':e,'actual':a})
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--actual',required=True,type=Path)
    args=parser.parse_args();expected=ROOT/'audit/native_contract/expected.csv'
    contract=json.loads((ROOT/'audit/native_contract/contract.json').read_text())
    for name,digest in contract['data_sha256'].items():
        if hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest()!=digest:raise ValueError('Current data differ from the native contract: '+name)
    errors=compare(expected,args.actual)
    result={'status':'PASS' if not errors else 'FAIL','scope':'Comparison of a user-supplied export; native execution provenance and visual interactions require separate confirmation','contexts':contract['contexts'],'measures':contract['measures'],'blank_is_distinct_from_zero':True,'actual_sha256':hashlib.sha256(args.actual.read_bytes()).hexdigest(),'expected_sha256':hashlib.sha256(expected.read_bytes()).hexdigest(),'mismatches':errors}
    (ROOT/'audit/evidence/native_dax_comparison.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'status':result['status'],'contexts':result['contexts'],'measures':result['measures'],'mismatches':len(errors)},indent=2))
    return 0 if not errors else 1

if __name__=='__main__':raise SystemExit(main())
