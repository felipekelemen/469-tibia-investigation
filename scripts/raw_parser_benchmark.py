#!/usr/bin/env python3
"""Frozen external qualification of raw parsing with a supplied TRUE key.

Tests parsing, not unknown-key cryptanalysis. No Tibia file is accessed.
"""
import argparse
import datetime
import hashlib
import json
import math
import pathlib
import random
import time

import numpy as np

from copied_homophonic_v3 import build_model
from homophonic_benchmark import FREQUENCIES, letters
from raw_digit_decoder import (RULES, CharacterLanguage, UniformLanguage, decode,
                               measures, serialize)

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'data/raw_parser_v1_protocol.json'
RESULT = ROOT / 'results/raw_parser_v1.json'
LENGTHS = (64, 128)
TRUE_RULES = ('never', 'always', 'iid_0.3', 'previous_mod3')
SEED = 70469000


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key_and_emissions(seed):
    rng = random.Random(seed)
    allocation = [1] * 26
    for c in rng.choices(range(26), weights=FREQUENCIES, k=73):
        allocation[c] += 1
    ids = [i for i in range(100) if i != 39]
    rng.shuffle(ids)
    key = [-1] * 100
    probabilities = [0.0] * 100
    cursor = 0
    for letter, count in enumerate(allocation):
        weights = [(i + 1) ** -1.25 for i in range(count)]
        for code, weight in zip(ids[cursor:cursor + count], weights):
            key[code] = letter
            probabilities[code] = weight / sum(weights)
        cursor += count
    return key, probabilities


def encode_letters(text, key, probabilities, rng):
    pools = [[i for i, c in enumerate(key) if c == letter] for letter in range(26)]
    return [rng.choices(pools[ord(c) - 65], weights=[probabilities[i] for i in pools[ord(c) - 65]], k=1)[0] for c in text]


def fixture(index, length):
    if not 0 <= index < 30 or length not in LENGTHS:
        raise ValueError('fixture')
    source = 'treasure_island' if index < 15 else 'call_wild'
    offset = 1000 + (index % 15) * 1024 + LENGTHS.index(length) * 32768
    text = letters(ROOT / f'data/raw_parser_reference/{source}.txt')[offset:offset + 512 + length]
    if len(text) != 512 + length:
        raise ValueError('qualification source too short')
    seed = SEED + LENGTHS.index(length) * 10000 + index
    key, probabilities = key_and_emissions(seed)
    codes = encode_letters(text, key, probabilities, random.Random(seed + 100000))
    return {'source': source, 'offset': offset, 'seed': seed, 'key': key, 'probabilities': probabilities,
            'calibration_text': text[:512], 'evaluation_text': text[512:],
            'calibration_codes': codes[:512], 'evaluation_codes': codes[512:],
            'text_sha256': hashlib.sha256(text.encode()).hexdigest()}


