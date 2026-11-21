"""Recipe contracts: reject ambiguous inputs, false success and unsafe overwrite."""
from pathlib import Path
import copy
import importlib.util
import json
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('recipe_cli',ROOT/'run_recipe.py')
cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)

def sample():
    return {'schema_version':1,'problem_id':'advection-sine','parameters':{},'acceptance':[{'id':'error','metric':'error','comparison':'maximum','tolerance':.1,'description':{'ja':'誤差','en':'Error'}}]}

@pytest.mark.parametrize('kind',['version','unknown','missing','duplicate','nan','boolean','negative','malformed','null-description','array-description','number-description'])
def test_invalid_recipe_specifications_are_rejected(kind):
    data=sample()
    if kind=='version':data['schema_version']=True
    elif kind=='unknown':data['problem_id']='nonexistent'
    elif kind=='missing':data['acceptance']=[]
    elif kind=='duplicate':data['acceptance']*=2
    elif kind=='nan':data['acceptance'][0]['tolerance']=float('nan')
    elif kind=='boolean':data['acceptance'][0]['tolerance']=True
    elif kind=='negative':data['acceptance'][0]['tolerance']=-1
    elif kind=='malformed':data['acceptance']=[None]
    elif kind=='null-description':data['acceptance'][0]['description']=None
    elif kind=='array-description':data['acceptance'][0]['description']=[]
    elif kind=='number-description':data['acceptance'][0]['description']=1
    with pytest.raises(ValueError):cli.validate_input(data)

@pytest.mark.parametrize('observed',[None,True,float('nan'),float('inf'),-1.,.11])
def test_error_metric_cannot_report_false_success(observed):
    assert cli.evaluate({'error':observed},sample()['acceptance'])[0]['passed'] is False

def test_order_minimum_and_explicit_boolean_flags_have_distinct_meaning():
    checks=[{'id':'order','metric':'order','comparison':'minimum','tolerance':1.8},
            {'id':'converged','metric':'converged','comparison':'equals','expected':True}]
    assert all(x['passed'] for x in cli.evaluate({'order':1.99,'converged':True},checks))
    assert not any(x['passed'] for x in cli.evaluate({'order':1.2,'converged':1},checks))

def test_every_published_input_has_nonempty_scientific_acceptance():
    inputs=list((ROOT/'recipes').glob('*.json'))
    assert {p.stem for p in inputs}==set(cli.CASES)
    for path in inputs:
        doc=cli.validate_input(json.loads(path.read_text()))
        assert doc['problem_id']==path.stem
        assert len(doc['parameters'])>=3
        assert len(doc['acceptance'])>=3

def test_nonempty_output_is_preserved_without_execution(tmp_path):
    output=tmp_path/'output';output.mkdir();file=output/'do-not-change.txt';file.write_text('keep')
    process=subprocess.run([sys.executable,str(ROOT/'run_recipe.py'),'--input',str(ROOT/'recipes/harmonic-oscillator.json'),'--output',str(output)],capture_output=True,text=True)
    assert process.returncode==2 and file.read_text()=='keep'
    assert not (output/'result.json').exists()

def test_recipe_cli_reports_input_failure_as_error_not_pass(tmp_path):
    source=tmp_path/'bad.json';source.write_text('{}')
    process=subprocess.run([sys.executable,str(ROOT/'run_recipe.py'),'--input',str(source),'--output',str(tmp_path/'out')],capture_output=True,text=True)
    result=json.loads((tmp_path/'out/result.json').read_text())
    assert process.returncode==2 and result['status']=='error' and result['passed'] is False
    assert not (tmp_path/'out/solution.csv').exists()
