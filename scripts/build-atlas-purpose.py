#!/usr/bin/env python3
"""Retain the bilingual public purpose statement through upstream site imports."""
from pathlib import Path
import hashlib
import html
import json
import re
from atlas_execution_discovery import load_discovery, entry_url, ENTRY_BASE

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'numerical-methods-atlas'
copy=json.loads((ROOT/'catalog/atlas-purpose.json').read_text())
policy=json.loads((ROOT/'catalog/atlas-methods.json').read_text())['editorial_policy']
coverage=json.loads((ATLAS/'coverage.json').read_text())
discovery=load_discovery(ROOT)
discovery_by_id={x['id']:x for x in discovery['examples']}
format_counts={**coverage['counts'],'execution_examples':len(discovery['examples'])}
def browse(lang):
    c=copy[lang]
    routes={'words':'/search/?lang='+lang,'equations':'/numerical-methods-atlas/equations/?lang='+lang,'pictures':'/numerical-methods-atlas/gallery/?lang='+lang}
    previews={'words':'<span aria-hidden="true">Aa / あ</span>','equations':'<span aria-hidden="true">∇²u = f</span>','pictures':'<img src="/numerical-methods-atlas/assets/field-fem-poisson.png" alt="" width="900" height="360" loading="lazy">'}
    cards=[]
    for x in c['browse']:
        attr=' data-atlas-word-search' if x['id']=='words' else ''
        cards.append('<a class="atlas-way" href="'+routes[x['id']]+'"'+attr+'><div class="atlas-way-preview '+('formula' if x['id']=='equations' else '')+'">'+previews[x['id']]+'</div><h3>'+html.escape(x['title'])+'</h3><p>'+html.escape(x['description'].format(**format_counts))+'</p><span class="atlas-way-arrow">'+html.escape(x['action'])+'</span></a>')
    return '<section class="page-width atlas-ways" aria-labelledby="atlas-ways-'+lang+'"><h2 id="atlas-ways-'+lang+'">'+html.escape(c['browse_title'])+'</h2><div class="atlas-way-grid">'+''.join(cards)+'</div></section>'
def metrics(lang):
    counts=coverage['counts'];c=copy[lang]['metrics']
    routes={key:'/numerical-methods-atlas/?lang='+lang+value for key,value in {'methods':'#/coverage?kind=method','papers':'#/references','equations':'#/coverage?kind=equation'}.items()}
    routes['test_problems']='/numerical-methods-atlas/test-cases/?lang='+lang
    result='<div class="summary-counts atlas-metrics">'
    for key in ['methods','papers','equations','test_problems']:
        result+='<a href="'+routes[key]+'"><strong>'+str(counts[key])+'</strong><span>'+html.escape(c[key]['label'])+'</span><small>'+html.escape(c[key]['note'].format(**counts))+'</small></a>'
    return result+'</div>'
def render(lang):
    c=copy[lang]
    links=[('/numerical-methods-atlas/methods/',c['map']),('/numerical-methods-atlas/code-and-data/',c['code']),('/using/',c['using']),(f'/numerical-methods-atlas/{lang}/read/quantum-chemistry/','量子化学・DFTの見取り図' if lang=='ja' else 'Quantum chemistry & DFT')]
    return browse(lang)+'<section class="page-width atlas-purpose" aria-labelledby="atlas-purpose-title-'+lang+'"><h2 id="atlas-purpose-title-'+lang+'">'+html.escape(c['title'])+'</h2>'+''.join('<p>'+html.escape(p)+'</p>' for p in c['paragraphs'])+'<p><strong>'+html.escape(policy['title'][lang])+':</strong> '+html.escape(policy['statement'][lang])+'</p><nav aria-label="Atlas resources">'+''.join('<a href="'+url+'">'+html.escape(label)+'</a>' for url,label in links)+'</nav></section>'