def freeze():
    if PROTOCOL.exists():
        raise RuntimeError('already frozen; use a new version for changes')
    _, model = build_model()
    source_rows = json.loads((ROOT / 'data/raw_parser_reference/SOURCES.json').read_text())
    paths = ['scripts/raw_digit_decoder.py', 'scripts/raw_parser_benchmark.py',
             'scripts/copied_homophonic_v3.py', 'scripts/homophonic_benchmark.py']
    p = {'version': 'RAW_PARSER_V1_KNOWN_KEY', 'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'selection': 'Algorithm and candidate family fixed theoretically; no qualification-based tuning.',
         'lengths': LENGTHS, 'fixtures_per_cell': 30, 'calibration_letters': 512,
         'true_rules': TRUE_RULES, 'candidate_rules': RULES, 'seed': SEED,
         'supplied_information': ['true homophonic code-to-letter key', 'true P(code|letter) for all letters',
                                 'true omission rule in oracle mode only'],
         'hidden_evaluation_information': ['plaintext', 'code count', 'code boundaries', 'omitted-zero positions'],
         'language': model, 'message_length_prior': 'P(N=n)=(1/128)*(127/128)^n, n>=0; true evaluation length not supplied',
         'rule_selection': 'maximize exact forward marginal likelihood on a separate 512-letter encoded calibration message; selected once per rule/fixture; unchanged on evaluation/controls',
         'gate': {'minimum_boundary_f1': .95, 'minimum_code_span_f1': .95,
                  'minimum_character_edit_accuracy': .95, 'minimum_passes_per_cell': 27},
         'controls': ['shuffle_codes', 'blocks8_codes'],
         'control_policy': 'Preserve exact code multiset. Preserve per-token omission flags when independent of context, hence raw length. For previous_mod3 reserialize the shuffled codes under the true context rule; length may change.',
         'baseline': 'uniform-letter language, true key/emissions and true omission rule',
         'application_gate': 'A passing conditional parser is not an unknown-key solver. No game key search or translation claim authorized by this gate alone.',
         'source_hashes': {r['name']: r['sha256'] for r in source_rows},
         'implementation_hashes': {f: digest(ROOT / f) for f in paths},
         'fixture_manifest': [{'fixture': i, 'length': n, 'source': fixture(i, n)['source'],
                               'offset': fixture(i, n)['offset'], 'sha256': fixture(i, n)['text_sha256']}
                              for n in LENGTHS for i in range(30)],
         'limits': ['Known true key and code emission distribution are strong oracle advantages, unavailable for real469.',
                    'Four rule scenarios and order controls share each of60source excerpts/keys; do not pool as independent plaintexts.',
                    'Only two fresh authors; short finite samples and a small explicitly defined rule family.',
                    'Forward probability and MAP posterior are conditional on the approximate character model, not semantic truth.',
                    'Controls have known valid encryption/zero rules but disrupted order; not every permuted passage is guaranteed meaningless.',
                    'Synthetic99-code keys use all00..99 except39 to match inventory size; this is not evidence that the imported469stream is correct.']}
    PROTOCOL.write_text(json.dumps(p, indent=2) + '\n')
    return p


def verify(p):
    for f, expected in p['implementation_hashes'].items():
        if digest(ROOT / f) != expected:
            raise ValueError('frozen implementation changed: ' + f)
    for name, expected in p['source_hashes'].items():
        if digest(ROOT / f'data/raw_parser_reference/{name}.txt') != expected:
            raise ValueError('qualification source changed')
    if build_model()[1]['model_sha256'] != p['language']['model_sha256']:
        raise ValueError('language model changed')


def order_control(codes, original_path, rule, mode, seed):
    rng = random.Random(seed)
    if mode == 'shuffle_codes':
        indices = list(range(len(codes)))
        rng.shuffle(indices)
    elif mode == 'blocks8_codes':
        chunks = [list(range(i, min(i + 8, len(codes)))) for i in range(0, len(codes), 8)]
        rng.shuffle(chunks)
        indices = [i for chunk in chunks for i in chunk]
    else:
        raise ValueError(mode)
    reordered = [codes[i] for i in indices]
    if rule == 'previous_mod3':
        raw, path = serialize(reordered, rule, rng)
    else:
        pieces = []
        path = []
        position = 0
        for i in indices:
            omitted = original_path[i]['omitted']
            piece = f'{codes[i]:02d}'[1:] if omitted else f'{codes[i]:02d}'
            pieces.append(piece)
            path.append({'start': position, 'end': position + len(piece), 'code': codes[i], 'omitted': omitted})
            position += len(piece)
        raw = ''.join(pieces)
    return raw, path, reordered


def compact(fit, truth_path, truth_text):
    return {**measures(fit, truth_path, truth_text),
            'literal': fit['literal'], 'log_evidence': fit['log_evidence'],
            'predicted_codes': [r['code'] for r in fit['path']],
            'predicted_end_positions': [r['end'] for r in fit['path']]}


def passes(row, p):
    return all(row[k] >= p['gate']['minimum_' + k] for k in ['boundary_f1', 'code_span_f1', 'character_edit_accuracy'])


