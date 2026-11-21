#!/usr/bin/env python3
"""Generate stable, bilingual human and machine routes from one method catalog."""
from pathlib import Path
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'numerical-methods-atlas'
ORIGIN='https://hrkoyama.github.io'
DATA=json.loads((ROOT/'catalog/atlas-methods.json').read_text())
METHODS=DATA['methods']
# Remove obsolete generated records when the editorial catalog excludes a topic.
active_ids={x['id'] for x in METHODS}
for directory in (ATLAS/'methods').glob('*'):
    if directory.is_dir() and directory.name not in active_ids:
        assert {p.name for p in directory.iterdir()} <= {'index.html','index.json','index.md'},directory
        for p in directory.iterdir():p.unlink()
        directory.rmdir()
existing_count=sum(x['status']!='planned' for x in METHODS)
example_count=sum(x['status']=='educational-example' for x in METHODS)
reading_count=sum(x['status']=='reading-only' for x in METHODS)
planned_count=sum(x['status']=='planned' for x in METHODS)
CODE=DATA['code_base']
EDITION=DATA['code_edition']
release=ROOT/CODE.lstrip('/')
verification=json.loads((release/'verification.json').read_text())
archive='atlas-code-'+EDITION+'.zip'
archive_hash=hashlib.sha256((release/archive).read_bytes()).hexdigest()
assert archive_hash==verification['archive_sha256']
manifest=json.loads((release/'source-manifest.json').read_text())
module_count=sum(name.startswith('numart/') and name.endswith('.py') for name in manifest['files'])
test_count=sum(name.startswith('tests/test_') and name.endswith('.py') for name in manifest['files'])
archive_mb=f'{(release/archive).stat().st_size/1_000_000:.1f}'
assert verification['failures']==verification['errors']==0
for name,digest in manifest['files'].items():
    assert hashlib.sha256((release/name).read_bytes()).hexdigest()==digest,name
ATOMS=json.loads((ROOT/'catalog/atlas-quantum-examples.json').read_text())
ACODE=ATOMS['code_base']
ABASE=ROOT/ACODE.lstrip('/')
AVER=json.loads((ABASE/'verification.json').read_text())
AHASH=hashlib.sha256((ABASE/ATOMS['archive']).read_bytes()).hexdigest()
assert AHASH==AVER['archive_sha256'] and AVER['failures']==AVER['errors']==0
ACASES={x['id']:x for x in ATOMS['cases']}
esc=html.escape
STATUS={'educational-example':{'ja':'教育用例・関連コードあり','en':'Educational example / related code'},'reading-only':{'ja':'解説あり・専用実装なし','en':'Reading only / no dedicated implementation'},'planned':{'ja':'Under construction / 収録予定','en':'Under construction / planned'}}
def status(x,lang):
    if x['status']=='planned' and x['reading']:
        return '比較解説あり・実装予定' if lang=='ja' else 'Comparative reading / implementation planned'
    return STATUS[x['status']][lang]
def link(url,label):return '<a href="'+esc(url)+'">'+esc(label)+'</a>'
def page(title_ja,title_en,url,sections,structured=None):
    metadata='' if structured is None else '<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title data-page-title-ja="{esc(title_ja)} | 数値計算法アトラス" data-page-title-en="{esc(title_en)} | Numerical Methods Atlas">{esc(title_ja)} | 数値計算法アトラス</title>
