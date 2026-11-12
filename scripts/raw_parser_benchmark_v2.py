#!/usr/bin/env python3
"""New-author qualification of the development-selected long-context parser."""
import argparse
import datetime
import hashlib
import json
import math
import pathlib
import random
import time

from copied_homophonic_v3 import build_model
from homophonic_benchmark import letters
from raw_digit_decoder import RULES, CharacterLanguage, decode as decode_v1, serialize
from raw_parser_benchmark import (LENGTHS, TRUE_RULES, compact, digest, encode_letters,
                                  key_and_emissions, order_control, passes)
from raw_parser_long_context import LongContextLanguage, decode

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'data/raw_parser_v2_protocol.json'
RESULT = ROOT / 'results/raw_parser_v2.json'
SEED = 80469000


def fixture(index, length):
    if not 0 <= index < 30 or length not in LENGTHS:
        raise ValueError('fixture')
    source = 'anne_green_gables' if index < 15 else 'secret_agent'
    # Start farther into the book to avoid the front matter found in V1.
    offset = 10000 + (index % 15) * 1024 + LENGTHS.index(length) * 32768
    text = letters(ROOT / f'data/raw_parser_reference_v2/{source}.txt')[offset:offset + 512 + length]
    if len(text) != 512 + length:
        raise ValueError('qualification source too short')
    seed = SEED + LENGTHS.index(length) * 10000 + index
    key, probabilities = key_and_emissions(seed)
    codes = encode_letters(text, key, probabilities, random.Random(seed + 100000))
    return {'source': source, 'offset': offset, 'seed': seed, 'key': key, 'probabilities': probabilities,
            'calibration_codes': codes[:512], 'evaluation_codes': codes[512:],
            'truth': text[512:], 'text_sha256': hashlib.sha256(text.encode()).hexdigest()}


def freeze():
    if PROTOCOL.exists():
        raise RuntimeError('already frozen')
    development = json.loads((ROOT / 'results/raw_parser_v1_diagnosis.json').read_text())
    choice = development['selected_for_future_qualification']
    sources = json.loads((ROOT / 'data/raw_parser_reference_v2/SOURCES.json').read_text())
    files = ['scripts/raw_parser_benchmark_v2.py', 'scripts/raw_parser_long_context.py',
             'scripts/raw_parser_benchmark.py', 'scripts/raw_digit_decoder.py',
             'scripts/copied_homophonic_v3.py', 'scripts/homophonic_benchmark.py']
    p = {'version': 'RAW_PARSER_V2_KNOWN_KEY', 'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'selected_model': {'order': choice['order'], 'backoff': choice['backoff']},
         'development_result_sha256': digest(ROOT / 'results/raw_parser_v1_diagnosis.json'),
         'training_sources': LongContextLanguage(choice['order'], choice['backoff']).sources,
         'lengths': LENGTHS, 'fixtures_per_cell': 30, 'calibration_letters': 512,
         'true_rules': TRUE_RULES, 'candidate_rules': RULES, 'seed': SEED,
         'gate': {'minimum_boundary_f1': .95, 'minimum_code_span_f1': .95,
                  'minimum_character_edit_accuracy': .95, 'minimum_passes_per_cell': 27},
         'supplied_information': ['true homophonic key', 'true P(code|letter)', 'true omission rule in oracle mode'],
         'hidden_evaluation_information': ['plaintext', 'code count', 'boundaries', 'zero omission positions'],
         'length_prior': 'P(N=n)=(1/128)*(127/128)^n, n>=0; no supplied true length',
         'rule_selection': 'Eight fixed models compared by exact forward evidence only on the512-letter calibration message; no evaluation fitting',
         'controls': ['shuffle_codes', 'blocks8_codes'],
         'paired_baseline': 'V1 character model on the identical new ciphertext, key/emissions and true rule; scorer changes order and interpolation jointly',
         'implementation_hashes': {f: digest(ROOT / f) for f in files},
         'source_hashes': {r['name']: r['sha256'] for r in sources},
         'fixture_manifest': [{'fixture': i, 'length': n, 'source': fixture(i, n)['source'],
                               'offset': fixture(i, n)['offset'], 'sha256': fixture(i, n)['text_sha256']}
                              for n in LENGTHS for i in range(30)],
         'limits': ['Known-key conditional parsing only; this gate cannot qualify unknown-key decryption or real469translation.',
                    'Four zero rules and controls share60newplaintext excerpts/keys. Only two new authors.',
                    'Model selected on all opened V1cases; new source offsets begin10000letters into books but can still cut words/sentences.',
                    'Code multiset preserved in controls; context-free omission flags also preserved, contextual rules reserialized.',
                    'Forward probabilities and posteriors are conditional on the model, not semantic correctness.',
                    'No Tibia text, lore term or purported translation enters this qualification.']}
    PROTOCOL.write_text(json.dumps(p, indent=2) + '\n')


