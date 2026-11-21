#!/usr/bin/env python3
"""Publish every independent test problem as a bilingual image-to-reading card.

No numerical runtime is needed: verify the saved scientific-preview receipts.
"""
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / 'numerical-methods-atlas'
DEST = ATLAS / 'gallery'
ORIGIN = 'https://hrkoyama.github.io'
ROUTE = '/numerical-methods-atlas/gallery/'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
esc = html.escape
inventory = json.loads((ATLAS / 'test-cases/index.json').read_text())
mapping = json.loads((ROOT / 'catalog/atlas-gallery.json').read_text())
manifest = json.loads((DEST / 'preview-manifest.json').read_text())
calculations = json.loads((DEST / 'calculations.json').read_text())
verification = json.loads((DEST / 'verification.json').read_text())
ids = [x['id'] for x in inventory['problems']]
for rows in [mapping['items'], manifest['items']]:
    assert len(rows) == len(ids) and {x['id'] for x in rows} == set(ids), 'Gallery must match every inventory ID exactly once'
assert manifest['calculations_sha256'] == sha(DEST / 'calculations.json')
assert set(calculations['cases']) == {x['id'] for x in mapping['items'] if x['kind'] == 'computed-preview'}
assert verification['failures'] == verification['errors'] == 0 and verification['passed'] > 0
receipts = {**manifest['source_sha256'], **verification['source_sha256']}
for path, digest in receipts.items():
    assert sha(ROOT / path) == digest, 'Regenerate previews or verification: ' + path
for name in ['preview-manifest.json', 'calculations.json', 'verification.json', '../test-cases/index.json']:
    path = (DEST / name).resolve()
    receipts[path.relative_to(ROOT).as_posix()] = sha(path)
visuals = {x['id']: x for x in manifest['items']}
inputs = {x['id']: x for x in mapping['items']}
items = []
for problem in inventory['problems']:
    image = visuals[problem['id']]
    path = (ROOT / image['image'].lstrip('/')).resolve()
    assert path.is_relative_to(ROOT) and sha(path) == image['image_sha256'], problem['id']
    # Dimension metadata is saved during authoring; normal refresh needs no Pillow.
    width, height = image['width'], image['height']
    assert width > 0 and height > 0
    if path.suffix == '.png':
        assert path.read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
        assert (width, height) == struct.unpack('>II', path.read_bytes()[16:24])
    else:
        assert path.suffix == '.webp'
    items.append({**problem, **image, 'visual_input': inputs[problem['id']], 'width': width, 'height': height,
                  'gallery_url': ORIGIN + ROUTE + '#' + problem['id'] + '-ja'})
counts = Counter(x['group'] for x in items)
source_labels = {
    'existing-figure': {'ja': '保存済みの結果図', 'en': 'Saved result figure'},
    'stored-data-plot': {'ja': '保存数値データを図示', 'en': 'Plot of saved numerical data'},
    'computed-preview': {'ja': '公開コードで新たに計算・図示', 'en': 'New run of the public code'},
}
groups = {x['id']: x for x in inventory['groups']}
def link(url, label):
    return '<a href="' + esc(url) + '">' + esc(label) + '</a>'
