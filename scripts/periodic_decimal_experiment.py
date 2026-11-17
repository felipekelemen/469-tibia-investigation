#!/usr/bin/env python3
"""Frozen end-to-end position/context decoder experiment on priority messages."""
import argparse
import random
import re
from target_decimal_experiment import ROOT, load, dump, sha, vocabulary
from target_decimal_solver import FAMILIES, encode
from independent_word_validator import body, words
from periodic_decimal_solver import CODECS, Codebook, catalog, completions, positions

SEED=213478469


def search(groups,models,unspaced=False):
    return {name:(m.solve_unspaced(groups) if unspaced else m.solve(groups)) for name,m in models.items()}


def spaced_transfer(groups,fits,models,offset=0,previous=0):
    union=[set() for _ in groups]; first=[None]*len(groups); agreement=[True]*len(groups)
    empty=[0]*len(groups); rows=[]; incomplete=[]
    contexts=positions(groups)
    contexts=[(o+offset,previous if i==0 else prev) for i,(o,prev) in enumerate(contexts)]
    total=0
    for name,fit in fits.items():
        keys=completions(fit)
        if keys is None:incomplete.append(name);continue
        for key in keys:
            candidates=[models[name].words(raw,key,*ctx) for raw,ctx in zip(groups,contexts)]
            rows.append({'model':name,'key':list(key),'word_candidates':candidates})
            for i,c in enumerate(candidates):
                union[i].update(c);empty[i]+=not bool(c)
                if total==0:first[i]=c
                if len(c)!=1 or c!=first[i]:agreement[i]=False
            total+=1
    consensus=[next(iter(v)) if total and not incomplete and agreement[i] else None for i,v in enumerate(union)]
    return {'model_key_pairs':total,'incomplete_models':incomplete,'possible_words':[sorted(v) for v in union],
            'empty_predictions':empty,'strict_consensus':consensus,'rows':rows}


def unspaced_transfer(groups,fits,models):
    contexts=positions(groups); rows=[]; incomplete=[]
    for name,fit in fits.items():
        keys=completions(fit)
        if keys is None:incomplete.append(name);continue
        for key in keys:
            parsed=[models[name].segment(raw,key,*ctx) for raw,ctx in zip(groups,contexts)]
            rows.append({'model':name,'key':list(key),'parts':parsed})
    return {'incomplete_models':incomplete,'rows':rows,
            'scope':'Exact lexical word-path counts under each frozen key, not grammar or semantic proof.'}


