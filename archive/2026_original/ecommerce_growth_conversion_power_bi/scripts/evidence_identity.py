"""Reuse historical parser evidence only when its entire tested input is identical."""
import json
from pipeline import ROOT,sha256

def matches(name, evidence):
    if evidence.get('status')!='PASS':return False
    definition=ROOT/'powerbi/EcommerceGrowth.Model/definition'
    try:
        if name=='tmdl_parser.json':
            current={f.relative_to(definition).as_posix():sha256(f) for f in sorted(definition.rglob('*.tmdl'))}
            return current==evidence['current_model_sha256']
        if name=='m_syntax_parser.json':
            return len(evidence['tables'])==8 and all(sha256(definition/'tables'/f"{i['table']}.tmdl")==i['tmdl_sha256'] for i in evidence['tables']) and sha256(definition/'expressions.tmdl')==evidence['parameter_sha256']
        if name=='report_schema.json':
            return bool(evidence['files']) and all(sha256(ROOT/i['file'])==i['sha256'] for i in evidence['files'])
        if name=='opener_tests.json':
            return bool(evidence['file_sha256']) and all(sha256(ROOT/f)==h for f,h in evidence['file_sha256'].items())
    except (KeyError,OSError,TypeError):return False
    return False
