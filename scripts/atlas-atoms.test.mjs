import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {searchChapters} from '../numerical-methods-atlas/home-search.js';
const root=new URL('../',import.meta.url);
const bytes=p=>readFileSync(new URL(p,root));
const read=p=>bytes(p).toString();
const json=p=>JSON.parse(read(p));
const hash=p=>createHash('sha256').update(bytes(p)).digest('hex');
const config=json('catalog/atlas-quantum-examples.json');
const base=config.code_base.slice(1);
const verification=json(base+'verification.json');

test('atomic download matches the independently executed package and every source receipt',()=>{
  assert.equal(hash(base+config.archive),verification.archive_sha256);
  assert.equal(hash(base+'source-manifest.json'),verification.source_manifest_sha256);
  const manifest=json(base+'source-manifest.json');
  for(const [file,digest] of Object.entries(manifest.files)){
    assert.ok(!file.startsWith('/')&&!file.split('/').includes('..'));
    assert.equal(hash(base+file),digest,file);
  }
  assert.equal(verification.passed,23);
  assert.equal(verification.failures+verification.errors+verification.skipped,0);
  assert.equal(verification.maximum_reproduced_energy_difference,0);
  assert.ok(Object.values(verification.checks).every(x=>x===true));
  const reference=json(base+'reference-pyscf.json');
  assert.equal(reference.inputs.pyscf_xc,'LDA_X,');
  assert.equal(reference.environment.pyscf,'2.11.0');
  assert.ok(!read(base+'reference_pyscf.py').includes('import atomic_radial'));
});

test('published atomic results retain raw mesh values, extrapolation, density and failed-SCF evidence',()=>{
  const result=json(base+'results/results.json');
  assert.ok(Object.values(result.checks).every(x=>x===true));
  for(const x of result.helium.independent_comparison){
    assert.ok(x.finest_reference_difference>1e-5&&x.finest_reference_difference<3e-5);
    assert.ok(Math.abs(x.extrapolated_reference_difference)<1e-8);
    assert.ok(x.radial_density_l1_difference>0&&x.radial_density_l1_difference<3e-5);
  }
  for(const lang of ['ja','en']){
    const route=`numerical-methods-atlas/${lang}/read/quantum-atoms/`;
    const page=read(route+'index.html');
    const record=json(route+'index.json');
    assert.equal(record.archive_sha256,verification.archive_sha256);
    assert.ok(page.includes('converged=false')&&page.includes('max_iterations'));
    assert.ok(page.includes('LDA_X')&&page.includes('katex-mathml')&&!page.includes('katex-error'));
    assert.ok(page.includes('h²')&&page.includes('0.0025'));
    for(const c of config.cases)assert.ok(page.includes(`id="${c.section}"`));
  }
});

test('only scoped atomic methods expose the separate edition, with correct root-level commands',()=>{
  const registry=json('numerical-methods-atlas/methods/index.json');
  const atomic=registry.methods.filter(x=>x.quantum_examples?.length);
  assert.equal(atomic.length,6);
  for(const x of atomic){
    assert.equal(x.status,'educational-example');
    assert.equal(x.code_base,'https://hrkoyama.github.io/'+base);
    assert.ok(x.code_download.endsWith(config.archive));
    assert.deepEqual(x.run_commands,[config.test_command,config.run_command]);
    assert.ok(x.example_scope.ja&&x.example_scope.en);
    for(const u of [...x.code_urls,...x.test_urls])assert.ok(existsSync(new URL(new URL(u).pathname.slice(1),root)));
    assert.ok(read(`numerical-methods-atlas/methods/${x.id}/index.md`).includes(x.code_download));
  }
  for(const id of ['diis','band-symmetry'])assert.equal(registry.methods.find(x=>x.id===id).status,'reading-only');
});

test('atomic examples are reachable from inventory, gallery and Japanese/English searches',()=>{
  const problems=json('numerical-methods-atlas/test-cases/index.json').problems;
  const images=json('numerical-methods-atlas/gallery/index.json').items;
  for(const c of config.cases){
    const problem=problems.find(x=>x.id===c.id),image=images.find(x=>x.id===c.id);
    assert.deepEqual(problem.run_commands,[config.test_command,config.run_command]);
    for(const lang of ['ja','en']){
      assert.ok(problem.reading[lang].endsWith('/quantum-atoms/#'+c.section));
      assert.equal(image.reading[lang],problem.reading[lang]);
    }
  }
  const index=json('numerical-methods-atlas/home-search-index.json');
  for(const [query,lang] of [['水素型原子','ja'],['helium','en']]){
    assert.ok(searchChapters(index,query,lang).some(x=>x.url?.includes('/read/quantum-atoms/')),query);
  }
  assert.ok(read('llms.txt').includes('/quantum-atoms/')&&read('llms.txt').includes('23 independently extracted package checks'));
});
