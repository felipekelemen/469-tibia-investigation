#!/usr/bin/env python3
"""Frozen exact columnar-relation tests. No English scoring or repaired output."""
import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import random
import time

from exact_columnar_keys import apply, decrypt, encrypt, fit_pair, infer

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'data/columnar_pair_protocol.json'
RESULT = ROOT / 'results/columnar_pair_experiment.json'
SEED = 134690000


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(i, width, ambiguous=False):
    rng = random.Random(SEED + width * 1000 + i + (100000 if ambiguous else 0))
    if ambiguous:
        # Within each ragged length class, many columns are identical in the
        # fit string, but their identities matter on new text/length.
        rows = ''.join(rng.choice('0123456789') for _ in range(9))
        source = ''.join(c * width for c in rows)[:137]
    else:
        source = ''.join(rng.choice('0123456789') for _ in range(137))
    held = ''.join(rng.choice('0123456789') for _ in range(173))
    key = list(range(width))
    rng.shuffle(key)
    return {'source': source, 'target': encrypt(source, key), 'key': key,
            'held_source': held, 'held_target': encrypt(held, key)}


def positive_trial(f, width, p):
    result = infer(f['source'], f['target'], width, p['state_cap'], p['key_cap'])
    unique_exact = result['keys_complete'] and result['keys'] == [f['key']]
    predicts = (result['keys_complete'] and bool(result['keys'])
                and all(encrypt(f['held_source'], key) == f['held_target'] for key in result['keys']))
    decoded = unique_exact and decrypt(f['held_target'], result['keys'][0]) == f['held_source']
    return {'inference': result, 'unique_exact_key': unique_exact,
            'all_keys_predict_held_exactly': predicts, 'unique_held_decryption_exact': decoded}


def freeze():
    if PROTOCOL.exists():
        raise RuntimeError('protocol already frozen')
    paths = ['scripts/exact_columnar_keys.py', 'scripts/columnar_pair_experiment.py',
             'data/normalized_books.json', 'data/external_book_round10.json']
    p = {'version': 'EXACT_COLUMNAR_PAIR_V1', 'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'prior_exposure': 'All game digit texts and their raw anagram relations were already exposed. New exact-columnar outcomes not inspected before freezing.',
         'primary_hypothesis': 'Book22andKharos are related by a pure standard columnar transposition with arbitrary column order, ragged rows without padding, widths2..32. Both directions and global input/output reversals are allowed.',
         'widths': list(range(2, 33)), 'state_cap': 100000, 'key_cap': 256,
         'parameterizations': 248, 'key_space': 'All column-index permutations, NOT only natural or skull-ranked orders. Identical fit columns retain factorially many physical key identities.',
         'positive_fixtures_per_width': 30, 'positive_source_length': 137, 'positive_held_length': 173,
         'positive_design': 'IIDuniform decimal source/held strings, independent seeds perwidth/fixture, one random true key shared across fit and held. True width supplied for positive key identification; held target never used to select a key.',
         'positive_gates': 'At every width,30/30true family members must be SAT without unresolved budget; at least27/30must have one exact true key, predict the173digit held target exactly and decrypt it exactly.',
         'ambiguity_controls': '30width16sources with identical columns inside ragged length classes. Must report multiple exact key identities and no uniqueness, even though every retained key reproduces the fit target.',
         'nulls': {'modes': ['digit_shuffle', 'blocks8_shuffle'], 'replicates_each': 99,
                   'seed': SEED + 200000, 'policy': 'Preserve Kharos raw length and exact digit histogram; refit the entire248parameterization family with same budget per target.'},
         'secondary': 'All10directed pairs in5exact raw-histogram groups among70Hellgate books; exact raw only, no imported target tokens.',
         'cross_pair_prediction': 'If any primary keys fit, apply every retained key/config unchanged to the five canonical lower-ID→higher-ID pairs. Count exact predictions; do not choose direction per pair. IDs do not establish historical order.',
         'matrix_scope': 'Width16contains every skull-induced column-index ordering as a subset. This tests only a direct whole-book columnar relation, not arbitrary matrix ciphers, chronology, or either text as English plaintext.',
         'stopping': 'No padding, local reversals, arbitrary row orders, exceptions or wider keys added after outcomes. No English output or semantic conclusions from exact paired digit feasibility.',
         'hashes': {path: digest(ROOT / path) for path in paths}}
    PROTOCOL.write_text(json.dumps(p, indent=2) + '\n')


