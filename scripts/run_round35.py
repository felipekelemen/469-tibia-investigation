#!/usr/bin/env python3
"""Public-only audit; independent literal/scoring checks, optional full replay.

The oracle search is deliberately not imported by the witness verifier.
Nothing here authenticates the semantics or original production of game text.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifests():
    count = 0
    for path in ['data/round35_prerun_manifest.json', 'data/round35_execution_manifest.json',
                 'data/round35_oracle_manifest.json', 'data/round35_result_manifest.json']:
        if not (ROOT / path).exists() and path.endswith('result_manifest.json'):
            continue
        for name, expected in load(path)['sha256'].items():
            assert digest(ROOT / name) == expected, name
            count += 1
    return count


def independent_model():
    """Parse the file into words, unlike the search's numeric word IDs."""
    spec = load('data/round35_model_manifest.json')
    path = ROOT / spec['path']
    if not path.exists():
        subprocess.run([sys.executable, str(ROOT / 'scripts/round35_fixtures.py'),
                        '--model-only'], cwd=ROOT, check=True)
    assert digest(path) == spec['sha256'] and path.stat().st_size == spec['bytes']
    lines = iter(path.read_text().splitlines())
    count = int(next(lines))
    words, frequencies = [], {}
    for _ in range(count):
        word, frequency = next(lines).split()
        words.append(word)
        frequencies[word] = int(frequency)
    pairs = {}
    for _ in range(int(next(lines))):
        a, b, frequency = map(int, next(lines).split())
        pairs[words[a], words[b]] = frequency
    assert next(lines, None) is None and words[0] == '<s>'
    settings = load('data/round35_protocol.json')['score']
    smooth = settings['additive_smoothing']
    norm = smooth * (len(words) - 1)
    total = sum(v for k, v in frequencies.items() if k != '<s>')

    def score(forms):
        components = []
        for before, word in zip(['<s>'] + forms[:-1], forms):
            components.append(settings['unigram_weight'] *
                              (math.log(frequencies[word] + smooth) - math.log(total + norm)))
            components.append(settings['bigram_weight'] *
                              (math.log(pairs.get((before, word), 0) + smooth) -
                               math.log(frequencies[before] + norm)))
        return math.fsum(components)
    return set(words[1:]), score


def translate(groups, key):
    return [''.join(key[d] for d in group) for group in groups]


def audit():
    references = verify_manifests()
    protocol = load('data/round35_protocol.json')
    fixtures = load('data/round35_fixtures.json')
    cases = {c['id']: c for c in fixtures['cases']}
    assert len(cases) == len(fixtures['cases']) == 480
    assert set(protocol['language_model_sources']).isdisjoint(protocol['qualification_sources'])
    lexical, score = independent_model()
    source_forms = set()
    for case in cases.values():
        if case['expected'] is not None:
            expected = ([''.join(case['expected'])] if case['scenario'] == 'unspaced'
                        else case['expected'])
            assert translate(case['input'], case['key']) == expected, case['id']
        assert translate(case['probes'], case['key']) == case['probe_truth'], case['id']
        assert all(re.fullmatch('[a-z]{1,3}', u) for u in case['key'].values())
        if case['scenario'] == 'natural7':
            assert tuple(case['expected']) not in source_forms
            source_forms.add(tuple(case['expected']))
            assert len(case['input']) == 7 and set(case['expected']) <= lexical
            assert 7 <= len(case['key']) <= 10 and any(len(u) > 1 for u in case['key'].values())
        if case['scenario'] in ['uniform_null', 'within_group_shuffle']:
            base = cases[case['id'].replace(case['scenario'], 'natural7')]
            assert list(map(len, case['input'])) == list(map(len, base['input']))
            if case['scenario'] == 'within_group_shuffle':
                assert case['input'] != base['input']
                assert list(map(Counter, case['input'])) == list(map(Counter, base['input']))
        if case['scenario'] == 'missing_digit':
            assert case['removed_digit'] not in ''.join(case['input'])
            assert all(case['removed_digit'] in p for p in case['probes'])
        if case['scenario'] == 'ambiguous_pair':
            assert [translate(case['input'], key) for key in case['alternative_keys']] == case['alternative_plaintexts']
            assert case['alternative_plaintexts'][0] != case['alternative_plaintexts'][1]
    assert len(source_forms) == 60
    # Check actual selected input text against the LM training sentences, in
    # addition to the author/source split; common individual words are expected.
    from round35_fixtures import body, words
    training_segments = {tuple(words(s)) for p in protocol['language_model_sources']
                         for s in re.split('[.!?]+', body(p))}
    overlap = sorted(source_forms & training_segments)
    assert not overlap, overlap
    result = load('results/round35_qualification.json')
    assert [r['id'] for r in result['cases']] == list(cases)
    from round35_experiment import evaluate, summarize
    for row in result['cases']:
        assert evaluate(cases[row['id']], row['fit'], protocol) == row
    assert summarize(result['cases'], protocol) == result['summary']
    note = load('results/round35_technical_replay.json')
    assert digest(ROOT / 'results/round35_qualification.json') == note['original_result_sha256']
    assert note['original_row'] == result['cases'][note['affected_index_zero_based']]
    replay = note['unchanged_replay_row']
    assert evaluate(cases[replay['id']], replay['fit'], protocol) == replay
    assert {k:v for k,v in replay.items() if k != 'fit'} == {k:v for k,v in note['original_row'].items() if k != 'fit'}
    oracle = load('results/round35_oracle.json')
    natural_ids = [c['id'] for c in cases.values() if c['scenario'] == 'natural7']
    assert [r['id'] for r in oracle['cases']] == natural_ids
    witness_count, either, same, replacement, below = 0, 0, 0, 0, 0
    examples = []
    for row in oracle['cases']:
        case = cases[row['id']]
        truth_score = score(case['expected'])
        assert math.isclose(truth_score, row['true_score'], abs_tol=1e-10)
        is_below = truth_score / 7 < protocol['score']['minimum_mean_log_score']
        assert is_below == row['true_below_acceptance_threshold']
        below += is_below
        either += bool(row['witnesses'])
        kinds = []
        for witness in row['witnesses']:
            witness_count += 1
            key = witness['key']
            assert set(key) == set(''.join(case['input']))
            assert all(re.fullmatch('[a-z]{1,3}', u) for u in key.values())
            output = translate(case['input'], key)
            assert output == witness['training_output'] and set(output) <= lexical
            actual = score(output)
            assert math.isclose(actual, witness['score'], abs_tol=1e-10)
            assert actual + 1e-10 >= truth_score
            index = witness['probe_index']
            prediction = translate([case['probes'][index]], key)[0]
            assert prediction == witness['probe_output'] != case['probe_truth'][index]
            assert witness['probe_truth'] == case['probe_truth'][index]
            if witness['kind'] == 'same_plaintext':
                assert output == case['expected']
            else:
                assert witness['kind'] == 'single_digit_replacement'
                assert sum(key[d] != case['key'][d] for d in key) == 1
            kinds.append(witness['kind'])
        same += 'same_plaintext' in kinds
        replacement += 'single_digit_replacement' in kinds
        if 'same_plaintext' in kinds and len(examples) < 2:
            w = next(w for w in row['witnesses'] if w['kind'] == 'same_plaintext')
            examples.append({'id': row['id'], 'input_english': ' '.join(case['expected']),
                             'true_key': case['key'], 'alternative_key': w['key'],
                             'probe': case['probes'][w['probe_index']],
                             'true_output': w['probe_truth'], 'alternative_output': w['probe_output']})
    summary = oracle['summary']
    assert [len(natural_ids), below, same, replacement, either] == [summary[k] for k in
        ['cases', 'true_below_acceptance_threshold', 'same_plaintext_transfer_counterexamples',
         'single_digit_equal_or_better_score_counterexamples', 'either_counterexample']]
    return {'round': 35, 'frozen_hash_references': references, 'fixtures_verified': len(cases),
            'unique_natural_input_segments': len(source_forms),
            'exact_normalized_training_sentence_overlap': len(overlap),
            'qualification_status_counts': dict(Counter(r['fit']['status'] for r in result['cases'])),
            'all_qualification_decisions_recomputed': True,
            'technical_replay_decision_unchanged': True,
            'independently_verified_witnesses': witness_count,
            'cases_with_counterexamples': either, 'same_plaintext_cases': same,
            'examples_are_synthetic_benchmark_not_469': examples,
            'external_peer_review': False, 'validated_translation': False,
            'scope': 'Internal independent implementation of literal witness and score checks; not source authentication, blind recovery or global impossibility.'}


