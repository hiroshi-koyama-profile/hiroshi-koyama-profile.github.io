import { readFile, writeFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { decorateSite } from './site-chrome.mjs';
const root = new URL('../', import.meta.url);
async function walk(dir) {
  for (const entry of await readdir(dir, {withFileTypes:true})) {
    if (entry.name.startsWith('.')) continue;
    const url = new URL(entry.name + (entry.isDirectory() ? '/' : ''), dir);
    if (entry.isDirectory()) await walk(url);
    else if (entry.name.endsWith('.html')) {
      const path = decodeURIComponent(url.pathname.slice(root.pathname.length));
      const reading = /^numerical-methods-atlas\/(en|ja)\/read\//.exec(path);
      const fixed = reading ? reading[1] : path === 'academic-roots/index.html' || path.startsWith('notebooks/') ? 'ja' : path.startsWith('gordon-bell/') || path.startsWith('the-art-of-thermal-instability/') ? 'en' : '';
      await writeFile(url, decorateSite(await readFile(url,'utf8'), {contentLanguage:fixed}));
    }
  }
}
await walk(root);
// Keep viewing-asset receipts in sync when shared navigation changes notebook HTML.
const manifestUrl = new URL('notebooks/public-manifest.json',root);
const manifest = JSON.parse(await readFile(manifestUrl,'utf8'));
for (const file of manifest.files) {
  const bytes = await readFile(new URL('notebooks/' + file.path,root));
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  if (file.sha256 !== sha256 && !/\.(html|md|js|css)$/.test(file.path)) throw Error('Unexpected viewing asset change: ' + file.path);
  file.bytes = bytes.length; file.sha256 = sha256;
}
await writeFile(manifestUrl, JSON.stringify(manifest,null,2)+'\n');
console.log('Built shared bilingual navigation, rights notices and AI discovery links.');
