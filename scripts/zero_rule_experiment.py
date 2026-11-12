#!/usr/bin/env python3
"""Freeze and execute exact zero-renderer compatibility, with mechanical controls."""
import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import random
import time

from zero_rule_constraints import FAMILIES, alignments, feature, predict, serialize, solve

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'data/zero_rule_constraints_protocol.json'
RESULT = ROOT / 'results/zero_rule_constraints.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze():
    if PROTOCOL.exists():
        raise RuntimeError('already frozen')
    p = {'version': 'ZERO_RENDERER_CONSTRAINTS_V1',
         'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'scope': 'Does a shared deterministic Boolean formatter exist for these supplied code streams? Not raw segmentation, key recovery or translation.',
         'families': FAMILIES, 'alignment_cap': 4096, 'search_node_cap': 100000,
         'selection': 'No English score or model selection. Exact satisfiability per fixed family on68discovery books.',
         'split': 'Existing exposed68/2 split; fit table only on discovery. Reserved prediction is conditional on imported codes and is not blind validation.',
         'unseen_feature_default': 'preserve zero',
         'controls': {'seed': 84690000, 'within_book_code_shuffles': 39,
                      'copy_consistent_window3_controls': 9, 'planted_per_family': 1},
         'shuffle_policy': 'Permute annotated omission flags only among occurrences of the same code in the same book. Preserve imported code stream, per-book raw length and per-book/code omission counts. Raw copying can change.',
         'copy_control_policy': 'One seeded random action per copied7-code window, using annotated per-code omission rates. Preserve code streams and force matching local contexts to use the same action. Raw lengths/counts only approximate the observation.',
         'positive_policy': 'Construct one exact table per family, serialize the supplied code streams with it, and require the existence solver to find a compatible table.',
         'no_statistical_claim': 'SAT/UNSAT is a logical compatibility test, no pvalues; repeated copies do not create independent evidence.',
         'matrix_scope': 'code_phase16 covers any shared function of current code and fixed position in a16-code cycle reset at book start, hence any fixed orientation/phase relabeling of a4x4cell. Does not cover per-book unknown phases, other state, mixing or the full cipher.',
         'input_hashes': {f: digest(ROOT / f) for f in ['data/normalized_books.json', 'data/normalized_splits.json', 'data/normalized_code_map.json']},
         'implementation_hashes': {f: digest(ROOT / f) for f in ['scripts/zero_rule_constraints.py', 'scripts/zero_rule_experiment.py']},
         'upstream_relation': 'Extends prior zero-context probes with all fixed-stream alignments and exact arbitrary-table constraints; does not accept their semantic claims.',
         'limits': ['Imported token sequence is fixed throughout and learned upstream on the public corpus. Alternative tokenizations are not excluded.',
                    'Nonlocal, randomized, framed, keyed, epoch-specific or book-specific formatters remain outside these families.',
                    'SAT lookup tables can memorize data; a fit is not a compact generative discovery, raw decoder or translation.',
                    'Control shuffles use one recorded ambiguous alignment; real contradictions use all compatible alignments.',
                    'Alignment/search caps yield unresolved, never rejection.']}
    PROTOCOL.write_text(json.dumps(p, indent=2) + '\n')


def verify(p):
    for relative, expected in {**p['input_hashes'], **p['implementation_hashes']}.items():
        if digest(ROOT / relative) != expected:
            raise ValueError('frozen source/input changed: ' + relative)


def label_rates(books):
    counts = collections.Counter()
    omitted = collections.Counter()
    for b in books:
        mask = set(b['omitted_zero_code_indices'])
        for i, code in enumerate(b['codes']):
            if code.startswith('0'):
                counts[code] += 1
                omitted[code] += i in mask
    return {c: omitted[c] / n for c, n in counts.items()}


def shuffled_books(books, seed):
    rng = random.Random(seed)
    output = []
    for b in books:
        groups = collections.defaultdict(list)
        old_mask = set(b['omitted_zero_code_indices'])
        for i, code in enumerate(b['codes']):
            if code.startswith('0'):
                groups[code].append(i)
        mask = set()
        for code, indices in groups.items():
            flags = [i in old_mask for i in indices]
            rng.shuffle(flags)
            mask.update(i for i, flag in zip(indices, flags) if flag)
            assert sum(i in mask for i in indices) == sum(i in old_mask for i in indices)
        raw = serialize(b['codes'], mask)
        assert len(raw) == len(b['digits'])
        output.append({'id': b['id'], 'codes': b['codes'], 'digits': raw,
                       'omitted_zero_code_indices': sorted(mask)})
    return output