def run():
    if RESULT.exists():
        raise RuntimeError('result exists; do not silently reopen qualification')
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    language = CharacterLanguage(build_model()[0])
    uniform = UniformLanguage()
    started = time.monotonic()
    trials = []
    for length in LENGTHS:
        for i in range(30):
            f = fixture(i, length)
            key, probabilities = f['key'], f['probabilities']
            for rindex, rule in enumerate(TRUE_RULES):
                seed = f['seed'] + 1000000 + rindex * 1000
                calibration, _ = serialize(f['calibration_codes'], rule, random.Random(seed))
                evidence = {}
                for candidate in RULES:
                    fit = decode(calibration, key, probabilities, language, candidate)
                    evidence[candidate] = fit['log_evidence']
                selected = max(RULES, key=lambda c: evidence[c] if evidence[c] is not None else -math.inf)
                raw, path = serialize(f['evaluation_codes'], rule, random.Random(seed + 500000))
                truth = f['evaluation_text']
                oracle = decode(raw, key, probabilities, language, rule)
                estimated = oracle if selected == rule else decode(raw, key, probabilities, language, selected)
                baseline = decode(raw, key, probabilities, uniform, rule)
                row = {'fixture': i, 'length': length, 'true_rule': rule, 'selected_rule': selected,
                       'source': f['source'], 'source_offset': f['offset'], 'seed': seed,
                       'text_sha256': f['text_sha256'], 'calibration_raw_sha256': hashlib.sha256(calibration.encode()).hexdigest(),
                       'calibration_log_evidence': evidence, 'evaluation_raw': raw,
                       'truth_literal': truth, 'truth_codes': f['evaluation_codes'],
                       'truth_omitted_indices': [j for j, x in enumerate(path) if x['omitted']],
                       'oracle': compact(oracle, path, truth), 'selected': compact(estimated, path, truth),
                       'uniform_oracle': compact(baseline, path, truth), 'controls': []}
                for cindex, mode in enumerate(p['controls']):
                    craw, cpath, ccodes = order_control(f['evaluation_codes'], path, rule, mode, seed + 800000 + cindex)
                    ctruth = ''.join(chr(key[c] + 65) for c in ccodes)
                    cfit = decode(craw, key, probabilities, language, rule)
                    cselected = cfit if rule == selected else decode(craw, key, probabilities, language, selected)
                    row['controls'].append({'mode': mode, 'raw': craw, 'truth_literal': ctruth,
                                            'truth_codes': ccodes, 'raw_length_preserved': len(craw) == len(raw),
                                            'oracle': compact(cfit, cpath, ctruth),
                                            'selected': compact(cselected, cpath, ctruth)})
                trials.append(row)
            print('raw parser', length, i, 'complete', flush=True)
    summaries = []
    for length in LENGTHS:
        for rule in TRUE_RULES:
            part = [r for r in trials if r['length'] == length and r['true_rule'] == rule]
            modes = {}
            for mode in ['oracle', 'selected', 'uniform_oracle']:
                count = sum(passes(r[mode], p) for r in part)
                modes[mode] = {'passed': count, 'passes_gate': count >= p['gate']['minimum_passes_per_cell'],
                               'exact_paths': sum(r[mode]['exact_path'] for r in part),
                               **{'mean_' + k: float(np.mean([r[mode][k] for r in part]))
                                  for k in ['boundary_f1', 'code_span_f1', 'character_edit_accuracy']}}
            summaries.append({'length': length, 'rule': rule, 'fixtures': len(part),
                              'correct_rule_selected': sum(r['selected_rule'] == rule for r in part), 'modes': modes})
    verify(p)
    out = {'complete': True, 'protocol_sha256': digest(PROTOCOL), 'protocol': p,
           'trials': trials, 'summaries': summaries,
           'oracle_gate_passes': all(s['modes']['oracle']['passes_gate'] for s in summaries),
           'selected_rule_gate_passes': all(s['modes']['selected']['passes_gate'] for s in summaries),
           'game_inputs_read': False, 'unknown_key_searches': 0, 'verified_translations': 0,
           'runtime_seconds': time.monotonic() - started, 'limits': p['limits']}
    RESULT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'summaries': summaries, 'runtime_seconds': out['runtime_seconds']}, indent=2), flush=True)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--freeze', action='store_true')
    ap.add_argument('--run', action='store_true')
    args = ap.parse_args()
    if args.freeze:
        freeze()
        print('Raw parser V1 protocol frozen; qualification not yet run.')
    if args.run:
        run()
