#!/usr/bin/env python3
"""Complete offline replay of exact columnar tests and independent certificates."""
import json
import random

from columnar_pair_experiment import (PROTOCOL, RESULT, ROOT, digest, fixture,
                                      game_pairs, positive_trial, verify)
from columnar_prefix_audit import certificates
from exact_columnar_keys import encrypt, fit_pair


def main():
    manifest = json.loads((ROOT / 'data/round13_evidence_manifest.json').read_text())
    for path, expected in manifest['sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('round13 artifact changed: ' + path)
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    r = json.loads(RESULT.read_text())
    if not r['complete'] or r['protocol_sha256'] != digest(PROTOCOL):
        raise ValueError('incomplete result or changed protocol')
    if len(r['positive_trials']) != 930 or len(r['gates']) != 31:
        raise ValueError('missing known-key fixtures')
    for row in r['positive_trials']:
        f = fixture(row['fixture'], row['width'])
        if row['truth'] != f:
            raise ValueError('positive fixture changed')
        if {'fixture': row['fixture'], 'width': row['width'], 'truth': f,
            **positive_trial(f, row['width'], p)} != row:
            raise ValueError('known-key inference changed')
    for gate in r['gates']:
        rows = [row for row in r['positive_trials'] if row['width'] == gate['width']]
        if len(rows) != 30:
            raise ValueError('width qualification missing replicates')
        feasible = sum(row['inference']['status'] == 'SAT' for row in rows)
        exact = sum(row['unique_exact_key'] and row['all_keys_predict_held_exactly'] and row['unique_held_decryption_exact'] for row in rows)
        if (feasible, exact, feasible == 30 and exact >= 27) != (gate['feasible'], gate['unique_exact_key_and_held'], gate['passes']):
            raise ValueError('width gate inconsistent')
    if not r['all_positive_gates_pass'] or not all(g['passes'] for g in r['gates']):
        raise ValueError('known-key engine not qualified')
    if len(r['ambiguity_controls']) != 30:
        raise ValueError('missing ambiguity controls')
    for row in r['ambiguity_controls']:
        f = fixture(row['fixture'], 16, ambiguous=True)
        inferred = positive_trial(f, 16, p)
        distinct = len({encrypt(f['held_source'], key) for key in inferred['inference']['keys']})
        expected = {'fixture': row['fixture'], 'truth': f, **inferred,
                    'retained_distinct_held_predictions': distinct}
        if expected != row or row['unique_exact_key'] or int(row['inference']['key_count']) <= 1:
            raise ValueError('ambiguous identities incorrectly identified')
    if not r['ambiguity_gate_pass']:
        raise ValueError('ambiguity guard failed')
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    source = next(b['digits'] for b in books if b['id'] == '22')
    target = json.loads((ROOT / 'data/external_book_round10.json').read_text())['digits']

    def fitted(s, t):
        return fit_pair(s, t, p['widths'], p['state_cap'], p['key_cap'])

    if fitted(source, target) != r['primary'] or r['primary']['status'] != 'UNSAT' or r['primary']['unresolved_parameterizations']:
        raise ValueError('primary exact feasibility changed')
    audit = json.loads((ROOT / 'results/columnar_prefix_certificates.json').read_text())
    proof = certificates(source, target, p['widths'])
    if proof != audit['certificates'] or len(proof) != 248 or any(c is None for c in proof):
        raise ValueError('independent prefix certificate changed')
    if audit['protocol_sha256'] != digest(PROTOCOL) or not audit['performed_after_primary_outcome']:
        raise ValueError('certificate provenance changed')
    for null in r['nulls']:
        if len(null['trials']) != 99:
            raise ValueError('missing exact-fit nulls')
        for i, row in enumerate(null['trials']):
            units = list(target) if null['mode'] == 'digit_shuffle' else [target[j:j + 8] for j in range(0, len(target), 8)]
            random.Random(p['nulls']['seed'] + i).shuffle(units)
            if fitted(source, ''.join(units)) != row['result']:
                raise ValueError('full-family null search changed')
    pairs = game_pairs(books)
    if len(pairs) != 10 or len(r['secondary_pairs']) != 10:
        raise ValueError('anagram-pair inventory changed')
    for (a, b), row in zip(pairs, r['secondary_pairs'], strict=True):
        if {'source': a['id'], 'target': b['id'], 'result': fitted(a['digits'], b['digits'])} != row:
            raise ValueError('secondary exact feasibility changed')
    if r['cross_pair_predictions'] or r['english_outputs'] or r['verified_translations']:
        raise ValueError('unexpected prediction or semantic output')
    print('Replayed30known-pair controls at each width2..32:927/930unique true keys predict/decrypt173held digits exactly.')
    print('Replayed30identical-column controls; physical key ambiguity preserved, not labeled unique.')
    print('Kharos/book22:0/248parameterizations fit; independent248prefix certificates verified.')
    print('Replayed full-family fits on198histogram-preserving nulls and10directed real anagram pairs.')
    print('Scope:relation between two supplied raw strings, not a ciphertext-only language decoder.')
    print('English outputs:0. Verified translations:0.')


if __name__ == '__main__':
    main()
