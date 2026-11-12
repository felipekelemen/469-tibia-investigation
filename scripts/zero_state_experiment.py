#!/usr/bin/env python3
"""Bounded state/metadata consistency tests; no English, key search or raw parsing."""
import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import random
import time

from zero_rule_constraints import alignments
from zero_rule_experiment import shuffled_books
from zero_state_constraints import FAMILIES, emit, planted_encode, solve

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'data/zero_state_protocol.json'
RESULT = ROOT / 'results/zero_state_constraints.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze():
    if PROTOCOL.exists():
        raise RuntimeError('already frozen')
    paths = ['data/normalized_books.json', 'data/normalized_splits.json', 'data/book_location_listing.json',
             'results/book_metadata_audit.json', 'scripts/zero_state_constraints.py',
             'scripts/zero_state_experiment.py', 'scripts/zero_rule_constraints.py',
             'scripts/zero_rule_experiment.py']
    p = {'version': 'ZERO_STATE_METADATA_V1', 'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'families': FAMILIES, 'alignment_cap': 4096, 'search_node_cap': 100000,
         'seed': 94690000, 'shuffle_replicates': 39, 'shelf_permutations': 39,
         'positive_books_each_family': 8, 'positive_codes_each_book': 24,
         'positive_retry_cap_per_book': 200,
         'positive_generation': 'Seeded shared hash action per state key. For raw-length-conditioned rules enumerate admissible final lengths and retain an actual fixed point; retry random synthetic code streams when none exists. This is not universal encoder qualification.',
         'scope': 'Existence of any deterministic Boolean state lookup that serializes the supplied code streams. Not token recovery, original author key discovery or translation.',
         'available_inputs': {'raw_length': 'Observable from digits; may condition a noncausal consistency rule.',
                              'token_length': 'Oracle input from imported tokenization, unavailable for raw-only decoding.',
                              'shelf_ordinal': 'Community listing category, unverified physical geometry; all71occurrences retained.'},
         'alignment_policy': 'Recompute state from the complete prefix for every compatible alignment. Never pin an ambiguous occurrence to one recorded annotation.',
         'fallbacks_frozen_before_results': ['preserve_zero', 'code_majority_averaged_over_all_training_alignments; ties preserve'],
         'validation': 'Existing exposed68/2 split by content. Shelf models have69training occurrences because book61is duplicated; copies never split across train/test.',
         'shuffle_control': 'Within-code, within-book omission shuffles preserve every book raw length and per-code counts. Expand duplicated shelf occurrences only after shuffling unique source books.',
         'shelf_control': 'Permute the40source shelf ordinals bijectively, retaining bookcase membership and both occurrences of duplicated book61; fit only shelf families.',
         'statistics': 'Logical SAT/UNSAT compatibility, no semantic pvalues or claims of independent repeated windows.',
         'stop_rule': 'Execute this fixed18family batch. No larger lookup/state grid solely to absorb remaining exceptions; require new serialization/source evidence before expanding.',
         'hashes': {f: digest(ROOT / f) for f in paths},
         'limits': ['All results condition on the community code sequence; another tokenization can escape these exclusions.',
                    'Final raw-length-conditioned rules need fixed-point consistency and do not by themselves define an encoder for every input.',
                    'Shelf list numbers are not x/y/z coordinates or authenticated historical object positions.',
                    'A fitting table can memorize state labels and is not an English translation; reserved books are already exposed.',
                    'Alignment/search caps yield unresolved, not rejection.']}
    PROTOCOL.write_text(json.dumps(p, indent=2) + '\n')


def verify(p):
    for f, expected in p['hashes'].items():
        if digest(ROOT / f) != expected:
            raise ValueError('frozen input/code changed: ' + f)


def expand_locations(books, locations):
    byid = {b['id']: b for b in books}
    return [{**byid[x['origin_book_id']], 'id': f"{x['origin_book_id']}@{x['library_number']}",
             'origin_book_id': x['origin_book_id'], 'shelf_ordinal': x['shelf_ordinal'],
             'shelf_name': x['shelf_name']} for x in locations]


def domain(books, locations, spec):
    return expand_locations(books, locations) if spec['seed'] == 'shelf_ordinal' else books


def majority(books, aa):
    count, omitted = collections.Counter(), collections.Counter()
    for book, a in zip(books, aa):
        for i, code in enumerate(book['codes']):
            if code.startswith('0'):
                count[code] += 1
                omitted[code] += sum(i in path for path in a['paths']) / len(a['paths'])
    return {c: omitted[c] > n / 2 for c, n in count.items()}


