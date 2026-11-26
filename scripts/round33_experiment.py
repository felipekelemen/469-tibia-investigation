#!/usr/bin/env python3
"""Frozen exact lexical key counting; no scoring, candidate repair or translation."""
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import resource
import subprocess
import tempfile
import time
from unit_morphism_lexicon import banks

ROOT=Path(__file__).resolve().parents[1]


def load(path):return json.loads((ROOT/path).read_text())
def save_new(path,obj):
    with (ROOT/path).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def compile_engine(directory):
    binary=Path(directory)/'count'
    subprocess.run(['g++','-O2','-std=c++17','-Wall','-Wextra',str(ROOT/'scripts/round33_count.cpp'),'-o',str(binary)],check=True,capture_output=True,text=True)
    subprocess.run([str(binary),'--arithmetic-test'],check=True,capture_output=True,text=True)
    return binary


def run_case(binary,lexicon,case,directory,budgets):
    path=Path(directory)/'case.txt'
    words=list(dict.fromkeys(case['words']));forced=case.get('forced',{})
    path.write_text(str(len(words))+'\n'+''.join(w+' '+forced.get(w,'-')+'\n' for w in words))
    def limits():
        limit=budgets['per_fit_address_space_bytes']
        resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
    started=time.monotonic()
    try:
        proc=subprocess.run([str(binary),str(lexicon),str(path)],capture_output=True,text=True,
                            timeout=budgets['per_fit_wall_seconds'],preexec_fn=limits)
        if proc.returncode:
            out={'complete':False,'count':None,'reason':'process_exit_'+str(proc.returncode),'stderr':proc.stderr[-1000:]}
        else:out=json.loads(proc.stdout)
    except subprocess.TimeoutExpired:
        out={'complete':False,'count':None,'reason':'wall_time_limit'}
    out['elapsed_seconds']=round(time.monotonic()-started,6)
    return out


def brute_count(words,lexicon):
    """Independent whole-key enumeration over every A/B unit of length1..3."""
    digits=sorted(set(''.join(words)))
    units=[''.join(u) for n in range(1,4) for u in product('AB',repeat=n)]
    count=0;forms=set(lexicon)
    for values in product(units,repeat=len(digits)):
        key=dict(zip(digits,values))
        if all(''.join(key[d] for d in raw) in forms for raw in words):count+=1
    return count


def prepare():
    rng=random.Random(334690033);tiny=[]
    pool=[''.join(p) for n in range(1,7) for p in product('AB',repeat=n)]
    for i in range(100):
        words=list(dict.fromkeys(''.join(rng.choice('012') for _ in range(rng.randint(1,4))) for _ in range(rng.randint(1,4))))
        lex=set(rng.sample(pool,rng.randint(3,14)))
        if i%2==0:
            key={d:''.join(rng.choice('AB') for _ in range(rng.randint(1,3))) for d in '012'}
            lex.update(''.join(key[d] for d in w) for w in words)
        tiny.append({'id':'tiny_'+str(i),'words':words,'lexicon':sorted(lex)})
    old=load('results/round23_targets.json');qual=load('results/round23_qualification.json')
    sourcefixtures=load('data/round23_fixtures.json');family='grapheme1_3'
    knight=next(r for r in old['targets'] if r['id']=='knightmare' and r['family']==family)
    cases=[{'id':'knightmare','kind':'real','words':knight['words'],'previous_returned_keys':len(knight['keys'])}]
    for name in ['BEHOLDER','BONELORD']:
        cases.append({'id':'knightmare_'+name,'kind':'previous_zero_regression','words':knight['words'],'forced':{'3478':name},'expected_count':'0'})
    for row in sourcefixtures['global']:
        if row['family']!=family:continue
        previous=next(r for r in qual['global'] if r['id']==row['id'])
        cases.append({'id':row['id'],'kind':'known_key_regression','words':row['train'],'true_key':row['key'],'previous_returned_keys':len(previous['keys'])})
    for row in old['nulls']:
        if row['family']==family and row['id'].startswith('knightmare_'):
            cases.append({'id':row['id'],'kind':'within_word_shuffle','words':row['words'],'previous_returned_keys':len(row['keys'])})
    rng=random.Random(load('data/round33_protocol.json')['uniform_seed'])
    for i in range(19):
        cases.append({'id':'uniform_'+str(i),'kind':'uniform_lengths','words':[''.join(rng.choice('0123456789') for _ in w) for w in knight['words']]})
    bank=banks()[0]['grapheme1_3'];lex=''.join(w+'\n' for w in sorted(bank.reverse))
    save_new('data/round33_fixtures.json',{'tiny_seed':334690033,'tiny':tiny,'cases':cases,'lexicon_forms':len(bank.reverse),'normalized_lexicon_sha256':hashlib.sha256(lex.encode()).hexdigest(),'scope':'Same CMU bank asR23. Tiny brute-force cases qualify arithmetic only; known keys are never passed to the count engine.'})


def qualify(binary,directory,fixtures,protocol):
    rows=[];lex=Path(directory)/'tiny_lexicon.txt'
    for case in fixtures['tiny']:
        lex.write_text('\n'.join(case['lexicon'])+'\n')
        expected=brute_count(case['words'],case['lexicon'])
        actual=run_case(binary,lex,case,directory,protocol['budgets'])
        if not actual['complete'] or int(actual['count'])!=expected:
            raise AssertionError((case['id'],expected,actual))
        rows.append({'id':case['id'],'independent_count':str(expected),'engine_count':actual['count']})
    return {'cases':rows,'all_counts_match':True,'scope':'Exact counts in100small A/B cases and128bit overflow guards; no semantic or English recovery qualification.'}


def verify_inputs():
    for path,sha in load('data/round33_input_manifest.json')['sha256'].items():
        if digest(path)!=sha:raise ValueError('Frozen input changed: '+path)


def execute():
    verify_inputs();fixtures=load('data/round33_fixtures.json');protocol=load('data/round33_protocol.json')
    bank=banks()[0]['grapheme1_3'];lex=''.join(w+'\n' for w in sorted(bank.reverse))
    assert hashlib.sha256(lex.encode()).hexdigest()==fixtures['normalized_lexicon_sha256']
    if (ROOT/'results/round33_counts.json').exists():raise FileExistsError('Preserve completed results')
    with tempfile.TemporaryDirectory(prefix='469-r33-') as directory:
        binary=compile_engine(directory)
        qualification=qualify(binary,directory,fixtures,protocol)
        save_new('results/round33_count_qualification.json',qualification)
        lexicon=Path(directory)/'lexicon.txt';lexicon.write_text(lex)
        records=[]
        for case in fixtures['cases']:
            actual=run_case(binary,lexicon,case,directory,protocol['budgets'])
            if case['kind']=='known_key_regression':
                assert all(''.join(case['true_key'][d] for d in w) in bank.reverse for w in case['words'])
            if actual['complete']:
                assert int(actual['count'])>=case.get('previous_returned_keys',0)
                if 'expected_count' in case:assert actual['count']==case['expected_count']
                if case['kind']=='known_key_regression':assert int(actual['count'])>=1
            records.append({'id':case['id'],'kind':case['kind'],**actual})
            (ROOT/'data/private/round33').mkdir(parents=True,exist_ok=True)
            (ROOT/'data/private/round33/checkpoint.json').write_text(json.dumps(records,indent=2)+'\n')
            print(case['id'],actual['complete'],actual['count'],actual.get('reason',''),actual['elapsed_seconds'],flush=True)
        save_new('results/round33_counts.json',{'cases':records})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');args=parser.parse_args()
    prepare() if args.prepare else execute()
