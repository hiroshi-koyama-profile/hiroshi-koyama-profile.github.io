import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const root=new URL('../',import.meta.url);
const read=path=>readFileSync(new URL(path,root),'utf8');
const registry=JSON.parse(read('catalog/atlas-execution-examples.json'));
const page=read('numerical-methods-atlas/code-and-data/index.html');
const escape=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#x27;');

function sectionWithAttribute(html,attribute,value){
  const attributePattern=new RegExp(`\\s${attribute}="${value}"`);
  const openings=[...html.matchAll(/<section\b[^>]*>/g)].filter(token=>attributePattern.test(token[0]));
  assert.equal(openings.length,1,`Expected one section with ${attribute}="${value}"`);
  const start=openings[0].index+openings[0][0].length;
  const tags=/<\/?section\b[^>]*>/g;
  tags.lastIndex=start;
  let depth=1;
  for(let token;(token=tags.exec(html));){
    depth+=token[0].startsWith('</')?-1:1;
    if(depth===0)return html.slice(start,token.index);
  }
  assert.fail(`Unclosed section with ${attribute}="${value}"`);
}

test('both language guides connect the correct inputs, executable commands and output conditions for each example',()=>{
  for(const lang of ['ja','en']){
    const locale=sectionWithAttribute(page,'data-site-language',lang);
    assert.equal([...locale.matchAll(/<section\b[^>]*\bdata-execution-example="/g)].length,registry.examples.length,lang+' recipe count');
    for(const x of registry.examples){
      const section=sectionWithAttribute(locale,'id',`${x.id}-${lang}`);
      const label=x.id+'/'+lang;
      assert.ok(section.includes(escape(x.name[lang])),label+' name');
      for(const field of ['scope','assumptions','units','boundaries']){
        for(const value of [].concat(x[field][lang]))assert.ok(section.includes(escape(value)),label+' '+field);
      }
      assert.ok(section.includes(`href="${escape(x.inputs.url)}"`),label+' input');
      assert.ok(section.includes(escape(x.commands.install+'\n'+x.commands.run)),label+' commands');
      for(const c of [...x.checks,...(x.expected_failures||[])]){
        assert.ok(section.includes(escape(c.description[lang])),label+' acceptance');
        assert.ok(section.includes(escape(c.pointer)),label+' output location');
      }
      for(const field of ['reference_notes','failure_scope']){
        if(x[field])assert.ok(section.includes(escape(x[field][lang])),label+' '+field);
      }
      for(const reference of x.references){
        assert.ok(section.includes(`href="${escape(reference.url)}"`),label+' reference link');
        assert.ok(section.includes(escape(reference.description[lang])),label+' reference description');
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
