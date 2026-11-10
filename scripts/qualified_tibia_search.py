#!/usr/bin/env python3
"""Gated, equal-budget exploratory homophonic search and fully refitted nulls.

Every hypothesis is conditioned on the imported code streams; no translation
is accepted from scores and the61-code old holdout is not new/blind data.
"""
import argparse,hashlib,json,pathlib,random,time,datetime
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from cipher_battery import english_model,score
from homophonic_controls import euler_shuffle
from robust_homophonic import solve
from fast_homophonic import library
from qualification_gate_v2 import assess
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'data/protocols/qualified_search_v2.json'
RESULT=ROOT/'results/qualified_tibia_search_v2.json'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def freeze():
    if PROTOCOL.exists():raise RuntimeError('protocol already frozen')
    p={'version':'P04_V2_EXPLORATORY','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'gate':'all6freshV2synthetic scenarios pass>=27/30 at>=95% accuracy; otherwise noTibia fit',
      'input_sha256':digest(ROOT/'data/normalized_books.json'),'split_sha256':digest(ROOT/'data/normalized_splits.json'),
      'scorer':'Alice frozen first80% tetragrams, train regularization2.0; selection by training objective only',
      'solver_budget':{'banks':2,'restarts':8,'steps':100000,'num_codes':100,'max_temp':12.0,'frequency_weight':2.0},
      'nulls':['shuffle','bigrams','blocks8'],'replicates_each':99,'workers':2,'seed':70469000,
      'statistic':'weighted mean raw log10 tetragram score on previously exposed61-code holdout, map selected only on discovery',
      'null_selection':'refit whole2-bank optimization on each null; fresh seeds, identical budget',
      'transformation':'perbook reconstructed integer codes; each null preserves lengths; blocks8 uses one position permutation perbook',
      'scope':'Exploratory screen only; no external plaintext, tiny correlated test; structural dependencies remain',
      'acceptance':'No automatic translation, regardless of p; output literal without repairs',
      'implementation_hashes':{s:digest(ROOT/s) for s in ['scripts/qualified_tibia_search.py','scripts/qualification_gate_v2.py','scripts/robust_homophonic.py','scripts/fast_homophonic.py','src/homophonic_solver.cpp','scripts/cipher_battery.py','scripts/homophonic_controls.py']}}
    PROTOCOL.write_text(json.dumps(p,indent=2)+'\n');return p

def null_data(seqs,rng,mode):
    result=[]
    for seq in seqs:
        x=list(seq)
        if mode=='shuffle':rng.shuffle(x)
        elif mode=='bigrams':x=euler_shuffle(x,rng)
        elif mode=='blocks8':
            chunks=[x[i:i+8] for i in range(0,len(x),8)];rng.shuffle(chunks);x=[c for chunk in chunks for c in chunk]
        else:raise ValueError(mode)
        result.append(x)
    return result

def fit(train,hold,table,seed,budget):
    r=solve(train,table,seed=seed,**budget);m=r['mapping'];decoded=[[m[c] for c in seq] for seq in hold]
    weights=[max(0,len(s)-3) for s in decoded]
    hscore=sum(score(s,table)*n for s,n in zip(decoded,weights) if n)/sum(weights)
    return {'train_score':r['train_score'],'objective':r['objective'],'holdout_score':hscore,
      'mapping':m,'literal_holdout':[''.join(chr(c+65) for c in s) for s in decoded],
      'selected_bank':r['selected_bank'],'runtime_seconds':r['total_runtime_seconds']}

def run():
    gate=assess();(ROOT/'results/p04_gate_v2.json').write_text(json.dumps(gate,indent=2)+'\n')
    if not gate['gate_passed']:
        print('BLOCKED_INSUFFICIENT_V2_QUALIFICATION; zero newTibia fits',flush=True);return
    if RESULT.exists():raise RuntimeError('result exists, do not silently rerun')
    p=json.loads(PROTOCOL.read_text())
    for s,h in p['implementation_hashes'].items():
        if digest(ROOT/s)!=h:raise RuntimeError('frozen implementation changed:'+s)
    if digest(ROOT/'data/normalized_books.json')!=p['input_sha256']:raise RuntimeError('corpuschanged')
    if digest(ROOT/'data/normalized_splits.json')!=p['split_sha256']:raise RuntimeError('splitchanged')
    books=json.loads((ROOT/'data/normalized_books.json').read_text());split=json.loads((ROOT/'data/normalized_splits.json').read_text())
    train=[[int(c) for c in b['codes']] for b in books if b['id'] in split['discovery_book_ids']]
    hold=[[int(c) for c in b['codes']] for b in books if b['id'] in split['holdout_book_ids']]
    table,_=english_model(ROOT/'data/english_reference/alice.txt');library();started=time.monotonic()
    observed=fit(train,hold,table,p['seed'],p['solver_budget']);print('observed',observed['train_score'],observed['holdout_score'],observed['literal_holdout'],flush=True)
    controls={}
    with ThreadPoolExecutor(max_workers=p['workers']) as pool:
        for mi,mode in enumerate(p['nulls']):
            tasks=[]
            for i in range(p['replicates_each']):
                seed=p['seed']+10000*(mi+1)+i;rng=random.Random(seed)
                a=null_data(train,rng,mode);b=null_data(hold,rng,mode)
                changed=sum(x!=y for x,y in zip(hold,b))
                tasks.append((i,changed,pool.submit(fit,a,b,table,seed+500000,p['solver_budget'])))
            trials=[]
            for i,changed,f in tasks:
                r=f.result();r.pop('mapping');r.pop('literal_holdout');r.update(replicate=i,changed_holdout_books=changed)
                trials.append(r);print(mode,i+1,r['holdout_score'],flush=True)
                (ROOT/'results/qualified_search_v2_checkpoint.json').write_text(json.dumps({'complete':False,'mode':mode,'finished_current':len(trials),'observed':observed,'completed_modes':controls,'current_trials':trials},indent=2)+'\n')
            controls[mode]={'trials':trials,'replicates':len(trials),'holdout_upper_tail_p':(1+sum(t['holdout_score']>=observed['holdout_score'] for t in trials))/(1+len(trials)),
              'mean_holdout_score':float(np.mean([t['holdout_score'] for t in trials]))}
    result={'complete':True,'gate':gate,'protocol_sha256':digest(PROTOCOL),'protocol':p,'observed':observed,'controls':controls,
      'runtime_seconds':time.monotonic()-started,'verdict':'NO_VERIFIED_TRANSLATION',
      'limits':['Old61-code dependent holdout is not prospective independent validation.',
        'Null p values are exploratory and not probability of semantic correctness; multiple nulls are not independent tests.',
        'Euler nulls are not uniform over valid trails; longer motifs not preserved; unchanged holdouts restrict variation.',
        'Imported tokenization was learned using full public corpus; no known game English plaintext.',
        'This finite English homophonic objective and code representation do not exhaust all469 algorithms.']}
    RESULT.write_text(json.dumps(result,indent=2)+'\n');print('completed',json.dumps({m:c['holdout_upper_tail_p'] for m,c in controls.items()}),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if a.freeze:print(json.dumps(freeze(),indent=2))
    if a.run:run()
