#!/usr/bin/env python3
"""Complete the previously bounded cases, with original matched controls."""
import argparse
import random
import re
import subprocess
from collections import Counter
from target_decimal_experiment import ROOT,load,dump,sha,vocabulary
from target_decimal_solver import encode
from periodic_decimal_solver import Codebook,Model,positions
from periodic_decimal_fast import fast_segment
from exhaustive_periodic_native import run_native,FLAGS
from independent_word_validator import body,words

CODECS=('ordinal0_compact','ordinal1_compact')
SEED=226613


def prepare():
    if (ROOT/'data/round22_cases.json').exists():raise ValueError('cases already exist')
    vocab=vocabulary();vset=set(vocab)
    docs={n:words(body(ROOT/f'data/word_validator_reference/{n}.txt')) for n in ('wizard_oz','peter_pan')}
    inv={r['id']:r for r in load('data/source_validation_inventory.json')}
    real=[inv[k]['text'] for k in ('chayenne_2009_part1','chayenne_2009_part2')]
    old=load('results/round21_periodic_decimal.json')
    nulls=[{'kind':c['kind'],'trial':row['trial'],'groups':row['groups']} for c in old['controls'] if c['target']=='chayenne_direct' for row in c['rows']]
    cases=[];rng=random.Random(SEED)
    for ci,codec in enumerate(CODECS):
        book=Codebook(vocab,codec)
        for period in (6,7,8):
            starts={n:[i for i in range(len(d)-6) if all(w in vset for w in d[i:i+6])
                       and all(len(encode(''.join(d[i+j:i+j+3]),codec))>=period for j in (0,3))] for n,d in docs.items()}
            for feedback in (0,1):
                model=Model(book,period,'stream',feedback)
                for trial in range(30):
                    name=('wizard_oz','peter_pan')[trial%2];start=rng.choice(starts[name]);w=docs[name][start:start+6]
                    key=tuple(rng.randrange(10) for _ in range(period));raw=model.encrypt(w,key)
                    cases.append({'id':f'q_{ci}_{period}_{feedback}_{trial}','codec':codec,'period':period,'feedback':feedback,
                                  'kind':'qualification','groups':[''.join(raw[:3]),''.join(raw[3:])],
                                  'source':name,'start_word':start,'truth_words':w,'true_key':''.join(map(str,key))})
                cases.append({'id':f'real_{ci}_{period}_{feedback}','codec':codec,'period':period,'feedback':feedback,'kind':'real','groups':real})
                for ni,row in enumerate(nulls):
                    cases.append({'id':f'n_{ci}_{period}_{feedback}_{ni}','codec':codec,'period':period,'feedback':feedback,
                                  'kind':row['kind'],'trial':row['trial'],'groups':row['groups']})
    dump('data/round22_cases.json',cases)
    print('Prepared',len(cases),'frozen case inputs; no new key search performed.',flush=True)


def independent_review(case,result,vocab):
    model=Model(Codebook(vocab,case['codec']),case['period'],'stream',case['feedback'])
    contexts=positions(case['groups']);rows=[]
    for keytext in result['keys']:
        key=tuple(map(int,keytext));parts=[fast_segment(model,g,key,*ctx) for g,ctx in zip(case['groups'],contexts)]
        if not all(r['word_path_count']>0 for r in parts):raise ValueError('native candidate fails independent Python DP')
        if all(r['unique_words'] is not None for r in parts):
            text=[w for r in parts for w in r['unique_words']]
            emitted=model.encrypt(text,key);cut=len(parts[0]['unique_words'])
            if [''.join(emitted[:cut]),''.join(emitted[cut:])]!=case['groups']:raise ValueError('literal roundtrip mismatch')
        rows.append({'key':keytext,'parts':parts})
    return rows


