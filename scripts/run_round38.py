#!/usr/bin/env python3
"""Audit all published conditional keys; optionally replay all 597 controls."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import random
import tempfile

from round36_experiment import ROOT, load, verify
from round38_experiment import (control_summary, execute, inspect_keys,
                                 prepare_qualification)
from round38_diagnostics import calculate as deductions
from unit_morphism_lexicon import banks


def read(path):
    data = path.read_bytes()
    if path.suffix=='.gz':data=gzip.decompress(data)
    return json.loads(data)


def strip_times(value):
    if isinstance(value,dict):
        return {k:strip_times(v) for k,v in value.items() if k not in ['wall_seconds','control_fit_wall_seconds']}
    if isinstance(value,list):return [strip_times(v) for v in value]
    return value


def verify_controls(fixtures):
    protocol = load('data/round38_protocol.json')['controls']
    rng = random.Random(protocol['seed'])
    original = fixtures['real']['groups']
    reconstructed = []
    for family in protocol['families']:
        for i in range(protocol['per_family']):
            if family=='pooled_other_digits_anchor_fixed':
                chars=list(''.join(original[:-1]));rng.shuffle(chars);words=[];offset=0
                for g in original[:-1]:
                    words.append(''.join(chars[offset:offset+len(g)]));offset+=len(g)
                words.append(original[-1])
            else:
                mapping={}
                for g in dict.fromkeys(original):
                    chars=list(g)
                    if family=='within_all_groups' or g!=original[-1]:rng.shuffle(chars)
                    mapping[g]=''.join(chars)
                words=[mapping[g] for g in original]
            assert list(map(len,words))==list(map(len,original))
            assert Counter(''.join(words))==Counter(''.join(original))
            if family!='within_all_groups':assert words[-1]==original[-1]
            if family!='pooled_other_digits_anchor_fixed':
                assert all(Counter(a)==Counter(b) for a,b in zip(words,original))
            reconstructed.append({'id':family+'_'+str(i),'family':family,'groups':words,'anchor_index':6,'anchor_word':'FOOL'})
    assert reconstructed==fixtures['controls']


def audit():
    for path in ['data/round38_input_manifest.json','data/round38_execution_manifest.json','data/round38_result_manifest.json']:
        verify(path)
    assert prepare_qualification()==load('data/round38_qualification_fixtures.json')
    fixtures = load('data/round38_fixtures.json')
    verify_controls(fixtures)
    q = load('results/round38/qualification.json')
    assert len(q)==70 and all(r['complete_keys_match_independent_brute'] for r in q)
    actual = read(ROOT/'results/round38/real_keys.json.gz')
    assert actual['complete'] and actual['count']==3976
    report = inspect_keys(actual['keys'],fixtures,set(banks()[0]['grapheme1_3'].reverse))
    assert json.loads(json.dumps(report))==load('results/round38/inspection.json')
    assert deductions()==load('results/round38/deductions.json')
    controls = load('results/round38/controls.json')
    assert len(controls)==len(fixtures['controls'])==597
    for row, case in zip(controls,fixtures['controls']):
        assert {k:row[k] for k in case}==case
        r=row['result']
        assert (r['count'] is not None)==r['complete']
    summary = load('results/round38/summary.json')
    assert control_summary(controls,actual['count'])==summary['controls']
    assert summary['distinct_training_strings']==report['distinct_training_strings']
    return {'round':38,'arithmetic_qualification_cases':70,'complete_conditional_keys_verified':3976,
            'controls':597,'complete_controls':sum(r['result']['complete'] for r in controls),
            'limited_controls':sum(not r['result']['complete'] for r in controls),
            'positive_complete_controls':sum(r['result']['complete'] and r['result']['count']>0 for r in controls),
            'unanimous_fragment_obstructions':len(deductions()['unchangeable_fragment_obstructions']),
            'mission_outcome':'I_inconclusive','new_validated_translation':None}


def replay():
    with tempfile.TemporaryDirectory(prefix='469-r38-replay-') as name:
        path=Path(name)/'results'
        execute(path)
        for filename in ['qualification.json','real_keys.json.gz','inspection.json','controls.json','summary.json']:
            assert strip_times(read(path/filename))==strip_times(read(ROOT/'results/round38'/filename)),filename
    return {'all_70_arithmetic_cases_repeated':True,'all_3976_real_keys_identical':True,
            'all_597_controls_repeated':True,'complete_and_limited_outcomes_identical':True,
            'all_transfer_diagnostics_identical':True}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--full',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=audit()
    if args.full:result['replay']=replay()
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
