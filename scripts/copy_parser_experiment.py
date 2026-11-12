#!/usr/bin/env python3
"""Freeze a raw-copy parser control test, then inspect an external known book.

No refitted English key, no lore bonuses, no target tokenization supplied.
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import random
import time

from homophonic_benchmark import letters
from raw_copy_parser import build_dictionary, parse, raw_novelty
from raw_digit_decoder import serialize
from raw_parser_benchmark import encode_letters, key_and_emissions

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'data/copy_parser_protocol.json'
RESULT = ROOT / 'results/copy_parser_experiment.json'
MINIMUMS = (8, 12, 16)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(i):
    # Previously opened authors: operational positive controls, not a new
    # independent English-coherence qualification.
    source = 'wizard_oz' if i < 15 else 'peter_pan'
    offset = 10000 + (i % 15) * 1024
    text = letters(ROOT / f'data/word_validator_reference/{source}.txt')[offset:offset + 512]
    seed = 104690000 + i
    key, probabilities = key_and_emissions(seed)
    codes = encode_letters(text, key, probabilities, random.Random(seed))
    motifs = []
    for j in range(8):
        piece = codes[j * 64:(j + 1) * 64]
        raw, _ = serialize(piece, 'iid_0.3', random.Random(seed + 1000 + j))
        motifs.append({'id': f'm{j}', 'codes': [f'{c:02d}' for c in piece], 'digits': raw})
    schedule = random.Random(seed + 2000).sample(range(8), 4)
    raw = ''.join(motifs[j]['digits'] for j in schedule)
    truth = [int(c) for j in schedule for c in motifs[j]['codes']]
    return {'seed': seed, 'source': source, 'offset': offset, 'motifs': motifs,
            'schedule': schedule, 'raw': raw, 'truth': truth}


def freeze():
    if PROTOCOL.exists():
        raise RuntimeError('already frozen')
    paths = ['scripts/raw_copy_parser.py', 'scripts/copy_parser_experiment.py',
             'scripts/zero_rule_constraints.py', 'scripts/raw_parser_benchmark.py',
             'scripts/raw_digit_decoder.py', 'scripts/homophonic_benchmark.py',
             'data/normalized_books.json', 'data/external_book_round10.json',
             'results/qualified_tibia_search_v4.json',
             'data/word_validator_reference/wizard_oz.txt', 'data/word_validator_reference/peter_pan.txt']
    p = {'version': 'RAW_COPY_PARSER_V1', 'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'dictionary_minimum_raw': 8, 'dictionary_maximum_raw': 96, 'minimums': MINIMUMS,
         'primary_minimum': 16, 'stream_cap': 512, 'source_alignment_cap': 4096,
         'objective': 'Lexicographic minimum uncovered raw digits, then copied pieces. No English scoring or choice among code streams by readability.',
         'positive_fixtures': 30, 'positive_design': '8source motifs of64letters each; encode with random99-code key andIIDzero omissions; target concatenates4distinct exact raw motifs in a new order.',
         'controls': ['raw_digit_shuffle', 'raw_blocks8_shuffle', 'whole_motif_order_shuffle'],
         'positive_gate_each_minimum': 'At least27/30targets have a complete unique minimum-cost code sequence exactly equal to truth.',
         'game_literal_gate': 'Only primary minimum16passing synthetic code-copy gate AND complete unique full Kharos reconstruction may display the fixedV4English-key literal. No new key fit.',
         'validation_scope': 'External book absent from70training books, but publicly exposed upstream and sharing motifs; not blind semantic validation.',
         'hashes': {f: digest(ROOT / f) for f in paths},
         'limits': ['Source code streams are supplied/imported. The dictionary parser generalizes only recombinations of observed raw/code fragments.',
                    'Source snippets never cross books; target recombination is deliberate and not evidence of original word boundaries.',
                    'Coverage or a unique minimum under this dictionary does not establish plaintext, language or true tokenization.',
                    'FixedV4key was selected on the public source corpus. Copied target material leaks those source contents.',
                    'Capped enumeration returns incomplete and forbids uniqueness/translation claims.',
                    'Previously opened English authors are parser controls, not fresh coherence qualification.']}
    PROTOCOL.write_text(json.dumps(p, indent=2) + '\n')


def verify(p):
    for path, expected in p['hashes'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('frozen source/input changed: ' + path)


def summary(result):
    return {k: v for k, v in result.items() if k not in ['streams', 'representative_path']}


def run():
    if RESULT.exists():
        raise RuntimeError('result exists')
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    started = time.monotonic()
    controls = []
    for i in range(p['positive_fixtures']):
        f = fixture(i)
        dictionary = build_dictionary(f['motifs'], p['dictionary_minimum_raw'], p['dictionary_maximum_raw'], p['source_alignment_cap'])
        rng = random.Random(f['seed'] + 3000)
        chars = list(f['raw'])
        rng.shuffle(chars)
        blocks = [f['raw'][j:j + 8] for j in range(0, len(f['raw']), 8)]
        rng.shuffle(blocks)
        alternative = f['schedule'][1:] + f['schedule'][:1]
        motif_raw = ''.join(f['motifs'][j]['digits'] for j in alternative)
        motif_truth = [int(c) for j in alternative for c in f['motifs'][j]['codes']]
        rows = []
        for minimum in p['minimums']:
            fitted = parse(f['raw'], dictionary, minimum, p['stream_cap'])
            row = {'minimum': minimum, 'positive': summary(fitted),
                   'unique_exact_codes': fitted['unique_full_codes'] == f['truth'], 'controls': {}}
            for mode, raw in [('raw_digit_shuffle', ''.join(chars)), ('raw_blocks8_shuffle', ''.join(blocks)),
                              ('whole_motif_order_shuffle', motif_raw)]:
                value = parse(raw, dictionary, minimum, p['stream_cap'])
                row['controls'][mode] = summary(value)
                if mode == 'whole_motif_order_shuffle':
                    row['controls'][mode]['unique_exact_codes'] = value['unique_full_codes'] == motif_truth
            rows.append(row)
        controls.append({'fixture': i, 'source': f['source'], 'source_offset': f['offset'],
                         'seed': f['seed'], 'raw_sha256': hashlib.sha256(f['raw'].encode()).hexdigest(), 'trials': rows})
        print('copyparser fixture', i, 'complete', flush=True)
    gates = []
    for minimum in p['minimums']:
        count = sum(row['unique_exact_codes'] for fixture_row in controls for row in fixture_row['trials'] if row['minimum'] == minimum)
        gates.append({'minimum': minimum, 'exact_unique_recoveries': count, 'fixtures': 30, 'passes_gate': count >= 27})
    # Target is accessed only after the fixed synthetic controls. No parameter
    # selection or key fit follows the outcome of this target.
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    target = json.loads((ROOT / 'data/external_book_round10.json').read_text())
    dictionary = build_dictionary(books, p['dictionary_minimum_raw'], p['dictionary_maximum_raw'], p['source_alignment_cap'])
    parsed = [{'minimum': minimum, **parse(target['digits'], dictionary, minimum, p['stream_cap'])} for minimum in p['minimums']]
    primary = next(x for x in parsed if x['minimum'] == p['primary_minimum'])
    primary_gate = next(x['passes_gate'] for x in gates if x['minimum'] == p['primary_minimum'])
    literal = None
    if primary_gate and primary['unique_full_codes'] is not None:
        key = json.loads((ROOT / 'results/qualified_tibia_search_v4.json').read_text())['observed']['mapping']
        literal = ''.join(chr(key[c] + 65) for c in primary['unique_full_codes'])
    verify(p)
    out = {'complete': True, 'protocol': p, 'protocol_sha256': digest(PROTOCOL),
           'positive_controls': controls, 'gates': gates,
           'target_id': target['id'], 'target_raw_sha256': target['digits_sha256'],
           'target_exact_source_book': any(target['digits'] == b['digits'] for b in books),
           'target_substring_source_books': [b['id'] for b in books if target['digits'] in b['digits']],
           'target_raw_novelty': raw_novelty(target['digits'], books),
           'dictionary': {'raw_keys': len(dictionary['entries']),
                          'code_variants': sum(len(v) for v in dictionary['entries'].values()),
                          'source_alignments': dictionary['source_alignments']},
           'target_parses': parsed, 'conditional_fixed_v4_literal': literal,
           'literal_is_verified_translation': False, 'new_key_fits': 0, 'verified_translations': 0,
           'runtime_seconds': time.monotonic() - started, 'limits': p['limits']}
    RESULT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'gates': gates, 'target': [{k: x[k] for k in ['minimum', 'uncovered_raw_digits', 'copied_pieces', 'retained_distinct_streams', 'stream_enumeration_complete']} for x in parsed], 'literal': literal}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
        print('Copy parser protocol frozen.')
    if args.run:
        run()