def qualification(models,vocab):
    docs={n:words(body(ROOT/f'data/word_validator_reference/{n}.txt')) for n in ('wizard_oz','peter_pan')}
    starts={n:[i for i in range(len(d)-14) if all(w in vocab for w in d[i:i+7])] for n,d in docs.items()}
    rows=[]; rng=random.Random(SEED)
    for codec in CODECS:
        for period in (2,4,8):
            for reset in ('word','stream'):
                for fb in (0,1):
                    name=f'{codec}/p{period}/{reset}/feedback{fb}'; model=models[name]
                    for trial in range(3):
                        source=('wizard_oz','peter_pan')[len(rows)%2]; start=rng.choice(starts[source]); w=docs[source][start:start+14]
                        key=tuple(rng.randrange(10) for _ in range(period)); raw=model.encrypt(w,key)
                        fits=search(raw[:7],models)
                        true_retained=any(all(v<0 or v==key[i] for i,v in enumerate(k)) for k in fits[name]['keys'])
                        pred=spaced_transfer(raw[7:],fits,models,sum(map(len,raw[:7])),int(raw[6][-1]))
                        rows.append({'true_model':name,'trial':trial,'source':source,'start':start,'truth':w,'true_key':list(key),'raw':raw,
                                     'all_searches_complete':all(f['complete'] for f in fits.values()),
                                     'all_completions_complete':not pred['incomplete_models'],'truth_retained':true_retained,
                                     'model_key_pairs':pred['model_key_pairs'],'held_in_lexicon':sum(t in vocab for t in w[7:]),
                                     'strict_consensus':pred['strict_consensus'],
                                     'correct':sum(p==t for p,t in zip(pred['strict_consensus'],w[7:])),
                                     'wrong':sum(p is not None and p!=t for p,t in zip(pred['strict_consensus'],w[7:]))})
                        Codebook.constraints.cache_clear()
            print('Qualification:',codec,period,len(rows),flush=True)
    summary={'cases':len(rows),'complete_search_cases':sum(r['all_searches_complete'] for r in rows),
             'complete_transfer_cases':sum(r['all_completions_complete'] for r in rows),
             'true_key_retained_cases':sum(r['truth_retained'] for r in rows),
             'held_words':len(rows)*7,'held_in_lexicon':sum(r['held_in_lexicon'] for r in rows),
             'strict_correct':sum(r['correct'] for r in rows),'strict_wrong':sum(r['wrong'] for r in rows)}
    summary['prediction_gate_pass']=(all(r['all_searches_complete'] and r['all_completions_complete'] and r['truth_retained'] for r in rows)
                                     and summary['strict_wrong']==0 and summary['strict_correct']>=.9*summary['held_in_lexicon'])
    unspaced=[]
    for codec in CODECS:
        for reset in ('word','stream'):
            for fb in (0,1):
                name=f'{codec}/p4/{reset}/feedback{fb}';model=models[name]
                source=('wizard_oz','peter_pan')[len(unspaced)%2];start=rng.choice(starts[source]); w=docs[source][start:start+6]
                key=tuple(rng.randrange(10) for _ in range(4)); raw=model.encrypt(w,key); groups=[''.join(raw[:3]),''.join(raw[3:])]
                fit=model.solve_unspaced(groups)
                unspaced.append({'model':name,'source':source,'start':start,'truth':w,'true_key':list(key),'groups':groups,
                                 'complete':fit['complete'],'nodes':fit['nodes'],'full_keys':fit['full_key_count'],
                                 'truth_retained':any(all(v<0 or v==key[i] for i,v in enumerate(k)) for k in fit['keys'])})
                Codebook.constraints.cache_clear()
    return {'summary':summary,'rows':rows,'unspaced':unspaced,
            'scope':'All96models searched for spaced fixtures; only generating model for12unspaced parser fixtures. Existing two authors, overlapping lexicon-conditioned fit spans; not independent sources.'}


def fixed_width_preflight(inputs):
    widths={'ordinal0_fixed2':2,'ordinal1_fixed2':2,'ascii_upper':2,'ascii_lower_fixed3':3}
    return {name:{codec:[{'index':i,'length':len(g)} for i,g in enumerate(groups) if len(g)%width]
                  for codec,width in widths.items()} for name,groups in inputs.items()}