def featured(lang):
    ja=lang=='ja'
    title='固定入力から、まず3つの計算を試す' if ja else 'Start with three fixed-input calculations'
    names={'poisson-2d-sine':('Poisson：解法と誤差','Poisson: solvers and errors'),'barnes-hut':('Barnes–Hut：近似力の精度','Barnes–Hut: approximate forces'),'helium-ground-state':('H・He：原子の計算','H / He: atomic calculations')}
    body='<section class="page-width atlas-featured-examples" aria-labelledby="atlas-examples-'+lang+'"><h2 id="atlas-examples-'+lang+'">'+title+'</h2><ul>'
    for ident in ['poisson-2d-sine','barnes-hut','helium-ground-state']:
        item=discovery_by_id[ident]
        outcome=item['outcome'][lang]
        if ident=='helium-ground-state':outcome='Hの解析解比較と、Heの閉殻HF・交換のみLDAを試す。' if ja else 'Compare H with analytic states and try closed-shell HF / exchange-only LDA for He.'
        body+='<li data-featured-example="'+ident+'"><h3>'+html.escape(names[ident][0 if ja else 1])+'</h3><p>'+html.escape(outcome)+'</p><a href="'+entry_url(ident,lang)+'">'+('入力・実行・検証へ →' if ja else 'Input, execution and checks →')+'</a>'
        if ident=='helium-ground-state':body+=' · <a href="'+entry_url('hydrogenic-atoms',lang)+'">'+('水素型原子' if ja else 'Hydrogenic atoms')+'</a>'
        body+='</li>'
    return body+'</ul><p><a href="'+ENTRY_BASE+'?lang='+lang+'">'+('代表15問題をすべて見る →' if ja else 'See all 15 representative examples →')+'</a></p></section>'

sections={lang:render(lang) for lang in copy}
module=ATLAS/'atlas-purpose.js'
module.write_text("// Generated from atlas purpose, coverage and verified execution discovery.\nimport {currentLanguage} from './i18n.js';\nconst sections="+json.dumps(sections,ensure_ascii=False)+";\nconst metrics="+json.dumps({lang:metrics(lang) for lang in copy},ensure_ascii=False)+";\nexport const atlasPurpose=()=>sections[currentLanguage()];\nexport const atlasMetrics=()=>metrics[currentLanguage()];\nconst featured="+json.dumps({lang:featured(lang) for lang in copy},ensure_ascii=False)+";\nexport const atlasExamples=()=>featured[currentLanguage()];\n")
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()[:12]
overview=ATLAS/'home-overview.js';text=overview.read_text()
text=re.sub(r"import \{atlasPurpose(?:,atlasMetrics)?(?:,atlasExamples)?\} from './atlas-purpose[.]js(?:[?]v=[a-f0-9]+)?';\n?",'',text)
marker=' ${homeSearchPage()}'
text=re.sub(r'^[ \t]*\$\{atlasPurpose\(\)\}[ \t]*\n(?:[ \t]*\n)*','',text,flags=re.M)
text=re.sub(r'^[ \t]*\$\{atlasExamples\(\)\}[ \t]*\n(?:[ \t]*\n)*','',text,flags=re.M)
assert text.count(marker)==1,'Review upstream homepage layout before adapting'
text="import {atlasPurpose,atlasMetrics,atlasExamples} from './atlas-purpose.js?v="+digest(module)+"';\n"+text.replace(marker,' ${atlasPurpose()}\n'+marker+'\n ${atlasExamples()}\n')
if '${atlasMetrics()}' not in text:
    text,count=re.subn(r'<div class="summary-counts">.*?</div><p class="flow">','${atlasMetrics()}<p class="flow">',text,count=1)
    assert count==1,'Review upstream coverage presentation'
