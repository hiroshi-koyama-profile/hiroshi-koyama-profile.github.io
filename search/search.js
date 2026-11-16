import {makeSearch,excerpt,safePath} from './engine.mjs?v=e158973c70cd';
const main = document.querySelector('[data-search-index]');
const input = document.querySelector('#search-query');
const status = document.querySelector('#search-status');
const results = document.querySelector('#search-results');
const more = document.querySelector('#search-more');
const examples = document.querySelector('#search-examples');
const locale = () => ['ja','en'].includes(new URLSearchParams(location.search).get('lang')) ? new URLSearchParams(location.search).get('lang') : document.documentElement.lang === 'en' ? 'en' : 'ja';
const phrases = {
  ja: {loading:'検索対象を読み込んでいます…',ready:'公開ページ・資料 {count} 件を検索できます。',found:'「{query}」：{count} 件',none:'「{query}」に一致するページはありません。短い語や別の表記でお試しください。',failed:'検索データを読み込めませんでした。接続を確認して、もう一度お試しください。',ja:'日本語',en:'English',both:'日本語・English'},
  en: {loading:'Loading the search index…',ready:'Search {count} public pages and resources.',found:'{count} results for “{query}”',none:'No results for “{query}”. Try a shorter term or another spelling.',failed:'The search index could not be loaded. Check your connection and try again.',ja:'日本語',en:'English',both:'Japanese / English'}
};
const words = (key,values={}) => Object.entries(values).reduce((text,[key,value]) => text.replaceAll('{'+key+'}',String(value)),phrases[locale()][key]);
let engine, count=0, matches=[], query='', shown=20;
let loading;
function readQuery() {
  return (new URLSearchParams(location.hash.slice(1)).get('q') || '').trim().slice(0,200);
}
function label(doc) { return locale()==='en' && doc.titleEn ? doc.titleEn : doc.title; }
function showRows() {
  const fragment = document.createDocumentFragment();
  for (const doc of matches.slice(0,shown)) {
    const path = safePath(doc.url);
    if (!path) continue;
    const item=document.createElement('li');
    const heading=document.createElement('h2');
    const link=document.createElement('a');
    const url=new URL(path,location.origin);
    url.searchParams.set('lang',locale());
    link.href=url.pathname+url.search+url.hash;
    link.textContent=label(doc);
    heading.append(link);
    const meta=document.createElement('p');meta.className='search-meta';
    meta.textContent=(locale()==='en' ? doc.categoryEn : doc.categoryJa)+' · '+words(doc.lang);
    const summary=document.createElement('p');summary.className='search-excerpt';
    summary.textContent=excerpt(doc.text,query);
    item.append(meta,heading,summary);fragment.append(item);
  }
  results.replaceChildren(fragment);
  more.hidden=shown>=matches.length;
}
async function load() {
  if (engine) return;
  if (loading) return loading;
  loading=(async () => {
    const response=await fetch(main.dataset.searchIndex,{credentials:'omit'});
    if (!response.ok) throw Error('Search index HTTP '+response.status);
    const data=await response.json();
    if (!Array.isArray(data.documents) || data.documents.length>2000) throw Error('Invalid search index');
    engine=makeSearch(data.documents);count=data.documents.length;
  })();
  try {await loading;} finally {loading=null;}
}
async function render() {
  query=readQuery();input.value=query;shown=20;
  document.querySelectorAll('.site-search input').forEach(field => {field.value=query;});
  examples.hidden=!!query;
  status.textContent=words('loading');
  try {await load();} catch {
    status.textContent=words('failed');results.replaceChildren();more.hidden=true;return;
  }
  // Ignore an earlier response if the user changed the fragment during the fetch.
  if (query!==readQuery()) {render();return;}
  matches=query ? engine(query,locale()) : [];
  status.textContent=query ? words(matches.length?'found':'none',{query,count:matches.length}) : words('ready',{count});
  showRows();
}
more.addEventListener('click',() => {shown+=20;showRows();});
document.addEventListener('site-search-query',render);
addEventListener('hashchange',render);
addEventListener('popstate',render);
render();
