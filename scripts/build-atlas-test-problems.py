#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish the atlas-wide, deduplicated test-problem inventory with checked evidence."""
import ast
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ATLAS=ROOT/'numerical-methods-atlas'
ORIGIN='https://hrkoyama.github.io'
ROUTE='/numerical-methods-atlas/test-cases/'
source=ROOT/'catalog/atlas-test-problems.json'
data=json.loads(source.read_text())
problems=data['problems']
assert len({x['id'] for x in problems})==len(problems)
counts=Counter(x['group'] for x in problems)
availability=Counter(x['availability'] for x in problems)
assert all(x['group'] in {g['id'] for g in data['groups']} for x in problems)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipts={source.relative_to(ROOT).as_posix():digest(source)}
for problem in problems:
    assert problem['evidence']
    assert (ATLAS/'en/read'/problem['chapter']/'index.html').is_file(),problem['id']
    for e in problem['evidence']:
        path=(ROOT/e['path']).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(),e
        receipts[e['path']]=digest(path)
        if 'python_symbol' in e:
            tree=ast.parse(path.read_text())
            assert e['python_symbol'] in {n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)},e
        elif 'json_pointer' in e:
            value=json.loads(path.read_text())
            for part in e['json_pointer'].split('/')[1:]:
                part=part.replace('~1','/').replace('~0','~')
                value=value[int(part)] if isinstance(value,list) else value[part]
            if e.get('where'):
                assert isinstance(value,list) and any(all(row.get(k)==v for k,v in e['where'].items()) for row in value),e
        else:
            assert e.get('artifact')=='image' and path.suffix=='.png',e
        if problem['availability']=='verified-code-check':assert 'python_symbol' in e
code_data=json.loads((ROOT/'catalog/atlas-methods.json').read_text())
edition=code_data['code_base']
verification=json.loads((ROOT/edition.lstrip('/')/'verification.json').read_text())
assert verification['failures']==verification['errors']==0
total=len(problems)
summary={'test_problems':total,'saved_test_problems':availability['saved-output'],'code_test_problems':availability['verified-code-check'],'groups':dict(counts)}
public={**data,'url':ORIGIN+ROUTE,'counts':summary,'source_sha256':receipts,'code_edition':code_data['code_edition'],'code_verification':ORIGIN+edition+'verification.json'}
for x in public['problems']:
    x['reading']={}
    for lang in ['ja','en']:
        available=lang if (ATLAS/lang/'read'/x['chapter']/'index.html').is_file() else 'en'
        x['reading'][lang]=ORIGIN+f'/numerical-methods-atlas/{available}/read/'+x['chapter']+'/'
    x['url']=ORIGIN+ROUTE+'#'+x['id']
    x['run_commands']=['python -m pytest -q tests/'+Path(e['path']).name+' -k '+e['python_symbol'] for e in x['evidence'] if 'python_symbol' in e]
dest=ROOT/ROUTE.lstrip('/');dest.mkdir(parents=True,exist_ok=True)
(dest/'index.json').write_text(json.dumps(public,ensure_ascii=False,indent=2)+'\n')
esc=html.escape
def link(url,label):return '<a href="'+esc(url)+'">'+esc(label)+'</a>'
sections=[]
for lang in ['ja','en']:
    ja=lang=='ja'
    body='<section data-site-language="'+lang+'" lang="'+lang+'"><p class="eyebrow">ATLAS-WIDE TEST PROBLEMS / '+data['reviewed_on']+'</p><h1>'+(f'テスト計算：{total}問題' if ja else f'{total} independent test problems')+'</h1>'
    body+='<p class="intro">'+('波形ギャラリーだけでなく、アトラス全体の時間発展・境界値・重力・関数近似・代数問題を集計しました。' if ja else 'An atlas-wide inventory of time evolution, boundary-value, gravity, approximation and algebraic problems, extending beyond the wave-profile gallery.')+'</p>'
    status_ja=f'保存データ・結果図がある問題{availability["saved-output"]}件。'
    status_en=f'{availability["saved-output"]} problems have saved results or figures.'
    if availability['verified-code-check']:
        status_ja+=f'検証済み公開コードの問題{availability["verified-code-check"]}件。両方がある場合は前者に1回だけ数えます。'
        status_en+=f' {availability["verified-code-check"]} more are available as verified public-code checks. A problem with both is counted once in the first group.'
    body+='<p class="resource-summary">'+(status_ja if ja else status_en)+'</p>'
    body+='<nav class="resource-nav">'+link('/numerical-methods-atlas/','アトラスの冒頭' if ja else 'Atlas home')+link('/numerical-methods-atlas/gallery/?lang='+lang,'画像ギャラリー' if ja else 'Computed gallery')+link('/numerical-methods-atlas/code-and-data/','コード・実行手順' if ja else 'Code and run instructions')+link('index.json','問題台帳 / JSON' if ja else 'Problem inventory / JSON')+'</nav>'
    body+='<h2>'+('数え方' if ja else 'Counting rules')+'</h2><p>'+esc(data['policy'][lang])+'</p>'
    body+='<p>'+('既存の波形テスト9ケースはこの総数に含みます。自動検査411件の件数、画像数、実行回数とは別です。各問題の適用範囲と失敗例はリンク先に残しており、すべての手法がすべての問題を解けるという意味ではありません。保存データの再集計に加え、9問題は公開コードを固定条件で実行して結果と画像を追加しました。全問題の再実行ではありません。' if ja else 'The nine wave-profile cases are included in this total. Problems are distinct from the 411 automated checks, images and solver runs. Linked sources retain method-specific scope and failure cases; not every method solves every problem. The existing material is recounted, and nine problems have new fixed-input public-code runs with saved results and images. This is not a full numerical rerun.')+'</p>'
    body+='<nav class="resource-nav">'+''.join(link('#'+g['id']+'-'+lang,g[lang]+' ('+str(counts[g['id']])+')') for g in data['groups'])+'</nav>'
    for g in data['groups']:
        body+='<section><h2 id="'+g['id']+'-'+lang+'">'+esc(g[lang])+' — '+str(counts[g['id']])+'</h2><ul class="method-list">'
        for x in problems:
            if x['group']!=g['id']:continue
            label=('保存結果あり' if x['availability']=='saved-output' else '公開コードの検証問題') if ja else ('Saved results' if x['availability']=='saved-output' else 'Verified code check')
            ident=x['id'] if ja else x['id']+'-en'
            reading_label=('問題定義・解説' if '/ja/' in x['reading'][lang] else '英語の解説（日本語版未公開）') if ja else 'Problem definition and reading'
            body+='<li id="'+ident+'"><h3>'+esc(x['name'][lang])+'</h3><span class="resource-status">'+label+'</span><p>'+link(x['reading'][lang],reading_label)+'</p><details><summary>'+('計算データ・検証コードの根拠' if ja else 'Result and code evidence')+'</summary><ul>'
            for e in x['evidence']:
                label=Path(e['path']).name
                if e.get('python_symbol'):label+=' / '+e['python_symbol']
                if e.get('json_pointer'):label+=' '+e['json_pointer']
                body+='<li>'+link('/'+e['path'],label)
                if e.get('where'):body+=' <code>'+esc(json.dumps(e['where'],ensure_ascii=False))+'</code>'
                body+='</li>'
            body+='</ul></details></li>'
        body+='</ul></section>'
    body+='<h2>'+('総数に加算しないもの' if ja else 'Not added to the total')+'</h2><ul>'+''.join('<li>'+esc(x)+'</li>' for x in data['excluded_examples'][lang])+'</ul><p>'+link('/using/','利用・引用' if ja else 'Use and citation')+'</p></section>'
    sections.append(body)
