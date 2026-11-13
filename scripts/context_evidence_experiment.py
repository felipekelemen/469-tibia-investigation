#!/usr/bin/env python3
"""Round18 context information in an explicitly supplied finite key family.

This is not a general hidden-vocabulary learner. Blocks define candidate
codewords; observations supply raw frames only; labels stay in the scorer.
"""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import time

from context_constraint_solver import (FrameParser, KeySet, ResourceLimit,
    consensus_decode, constraints_from_frames, prefix_certificate)

ROOT = Path(__file__).resolve().parents[1]
SEED = 18469486
CUTS = (4, 5, 6)
DOSES = (0, 1, 2, 4, 8, 16, 32, 64, 128)
ANCHORS = DOSES[:7]
KINDS = ('whole_parent_pairs_control', 'unpaired_unit_recombinations', 'isolated_valid_unit_frames')


def load(path):
    return json.loads((ROOT / path).read_text())


def dump(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def generate_blocks(rng, groups=32):
    blocks, used = [], set()
    for _ in range(groups):
        for _ in range(100000):
            raw = ''.join(rng.choice('0123456789') for _ in range(10))
            prefixes = [raw[:3]]+[raw[k:k+3] for k in CUTS]
            if len(set(prefixes)) == 4 and not (set(prefixes) & used):
                blocks.append(raw); used.update(prefixes); break
        else:
            raise ResourceLimit('candidate-family generation exhausted')
    assert prefix_certificate(blocks)
    return blocks


def fixed_key_words(blocks, values):
    return [word for raw, ci in zip(blocks, values) for word in (raw[:CUTS[ci]], raw[CUTS[ci]:])]


def new_frame(rng, blocks, truth):
    i, j = rng.sample(range(len(blocks)), 2)
    side_i, side_j = rng.randrange(2), rng.randrange(2)
    def word(group, side):
        raw, cut = blocks[group], CUTS[truth[group]]
        return raw[:cut] if side == 0 else raw[cut:]
    units = [word(i, side_i), word(j, side_j)]
    return {'raw': ''.join(units), 'true_units': units}


def fixture(index):
    rng = random.Random(SEED+index)
    blocks = generate_blocks(rng)
    truth = [rng.randrange(3) for _ in blocks]
    pairs = list(range(32))*35; rng.shuffle(pairs)
    training = [''.join(blocks[i] for i in pairs[j:j+16]) for j in range(0, len(pairs), 16)]
    assert len(training) == 70 and sum(map(len, training)) == 11200
    pool, seen = [], set(blocks)
    while len(pool) < 160:
        row = new_frame(rng, blocks, truth)
        if row['raw'] not in seen:
            seen.add(row['raw']); pool.append(row)
    order = rng.sample(range(32), 32)
    isolated = [blocks[i][:CUTS[truth[i]]] for i in order]
    paired_control = [rng.choice(blocks) for _ in range(128)]
    return {'case': index, 'seed': SEED+index, 'blocks': blocks, 'true_cut_indices': truth,
            'training_raw': training, 'context_frames': [r['raw'] for r in pool[:128]],
            'pair_control_frames': paired_control, 'isolated_frames': isolated,
            'isolated_group_order': order,
            'new_targets': pool[128:],
            'paired_targets': [{'raw': raw, 'true_units': [raw[:CUTS[ci]], raw[CUTS[ci]:]]} for raw, ci in zip(blocks, truth)]}


def evaluate_targets(parser, keyset, targets):
    counts = collections.Counter(); examples = []
    for target in targets:
        result = consensus_decode(parser, keyset, target['raw'])
        if target['true_units'] not in [p['units'] for p in result['possible_paths']]:
            raise AssertionError('valid true target path was lost')
        counts[result['status']] += 1
        if result['status'] == 'unique' and result['prediction'] != target['true_units']:
            raise AssertionError('false confident prediction despite valid family/observations')
        if not any(r['status'] == result['status'] for r in examples):
            examples.append({'raw': target['raw'], 'status': result['status'],
                             'prediction': result['prediction'], 'possible_paths': result['possible_paths']})
    return {'targets': len(targets), 'unique': counts['unique'], 'ambiguous': counts['ambiguous'],
            'inconsistent': counts['inconsistent'], 'unique_fraction': counts['unique']/len(targets),
            'wrong_unique': 0, 'examples': examples,
            'scope': 'Condition on target raw frame locally; compatible target paths may reject keys that cannot emit this frame. Target is not added to adaptation or used to choose parameters.'}


def contamination(parser, f):
    group = f['isolated_group_order'][0]
    true_value = f['true_cut_indices'][group]
    bad = f['blocks'][group][:CUTS[(true_value+1) % 3]]
    good = f['blocks'][group][:CUTS[true_value]]
    badset = KeySet(32, constraints_from_frames(parser, [bad]))
    both = KeySet(32, constraints_from_frames(parser, [bad, good]))
    return {'group': group, 'bad_frame': bad, 'true_frame': good,
            'bad_only_keys': badset.count(),
            'true_key_still_allowed': bool(badset.count(tuple(enumerate(f['true_cut_indices'])))),
            'contradictory_frames_keys': both.count(),
            'scope': 'Wrong framing is not always detectable from copied training alone. A sound conditional solver can be wrong if assumptions/observations are false.'}


def run_case(index):
    f = fixture(index)
    parser = FrameParser(f['blocks'])
    rows = []
    for kind in KINDS:
        available = f['pair_control_frames'] if kind == KINDS[0] else f['context_frames'] if kind == KINDS[1] else f['isolated_frames']
        for dose in ANCHORS if kind == KINDS[2] else DOSES:
            try:
                frames = available[:dose]
                constraints = constraints_from_frames(parser, frames)
                keyset = KeySet(32, constraints)
                count = keyset.count()
                # Truth enters a separate verifier, never the inference
                # object's state/cache or branch-selection procedure.
                verifier = KeySet(32, constraints)
                if verifier.count(tuple(enumerate(f['true_cut_indices']))) != 1:
                    raise AssertionError('valid observations excluded true key')
                if kind == KINDS[0] and count != 3**32:
                    raise AssertionError('paired control falsely informative')
                if kind == KINDS[2] and count != 3**(32-dose):
                    raise AssertionError('isolated-unit analytic count mismatch')
                support = keyset.supported_domains()
                row = {'kind': kind, 'dose': dose, 'status': 'exact', 'compatible_keys': count,
                       'remaining_bits_uniform_key_prior': math.log2(count),
                       'identified_cut_variables': sum(len(v) == 1 for v in support),
                       'supported_cut_indices': support,
                       'paired_boundary_diagnostic': evaluate_targets(parser, keyset, f['paired_targets']),
                       'new_recombination_targets': evaluate_targets(parser, keyset, f['new_targets']),
                       'search_nodes_all_queries': keyset.nodes}
                rows.append(row)
            except ResourceLimit as error:
                rows.append({'kind': kind, 'dose': dose, 'status': 'resource_limit', 'reason': str(error)})
    return {'fixture': f, 'rows': rows, 'invalid_frame_control': contamination(parser, f)}


def build():
    cases = []
    for i in range(30):
        cases.append(run_case(i))
        print('case '+str(i)+' complete', flush=True)
    summary = []
    for kind in KINDS:
        for dose in ANCHORS if kind == KINDS[2] else DOSES:
            rows = [r for c in cases for r in c['rows'] if r['kind'] == kind and r['dose'] == dose]
            exact = [r for r in rows if r['status'] == 'exact']
            summary.append({'kind': kind, 'dose': dose, 'exact_cases': len(exact), 'resource_limits': len(rows)-len(exact),
                'unique_key_cases': sum(r['compatible_keys'] == 1 for r in exact),
                'mean_remaining_bits': sum(r['remaining_bits_uniform_key_prior'] for r in exact)/len(exact) if exact else None,
                'mean_identified_cuts': sum(r['identified_cut_variables'] for r in exact)/len(exact) if exact else None,
                'mean_paired_boundary_unique_fraction': sum(r['paired_boundary_diagnostic']['unique_fraction'] for r in exact)/len(exact) if exact else None,
                'mean_new_target_unique_fraction': sum(r['new_recombination_targets']['unique_fraction'] for r in exact)/len(exact) if exact else None,
                'wrong_unique_predictions': sum(r['paired_boundary_diagnostic']['wrong_unique']+r['new_recombination_targets']['wrong_unique'] for r in exact)})
    return {'cases': cases, 'summary': summary, 'baseline_keys': 3**32,
            'baseline_bits_uniform_key_prior': math.log2(3**32),
            'game_application': 'NOT_LICENSED_SUPPLIED_CANDIDATE_FAMILY_ONLY', 'verified_translations': 0,
            'scope': 'Exact inference conditional on supplied candidate word family and valid message framing, not a general vocabulary learner or English translation. Abstract numeric fixtures, no new authors/semantic validation.'}


def freeze():
    if (ROOT / 'data/round18_evidence_manifest.json').exists():
        raise ValueError('already frozen')
    files = ['data/round18_protocol.json', 'scripts/context_constraint_solver.py',
             'scripts/context_evidence_experiment.py']
    dump('data/round18_evidence_manifest.json', {'stage': 'Before generated-case results',
                                               'sha256': {p: sha(p) for p in files}})


def main(check=False):
    for path, expected in load('data/round18_evidence_manifest.json')['sha256'].items():
        if sha(path) != expected:
            raise ValueError('frozen input changed: '+path)
    if check:
        for path, expected in load('data/round18_result_manifest.json')['sha256'].items():
            if sha(path) != expected:
                raise ValueError('published artifact changed: '+path)
    start = time.monotonic()
    result = build()
    if check:
        if load('results/round18_context_evidence.json') != result:
            raise ValueError('full replay mismatch')
    else:
        dump('results/round18_context_evidence.json', result)
        dump('results/round18_execution.json', {'seconds': round(time.monotonic()-start, 3),
            'cases': 30, 'condition_budget_fits': 750,
            'game_application': result['game_application'], 'verified_translations': 0})
    print('Round18 '+('full replay matched.' if check else 'complete.'), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    elif args.run or args.check:
        main(args.check)
    else:
        parser.error('use --freeze, --run or --check')
