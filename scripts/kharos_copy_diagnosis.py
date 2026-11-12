#!/usr/bin/env python3
"""Post-opening structural diagnosis. Not independent cipher confirmation."""
import hashlib
import json
import pathlib
import random
import time

from raw_fragment_cover import cover

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAN = ROOT / 'data/kharos_copy_diagnostic_plan.json'


def freeze():
    if PLAN.exists():
        raise RuntimeError('diagnostic plan already recorded')
    files = ['scripts/raw_fragment_cover.py', 'scripts/kharos_copy_diagnosis.py',
             'data/normalized_books.json', 'data/external_book_round10.json', 'results/copy_parser_experiment.json']
    p = {'role': 'Structural diagnosis after viewing copy-parser results; no blind validation claim.',
         'minimums': [1, 8, 12, 16], 'maximum': 96, 'seed': 105690000, 'replicates_each': 99,
         'statistic': 'minimum copied pieces at minimum1; every digit can be covered, so no semantic content test',
         'nulls': ['raw_digit_shuffle', 'raw_blocks8_shuffle'],
         'hashes': {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files},
         'limits': ['Minimum1can trivially cover any string using single digits; compare piece count, not coverage.',
                    'Matched blocks are not words or code units; copying can occur in real encrypted prose too.',
                    'The data were already opened and all references are public; pvalues, if reported, are exploratory structural ranks.']}
    PLAN.write_text(json.dumps(p, indent=2) + '\n')


def run():
    destination = ROOT / 'results/kharos_copy_diagnosis.json'
    if destination.exists():
        raise RuntimeError('diagnostic result exists')
    p = json.loads(PLAN.read_text())
    for f, h in p['hashes'].items():
        if hashlib.sha256((ROOT / f).read_bytes()).hexdigest() != h:
            raise ValueError('diagnostic dependency changed')
    start = time.monotonic()
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    raw = json.loads((ROOT / 'data/external_book_round10.json').read_text())['digits']
    observed = [cover(raw, books, minimum, p['maximum']) for minimum in p['minimums']]
    target = observed[0]['copied_pieces']
    controls = []
    for mode in p['nulls']:
        trials = []
        for i in range(p['replicates_each']):
            rng = random.Random(p['seed'] + 1000 * p['nulls'].index(mode) + i)
            parts = list(raw) if mode == 'raw_digit_shuffle' else [raw[j:j + 8] for j in range(0, len(raw), 8)]
            rng.shuffle(parts)
            permuted = ''.join(parts)
            assert len(permuted) == len(raw) and sorted(permuted) == sorted(raw)
            fit = cover(permuted, books, 1, p['maximum'])
            trials.append({'replicate': i, 'copied_pieces': fit['copied_pieces'],
                           'unchanged': permuted == raw})
        controls.append({'mode': mode, 'trials': trials,
                         'mean_copied_pieces': sum(x['copied_pieces'] for x in trials) / len(trials),
                         'exploratory_lower_tail_rank': (1 + sum(x['copied_pieces'] <= target for x in trials)) / (1 + len(trials))})
    out = {'plan': p, 'plan_sha256': hashlib.sha256(PLAN.read_bytes()).hexdigest(),
           'observed': observed, 'controls': controls, 'runtime_seconds': time.monotonic() - start,
           'code_layer_inferred': False, 'verified_translations': 0, 'limits': p['limits']}
    destination.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'observed': [{k: x[k] for k in ['minimum', 'uncovered_raw_digits', 'copied_pieces']} for x in observed],
                      'controls': [{k: x[k] for k in ['mode', 'mean_copied_pieces', 'exploratory_lower_tail_rank']} for x in controls]}, indent=2))


if __name__ == '__main__':
    freeze()
    run()
