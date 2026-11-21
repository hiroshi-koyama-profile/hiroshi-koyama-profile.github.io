#!/usr/bin/env python3
"""Retain the bilingual public purpose statement through upstream site imports."""
from pathlib import Path
import hashlib
import html
import json
import re

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'numerical-methods-atlas'
copy=json.loads((ROOT/'catalog/atlas-purpose.json').read_text())
policy=json.loads((ROOT/'catalog/atlas-methods.json').read_text())['editorial_policy']
coverage=json.loads((ATLAS/'coverage.json').read_text())
def browse(lang):
    c=copy[lang]
    routes={'words':'/search/?lang='+lang,'equations':'/numerical-methods-atlas/equations/?lang='+lang,'pictures':'/numerical-methods-atlas/gallery/?lang='+lang}
    previews={'words':'<span aria-hidden="true">Aa / あ</span>','equations':'<span aria-hidden="true">∇²u = f</span>','pictures':'<img src="/numerical-methods-atlas/assets/field-fem-poisson.png" alt="" width="900" height="360" loading="lazy">'}
    cards=[]
    for x in c['browse']:
        attr=' data-atlas-word-search' if x['id']=='words' else ''
        cards.append('<a class="atlas-way" href="'+routes[x['id']]+'"'+attr+'><div class="atlas-way-preview '+('formula' if x['id']=='equations' else '')+'">'+previews[x['id']]+'</div><h3>'+html.escape(x['title'])+'</h3><p>'+html.escape(x['description'])+'</p><span class="atlas-way-arrow">'+html.escape(x['action'])+'</span></a>')
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
sections={lang:render(lang) for lang in copy}
module=ATLAS/'atlas-purpose.js'
module.write_text("// Generated from catalog/atlas-purpose.json and coverage.json.\nimport {currentLanguage} from './i18n.js';\nconst sections="+json.dumps(sections,ensure_ascii=False)+";\nconst metrics="+json.dumps({lang:metrics(lang) for lang in copy},ensure_ascii=False)+";\nexport const atlasPurpose=()=>sections[currentLanguage()];\nexport const atlasMetrics=()=>metrics[currentLanguage()];\n")
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()[:12]
overview=ATLAS/'home-overview.js';text=overview.read_text()
text=re.sub(r"import \{atlasPurpose(?:,atlasMetrics)?\} from './atlas-purpose[.]js(?:[?]v=[a-f0-9]+)?';\n?",'',text)
marker=' ${homeSearchPage()}'
text=text.replace(' ${atlasPurpose()}\n','')
assert text.count(marker)==1,'Review upstream homepage layout before adapting'
text="import {atlasPurpose,atlasMetrics} from './atlas-purpose.js?v="+digest(module)+"';\n"+text.replace(marker,' ${atlasPurpose()}\n'+marker)
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
fallback='<!-- atlas-purpose-fallback -->'+''.join('<div data-site-language="'+lang+'" lang="'+lang+'">'+metrics(lang)+sections[lang]+'</div>' for lang in copy)+'<!-- /atlas-purpose-fallback -->'
text=text.replace('</main>',fallback+'</main>')
text=re.sub(r'<link rel="stylesheet" href="/styles/atlas-purpose.css(?:[?]v=[a-f0-9]+)?">\n?','',text)
text=text.replace('</head>','<link rel="stylesheet" href="/styles/atlas-purpose.css?v='+digest(ROOT/'styles/atlas-purpose.css')+'">\n</head>')
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
