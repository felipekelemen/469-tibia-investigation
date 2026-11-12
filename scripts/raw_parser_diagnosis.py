#!/usr/bin/env python3
"""Explain V1 failures and develop longer-context models on OPENED fixtures.

This is not a fresh qualification. No Tibia data, key search or translation.
"""
import hashlib
import json
import math
import pathlib
import random
import time

from copied_homophonic_v3 import build_model
from raw_digit_decoder import CharacterLanguage, measures, omission_probability, serialize
from raw_parser_benchmark import fixture, passes, verify
from raw_parser_long_context import LongContextLanguage, decode

ROOT = pathlib.Path(__file__).resolve().parents[1]


def path_score(codes, omitted, key, probabilities, language, rule):
    history = ()
    previous = -1
    score = math.log(1 / 128)
    for i, code in enumerate(codes):
        q = omission_probability(rule, previous)
        action = q if i in omitted else (1 - q if code < 10 else 1)
        score += math.log(probabilities[code]) + math.log(action)
        score += language.log_probability(history, key[code]) + math.log(127 / 128)
        history = (history + (key[code],))[-3:]
        previous = code % 3
    return score


def main():
    started = time.monotonic()
    path = ROOT / 'results/raw_parser_v1.json'
    result = json.loads(path.read_text())
    verify(result['protocol'])
    language = CharacterLanguage(build_model()[0])
    diagnoses = []
    for row in result['trials']:
        if passes(row['oracle'], result['protocol']):
            continue
        f = fixture(row['fixture'], row['length'])
        true_score = path_score(row['truth_codes'], set(row['truth_omitted_indices']), f['key'], f['probabilities'], language, row['true_rule'])
        best_score = row['oracle']['log_evidence'] + math.log(row['oracle']['map_path_posterior'])
        gap = best_score - true_score
        if gap < -1e-8:
            raise AssertionError('exact decoder lost to a valid path')
        diagnoses.append({'fixture': row['fixture'], 'length': row['length'], 'rule': row['true_rule'],
                          'map_objective_advantage_over_truth': gap,
                          'truth_literal': row['truth_literal'], 'map_literal': row['oracle']['literal']})
    controls = []
    for mode in ['shuffle_codes', 'blocks8_codes']:
        rows = [c['oracle'] for row in result['trials'] for c in row['controls'] if c['mode'] == mode]
        wrong = [r for r in rows if not r['exact_path']]
        controls.append({'mode': mode, 'cases': len(rows), 'exact_paths': len(rows) - len(wrong),
                         'mean_character_edit_accuracy': sum(r['character_edit_accuracy'] for r in rows) / len(rows),
                         'wrong_paths_with_posterior_over95percent': sum(r['map_path_posterior'] > .95 for r in wrong),
                         'limit': 'Posterior is conditional on an approximate English model applied to order controls; not a real-world probability of correctness.'})
    # Fixed grid evaluated on all already opened cases. Selection only here;
    # this can never upgrade the V1 qualification or count as new validation.
    development = []
    for order, backoff in [(4, 1), (4, 10), (6, 1), (6, 10)]:
        model = LongContextLanguage(order, backoff)
        rows = []
        for row in result['trials']:
            f = fixture(row['fixture'], row['length'])
            raw, truth_path = serialize(row['truth_codes'], row['true_rule'], random.Random(row['seed'] + 500000))
            if raw != row['evaluation_raw']:
                raise AssertionError('fixture changed')
            fit = decode(raw, f['key'], f['probabilities'], model, row['true_rule'])
            m = measures(fit, truth_path, row['truth_literal'])
            rows.append({'fixture': row['fixture'], 'length': row['length'], 'rule': row['true_rule'],
                         'passes': passes(m, result['protocol']), **m})
        summary = {'order': order, 'backoff': backoff, 'cases': len(rows),
                   'passed': sum(r['passes'] for r in rows),
                   'minimum_character_edit_accuracy': min(r['character_edit_accuracy'] for r in rows),
                   'mean_character_edit_accuracy': sum(r['character_edit_accuracy'] for r in rows) / len(rows),
                   'cells': [{'length': n, 'rule': rule, 'passed': sum(r['passes'] for r in rows if r['length'] == n and r['rule'] == rule)}
                             for n in result['protocol']['lengths'] for rule in result['protocol']['true_rules']],
                   'trials': rows}
        development.append(summary)
        print('development', order, backoff, summary['passed'], flush=True)
    selected = max(development, key=lambda r: (min(c['passed'] for c in r['cells']), r['passed'], r['minimum_character_edit_accuracy'], -r['order'], -r['backoff']))
    out = {'input_result_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'implementation_hashes': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()
                                      for f in ['scripts/raw_parser_diagnosis.py', 'scripts/raw_parser_long_context.py']},
           'oracle_failures': diagnoses, 'objective_gaps_strictly_positive': all(r['map_objective_advantage_over_truth'] > 1e-8 for r in diagnoses),
           'controls': controls, 'development': development,
           'selected_for_future_qualification': {k: selected[k] for k in ['order', 'backoff', 'passed', 'cells']},
           'selection': 'max minimum cell pass count, then total passes, then minimum edit accuracy, then smaller order/backoff; all data opened V1 development',
           'training_sources': LongContextLanguage(4, 1).sources,
           'fresh_qualification_completed': False, 'new_game_key_fits': 0, 'verified_translations': 0,
           'source_quality_note': '64-letter fixture0 contains Roman-numeral table-of-contents text. V1 remains unchanged; do not describe every fixture as a grammatical English sentence.',
           'limits': ['Higher-order development receives true key, true emissions and true omission rule. Unknown-rule selection not tested in this development.',
                      'All four models were selected after V1 outcomes; new authors/data and a frozen protocol are necessary before qualification.',
                      'Exact MAP optimality is specific to this likelihood, not evidence of semantic correctness or absence of a cipher.'],
           'runtime_seconds': time.monotonic() - started}
    (ROOT / 'results/raw_parser_v1_diagnosis.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out['selected_for_future_qualification'], indent=2), flush=True)


if __name__ == '__main__':
    main()
