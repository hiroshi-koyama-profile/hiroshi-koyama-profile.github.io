#!/usr/bin/env python3
"""Build the root sitemap from published canonical HTML, without private files."""
from pathlib import Path
from html.parser import HTMLParser
import os
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://hrkoyama.github.io'
class Head(HTMLParser):
    def __init__(self):
        super().__init__(); self.canonical = None; self.blocked = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href')
        if tag == 'meta' and a.get('name') == 'robots' and 'noindex' in a.get('content', ''): self.blocked = True
urls = set()
for parent, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'node_modules', 'scripts', 'docs'}]
    for name in files:
        if not name.endswith('.html') or name.startswith('google'): continue
        p = Path(parent) / name; head = Head(); head.feed(p.read_text())
        if head.blocked or not head.canonical: continue
        url = head.canonical
        if not url.startswith(ORIGIN + '/') or '?' in url or '#' in url: raise ValueError(url)
        urls.add(url)
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
tree = ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
for url in sorted(urls):
    item = ET.SubElement(tree, 'url'); ET.SubElement(item, 'loc').text = url
ET.indent(tree)
ET.ElementTree(tree).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
print(f'Built root sitemap: {len(urls)} canonical pages.')
