import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {configureLocale} from '../numerical-methods-atlas/i18n.js';
import {atlasPurpose,atlasMetrics} from '../numerical-methods-atlas/atlas-purpose.js';
const root=new URL('../',import.meta.url);
const read=p=>readFileSync(new URL(p,root),'utf8');
const coverage=JSON.parse(read('numerical-methods-atlas/coverage.json'));

test('the three browse routes are available in both languages before the purpose text',()=>{
  const copy=JSON.parse(read('catalog/atlas-purpose.json'));
  for(const lang of ['ja','en']){
    configureLocale({},lang);const html=atlasPurpose();
    assert.equal((html.match(/class="atlas-way"/g)||[]).length,3);
    assert.ok(html.indexOf('atlas-ways')<html.indexOf('atlas-purpose'));
    for(const item of copy[lang].browse)assert.ok(html.includes(item.title));
    assert.ok(html.includes('/numerical-methods-atlas/equations/?lang='+lang));
    assert.ok(html.includes('/numerical-methods-atlas/?lang='+lang+'#/gallery'));
    assert.ok(html.includes('data-atlas-word-search'));
  }
});
test('prominent counts use the atlas-wide problem inventory, with scoped wave cases retained',()=>{
  const inventory=JSON.parse(read('numerical-methods-atlas/test-cases/index.json'));
  assert.equal(coverage.counts.test_problems,inventory.problems.length);
  assert.ok(coverage.counts.test_problems>coverage.counts.gallery_cases);
  assert.equal(coverage.counts.gallery_cases,JSON.parse(read('numerical-methods-atlas/equation-gallery.json')).cases.length);
  assert.equal(coverage.counts.methods,coverage.items.filter(x=>x.kind==='method').length);
  assert.equal(coverage.counts.equations,coverage.items.filter(x=>x.kind==='equation').length);
  for(const lang of ['ja','en']){
    configureLocale({},lang);const html=atlasMetrics();
    for(const key of ['methods','papers','equations','test_problems'])assert.ok(html.includes('<strong>'+coverage.counts[key]+'</strong>'));
    assert.ok(html.includes('/numerical-methods-atlas/test-cases/'));
    assert.equal((html.match(/<a href=/g)||[]).length,4);
  }
});
test('equation records link to existing chapters in both languages and expose a matching public index',()=>{
  const source=JSON.parse(read('catalog/atlas-equations.json'));
  const published=JSON.parse(read('numerical-methods-atlas/equations/index.json'));
  const html=read('numerical-methods-atlas/equations/index.html');
  assert.equal(new Set(source.equations.map(x=>x.id)).size,source.equations.length);
  assert.equal(published.equations.length,source.equations.length);
  for(const x of source.equations){
    assert.ok(x.formula.length&&x.note.ja&&x.note.en);
    for(const lang of ['ja','en'])assert.ok(existsSync(new URL(`numerical-methods-atlas/${lang}/read/${x.chapter}/index.html`,root)));
  }
  assert.equal((html.match(/class="equation-entry"/g)||[]).length,2*source.equations.length);
  assert.ok(html.includes('全'+coverage.counts.equations+'方程式・モデル'));
});
