#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a static, bilingual equation-first reading index from curated representative forms."""
from pathlib import Path
import html
import json
import hashlib
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://hrkoyama.github.io'
url='/numerical-methods-atlas/equations/'
data=json.loads((ROOT/'catalog/atlas-equations.json').read_text())
total=json.loads((ROOT/'numerical-methods-atlas/coverage.json').read_text())['counts']['equations']
esc=html.escape
sections=[]
for lang in ['ja','en']:
    ja=lang=='ja'
    title='数式から探す' if ja else 'Browse by equation'
    count=len(data['equations'])
    body='<section data-site-language="'+lang+'" lang="'+lang+'"><p class="eyebrow">EQUATIONS / READING ROUTES</p><h1>'+title+'</h1><p class="intro">'+(f'式の形を眺めて、扱いたい問題を選んでください。代表的な{count}項目から、解説・手法・テスト計算へ進めます。' if ja else f'Recognize an equation and choose a problem. Start with {count} representative entries, then follow explanations, methods and test calculations.')+'</p><p>'+(f'掲載式は入口となる代表形です。係数・単位・次元・状態方程式・境界条件は解説先で確認してください。全{total}方程式・モデルの収録一覧とは区別しています。' if ja else f'These are representative forms. Check coefficients, units, dimensions, closure and boundaries in the linked chapters. This initial index is separate from the full {total}-entry equation/model inventory.')+'</p><nav class="resource-nav"><a href="/numerical-methods-atlas/?lang='+lang+'">'+('アトラスの冒頭' if ja else 'Atlas home')+'</a><a href="/numerical-methods-atlas/?lang='+lang+'#/coverage?kind=equation">'+('全方程式・モデルの収録一覧' if ja else 'Full equation/model inventory')+'</a><a href="/numerical-methods-atlas/?lang='+lang+'#/equations">'+('計算した波形を比較する' if ja else 'Compare computed profiles')+'</a></nav><div class="equation-index">'
    for x in data['equations']:
        route=f'/numerical-methods-atlas/{lang}/read/'+x['chapter']+'/'
        assert (ROOT/route.lstrip('/')/'index.html').exists(),route
        body+='<article class="equation-entry" id="'+x['id']+'-'+lang+'"><h2>'+esc(x['name'][lang])+'</h2><div class="equation-preview">'+''.join('<div>'+esc(f)+'</div>' for f in x['formula'])+'</div><p>'+esc(x['note'][lang])+'</p><a href="'+route+'">'+('解説・手法・検証へ →' if ja else 'Explanations, methods and checks →')+'</a></article>'
    body+='</div><p><a href="index.json">Equation index / JSON</a> · <a href="/using/">'+('引用と利用条件' if ja else 'Citation and reuse')+'</a></p></section>'
    sections.append(body)
version=hashlib.sha256((ROOT/'styles/atlas-purpose.css').read_bytes()).hexdigest()[:12]
resource_version=hashlib.sha256((ROOT/'styles/atlas-resources.css').read_bytes()).hexdigest()[:12]
document='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title data-page-title-ja="数式から探す | 数値計算法アトラス" data-page-title-en="Browse by equation | Numerical Methods Atlas">数式から探す | 数値計算法アトラス</title><meta name="description" content="代表的な方程式の形から、数値計算の解説・手法・検証へ。Browse representative equations and follow reading and verification routes."><link rel="canonical" href="'''+ORIGIN+url+'"><link rel="stylesheet" href="/styles/atlas-resources.css?v='+resource_version+'"><link rel="stylesheet" href="/styles/atlas-purpose.css?v='+version+'"></head><body class="profile-page"><main id="main" class="profile-main atlas-resource-main">'+''.join(sections)+'</main></body></html>\n'
dest=ROOT/url.lstrip('/');dest.mkdir(parents=True,exist_ok=True);(dest/'index.html').write_text(document)
public={**data,'url':ORIGIN+url,'equations':[{**x,'reading':{lang:ORIGIN+f'/numerical-methods-atlas/{lang}/read/'+x['chapter']+'/' for lang in ['ja','en']}} for x in data['equations']]}
(dest/'index.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
path=ROOT/'numerical-methods-atlas/sitemap.xml';xml=ET.parse(path);root=xml.getroot();ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
if ORIGIN+url not in {x.text for x in root.findall('.//{*}loc')}:ET.SubElement(ET.SubElement(root,ns+'url'),ns+'loc').text=ORIGIN+url
ET.register_namespace('',ns[1:-1]);xml.write(path,encoding='utf-8',xml_declaration=True)
print('Built equation-first index:',len(data['equations']),'representative entries.')
