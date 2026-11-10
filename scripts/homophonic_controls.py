#!/usr/bin/env python3
"""Equal-budget homophonic optimization against exact marginal/bigram nulls.

The optimizer and frozen independent scorer are reused from cipher_battery.
Randomized Euler trails preserve bigram counts exactly but are NOT uniform
samples from the set of compatible sequences.
"""
import argparse, collections, hashlib, json, pathlib, random, time
import numpy as np
from cipher_battery import english_model, homophonic_anneal, records, score
ROOT=pathlib.Path(__file__).resolve().parents[1]
SEED=23469478

def bigrams(xs):
    return collections.Counter(zip(xs,xs[1:]))

def euler_shuffle(xs,rng):
    """Hierholzer on shuffled outgoing multiedges, preserving endpoints exactly."""
    xs=list(xs)
    if len(xs)<2:return xs.copy()
    adjacency=collections.defaultdict(list)
    for a,b in zip(xs,xs[1:]):adjacency[a].append(b)
    for outgoing in adjacency.values():rng.shuffle(outgoing)
    stack=[xs[0]]; reverse_path=[]
    while stack:
        if adjacency[stack[-1]]:stack.append(adjacency[stack[-1]].pop())
        else:reverse_path.append(stack.pop())
    out=list(reversed(reverse_path))
    assert len(out)==len(xs) and out[0]==xs[0] and out[-1]==xs[-1]
    assert collections.Counter(out)==collections.Counter(xs) and bigrams(out)==bigrams(xs)
    return out

def null_records(books,rng,mode):
    out=[]
    for b in books:
        xs=b['codes'].tolist()
        if mode=='shuffle':rng.shuffle(xs)
        elif mode=='bigrams':xs=euler_shuffle(xs,rng)
        else:raise ValueError(mode)
        out.append({'id':b['id'],'codes':np.asarray(xs,dtype=np.int64)})
    return out

def fit(train,hold,table,seed,restarts,steps):
    out=homophonic_anneal(train,hold,table,random.Random(seed),restarts,steps)
    out.pop('warning',None)
    out['train_minus_holdout']=out['train_score']-out['holdout_score']
    return out

def encode_homophonic(text,rng):
    """Two disjoint numeric codes per English letter, chosen independently."""
    return np.asarray([2*(ord(c)-65)+rng.randrange(2) for c in text],dtype=np.int64)