def planted_books(books, spec, seed, rates):
    table = {}
    output = []
    for b in books:
        omitted = set()
        for i, code in enumerate(b['codes']):
            if not code.startswith('0'):
                continue
            key = feature(b['codes'], i, spec)
            # Order-independent, same action in every copied context.
            if key not in table:
                material = json.dumps([seed, key], separators=(',', ':')).encode()
                value = int.from_bytes(hashlib.sha256(material).digest()[:8], 'big') / 2**64
                table[key] = value < rates[code]
            if table[key]:
                omitted.add(i)
        output.append({'id': b['id'], 'codes': b['codes'], 'digits': serialize(b['codes'], omitted),
                       'omitted_zero_code_indices': sorted(omitted)})
    return output


def analyze(books, p, ids):
    aligned = [alignments(b, p['alignment_cap']) for b in books]
    if any(a['count'] == 0 for a in aligned):
        raise ValueError('supplied stream has no valid alignment')
    selected = [(b, a) for b, a in zip(books, aligned) if b['id'] in ids]
    train = [b for b, _ in selected]
    aa = [a for _, a in selected]
    return aligned, [solve(train, aa, spec, p['search_node_cap']) for spec in FAMILIES]


def compact_fits(fits):
    return {spec['name']: {k: fit[k] for k in ['status', 'nodes', 'observed_parameters'] if k in fit}
            for spec, fit in zip(FAMILIES, fits)}


def run():
    if RESULT.exists():
        raise RuntimeError('result exists; preserve completed execution')
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    started = time.monotonic()
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    split = json.loads((ROOT / 'data/normalized_splits.json').read_text())
    discovery = set(split['discovery_book_ids'])
    reserved = [b for b in books if b['id'] not in discovery]
    aligned, fits = analyze(books, p, discovery)
    real = []
    for spec, fit in zip(FAMILIES, fits):
        row = {'family': spec, 'discovery_fit': fit, 'reserved_predictions': None}
        if fit['status'] == 'SAT':
            row['reserved_predictions'] = [predict(b, fit['table'], spec) for b in reserved]
        real.append(row)
        print(spec['name'], fit['status'], flush=True)
    rates = label_rates([b for b in books if b['id'] in discovery])
    positive = []
    seed = p['controls']['seed']
    for index, spec in enumerate(FAMILIES):
        dataset = planted_books(books, spec, seed + index, rates)
        aa = [alignments(b, p['alignment_cap']) for b in dataset]
        chosen = [(b, a) for b, a in zip(dataset, aa) if b['id'] in discovery]
        fit = solve([b for b, _ in chosen], [a for _, a in chosen], spec, p['search_node_cap'])
        positive.append({'family': spec['name'], 'expected': 'SAT', 'actual': fit['status'],
                         'nodes': fit['nodes']})
    nulls = []
    for i in range(p['controls']['within_book_code_shuffles']):
        dataset = shuffled_books(books, seed + 10000 + i)
        _, controls = analyze(dataset, p, discovery)
        changed = sum(b['digits'] != original['digits'] for b, original in zip(dataset, books))
        nulls.append({'replicate': i, 'seed': seed + 10000 + i,
                      'changed_books': changed,
                      'dataset_sha256': hashlib.sha256(json.dumps(dataset, sort_keys=True).encode()).hexdigest(),
                      'fits': compact_fits(controls)})
    copy_controls = []
    window3 = next(s for s in FAMILIES if s['name'] == 'window3')
    for i in range(p['controls']['copy_consistent_window3_controls']):
        dataset = planted_books(books, window3, seed + 20000 + i, rates)
        _, controls = analyze(dataset, p, discovery)
        copy_controls.append({'replicate': i, 'seed': seed + 20000 + i,
                              'dataset_sha256': hashlib.sha256(json.dumps(dataset, sort_keys=True).encode()).hexdigest(),
                              'fits': compact_fits(controls)})
    verify(p)
    alignment_summary = [{'id': a['id'], 'alignments': a['count'], 'enumeration_complete': a['enumeration_complete'],
                          'zero_events': len(a['events']),
                          'forced_events': sum(len(e['actions']) == 1 for e in a['events']),
                          'ambiguous_events': sum(len(e['actions']) > 1 for e in a['events'])} for a in aligned]
    out = {'complete': True, 'protocol': p, 'protocol_sha256': digest(PROTOCOL),
           'alignment_summary': alignment_summary, 'families': real,
           'positive_controls': positive, 'shuffled_controls': nulls, 'copy_controls': copy_controls,
           'positive_controls_pass': all(x['actual'] == 'SAT' for x in positive),
           'copied_positive_controls_pass': all(x['fits']['window3']['status'] == 'SAT' for x in copy_controls),
           'new_english_decodings': 0, 'verified_translations': 0,
           'runtime_seconds': time.monotonic() - started, 'limits': p['limits']}
    RESULT.write_text(json.dumps(out, indent=2) + '\n')
    print('Positivecontrols', out['positive_controls_pass'], 'copycontrols', out['copied_positive_controls_pass'], flush=True)
    print('Runtime', out['runtime_seconds'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
        print('Zero renderer constraint protocol frozen.')
    if args.run:
        run()
