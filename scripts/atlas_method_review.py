"""Validate and present method-specific applicability and source-review records.

This metadata audit never changes implementation status or reruns numerical code.
"""
import html
from urllib.parse import urlparse

LANGUAGES=('ja','en')
FIELDS=('assumptions','units','boundary_conditions','limitations')
STATES={
 'specified':{'ja':'条件を記載','en':'Specified'},
 'not-applicable':{'ja':'この構成要素では対象外','en':'Not applicable to this component'},
 'unknown':{'ja':'未確認','en':'Unknown'},
}
ROLES={
 'original-method':{'ja':'原法','en':'Original method'},
 'adopted-variant':{'ja':'採用変種','en':'Adopted variant'},
 'formulation':{'ja':'定式化','en':'Formulation'},
 'reference-solution':{'ja':'参照解・独立参照','en':'Reference solution / independent reference'},
 'context':{'ja':'関連する背景','en':'Context'},
}
LEVELS={
 'full-text':{'ja':'本文の該当箇所を確認','en':'Relevant full-text passages checked'},
 'abstract-and-metadata':{'ja':'抄録・書誌を確認','en':'Abstract and metadata checked'},
 'metadata':{'ja':'書誌を確認','en':'Metadata checked'},
}
KIND_LABELS={
 'primary-research':{'ja':'一次研究','en':'Primary research'},
 'book':{'ja':'著書','en':'Book'},
 'official-documentation':{'ja':'公式文書','en':'Official documentation'},
}
ESC=html.escape

def bilingual(value,where,lists=False):
    if not isinstance(value,dict) or any(lang not in value for lang in LANGUAGES):
        raise ValueError(where+': both languages are required')
    for lang in LANGUAGES:
        v=value[lang]
        if lists:
            if not isinstance(v,list) or not v or any(not isinstance(s,str) or not s.strip() for s in v):
                raise ValueError(where+': nonempty bilingual lists are required')
        elif not isinstance(v,str) or not v.strip():
            raise ValueError(where+': nonempty bilingual text is required')

def https(url,where):
    p=urlparse(url)
    if p.scheme!='https' or not p.netloc or p.username or p.password:
        raise ValueError(where+': use a public HTTPS URL')

def validate_method_reviews(catalog):
    policy=catalog.get('priority_review')
    reviews=[m for m in catalog['methods'] if m.get('method_review')]
    if policy is None:
        if reviews:raise ValueError('reviewed methods require a priority_review inventory')
        return []
    ids=policy['method_ids']
    if len(ids)!=24 or len(set(ids))!=24 or set(ids)!={m['id'] for m in reviews}:
        raise ValueError('priority_review must identify exactly the 24 reviewed methods')
    by_id={m['id']:m for m in catalog['methods']}
    for ident in ids:
        m=by_id[ident];review=m['method_review']
        if review.get('version')!=1 or not review.get('on'):
            raise ValueError(ident+': missing review version or date')
        for field in ['summary','limitations']:bilingual(m[field],ident+'.'+field)
        for field in ['assumptions','assumptions_ja']:
            if not isinstance(m.get(field),list) or not m[field] or any(not isinstance(v,str) or not v.strip() for v in m[field]):
                raise ValueError(ident+': explicit bilingual assumptions required')
        for field in ['units','units_ja','boundary_conditions','boundary_conditions_ja']:
            if not isinstance(m.get(field),str) or not m[field].strip():raise ValueError(ident+': missing '+field)
        for field in ['problem','variant']:bilingual(review[field],ident+'.'+field)
        for field in ['use_when','avoid_when']:bilingual(review[field],ident+'.'+field,lists=True)
        for field in FIELDS:
            state=review['fields'][field]
            if state.get('state') not in STATES:raise ValueError(ident+': invalid metadata state')
            bilingual(state['reason'],ident+'.'+field+'.reason')
        verification=review['verification']
        if verification.get('kind') not in ['source-and-code-inspection','source-review-no-implementation']:
            raise ValueError(ident+': distinguish metadata inspection from a new numerical run')
        bilingual(verification['summary'],ident+'.verification.summary')
        bilingual(verification['not_checked'],ident+'.verification.not_checked',lists=True)
        for evidence in verification['evidence']:
            https(evidence['url'],ident+'.evidence')
            if not evidence.get('label') or not evidence.get('kind'):raise ValueError(ident+': incomplete evidence')
        if m['status']=='planned' and (m['code_modules'] or m['test_files'] or m.get('quantum_examples') or m.get('example')):
            raise ValueError(ident+': a planned method cannot acquire implementation evidence')
        refs=m['references']
        if not refs or not any(r.get('kind')=='primary-research' and r.get('role')!='context' for r in refs):
            raise ValueError(ident+': a method-specific primary publication is required')
        for ref in refs:
            https(ref['url'],ident+'.reference')
            if ref.get('role') not in ROLES or ref.get('kind') not in KIND_LABELS:
                raise ValueError(ident+': distinguish reference role and publication kind')
            if not ref.get('scope') or not ref.get('label'):raise ValueError(ident+': missing reference scope or label')
            bilingual(ref['supports'],ident+'.reference.supports')
            v=ref['verification']
            https(v['url'],ident+'.reference.verification')
            if v.get('level') not in LEVELS or not v.get('checked_on') or not v.get('locator'):
                raise ValueError(ident+': record actual source-check depth and locator')
    return [by_id[i] for i in ids]

