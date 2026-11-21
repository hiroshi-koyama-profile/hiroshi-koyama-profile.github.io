import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root=new URL('../',import.meta.url);
const read=p=>readFileSync(new URL(p,root),'utf8');
const data=JSON.parse(read('catalog/atlas-methods.json'));
const base=data.code_base.slice(1);
const manifest=JSON.parse(read(base+'source-manifest.json'));
const verification=JSON.parse(read(base+'verification.json'));
const hash=b=>createHash('sha256').update(b).digest('hex');

test('planned methods never inherit available implementations or verified status',()=>{
  const items=data.methods;
  assert.equal(new Set(items.map(x=>x.id)).size,items.length);
  assert.equal(items.filter(x=>x.origin==='existing-coverage-catalog').length,90);
  for(const x of items.filter(x=>x.status==='planned')){
    assert.deepEqual(x.code_modules,[]);assert.deepEqual(x.test_files,[]);
    assert.ok(x.next_deliverable.ja&&x.next_deliverable.en);
    assert.match(x.limitations.en,/No dedicated implementation/);
  }
  for(const id of ['ewald','pme','spme','hartree-fock','kohn-sham-dft'])assert.equal(items.find(x=>x.id===id).status,'planned');
  assert.equal(items.find(x=>x.id==='barnes-hut').status,'educational-example');
  assert.match(items.find(x=>x.id==='pm').limitations.en,/not.*Ewald/);
});

test('all advertised source and test files are present in the verified edition',()=>{
  for(const [name,expected] of Object.entries(manifest.files)){
    assert.ok(!name.includes('..')&&!name.startsWith('/'));
    const bytes=readFileSync(new URL(base+name,root));assert.equal(hash(bytes),expected,name);
  }
  for(const x of data.methods){
    for(const name of x.code_modules)assert.ok(manifest.files['numart/'+name+'.py'],x.id);
    for(const name of x.test_files)assert.ok(manifest.files['tests/'+name+'.py'],x.id);
  }
  const archive=readFileSync(new URL(base+'atlas-code-'+data.code_edition+'.zip',root));
  assert.equal(hash(archive),verification.archive_sha256);
  assert.equal(verification.failures+verification.errors,0);
  assert.equal(verification.tests,verification.passed+verification.skipped);
  assert.equal(verification.skipped_cases.length,verification.skipped);
});

test('each method has readable HTML, JSON and Markdown with valid reading-language fallbacks',()=>{
  for(const x of data.methods){
    const route='numerical-methods-atlas/methods/'+x.id+'/';
    for(const ext of ['html','json','md'])assert.ok(existsSync(new URL(route+'index.'+ext,root)));
    const record=JSON.parse(read(route+'index.json'));assert.equal(record.status,x.status);
    const html=read(route+'index.html');assert.ok(html.includes('data-site-language="ja"')&&html.includes('data-site-language="en"'));
    for(const path of Object.values(x.reading))assert.ok(existsSync(new URL(path.slice(1)+'index.html',root)));
    if(x.status!=='planned'&&!x.reading.ja)assert.ok(html.includes('英語の解説を読む'));
    assert.doesNotMatch(html,/https:\/\/github\.com\/koyamarium\//);
  }
});

test('discovery routes expose the catalog and downloads without private GitHub dependencies',()=>{
  const index=read('numerical-methods-atlas/methods/index.html');
  const ids=[...index.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);assert.equal(ids.length,new Set(ids).size);
  const publicData=JSON.parse(read('numerical-methods-atlas/methods/index.json'));
  assert.equal(publicData.methods.length,data.methods.length);
  assert.equal(publicData.code_release.sha256,verification.archive_sha256);
  assert.ok(read('llms.txt').includes('/numerical-methods-atlas/methods/'));
  for(const name of ['index.html','content.en.json','content.ja.json','content.json'])assert.doesNotMatch(read('numerical-methods-atlas/'+name),/https:\/\/github\.com\/koyamarium\/(?:numerical-methods-atlas|the-art-of-numerical-algorithms)/);
});
