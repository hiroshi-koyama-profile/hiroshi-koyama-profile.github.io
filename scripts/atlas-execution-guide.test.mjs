import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root=new URL('../',import.meta.url);
const read=path=>readFileSync(new URL(path,root),'utf8');
const registry=JSON.parse(read('catalog/atlas-execution-examples.json'));
const page=read('numerical-methods-atlas/code-and-data/index.html');
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#x27;');

test('both language guides connect the correct inputs, executable commands and output conditions for each example',()=>{
  for(const lang of ['ja','en']){
    assert.ok(page.includes(`data-site-language="${lang}"`));
    for(const x of registry.examples){
      assert.ok(page.includes(`id="${x.id}-${lang}"`),x.id);
      assert.ok(page.includes(escape(x.scope[lang])),x.id+' scope');
      assert.ok(page.includes(`href="${escape(x.inputs.url)}"`),x.id+' input');
      assert.ok(page.includes(escape(x.commands.install+'\n'+x.commands.run)),x.id+' commands');
      for(const c of [...x.checks,...(x.expected_failures||[])]){
        assert.ok(page.includes(escape(c.description[lang])),x.id+' acceptance');
        assert.ok(page.includes(escape(c.pointer)),x.id+' output location');
      }
    }
  }
});

test('shared atomic execution, independent receipt and code-versus-content terms stay explicit',()=>{
  const atomic=registry.examples.filter(x=>x.release.family==='quantum-atoms');
  assert.equal(atomic.length,2);
  assert.deepEqual(atomic[0].release,atomic[1].release);
  assert.equal(atomic[0].commands.run,atomic[1].commands.run);
  assert.ok(page.includes('1回の実行')&&page.includes('One run produces both'));
  assert.ok(page.includes('411')&&page.includes('23'));
  assert.ok(page.includes('再配布・改変公開の権限を追加するものではありません'));
  assert.ok(page.includes('tabindex="0"')&&page.includes('scope="col"'));
  assert.ok(page.includes('examples.json'));
});