sections = []
for lang in ['ja', 'en']:
    ja = lang == 'ja'
    body = '<section data-site-language="' + lang + '" data-gallery lang="' + lang + '">'
    body += '<p class="eyebrow">NUMERICAL METHODS ATLAS · VISUAL INDEX</p><h1>' + ('絵から探す：全' + str(len(ids)) + 'のテスト計算' if ja else 'Browse by picture: all ' + str(len(ids)) + ' test problems') + '</h1>'
    body += '<p class="intro gallery-intro">' + ('波形、衝撃波、渦、重力場、境界値問題、時間積分、関数近似まで。画像を選ぶと、その問題の解説へ進みます。' if ja else 'Explore profiles, shocks, vortices, gravity, boundary-value problems, time integration and approximation. Select any image to open the corresponding reading.') + '</p>'
    body += '<nav class="resource-nav">' + ''.join(link(url, label) for url, label in [
        ('/numerical-methods-atlas/?lang=' + lang, 'アトラス冒頭' if ja else 'Atlas home'),
        ('/numerical-methods-atlas/equations/?lang=' + lang, '数式から探す' if ja else 'Browse by equation'),
        ('/numerical-methods-atlas/test-cases/?lang=' + lang, '問題台帳と数え方' if ja else 'Inventory and counting rules'),
        ('/numerical-methods-atlas/?lang=' + lang + '#/figures', '図版・比較ツール' if ja else 'Figures and comparison tools'),
    ]) + '</nav>'
    body += '<div class="gallery-tools"><label for="gallery-query-' + lang + '">' + ('問題名・現象で絞り込む（日英対応）' if ja else 'Filter by problem or phenomenon (Japanese / English)') + '</label><div class="gallery-search-row"><input id="gallery-query-' + lang + '" type="search" placeholder="' + ('例：Poisson、渦、衝撃波' if ja else 'e.g. Poisson, vortex, shock') + '"><button type="button" data-gallery-reset>' + ('絞り込みを解除' if ja else 'Reset filters') + '</button></div><div class="gallery-groups" role="group" aria-label="' + ('分野' if ja else 'Domain') + '">'
    body += '<button type="button" data-gallery-group="all" aria-pressed="true">' + ('すべて' if ja else 'All') + ' (' + str(len(ids)) + ')</button>'
    for g in inventory['groups']:
        body += '<button type="button" data-gallery-group="' + g['id'] + '" aria-pressed="false">' + esc(g[lang]) + ' (' + str(counts[g['id']]) + ')</button>'
    body += '</div><p class="gallery-count" data-gallery-count role="status" aria-live="polite">' + (f'{len(ids)} / {len(ids)} 問題を表示' if ja else f'Showing {len(ids)} of {len(ids)} problems') + '</p></div>'
    body += '<p class="gallery-note">' + (f'{len(ids)}は手法・格子・刻み違いを統合した問題数です。解の画像に加え、誤差・残差・収束の図も含みます。複数問題の共有図は説明に明記しています。9問題の追加計算に加え、原子計算2問題群も別配布版で実行・検証しています。' if ja else f'The {len(ids)} problems merge method, grid and time-step variants. Visuals include solutions, errors, residuals and convergence. Captions identify shared figures. Nine preview problems have new fixed-input runs; two atomic problem families also have a separately verified code edition.') + '</p><ul class="gallery-grid">'
    for x in items:
        search = ' '.join([x['id'], *x['name'].values(), *groups[x['group']].values(), *x['caption'].values(), x['chapter']])
        reading = x['reading'][lang]
        fallback = ja and '/en/read/' in reading
        body += '<li class="gallery-tile" id="' + x['id'] + '-' + lang + '" data-problem-id="' + x['id'] + '" data-group="' + x['group'] + '" data-search="' + esc(search) + '">'
        body += '<a class="gallery-image-link" href="' + esc(reading) + '" aria-label="' + esc(x['name'][lang] + ('の解説へ' if ja else ': open reading')) + '"><img src="' + esc(x['image']) + '" alt="' + esc(x['name'][lang] + ' — ' + x['caption'][lang]) + '" width="' + str(x['width']) + '" height="' + str(x['height']) + '" loading="lazy" decoding="async"></a>'
        body += '<div class="gallery-card-body"><p class="gallery-meta">' + esc(groups[x['group']][lang]) + '</p><h2>' + link(reading, x['name'][lang]) + '</h2><p>' + esc(x['caption'][lang]) + '</p><p class="gallery-meta">' + source_labels[x['source_kind']][lang] + (' · 英語の解説（日本語版未公開）' if fallback else '') + '</p><nav class="gallery-card-links">'
        body += link(reading, '解説へ →' if ja else 'Read →') + link('/numerical-methods-atlas/test-cases/?lang=' + lang + '#' + x['id'] + ('' if ja else '-en'), '条件・根拠' if ja else 'Conditions and evidence') + link(x['image'], '画像を拡大' if ja else 'Full-size image') + ''.join(link(e['guide'][lang], '実行・検証' if ja else 'Run and validate') for e in x.get('execution_examples',[])) + '</nav></div></li>'
    body += '</ul><p class="gallery-empty" data-gallery-empty hidden>' + ('該当する問題がありません。検索語や分野を変えてください。' if ja else 'No matching problems. Try another query or domain.') + '</p><p>'
    body += link('index.json', '画像・解説・出典の全件JSON' if ja else 'All images, readings and sources / JSON') + ' · ' + link('calculations.json', '新規9計算の入力・値・数値検査' if ja else 'Inputs, values and checks for the nine new runs') + ' · ' + link('verification.json', '追加の実行確認' if ja else 'Additional verification') + ' · ' + link('/scripts/render-atlas-gallery.py', '図の再生成スクリプト' if ja else 'Preview reproduction script')
    body += '</p><p>' + link('/using/?lang=' + lang, '利用・引用' if ja else 'Reuse and citation') + '</p></section>'
    sections.append(body)
