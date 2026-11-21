#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish every shared equation/model entry with statically typeset formulas and deep reading links."""
from collections import Counter
from pathlib import Path
import hashlib
import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'numerical-methods-atlas'
ORIGIN='https://hrkoyama.github.io'
URL='/numerical-methods-atlas/equations/'
data=json.loads((ROOT/'catalog/atlas-equations.json').read_text())
coverage=json.loads((ATLAS/'coverage.json').read_text())
inventory={x['id']:x for x in coverage['items'] if x['kind']=='equation'}
records=data['equations']
assert len({x['id'] for x in records})==len(records)
assert {x['id'] for x in records}==set(inventory),'Reconcile equation formulas with the shared coverage inventory'
assert len(records)==coverage['counts']['equations']
groups={g['id']:g for g in data['groups']}
for x in records:
    assert x['status']==inventory[x['id']]['status'],x['id']
    assert x['chapter']==inventory[x['id']]['chapter'],x['id']
    assert x['group'] in groups and x['formula'] and all(x['formula']),x['id']
    assert x['name']['ja'] and x['name']['en'] and x['note']['ja'] and x['note']['en']

math=json.loads(subprocess.run(
    ['node','scripts/render-atlas-math.cjs'],cwd=ROOT,
    input=json.dumps(records,ensure_ascii=False),text=True,capture_output=True,check=True
).stdout)
counts=Counter(x['group'] for x in records)
status_counts=Counter(x['status'] for x in records)
assert status_counts['local-example']==coverage['counts']['local_equations']
assert status_counts['reading']==coverage['counts']['reading_equations']
esc=html.escape

def link(url,label):
    return '<a href="'+esc(url)+'">'+esc(label)+'</a>'

def reading(chapter,lang,section=None):
    path=ATLAS/lang/'read'/chapter/'index.html'
    assert path.is_file(),path
    if section:
        assert re.search(r'\bid=[\"\']'+re.escape(section)+r'[\"\']',path.read_text()),(chapter,lang,section)
    return f'/numerical-methods-atlas/{lang}/read/{chapter}/'+('#'+section if section else '')

sections=[]
for lang in ['ja','en']:
    ja=lang=='ja'
    title='数式から探す' if ja else 'Browse by equation'
    body='<section data-site-language="'+lang+'" lang="'+lang+'"><p class="eyebrow">EQUATIONS / ALL ATLAS MODELS</p><h1>'+title+'</h1>'
    intro=(f'アトラスに収録中の全{len(records)}方程式・モデルを並べました。式の形から選び、それぞれの解説へ進めます。' if ja else f'Browse all {len(records)} equation/model entries in the atlas. Recognize a formula and follow its explanation.')
    body+='<p class="intro">'+intro+'</p>'
    summary=(f'計算例あり{status_counts["local-example"]}項目・文献解説のみ{status_counts["reading"]}項目。モデルの種類数であり、表示する式の行数ではありません。' if ja else f'{status_counts["local-example"]} entries link to scoped local examples; {status_counts["reading"]} are literature-only. These count model entries, not displayed equation lines.')
    body+='<p class="resource-summary">'+summary+'</p>'
    note=('式は代表形、または明記した模式形です。係数・単位・次元・構成則・境界条件は解説先で確認してください。「計算例あり」には縮約模型やFourier記号の検証も含みます。' if ja else 'Formulas are representative or explicitly schematic forms. Consult each chapter for coefficients, units, dimensions, closure and boundaries. Local examples can include reduced models and Fourier-symbol checks.')
    body+='<p>'+note+'</p><nav class="resource-nav">'
    body+=link('/numerical-methods-atlas/?lang='+lang,'アトラスの冒頭' if ja else 'Atlas home')
    body+=link('/numerical-methods-atlas/?lang='+lang+'#/coverage?kind=equation','収録台帳と数え方' if ja else 'Coverage inventory and counting rules')
    body+=link('/numerical-methods-atlas/test-cases/?lang='+lang,'テスト計算の全体一覧' if ja else 'All test problems')+'</nav>'
    body+='<nav class="resource-nav" aria-label="Equation groups">'
    body+=''.join(link('#'+g['id']+'-'+lang,g[lang]+' ('+str(counts[g['id']])+')') for g in data['groups'])+'</nav>'
    for group in data['groups']:
        group_rows=[x for x in records if x['group']==group['id']]
        body+='<section><h2 id="'+group['id']+'-'+lang+'">'+esc(group[lang])+' — '+str(len(group_rows))+'</h2>'
        body+='<nav class="equation-jump-list" aria-label="'+esc(group[lang])+'">'
        body+=''.join(link('#'+x['id']+'-'+lang,x['name'][lang]) for x in group_rows)+'</nav><div class="equation-index">'
        for x in group_rows:
            route=reading(x['chapter'],lang,x.get('section'))
            wide=' equation-entry-wide' if any(len(f)>95 for f in x['formula']) else ''
            body+='<article class="equation-entry'+wide+'" id="'+x['id']+'-'+lang+'" data-equation-id="'+x['id']+'" data-equation-status="'+x['status']+'">'
            for alias in x.get('anchor_aliases',[]):body+='<span id="'+alias+'-'+lang+'"></span>'
            body+='<h3>'+esc(x['name'][lang])+'</h3>'
            label=('計算例あり' if x['status']=='local-example' else '文献解説のみ・専用ソルバーなし') if ja else ('Scoped local example' if x['status']=='local-example' else 'Literature only / no dedicated solver')
            body+='<p class="resource-status">'+label+'</p><div class="equation-preview">'+''.join(math['rendered'][x['id']])+'</div>'
            if wide:body+='<p class="equation-scroll-note">'+('長い数式は横にスクロールして読めます。' if ja else 'Scroll horizontally to read long equations.')+'</p>'
            body+='<p>'+esc(x['note'][lang])+'</p>'+link(route,'このモデルの解説へ →' if ja else 'Read this model →')
            for chapter in x.get('related_chapters',[]):body+=' · '+link(reading(chapter,lang),'関連するテストの解説' if ja else 'Related test definitions')
            body+='</article>'
        body+='</div></section>'
    body+='<p>'+link('index.json','全方程式・モデル / JSON' if ja else 'All equations and models / JSON')+' · '+link('/using/','引用と利用条件' if ja else 'Citation and reuse')+'</p></section>'
    sections.append(body)

digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()[:12]
head='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
head+='<title data-page-title-ja="数式から探す | 数値計算法アトラス" data-page-title-en="Browse by equation | Numerical Methods Atlas">数式から探す | 数値計算法アトラス</title>'
head+='<meta name="description" content="全'+str(len(records))+'方程式・モデルの数式一覧から、それぞれの解説へ。Browse every atlas equation/model with formulas and direct chapter links.">'
head+='<link rel="canonical" href="'+ORIGIN+URL+'">'
head+='<link rel="stylesheet" href="/numerical-methods-atlas/vendor/katex.min.css">'
head+='<link rel="stylesheet" href="/styles/atlas-resources.css?v='+digest(ROOT/'styles/atlas-resources.css')+'">'
head+='<link rel="stylesheet" href="/styles/atlas-purpose.css?v='+digest(ROOT/'styles/atlas-purpose.css')+'"></head>'
dest=ROOT/URL.lstrip('/');dest.mkdir(parents=True,exist_ok=True)
(dest/'index.html').write_text(head+'<body class="profile-page"><main id="main" class="profile-main atlas-resource-main">'+''.join(sections)+'</main></body></html>\n')
public={**data,'url':ORIGIN+URL,'counts':{'total':len(records),'local_example':status_counts['local-example'],'reading_only':status_counts['reading'],'groups':dict(counts)},'formula_renderer':{'name':math['renderer'],'version':math['version']},'equations':[{**x,'reading':{lang:ORIGIN+reading(x['chapter'],lang,x.get('section')) for lang in ['ja','en']}} for x in records]}
(dest/'index.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
path=ATLAS/'sitemap.xml';xml=ET.parse(path);root=xml.getroot();ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
if ORIGIN+URL not in {x.text for x in root.findall('.//{*}loc')}:ET.SubElement(ET.SubElement(root,ns+'url'),ns+'loc').text=ORIGIN+URL
ET.register_namespace('',ns[1:-1]);xml.write(path,encoding='utf-8',xml_declaration=True)
guide=ROOT/'llms.txt';text=guide.read_text()
text=re.sub(r'^- \[Equation/model index\].*\n?','',text,flags=re.M)
line=f'- [Equation/model index]({ORIGIN}{URL}): all {len(records)} shared model entries, representative LaTeX formulas, local-example/literature-only status and direct bilingual chapter-section links. Machine-readable records are at {ORIGIN}{URL}index.json.\n'
guide.write_text(text.rstrip()+'\n'+line)
print('Built complete equation/model index:',len(records),'entries;',dict(status_counts))