def build():
    cases=load('data/round22_cases.json');vocab=vocabulary();results=[]
    for codec in CODECS:
        batch=[r for r in cases if r['codec']==codec]
        codes=sorted({encode(w,codec) for w in vocab})
        print('Starting native codec',codec,len(batch),'cases',flush=True)
        found=run_native(codes,batch,progress=True)
        for case,row in zip(batch,found):
            reviewed=independent_review(case,row,vocab) if row['keys'] else []
            truth=case.get('true_key')
            if truth is not None and truth not in row['keys']:raise ValueError('synthetic true key lost')
            results.append({**row,'codec':codec,'kind':case['kind'],
                            'true_key_retained':truth in row['keys'] if truth is not None else None,
                            'python_candidate_reviews':reviewed})
    inv={r['id']:r for r in load('data/source_validation_inventory.json')};transfers=[]
    case_index={r['id']:r for r in cases}
    for result in results:
        if result['kind']!='real':continue
        case=case_index[result['id']];model=Model(Codebook(vocab,case['codec']),case['period'],'stream',case['feedback'])
        for keytext in result['keys']:
            key=tuple(map(int,keytext))
            for source in ('avar_tar_poem','knightmare_2012','official_poll_2020_option_c'):
                groups=re.findall(r'\d+',inv[source]['text'])
                transfers.append({'case':case['id'],'key':keytext,'source':source,
                                  'word_candidates':[model.words(g,key,*ctx) for g,ctx in zip(groups,positions(groups))]})
    q=[r for r in results if r['kind']=='qualification'];real=[r for r in results if r['kind']=='real'];nulls=[r for r in results if r['kind'] not in ('real','qualification')]
    summary={'total_fits':len(results),'all_complete':all(r['complete'] for r in results),
             'total_domain_key_assignments':sum(r['domain_keys'] for r in results),
             'prefix_checked_key_assignments':sum(r['checked_keys'] for r in results),
             'prefix_pruned_key_assignments':sum(r['prefix_pruned_keys'] for r in results),
             'qualification_fits':len(q),'qualification_truth_retained':sum(r['true_key_retained'] for r in q),
             'qualification_unique_key':sum(len(r['keys'])==1 for r in q),
             'real_fits':len(real),'real_keys':sum(len(r['keys']) for r in real),
             'null_fits':len(nulls),'null_fits_with_keys':sum(bool(r['keys']) for r in nulls),
             'null_keys':sum(len(r['keys']) for r in nulls),
             'scope':'Domain counts include mathematically pruned keys, not billions of explicit full-message decodings. Model/case aliases are not independent semantic evidence.'}
    return {'summary':summary,'results':results,'transfers':transfers,'new_verified_translations':0,
            'scope':'Exact completion of the fixed12round21models and matched controls, conditional on lexicon/codecs/framing. No independent meaning attestation.'}


def freeze():
    if (ROOT/'data/round22_evidence_manifest.json').exists():raise ValueError('already frozen')
    files=['data/round22_protocol.json','data/round22_cases.json','native/periodic_dictionary_search.cpp',
           'scripts/exhaustive_periodic_native.py','scripts/round22_exhaustive_experiment.py','scripts/periodic_decimal_solver.py',
           'scripts/periodic_decimal_fast.py','scripts/target_decimal_experiment.py','scripts/target_decimal_solver.py','scripts/independent_word_validator.py',
           'data/source_validation_inventory.json','results/round21_periodic_decimal.json']
    files += [f'data/word_validator_reference/{n}.txt' for n in ('secret_garden','my_man_jeeves','wizard_oz','peter_pan')]
    dump('data/round22_evidence_manifest.json',{'stage':'Before complete-key search on new fixtures/real/null data',
                                             'sha256':{p:sha(p) for p in files}})


def run(check=False):
    for p,h in load('data/round22_evidence_manifest.json')['sha256'].items():
        if sha(p)!=h:raise ValueError('frozen input changed: '+p)
    result=build()
    if check:
        if result!=load('results/round22_exhaustive.json'):raise ValueError('full replay mismatch')
    else:
        dump('results/round22_exhaustive.json',result)
        dump('results/round22_compiler.json',{'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],'flags':FLAGS})
    print(result['summary'],flush=True)
    print('Full replay matches.' if check else 'Results saved.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--freeze',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.prepare:prepare()
    elif a.freeze:freeze()
    else:run(a.check)
