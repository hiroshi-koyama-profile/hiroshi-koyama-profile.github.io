"""Discovery links for existing verified examples, separate from execution receipts."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://hrkoyama.github.io'
ENTRY_BASE='/numerical-methods-atlas/code-and-data/examples/'
REGISTRY_URL=ORIGIN+'/numerical-methods-atlas/code-and-data/examples.json'
SOURCE='catalog/atlas-execution-discovery.json'


def entry_path(ident):
    if not isinstance(ident,str) or not re.fullmatch('[a-z0-9-]+',ident):raise ValueError('Invalid execution-example ID')
    return ENTRY_BASE+ident+'/'


def entry_url(ident,lang=None):
    if lang is not None and lang not in ['ja','en']:raise ValueError('Unsupported language')
    return ORIGIN+entry_path(ident)+('?lang='+lang if lang else '')


def bilingual(value,where):
    if not isinstance(value,dict) or any(not isinstance(value.get(lang),str) or not value[lang].strip() for lang in ['ja','en']):
        raise ValueError(where+': both languages are required')


def load_discovery(root=ROOT):
    root=Path(root);source=root/SOURCE
    data=json.loads(source.read_text())
    if data.get('schema_version')!=1 or data.get('registry')!=REGISTRY_URL:raise ValueError('Unsupported discovery catalog')
    bilingual(data['scope'],'scope')
    records=json.loads((root/'catalog/atlas-execution-examples.json').read_text())['examples']
    public_bytes=(root/'numerical-methods-atlas/code-and-data/examples.json').read_bytes()
    public=json.loads(public_bytes)
    if public['examples']!=records:raise ValueError('Refresh the execution registry before discovery pages')
    by_id={x['id']:x for x in records};items=data['examples']
    ids=[x['id'] for x in items]
    if len(ids)!=len(set(ids)) or set(ids)!=set(by_id):raise ValueError('Discovery must cover every verified example once')
    equations={x['id']:x for x in json.loads((root/'catalog/atlas-equations.json').read_text())['equations']}
    for x in items:
        record=by_id[x['id']]
        if x['problem_id']!=record['problem_id']:raise ValueError('Problem/example mismatch')
        bilingual(x['outcome'],x['id']+'.outcome')
        if not isinstance(x['keywords'],list) or not x['keywords'] or any(not isinstance(k,str) or not k.strip() for k in x['keywords']):raise ValueError('Missing discovery keywords')
        model_ids=x['equation_ids']
        if not isinstance(model_ids,list) or len(set(model_ids))!=len(model_ids):raise ValueError('Invalid model mapping')
        for ident in model_ids:
            if ident not in equations or equations[ident]['status']!='local-example':raise ValueError('Discovery cannot promote an unimplemented model')
        formula=x['formula']
        if formula['role'] not in ['problem','approximation','diagnostic']:raise ValueError('Distinguish problem and numerical definition')
        if not isinstance(formula['latex'],list) or not formula['latex'] or any(not isinstance(f,str) or not f.strip() for f in formula['latex']):raise ValueError('A scoped formula is required')
        bilingual(formula['note'],x['id']+'.formula.note')
    return {**data,'registry_sha256':hashlib.sha256(public_bytes).hexdigest(),
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'examples':[{**x,'execution':by_id[x['id']]} for x in items]}


def public_discovery(data):
    return {k:v for k,v in data.items() if k!='examples'}|{'examples':[
        {**{k:v for k,v in x.items() if k!='execution'},'name':x['execution']['name'],
         'url':entry_url(x['id']),'entry':{lang:entry_url(x['id'],lang) for lang in ['ja','en']},
         'registry_url':REGISTRY_URL,'input':x['execution']['inputs']['url'],
         'method_ids':x['execution']['method_ids'],'reference_type':x['execution'].get('reference_type')}
        for x in data['examples']]}
