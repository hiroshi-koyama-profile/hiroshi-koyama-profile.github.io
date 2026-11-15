// Import only the reviewed public dist/ output; scientific model modules stay unchanged.
import {cpSync,readFileSync,writeFileSync,rmSync,existsSync,readdirSync} from 'node:fs';
import {resolve,dirname,relative,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
if(process.argv.length!==3)throw Error('Usage: node scripts/import-astronomy.mjs /absolute/path/to/astronomy/dist');
const source=resolve(process.argv[2]);
for(const file of ['ja/index.html','en/index.html','ja/advanced/index.html','en/solutions/index.html','sitemap.xml'])if(!existsSync(resolve(source,file)))throw Error('Missing publication file: '+file);
const target=resolve(root,'astronomy-step-by-step');
const sourceCommit=execFileSync('git',['-C',source,'rev-parse','HEAD'],{encoding:'utf8'}).trim();
const receipt={importedOn:'2026-11-16',sourceRepository:'https://github.com/koyamarium/astronomy-step-by-step',sourceCommit,scope:'Complete bilingual public textbook, including foundations, advanced, solutions, books and numbers supplement.',originalSha256:{}};
const files=[];
function walk(dir){for(const entry of readdirSync(dir,{withFileTypes:true})){const p=resolve(dir,entry.name);if(entry.isDirectory())walk(p);else if(entry.isFile())files.push(p);else throw Error('Non-file in publication artifact: '+p);}}
walk(source);
rmSync(target,{recursive:true,force:true});cpSync(source,target,{recursive:true});
for(const path of files){
 const rel=relative(source,path),data=readFileSync(path);receipt.originalSha256[rel]=createHash('sha256').update(data).digest('hex');
 if(!['.html','.js','.css','.json','.xml','.md','.txt'].includes(extname(path)))continue;
 let text=data.toString('utf8').replaceAll('https://koyamarium.github.io/#contact','mailto:koyamarium@gmail.com').replaceAll('https://koyamarium.github.io','https://hrkoyama.github.io');
 if(rel==='app.js'){
  const patch=(before,after)=>{if(text.split(before).length!==2)throw Error('Upstream UI changed: '+before.slice(0,70));text=text.replace(before,after);};
  patch("let { language: locale } = routing.resolve(location, storage.get('astro.language', 'ja'));", "let sharedLanguage; try { sharedLanguage = localStorage.getItem('hrkoyama.home.language'); } catch {}\n  let { language: locale } = routing.resolve(location, ['ja','en'].includes(sharedLanguage) ? sharedLanguage : storage.get('astro.language', 'ja'));");
  patch('document.documentElement.lang = locale;', "document.documentElement.lang = locale;\n    try { localStorage.setItem('hrkoyama.home.language', locale); } catch {}\n    document.body.classList.add('site-language-managed');");
  patch("const langButton = event.target.closest('[data-lang]');", "const langButton = event.target.closest('[data-lang], [data-site-lang]');");
  patch("if (locale === langButton.dataset.lang) return;\n      locale = langButton.dataset.lang;", "const nextLanguage = langButton.dataset.lang || langButton.dataset.siteLang;\n      if (locale === nextLanguage) return;\n      locale = nextLanguage;");
  patch('document.querySelector(`[data-lang="${locale}"]`).focus({ preventScroll: true });', '(document.querySelector(`[data-site-lang="${locale}"]`) || document.querySelector(`[data-lang="${locale}"]`)).focus({ preventScroll: true });');
  patch("else window.scrollTo({ top: 0, behavior: 'instant' });\n  }", "else window.scrollTo({ top: 0, behavior: 'instant' });\n    document.dispatchEvent(new CustomEvent('archive-language-change', { detail: locale }));\n  }");
 }
 if(rel==='style.css')text+='\n/* Shared site controls handle language changes; native links remain usable without JavaScript. */\nbody.site-language-managed>.header>.languages{display:none!important}\n';
 writeFileSync(resolve(target,rel),text);
}
writeFileSync(resolve(root,'astronomy-import.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(`Imported complete astronomy publication: ${files.length} files, source ${sourceCommit.slice(0,7)}.`);
