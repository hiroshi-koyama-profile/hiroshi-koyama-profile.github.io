#!/usr/bin/env python3
"""Run a fixed atlas input and report numerical acceptance separately from exit."""
from pathlib import Path
import argparse
import csv
import hashlib
import importlib
import json
import math
import sys

CASES={
 'advection-sine':'waves','sod':'waves','shu-osher':'waves','brio-wu':'waves',
 'poisson-1d-dirichlet':'elliptic_basis','poisson-2d-sine':'elliptic_basis',
 'bratu':'elliptic_basis','smooth-function-projection':'elliptic_basis',
 'harmonic-oscillator':'dynamics_particles','stiff-cosine':'dynamics_particles',
 'periodic-particles':'dynamics_particles','taylor-green':'dynamics_particles',
}
MODES={'maximum','minimum','absolute_maximum','equals'}

def finite_number(value):
    return type(value) in (int,float) and math.isfinite(value)

def validate_input(document):
    if not isinstance(document,dict) or type(document.get('schema_version')) is not int or document['schema_version']!=1:
        raise ValueError('Expected input schema_version 1')
    if document.get('problem_id') not in CASES or not isinstance(document.get('parameters'),dict):
        raise ValueError('Unknown problem or missing parameters')
    checks=document.get('acceptance')
    if not isinstance(checks,list) or not checks:raise ValueError('Nonempty acceptance criteria are required')
    ids=[]
    for check in checks:
        if not isinstance(check,dict):raise ValueError('Acceptance criteria must be objects')
        if not all(isinstance(check.get(k),str) and check[k] for k in ['id','metric','comparison']):
            raise ValueError('Incomplete acceptance criterion')
        if check['comparison'] not in MODES:raise ValueError('Unsupported comparison')
        if check['comparison']=='equals':
            value=check.get('expected')
            if not (type(value) is bool or finite_number(value)):raise ValueError('Expected value must be a boolean or finite number')
        elif not finite_number(check.get('tolerance')) or check['tolerance']<0:
            raise ValueError('Tolerance must be finite and nonnegative')
        if not isinstance(check.get('description'),dict):raise ValueError('Criterion descriptions must be an object')
        if not all(isinstance(check.get('description',{}).get(lang),str) and check['description'][lang] for lang in ['ja','en']):
            raise ValueError('Criterion needs Japanese and English descriptions')
        ids.append(check['id'])
    if len(set(ids))!=len(ids):raise ValueError('Duplicate acceptance criterion')
    return document

def plain(value):
    if hasattr(value,'tolist'):return plain(value.tolist())
    if isinstance(value,dict):return {str(k):plain(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [plain(v) for v in value]
    if value is None or isinstance(value,(str,bool,int)):return value
    if isinstance(value,float) and math.isfinite(value):return value
    raise ValueError('Result contains a non-finite or unsupported value')

def evaluate(metrics,criteria):
    rows=[]
    for check in criteria:
        value=metrics.get(check['metric']);mode=check['comparison'];passed=False
        if mode=='equals':
            expected=check['expected'];passed=type(value) is type(expected) and value==expected
            if type(expected) in (int,float):passed=finite_number(value) and value==expected
        elif finite_number(value):
            threshold=check['tolerance']
            passed=(value>=threshold if mode=='minimum' else abs(value)<=threshold if mode=='absolute_maximum' else 0<=value<=threshold)
        rows.append({**check,'observed':value,'passed':bool(passed)})
    return rows

def calculate(document):
    validate_input(document)
    module=importlib.import_module('recipes.'+CASES[document['problem_id']])
    result=plain(module.run(document['problem_id'],document['parameters']))
    metrics=result['metrics'];table=result['table']
    if not isinstance(metrics,dict) or not metrics or not all(type(v)is bool or finite_number(v) for v in metrics.values()):
        raise ValueError('Metrics must be finite numbers or explicit boolean flags')
    if not isinstance(table,dict) or not table or not all(isinstance(k,str) and k for k in table):
        raise ValueError('A named numerical table is required')
    lengths=[]
    for column in table.values():
        if not isinstance(column,list) or not column or not all(finite_number(v) for v in column):
            raise ValueError('Table columns must contain finite numerical rows')
        lengths.append(len(column))
    if len(set(lengths))!=1:raise ValueError('Table columns have different lengths')
    decisions=evaluate(metrics,document['acceptance'])
    passed=all(row['passed'] for row in decisions)
    return {'schema_version':1,'problem_id':document['problem_id'],'parameters':document['parameters'],
            'status':'passed' if passed else 'failed','passed':passed,'metrics':metrics,
            'checks':{row['id']:row['passed'] for row in decisions},'acceptance':decisions,
            'table':{'file':'solution.csv','columns':list(table),'rows':lengths[0]},'details':result.get('details',{})},table

def write_json(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True,help='Fixed JSON input from recipes/')
    parser.add_argument('--output',type=Path,required=True,help='New empty output directory')
    args=parser.parse_args(argv)
    output=args.output.resolve();base=Path(__file__).resolve().parent
    protected=[base/name for name in ['recipes','numart','tests','docs','examples','reference']]
    if output==base or any(output==p or p in output.parents for p in protected) or output==args.input.resolve().parent:
        parser.error('Choose a separate output directory, outside packaged inputs/source/references')
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error('Output must be a new or empty directory; existing files are never overwritten')
    output.mkdir(parents=True,exist_ok=True)
    raw=b''
    try:
        raw=args.input.read_bytes();document=json.loads(raw)
        result,table=calculate(document)
        result['input_sha256']=hashlib.sha256(raw).hexdigest()
        with (output/'solution.csv').open('w',newline='') as handle:
            writer=csv.writer(handle);writer.writerow(table);writer.writerows(zip(*table.values()))
        write_json(output/'result.json',result)
        print(json.dumps({'problem_id':result['problem_id'],'status':result['status'],'checks':result['checks']}))
        return 0 if result['passed'] else 1
    except (ValueError,TypeError,KeyError,ArithmeticError,OSError,RuntimeError) as exc:
        write_json(output/'result.json',{'schema_version':1,'status':'error','passed':False,'input_sha256':hashlib.sha256(raw).hexdigest(),'error':str(exc)})
        print(str(exc),file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
