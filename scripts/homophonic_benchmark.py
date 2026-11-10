#!/usr/bin/env python3
"""Positive-control qualification. Never reads Tibia data or adjusts a key on test.

Protocol must be frozen before qualification. Six scenarios share thirty source
excerpts, so scenarios are paired and must not be pooled as 180 independent texts.
"""
import argparse,collections,datetime,hashlib,json,math,pathlib,random,re,time,functools
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from cipher_battery import english_model,score
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'data/homophonic_benchmark_protocol.json'
SOURCES=ROOT/'data/benchmark_reference/SOURCES.json'
TRAIN_N=5668
HOLD_N=1024
FIXTURES=30
SEED=46930000
FREQUENCIES=[8.2,1.5,2.8,4.3,12.7,2.2,2,6.1,7,0.15,0.77,4,2.4,6.7,7.5,1.9,0.095,6,6.3,9.1,2.8,0.98,2.4,0.15,2,0.074]

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

@functools.lru_cache(maxsize=4)
def letters(path):
    raw=path.read_text(encoding='utf-8-sig')
    if '*** START OF THE PROJECT GUTENBERG EBOOK' in raw:
        raw=raw.split('*** START OF THE PROJECT GUTENBERG EBOOK',1)[1].split('***',1)[1]
    raw=raw.split('*** END OF THE PROJECT GUTENBERG EBOOK',1)[0]
    return re.sub('[^A-Z]','',raw.upper())

def excerpt(index):
    """15 nonoverlapping contiguous source excerpts from each of two authors."""
    if not 0<=index<FIXTURES:raise ValueError(index)
    source='pride_prejudice' if index<15 else 'sherlock_holmes'
    offset=(index%15)*(TRAIN_N+HOLD_N)
    full=letters(ROOT/f'data/benchmark_reference/{source}.txt')
    text=full[offset:offset+TRAIN_N+HOLD_N]
    if len(text)!=TRAIN_N+HOLD_N:raise ValueError('reference too short')
    return text,source,offset

