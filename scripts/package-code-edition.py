#!/usr/bin/env python3
"""Package an uncommitted code edition; refuse to replace a tracked archive."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--edition',required=True,help='New edition directory, YYYY-MM-DD')
args=parser.parse_args()
if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',args.edition):parser.error('Use YYYY-MM-DD')
date=datetime.date.fromisoformat(args.edition)
folder=ROOT/'code/numerical-methods-atlas'/args.edition
archive=folder/('atlas-code-'+args.edition+'.zip')
tracked=subprocess.run(['git','ls-files','--error-unmatch',archive.relative_to(ROOT).as_posix()],cwd=ROOT,capture_output=True)
if tracked.returncode==0:raise SystemExit('Archive is already tracked. Prepare a new edition instead of replacing it.')
manifest=json.loads((folder/'source-manifest.json').read_text())
files={}
for p in sorted(folder.rglob('*')):
    if not p.is_file() or p.name in {'source-manifest.json','verification.json',archive.name,'.DS_Store'}:continue
    relative=p.relative_to(folder).as_posix()
    if any(part.startswith('.') or part=='__pycache__' for part in p.relative_to(folder).parts):continue
    if p.suffix not in {'.py','.json','.npz','.csv','.md','.txt','.toml'} and p.name!='LICENSE':raise ValueError('Review unexpected file type before packaging: '+relative)
    files[relative]=hashlib.sha256(p.read_bytes()).hexdigest()
if any(manifest['files'].get(name)!=digest for name,digest in files.items() if name.startswith('numart/')):
    manifest['derived_from_source_revision']=manifest.get('source_revision')
    manifest['source_revision']=None
    manifest['revision_note']='Modified public source; use file hashes to identify this edition.'
manifest.update(edition=args.edition,public_base_url='https://hrkoyama.github.io/code/numerical-methods-atlas/'+args.edition+'/',files=files)
(folder/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in sorted([*files,'source-manifest.json']):
        info=zipfile.ZipInfo('atlas-code-'+args.edition+'/'+name,date_time=(date.year,date.month,date.day,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
        z.writestr(info,(folder/name).read_bytes())
print(json.dumps({'files':len(files),'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},indent=2))
