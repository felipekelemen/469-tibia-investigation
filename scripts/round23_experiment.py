#!/usr/bin/env python3
"""Frozen round23 experiment: lexical unit morphisms, controls and transfers."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,random,re
from unit_morphism_lexicon import banks,FAMILIES
from unit_morphism_solver import solve,word_extensions,key_tuple,decode_word,decode_stream
ROOT=Path(__file__).resolve().parents[1]

def load(path):return json.loads((ROOT/path).read_text())
def save(path,data):
    (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def check_manifest():
    for p,h in load('data/round23_input_manifest.json')['sha256'].items():
        if sha(p)!=h:raise ValueError('changed frozen input: '+p)

def groups(text):return re.findall(r'[0-9]+',text)

def verify_keys(words,b,out,cribs=None):
    for key in out['keys']:
        assert set(key)==set(''.join(words))
        assert all(b.minimum<=len(u)<=b.maximum for u in key.values())
        for w in words:
            form=''.join(key[d] for d in w)
            assert form in b.reverse
            if cribs and w in cribs:assert form in cribs[w]

def qualify(bs,fixtures):
    local=[];joint=[]
    for c in fixtures['local']:
        b=bs[c['family']]
        keys={key_tuple(k) for k in word_extensions(c['raw'],c['form'],b.minimum,b.maximum)}
        retained=key_tuple(c['key']) in keys
        if not retained:raise AssertionError('local true key lost')
        local.append({'family':c['family'],'partitions':len(keys),'truth_retained':retained})
    for c in fixtures['global']:
        b=bs[c['family']];out=solve(c['train'],b);verify_keys(c['train'],b,out)
        truth={d:u for d,u in c['key'].items() if d in ''.join(c['train'])}
        retained=truth in out['keys']
        if out['complete'] and not retained:raise AssertionError('complete solver lost generator')
        predictions=[]
        for raw,trueform in zip(c['held'],c['held_forms']):
            missing=any(set(raw)-set(k) for k in out['keys'])
            forms=sorted({''.join(k[d] for d in raw) for k in out['keys'] if not set(raw)-set(k)})
            eligible=out['complete'] and bool(out['keys']) and not missing
            unique=eligible and len(forms)==1
            predictions.append({'raw':raw,'complete_consensus_eligible':eligible,'unknown_digit':missing,'candidate_forms':len(forms),'unique_correct_form':unique and forms[0]==trueform,'unique_wrong_form':unique and forms[0]!=trueform,'trueform_spellings':b.reverse[trueform],'unique_spelling':unique and len(b.reverse.get(forms[0],[]))==1})
        row={'id':c['id'],'family':c['family'],'truth_retained':retained,'training_observed_digits':len(truth),'held_predictions':predictions,**out}
        joint.append(row)
        print('fixture',c['id'],'complete',out['complete'],'keys',len(out['keys']),'states',out['states'],flush=True)
    return {'local':local,'global':joint}

def target_cases(bs):
    inventory=load('data/source_validation_inventory.json')
    texts={r['id']:r['text'] for r in inventory if r['canonical_candidate']}
    avar=groups(texts['avar_tar_poem']);knight=groups(texts['knightmare_2012'])
    definitions=[('avar_first10',avar[:10]),('avar_full20',avar),('knightmare',knight)]
    rows=[];rng=random.Random(23639469+1)
    controls=[]
    for name,words in [('avar_first10',avar[:10]),('knightmare',knight)]:
        for index in range(19):
            shuffled={}
            for w in dict.fromkeys(words):
                chars=list(w);rng.shuffle(chars);shuffled[w]=''.join(chars)
            controls.append({'id':name+'_shuffle_'+str(index),'words':[shuffled[w] for w in words]})
    for family in FAMILIES:
        b=bs[family]
        for name,words in definitions:
            out=solve(words,b);verify_keys(words,b,out)
            transfers=[]
            for key in out['keys']:
                bytarget={}
                for target,text in texts.items():
                    if target.startswith('chayenne_'):
                        bytarget[target]=decode_stream(''.join(groups(text)),key,b)
                    else:bytarget[target]=[decode_word(w,key,b) for w in groups(text)]
                transfers.append({'key_rendered':{d:b.render(u) for d,u in key.items()},'predictions':bytarget})
            rows.append({'id':name,'family':family,'words':words,'transfer_is_provisional_if_fit_incomplete':not out['complete'],'transfers':transfers,**out})
            print('target',family,name,'complete',out['complete'],'keys',len(out['keys']),'states',out['states'],flush=True)
    nulls=[]
    for c in controls:
        for family in FAMILIES:
            out=solve(c['words'],bs[family]);verify_keys(c['words'],bs[family],out)
            nulls.append({**c,'family':family,**out})
        print('control',c['id'],flush=True)
    cribs=[]
    for family in FAMILIES:
        b=bs[family]
        for name in ('BEHOLDER','BONELORD'):
            forms=b.wordforms.get(name,[])
            if not forms:
                cribs.append({'family':family,'name':name,'status':'source_form_unavailable'});continue
            localkeys=[k for f in forms for k in word_extensions('3478',f,b.minimum,b.maximum)]
            out=solve(knight,b,cribs={'3478':forms});verify_keys(knight,b,out,{'3478':forms})
            cribs.append({'family':family,'name':name,'status':'fitted','isolated_3478_assignments':len({key_tuple(k) for k in localkeys}),**out})
    return {'targets':rows,'nulls':nulls,'cribs':cribs,'control_method':'19 distinct-word digit shuffles per Avar first10 and Knightmare; seed23639470. Root impossible groups are local lexical certificates, not translations.'}

def summarize(qualification,targets):
    summary={'families':{},'translation_validated':False}
    for family in FAMILIES:
        loc=[r for r in qualification['local'] if r['family']==family]
        pos=[r for r in qualification['global'] if r['family']==family]
        real=[r for r in targets['targets'] if r['family']==family]
        null=[r for r in targets['nulls'] if r['family']==family]
        predictions=[r for p in pos for r in p['held_predictions']]
        summary['families'][family]={
            'local_fixtures':len(loc),'local_truth_retained':sum(r['truth_retained'] for r in loc),
            'global_fixtures':len(pos),'global_complete':sum(r['complete'] for r in pos),'global_truth_retained':sum(r['truth_retained'] for r in pos),'global_unique_keys':sum(r['complete'] and len(r['keys'])==1 for r in pos),
            'held_forms':len(predictions),'held_unique_correct_forms':sum(r['unique_correct_form'] for r in predictions),'held_unique_wrong_forms':sum(r['unique_wrong_form'] for r in predictions),'held_unique_spellings':sum(r['unique_spelling'] for r in predictions),
            'real':[{'id':r['id'],'complete':r['complete'],'states':r['states'],'keys':len(r['keys']),'root_impossible_groups':r['root_impossible_groups']} for r in real],
            'null_fits':len(null),'null_complete':sum(r['complete'] for r in null),'null_nonempty':sum(bool(r['keys']) for r in null)}
    return summary

def run(check=False):
    check_manifest();bs,meta=banks();fixtures=load('data/round23_fixtures.json')
    if meta!=fixtures['lexicon']:raise ValueError('lexicon drift')
    q=qualify(bs,fixtures);t=target_cases(bs);s=summarize(q,t)
    outputs={'results/round23_qualification.json':q,'results/round23_targets.json':t,'data/round23_summary.json':s}
    for path,content in outputs.items():
        if check:
            if load(path)!=content:raise ValueError('replay mismatch: '+path)
        else:save(path,content)
    print(json.dumps(s,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();run(a.check)
