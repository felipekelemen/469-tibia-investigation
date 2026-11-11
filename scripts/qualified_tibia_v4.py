#!/usr/bin/env python3
"""New frozen English scorer, old exposed corpus: fully refitted exploratorynulls."""
import json,pathlib,hashlib,time,random,datetime,argparse
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from copied_homophonic_v3 import build_model
from copied_v4_gate import assess
from qualified_tibia_search import fit,null_data
from fast_homophonic import library
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'data/protocols/qualified_search_v4.json'
RESULT=ROOT/'results/qualified_tibia_search_v4.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def freeze():
    if PROTOCOL.exists():raise RuntimeError('alreadyfrozen')
    temperature=json.loads((ROOT/'results/reheat_v4_development.json').read_text())['selected']['temperature'];config={'banks':2,'frequency_weight':2.0,'max_temp':temperature}
    p={'version':'P04_V4','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'gate':'all3copiedV4qualification modes pass before anynew469fit',
      'model':build_model()[1],'budget':dict(config,restarts=8,steps=100000,num_codes=100),
      'input_sha256':digest(ROOT/'data/normalized_books.json'),'split_sha256':digest(ROOT/'data/normalized_splits.json'),
      'seed':120469000,'nulls':['shuffle','bigrams','blocks8'],'replicates_each':99,'workers':2,
      'selection':'trainobjective only; identical completebudget oneachnull',
      'heldout':'old61codesalreadyexposed, notprospectiveindependentvalidation',
      'interpretation':'Englishscorerstatistic only; literaloutputs; noautotranslation or manualrepairs',
      'implementation_hashes':{s:digest(ROOT/s) for s in ['scripts/qualified_tibia_v4.py','scripts/copied_v4_gate.py','scripts/copied_homophonic_v3.py','scripts/qualified_tibia_search.py','scripts/robust_homophonic.py','scripts/fast_homophonic.py','src/homophonic_solver.cpp','scripts/cipher_battery.py','scripts/homophonic_controls.py']}}
    PROTOCOL.write_text(json.dumps(p,indent=2)+'\n');return p
def run():
    gate=assess();(ROOT/'results/copied_v4_gate.json').write_text(json.dumps(gate,indent=2)+'\n')
    if not gate['gate_passed']:print('BLOCKED: copiedV4qualification failed; zero newTibiafits',flush=True);return
    if RESULT.exists():raise RuntimeError('resultalreadyexists')
    p=json.loads(PROTOCOL.read_text())
    for s,h in p['implementation_hashes'].items():
        if digest(ROOT/s)!=h:raise ValueError('frozenimplementationchanged:'+s)
    if digest(ROOT/'data/normalized_books.json')!=p['input_sha256'] or digest(ROOT/'data/normalized_splits.json')!=p['split_sha256']:raise ValueError('inputchanged')
    table,meta=build_model()
    if meta['model_sha256']!=p['model']['model_sha256']:raise ValueError('modelchanged')
    books=json.loads((ROOT/'data/normalized_books.json').read_text());split=json.loads((ROOT/'data/normalized_splits.json').read_text())
    train=[[int(c) for c in b['codes']] for b in books if b['id'] in split['discovery_book_ids']]
    hold=[[int(c) for c in b['codes']] for b in books if b['id'] in split['holdout_book_ids']]
    library();start=time.monotonic();observed=fit(train,hold,table,p['seed'],p['budget'])
    print('observed',observed['train_score'],observed['holdout_score'],observed['literal_holdout'],flush=True);controls={}
    with ThreadPoolExecutor(max_workers=p['workers']) as pool:
        for mi,mode in enumerate(p['nulls']):
            tasks=[]
            for i in range(p['replicates_each']):
                seed=p['seed']+10000*(mi+1)+i;rng=random.Random(seed);a=null_data(train,rng,mode);b=null_data(hold,rng,mode)
                tasks.append((i,sum(x!=y for x,y in zip(hold,b)),pool.submit(fit,a,b,table,seed+500000,p['budget'])))
            rows=[]
            for i,changed,future in tasks:
                r=future.result();r.pop('mapping');r.pop('literal_holdout');r.update(replicate=i,changed_holdout_books=changed)
                rows.append(r);print(mode,i+1,r['holdout_score'],flush=True)
                (ROOT/'results/qualified_search_v4_checkpoint.json').write_text(json.dumps({'complete':False,'mode':mode,'finished':len(rows),'observed':observed,'completed_modes':controls,'current_trials':rows},indent=2)+'\n')
            controls[mode]={'trials':rows,'holdout_upper_tail_p':(1+sum(r['holdout_score']>=observed['holdout_score'] for r in rows))/(1+len(rows)),
              'mean_holdout_score':float(np.mean([r['holdout_score'] for r in rows]))}
    r={'complete':True,'gate':gate,'protocol':p,'protocol_sha256':digest(PROTOCOL),'observed':observed,'controls':controls,
      'runtime_seconds':time.monotonic()-start,'verdict':'NO_VERIFIED_TRANSLATION',
      'limits':['Repeated studies on exposed61codeholdout are exploratory; no independentgameplaintext.',
       'Importedtwo-digitreconstruction, Englishlettermap and finiteoptimizer only, notall469algorithms.',
       'Matchednulls refit fully; Eulernotuniform; shorttest sometimesunchanged; longercontextsnotexactlypreserved.',
       'Gatecovers specified synthetic copied/ordinarygenres; no universalcryptanalytic power asserted.']}
    RESULT.write_text(json.dumps(r,indent=2)+'\n');print('complete',json.dumps({m:v['holdout_upper_tail_p'] for m,v in controls.items()}),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if a.freeze:print(json.dumps(freeze(),indent=2))
    if a.run:run()
