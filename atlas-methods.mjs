/** Local, bilingual filtering of the already-published method list. */
const statuses=new Set(['educational-example','reading-only','planned']);
const storageKey='hrkoyama.atlas.methodFilters.v1';
const queryLimit=200;
const instances=new WeakMap();

export function normalizeMethodSearch(value){
  return String(value??'').normalize('NFKC').toLowerCase()
    .replace(/[\p{Dash_Punctuation}\u2212]/gu,' ').replace(/\s+/gu,' ').trim();
}

export function methodMatches(record,status='all',query=''){
  if(!record||!statuses.has(record.status))return false;
  if(status!=='all'&&record.status!==status)return false;
  const haystack=normalizeMethodSearch(record.search);
  return normalizeMethodSearch(query).split(' ').filter(Boolean).every(word=>haystack.includes(word));
}

function sessionStorageOrNull(storage){
  if(storage!==undefined)return storage;
  try{return globalThis.sessionStorage??null;}catch{return null;}
}

function restore(storage){
  const fallback={status:'all',query:''};
  try{
    const raw=storage?.getItem(storageKey);
    if(!raw)return fallback;
    const saved=JSON.parse(raw);
    if(!saved||Array.isArray(saved)||!['all',...statuses].includes(saved.status)||typeof saved.query!=='string')return fallback;
    return {status:saved.status,query:saved.query.slice(0,queryLimit)};
  }catch{return fallback;}
}

function save(storage,state){
  try{storage?.setItem(storageKey,JSON.stringify(state));}catch{/* Filtering also works without storage. */}
}

export function wireMethodMaps(root=globalThis.document,storage){
  if(!root||typeof root.querySelectorAll!=='function')return null;
  if(instances.has(root))return instances.get(root);
  const sections=[...root.querySelectorAll('[data-method-map]')];
  if(typeof root.matches==='function'&&root.matches('[data-method-map]'))sections.unshift(root);
  const bindings=[...new Set(sections)].flatMap(section=>{
    const controls=section.querySelector('[data-method-controls]');
    const input=section.querySelector('[data-method-query]');
    const select=section.querySelector('[data-method-status]');
    const reset=section.querySelector('[data-method-reset]');
    const count=section.querySelector('[data-method-count]');
    const empty=section.querySelector('[data-method-empty]');
    // Leave the complete, readable fallback alone if a control is missing.
    if(!controls||!input||!select||!reset||!count||!empty)return [];
    const items=[...section.querySelectorAll('[data-method-id]')].map(node=>({
      node,record:{status:node.dataset.status,search:node.dataset.search??''}
    }));
    const groups=[...section.querySelectorAll('[data-method-group]')].map(node=>({
      node,id:node.dataset.methodGroup,
      items:[...node.querySelectorAll('[data-method-id]')],
      count:node.querySelector('[data-method-group-count]')
    }));
    return [{section,controls,input,select,reset,count,empty,items,groups,
      links:[...section.querySelectorAll('[data-method-group-link]')],
      ja:section.dataset.siteLanguage==='ja'||section.lang==='ja',composing:false}];
  });
  if(!bindings.length)return null;
  const store=sessionStorageOrNull(storage);
  let state=restore(store);
  const listeners=[];
  function listen(node,type,listener){
    node.addEventListener(type,listener);
    listeners.push(()=>node.removeEventListener(type,listener));
  }
  function render(){
    for(const binding of bindings){
      if(!binding.composing&&binding.input.value!==state.query)binding.input.value=state.query;
      if(binding.select.value!==state.status)binding.select.value=state.status;
      let visible=0;
      for(const item of binding.items){
        item.node.hidden=!methodMatches(item.record,state.status,state.query);
        if(!item.node.hidden)visible++;
      }
      const total=binding.items.length;
      binding.count.textContent=binding.ja?`${total}件中${visible}件を表示`:`Showing ${visible} of ${total} methods.`;
      binding.empty.hidden=visible!==0;
      const hiddenGroups=new Map();
      for(const group of binding.groups){
        const shown=group.items.filter(item=>!item.hidden).length;
        group.node.hidden=shown===0;
        hiddenGroups.set(group.id,group.node.hidden);
        if(group.count)group.count.textContent=binding.ja?`（${shown}/${group.items.length}）`:`(${shown}/${group.items.length})`;
      }
      for(const link of binding.links)link.hidden=hiddenGroups.get(link.dataset.methodGroupLink)===true;
    }
  }
  function update(next){
    if(next.status===state.status&&next.query===state.query)return;
    state=next;render();save(store,state);
  }
  function commit(binding){
    const status=binding.select.value==='all'||statuses.has(binding.select.value)?binding.select.value:'all';
    const query=binding.composing?state.query:String(binding.input.value).slice(0,queryLimit);
    if(binding.select.value!==status)binding.select.value=status;
    if(!binding.composing&&binding.input.value!==query)binding.input.value=query;
    update({status,query});
  }
  for(const binding of bindings){
    const onInput=event=>{if(!binding.composing&&!event?.isComposing)commit(binding);};
    listen(binding.input,'input',onInput);
    listen(binding.input,'search',onInput);
    listen(binding.select,'change',()=>commit(binding));
    listen(binding.input,'compositionstart',()=>{binding.composing=true;});
    listen(binding.input,'compositionend',()=>{binding.composing=false;commit(binding);});
    listen(binding.controls,'submit',event=>{
      event.preventDefault();
      if(!binding.composing&&!event.isComposing)commit(binding);
    });
    listen(binding.reset,'click',event=>{
      event.preventDefault();
      for(const other of bindings)other.composing=false;
      state={status:'all',query:''};render();
      try{store?.removeItem(storageKey);}catch{/* Reset is still effective in memory. */}
      binding.input.focus();
    });
  }
  render();
  for(const binding of bindings)binding.controls.hidden=false;
  const instance={
    getState:()=>({...state}),
    destroy(){for(const remove of listeners)remove();instances.delete(root);}
  };
  instances.set(root,instance);
  return instance;
}

if(typeof document!=='undefined'){
  const start=()=>wireMethodMaps(document);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
}
