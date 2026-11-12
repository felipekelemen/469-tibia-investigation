#!/usr/bin/env python3
"""Test digit-anagram vs source-code-multiset conservation, without English."""
import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import random
import time

from conserved_code_parser import solve_source
from omission_set_reference import enumerate_parses
from zero_rule_constraints import alignments

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'data/conserved_code_protocol.json'
RESULT = ROOT / 'results/conserved_code_experiment.json'
MODES = ('wire_multiset', 'code_multiset')
SEED = 124690000


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anagram_groups(books):
    groups = collections.defaultdict(list)
    for b in books:
        groups[tuple(sorted(collections.Counter(b['digits']).items()))].append(b['id'])
    return [g for g in groups.values() if len(g) > 1]


def truth_source():
    return next(b for b in json.loads((ROOT / 'data/normalized_books.json').read_text()) if b['id'] == '22')


def fixture(i, kind):
    source = truth_source()
    codes = [int(c) for c in source['codes']]
    omitted = set(alignments(source)['paths'][0])
    rng = random.Random(SEED + i)
    if kind == 'zero_action_reassignment':
        zero_indices = [i for i, c in enumerate(codes) if c < 10]
        omitted = set(rng.sample(zero_indices, len(omitted)))
    elif kind != 'wire_permutation':
        raise ValueError('positive kind')
    tokens = [(c, f'{c:02d}'[1:] if j in omitted else f'{c:02d}') for j, c in enumerate(codes)]
    rng.shuffle(tokens)
    return {'raw': ''.join(w for _, w in tokens), 'truth_codes': [c for c, _ in tokens]}


def freeze():
    if PROTOCOL.exists():
        raise RuntimeError('protocol exists')
    paths = ['scripts/conserved_code_parser.py', 'scripts/conserved_code_experiment.py',
             'scripts/omission_set_reference.py', 'scripts/zero_rule_constraints.py',
             'data/normalized_books.json', 'data/external_book_round10.json',
             'results/qualified_tibia_search_v4.json']
    p = {'version': 'CONSERVED_CODES_V1', 'frozen_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'prior_exposure': 'All digit strings, imported token streams and the exact book22/Kharos histogram equality were known before freezing. No new parse outcomes inspected.',
         'primary': 'Source book22 (137digits/70codes) -> raw Kharos137digits. No target code sequence, zero positions or English supplied.',
         'hypotheses': {'wire_multiset': 'Permute exactly the source (code,wireform) multiset from any compatible source alignment; no insertion, deletion, reversal inside codes or duplicated token.',
                        'code_multiset': 'Permute exactly the source code multiset. Each0d may retain or omit its leadingzero independently. Raw length fixes total omissions, not positions.'},
         'state_cap': 1000000, 'stream_cap': 256,
         'reference': 'Independently enumerate every omitted-token index set of size2*N-raw_length, capped at1000000patterns; compare code-multiset paths and exact streams.',
         'positive_design': '30random permutations of book22wire tokens and30permutations after reassigning its3zero omissions among8eligible tokens. These are mechanical controls, not English messages or independent source texts.',
         'feasibility_gate': 'Both modes must accept30/30wire-permutation positives; code-multiset must also accept30/30zero-action reassignment positives, all with complete path counts.',
         'code_recovery_gate': 'Per positive condition/mode at least27/30complete unique streams must equal truth; feasibility alone does not qualify a decoder.',
         'nulls': {'modes': ['digit_shuffle', 'blocks8_shuffle'], 'replicates_each': 99, 'seed': SEED + 100000,
                   'interpretation': 'Preserve target digit histogram and raw length. SAT frequency is structural only; no semantics or message-absence conclusion.'},
         'secondary': 'All10directed pairs from the5exact digit-histogram groups among the70original books. Hold target imported codes out of parsing; compare them only descriptively afterward.',
         'literal_gate': 'Only complete unique Kharos codes agreed by both modes and independent enumeration, plus passing wire-permutation recovery gates, may display the fixed priorV4mapping as an explicitly conditional literal. No refitting or repairs.',
         'hashes': {f: digest(ROOT / f) for f in paths}}
    PROTOCOL.write_text(json.dumps(p, indent=2) + '\n')