def verify(p):
    for f, expected in p['implementation_hashes'].items():
        if digest(ROOT / f) != expected:
            raise ValueError('frozen implementation changed: ' + f)
    for source in p['training_sources']:
        if digest(ROOT / source['path']) != source['source_sha256']:
            raise ValueError('training source changed')
    for name, expected in p['source_hashes'].items():
        if digest(ROOT / f'data/raw_parser_reference_v2/{name}.txt') != expected:
            raise ValueError('qualification source changed')
    if digest(ROOT / 'results/raw_parser_v1_diagnosis.json') != p['development_result_sha256']:
        raise ValueError('development changed')


def run():
    if RESULT.exists():
        raise RuntimeError('result exists; do not reopen qualification')
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    model = LongContextLanguage(**p['selected_model'])
    baseline_model = CharacterLanguage(build_model()[0])
    trials = []
    start = time.monotonic()
    for length in LENGTHS:
        for i in range(30):
            f = fixture(i, length)
            key, probabilities = f['key'], f['probabilities']
            for rindex, rule in enumerate(TRUE_RULES):
                seed = f['seed'] + 1000000 + rindex * 1000
                calibration, _ = serialize(f['calibration_codes'], rule, random.Random(seed))
                evidence = {c: decode(calibration, key, probabilities, model, c)['log_evidence'] for c in RULES}
                selected = max(RULES, key=lambda c: evidence[c] if evidence[c] is not None else -math.inf)
                raw, path = serialize(f['evaluation_codes'], rule, random.Random(seed + 500000))
                oracle = decode(raw, key, probabilities, model, rule)
                estimated = oracle if selected == rule else decode(raw, key, probabilities, model, selected)
                baseline = decode_v1(raw, key, probabilities, baseline_model, rule)
                truth = f['truth']
                row = {'length': length, 'fixture': i, 'true_rule': rule, 'selected_rule': selected,
                       'source': f['source'], 'source_offset': f['offset'], 'seed': seed,
                       'text_sha256': f['text_sha256'], 'calibration_raw_sha256': hashlib.sha256(calibration.encode()).hexdigest(),
                       'calibration_log_evidence': evidence, 'evaluation_raw': raw,
                       'truth_literal': truth, 'truth_codes': f['evaluation_codes'],
                       'truth_omitted_indices': [j for j, r in enumerate(path) if r['omitted']],
                       'oracle': compact(oracle, path, truth), 'selected': compact(estimated, path, truth),
                       'V1_paired_oracle': compact(baseline, path, truth), 'controls': []}
                for cindex, mode in enumerate(p['controls']):
                    craw, cpath, ccodes = order_control(f['evaluation_codes'], path, rule, mode, seed + 800000 + cindex)
                    ctruth = ''.join(chr(key[c] + 65) for c in ccodes)
                    fit = decode(craw, key, probabilities, model, rule)
                    estimated = fit if selected == rule else decode(craw, key, probabilities, model, selected)
                    row['controls'].append({'mode': mode, 'raw': craw, 'truth_literal': ctruth,
                                            'raw_length_preserved': len(raw) == len(craw),
                                            'oracle': compact(fit, cpath, ctruth),
                                            'selected': compact(estimated, cpath, ctruth)})
                trials.append(row)
            print('V2raw parser', length, i, 'complete', flush=True)
    summaries = []
    for length in LENGTHS:
        for rule in TRUE_RULES:
            part = [r for r in trials if r['length'] == length and r['true_rule'] == rule]
            modes = {}
            for mode in ['oracle', 'selected', 'V1_paired_oracle']:
                count = sum(passes(r[mode], p) for r in part)
                modes[mode] = {'passed': count, 'passes_gate': count >= 27,
                               'exact_paths': sum(r[mode]['exact_path'] for r in part),
                               **{'mean_' + k: sum(r[mode][k] for r in part) / len(part)
                                  for k in ['boundary_f1', 'code_span_f1', 'character_edit_accuracy']}}
            summaries.append({'length': length, 'rule': rule, 'fixtures': len(part),
                              'correct_rule_selected': sum(r['selected_rule'] == rule for r in part), 'modes': modes})
    verify(p)
    out = {'complete': True, 'protocol': p, 'protocol_sha256': digest(PROTOCOL), 'trials': trials, 'summaries': summaries,
           'oracle_gate_passes': all(s['modes']['oracle']['passes_gate'] for s in summaries),
           'selected_rule_gate_passes': all(s['modes']['selected']['passes_gate'] for s in summaries),
           'game_inputs_read': False, 'unknown_key_searches': 0, 'verified_translations': 0,
           'runtime_seconds': time.monotonic() - start, 'limits': p['limits']}
    RESULT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'summaries': summaries, 'runtime_seconds': out['runtime_seconds']}, indent=2), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--freeze', action='store_true')
    ap.add_argument('--run', action='store_true')
    args = ap.parse_args()
    if args.freeze:
        freeze()
        print('V2 protocol frozen; new qualification not yet run.')
    if args.run:
        run()
