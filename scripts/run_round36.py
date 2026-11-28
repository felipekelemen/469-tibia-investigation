#!/usr/bin/env python3
"""Verify conditional anchor partitions; optionally repeat the full experiment."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
from round36_experiment import (ROOT, check_witnesses, decode_key, emit, load,
                                prepare, run, summarize, verify)
from unit_morphism_lexicon import banks


def result(path):
    return json.loads(gzip.decompress(path.read_bytes())) if path.name.endswith('.gz') else json.loads(path.read_text())


def strip_resources(value):
    if isinstance(value, dict):
        return {k: strip_resources(v) for k,v in value.items()
                if k not in ['resources','budget_wall_seconds_including_qualification']}
    if isinstance(value, list):
        return [strip_resources(v) for v in value]
    return value


def audit():
    for path in ['data/round36_input_manifest.json', 'data/round36_execution_manifest.json',
                 'data/round36_result_manifest.json']:
        verify(path)
    fixtures = load('data/round36_fixtures.json')
    assert prepare() == fixtures
    lexicon = set(banks()[0]['grapheme1_3'].reverse)
    summary = load('results/round36/summary.json')
    qualifications = load('results/round36/qualification.json')
    assert [r['id'] for r in qualifications] == [r['id'] for r in fixtures['tiny']]
    assert all(r['all_marginal_counts_and_message_uniqueness_match'] for r in qualifications)
    old_counts = {r['id']: r for r in load('results/round33_counts.json')['cases']}
    witness_count = 0
    main = None
    for case, row in zip(fixtures['targets'], summary['targets']):
        assert case['id'] == row['id']
        actual = result(ROOT / 'results/round36' / (case['id']+'.json.gz'))
        expected = dict(id=case['id'],kind=case['kind'],**summarize(actual),
                        witnesses_checked=check_witnesses(actual,case['words'],lexicon),
                        resources=actual.get('resources'))
        assert expected == row
        assert actual['complete'] and actual['count'] == old_counts[case['id']]['count']
        witness_count += expected['witnesses_checked']
        if case['id'] == 'knightmare':
            main = actual
    assert len(summary['targets']) == len(fixtures['targets']) == 6
    checks = load('results/round36/independent_checks.json')
    required = set()
    for group in main['marginals']:
        rows = group['rows']
        if rows:
            selected = [min(rows,key=lambda r:r[0]), min(rows,key=lambda r:(int(r[1]),r[0])),
                        min(rows,key=lambda r:(-int(r[1]),r[0]))]
            required.update((group['raw'],r[0],r[1]) for r in selected)
    required.update(('3478',w,'0') for w in ['BEHOLDER','BONELORD'])
    assert [(r['raw'],r['word'],r['expected']) for r in checks] == sorted(required)
    assert all(r['matches'] and r['result']['complete'] and r['result']['count'] == r['expected'] for r in checks)
    review = load('results/round36/unique_frames.json')
    frames = {}
    for word,n,first,second in main['marginals'][6]['rows']:
        if second is None:
            phrase = [emit(g,decode_key(first)) for g in fixtures['targets'][0]['words']]
            frames.setdefault(tuple(phrase[:-1]),[]).append(word)
    assert [{'first_six_words':list(k),'last_word_values':v} for k,v in frames.items()] == review['frames']
    assert sum(map(len,frames.values())) == review['unique_anchor_word_values']
    return {'round':36,'arithmetic_qualification_cases':len(qualifications),
            'total_whole_keys_enumerated_in_qualification':sum(r['whole_keys_enumerated'] for r in qualifications),
            'complete_target_and_control_counts':6,'old_R33_counts_matched':6,
            'literal_key_witnesses_verified':witness_count,
            'independent_conditional_counts_matching':len(checks),
            'unique_anchor_word_values_in_345':review['unique_anchor_word_values'],
            'unique_conditional_message_frames':len(frames),
            'translation_validated':False,'scope':'Conditional arithmetic and literal witness verification; lexical or conditional uniqueness is not semantic authentication.'}


def replay():
    with tempfile.TemporaryDirectory(prefix='469-round36-replay-') as name:
        directory = Path(name)/'run'
        run(directory)
        for filename in ['qualification.json','summary.json','independent_checks.json']:
            assert strip_resources(result(directory/filename)) == strip_resources(result(ROOT/'results/round36'/filename)), filename
        for case in load('data/round36_fixtures.json')['targets']:
            filename = case['id']+'.json.gz'
            assert strip_resources(result(directory/filename)) == strip_resources(result(ROOT/'results/round36'/filename)), filename
    return {'all_60_arithmetic_cases_repeated':True,'all_6_censuses_repeated':True,
            'all_22_conditional_counts_repeated':True,'scientific_outputs_identical':True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    output = audit()
    if args.full:
        output['replay'] = replay()
    if args.output:
        args.output.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))
