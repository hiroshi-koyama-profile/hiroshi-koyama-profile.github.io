#!/usr/bin/env python3
"""Package a new immutable quantum-atom edition and verify an independent extraction."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.metadata,json,os,re,subprocess,sys,tempfile,zipfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--edition',default='2026-11-21');a=p.parse_args()
assert re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:-r\d+)?',a.edition)
base=ROOT/'code/quantum-atoms'/a.edition;archive=base/('quantum-atoms-'+a.edition+'.zip')
if subprocess.run(['git','ls-files','--error-unmatch',archive.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True).returncode==0:
    raise SystemExit('Published edition: prepare a new dated/revision directory instead of overwriting it.')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
files={}
for path in sorted(base.rglob('*')):
    rel=path.relative_to(base)
    if not path.is_file() or any(s.startswith('.') or s=='__pycache__' for s in rel.parts):continue
    if path.name in ['source-manifest.json','verification.json',archive.name]:continue
    if path.suffix not in ['.py','.json','.csv','.md','.txt','.png'] and path.name!='LICENSE':raise ValueError(rel)
    files[rel.as_posix()]=sha(path)
manifest={'schema_version':1,'edition':a.edition,'family':'quantum-atoms','public_base_url':'https://hrkoyama.github.io/code/quantum-atoms/'+a.edition+'/',
          'files':files,'terms':{'original_python':'MIT / LICENSE','text_figures_data':'https://hrkoyama.github.io/rights/'},
          'scope':'Hydrogenic radial states and isolated 1s^2 helium HF / exchange-only LDA; includes fixed inputs and independently run finite-basis PySCF references.'}
(base/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
prefix='quantum-atoms-'+a.edition+'/'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in sorted([*files,'source-manifest.json']):
        info=zipfile.ZipInfo(prefix+name,date_time=(*map(int,a.edition[:10].split('-')),0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
        z.writestr(info,(base/name).read_bytes())
with tempfile.TemporaryDirectory(prefix='quantum-atoms-check-') as td:
    temp=Path(td)
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())=={prefix+f for f in [*files,'source-manifest.json']}
        assert sum(x.file_size for x in z.infolist())<50_000_000
        for name in files:assert hashlib.sha256(z.read(prefix+name)).hexdigest()==files[name]
        z.extractall(temp)
    extracted=temp/prefix
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','MPLCONFIGDIR':str(temp/'mpl')}
    tests=subprocess.run([sys.executable,'-m','pytest','-q','--junitxml='+str(temp/'tests.xml')],cwd=extracted,text=True,capture_output=True,env=env)
    print(tests.stdout[-350:])
    if tests.returncode:print(tests.stderr);raise SystemExit(tests.returncode)
    suite=ET.parse(temp/'tests.xml').getroot().find('testsuite');counts={k:int(suite.attrib[k]) for k in ['tests','failures','errors','skipped']}
    reproduced=subprocess.run([sys.executable,'run.py','--output',str(temp/'reproduced'),'--figures'],cwd=extracted,text=True,capture_output=True,env=env)
    if reproduced.returncode:print(reproduced.stdout,reproduced.stderr);raise SystemExit(reproduced.returncode)
    report=json.loads((temp/'reproduced/results.json').read_text());stored=json.loads((base/'results/results.json').read_text())
    assert all(report['checks'].values())
    pairs=list(zip(report['hydrogenic']['refinement'],stored['hydrogenic']['refinement']))+list(zip(report['helium']['refinement'],stored['helium']['refinement']))
    energy_delta=max(abs(x['energy']-y['energy']) for x,y in pairs);assert energy_delta<1e-10
    result={'schema_version':1,'verified_on':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat(),'edition':a.edition,'archive_sha256':sha(archive),'source_manifest_sha256':sha(base/'source-manifest.json'),
            'execution':'Archive extracted into an independent temporary directory; packaged tests and full fixed-input runner including figures executed there without network or private files.',
            'python':'.'.join(map(str,sys.version_info[:3])),'environment':{x:importlib.metadata.version(x) for x in ['numpy','scipy','matplotlib','pytest']},
            **counts,'passed':counts['tests']-counts['failures']-counts['errors']-counts['skipped'],'checks':report['checks'],
            'maximum_reproduced_energy_difference':energy_delta,'independent_reference':{'file':'reference-pyscf.json','sha256':sha(base/'reference-pyscf.json'),'environment':json.loads((base/'reference-pyscf.json').read_text())['environment'],'regeneration':'python reference_pyscf.py --input inputs.json --output new-reference.json'},
            'scope':'Limited educational checks and finite-basis/quadrature reference comparisons; not certification of general-purpose HF/DFT or exact correlated helium.'}
    (base/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'archive_bytes':archive.stat().st_size,'files':len(files),'passed':result['passed'],'energy_delta':energy_delta}))
