#!/usr/bin/env python3
"""V2 fresh-author qualification. No Tibia reads, no tuning after freeze."""
import argparse,datetime,hashlib,json,pathlib,time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from cipher_battery import english_model,score
from homophonic_benchmark import letters,encode,segments
from robust_homophonic import solve
from fast_homophonic import library
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'data/homophonic_benchmark_v2_protocol.json'
RESULT=ROOT/'results/homophonic_benchmark_v2.json'
SOURCES=ROOT/'data/benchmark_reference_v2/SOURCES.json'
TRAIN_N,HOLD_N,FIXTURES,SEED=5668,1024,30,46940000

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def fixture(index,n,distribution):
    if type(index) is not int or not 0<=index<30:raise ValueError(index)
    source='war_worlds' if index<15 else 'great_expectations'
    offset=index%15*(TRAIN_N+HOLD_N)
    text=letters(ROOT/f'data/benchmark_reference_v2/{source}.txt')[offset:offset+TRAIN_N+HOLD_N]
    if len(text)!=TRAIN_N+HOLD_N:raise ValueError('source too short')
    seed=SEED+10000*n+(1000 if distribution=='skewed' else 0)+index
    codes,key,allocation=encode(text,n,distribution,seed);train=codes[:TRAIN_N];hold=codes[TRAIN_N:]
    return {'fixture':index,'source':source,'offset':offset,'text_hash':hashlib.sha256(text.encode()).hexdigest(),
      'seed':seed,'train':segments(train),'hold':segments(hold),'truth_hold':text[TRAIN_N:],
      'true_key':key,'allocation':allocation,'unseen_positions':sum(c not in set(train) for c in hold)}

def freeze():
    if PROTOCOL.exists():raise RuntimeError('V2 protocol already exists; never overwrite a frozen study')
    implementation=['scripts/homophonic_benchmark_v2.py','scripts/robust_homophonic.py','scripts/fast_homophonic.py',
      'src/homophonic_solver.cpp','scripts/homophonic_benchmark.py','scripts/cipher_battery.py']
    rows=json.loads(SOURCES.read_text())
    p={'version':'p02-v2','frozen':True,'frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'data_scope':'fresh-author synthetic qualification; no Tibia input',
      'development':'V1 old qualification fixtures now explicitly development; V1 preserved unchanged',
      'qualification_authors':['H. G. Wells','Charles Dickens'],'seed':SEED,'train_letters':TRAIN_N,'holdout_letters':HOLD_N,
      'fixtures_per_scenario':30,'scenarios':[{'codes':n,'distribution':d} for n in [52,75,99] for d in ['balanced','skewed']],
      'gate':{'minimum_holdout_character_accuracy':.95,'minimum_pass_count':27,'minimum_fixture_pass_fraction':.9},
      'solver_budget':{'banks':2,'restarts':8,'steps':100000,'num_codes':100,'max_temp':12.0,'frequency_weight':2.0},
      'bank_selection':'highest training objective; ties first; never test accuracy; bank1 seed=bank0seed+1000003',
      'baseline':'first bank only, paired on same fresh fixtures; secondary report, no influence on main selection',
      'workers':2,'primary_scorer':'Alice first80% tetragrams, unchanged from V1',
      'implementation_hashes':{s:digest(ROOT/s) for s in implementation},
      'source_hashes':{r['name']:r['sha256'] for r in rows},'alice_sha256':digest(ROOT/'data/english_reference/alice.txt'),
      'excerpt_manifest':[{'fixture':i,'source':fixture(i,52,'balanced')['source'],'offset':fixture(i,52,'balanced')['offset'],
         'length':TRAIN_N+HOLD_N,'sha256':fixture(i,52,'balanced')['text_hash']} for i in range(30)],
      'limits':['Thirty disjoint excerpts, two new authors; paired reuse of texts across six scenarios, not180 independenttexts.',
        'Sequential study designed after V1 failure: operational qualification, not an alpha-controlled proof of90% population success.',
        'No hyperparameter changes or additional attempts after openingV2 qualification.']}
    PROTOCOL.write_text(json.dumps(p,indent=2)+'\n');return p

