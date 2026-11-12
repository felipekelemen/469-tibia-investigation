#!/usr/bin/env python3
"""Freeze and run a paid-address raw/code-copy mechanism comparison."""
import argparse
import datetime
import hashlib
import json
import pathlib
import random
import time

from copy_wire_codec import build_index, encode, prepare
from homophonic_benchmark import letters
from raw_digit_decoder import serialize
from raw_parser_benchmark import encode_letters, key_and_emissions

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'data/copy_wire_protocol.json'
RESULT = ROOT / 'results/copy_wire_experiment.json'
SEED = 114690000
REFERENCES = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(i, content):
    source = 'wizard_oz' if i < 15 else 'peter_pan'
    if source not in REFERENCES:
        REFERENCES[source] = letters(ROOT / f'data/word_validator_reference/{source}.txt')
    offset = 10000 + (i % 15) * 5000
    text = REFERENCES[source][offset:offset + 4480]
    if len(text) != 4480:
        raise ValueError('not enough reference text')
    seed = SEED + i
    key, pmf = key_and_emissions(seed)
    codes = encode_letters(text, key, pmf, random.Random(seed))
    books, paths = [], []
    for j in range(70):
        piece = codes[j * 64:(j + 1) * 64]
        if content == 'shuffled_codes':
            random.Random(seed + 10000 + j).shuffle(piece)
        elif content != 'encrypted_english':
            raise ValueError('content condition')
        raw, path = serialize(piece, 'iid_0.3', random.Random(seed + 1000 + j))
        books.append({'id': str(j), 'codes': [f'{c:02d}' for c in piece], 'digits': raw})
        paths.append(path)
    schedule = random.Random(seed + 2000).sample(range(70), 4)
    targets = {'aligned': [], 'clipped': []}
    witnesses = []
    for j in schedule:
        path = paths[j]
        candidates = [s for s in range(8, 25)
                      if path[s]['end'] - path[s]['start'] == 2
                      and path[s + 31]['end'] - path[s + 31]['start'] == 2]
        start = random.Random(seed + 3000 + j).choice(candidates)
        lo, hi = path[start]['start'], path[start + 31]['end']
        raw = books[j]['digits']
        targets['aligned'].append(raw[lo:hi])
        targets['clipped'].append(raw[lo + 1:hi - 1])
        witnesses.append({'book_index': j, 'code_start': start, 'code_count': 32,
                          'aligned_start': lo, 'aligned_end': hi,
                          'clipped_start': lo + 1, 'clipped_end': hi - 1})
    return {'seed': seed, 'source': source, 'offset': offset, 'books': books,
            'targets': {k: ''.join(v) for k, v in targets.items()}, 'truth_copy_spans': witnesses}


def freeze():
    if PROTOCOL.exists():
        raise RuntimeError('protocol already frozen')
    paths = ['scripts/copy_wire_codec.py', 'scripts/copy_wire_experiment.py',
             'scripts/zero_rule_constraints.py', 'scripts/homophonic_benchmark.py',
             'scripts/raw_digit_decoder.py', 'scripts/raw_parser_benchmark.py',
             'data/normalized_books.json', 'data/external_book_round10.json',
             'data/word_validator_reference/wizard_oz.txt', 'data/word_validator_reference/peter_pan.txt']
    p = {'version': 'COPY_WIRE_V1', 'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'prior_exposure': 'All game targets and English authors previously exposed. New protocol precedes the new codec outcomes, not historical exposure.',
         'maximum_reference_raw_digits': 96, 'fixtures_per_cell': 30, 'source_books_per_fixture': 70,
         'source_codes_per_book': 64, 'target_pieces': 4, 'target_codes_per_uncut_piece': 32,
         'contents': ['encrypted_english', 'shuffled_codes'], 'cuts': ['aligned', 'clipped'],
         'seed': SEED, 'gate': 'In each content cell, at least27/30aligned targets strictly prefer codes and at least27/30clipped targets strictly prefer raw. Ties fail. Failure prevents mechanism identification on game data.',
         'coding': {'common': '1bit family selector + Elias gamma(raw_target_length+1); literal0 +4bit digit; reference1 +ceil(log2(number_of_source_books))bit book index.',
                    'raw_reference': 'ceil(log2(source_raw_length))bit raw start + gamma(raw_length).',
                    'code_reference': 'ceil(log2(compatible_alignment_count))bit alignment +ceil(log2(source_code_count))bit code start +gamma(code_count).',
                    'objective': 'Exact minimum total bit length, no English scoring; all raw reference lengths1..96; cheapest witness per raw string, ties by bitstring.',
                    'side_information': 'Ordered source raw books and complete compatible boundary annotations are shared by both models. These are CONDITIONAL target bits; source/annotation description cost is not included.',
                    'decoder': 'Actual prefix bitstreams roundtrip; reference length inferred from addressed source; no cross-book source snippets, no target dictionary learning.'},
         'primary_target': 'Previously exposed137digit Kharos; fitted dictionaries contain only70Hellgate books.',
         'target_controls': {'replicates_each': 99, 'modes': ['digit_shuffle', 'blocks8_shuffle'],
                             'score': 'Delta=codes_bits-raw_bits. Exploratory upper tail rank per mode; no hypothesis-test or semantic claim.'},
         'secondary_game_evaluation': 'Two raw16-overlap components68+2, each predicted only from the other. Previously exposed and tiny; shorter/transformed leakage persists. Sum conditional target bits, not independence of windows.',
         'translation_gate': 'No code-to-English output in this experiment. A copying mechanism does not identify a cipher, true tokenization, or semantic content.',
         'hashes': {path: digest(ROOT / path) for path in paths}}
    PROTOCOL.write_text(json.dumps(p, indent=2) + '\n')