doc = '<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title data-page-title-ja="絵から探す：58のテスト計算 | 数値計算法アトラス" data-page-title-en="Browse 58 test problems by picture | Numerical Methods Atlas">絵から探す：58のテスト計算 | 数値計算法アトラス</title><meta name="description" content="数値計算法アトラス全58問題の画像一覧。波形、衝撃波、渦、重力、Poisson問題、時間積分、関数近似から解説へ。A visual index of all 58 numerical test problems."><link rel="canonical" href="' + ORIGIN + ROUTE + '">'
for style in ['atlas-resources', 'atlas-gallery']:
    doc += '<link rel="stylesheet" href="/styles/' + style + '.css?v=' + sha(ROOT / 'styles' / (style + '.css'))[:12] + '">'
doc=doc.replace('58',str(len(ids)))
doc += '<script type="module" src="/atlas-gallery.mjs?v=' + sha(ROOT / 'atlas-gallery.mjs')[:12] + '"></script></head><body class="profile-page"><main id="main" class="profile-main atlas-resource-main atlas-gallery-main">' + ''.join(sections) + '</main></body></html>\n'
(DEST / 'index.html').write_text(doc)
(DEST / 'index.json').write_text(json.dumps({'schema_version': 1, 'url': ORIGIN + ROUTE, 'reviewed_on': mapping['reviewed_on'], 'scope': mapping['scope'], 'counts': {'test_problems': len(ids), 'groups': dict(counts), 'visual_sources': dict(Counter(x['source_kind'] for x in items))}, 'items': items, 'source_sha256': receipts}, ensure_ascii=False, indent=2) + '\n')

# Preserve the old route as an entrance to the complete index. Original visual
# experiments remain available under #/figures, including their comparison tools.
app = ATLAS / 'app.js'
text = app.read_text()
marker = " if(type==='gallery'){location.replace('/numerical-methods-atlas/gallery/?lang='+currentLanguage());return;}"
if marker not in text:
    target = " if(type==='read' && !documents[parts[1]]) {"
    assert target in text
    text = text.replace(target, marker + '\n' + target, 1)
text = re.sub(r'gallery,(?:figures:gallery,)+movies:moviesPage', 'gallery,figures:gallery,movies:moviesPage', text)
if 'figures:gallery' not in text:
    text = text.replace('methods:methodPage,gallery,', 'methods:methodPage,gallery,figures:gallery,', 1)
text = text.replace("gallery:'Numerical gallery',movies:", "gallery:'Numerical gallery',figures:'Figures and comparison tools',movies:")
assert 'figures:gallery' in text
app.write_text(text)
path = ATLAS / 'sitemap.xml'
xml = ET.parse(path); ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
if ORIGIN + ROUTE not in {x.text for x in xml.getroot().findall('.//{*}loc')}:
    ET.SubElement(ET.SubElement(xml.getroot(), ns + 'url'), ns + 'loc').text = ORIGIN + ROUTE
ET.register_namespace('', ns[1:-1]); xml.write(path, encoding='utf-8', xml_declaration=True)
guide = ROOT / 'llms.txt'
lines = [x for x in guide.read_text().splitlines() if not x.startswith('- [Atlas-wide visual test index]')]
guide.write_text('\n'.join(lines).rstrip() + '\n- [Atlas-wide visual test index](' + ORIGIN + ROUTE + '): all ' + str(len(ids)) + ' independent problems, one mapped visual each, bilingual readings, source receipts and JSON. Shared figures and newly computed results are labeled.\n')
print('Built complete visual index:', len(ids), 'problems.')