def verify(p):
    for path, expected in p['hashes'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('frozen input changed: ' + path)


def game_pairs(books):
    groups = collections.defaultdict(list)
    for b in books:
        groups[tuple(sorted(collections.Counter(b['digits']).items()))].append(b)
    return [(a, b) for group in groups.values() if len(group) > 1
            for a in group for b in group if a['id'] != b['id']]


def run():
    if RESULT.exists():
        raise RuntimeError('result already exists')
    start = time.monotonic()
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    positives, gates = [], []
    for width in p['widths']:
        rows = []
        for i in range(p['positive_fixtures_per_width']):
            f = fixture(i, width)
            row = {'fixture': i, 'width': width, 'truth': f, **positive_trial(f, width, p)}
            rows.append(row)
        feasible = sum(r['inference']['status'] == 'SAT' for r in rows)
        recovered = sum(r['unique_exact_key'] and r['all_keys_predict_held_exactly'] and r['unique_held_decryption_exact'] for r in rows)
        gates.append({'width': width, 'fixtures': 30, 'feasible': feasible,
                      'unique_exact_key_and_held': recovered, 'passes': feasible == 30 and recovered >= 27})
        positives.extend(rows)
        print('columnar width', width, 'gate', gates[-1], flush=True)
    ambiguity = []
    for i in range(30):
        f = fixture(i, 16, ambiguous=True)
        row = positive_trial(f, 16, p)
        predictions = {encrypt(f['held_source'], key) for key in row['inference']['keys']}
        ambiguity.append({'fixture': i, 'truth': f, **row,
                          'retained_distinct_held_predictions': len(predictions)})
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    source = next(b['digits'] for b in books if b['id'] == '22')
    target = json.loads((ROOT / 'data/external_book_round10.json').read_text())['digits']
    def fitted(raw_source, raw_target):
        return fit_pair(raw_source, raw_target, p['widths'], p['state_cap'], p['key_cap'])
    primary = fitted(source, target)
    print('columnar primary', primary['status'], 'fits', primary['satisfiable_parameterizations'], flush=True)
    nulls = []
    for mode in p['nulls']['modes']:
        rows = []
        for i in range(p['nulls']['replicates_each']):
            units = list(target) if mode == 'digit_shuffle' else [target[j:j + 8] for j in range(0, len(target), 8)]
            random.Random(p['nulls']['seed'] + i).shuffle(units)
            rows.append({'replicate': i, 'result': fitted(source, ''.join(units))})
        nulls.append({'mode': mode, 'trials': rows})
    secondary = [{'source': a['id'], 'target': b['id'], 'result': fitted(a['digits'], b['digits'])}
                 for a, b in game_pairs(books)]
    canonical = [(a, b) for a, b in game_pairs(books) if int(a['id']) < int(b['id'])]
    cross = []
    for row in primary['fits']:
        for key in row['result']['keys']:
            predictions = [{'source': a['id'], 'target': b['id'],
                            'exact': apply(a['digits'], row['config'], key) == b['digits']}
                           for a, b in canonical]
            cross.append({'config': row['config'], 'key': key, 'predictions': predictions})
    verify(p)
    out = {'complete': True, 'protocol_sha256': digest(PROTOCOL), 'positive_trials': positives,
           'gates': gates, 'all_positive_gates_pass': all(g['passes'] for g in gates),
           'ambiguity_controls': ambiguity,
           'ambiguity_gate_pass': all(r['inference']['status'] == 'SAT' and int(r['inference']['key_count']) > 1
                                      and not r['unique_exact_key'] for r in ambiguity),
           'primary': primary, 'nulls': nulls, 'secondary_pairs': secondary,
           'cross_pair_predictions': cross, 'runtime_seconds': time.monotonic() - start,
           'english_outputs': 0, 'verified_translations': 0,
           'scope': 'Exact known-pair feasibility only. No assumption that either real text is plaintext, no whole cipher-family exclusion and no plaintext semantics.'}
    RESULT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'all_positive_gates_pass': out['all_positive_gates_pass'],
                      'minimum_recovery_per_width': min(g['unique_exact_key_and_held'] for g in gates),
                      'ambiguity_gate_pass': out['ambiguity_gate_pass'], 'primary': primary,
                      'secondary_statuses': [r['result']['status'] for r in secondary],
                      'seconds': out['runtime_seconds']}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
        print('Exact columnar protocol frozen.')
    if args.run:
        run()
