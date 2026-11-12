#!/usr/bin/env python3
"""Constructive limits of fitting formatter lookup tables. No semantic decoding."""
import hashlib
import itertools
import json
import pathlib

from zero_rule_constraints import alignments, feature, predict, serialize
from zero_rule_experiment import verify

ROOT = pathlib.Path(__file__).resolve().parents[1]


def rows(table):
    return [{'feature': list(key), 'omit': value} for key, value in sorted(table.items())]


def main():
    source = ROOT / 'results/zero_rule_constraints.json'
    study = json.loads(source.read_text())
    verify(study['protocol'])
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    split = json.loads((ROOT / 'data/normalized_splits.json').read_text())
    ids = set(split['discovery_book_ids'])
    train = [b for b in books if b['id'] in ids]
    hold = [b for b in books if b['id'] not in ids]
    cases = []
    for family in study['families']:
        fit = family['discovery_fit']
        if fit['status'] != 'SAT':
            continue
        spec = family['family']
        table = {tuple(row['feature']): row['omit'] for row in fit['table']}
        unknown = []
        for b in hold:
            for i, code in enumerate(b['codes']):
                if code.startswith('0'):
                    key = feature(b['codes'], i, spec)
                    if key not in table:
                        unknown.append({'book_id': b['id'], 'index': i, 'code': code, 'feature': list(key)})
        unique = sorted({tuple(x['feature']) for x in unknown})
        if not unique:
            raise AssertionError('expected unobserved features for this case')
        extension_a = {**table, **{key: False for key in unique}}
        extension_b = {**extension_a, unique[0]: True}
        for extension in [extension_a, extension_b]:
            assert all(predict(b, rows(extension), spec)['exact_raw'] for b in train)
        a = [predict(b, rows(extension_a), spec) for b in hold]
        bpred = [predict(b, rows(extension_b), spec) for b in hold]
        assert any(x['predicted_raw'] != y['predicted_raw'] for x, y in zip(a, bpred))
        # Retrospective oracle extension is explicitly fitted to the exposed
        # reserved answers; included only to exhibit how easy leakage would be.
        alternatives = [alignments(b, study['protocol']['alignment_cap'])['paths'] for b in hold]
        if any(x is None for x in alternatives):
            raise ValueError('alignment cap reached')
        oracle_extension = None
        for combination in itertools.product(*alternatives):
            candidate = table.copy()
            consistent = True
            for book, omitted in zip(hold, combination):
                mask = set(omitted)
                for i, code in enumerate(book['codes']):
                    if not code.startswith('0'):
                        continue
                    key = feature(book['codes'], i, spec)
                    action = i in mask
                    if key in candidate and candidate[key] != action:
                        consistent = False
                        break
                    candidate[key] = action
            if consistent:
                oracle_extension = candidate
                break
        oracle = None if oracle_extension is None else [predict(book, rows(oracle_extension), spec) for book in hold]
        if oracle:
            assert all(x['exact_raw'] for x in oracle)
            assert all(predict(book, rows(oracle_extension), spec)['exact_raw'] for book in train)
        cases.append({'family': spec['name'], 'discovery_table_entries': len(table),
                      'held_zero_events': sum(c.startswith('0') for book in hold for c in book['codes']),
                      'unobserved_held_events': unknown, 'unique_unobserved_held_features': len(unique),
                      'independent_boolean_extensions_on_unseen_features': str(2 ** len(unique)),
                      'two_extensions_both_exact_on_discovery': True,
                      'extension_a_preserve_all_unseen': a, 'extension_b_flip_one_unseen': bpred,
                      'retrospective_exposed_answer_fitted_extension': oracle,
                      'retrospective_extension_is_prediction': False})
    # Start-of-message collision excludes ANY amount of causal past history
    # with a common reset state, not just the eight-code implementation.
    start_certificate = next(x['discovery_fit']['certificate'] for x in study['families']
                             if x['family']['name'] == 'code_prev8')
    assert start_certificate['preserved']['code_index'] == start_certificate['omitted']['code_index'] == 0
    assert start_certificate['preserved']['code'] == start_certificate['omitted']['code']
    matrix_certificate = next(x['discovery_fit']['certificate'] for x in study['families']
                              if x['family']['name'] == 'code_prev1_phase16')
    x, y = matrix_certificate['preserved'], matrix_certificate['omitted']
    byid = {b['id']: b for b in books}
    assert x['book_id'] == y['book_id']
    assert byid[x['book_id']]['codes'][x['code_index'] - 1] == byid[y['book_id']]['codes'][y['code_index'] - 1]
    assert all((x['code_index'] + phase) % 16 == (y['code_index'] + phase) % 16 for phase in range(16))
    out = {'input_result_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'implementation_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           'lookup_identifiability': cases,
           'common_reset_causal_formatter_counterexample': start_certificate,
           'common_reset_causal_scope': 'Imported code stream fixed. A shared deterministic zero formatter with the same initial state and only current/past codes cannot give different first-code actions. Different initial states, message length, metadata, lookahead, randomness and other tokenizations remain possible.',
           'same_book_period16_counterexample': matrix_certificate,
           'period16_scope': 'Same book/current code/previous code/cycle cell, even under any book-specific constant phase or fixed cell permutation. Does not test block-dependent state, mixing, lookahead or all uses of either skull matrix.',
           'verified_translations': 0}
    (ROOT / 'results/zero_rule_identifiability.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps([{k: row[k] for k in ['family', 'discovery_table_entries', 'held_zero_events', 'unique_unobserved_held_features', 'independent_boolean_extensions_on_unseen_features']} for row in cases], indent=2))


if __name__ == '__main__':
    main()