<meta name="description" content="{esc(title_ja)}：位置付け、解説、コード、検証、一次文献と実装状況。"><link rel="canonical" href="{ORIGIN+url}">
<link rel="stylesheet" href="/styles/atlas-resources.css?v={hashlib.sha256((ROOT/'styles/atlas-resources.css').read_bytes()).hexdigest()[:12]}">{metadata}</head>
<body class="profile-page"><main class="profile-main atlas-resource-main" id="main">{sections}</main></body></html>'''
def write(path,text):
    p=ROOT/path.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def nav(lang):
    labels=['手法の見取り図','コード・入力・検証','解説章の目次'] if lang=='ja' else ['Method map','Code, inputs and checks','Reading chapters']
    return '<nav class="resource-nav" aria-label="Atlas resources">'+''.join(link(u,l) for u,l in zip(['/numerical-methods-atlas/methods/','/numerical-methods-atlas/code-and-data/',f'/numerical-methods-atlas/{lang}/read/'],labels))+'</nav>'
def public_record(x):
    url=ORIGIN+'/numerical-methods-atlas/methods/'+x['id']+'/'
    record={**x,'url':url,'json_url':url+'index.json','markdown_url':url+'index.md',
            'reading':{lang:ORIGIN+path for lang,path in x['reading'].items()},
            'code_urls':[ORIGIN+CODE+'numart/'+name+'.py' for name in x['code_modules']],
            'test_urls':[ORIGIN+CODE+'tests/'+name+'.py' for name in x['test_files']],
            'run_commands':['python -m pytest -q '+' '.join('tests/'+name+'.py' for name in x['test_files'])] if x['test_files'] else [],
            'run_from':'Extracted code edition directory' if x['code_modules'] else None,
            'code_base':ORIGIN+CODE,'code_edition':EDITION if x['code_modules'] else None}
    if x.get('quantum_examples'):
        record.update(code_urls=[ORIGIN+ACODE+f for f in ['atomic_radial.py','run.py']],test_urls=[ORIGIN+ACODE+'test_atomic_radial.py'],run_commands=[ATOMS['test_command'],ATOMS['run_command']],run_from='Extracted quantum-atoms edition directory',code_base=ORIGIN+ACODE,code_edition=ATOMS['edition'],code_verification=ORIGIN+ACODE+'verification.json',code_download=ORIGIN+ACODE+ATOMS['archive'],inputs=ORIGIN+ACODE+'inputs.json',results=ORIGIN+ACODE+'results/results.json',independent_reference=ORIGIN+ACODE+'reference-pyscf.json',code_examples=[{**ACASES[i],'reading':{l:ORIGIN+f'/numerical-methods-atlas/{l}/read/quantum-atoms/#{ACASES[i]["section"]}' for l in ['ja','en']}} for i in x['quantum_examples']])
    return record

sections=[]
for lang in ['ja','en']:
    ja=lang=='ja'
    intro=(f'方程式から手法、一次文献、実装と検証へ。既存{existing_count}項目をたどり、新しい分野は収録予定と区別して探せます。' if ja else f'Follow equations to methods, original references, implementations and checks. Browse {existing_count} existing entries and separately identified development candidates.')
    body='<section data-site-language="'+lang+'" lang="'+lang+'"><p class="eyebrow">NUMERICAL METHODS / OPEN RESEARCH RESOURCES</p><h1>'+('手法の見取り図' if ja else 'A map of numerical methods')+'</h1><p class="intro resource-lead">'+intro+'</p>'+nav(lang)
    body+='<p class="resource-summary">'+(f'既存{existing_count}項目のうち教育用例{example_count}・解説のみ{reading_count}、拡張候補{planned_count}。教育用例は完成した汎用ソルバーの数ではありません。公開コード配布版の既存検査は{verification["passed"]}件通過・{verification["skipped"]}件対象外です。' if ja else f'{existing_count} existing entries: {example_count} with scoped educational examples and {reading_count} reading-only. Another {planned_count} are development candidates. These are not counts of complete production solvers. The code edition passes {verification["passed"]} existing checks, with {verification["skipped"]} inapplicable cases skipped.')+'</p>'
    body+='<p>'+('幅広い数値計算を結ぶ拡張中の地図です。未収録の分野もあり、すべての手法や原論文を網羅するという意味ではありません。' if ja else 'An expanding cross-field map, with gaps still to fill; not a claim to exhaust every method or original paper.')+'</p>'
    body+='<p><strong>'+esc(DATA['editorial_policy']['title'][lang])+':</strong> '+esc(DATA['editorial_policy']['statement'][lang])+'</p>'
    body+='<p>'+link('index.json','手法台帳 / JSON' if ja else 'Method registry / JSON')+' · '+link('/catalog/atlas-methods.json','正本データ' if ja else 'Catalog source')+' · '+link('/using/','使い方と引用' if ja else 'Use and citation')+'</p>'
    body+='<nav class="resource-nav" aria-label="Method groups">'+''.join(link('#'+g['id']+'-'+lang,g[lang]) for g in DATA['groups'])+'</nav>'
    for group in DATA['groups']:
        rows=[x for x in METHODS if x['group']['id']==group['id']]
        if not rows:continue
        body+='<section id="'+group['id']+'-'+lang+'"><h2>'+esc(group[lang])+'</h2><ul class="method-list">'
        for x in rows:
            body+='<li>'+link(x['id']+'/',x['name'][lang])+'<br><span class="resource-status">'+status(x,lang)+'</span><p>'+esc(x['summary'][lang])+'</p></li>'
        body+='</ul></section>'
    body+='</section>';sections.append(body)
write('/numerical-methods-atlas/methods/index.html',page('手法の見取り図','A map of numerical methods','/numerical-methods-atlas/methods/',''.join(sections)))
published={**DATA,'methods':[public_record(x) for x in METHODS],'code_release':{'download':ORIGIN+CODE+archive,'manifest':ORIGIN+CODE+'source-manifest.json','verification':ORIGIN+CODE+'verification.json','sha256':archive_hash}}
write('/numerical-methods-atlas/methods/index.json',json.dumps(published,ensure_ascii=False,indent=2)+'\n')

for x in METHODS:
    url='/numerical-methods-atlas/methods/'+x['id']+'/'
    sections=[]
    for lang in ['ja','en']:
        ja=lang=='ja';body='<section data-site-language="'+lang+'" lang="'+lang+'"><p class="eyebrow">'+esc(x['group'][lang])+'</p><h1>'+esc(x['name'][lang])+'</h1><p class="resource-status">'+status(x,lang)+'</p><p class="intro">'+esc(x['summary'][lang])+'</p>'+nav(lang)
        if x.get('aliases'):body+='<p>'+('別名・表記：' if ja else 'Other names: ')+esc(' / '.join(x['aliases']))+'</p>'
        if x['status']=='planned':
            body+='<h2>'+('次の成果物' if ja else 'Next deliverable')+'</h2><p>'+esc(x['next_deliverable'][lang])+'</p>'
        if x['reading']:
            reading=x['reading'].get(lang) or x['reading']['en']
            label=('解説章を読む' if lang in x['reading'] else '英語の解説を読む（日本語版未公開）') if ja else 'Read the chapter'
            body+='<h2>'+('解説と位置付け' if ja else 'Read the formulation')+'</h2><p>'+link(reading,label)+'</p>'
        if x.get('caution'):body+='<h2>'+('比較するときの注意' if ja else 'Comparison notes')+'</h2><p>'+esc(x['caution'][lang])+'</p>'
        if x.get('assumptions'):
            body+='<h2>'+('この例の前提' if ja else 'Assumptions for this example')+'</h2><ul>'+''.join('<li>'+esc(a)+'</li>' for a in (x.get('assumptions_ja',x['assumptions']) if ja else x['assumptions']))+'</ul>'
        if x.get('boundary_conditions'):
            body+='<p><strong>'+('境界条件' if ja else 'Boundaries')+':</strong> '+esc(x.get('boundary_conditions_ja',x['boundary_conditions']) if ja else x['boundary_conditions'])+'</p><p><strong>'+('単位系' if ja else 'Units')+':</strong> '+esc(x.get('units_ja',x['units']) if ja else x['units'])+'</p>'
        if x['code_modules']:
            body+='<h2>'+('関連コードと検証' if ja else 'Related code and checks')+'</h2><p>'+('この章に関係する実装と検査です。各ファイルが、その名前の手法のすべての変種を検証するわけではありません。' if ja else 'Chapter-related implementations and checks. These files do not verify every variant of the named method.')+'</p><ul class="resource-files">'
            body+=''.join('<li>'+link(CODE+'numart/'+name+'.py','numart/'+name+'.py')+'</li>' for name in x['code_modules'])
            body+=''.join('<li>'+link(CODE+'tests/'+name+'.py','tests/'+name+'.py')+'</li>' for name in x['test_files'])+'</ul><p>'+link('/numerical-methods-atlas/code-and-data/','一式の取得と実行手順' if ja else 'Download the complete edition and run it')+'</p>'
            if x['test_files']:body+='<pre><code>python -m pytest -q '+' '.join('tests/'+name+'.py' for name in x['test_files'])+'</code></pre>'
        if x.get('quantum_examples'):
            body+='<h2>'+('実行できる原子計算例' if ja else 'Runnable atomic examples')+'</h2><p>'+esc(x['example_scope'][lang])+'</p><ul>'
            for ident in x['quantum_examples']:
                c=ACASES[ident];body+='<li>'+link(f'/numerical-methods-atlas/{lang}/read/quantum-atoms/#{c["section"]}',c['name'][lang])+'</li>'
            body+='</ul><p>'+link(ACODE+ATOMS['archive'],'コード・入力・結果 ZIP' if ja else 'Code, inputs and results ZIP')+' · '+link(ACODE+'verification.json','独立展開の検証記録' if ja else 'Independent-extraction verification')+'</p><p>'+link(ACODE+'atomic_radial.py','Python solver')+' · '+link(ACODE+'test_atomic_radial.py','Tests')+' · '+link(ACODE+'inputs.json','Inputs JSON')+' · '+link(ACODE+'results/results.json','Results JSON')+' · '+link(ACODE+'reference-pyscf.json','Independent reference JSON')+'</p><pre><code>'+esc(ATOMS['test_command']+'\n'+ATOMS['run_command'])+'</code></pre>'
        if x.get('example'):
            example=x['example']
            body+='<h2>'+('固定入力から計算する' if ja else 'Run an explicit input')+'</h2><p>'+('192粒子の座標・質量を保存した入力を使い、ツリーと直接和の力を計算します。出力は誤差と検査を記録するJSON、粒子ごとの力を記録するCSVです。' if ja else 'Use explicit positions and masses for 192 particles. Compute tree and direct-sum forces, then export error/check records as JSON and particle forces as CSV.')+'</p><p>'+link(example['input'],'入力 / Input JSON')+' · '+link(example['runner'],'実行コード / Runner')+' · '+link(example['reference'],'参照出力 / Reference JSON')+' · '+link(example['forces'],'力のデータ / Force CSV')+'</p><pre><code>'+esc(example['command'])+'</code></pre>'
        body+='<h2>'+('適用範囲と残る作業' if ja else 'Scope and remaining work')+'</h2><p>'+esc(x['limitations'][lang])+'</p>'
        if x['metadata_review']['level'].startswith('chapter-linked') and not x.get('assumptions'):
            body+='<p>'+('この項目の条件・単位の個別整理は継続中です。空欄は適用条件がないことを意味しません。解説章とコードの条件を確認してください。' if ja else 'Method-record assumptions and units are still being curated. Missing fields do not mean unrestricted applicability; consult the chapter and code.')+'</p>'
        if x['references']:
            body+='<h2>'+('文献への入口' if ja else 'Reference entry points')+'</h2><ul>'+''.join('<li>'+link(r['url'],r.get('label',r['url']))+'</li>' for r in x['references'])+'</ul><p>'+('書誌や章の参照先の案内です。原文・式の確認範囲は元の章とJSONのscope欄を参照してください。' if ja else 'Bibliographic and chapter reference links. Consult the chapter and JSON scope fields for the extent of source review.')+'</p>'
        else:
            body+='<p>'+('一次文献の個別整理は今後の作業です。' if ja else 'Dedicated primary-reference curation remains to be completed.')+'</p>'
        body+='<p>'+link('index.json','この項目 / JSON' if ja else 'This record / JSON')+' · '+link('index.md','この項目 / Markdown' if ja else 'This record / Markdown')+' · '+link('/using/','引用と利用条件' if ja else 'Citation and reuse')+'</p></section>'
        sections.append(body)
    structured={'@context':'https://schema.org','@type':'LearningResource','name':x['name']['en'],'url':ORIGIN+url,'author':{'@type':'Person','name':'Hiroshi Koyama'},'isPartOf':{'@type':'WebSite','name':'An Atlas of Numerical Methods','url':ORIGIN+'/numerical-methods-atlas/'},'description':x['summary']['en'],'inLanguage':['ja','en']}
    write(url+'index.html',page(x['name']['ja'],x['name']['en'],url,''.join(sections),structured))
    record=public_record(x)
    write(url+'index.json',json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    md='# '+x['name']['en']+' / '+x['name']['ja']+'\n\nStatus: '+x['status']+'\n\n'+x['summary']['en']+'\n\n'+x['summary']['ja']+'\n\n'+x['limitations']['en']+'\n\n'
    if x.get('aliases'):md+='Other names: '+', '.join(x['aliases'])+'\n\n'
    if x.get('caution'):md+='Comparison notes: '+x['caution']['en']+'\n\n'+x['caution']['ja']+'\n\n'
    md+='\n'.join('- Reading ('+lang+'): '+ORIGIN+u for lang,u in x['reading'].items())+'\n\n'
    md+='\n'.join('- Code: '+ORIGIN+CODE+'numart/'+name+'.py' for name in x['code_modules'])+'\n\n'
    md+='\n'.join('- Reference: '+r['url']+' — '+r['scope'] for r in x['references'])+'\n\n'
    if x.get('quantum_examples'):md+='Scoped example: '+x['example_scope']['en']+'\n\n'+json.dumps(record['code_examples'],ensure_ascii=False,indent=2)+'\n\nDownload: '+record['code_download']+'\nVerification: '+record['code_verification']+'\nSource: '+record['code_urls'][0]+'\nResults: '+record['results']+'\nCommands (from extracted atomic edition):\n\n'+ '\n'.join(record['run_commands'])+'\n\n'
    if x.get('next_deliverable'):md+='Next: '+x['next_deliverable']['en']+'\n\n'
    if x.get('example'):md+='Runnable example:\n\n'+json.dumps(x['example'],ensure_ascii=False,indent=2)+'\n\n'
    md+='Source: '+ORIGIN+url+'\nEdition and terms: '+ORIGIN+'/numerical-methods-atlas/code-and-data/\n'
    write(url+'index.md',md)

sections=[]
for lang in ['ja','en']:
    ja=lang=='ja'
    body='<section data-site-language="'+lang+'" lang="'+lang+'"><p class="eyebrow">CODE EDITION '+EDITION+'</p><h1>'+('コード・入力・検証を取得する' if ja else 'Get code, inputs and verification')+'</h1><p class="intro">'+(f'{module_count}個のPythonモジュール、{test_count}個の検査ファイル、検査に必要な保存データをまとめた教育用配布版です。認証なしで取得できます。' if ja else f'An educational edition with {module_count} Python modules, {test_count} test files and the stored data required by the tests. No authentication is needed.')+'</p>'+nav(lang)
    body+='<aside class="resource-summary"><h2>'+('新しい原子計算の配布版' if ja else 'Separate atomic calculation edition')+'</h2><p>'+esc(ATOMS['scope'][lang])+'</p><p>'+link(f'/numerical-methods-atlas/{lang}/read/quantum-atoms/','水素型原子・Heの結果と実行手順' if ja else 'Hydrogenic/He results and reproduction')+' · '+link(ACODE+ATOMS['archive'],'Quantum atoms ZIP')+' · '+link(ACODE+'verification.json',str(AVER['passed'])+' checks passed / verification')+'</p></aside>'
    body+='<p>'+link(CODE+archive,f'コード一式を取得 / ZIP（約{archive_mb} MB）' if ja else f'Download code edition / ZIP (about {archive_mb} MB)')+' · '+link(CODE+'source-manifest.json','ファイル目録・SHA-256 / Manifest')+' · '+link(CODE+'verification.json','実行した検証の記録 / Verification')+'</p>'
    body+='<h2>'+('実行する' if ja else 'Run the examples')+'</h2><p>'+('ZIPを展開し、そのフォルダでPythonの仮想環境を作成・有効化してから実行してください。Python 3.12で配布版を検証しました。' if ja else 'Extract the ZIP, create and activate a Python virtual environment, then run these commands from the extracted folder. The edition was checked with Python 3.12.')+'</p><pre><code>python -m pip install -r requirements.txt\npython -m pytest -q\npython -m numart.cli --help</code></pre>'
    body+='<p>'+('小さな重力の検査から始める場合：' if ja else 'Start with a small gravity check:')+'</p><pre><code>python -m pytest -q tests/test_particle_gravity.py</code></pre>'
    body+='<p>'+link('/numerical-methods-atlas/methods/barnes-hut/','192粒子の固定入力を使い、JSONとCSVを出力する例' if ja else 'Run 192 explicitly specified particles and export JSON and CSV')+'</p>'
    body+='<h2>'+('検証した範囲' if ja else 'Verified scope')+'</h2><p>'+(f'ZIPを独立したフォルダに展開し、同梱ファイルだけで既存検査を実行しました。{verification["passed"]}件通過、適用対象外{verification["skipped"]}件、失敗0件です。これは全手法の汎用性や原論文の全図の再現を保証するものではありません。' if ja else f'The ZIP was extracted into an independent directory and checked using packaged files: {verification["passed"]} passed, {verification["skipped"]} inapplicable cases skipped, 0 failed. This does not establish general applicability or reproduction of every original figure.')+'</p>'
    body+='<p>'+('Barnes–Hutの孤立・軟化重力と、周期FFT PMは異なる境界問題です。この配布版に専用のEwald・PME・SPME・量子化学・DFTソルバーは含まれません。' if ja else 'Isolated softened Barnes–Hut gravity and periodic FFT PM are different boundary problems. No dedicated Ewald, PME, SPME, quantum-chemistry or DFT solver is included in this edition.')+'</p>'
    body+='<h2>'+('版と利用条件' if ja else 'Version and reuse')+'</h2><p class="resource-files">SHA-256: <code>'+archive_hash+'</code></p><p>'+('コード版・入力条件・原論文・参照URLを計算記録に残してください。自作実装コードはMIT、保存データ・本文・図は別条件です。' if ja else 'Retain the code edition, inputs, original method papers and source URL. Original implementation code is MIT; stored data, prose and figures have separate terms.')+'</p><p>'+link(CODE+'LICENSE','MIT License')+' · '+link(CODE+'LICENSING.md','適用範囲 / Licensing scope')+' · '+link('/using/','使い方・引用 / Use and cite')+'</p></section>'
    sections.append(body)
structured={'@context':'https://schema.org','@type':'SoftwareSourceCode','name':'Numerical Methods Atlas code edition '+EDITION,'codeRepository':'https://github.com/hrkoyama/hrkoyama.github.io/tree/main'+CODE,'programmingLanguage':'Python','softwareVersion':EDITION,'downloadUrl':ORIGIN+CODE+archive,'license':ORIGIN+CODE+'LICENSE','author':{'@type':'Person','name':'Hiroshi Koyama'}}
write('/numerical-methods-atlas/code-and-data/index.html',page('コード・入力・検証','Code, inputs and verification','/numerical-methods-atlas/code-and-data/',''.join(sections),structured))

# The old history remains private; normal navigation points to the public edition.
for p in ATLAS.rglob('*.html'):
    text=p.read_text()
    def replace(match):
        href,label=match.group(1),match.group(2)
        if not re.match(r'https://github[.]com/koyamarium/(?:numerical-methods-atlas|the-art-of-numerical-algorithms)(?:/|$)',href):return match.group(0)
        return link('/numerical-methods-atlas/code-and-data/','公開コード・データ / Public code and data')
    new=re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',replace,text,flags=re.S)
    if p==ATLAS/'index.html':
        marker='<!-- public-resource-entry -->'
        new=re.sub(r'<!-- public-resource-entry -->.*?<!-- /public-resource-entry -->','',new,flags=re.S)
        entry=marker+'<nav aria-label="Public atlas resources" style="display:flex;flex-wrap:wrap;gap:12px 24px;padding:16px 5%;border-bottom:1px solid #d2d3c8">'+link('/numerical-methods-atlas/methods/','手法の見取り図 / Method map')+link('/numerical-methods-atlas/code-and-data/','コード・入力・検証 / Code, inputs and checks')+'</nav><!-- /public-resource-entry -->'
        new=new.replace('<main',entry+'<main',1)
    if new!=text:p.write_text(new)
site_config=ATLAS/'site.json'
config=json.loads(site_config.read_text());config['repositoryUrl']=ORIGIN+'/numerical-methods-atlas/code-and-data/';config['legacyRepositoryUrl']=config['repositoryUrl'];site_config.write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
for p in ATLAS.glob('content*.json'):
    text=p.read_text()
    text=re.sub(r'https://github[.]com/koyamarium/(?:numerical-methods-atlas|the-art-of-numerical-algorithms)(?:/[^\s"<>\\)]*)?', ORIGIN+'/numerical-methods-atlas/code-and-data/', text)
    json.loads(text)
    p.write_text(text)
xml=ET.parse(ATLAS/'sitemap.xml');root=xml.getroot();existing={n.text for n in root.findall('.//{*}loc')};ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
for node in list(root):
    loc=node.find(ns+'loc')
    match=re.fullmatch(ORIGIN+r'/numerical-methods-atlas/methods/([^/]+)/',loc.text or '') if loc is not None else None
    if match and match.group(1) not in active_ids:root.remove(node)
for path in ['/numerical-methods-atlas/methods/','/numerical-methods-atlas/code-and-data/']+['/numerical-methods-atlas/methods/'+x['id']+'/' for x in METHODS]:
    if ORIGIN+path not in existing:ET.SubElement(ET.SubElement(root,ns+'url'),ns+'loc').text=ORIGIN+path
ET.register_namespace('',ns[1:-1]);xml.write(ATLAS/'sitemap.xml',encoding='utf-8',xml_declaration=True)
guide=ROOT/'llms.txt'
block=f'''\n## Method records and executable code

