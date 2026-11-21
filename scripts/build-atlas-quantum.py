#!/usr/bin/env python3
"""Publish the curated quantum reading, bibliography and honest coverage counts.

This offline build does not run or advertise an electronic-structure solver.
"""
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'numerical-methods-atlas'
ORIGIN='https://hrkoyama.github.io'
load=lambda p:json.loads(p.read_text())
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
esc=html.escape
data=load(ROOT/'catalog/atlas-quantum.json')
queue=load(ROOT/'catalog/atlas-work-queue.json')
methods={x['id']:x for x in load(ROOT/'catalog/atlas-methods.json')['methods'] if x['group']['id']=='quantum'}
assert {x['id'] for x in data['sections']}==set(methods)
assert all(x['status']=='reading-only' and not x['code_modules'] and not x['test_files'] for x in methods.values())
refs={x['id']:x for x in data['references']}
assert len(refs)==len(data['references'])
assert len({x['doi'].lower() for x in refs.values()})==len(refs)
assert all(x['references'] and all(r in refs for r in x['references']) for x in data['sections'])
math_records=data['sections']+[child for x in data['sections'] for child in x.get('subsections',[])]
math=json.loads(subprocess.run(['node','scripts/render-atlas-math.cjs'],cwd=ROOT,input=json.dumps(math_records),text=True,capture_output=True,check=True).stdout)['rendered']
def link(url,label):return '<a href="'+esc(url)+'">'+esc(label)+'</a>'
def paragraph(text):return '<p>'+esc(text)+'</p>'
def reference(r):return esc(r['author'].replace(' and ','; '))+f' ({r["year"]}). '+link(r['source'],r['title'])+'. '+esc(r['journal'])+'.'
bodies={}
for lang in ['ja','en']:
    ja=lang=='ja';route=f'/numerical-methods-atlas/{lang}/read/quantum-chemistry/'
    body='<p class="eyebrow">ELECTRONIC STRUCTURE · QUANTUM CHEMISTRY · DFT</p><h1>'+esc(data['title'][lang])+'</h1><p class="intro">'+esc(data['description'][lang])+'</p>'
    body+='<p class="resource-summary">'+(f'{len(methods)}項目の日英解説と{len(refs)}件の一次文献を公開。専用の実行コード・数値検証例はUnder constructionです。以下の式や検証計画を、計算済みの結果とは区別しています。' if ja else f'Bilingual reading for {len(methods)} entries and {len(refs)} primary publications. Dedicated runnable code and numerical validation are under construction; the equations and test plans below are not computed results.')+'</p>'
    body+='<nav class="resource-nav">'+''.join(link(u,t) for u,t in [('/numerical-methods-atlas/?lang='+lang,'アトラス冒頭' if ja else 'Atlas home'),('/numerical-methods-atlas/methods/?lang='+lang+'#quantum-'+lang,'手法の見取り図' if ja else 'Method map'),('/numerical-methods-atlas/equations/?lang='+lang+'#quantum-'+lang,'数式から探す' if ja else 'Browse by equation'),('#verification','実行・検証の計画' if ja else 'Runnable-example plan'),('#sources','一次文献と公式資料' if ja else 'Primary sources and documentation')])+'</nav>'
    body+='<h2 id="how-to-read">'+('最初に分けて考える3つのこと' if ja else 'Three choices to keep separate')+'</h2><div class="quantum-terms">'
    choices=[('物理モデル・近似','Physical model and approximation','HF、KS-DFT、MP2、CI、CC等。どの多電子状態やエネルギーを近似するか。','HF, KS-DFT, MP2, CI or CC: which many-electron states and energies are approximated?'),('表現・離散化','Representation and discretization','基底、格子、擬ポテンシャル、k点。モデルを有限の計算問題にする方法。','Basis, grid, pseudopotential and k sampling: how is the model made finite?'),('方程式の解き方','Equation solver','固有値計算、SCF、混合、DIIS。選んだ離散問題をどこまで解いたか。','Eigensolvers, SCF, mixing and DIIS: how accurately is the chosen discrete problem solved?')]
    for jh,eh,jp,ep in choices:body+='<div><h3>'+esc(jh if ja else eh)+'</h3>'+paragraph(jp if ja else ep)+'</div>'
    body+='</div>'+paragraph('「SCFが収束した」「基底が収束した」「物理モデルが妥当」は別の確認です。代表式は原子単位系（ℏ = m_e = e = 4πε₀ = 1）を用います。有限の分子と周期的な固体は境界条件も違います。' if ja else 'SCF convergence, basis convergence and physical adequacy are distinct checks. Representative equations use atomic units (ℏ = m_e = e = 4πε₀ = 1). Finite molecules and periodic solids also require different boundaries.')
    body+='<nav class="quantum-map" aria-label="'+('分野の見取り図' if ja else 'Field map')+'">'
    for lane in data['lanes']:
        body+='<section><h2>'+esc(lane[lang])+'</h2><ul>'+''.join('<li>'+link('#'+x['id'],methods[x['id']]['name'][lang])+'</li>' for x in data['sections'] if x['lane']==lane['id'])+'</ul></section>'
    body+='</nav>'
    for x in data['sections']:
        body+='<section class="quantum-entry" data-quantum-id="'+x['id']+'"><h2 id="'+x['id']+'">'+esc(methods[x['id']]['name'][lang])+'</h2>'
        body+=''.join(paragraph(p) for p in x['paragraphs'][lang])
        if math[x['id']]:
            body+='<div class="quantum-math">'+''.join(math[x['id']])+'</div>'
            if any(len(f)>90 for f in x['formula']):body+='<p class="quantum-scroll-note">'+('長い式は横にスクロールできます。' if ja else 'Long equations scroll horizontally.')+'</p>'
        for child in x.get('subsections',[]):
            body+='<section class="quantum-subsection"><h3 id="'+child['id']+'">'+esc(child['title'][lang])+'</h3>'+''.join(paragraph(p) for p in child['paragraphs'][lang])
            if math[child['id']]:body+='<div class="quantum-math">'+''.join(math[child['id']])+'</div>'
            body+='</section>'
        body+='<p class="quantum-caution">'+esc(x['caution'][lang])+'</p><p>'+link('/numerical-methods-atlas/methods/'+x['id']+'/?lang='+lang,'条件・実装状況・JSON' if ja else 'Assumptions, implementation status and JSON')+'</p><ul>'
        body+=''.join('<li>'+link('#ref-'+r,refs[r]['author'].replace(' and ','; ')+f' ({refs[r]["year"]})')+'</li>' for r in x['references'])+'</ul></section>'
    body+='<section><h2 id="verification">'+('次に付ける実行・検証例' if ja else 'Next runnable validation examples')+'</h2>'+paragraph('以下は計画で、まだ計算結果ではありません。同じ入力と停止条件を公開し、独立した参照、数値誤差、モデルの限界を別々に示します。現行58問題の総数には加えていません。' if ja else 'These are plans, not results, and are not added to the current 58-problem inventory. Publish explicit inputs and stopping rules, with independent references, numerical error and model limitations distinguished.')
    for x in data['verification_plan']:body+='<article class="quantum-plan"><p class="resource-status">Under construction</p><h3>'+esc(x['title'][lang])+'</h3>'+paragraph(x['check'][lang])+'</article>'
    body+='</section><section><h2 id="further-topics">'+('今後広げる項目' if ja else 'Further topics to develop')+'</h2>'+paragraph('以下は追加候補です。この導入で専用解説・実装を提供しているという意味ではありません。AMR・並列化・mixed precisionは既存の収録方針どおり対象外です。' if ja else 'These are extension candidates, not dedicated readings or implementations already supplied here. AMR, parallelization and mixed precision remain outside the editorial scope.')+'<ul>'+''.join('<li>'+esc(x)+'</li>' for x in data['future_topics'][lang])+'</ul></section>'
    body+='<section><h2 id="sources">'+('一次文献と確認範囲' if ja else 'Primary publications and review scope')+'</h2>'+paragraph(data['source_policy'][lang])+'<ol class="quantum-references">'
    for r in sorted(refs.values(),key=lambda x:(x['year'],x['id'])):body+='<li id="ref-'+r['id']+'"><cite>'+reference(r)+'</cite></li>'
    body+='</ol><h3>'+('実装を調べるための公式資料' if ja else 'Official implementation documentation')+'</h3>'+paragraph('以下は外部ソフトウェアの資料です。このアトラスで実行・検証済みであることは意味しません。' if ja else 'These describe external software; linking them does not claim an atlas-verified run.')+'<ul>'+''.join('<li>'+link(x['url'],x['label'])+'</li>' for x in data['documentation'])+'</ul></section><p>'+link('/catalog/atlas-quantum.json','本文・式・出典 / JSON' if ja else 'Text, formulas and sources / JSON')+' · '+link('/using/?lang='+lang,'利用と引用' if ja else 'Use and citation')+'</p>'
    bodies[lang]=body
    other='en' if ja else 'ja'
    head='<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(data['title'][lang])+' | Numerical Methods Atlas</title><meta name="description" content="'+esc(data['description'][lang])+'"><link rel="canonical" href="'+ORIGIN+route+'"><link rel="alternate" hreflang="'+other+'" href="'+ORIGIN+f'/numerical-methods-atlas/{other}/read/quantum-chemistry/'+'"><link rel="stylesheet" href="/numerical-methods-atlas/vendor/katex.min.css">'
    for name in ['atlas-resources','atlas-quantum']:head+='<link rel="stylesheet" href="/styles/'+name+'.css?v='+sha(ROOT/'styles'/(name+'.css'))[:12]+'">'
    dest=ROOT/route.lstrip('/');dest.mkdir(parents=True,exist_ok=True)
    structured={'@context':'https://schema.org','@type':'LearningResource','name':data['title'][lang],'description':data['description'][lang],'inLanguage':lang,'url':ORIGIN+route,'dateModified':data['reviewed_on'],'educationalLevel':'Graduate','learningResourceType':'Introductory survey','citation':[r['source'] for r in refs.values()]}
    (dest/'index.html').write_text(head+'<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False).replace('<','\\u003c')+'</script></head><body class="profile-page"><main id="main" class="profile-main atlas-resource-main atlas-quantum-main">'+body+'</main></body></html>\n')
    path=ATLAS/lang/'read/index.html';text=re.sub(r'<!-- quantum-entry -->.*?<!-- /quantum-entry -->','',path.read_text(),flags=re.S)
    text=text.replace('</main>','<!-- quantum-entry --><section class="page-width"><h2>'+link(route,data['title'][lang])+'</h2>'+paragraph(data['description'][lang])+'</section><!-- /quantum-entry --></main>');path.write_text(text)

# The live reading router must know the chapter before redirecting to static HTML.
for name in ['content.en.json','content.ja.json','content.json']:
    path=ATLAS/name;content=load(path);lang='ja' if '.ja.' in name else 'en'
    content['quantum-chemistry']={'title':data['title'][lang],'html':bodies[lang],'headings':[{'level':2,'id':x['id'],'title':methods[x['id']]['name'][lang]} for x in data['sections']],'locale':lang}
    write(path,content)

# Extend the common reference library and downloadable BibTeX, deduplicating DOI.
path=ATLAS/'references.json';library=[x for x in load(path) if x.get('origin')!='curated-quantum-reading']
identities={x.get('doi','').lower() for x in library if x.get('doi')}
for r in refs.values():
    if r['doi'].lower() not in identities:
        assert r['id'] not in {x['id'] for x in library}
        library.append(r);identities.add(r['doi'].lower())
write(path,library)
path=ATLAS/'assets/references.bib';text=re.sub(r'\n% BEGIN QUANTUM READING\n.*?% END QUANTUM READING\n?','',path.read_text(),flags=re.S)
text+='\n% BEGIN QUANTUM READING\n'
for r in refs.values():text+='@article{'+r['id']+',\n'+''.join('  '+k+' = {'+str(r[k])+'},\n' for k in ['author','title','journal','year','doi'])+'}\n\n'
path.write_text(text+'% END QUANTUM READING\n')

equations=[x for x in load(ROOT/'catalog/atlas-equations.json')['equations'] if x['group']=='quantum']
for path in [ATLAS/'coverage.json',ATLAS/'assets/site-coverage.json']:
    coverage=load(path)
    coverage['items']=[x for x in coverage['items'] if x.get('origin')!='curated-quantum-reading']
    for x in methods.values():coverage['items'].append({'kind':'method','id':x['id'],'label':x['name']['en'],'chapter':'quantum-chemistry','status':'reading','group':'Electronic structure & quantum chemistry','scope':'Introductory formulation only; no dedicated solver or numerical validation.','origin':'curated-quantum-reading'})
    for x in equations:coverage['items'].append({'kind':'equation','id':x['id'],'label':x['name']['en'],'chapter':x['chapter'],'status':x['status'],'group':'Electronic structure & quantum chemistry','scope':x['note']['en'],'origin':'curated-quantum-reading'})
    coverage['publications']=[x for x in coverage['publications'] if x.get('origin')!='curated-quantum-reading']
    identities={x['identity'] for x in coverage['publications']}
    for r in refs.values():
        ident='doi:'+r['doi'].lower()
        if ident not in identities:
            coverage['publications'].append({'id':r['id'],'type':'article','identity':ident,'origin':'curated-quantum-reading'});identities.add(ident)
    c=coverage['counts'];pub=Counter(x['type'] for x in coverage['publications'])
    for kind in ['method','equation']:
        rows=[x for x in coverage['items'] if x['kind']==kind]
        c[kind+'s']=len(rows);c['local_'+kind+'s']=sum(x['status']=='local-example' for x in rows);c['reading_'+kind+'s']=sum(x['status']=='reading' for x in rows)
    c.update(references=len(coverage['publications']),journal_articles=pub['article'],conference_papers=pub['inproceedings'],papers=pub['article']+pub['inproceedings'],reading_chapters=len({p.parent for p in (ATLAS/'en/read').glob('*/index.html')}))
    coverage['counted_on']=data['reviewed_on']
    coverage['public_extension_sha256']={f:sha(ROOT/f) for f in ['catalog/atlas-quantum.json','catalog/atlas-methods.json','catalog/atlas-equations.json']}
    write(path,coverage)

# Keep imported prose inventories current without changing any original anchor.
counts=coverage['counts']
for lang in ['ja','en']:
    ja=lang=='ja';extension='<section id="quantum-extension"><h2>'+('電子状態・量子化学の追加項目' if ja else 'Added electronic-structure reading')+'</h2>'+paragraph('以下は導入解説のみで、専用実装は未公開です。' if ja else 'These are introductory readings, without dedicated implementations.')+'<ul>'+''.join('<li>'+link(f'/numerical-methods-atlas/{lang}/read/quantum-chemistry/#{x["id"]}',x['name'][lang])+'</li>' for x in methods.values())+'</ul></section>'
    bib='<section id="quantum-references"><h2>'+('量子化学の追加一次文献' if ja else 'Added quantum-chemistry primary publications')+'</h2><ol>'+''.join('<li>'+reference(r)+'</li>' for r in refs.values())+'</ol></section>'
    roadmap='<section id="atlas-work-queue"><h2>'+('現在の優先順位と2027年以降' if ja else 'Current priorities and 2027 onward')+'</h2>'
    for x in queue['items']:roadmap+='<h3>'+str(x['target_year'])+' · '+esc(x['title'][lang])+'</h3>'+paragraph(x['scope'][lang])
    roadmap+='<p>'+link('/catalog/atlas-work-queue.json','作業台帳 / JSON' if ja else 'Work queue / JSON')+'</p></section>'+paragraph('これより下は、これまでの整備と従来の検証計画です。現在の優先順位は上記を参照してください。' if ja else 'The sections below record earlier development and validation plans. The current priorities are stated above.')
    for name,block,marker in [('site-coverage',extension,'quantum-inventory'),('references',bib,'quantum-bibliography'),('roadmap',roadmap,'atlas-work-queue')]:
        start='<!-- '+marker+' -->';end='<!-- /'+marker+' -->'
        for path,mode in [(ATLAS/lang/'read'/name/'index.html','static'),(ATLAS/('content.'+lang+'.json'),'content')]+([(ATLAS/'content.json','content')] if lang=='en' else []):
            doc=load(path) if mode=='content' else None
            text=doc[name]['html'] if doc is not None else path.read_text()
            text=re.sub(re.escape(start)+r'.*?'+re.escape(end),'',text,flags=re.S)
            if name=='roadmap':
                heading='量子化学・DFT：解説公開、検証例は次段階' if ja else 'Quantum chemistry and DFT: reading available, numerical validation next'
                current='<h2 id="planned-quantum-chemistry-and-dft">'+heading+'</h2>'+paragraph(f'{len(methods)}項目の導入解説・代表式・一次文献を公開しました。専用コードと数値検証は次段階です。解説のみとして収録台帳へ加え、実装済み・検証済みとは表示していません。' if ja else f'Introductions, representative formulas and primary references are available for {len(methods)} entries. Dedicated code and numerical validation are next. These entries are counted as reading-only, without implementation or verification claims.')
                current+='<p>'+link(f'/numerical-methods-atlas/{lang}/read/quantum-chemistry/','日英の解説と計算例の計画' if ja else 'Bilingual overview and planned numerical examples')+'</p>'
                text=re.sub(r'<h2 id="planned-quantum-chemistry-and-dft"[^>]*>.*?(?=<h2|\Z)',lambda m:current,text,flags=re.S)
                if doc is not None:
                    for h in doc[name]['headings']:
                        if h['id']=='planned-quantum-chemistry-and-dft':h['title']=heading
            if name=='site-coverage':
                text=re.sub(r'(counted |集計日)\d{4}-\d\d-\d\d',lambda m:m[1]+data['reviewed_on'],text)
                if ja:
                    text=re.sub(r'方程式・モデル\d+項目・計算法と構成要素\d+項目・学術誌／会議論文\d+件・全参考資料\d+件。',f'方程式・モデル{counts["equations"]}項目・計算法と構成要素{counts["methods"]}項目・学術誌／会議論文{counts["papers"]}件・全参考資料{counts["references"]}件。',text)
                    text=re.sub(r'文献解説のみは\d+で',f'文献解説のみは{counts["reading_equations"]}で',text)
                    text=re.sub(r'ローカル実験のある項目は85、文献解説のみは\d+です',f'ローカル実験のある項目は85、文献解説のみは{counts["reading_methods"]}です',text)
                    text=re.sub(r'読書章はこの一覧を含め\d+章',f'読書章はこの一覧を含め{counts["reading_chapters"]}章',text)
                    text=re.sub(r'\d+件：学術誌論文',f'{counts["journal_articles"]}件：学術誌論文',text)
                else:
                    text=re.sub(r'\d+ equation/model entries · \d+ methods and building blocks · \d+ journal/conference papers · \d+ total sources[.]',f'{counts["equations"]} equation/model entries · {counts["methods"]} methods and building blocks · {counts["papers"]} journal/conference papers · {counts["references"]} total sources.',text)
                    text=re.sub(r'15 entries have scoped local examples; \d+ are reading-only',f'15 entries have scoped local examples; {counts["reading_equations"]} are reading-only',text)
                    text=re.sub(r'85 entries have scoped local examples; \d+ are reading-only',f'85 entries have scoped local examples; {counts["reading_methods"]} are reading-only',text)
                    text=re.sub(r'and \d+ reading chapters including this inventory',f'and {counts["reading_chapters"]} reading chapters including this inventory',text)
                    text=re.sub(r'\d+ journal-article records',f'{counts["journal_articles"]} journal-article records',text)
            addition=start+block+end
            if name=='roadmap':text=re.sub(r'(</h1>)',lambda m:m[1]+addition,text,count=1)
            else:text=text.replace('</main>',addition+'</main>') if doc is None else text+addition
            if doc is None:path.write_text(text)
            else:doc[name]['html']=text;write(path,doc)

# Register only real reading pages; examples and extended topics remain plans.
path=ATLAS/'sitemap.xml';xml=ET.parse(path);ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';existing={x.text for x in xml.getroot().findall('.//{*}loc')}
for lang in ['ja','en']:
    url=ORIGIN+f'/numerical-methods-atlas/{lang}/read/quantum-chemistry/'
    if url not in existing:ET.SubElement(ET.SubElement(xml.getroot(),ns+'url'),ns+'loc').text=url
ET.register_namespace('',ns[1:-1]);xml.write(path,encoding='utf-8',xml_declaration=True)
messages=ATLAS/'locales/messages.json';translations=load(messages)
new_copy={
    'planned.quantum.eyebrow':{'ja':'導入解説 / 量子化学・DFT','en':'READING / QUANTUM CHEMISTRY + DFT'},
    'planned.quantum.title':{'ja':'基底関数から電子状態計算へ。','en':'From basis functions to electronic structure.'},
    'planned.quantum.scope':{'ja':f'Schrödinger、HF・DFT、基底・SCF、バンドの対称群、電子相関・励起まで{len(methods)}項目の導入を日英で公開しています。','en':f'Bilingual introductions to {len(methods)} entries cover Schrödinger, HF and DFT, bases, SCF, band symmetry, correlation and excitations.'},
    'planned.quantum.status':{'ja':'導入解説と一次文献を公開。専用の実行コードと数値検証はUnder constructionです。','en':'Introductory reading and primary references are available. Dedicated runnable code and numerical checks are under construction.'},
    'planned.quantum.link':{'ja':'量子化学・DFTの解説を読む','en':'Read the quantum chemistry and DFT overview'},
    'home-map.future':{'ja':'量子化学・DFTの導入解説を公開しました。専用の計算例と検証は今後の作業として区別しています。','en':'Quantum chemistry and DFT now have introductory readings. Dedicated runnable examples and validation remain planned.'},
}
old_copy={key:translations[key] for key in new_copy}
translations.update(new_copy);write(messages,translations)
# Also adapt the static shell retained for visitors without client rendering.
page=ATLAS/'index.html';static=page.read_text()
for key,old in old_copy.items():
    for lang,value in old.items():static=static.replace(esc(value),esc(new_copy[key][lang]))
page.write_text(static)
app=ATLAS/'app.js';text=app.read_text()
notice='const plannedQuantumNotice = () => `<aside class="callout page-width planned-extension" id="quantum-plan" aria-labelledby="quantum-plan-title"><p class="eyebrow">${escapeHTML(t("planned.quantum.eyebrow"))}</p><h2 id="quantum-plan-title">${escapeHTML(t("planned.quantum.title"))}</h2><p>${escapeHTML(t("planned.quantum.scope"))}</p><p class="planned-status">${escapeHTML(t("planned.quantum.status"))}</p><a class="text-link" href="#/read/quantum-chemistry">${escapeHTML(t("planned.quantum.link"))}</a></aside>`;'
text,n=re.subn(r'const plannedQuantumNotice = [^\n]+',lambda m:notice,text);assert n==1
for filename in ['references.json','locales/messages.json']:
    text=re.sub("'"+re.escape(filename)+r"(?:[?]v=[a-f0-9]+)?'","'"+filename+'?v='+sha(ATLAS/filename)[:12]+"'",text)
app.write_text(text)
print('Built bilingual quantum reading:',len(methods),'topics,',len(refs),'primary publications; counts:',counts['methods'],counts['equations'],counts['papers'])
