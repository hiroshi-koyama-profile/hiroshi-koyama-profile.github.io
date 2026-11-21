#!/usr/bin/env python3
"""Merge curated method references by identity, keeping one count per publication."""
from pathlib import Path
from collections import Counter
import html
import json
import re
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'numerical-methods-atlas'
SOURCE=ROOT/'catalog/atlas-method-primary-references.json'
ORIGIN='curated-method-metadata'
if not SOURCE.is_file():
    raise SystemExit('Missing method bibliography catalog; complete curation before rebuilding.')
data=json.loads(SOURCE.read_text())
refs=data['references']

def normalized_doi(r):
    return re.sub(r'^https?://(?:dx\.)?doi.org/','',(r.get('doi') or '').strip(),flags=re.I).lower()

def identity(r):
    if normalized_doi(r):return 'doi:'+normalized_doi(r)
    return r.get('identity') or 'url:'+r['source']

def title_year(r):
    # URL aliases and punctuation/case/width differences do not create works.
    title=unicodedata.normalize('NFKC',r['title']).casefold()
    return ''.join(c for c in title if c.isalnum()),int(r['year'])

def existing_reference(record,library):
    matches=[]
    for previous in library:
        same_id=record['id']==previous['id']
        same_identity=identity(record)==identity(previous)
        same_title_year=title_year(record)==title_year(previous)
        if not (same_id or same_identity or same_title_year):continue
        doi,old_doi=normalized_doi(record),normalized_doi(previous)
        if doi and old_doi and doi!=old_doi:
            raise ValueError('Conflicting DOIs for '+record['id']+' and '+previous['id']+': '+doi+' / '+old_doi)
        if not same_title_year and not (doi and doi==old_doi):
            raise ValueError('Conflicting publication metadata for '+record['id']+' and '+previous['id'])
        matches.append(previous)
    if len(matches)>1:
        raise ValueError('Ambiguous existing publication for '+record['id']+': '+', '.join(r['id'] for r in matches))
    return matches[0] if matches else None

def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
assert len({identity(r) for r in refs})==len(refs),'Duplicate source in method bibliography'
for r in refs:
    assert r['id'] and r['author'] and r['title'] and 1000<=int(r['year'])<=2026
    assert r['type'] in ['article','book','incollection','inproceedings','techreport','misc']
    assert r['source'].startswith('https://')
# Check curated aliases against one another as well: an existing DOI-less work
# must not conceal two incompatible DOI claims that would otherwise both skip.
for index,r in enumerate(refs):existing_reference(r,refs[:index])

path=ATLAS/'references.json'
library=[r for r in json.loads(path.read_text()) if r.get('origin')!=ORIGIN]
added=[]
for original in refs:
    # Retain the existing ID, metadata and coverage identity when a curated source
    # supplies another URL or title formatting for an already counted work.
    if existing_reference(original,library) is not None:continue
    r={**original,'origin':ORIGIN}
    library.append(r);added.append(r)
coverages=[]
for path in [ATLAS/'coverage.json',ATLAS/'assets/site-coverage.json']:
    coverage=json.loads(path.read_text())
    coverage['publications']=[r for r in coverage['publications'] if r.get('origin')!=ORIGIN]
    identifiers={r['identity'] for r in coverage['publications']}
    by_id={r['id']:r for r in coverage['publications']}
    for r in added:
        if r['id'] in by_id:
            existing=by_id[r['id']]['identity']
            if existing.startswith('doi:') and normalized_doi(r) and existing[4:].lower()!=normalized_doi(r):
                raise ValueError('Conflicting coverage DOI for '+r['id'])
            continue
        if identity(r) in identifiers:continue
        row={'id':r['id'],'type':r['type'],'identity':identity(r),'origin':ORIGIN}
        coverage['publications'].append(row)
        identifiers.add(row['identity']);by_id[r['id']]=row
    types=Counter(r['type'] for r in coverage['publications'])
    coverage['counts'].update(references=len(coverage['publications']),papers=types['article']+types['inproceedings'],journal_articles=types['article'],conference_papers=types['inproceedings'],books=types['book'],chapters=types['incollection'],reports=types['techreport'],other_sources=sum(n for t,n in types.items() if t not in ['article','inproceedings','book','incollection','techreport']))
    coverage['counted_on']=max(coverage['counted_on'],data['reviewed_on'])
    coverages.append((path,coverage))
# Reject identity/DOI conflicts before changing any generated bibliography data.
write(ATLAS/'references.json',library)
for path,coverage in coverages:write(path,coverage)

# Existing sources retain their existing BibTeX; add only genuinely new entries.
path=ATLAS/'assets/references.bib';bib=path.read_text()
bib=re.sub(r'\n% BEGIN METHOD METADATA SOURCES\n.*?% END METHOD METADATA SOURCES\n?','',bib,flags=re.S)
bib+='\n% BEGIN METHOD METADATA SOURCES\n'
for r in added:
    bib+='@'+r['type']+'{'+r['id']+',\n'
    for key in ['author','title','journal','booktitle','publisher','year','volume','number','pages','doi','url']:
        value=r.get(key,r['source'] if key=='url' else None)
        if value is not None:bib+='  '+key+' = {'+str(value)+'},\n'
    bib+='}\n\n'
path.write_text(bib+'% END METHOD METADATA SOURCES\n')

def reference(r):
    esc=html.escape
    label=esc(r['author'])+' ('+str(r['year'])+'). '+esc(r['title'])+'.'
    url='https://doi.org/'+r['doi'] if r.get('doi') else r['source']
    return label+' <a href="'+esc(url,quote=True)+'">'+esc(r.get('doi','Original source'))+'</a>'

# Add new sources to both static and client-rendered reading bibliographies.
for lang in ['ja','en']:
    heading='主要手法の条件整理で追加した一次文献・資料' if lang=='ja' else 'Sources added by priority-method curation'
    body='<section id="method-metadata-sources"><h2>'+heading+'</h2><p>'+('個別手法との対応と、原法・採用変種・参照解の区別は手法台帳で確認できます。既存の文献は重複して加算していません。' if lang=='ja' else 'Method records distinguish original methods, adopted variants and references. Existing publications are not counted twice.')+' <a href="/numerical-methods-atlas/methods/?lang='+lang+'">'+('主要24手法の条件と文献' if lang=='ja' else 'Conditions and sources for 24 priority methods')+'</a></p><ol>'+''.join('<li>'+reference(r)+'</li>' for r in added)+'</ol></section>'
    block='<!-- method-metadata-sources -->'+body+'<!-- /method-metadata-sources -->'
    locations=[(ATLAS/lang/'read/references/index.html',False),(ATLAS/('content.'+lang+'.json'),True)]+([(ATLAS/'content.json',True)] if lang=='en' else [])
    for path,is_json in locations:
        doc=json.loads(path.read_text()) if is_json else None
        text=doc['references']['html'] if is_json else path.read_text()
        text=re.sub(r'<!-- method-metadata-sources -->.*?<!-- /method-metadata-sources -->','',text,flags=re.S)
        text=text.replace('</main>',block+'</main>') if '</main>' in text else text+block
        if is_json:
            doc['references']['html']=text
            headings=[h for h in doc['references']['headings'] if h['id']!='method-metadata-sources']
            doc['references']['headings']=headings+[{'level':2,'id':'method-metadata-sources','title':heading}]
            write(path,doc)
        else:path.write_text(text)
print('Method bibliography:',len(refs),'source records,',len(added),'new unique publications.')