- [Method map]({ORIGIN}/numerical-methods-atlas/methods/): {existing_count} existing method/building-block entries and {planned_count} separately labeled development candidates. Planned entries have no dedicated solver or verification result.
- [Method registry / JSON]({ORIGIN}/numerical-methods-atlas/methods/index.json): Names, status, reading routes, chapter-related Python modules, tests, reference links and explicit metadata gaps. Each entry has a stable HTML URL, index.json and index.md. Null assumptions or boundaries mean not yet curated, not unrestricted applicability.
- Editorial scope: {DATA['editorial_policy']['statement']['en']}
- [Code, inputs and verification]({ORIGIN}/numerical-methods-atlas/code-and-data/): Public ZIP, file hashes, dependencies and standalone verification. Original implementation code is MIT within its scope; datasets and content retain separate terms.
- [Code edition manifest]({ORIGIN}{CODE}source-manifest.json): Direct file URLs are the public_base_url plus each listed path. The archive contains no Git history or private manuscripts.
- [Code edition verification]({ORIGIN}{CODE}verification.json): {verification['passed']} passed, {verification['skipped']} intentionally inapplicable cases skipped in an independent extraction. No Ewald/PME/SPME or DFT implementation is included in this edition.
- [Runnable atomic examples]({ORIGIN}/numerical-methods-atlas/en/read/quantum-atoms/): two hydrogenic/He problem families, {AVER["passed"]} independently extracted package checks passed; code, fixed inputs, CSV profiles, SCF histories and PySCF reference results. [Atomic source manifest]({ORIGIN}{ACODE}source-manifest.json) and [verification]({ORIGIN}{ACODE}verification.json). Only spherical 1s² HF and Dirac exchange-only LDA for He; not general molecular or periodic DFT.
- [Quantum chemistry and DFT]({ORIGIN}/numerical-methods-atlas/en/read/quantum-chemistry/): {sum(x['group']['id']=='quantum' for x in METHODS)} bilingual introductory topics, primary references, representative formulas and scoped hydrogenic/helium calculations and explicitly pending molecular/periodic checks. Canonical text and references: /catalog/atlas-quantum.json. Atlas-based specialist AI is deferred to 2027 or later in /catalog/atlas-work-queue.json.
'''
text=guide.read_text()
text=re.sub(r'\n## Method records and executable code\n.*?(?=\n## |\Z)',lambda _:block,text,flags=re.S) if '\n## Method records and executable code\n' in text else text+block
guide.write_text(text)
print(f'Built {len(METHODS)} method records, a public map and code download guide.')
