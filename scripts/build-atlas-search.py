#!/usr/bin/env python3
"""Include the public method registry in the atlas's own search, preserving chapters."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'numerical-methods-atlas'
catalog=json.loads((ROOT/'catalog/atlas-methods.json').read_text())
path=ATLAS/'home-search-index.json';index=json.loads(path.read_text())
index['entries']=[x for x in index['entries'] if x.get('origin')!='public-method-registry']
def add(ident,title,keywords,routes):
    index['entries'].append({'id':ident,'title':title,'headings':{'ja':[],'en':[]},'keywords':keywords,'routes':routes,'origin':'public-method-registry'})
for x in catalog['methods']:
    add('registry-'+x['id'],x['name'],list(x['name'].values())+x.get('aliases',[])+list(x['group'].values()),{lang:'/numerical-methods-atlas/methods/'+x['id']+'/?lang='+lang for lang in ['ja','en']})
add('public-method-map',{'ja':'手法の見取り図','en':'A map of numerical methods'},['手法 見取り図','method map'],{lang:'/numerical-methods-atlas/methods/?lang='+lang for lang in ['ja','en']})
add('public-code-guide',{'ja':'コード・入力・検証を取得する','en':'Get code, inputs and verification'},['公開コード','データ','download','code edition'],{lang:'/numerical-methods-atlas/code-and-data/?lang='+lang for lang in ['ja','en']})
add('thermostats',{'ja':'サーモスタット：温度制御と分布の比較','en':'Thermostats: temperature control and distributions'},['サーモスタット','温度制御','thermostat','NVT'],{lang:f'/numerical-methods-atlas/{lang}/read/thermostats/' for lang in ['ja','en']})
add('equation-index',{'ja':'数式から探す','en':'Browse by equation'},['数式検索','方程式の一覧','equation index','formula'],{lang:'/numerical-methods-atlas/equations/?lang='+lang for lang in ['ja','en']})
index['scope']='chapter titles, section headings, model and method labels, glossary aliases, and public method records'
path.write_text(json.dumps(index,ensure_ascii=False,separators=(',',':'))+'\n')
module=ATLAS/'home-search.js';text=module.read_text()
marker=' // Public word-search entry\n'
if marker not in text:
    target=" const schedule=()=>"
    assert target in text
    text=text.replace(target,marker+" document.querySelectorAll('[data-atlas-word-search]').forEach(link=>link.addEventListener('click',event=>{event.preventDefault();input.focus({preventScroll:true});form.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth'});}));\n"+target,1)
text=re.sub(r"new URL\('home-search-index[.]json(?:[?]v=[a-f0-9]+)?',import.meta.url\)","new URL('home-search-index.json?v="+hashlib.sha256(path.read_bytes()).hexdigest()[:12]+"',import.meta.url)",text)
old='score}];'
new="score,url:/^\\/numerical-methods-atlas\\/[a-z0-9/?=.-]+$/.test(entry.routes?.[locale]||'')&&!entry.routes[locale].includes('..')?entry.routes[locale]:null}];"
if old in text:text=text.replace(old,new)
assert new in text,'Review upstream search result shape'
text=text.replace("a.href=readingURL(new URL('.',import.meta.url),result.id,result.locale,result.section)","a.href=result.url||readingURL(new URL('.',import.meta.url),result.id,result.locale,result.section)")
text=text.replace('該当する章がありません。','該当する項目がありません。').replace('No chapters match.','No entries match.')
text=text.replace('`${n}章が該当${n>m?`（上位${m}章を表示）`', '`${n}件が該当${n>m?`（上位${m}件を表示）`')
text=text.replace("`${n} matching chapter${n===1?'':'s'}", "`${n} matching entr${n===1?'y':'ies'}")
module.write_text(text)
# Version the changed module dependency; the purpose builder versions its parent.
overview=ATLAS/'home-overview.js';text=overview.read_text()
text=re.sub(r"from './home-search[.]js(?:[?]v=[a-f0-9]+)?'","from './home-search.js?v="+hashlib.sha256(module.read_bytes()).hexdigest()[:12]+"'",text)
overview.write_text(text)
print('Built atlas-local search:',len(index['entries']),'chapter/resource entries.')