def verify(p):
    for path, expected in p['hashes'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('frozen input changed: ' + path)


def pair(raw, context, indices, full=False):
    results = {family: encode(raw, context, family, indices[family]) for family in ('raw', 'codes')}
    if not full:
        results = {family: {k: v for k, v in r.items() if k not in ('bitstream', 'path')}
                   for family, r in results.items()}
    delta = results['codes']['bits'] - results['raw']['bits']
    return {'delta_code_minus_raw_bits': delta, 'preferred': 'raw' if delta > 0 else 'codes' if delta < 0 else 'tie',
            'codecs': results}


def fit(books, p):
    context = prepare(books, p['maximum_reference_raw_digits'])
    return context, {family: build_index(context, family) for family in ('raw', 'codes')}


def components(books, k=16):
    groups = [{i} for i in range(len(books))]
    windows = [{b['digits'][i:i + k] for i in range(len(b['digits']) - k + 1)} for b in books]
    while True:
        changed = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if any(windows[a] & windows[b] for a in groups[i] for b in groups[j]):
                    groups[i] |= groups[j]
                    del groups[j]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return sorted([sorted(g) for g in groups], key=lambda g: (-len(g), g))


def run():
    if RESULT.exists():
        raise RuntimeError('result already exists')
    started = time.monotonic()
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    positives = []
    for i in range(p['fixtures_per_cell']):
        for content in p['contents']:
            f = fixture(i, content)
            context, indices = fit(f['books'], p)
            trials = {cut: pair(f['targets'][cut], context, indices) for cut in p['cuts']}
            positives.append({'fixture': i, 'content': content, 'source': f['source'], 'offset': f['offset'],
                              'seed': f['seed'], 'source_books_sha256': hashlib.sha256(json.dumps(f['books'], sort_keys=True).encode()).hexdigest(),
                              'target_raw_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f['targets'].items()},
                              'truth_copy_spans': f['truth_copy_spans'], 'trials': trials})
        print('wire fixture', i, 'complete', flush=True)
    gates = []
    for content in p['contents']:
        for cut in p['cuts']:
            preferred = 'codes' if cut == 'aligned' else 'raw'
            rows = [r['trials'][cut] for r in positives if r['content'] == content]
            count = sum(r['preferred'] == preferred for r in rows)
            gates.append({'content': content, 'cut': cut, 'expected': preferred, 'correct': count,
                          'fixtures': len(rows), 'ties': sum(r['preferred'] == 'tie' for r in rows),
                          'passes': count >= 27,
                          'mean_delta_bits': sum(r['delta_code_minus_raw_bits'] for r in rows) / len(rows)})
    print('wire gates', json.dumps(gates), flush=True)
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    target = json.loads((ROOT / 'data/external_book_round10.json').read_text())
    context, indices = fit(books, p)
    observed = pair(target['digits'], context, indices, full=True)
    controls = []
    for mode in p['target_controls']['modes']:
        trials = []
        for i in range(p['target_controls']['replicates_each']):
            rng = random.Random(SEED + 100000 + i)
            units = list(target['digits']) if mode == 'digit_shuffle' else [target['digits'][j:j + 8] for j in range(0, len(target['digits']), 8)]
            rng.shuffle(units)
            trials.append(pair(''.join(units), context, indices))
        controls.append({'mode': mode, 'trials': trials,
                         'exploratory_upper_rank': (1 + sum(r['delta_code_minus_raw_bits'] >= observed['delta_code_minus_raw_bits'] for r in trials)) / (1 + len(trials))})
    print('wire external target', observed['delta_code_minus_raw_bits'], flush=True)
    folds = []
    comps = components(books)
    for group in comps:
        train = [b for i, b in enumerate(books) if i not in group]
        held = [books[i] for i in group]
        if not train:
            folds.append({'status': 'INFEASIBLE', 'held_ids': [b['id'] for b in held]})
            continue
        context, indices = fit(train, p)
        rows = [{'id': b['id'], **pair(b['digits'], context, indices)} for b in held]
        folds.append({'status': 'COMPUTED_CONDITIONAL', 'train_ids': [b['id'] for b in train],
                      'held_ids': [b['id'] for b in held], 'targets': rows,
                      'total_bits': {family: sum(r['codecs'][family]['bits'] for r in rows) for family in ('raw', 'codes')}})
    verify(p)
    out = {'complete': True, 'protocol_sha256': digest(PROTOCOL), 'positive_controls': positives,
           'gates': gates, 'all_mechanism_gates_pass': all(g['passes'] for g in gates),
           'target_id': target['id'], 'target': observed, 'target_controls': controls,
           'raw16_component_folds': folds, 'source_library_paid': False,
           'runtime_seconds': time.monotonic() - started, 'verified_translations': 0,
           'english_outputs': 0, 'new_key_fits': 0,
           'limits': ['Conditional coding only: source library, annotations and code inventory are not charged as a stand-alone compressed archive.',
                      'Both code models reproduce original digits. Their bits do not recover semantic codes or English.',
                      'Synthetic encrypted-English pieces may lose letters at clipping; the clipped concatenation is not assumed to be a coherent English message.',
                      'Shuffled source codes destroy letter order but preserve each source code histogram; blocks and repetitions can remain.',
                      'All game targets and author references were already exposed. No blind semantic test or identified authoring history.',
                      'A failed gate precludes identifying a game mechanism from these costs. Even a passing gate identifies neither meaning nor absence of meaning.']}
    RESULT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'gates': gates, 'target': {k: v['bits'] for k, v in observed['codecs'].items()},
                      'folds': [{k: v for k, v in f.items() if k != 'targets'} for f in folds],
                      'seconds': out['runtime_seconds']}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
        print('Wire codec protocol frozen.')
    if args.run:
        run()
