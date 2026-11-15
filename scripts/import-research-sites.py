#!/usr/bin/env python3
"""Import reviewed static publication artifacts; never run scientific experiments.

Build the upstream numerical website/dist and thermal dist first, then pass
those directories. Only URL/navigation adaptations are applied to text files;
all images, movies, arrays and downloadable scientific code remain unchanged.
"""
import argparse,json,re,shutil,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--numerical-dist',type=Path,required=True)
parser.add_argument('--thermal-dist',type=Path,required=True)
args=parser.parse_args()
MOVED=('numerical-methods-atlas','the-art-of-thermal-instability')
TEXT={'.html','.js','.mjs','.json','.xml','.txt','.md','.css','.csv','.bib'}
def rebase(s):
 for prefix in (*MOVED,'guide','rights'):
  s=s.replace('https://koyamarium.github.io/'+prefix+'/', 'https://hrkoyama.github.io/'+prefix+'/')
 s=s.replace('https://koyamarium.github.io/the-art-of-numerical-algorithms/', 'https://hrkoyama.github.io/numerical-methods-atlas/')
 s=s.replace('https://koyamarium.github.io/#contact','mailto:koyamarium@gmail.com')
 s=s.replace('https://koyamarium.github.io/?lang=ja#contact','mailto:koyamarium@gmail.com')
 return s
receipt={'importedOn':'2026-11-16','adaptations':'Public URL rebasing and shared navigation/language integration. No recomputation of experiments.','projects':{}}
for name,source in zip(MOVED,[args.numerical_dist,args.thermal_dist]):
 source=source.resolve()
 for required in ['index.html','sitemap.xml']:assert (source/required).is_file(),source/required
 target=ROOT/name
 if target.exists():shutil.rmtree(target)
 shutil.copytree(source,target)
 binaries={};text_count=0
 for p in target.rglob('*'):
  if not p.is_file():continue
  if p.is_symlink():raise ValueError('Symlinks are not public artifacts: '+str(p))
  if p.suffix.lower() in TEXT:
   s=p.read_text();updated=rebase(s)
   if updated!=s:p.write_text(updated);text_count+=1
  else:binaries[p.relative_to(target).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 if name=='numerical-methods-atlas':
  p=target/'app.js';s=p.read_text().replace("localStorage.getItem('numart-language')", "localStorage.getItem('hrkoyama.home.language') || localStorage.getItem('numart-language')")
  s=s.replace("localStorage.setItem('numart-language',language);", "localStorage.setItem('numart-language',language);localStorage.setItem('hrkoyama.home.language',language);")
  p.write_text(s)
  p=target/'site.json';metadata=json.loads(p.read_text());metadata['sourcePublicationRepository']=metadata['publicationRepository'];metadata['publicationRepository']='hrkoyama/hrkoyama.github.io';p.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
 receipt['projects'][name]={'sourceRepository':'https://github.com/koyamarium/'+name,'sourceCommit':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),'files':sum(p.is_file() for p in target.rglob('*')),'rebasedTextFiles':text_count,'binarySha256':binaries}
(ROOT/'research-imports.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print('Imported public artifacts; run build-site-chrome.mjs, then build-guide.py --local-site .')