def scientific_row(row):
    row = json.loads(json.dumps(row))
    for name in ['wall_seconds', 'child_cpu_seconds']:
        row['fit'].pop(name, None)
    return row


def full_replay():
    from round35_fixtures import prepare
    assert prepare(load('data/round35_protocol.json')) == load('data/round35_fixtures.json')
    assert digest(ROOT / load('data/round35_model_manifest.json')['path']) == load('data/round35_model_manifest.json')['sha256']
    with tempfile.TemporaryDirectory(prefix='469-round35-full-') as name:
        output = Path(name) / 'fits'
        subprocess.run([sys.executable, str(ROOT / 'scripts/round35_experiment.py'),
                        '--output', str(output)], cwd=ROOT, check=True,
                       stdout=(Path(name) / 'fit.log').open('w'))
        actual = json.loads((output / 'qualification.json').read_text())
    expected = load('results/round35_qualification.json')
    technical = load('results/round35_technical_replay.json')
    for a, b in zip(actual['cases'], expected['cases']):
        if b['id'] == technical['original_row']['id']:
            b = technical['unchanged_replay_row']
        assert scientific_row(a) == scientific_row(b), a['id']
    assert len(actual['cases']) == len(expected['cases']) == 480
    assert actual['summary']['decisions'] == expected['summary']['decisions']
    # Repeat the post-fit diagnostic without overwriting the published result.
    import round35_oracle
    with tempfile.TemporaryDirectory(prefix='469-round35-oracle-') as name:
        scratch = Path(name)
        (scratch / 'data').symlink_to(ROOT / 'data', target_is_directory=True)
        (scratch / 'results').mkdir()
        round35_oracle.ROOT = scratch
        round35_oracle.run()
        repeated = json.loads((scratch / 'results/round35_oracle.json').read_text())
    original = load('results/round35_oracle.json')
    repeated['summary'].pop('cpu_seconds')
    original['summary'].pop('cpu_seconds')
    assert repeated == original
    return {'fixture_and_model_regeneration': 'identical', 'qualification_rows_replayed': 480,
            'oracle_diagnostic_replayed': 60, 'scientific_outputs_identical': True,
            'technical_pause_case_compared_with_documented_replay': True,
            'replay_child_cpu_seconds': actual['summary']['total_cpu_seconds']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit()
    if args.full:
        result['full_replay'] = full_replay()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