def decode_known(codes):
    return ''.join(chr(int(c)//2+65) for c in codes)

def control_positive(reference,train,hold,table,restarts,steps):
    # The reference is the last20% withheld from the language-model fitting.
    needed=sum(len(b['codes']) for b in train+hold)
    if len(reference)<needed:raise ValueError('insufficient reserved English')
    cursor=0; tr=[];ho=[]; rng=random.Random(SEED+10000);truth={}
    for group,output in [(train,tr),(hold,ho)]:
        for b in group:
            n=len(b['codes']);piece=reference[cursor:cursor+n];cursor+=n
            truth[b['id']]=piece
            output.append({'id':b['id'],'codes':encode_homophonic(piece,rng)})
    out=fit(tr,ho,table,SEED+20000,restarts,steps)
    predicted=out['holdout_output']
    expected=''.join(truth[r['id']] for r in predicted)
    actual=''.join(r['output'] for r in predicted)
    matches=sum(a==b for a,b in zip(expected,actual))
    out['holdout_character_accuracy']=matches/len(expected)
    out['holdout_correct_characters']=matches
    out['holdout_characters']=len(expected)
    out['expected_holdout']=[{'id':r['id'],'text':truth[r['id']]} for r in predicted]
    out['known_key_exact_recovery']=all(decode_known(b['codes'])==truth[b['id']] for b in tr+ho)
    out['true_key_holdout_score']=sum(score([ord(c)-65 for c in truth[b['id']]],table)*(len(b['codes'])-3) for b in ho)/sum(len(b['codes'])-3 for b in ho)
    out['role']='Synthetic two-homophone positive control, English not used to train scoring model, equal optimizer budget and book lengths.'
    return out

def run(nulls=19,restarts=2,steps=5000):
    start=time.monotonic()
    books=json.loads((ROOT/'data/normalized_books.json').read_text())
    split=json.loads((ROOT/'data/normalized_splits.json').read_text())
    train=records([b for b in books if b['id'] in split['discovery_book_ids']])
    hold=records([b for b in books if b['id'] in split['holdout_book_ids']])
    table,reference=english_model(ROOT/'data/english_reference/alice.txt')
    observed=fit(train,hold,table,SEED,restarts,steps)
    print('observed',observed['train_score'],observed['holdout_score'],flush=True)
    controls={}
    for mode_i,mode in enumerate(['shuffle','bigrams']):
        trials=[]
        for i in range(nulls):
            rng=random.Random(SEED+1000*(mode_i+1)+i)
            tr=null_records(train,rng,mode);ho=null_records(hold,rng,mode)
            r=fit(tr,ho,table,SEED+30000+i+1000*mode_i,restarts,steps)
            r.pop('mapping');r.pop('holdout_output')
            r['replicate']=i
            r['changed_train_books']=sum(not np.array_equal(a['codes'],b['codes']) for a,b in zip(train,tr))
            r['changed_holdout_books']=sum(not np.array_equal(a['codes'],b['codes']) for a,b in zip(hold,ho))
            trials.append(r)
            print(mode,i+1,nulls,r['train_score'],r['holdout_score'],flush=True)
        def p(key):return (1+sum(r[key]>=observed[key] for r in trials))/(nulls+1)
        controls[mode]={'replicates':nulls,'trials':trials,'train_mean':float(np.mean([r['train_score'] for r in trials])),
          'holdout_mean':float(np.mean([r['holdout_score'] for r in trials])),
          'train_upper_tail_p':p('train_score'),'holdout_upper_tail_p':p('holdout_score'),
          'gain_upper_tail_p':p('train_minus_holdout')}
    positive=control_positive(reference,train,hold,table,restarts,steps)
    out={'seed':SEED,'numpy_version':np.__version__,'budget':{'restarts':restarts,'mutations_each':steps,'total_fits':1+2*nulls+1},
      'input_sha256':hashlib.sha256((ROOT/'data/normalized_books.json').read_bytes()).hexdigest(),
      'reference_sha256':hashlib.sha256((ROOT/'data/english_reference/alice.txt').read_bytes()).hexdigest(),
      'split':{'train_ids':split['discovery_book_ids'],'holdout_ids':split['holdout_book_ids'],
               'train_codes':sum(len(b['codes']) for b in train),'holdout_codes':sum(len(b['codes']) for b in hold)},
      'observed':observed,'controls':controls,'positive_control':positive,'runtime_seconds':time.monotonic()-start,
      'verdict':'NO_VERIFIED_TRANSLATION',
      'limitations':['Equal-budget optimizer-null calibration is conditional on this scoring function, arbitrary 100-code to26-letter map, initialization and annealing schedule.',
       'Bigram controls are randomized Euler trails, not uniform samples; per-book length, endpoints, unigram and directed-bigram counts are exact, longer motifs are not preserved.',
       'Only61 holdout codes in one connected component; no verified game plaintext; tokenization was inferred on entire public corpus upstream.',
       'Training gain or a small p value is not semantic accuracy. Multiple reported p values are exploratory and uncorrected.',
       'Failure to recover the synthetic positive would show insufficient algorithmic power and forbids rejecting homophonic substitution.']}
    (ROOT/'results/homophonic_controls.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'runtime':out['runtime_seconds'],'positive_accuracy':positive['holdout_character_accuracy'],'controls':{m:{k:v for k,v in r.items() if k!='trials'} for m,r in controls.items()}},indent=2),flush=True)
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--nulls',type=int,default=19);ap.add_argument('--restarts',type=int,default=2);ap.add_argument('--steps',type=int,default=5000);args=ap.parse_args();run(args.nulls,args.restarts,args.steps)