def encode(text,code_count,distribution,seed):
    """Disjoint arbitrary codeIDs, all26 letters represented in the true key."""
    if code_count<26 or code_count>100:raise ValueError(code_count)
    rng=random.Random(seed);allocation=[1]*26
    if distribution=='balanced':
        allocation=[code_count//26]*26
        for i in rng.sample(range(26),code_count%26):allocation[i]+=1
    elif distribution=='skewed':
        for i in rng.choices(range(26),weights=FREQUENCIES,k=code_count-26):allocation[i]+=1
    else:raise ValueError(distribution)
    ids=list(range(code_count));rng.shuffle(ids);pools=[];key=[-1]*100;cursor=0
    for letter,n in enumerate(allocation):
        pool=ids[cursor:cursor+n];cursor+=n;pools.append(pool)
        for c in pool:key[c]=letter
    out=[]
    for c in text:
        pool=pools[ord(c)-65]
        weights=None if distribution=='balanced' else [(j+1)**-1.25 for j in range(len(pool))]
        out.append(rng.choices(pool,weights=weights,k=1)[0])
    return out,key,allocation

def segments(xs,width=128):return [xs[i:i+width] for i in range(0,len(xs),width)]

def fixture(index,code_count,distribution):
    text,source,offset=excerpt(index)
    seed=SEED+10000*code_count+(1000 if distribution=='skewed' else 0)+index
    codes,key,allocation=encode(text,code_count,distribution,seed)
    train=codes[:TRAIN_N];hold=codes[TRAIN_N:];seen=set(train)
    return {'fixture':index,'source':source,'source_offset_letters':offset,'seed':seed,
      'train_sequences':segments(train),'hold_sequences':segments(hold),'truth_key':key,
      'truth_train':text[:TRAIN_N],'truth_hold':text[TRAIN_N:],
      'allocation':allocation,'code_count':code_count,'distribution':distribution,
      'train_observed_codes':len(seen),'hold_unseen_positions':sum(c not in seen for c in hold),
      'seen_code_hold_fraction':sum(c in seen for c in hold)/len(hold),
      'plain_excerpt_sha256':hashlib.sha256(text.encode()).hexdigest()}

def freeze(restarts,steps,workers=2,max_temp=12.0,frequency_weight=2.0):
    if PROTOCOL.exists() and json.loads(PROTOCOL.read_text()).get('frozen'):
        raise RuntimeError('Protocol already frozen; create a new version for any later study')
    solver_paths=['scripts/fast_homophonic.py','src/homophonic_solver.cpp','scripts/homophonic_benchmark.py']
    for path in solver_paths:
        if not (ROOT/path).is_file():raise FileNotFoundError(path)
    source_rows=json.loads(SOURCES.read_text())
    protocol={'version':'p02-v1','frozen':True,'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'data_scope':'synthetic positive-control qualification only; no Tibia input',
      'seed':SEED,'train_letters':TRAIN_N,'holdout_letters':HOLD_N,'fixtures_per_scenario':FIXTURES,
      'scenarios':[{'codes':n,'distribution':d} for n in [52,75,99] for d in ['balanced','skewed']],
      'solver_budget':{'restarts':restarts,'steps_each':steps,'num_codes':100,'max_temp':max_temp,'frequency_weight':frequency_weight},
      'workers':workers,
      'gate':{'minimum_holdout_character_accuracy':.95,'minimum_fixture_pass_fraction':.9,'minimum_pass_count':27},
      'selection':'Budget chosen on development only; qualification measured once; no parameter adjustment from its outcomes.',
      'development_author':'Mary Shelley / Frankenstein, separate from qualification authors',
      'qualification_authors':['Jane Austen','Arthur Conan Doyle'],
      'scorers':{'primary':'Frozen Alice first80% tetragrams used for fitting','secondary':'Frankenstein first80% tetragrams used for evaluation only, never key selection'},
      'source_hashes':{r['name']:r['sha256'] for r in source_rows},
      'alice_sha256':digest(ROOT/'data/english_reference/alice.txt'),
      'implementation_hashes':{p:digest(ROOT/p) for p in solver_paths},
      'qualification_excerpt_manifest':[{'fixture':i,'source':excerpt(i)[1],'start':excerpt(i)[2],
        'length':TRAIN_N+HOLD_N,'sha256':hashlib.sha256(excerpt(i)[0].encode()).hexdigest()} for i in range(FIXTURES)],
      'independence':'Thirty disjoint plaintext excerpts shared across six scenarios. Adjacent same-author excerpts may share phrases/style; thirty excerpts are not thirty authors. No independent-pool claim across scenarios.',
      'identifiability':'Report unknown-code positions explicitly. seen-code fraction is coverage, not proof that unseen mappings could never be inferred from language.'}
    PROTOCOL.write_text(json.dumps(protocol,indent=2)+'\n');return protocol

def verify(protocol):
    for p,h in protocol['implementation_hashes'].items():
        if digest(ROOT/p)!=h:raise RuntimeError(f'Frozen implementation changed: {p}')
    for row in json.loads(SOURCES.read_text()):
        if digest(ROOT/f"data/benchmark_reference/{row['name']}.txt")!=protocol['source_hashes'][row['name']]:raise RuntimeError('source changed')
    if digest(ROOT/'data/english_reference/alice.txt')!=protocol['alice_sha256']:raise RuntimeError('scorer source changed')

def run():
    from fast_homophonic import solve,library
    protocol=json.loads(PROTOCOL.read_text());verify(protocol)
    primary,_=english_model(ROOT/'data/english_reference/alice.txt')
    secondary,_=english_model(ROOT/'data/benchmark_reference/frankenstein.txt')
    budget=protocol['solver_budget'];started=time.monotonic();trials=[];summaries=[]
    library() # Compile once before native calls in worker threads. Native RNG/Engine state is local to each call.
    executor=ThreadPoolExecutor(max_workers=protocol['workers'])
    def submit_fixture(scenario,i):
        f=fixture(i,scenario['codes'],scenario['distribution'])
        return executor.submit(solve,f['train_sequences'],primary,seed=f['seed']+500000,restarts=budget['restarts'],steps=budget['steps_each'],num_codes=100,max_temp=budget['max_temp'],frequency_weight=budget['frequency_weight'])
    for scenario in protocol['scenarios']:
        subset=[]
        futures=[submit_fixture(scenario,i) for i in range(FIXTURES)]
        for i in range(FIXTURES):
            f=fixture(i,scenario['codes'],scenario['distribution'])
            # Only training ciphertext and frozen score table reach the optimizer.
            fit=futures[i].result()
            mapping=np.asarray(fit['mapping'],dtype=np.int64)
            hold=list(x for seq in f['hold_sequences'] for x in seq)
            predicted=''.join(chr(int(mapping[x])+65) for x in hold)
            truth=f['truth_hold'];correct=sum(a==b for a,b in zip(predicted,truth))
            def weighted_score(xs,table):
                return sum(score(x,table)*max(0,len(x)-3) for x in xs)/sum(max(0,len(x)-3) for x in xs)
            decoded_sequences=[[int(mapping[c]) for c in seq] for seq in f['hold_sequences']]
            true_sequences=segments([ord(c)-65 for c in truth])
            seen_train={c for seq in f['train_sequences'] for c in seq}
            row={'scenario':scenario,'fixture':i,'source':f['source'],'source_offset_letters':f['source_offset_letters'],
              'plain_excerpt_sha256':f['plain_excerpt_sha256'],'seed':f['seed'],'allocation':f['allocation'],
              'train_observed_codes':f['train_observed_codes'],'hold_unseen_positions':f['hold_unseen_positions'],
              'seen_code_hold_fraction':f['seen_code_hold_fraction'],
              'correct_holdout_letters':correct,'holdout_letters':len(truth),'character_accuracy':correct/len(truth),
              'passes':correct/len(truth)>=protocol['gate']['minimum_holdout_character_accuracy'],
              'trained_code_key_accuracy':sum(int(mapping[c])==f['truth_key'][c] for c in seen_train)/len(seen_train),
              'train_score':fit.get('train_score'),'fit_runtime_seconds':fit.get('runtime_seconds'),
              'primary_score_decoded':weighted_score(decoded_sequences,primary),'primary_score_true':weighted_score(true_sequences,primary),
              'secondary_score_decoded':weighted_score(decoded_sequences,secondary),'secondary_score_true':weighted_score(true_sequences,secondary),
              'literal_holdout_preview':predicted[:160],'true_holdout_preview':truth[:160]}
            subset.append(row);trials.append(row)
            checkpoint={'protocol_sha256':digest(PROTOCOL),'finished_fits':len(trials),'trials':trials,'runtime_seconds':time.monotonic()-started,'complete':False}
            (ROOT/'results/homophonic_benchmark_checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
            print(json.dumps({'scenario':scenario,'fixture':i,'accuracy':row['character_accuracy'],'runtime':row['fit_runtime_seconds']}),flush=True)
        passes=sum(r['passes'] for r in subset)
        summaries.append({'scenario':scenario,'fixtures':len(subset),'passed_fixtures':passes,'passes_gate':passes>=protocol['gate']['minimum_pass_count'],
          'mean_character_accuracy':float(np.mean([r['character_accuracy'] for r in subset])),
          'min_character_accuracy':min(r['character_accuracy'] for r in subset),'max_character_accuracy':max(r['character_accuracy'] for r in subset),
          'minimum_seen_code_hold_fraction':min(r['seen_code_hold_fraction'] for r in subset)})
    executor.shutdown(wait=True)
    verify(protocol)
    result={'protocol_sha256':digest(PROTOCOL),'frozen_protocol':protocol,'trials':trials,'scenarios':summaries,'complete':True,
      'runtime_seconds':time.monotonic()-started,'overall_gate_passes':all(s['passes_gate'] for s in summaries),
      'limits':['This qualifies only synthetic fixed homophonic maps with these text lengths/distributions and objective.',
        'The secondary scorer evaluates the selected map and does not constitute a second independent solver.',
        'No failure is a rejection of all homophonic ciphers, especially scenarios not reliably recovered.',
        'No Tibia code or plaintext is read by this program. Reused plaintext across scenarios forbids treating all180 fits as independent evidence.']}
    (ROOT/'results/homophonic_benchmark.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'scenarios':summaries,'runtime_seconds':result['runtime_seconds']},indent=2),flush=True)
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run',action='store_true');ap.add_argument('--restarts',type=int,default=4);ap.add_argument('--steps',type=int,default=100000);ap.add_argument('--workers',type=int,default=2);ap.add_argument('--max-temp',type=float,default=12.0);ap.add_argument('--frequency-weight',type=float,default=2.0);args=ap.parse_args()
    if args.freeze:print(json.dumps(freeze(args.restarts,args.steps,args.workers,args.max_temp,args.frequency_weight),indent=2))
    if args.run:run()
