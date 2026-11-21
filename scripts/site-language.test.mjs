import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const script=readFileSync(new URL('../site.js',import.meta.url),'utf8');
const implementation=script.match(/^  function languageURL\(language\) \{[\s\S]*?^  \}/m)?.[0];
assert.ok(implementation,'Review the shared language URL function');
function destination(href,language,ids,enabled=true,alternate=null){
  const location=new URL(href);
  const document={body:{dataset:{siteLanguageAnchors:enabled?'suffix':'',contentLanguage:alternate?'ja':''}},querySelector:()=>alternate?{href:alternate}:null,getElementById:id=>ids.includes(id)?{}:null};
  return runInNewContext(implementation+';languageURL(language).href',{document,location,language,URL});
}

test('language switching follows the same example in the opted-in execution guide',()=>{
  const base='https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/';
  const ids=['helium-ground-state-ja','helium-ground-state-en'];
  assert.equal(destination(base+'?lang=ja#helium-ground-state-ja','en',ids),base+'?lang=en#helium-ground-state-en');
  assert.equal(destination(base+'?lang=en#helium-ground-state-en','ja',ids),base+'?lang=ja#helium-ground-state-ja');
});

test('ordinary anchors, missing translations and separate-language reading routes keep their fragments',()=>{
  const base='https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/';
  assert.ok(destination(base+'?lang=ja#download','en',[]).endsWith('?lang=en#download'));
  assert.ok(destination(base+'?lang=ja#unpaired-ja','en',[]).endsWith('?lang=en#unpaired-ja'));
  assert.ok(destination(base+'?lang=ja#example-ja','en',['example-en'],false).endsWith('?lang=en#example-ja'));
  assert.equal(destination('https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-atoms/#helium','en',[],false,'https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-atoms/'),'https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-atoms/?lang=en#helium');
});