style='/styles/atlas-resources.css?v='+digest(ROOT/'styles/atlas-resources.css')[:12]
document='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title data-page-title-ja="テスト計算の全体一覧 | 数値計算法アトラス" data-page-title-en="Test-problem inventory | Numerical Methods Atlas">テスト計算の全体一覧 | 数値計算法アトラス</title><meta name="description" content="アトラス全体の重複を除いたテスト計算の問題一覧。Problem definitions, saved results and verified public-code checks."><link rel="canonical" href="'+ORIGIN+ROUTE+'"><link rel="stylesheet" href="'+style+'"></head><body class="profile-page"><main id="main" class="profile-main atlas-resource-main">'+''.join(sections)+'</main></body></html>\n'
(dest/'index.html').write_text(document)
for path in [ATLAS/'coverage.json',ATLAS/'assets/site-coverage.json']:
    coverage=json.loads(path.read_text())
    coverage['counts'].update({k:v for k,v in summary.items() if k!='groups'})
    coverage['policy']['test_problems']=data['policy']['en']
    coverage['test_inventory']={'url':ORIGIN+ROUTE,'json_url':ORIGIN+ROUTE+'index.json','catalog':'catalog/atlas-test-problems.json','reviewed_on':data['reviewed_on']}
    path.write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
# The original nine-case statistic remains available under its scoped JSON key.
module=ATLAS/'coverage.js';text=module.read_text()
old="{n:c.gallery_cases,label:'Equation-gallery cases',note:`${c.gallery_equations} equation families · saved numerical profiles`,href:'#/equations',className:''}"
new="{n:c.test_problems,label:currentLanguage()==='ja'?'テスト計算':'Test problems',note:currentLanguage()==='ja'?'全分野の独立問題・重複を除く':'Independent problems across all atlas domains',href:'/numerical-methods-atlas/test-cases/',className:''}"
if old in text:text=text.replace(old,new)
assert new in text,'Review upstream coverage highlights'
module.write_text(text)
app=ATLAS/'app.js';text=app.read_text()
text=re.sub(r"from './coverage[.]js(?:[?]v=[a-f0-9]+)?'","from './coverage.js?v="+digest(module)[:12]+"'",text)
text=re.sub(r"'coverage[.]json(?:[?]v=[a-f0-9]+)?'","'coverage.json?v="+digest(ATLAS/'coverage.json')[:12]+"'",text)
app.write_text(text)
path=ATLAS/'sitemap.xml';xml=ET.parse(path);root=xml.getroot();ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
if ORIGIN+ROUTE not in {x.text for x in root.findall('.//{*}loc')}:ET.SubElement(ET.SubElement(root,ns+'url'),ns+'loc').text=ORIGIN+ROUTE
ET.register_namespace('',ns[1:-1]);xml.write(path,encoding='utf-8',xml_declaration=True)
guide=ROOT/'llms.txt';text=guide.read_text();line=f'- [Atlas-wide test-problem inventory]({ORIGIN}{ROUTE}): {total} deduplicated numerical problems with evidence, counting rules and JSON; not a count of solver runs or automated assertions.\n'
text=re.sub(r'^- \[Atlas-wide test-problem inventory\].*\n?','',text,flags=re.M);guide.write_text(text.rstrip()+'\n'+line)
print(json.dumps(summary,ensure_ascii=False))