def verify(p):
    for path, expected in p['hashes'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('frozen input changed: ' + path)


def trial(raw, source, p):
    return {mode: solve_source(raw, source, mode, p['state_cap'], p['stream_cap']) for mode in MODES}


def run():
    if RESULT.exists():
        raise RuntimeError('result exists')
    start = time.monotonic()
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    source = truth_source()
    positives = []
    for i in range(30):
        for kind in ('wire_permutation', 'zero_action_reassignment'):
            f = fixture(i, kind)
            rows = trial(f['raw'], source, p)
            positives.append({'fixture': i, 'kind': kind, 'raw': f['raw'], 'truth_codes': f['truth_codes'],
                              'trials': rows,
                              'unique_truth_recoveries': {mode: rows[mode]['unique_codes'] == f['truth_codes'] for mode in MODES}})
        print('conservation fixture', i, 'complete', flush=True)
    gates = []
    for kind in ('wire_permutation', 'zero_action_reassignment'):
        for mode in MODES:
            rows = [r for r in positives if r['kind'] == kind]
            feasible = sum(r['trials'][mode]['status'] == 'SAT' and r['trials'][mode]['all_counts_complete'] for r in rows)
            unique = sum(r['unique_truth_recoveries'][mode] for r in rows)
            gates.append({'kind': kind, 'mode': mode, 'feasible_complete': feasible, 'fixtures': 30,
                          'feasibility_required': not(kind == 'zero_action_reassignment' and mode == 'wire_multiset'),
                          'feasibility_pass': feasible == 30, 'unique_exact': unique, 'recovery_pass': unique >= 27})
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    target = json.loads((ROOT / 'data/external_book_round10.json').read_text())['digits']
    observed = trial(target, source, p)
    reference = enumerate_parses(target, source)
    code_result = observed['code_multiset']
    ref_streams = {tuple(s['codes']) for s in reference['solutions']} if reference['complete'] else None
    if reference['complete'] and code_result['all_counts_complete']:
        actual_paths = sum(int(r['path_count']) for r in code_result['inventories'])
        if actual_paths != len(reference['solutions']):
            raise AssertionError('independent path counts disagree')
        if code_result['all_streams_complete'] and ref_streams != {tuple(s) for r in code_result['inventories'] for s in r['streams']}:
            raise AssertionError('independent streams disagree')
    print('conservation target', {m: r['status'] for m, r in observed.items()}, flush=True)
    nulls = []
    for mode in p['nulls']['modes']:
        rows = []
        for i in range(p['nulls']['replicates_each']):
            units = list(target) if mode == 'digit_shuffle' else [target[j:j + 8] for j in range(0, len(target), 8)]
            random.Random(p['nulls']['seed'] + i).shuffle(units)
            rows.append({'replicate': i, 'trials': trial(''.join(units), source, p)})
        nulls.append({'mode': mode, 'trials': rows})
    groups = anagram_groups(books)
    byid = {b['id']: b for b in books}
    secondary = []
    for group in groups:
        for source_id in group:
            for target_id in group:
                if source_id == target_id:
                    continue
                rows = trial(byid[target_id]['digits'], byid[source_id], p)
                secondary.append({'source': source_id, 'target': target_id, 'trials': rows,
                                  'target_imported_code_histogram_equal': collections.Counter(byid[source_id]['codes']) == collections.Counter(byid[target_id]['codes']),
                                  'unique_stream_matches_supplied_target': {m: rows[m]['unique_codes'] == [int(c) for c in byid[target_id]['codes']] for m in MODES}})
    literal = None
    unique = observed['code_multiset']['unique_codes']
    if (unique is not None and observed['wire_multiset']['unique_codes'] == unique
            and reference['complete'] and ref_streams == {tuple(unique)}
            and all(g['recovery_pass'] for g in gates if g['kind'] == 'wire_permutation')):
        mapping = json.loads((ROOT / 'results/qualified_tibia_search_v4.json').read_text())['observed']['mapping']
        literal = ''.join(chr(mapping[c] + 65) for c in unique)
    verify(p)
    out = {'complete': True, 'protocol_sha256': digest(PROTOCOL), 'source_id': source['id'],
           'source_digits': len(source['digits']), 'source_codes': len(source['codes']),
           'target_digits': len(target), 'same_raw_histogram': collections.Counter(target) == collections.Counter(source['digits']),
           'histogram': dict(sorted(collections.Counter(target).items())), 'digit_sum': sum(map(int, target)),
           'positives': positives, 'gates': gates, 'target': observed, 'independent_reference': reference,
           'nulls': nulls, 'anagram_groups': groups, 'secondary_pairs': secondary,
           'conditional_v4_literal': literal, 'new_key_fits': 0, 'verified_translations': 0,
           'runtime_seconds': time.monotonic() - start,
           'scope': 'Only conservation of supplied source units tested. Digit equality does not determine tokenization, plaintext, editing history or a shared cipher.'}
    RESULT.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'gates': gates, 'target': {m: r['status'] for m, r in observed.items()},
                      'reference_patterns': reference['patterns'], 'reference_solutions': len(reference['solutions']) if reference['complete'] else None,
                      'secondary': [{k: v for k, v in r.items() if k != 'trials'} | {'statuses': {m: t['status'] for m, t in r['trials'].items()}} for r in secondary],
                      'literal': literal, 'seconds': out['runtime_seconds']}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
        print('Conserved-code protocol frozen.')
    if args.run:
        run()