def verify(p):
    for path,h in p['implementation_hashes'].items():
        if digest(ROOT/path)!=h:raise RuntimeError('implementation changed after freeze:'+path)
    for row in json.loads(SOURCES.read_text()):
        if digest(ROOT/f"data/benchmark_reference_v2/{row['name']}.txt")!=p['source_hashes'][row['name']]:raise RuntimeError('source changed')
    if digest(ROOT/'data/english_reference/alice.txt')!=p['alice_sha256']:raise RuntimeError('model source changed')

def run():
    if RESULT.exists():raise RuntimeError('qualification result exists; do not silently rerun frozen qualification')
    p=json.loads(PROTOCOL.read_text());verify(p);table,_=english_model(ROOT/'data/english_reference/alice.txt');library()
    started=time.monotonic();trials=[];summaries=[]
    with ThreadPoolExecutor(max_workers=p['workers']) as pool:
        for scenario in p['scenarios']:
            fs=[fixture(i,scenario['codes'],scenario['distribution']) for i in range(FIXTURES)]
            futures=[pool.submit(solve,f['train'],table,seed=f['seed']+900000,**p['solver_budget']) for f in fs]
            subset=[]
            for f,future in zip(fs,futures):
                fit=future.result();hold=[c for seq in f['hold'] for c in seq];truth=f['truth_hold']
                accuracies=[]
                for bank in fit['banks']:
                    decoded=''.join(chr(bank['mapping'][c]+65) for c in hold)
                    accuracies.append(sum(a==b for a,b in zip(decoded,truth))/len(truth))
                decoded=''.join(chr(fit['mapping'][c]+65) for c in hold);correct=sum(a==b for a,b in zip(decoded,truth))
                row={'scenario':scenario,'fixture':f['fixture'],'source':f['source'],'offset':f['offset'],'text_hash':f['text_hash'],
                  'seed':f['seed'],'holdout_letters':len(truth),'correct_holdout_letters':correct,'character_accuracy':correct/len(truth),
                  'passes':correct/len(truth)>=.95,'selected_bank':fit['selected_bank'],'bank_accuracies':accuracies,
                  'bank_objectives':[b['objective'] for b in fit['banks']],'baseline_character_accuracy':accuracies[0],
                  'unseen_positions':f['unseen_positions'],'mapping':fit['mapping'],'train_score':fit['train_score'],
                  'runtime_seconds':fit['total_runtime_seconds'],'literal_preview':decoded[:160],'true_preview':truth[:160]}
                trials.append(row);subset.append(row)
                (ROOT/'results/homophonic_benchmark_v2_checkpoint.json').write_text(json.dumps({'complete':False,'finished_fits':len(trials),'trials':trials},indent=2)+'\n')
                print(json.dumps({k:row[k] for k in ['scenario','fixture','character_accuracy','baseline_character_accuracy','selected_bank']}),flush=True)
            passed=sum(t['passes'] for t in subset);baseline=sum(t['baseline_character_accuracy']>=.95 for t in subset)
            summaries.append({'scenario':scenario,'fixtures':30,'passed_fixtures':passed,'baseline_passed_fixtures':baseline,
              'mean_character_accuracy':float(np.mean([t['character_accuracy'] for t in subset])),
              'baseline_mean_character_accuracy':float(np.mean([t['baseline_character_accuracy'] for t in subset])),
              'passes_gate':passed>=27})
    verify(p)
    result={'complete':True,'protocol_sha256':digest(PROTOCOL),'frozen_protocol':p,'trials':trials,'scenarios':summaries,
      'overall_gate_passes':all(s['passes_gate'] for s in summaries),'runtime_seconds':time.monotonic()-started,
      'limits':p['limits']+['Passing synthetic qualifications is not a translation or proof of matching Tibia mechanism.']}
    RESULT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(summaries,indent=2),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--freeze',action='store_true');ap.add_argument('--run',action='store_true');a=ap.parse_args()
    if a.freeze:print(json.dumps(freeze(),indent=2))
    if a.run:run()