overview.write_text(text)
app=ATLAS/'app.js';text=app.read_text()
text,count=re.subn(r"from './home-overview[.]js(?:[?]v=[a-f0-9]+)?'","from './home-overview.js?v="+digest(overview)+"'",text)
assert count==1,'Review upstream homepage module import'
app.write_text(text)
page=ATLAS/'index.html';text=page.read_text()
text=re.sub(r'<!-- atlas-purpose-fallback -->.*?<!-- /atlas-purpose-fallback -->','',text,flags=re.S)
fallback='<!-- atlas-purpose-fallback -->'+''.join('<div data-site-language="'+lang+'" lang="'+lang+'">'+metrics(lang)+sections[lang]+featured(lang)+'</div>' for lang in copy)+'<!-- /atlas-purpose-fallback -->'
text=text.replace('</main>',fallback+'</main>')
text=re.sub(r'<link rel="stylesheet" href="/styles/atlas-purpose.css(?:[?]v=[a-f0-9]+)?">\n?','',text)
text=text.replace('</head>','<link rel="stylesheet" href="/styles/atlas-purpose.css?v='+digest(ROOT/'styles/atlas-purpose.css')+'">\n</head>')
text=re.sub(r'<link rel="stylesheet" href="/styles/atlas-discovery.css(?:[?]v=[a-f0-9]+)?">\n?','',text)
text=text.replace('</head>','<link rel="stylesheet" href="/styles/atlas-discovery.css?v='+digest(ROOT/'styles/atlas-discovery.css')+'">\n</head>')
text=re.sub(r'src="app.js(?:[?]v=[a-f0-9]+)?"','src="app.js?v='+digest(app)+'"',text)
page.write_text(text)
# Keep the older roadmap wording consistent in both static and runtime editions.
replacements={
 '著者の要望によりAMRは保留で、今回の拡張に含みません。':'収録方針によりAMRは対象外です。',
 'AMRも引き続き保留します。':'AMRは収録対象外です。',
 'AMR is deferred at the author’s request; it is not part of this expansion.':'AMR is outside the editorial scope.',
 'and AMR remains deferred.':'and AMR is outside the editorial scope.'
}
def adapt_roadmap(text,lang):
    for old,new in replacements.items():text=text.replace(old,new)
    text=re.sub(r'<!-- atlas-scope -->.*?<!-- /atlas-scope -->','',text,flags=re.S)
    block='<!-- atlas-scope --><section><h2 id="atlas-editorial-scope">'+html.escape(policy['title'][lang])+'</h2><p>'+html.escape(policy['statement'][lang])+'</p></section><!-- /atlas-scope -->'
    return re.sub(r'(</h1>)',lambda m:m.group(1)+block,text,count=1)
for lang in ['ja','en']:
    roadmap=ATLAS/lang/'read/roadmap/index.html';roadmap.write_text(adapt_roadmap(roadmap.read_text(),lang))
for content in ATLAS.glob('content*.json'):
    data=json.loads(content.read_text());lang='ja' if '.ja.' in content.name else 'en'
    data['roadmap']['html']=adapt_roadmap(data['roadmap']['html'],lang)
    content.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
# A newly added chapter must also be discoverable through existing #/read links
# when a returning browser has a cached language document bundle.
versions={lang:digest(ATLAS/('content.'+lang+'.json')) for lang in ['ja','en']}
text=app.read_text()
text=re.sub(r'const atlasDocumentVersions = [^\n]+;\n','',text)
text=text.replace('const documentCache = new Map();','const atlasDocumentVersions = '+json.dumps(versions)+';\nconst documentCache = new Map();')
text=text.replace('fetch(`content.${language}.json`)','fetch(`content.${language}.json?v=${atlasDocumentVersions[language]}`)')
assert 'fetch(`content.${language}.json?v=${atlasDocumentVersions[language]}`)' in text
app.write_text(text)
text=page.read_text();text=re.sub(r'src="app.js(?:[?]v=[a-f0-9]+)?"','src="app.js?v='+digest(app)+'"',text);page.write_text(text)
print('Built bilingual atlas purpose statement for the live homepage and static fallback.')
