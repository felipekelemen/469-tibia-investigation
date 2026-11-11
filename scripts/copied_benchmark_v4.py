#!/usr/bin/env python3
"""Fresh-author qualification of copied English and ordinary99-code controls."""
import argparse,datetime,hashlib,json,pathlib,random,time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from homophonic_benchmark import letters,encode,segments
from copied_homophonic_v3 import build_model,TRAINING_PATHS
from robust_homophonic import solve
from cipher_battery import english_model
from robust_homophonic import solve as baseline_solve
from fast_homophonic import library
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'data/copied_benchmark_v4_protocol.json'
RESULT=ROOT/'results/copied_benchmark_v4.json'
MODES=['copied_static_codes','copied_fresh_homophones','ordinary']
SEED=110690000

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def fixture(i,mode):
    if not 0<=i<30 or mode not in MODES:raise ValueError('fixture')
    source='tom_sawyer' if i<15 else 'jane_eyre';local=i%15
    body=letters(ROOT/f'data/benchmark_reference_v4/{source}.txt');seed=SEED+1000*MODES.index(mode)+i;rng=random.Random(seed)
    if mode=='ordinary':
        offset=15*8192+local*6692;text=body[offset:offset+6692]
        if len(text)!=6692:raise ValueError('source too short')
        codes,key,allocation=encode(text,99,'skewed',seed);source_offsets=[offset]
    else:
        offset=local*8192;source_offsets=[offset+1024*j for j in range(8)]
        motifs=[body[x:x+256] for x in source_offsets]
        if any(len(s)!=256 for s in motifs):raise ValueError('source too short')
        schedule=[rng.randrange(8) for _ in range(30)];text=''.join(motifs[j] for j in schedule)[:6692]
        if mode=='copied_static_codes':
            encoded,key,allocation=encode(''.join(motifs),99,'skewed',seed)
            pools=[encoded[j*256:(j+1)*256] for j in range(8)];codes=[c for j in schedule for c in pools[j]][:6692]
        else:codes,key,allocation=encode(text,99,'skewed',seed)
    train=codes[:5668];hold=codes[5668:];seen=set(train)
    return {'fixture':i,'mode':mode,'source':source,'source_offsets':source_offsets,'seed':seed,
      'train':segments(train),'hold':segments(hold),'truth':text[5668:],'key':key,'allocation':allocation,
      'unseen_positions':sum(c not in seen for c in hold),'text_sha256':hashlib.sha256(text.encode()).hexdigest()}

def freeze():
    if PROTOCOL.exists():raise RuntimeError('protocol already frozen')
    development=json.loads((ROOT/'results/reheat_v4_development.json').read_text())
    if not development['complete']:raise ValueError('development incomplete')
    config={'banks':2,'frequency_weight':2.0,'max_temp':development['selected']['temperature']};table,meta=build_model()
    paths=['scripts/copied_benchmark_v4.py','scripts/copied_homophonic_v3.py','scripts/robust_homophonic.py',
       'scripts/fast_homophonic.py','src/homophonic_solver.cpp','scripts/homophonic_benchmark.py','scripts/cipher_battery.py']
    sources=json.loads((ROOT/'data/benchmark_reference_v4/SOURCES.json').read_text())
    p={'version':'P02_COPIED_V4','frozen':True,'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'development':'V3 opened failures+guards; fixed three-temperature grid, no qualification source used',
      'development_selected':development['selected'],'model':meta,'solver_config':config,
      'budget_each_bank':{'restarts':8,'steps':100000,'num_codes':100,'max_temp':config['max_temp']},
      'modes':MODES,'fixtures_per_mode':30,'train_letters':5668,'holdout_letters':1024,
      'gate':{'minimum_holdout_character_accuracy':.95,'minimum_pass_count':27,'minimum_fixture_pass_fraction':.9},
      'codes':99,'distribution':'skewed','seed':SEED,'workers':2,
      'qualification_authors':['Mark Twain','Charlotte Bronte'],
      'baseline':'V3 same broad scorer2banks temperature12 on static copied mode only; same ciphertext/seed; no test-based selection',
      'source_hashes':{r['name']:r['sha256'] for r in sources},
      'implementation_hashes':{s:digest(ROOT/s) for s in paths},
      'development_result_sha256':digest(ROOT/'results/reheat_v4_development.json'),
      'input_manifest':[{'fixture':i,'mode':m,'source':fixture(i,m)['source'],'offsets':fixture(i,m)['source_offsets'],
         'sha256':fixture(i,m)['text_sha256']} for m in MODES for i in range(30)],
      'limits':['Copied modes intentionally share underlying English motifs within each fixture and across the two copied modes. They are paired, not60independentcontents.',
        'Intervals across different fixtures do not overlap within a source. Only two authors, shared style remains.',
        'Operational gate in a sequential research program, not universal cryptanalytic power or proof of translation.',
        'No hyperparameter tuning after qualification results. No469reads in qualification.',
        'Modes share motifs but use different schedules and keys; their difference is not an isolated causal experiment.']}
    PROTOCOL.write_text(json.dumps(p,indent=2)+'\n');return p