def linked(url,label):
    return '<a href="'+ESC(url,quote=True)+'">'+ESC(label)+'</a>'

def review_intro(method,lang):
    r=method['method_review'];ja=lang=='ja'
    body='<section class="method-review" data-method-review="'+method['id']+'"><p class="resource-status">'+('条件・文献の個別整理：' if ja else 'Method-specific conditions and sources: ')+r['on']+'</p>'
    body+='<h2>'+('解く問題と採用形' if ja else 'Problem and adopted formulation')+'</h2><dl><dt>'+('解く問題' if ja else 'Problem')+'</dt><dd>'+ESC(r['problem'][lang])+'</dd><dt>'+('採用した変種・範囲' if ja else 'Variant and scope')+'</dt><dd>'+ESC(r['variant'][lang])+'</dd></dl>'
    body+='<div class="method-decision">'
    for key,title in [('use_when','使える条件' if ja else 'Use when'),('avoid_when','避ける条件・追加処理が必要な場合' if ja else 'Avoid or add further treatment when')]:
        body+='<section><h2>'+title+'</h2><ul>'+''.join('<li>'+ESC(s)+'</li>' for s in r[key][lang])+'</ul></section>'
    return body+'</div></section>'

def field_note(method,field,lang):
    state=method['method_review']['fields'][field]
    return '<p class="metadata-note" data-metadata-field="'+field+'" data-field-state="'+state['state']+'"><strong>'+STATES[state['state']][lang]+':</strong> '+ESC(state['reason'][lang])+'</p>'

def verification_html(method,lang):
    v=method['method_review']['verification'];ja=lang=='ja'
    body='<section class="method-verification"><h2>'+('今回確認した範囲' if ja else 'Scope of this review')+'</h2><p>'+ESC(v['summary'][lang])+'</p>'
    if v['evidence']:
        body+='<ul class="resource-files">'+''.join('<li>'+linked(e['url'],e['label'])+'</li>' for e in v['evidence'])+'</ul>'
    body+='<h3>'+('未確認・含めない範囲' if ja else 'Not checked or not included')+'</h3><ul>'+''.join('<li>'+ESC(s)+'</li>' for s in v['not_checked'][lang])+'</ul></section>'
    return body

def references_html(method,lang):
    ja=lang=='ja'
    body='<h2>'+('手法別の文献と確認範囲' if ja else 'Method-specific references and source-check scope')+'</h2><ol class="method-references">'
    for r in method['references']:
        v=r['verification']
        body+='<li><p>'+linked(r['url'],r['label'])+'</p><p class="reference-role">'+ROLES[r['role']][lang]+' · '+KIND_LABELS[r['kind']][lang]+'</p><p>'+ESC(r['supports'][lang])+'</p><p class="reference-check">'+LEVELS[v['level']][lang]+' ('+ESC(v['checked_on'])+'): '+ESC(v['locator'])+' · '+linked(v['url'],'確認先' if ja else 'Checked source')+'</p></li>'
    body+='</ol><p class="metadata-note">'+('「本文の該当箇所を確認」は全導出の独立検証や計算の再実行を意味しません。原法・採用変種・参照解と、書誌のみの確認を区別しています。' if ja else 'Checking relevant full-text passages is not an independent proof of every derivation or a numerical rerun. Original methods, adopted variants, reference solutions and metadata-only checks remain distinct.')+'</p>'
    return body

def review_markdown(method):
    r=method['method_review'];text=''
    for lang in LANGUAGES:
        text+='\n## '+('条件と確認範囲' if lang=='ja' else 'Conditions and review scope')+' ('+lang+')\n\n'
        for key in ['problem','variant']:text+=key+': '+r[key][lang]+'\n\n'
        for key in ['use_when','avoid_when']:
            text+=key+':\n'+'\n'.join('- '+s for s in r[key][lang])+'\n\n'
        for field in FIELDS:
            v=method[field if lang=='en' or field=='limitations' else field+'_ja']
            if field=='limitations':v=v[lang]
            state=r['fields'][field]
            text+=field+' ['+state['state']+']:\n'+('\n'.join('- '+s for s in v) if isinstance(v,list) else v)+'\n'+state['reason'][lang]+'\n\n'
        v=r['verification'];text+='Review: '+v['summary'][lang]+'\n\nNot checked:\n'+'\n'.join('- '+s for s in v['not_checked'][lang])+'\n\n'
        text+='Evidence:\n'+'\n'.join('- '+e['label']+': '+e['url'] for e in v['evidence'])+'\n\n'
        text+='References:\n'
        for ref in method['references']:
            check=ref['verification'];text+='- ['+ref['role']+' / '+ref['kind']+'] '+ref['label']+' — '+ref['url']+'\n  '+ref['supports'][lang]+'\n  '+check['level']+' ('+check['checked_on']+'); '+check['locator']+'; '+check['url']+'\n'
    return text