def fit_one(books, locations, ids, spec, p):
    dataset = domain(books, locations, spec)
    train = [b for b in dataset if b.get('origin_book_id', b['id']) in ids]
    reserved = [b for b in dataset if b.get('origin_book_id', b['id']) not in ids]
    aa = [alignments(b, p['alignment_cap']) for b in train]
    fit = solve(train, aa, spec, p['search_node_cap'])
    predictions = None
    if fit['status'] == 'SAT':
        table = {tuple(x['feature']): x['omit'] for x in fit['table']}
        predictions = {name: [emit(b, spec, table, fallback) for b in reserved]
                       for name, fallback in [('preserve_zero', {}), ('code_majority', majority(train, aa))]}
    return {'family': spec, 'training_occurrences': len(train), 'reserved_occurrences': len(reserved),
            'fit': fit, 'predictions': predictions}


def positive_corpus(spec, seed, p):
    rng = random.Random(seed)
    output = []
    retries = 0
    for i in range(p['positive_books_each_family']):
        success = None
        for attempt in range(p['positive_retry_cap_per_book']):
            codes = [rng.choice(['00', '01', '02', '04', '07', '09']) if rng.random() < .4 else
                     f'{rng.randrange(10, 100):02d}' for _ in range(p['positive_codes_each_book'])]
            codes = ['38' if c == '39' else c for c in codes]
            template = {'id': str(i), 'codes': codes, 'digits': '', 'shelf_ordinal': rng.randrange(1, 41)}
            zero = sum(c.startswith('0') for c in codes)
            lengths = range(2 * len(codes) - zero, 2 * len(codes) + 1) if spec['seed'] == 'raw_length' else [0]
            for candidate in lengths:
                template['digits'] = 'X' * candidate  #length input only; never emitted
                raw, mask = planted_encode(template, spec, seed)
                if spec['seed'] != 'raw_length' or len(raw) == candidate:
                    success = {**template, 'digits': raw, 'omitted_zero_code_indices': mask}
                    break
            if success:
                retries += attempt
                output.append(success)
                break
        if success is None:
            raise RuntimeError('positive fixed point could not be constructed within cap')
    return output, retries


def run():
    if RESULT.exists():
        raise RuntimeError('completed result exists')
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    start = time.monotonic()
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    locations = json.loads((ROOT / 'data/book_location_listing.json').read_text())['locations']
    ids = set(json.loads((ROOT / 'data/normalized_splits.json').read_text())['discovery_book_ids'])
    observed = []
    for spec in FAMILIES:
        row = fit_one(books, locations, ids, spec, p)
        observed.append(row)
        print(spec['name'], row['fit']['status'], flush=True)
    positives = []
    for index, spec in enumerate(FAMILIES):
        corpus, retries = positive_corpus(spec, p['seed'] + index, p)
        fit = solve(corpus, [alignments(b, p['alignment_cap']) for b in corpus], spec, p['search_node_cap'])
        positives.append({'family': spec['name'], 'expected': 'SAT', 'actual': fit['status'],
                          'books': len(corpus), 'generator_retries': retries,
                          'dataset_sha256': hashlib.sha256(json.dumps(corpus, sort_keys=True).encode()).hexdigest()})
    shuffled = []
    for i in range(p['shuffle_replicates']):
        corpus = shuffled_books(books, p['seed'] + 10000 + i)
        fits = [fit_one(corpus, locations, ids, spec, p) for spec in FAMILIES]
        shuffled.append({'replicate': i, 'seed': p['seed'] + 10000 + i,
                         'changed_books': sum(a['digits'] != b['digits'] for a, b in zip(corpus, books)),
                         'fits': {r['family']['name']: r['fit']['status'] for r in fits}})
    permuted = []
    ordinals = sorted({x['shelf_ordinal'] for x in locations})
    for i in range(p['shelf_permutations']):
        permutation = ordinals[:]
        random.Random(p['seed'] + 20000 + i).shuffle(permutation)
        mapping = dict(zip(ordinals, permutation))
        changed = [{**x, 'shelf_ordinal': mapping[x['shelf_ordinal']]} for x in locations]
        fits = [fit_one(books, changed, ids, spec, p) for spec in FAMILIES if spec['seed'] == 'shelf_ordinal']
        permuted.append({'replicate': i, 'permutation': mapping,
                         'fits': {r['family']['name']: r['fit']['status'] for r in fits}})
    verify(p)
    out = {'complete': True, 'protocol': p, 'protocol_sha256': digest(PROTOCOL), 'families': observed,
           'positive_controls': positives, 'all_positives_pass': all(x['actual'] == 'SAT' for x in positives),
           'shuffled_controls': shuffled, 'shelf_permutations': permuted,
           'new_raw_decoders': 0, 'new_english_decodings': 0, 'verified_translations': 0,
           'runtime_seconds': time.monotonic() - start, 'limits': p['limits']}
    RESULT.write_text(json.dumps(out, indent=2) + '\n')
    print('Positive controls', out['all_positives_pass'], 'runtime', out['runtime_seconds'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
        print('State/metadata protocol frozen.')
    if args.run:
        run()