def verify(p):
    for f,h in p['implementation_hashes'].items():
        if digest(ROOT/f)!=h:raise ValueError('frozenimplementation changed:'+f)
    for r in p['model']['training_sources']:
        if digest(ROOT/r['path'])!=r['source_sha256']:raise ValueError('modelsource changed')
    for name,h in p['source_hashes'].items():
        if digest(ROOT/f'data/benchmark_reference_v4/{name}.txt')!=h:raise ValueError('qualificationsource changed')
    if build_model()[1]['model_sha256']!=p['model']['model_sha256']:raise ValueError('modeltable changed')

def measure(f,result):
    hold=[c for s in f['hold'] for c in s];pred=''.join(chr(result['mapping'][c]+65) for c in hold)
    correct=sum(a==b for a,b in zip(pred,f['truth']))
    return {'correct_holdout_letters':correct,'holdout_letters':len(hold),'character_accuracy':correct/len(hold),
      'unseen_positions':f['unseen_positions'],'known_key_exact':''.join(chr(f['key'][c]+65) for c in hold)==f['truth'],
      'train_score':result['train_score'],'mapping':result['mapping'],'preview':pred[:120],'truth_preview':f['truth'][:120]}

def run():
    if RESULT.exists():raise RuntimeError('result already exists')
    p=json.loads(PROTOCOL.read_text());verify(p);table,_=build_model();library()
    rows=[];summaries=[];start=time.monotonic()
    with ThreadPoolExecutor(max_workers=p['workers']) as pool:
        for mode in MODES:
            fs=[fixture(i,mode) for i in range(30)]
            futs=[pool.submit(solve,f['train'],table,seed=f['seed']+700000,**p['solver_config']) for f in fs]
            baseline_futs=[pool.submit(baseline_solve,f['train'],table,seed=f['seed']+700000,banks=2,max_temp=12,frequency_weight=2.0) for f in fs] if mode=='copied_static_codes' else []
            subset=[]
            for i,(f,fut) in enumerate(zip(fs,futs)):
                fit=fut.result();r=measure(f,fit);r.update(scenario={'codes':99,'distribution':mode},fixture=i,source=f['source'],source_offsets=f['source_offsets'],text_sha256=f['text_sha256'],
                  selected_bank=fit['selected_bank'],runtime_seconds=fit['total_runtime_seconds'])
                if baseline_futs:r['V3_paired_baseline']=measure(f,baseline_futs[i].result())
                rows.append(r);subset.append(r);print(mode,i,r['character_accuracy'],flush=True)
                (ROOT/'results/copied_v4_qualification_checkpoint.json').write_text(json.dumps({'complete':False,'finished':len(rows),'trials':rows},indent=2)+'\n')
            passes=sum(r['character_accuracy']>=.95 for r in subset)
            s={'mode':mode,'fixtures':30,'passed_fixtures':passes,'passes_gate':passes>=27,
               'mean_character_accuracy':float(np.mean([r['character_accuracy'] for r in subset])),
               'min_character_accuracy':min(r['character_accuracy'] for r in subset)}
            if baseline_futs:s['V3_baseline_passed_fixtures']=sum(r['V3_paired_baseline']['character_accuracy']>=.95 for r in subset)
            summaries.append(s)
    verify(p);r={'complete':True,'protocol_sha256':digest(PROTOCOL),'frozen_protocol':p,'trials':rows,'summaries':summaries,
       'overall_gate_passes':all(s['passes_gate'] for s in summaries),'runtime_seconds':time.monotonic()-start,'limits':p['limits']}
    RESULT.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(summaries,indent=2),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if a.freeze:print(json.dumps(freeze(),indent=2))
    if a.run:run()