def build():
    vocab=vocabulary();models=catalog(vocab);q=qualification(models,set(vocab))
    print('Prediction gate:',q['summary'],flush=True)
    inv={r['id']:r for r in load('data/source_validation_inventory.json')}
    avar=re.findall(r'\d+',inv['avar_tar_poem']['text']);knight=re.findall(r'\d+',inv['knightmare_2012']['text'])
    poll=re.findall(r'\d+',inv['official_poll_2020_option_c']['text'])
    chayenne=[inv[k]['text'] for k in ('chayenne_2009_part1','chayenne_2009_part2')]
    inputs={'avar_prefix10':avar[:10],'knightmare7':knight,'avar_full20_diagnostic':avar,'chayenne_direct':chayenne}
    game={}
    for name,groups in inputs.items():
        fits=search(groups,models,name=='chayenne_direct')
        if name=='avar_prefix10': held=avar[10:];offset=sum(map(len,avar[:10]));prev=int(avar[9][-1])
        else:held=avar;offset=prev=0
        game[name]={'fit_groups':groups,'fits':fits,'avar_transfer':spaced_transfer(held,fits,models,offset,prev),
                    'knightmare_transfer':spaced_transfer(knight,fits,models), 'poll_transfer':spaced_transfer(poll,fits,models),
                    'chayenne_transfer':unspaced_transfer(chayenne,fits,models)}
        print(name,'complete',sum(f['complete'] for f in fits.values()),'model_keys',sum(f['full_key_count'] for f in fits.values()),flush=True)
        Codebook.constraints.cache_clear()
    controls=[]
    books=load('data/normalized_books.json'); ids=set(load('data/normalized_splits.json')['discovery_book_ids'])
    pools=[[b['digits'][i:i+n] for b in books if b['id'] in ids for i in range(len(b['digits'])-n+1)] for n in (36,13)]
    for ti,name in enumerate(('avar_prefix10','knightmare7','chayenne_direct')):
        groups=inputs[name]
        kinds=('within_fragment_shuffle','two_copied_fragments') if name=='chayenne_direct' else ('all_digit_shuffle','within_distinct_word_shuffle')
        for ki,kind in enumerate(kinds):
            rng=random.Random(SEED+1000+ti*100+ki);rows=[]
            for trial in range(19):
                if kind=='two_copied_fragments':changed=[rng.choice(p) for p in pools]
                elif kind=='all_digit_shuffle':
                    chars=list(''.join(groups));rng.shuffle(chars);changed=[];i=0
                    for g in groups:changed.append(''.join(chars[i:i+len(g)]));i+=len(g)
                else:
                    mapping={}
                    for g in sorted(set(groups)):
                        chars=list(g);rng.shuffle(chars);mapping[g]=''.join(chars)
                    changed=[mapping[g] for g in groups]
                fits=search(changed,models,name=='chayenne_direct')
                rows.append({'trial':trial,'groups':changed,'all_complete':all(f['complete'] for f in fits.values()),
                             'fits':{n:{'complete':f['complete'],'nodes':f['nodes'],'full_key_count':f['full_key_count']} for n,f in fits.items()}})
                Codebook.constraints.cache_clear()
            controls.append({'target':name,'kind':kind,'rows':rows})
            print('Nulls:',name,kind,flush=True)
    return {'models':list(models),'lexicon_size':len(vocab),'qualification':q,'game':game,'controls':controls,
            'fixed_width_preflight':fixed_width_preflight(inputs),'new_verified_translations':0,
            'scope':'Conditional periodic-additive decimal/lexicon/framing test. Model-key aliases not independent evidence. No new semantic anchor or invented English.'}


def freeze():
    if (ROOT/'data/round21_evidence_manifest.json').exists():raise ValueError('already frozen')
    files=['data/round21_protocol.json','scripts/periodic_decimal_solver.py','scripts/periodic_decimal_experiment.py',
           'scripts/target_decimal_solver.py','scripts/target_decimal_experiment.py','scripts/independent_word_validator.py',
           'data/source_validation_inventory.json','data/normalized_books.json','data/normalized_splits.json','requirements.txt']
    files += [f'data/word_validator_reference/{n}.txt' for n in ('secret_garden','my_man_jeeves','wizard_oz','peter_pan')]
    dump('data/round21_evidence_manifest.json',{'stage':'Before round21qualification and game results','sha256':{p:sha(p) for p in files}})


def run(check=False):
    for p,h in load('data/round21_evidence_manifest.json')['sha256'].items():
        if sha(p)!=h:raise ValueError('frozen input changed: '+p)
    result=build()
    if check:
        if result!=load('results/round21_periodic_decimal.json'):raise ValueError('replay mismatch')
    else:dump('results/round21_periodic_decimal.json',result)
    print('Full replay matches.' if check else 'Results saved.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.freeze:freeze()
    else:run(a.check)
