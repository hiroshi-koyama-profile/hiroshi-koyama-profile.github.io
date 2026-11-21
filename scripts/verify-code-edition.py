#!/usr/bin/env python3
"""Run the packaged numerical checks in an independent extraction."""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--edition',required=True)
args=parser.parse_args()
if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',args.edition):parser.error('Use YYYY-MM-DD')
base=ROOT/'code/numerical-methods-atlas'/args.edition
archive=base/('atlas-code-'+args.edition+'.zip')
manifest=json.loads((base/'source-manifest.json').read_text())
prefix='atlas-code-'+args.edition+'/'
with tempfile.TemporaryDirectory(prefix='atlas-edition-check-') as name:
    temporary=Path(name)
    with zipfile.ZipFile(archive) as z:
        allowed={prefix+p for p in manifest['files']}|{prefix+'source-manifest.json'}
        if set(z.namelist())!=allowed:raise ValueError('Archive differs from the file manifest')
        if sum(x.file_size for x in z.infolist())>50_000_000:raise ValueError('Review expanded archive size')
        for member in z.namelist():
            if '..' in Path(member).parts or member.startswith('/'):raise ValueError('Unsafe archive path')
        for relative,expected in manifest['files'].items():
            if hashlib.sha256(z.read(prefix+relative)).hexdigest()!=expected:raise ValueError('Archive hash differs: '+relative)
        z.extractall(temporary)
    result=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml='+str(temporary/'junit.xml')],cwd=temporary/prefix,text=True,capture_output=True,env={**os.environ,'MPLCONFIGDIR':str(temporary/'mpl-cache'),'PYTHONDONTWRITEBYTECODE':'1'})
    print(result.stdout[-600:])
    if not (temporary/'junit.xml').is_file():
        print(result.stderr,file=sys.stderr);raise SystemExit(result.returncode or 1)
    suite=ET.parse(temporary/'junit.xml').getroot().find('testsuite')
    skipped=[{'case':case.attrib['name'],'reason':case.find('skipped').attrib.get('message','')} for case in suite.findall('testcase') if case.find('skipped') is not None]
    counts={key:int(suite.attrib[key]) for key in ['tests','failures','errors','skipped']}
    examples=[]
    demo=temporary/prefix/'examples/barnes-hut/run.py'
    if demo.is_file() and result.returncode==0:
        demo_result=subprocess.run([sys.executable,str(demo),'--output',str(temporary/'demo')],cwd=temporary/prefix,text=True,capture_output=True)
        if demo_result.returncode:
            print(demo_result.stderr,file=sys.stderr);raise SystemExit(demo_result.returncode)
        output=json.loads((temporary/'demo/result.json').read_text())
        examples.append({'case':'barnes-hut','relative_rms_force_error':output['relative_rms_force_error'],'checks':output['checks'],'force_csv_rows':sum(1 for _ in (temporary/'demo/forces.csv').open())-1})
    report={'schema_version':1,'verified_on':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat(),'edition':args.edition,
            'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'execution':'Archive extracted to an independent temporary directory; tests used only packaged source and data.',
            'python':'.'.join(map(str,sys.version_info[:3])),**{p:importlib.metadata.version(p) for p in ['numpy','matplotlib','pytest']},
            'command':'python -m pytest -q',**counts,'passed':counts['tests']-counts['skipped']-counts['failures']-counts['errors'],'skipped_cases':skipped,'runnable_examples':examples,
            'scope':'Existing educational checks; not all source-paper figures or production use. Timing and floating-point behavior may differ across platforms.'}
    (base/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(counts))
    raise SystemExit(result.returncode)
