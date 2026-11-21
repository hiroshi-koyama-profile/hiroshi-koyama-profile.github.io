#!/usr/bin/env python3
"""Reapply the public research navigation after importing reviewed exhibits."""
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THERMAL = ROOT / 'the-art-of-thermal-instability'
esc = html.escape

def page(title, body, filename):
    url = 'https://hrkoyama.github.io/the-art-of-thermal-instability/' + filename
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · The Art of Thermal Instability</title>
<meta name="description" content="Published outcomes, reproducible code and explicit scientific limits for the thermal-instability archive.">
<link rel="canonical" href="{url}"><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="field-1965/exhibit.css">
</head><body data-content-language="en"><header><a class="brand" href="./">The Art of Thermal Instability</a><nav aria-label="Research resources"><a href="progress.html">Progress &amp; next questions</a><a href="code-and-data.html">Code &amp; data</a><a href="catalog.json">Paper catalog</a></nav></header>
<main class="exhibit" id="main">{body}</main><footer><a href="./#atlas">Paper atlas</a><a href="/using/">Use &amp; cite these resources</a><a href="/rights/">Rights &amp; AI policy</a></footer></body></html>'''

queue = json.loads((ROOT / 'catalog/thermal-work-queue.json').read_text())
(THERMAL / 'work-queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
sections = []
for state, label in [('published', 'Published outcomes'), ('planned', 'Next scientific questions'), ('deferred', 'Deferred until new evidence')]:
    entries = ''.join(f'<article id="{esc(x["id"])}"><h3><a href="{esc(x["url"])}">{esc(x["title"])}</a></h3><p><strong>{state.capitalize()}.</strong> {esc(x["outcome"])}</p></article>' for x in queue['items'] if x['state'] == state)
    sections.append(f'<section id="{state}"><h2>{label}</h2>{entries}</section>')
body = f'''<section class="hero"><p class="eyebrow">Public progress · reviewed {queue['reviewed_on']}</p><h1>Published results.<br>Bounded next questions.</h1>
<p class="intro">{esc(queue['current_focus'])}</p><p class="notice">This page is the public work record. Read the status and limits here without a GitHub account. Planned work has not been implemented; one scientific implementation is normally active at a time.</p>
<div class="downloads"><a href="work-queue.json">Work record / JSON</a><a href="code-and-data.html">Get code and data</a></div></section>''' + ''.join(sections) + '''
<section id="limits"><h2>Keep the scientific limits visible.</h2><p>Field1965 calculations are derived from the source equations; pointwise digitization is a separate task. Historical movie provenance is documented, but exact original run inputs and paper-figure matches remain unverified. The archive does not reproduce every result in every cataloged paper.</p><p>Specifications, implementations, numerical checks and historical agreement are separate milestones. See each exhibit for units, boundary conditions, source editions and unresolved questions.</p></section>
<section><h2>Further directions</h2><p>Small comparisons of reduced and compressible models, bounded front diagnostics, KI2000/2004, and analysis of available multidimensional outputs remain candidates. Full high-cost reruns are optional; no release date is assigned to these scientific extensions.</p></section>'''
(THERMAL / 'progress.html').write_text(page('Progress and next questions', body, 'progress.html'))

examples = [
    ('Field1965 / Figure2', 'field-1965/', ['reproduce.py', 'config.json', 'requirements.txt', 'figure-2.csv', 'validation.json'], 'python reproduce.py --output output', 'Source-equation calculation with independent numerical checks; not a pointwise digitization of the original figure.'),
    ('KI2002 / equilibrium and static potential', 'ki-2002/', ['README.md', 'equilibrium.py', 'reproduce.py', 'potential.py', 'config.json', 'config-potential.json', 'requirements.txt', 'equilibrium.csv', 'potential.csv', 'validation.json', 'validation-potential.json'], 'python reproduce.py --output output\npython potential.py --output output', 'Corrected analytic cooling fit and a static-front diagnostic; not a rerun of the original 2D simulation.'),
    ('Illustrative 2D condensation', 'ti-2d/', ['README.md', 'model.py', 'reproduce.py', 'config.json', 'requirements.txt', 'validation.json'], '', 'Enhanced conduction and deliberately limited model scope. Follow the README for the full run and the separate small checks.'),
]
cards = []
for title, prefix, names, command, scope in examples:
    names = [name for name in names if (THERMAL / prefix / name).is_file()]
    links = ' · '.join(f'<a href="{prefix}{esc(name)}">{esc(name)}</a>' for name in names)
    commands = f'<pre><code>python -m venv .venv\n# Activate the virtual environment for your shell.\npython -m pip install -r requirements.txt\n{esc(command)}</code></pre>' if command else ''
    cards.append(f'<section><h2><a href="{prefix}">{esc(title)}</a></h2><p>{esc(scope)}</p><p>{links}</p>{commands}<p>Save the linked Python files, configuration and requirements together. The exhibit and README remain authoritative for its full dependencies and execution scope.</p></section>')
gallery_note = '<p>The movie gallery preserves published media and provenance. Its original source-build workflow is not distributed here; a historical movie is not a reproducible simulation benchmark.</p>'
body = '''<section class="hero"><p class="eyebrow">Public research resources</p><h1>Code, inputs and evidence.</h1><p class="intro">Download the files directly from this site. No GitHub sign-in is needed. Each example states what was checked and what remains unresolved.</p></section>''' + ''.join(cards) + gallery_note + '''
<section><h2>Use, verify and cite</h2><p>Run downloaded code in your own isolated environment after inspection. Retain the source/configuration hashes in the validation records, and compare the reported quantities rather than only the appearance of a figure. See <a href="/using/">usage and citation guidance</a>.</p><p>Original implementation code is MIT within its stated scope. Data, prose, figures, movies and third-party sources have separate terms: <a href="LICENSING.md">licensing scope</a>, <a href="/rights/">site policy</a>. Linking a paper does not redistribute its full text.</p></section>'''
(THERMAL / 'code-and-data.html').write_text(page('Code and data', body, 'code-and-data.html'))

base = 'https://github.com/koyamarium/the-art-of-thermal-instability'
for p in THERMAL.rglob('*.html'):
    if p.name in ['progress.html', 'code-and-data.html']:
        continue
    source = p.read_text()
    def replace_link(match):
        href, text = match.group(1), match.group(2)
        if not href.startswith(base):
            return match.group(0)
        if '/issues/6' in href:
            target, label = '/the-art-of-thermal-instability/progress.html#kim-eigenfunctions', 'Public specification and status'
        elif '/issues' in href:
            target, label = '/the-art-of-thermal-instability/progress.html', 'Public progress'
        elif '/scripts/build_gallery.py' in href:
            target, label = '/the-art-of-thermal-instability/code-and-data.html', 'Available code and reproduction scope'
        else:
            target, label = '/the-art-of-thermal-instability/code-and-data.html', 'Code and data'
        return f'<a href="{target}">{label}</a>'
    source = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', replace_link, source, flags=re.S)
    if source != p.read_text():
        p.write_text(source)
audit = THERMAL / 'kim-kim-2013/source-audit.json'
audit.write_text(audit.read_text().replace(base + '/issues/6', 'https://hrkoyama.github.io/the-art-of-thermal-instability/progress.html#kim-eigenfunctions'))
xml = ET.parse(THERMAL / 'sitemap.xml')
root = xml.getroot()
existing = {node.text for node in root.findall('.//{*}loc')}
url = 'https://hrkoyama.github.io/the-art-of-thermal-instability/code-and-data.html'
if url not in existing:
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    ET.SubElement(ET.SubElement(root, ns + 'url'), ns + 'loc').text = url
    ET.register_namespace('', ns[1:-1])
    xml.write(THERMAL / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
print('Built public thermal progress, code/data guide and navigation.')
