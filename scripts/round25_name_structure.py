#!/usr/bin/env python3
"""Finite structural-family audit. Operational numeric groups have no English gloss."""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import argparse
import json
import random
import re

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('identity', 'whole_reverse', 'cyclic_rotation', 'pair_mirror',
            'pair_permutation', 'pair_mirror_and_permutation', 'whole_anagram')


def signature(word, family):
    if family == 'identity':
        value = word
    elif family == 'whole_reverse':
        value = min(word, word[::-1])
    elif family == 'cyclic_rotation':
        value = min(word[i:]+word[:i] for i in range(len(word)))
    elif family == 'whole_anagram':
        value = ''.join(sorted(word))
    else:
        padded = ('0' if len(word) % 2 else '') + word
        pairs = [padded[i:i+2] for i in range(0, len(padded), 2)]
        if family in ('pair_mirror', 'pair_mirror_and_permutation'):
            pairs = [''.join(sorted(p)) for p in pairs]
        if family in ('pair_permutation', 'pair_mirror_and_permutation'):
            pairs.sort()
        if family not in FAMILIES:
            raise ValueError(family)
        value = '/'.join(pairs)
    return (len(word), value)


def signature_map(words, family):
    out = defaultdict(set)
    for word in words:
        out[signature(word, family)].add(word)
    return out


def shared_nonidentical(left, right):
    return {s: sorted((a,b) for a in left[s] for b in right[s] if a != b)
            for s in left.keys() & right.keys()
            if any(a != b for a in left[s] for b in right[s])}


def evaluate(clusters, details=False):
    maximum, primary, rows = 0, 0, []
    for family in FAMILIES:
        maps = {k: signature_map(v, family) for k,v in clusters.items()}
        for a,b in combinations(clusters, 2):
            hits = shared_nonidentical(maps[a], maps[b]); count = len(hits)
            maximum = max(maximum, count)
            if family == 'whole_anagram' and {a,b} == {'avar','knightmare'}:
                primary = count
            if details and count:
                rows.append({'family': family, 'sources': [a,b], 'signature_count': count,
                             'matches': [{'signature': list(s), 'pairs': hits[s]} for s in sorted(hits)]})
    return {'primary_avar_knightmare_anagrams': primary, 'maximum_all_pairs_families': maximum}, rows


def clusters_from_inventory(protocol):
    inventory = {r['id']: r['text'] for r in json.loads((ROOT/'data/source_validation_inventory.json').read_text())}
    out = {}
    for source, ids in protocol['source_clusters'].items():
        out[source] = list(dict.fromkeys(w for id in ids for w in re.findall(r'\d+', inventory[id]) if len(w) >= 3))
    return out


def sample_null(clusters, kind, rng):
    if kind == 'whole_group_reassignment':
        by_length = defaultdict(list)
        for words in clusters.values():
            for w in words:
                by_length[len(w)].append(w)
        for words in by_length.values():
            rng.shuffle(words)
        return {k: [by_length[len(w)].pop() for w in words] for k,words in clusters.items()}
    out = {}
    for key, words in clusters.items():
        if kind == 'cluster_digit_pool':
            arr = list(''.join(words)); rng.shuffle(arr); pos = 0; changed = []
            for w in words:
                changed.append(''.join(arr[pos:pos+len(w)])); pos += len(w)
            out[key] = changed
        elif kind == 'cluster_digit_relabel':
            digits = list('0123456789'); rng.shuffle(digits)
            table = str.maketrans('0123456789', ''.join(digits))
            out[key] = [w.translate(table) for w in words]
        else:
            raise ValueError(kind)
    return out


def run():
    protocol = json.loads((ROOT/'data/round25_protocol.json').read_text())
    assert protocol['families'] == list(FAMILIES)
    clusters = clusters_from_inventory(protocol)
    observed, matches = evaluate(clusters, details=True)
    out = {'operational_groups': clusters, 'clusters': len(clusters), 'source_pairs': len(list(combinations(clusters,2))),
           'families': len(FAMILIES), 'observed': observed, 'observed_matches': matches, 'nulls': {}}
    for offset, kind in enumerate(('cluster_digit_pool','cluster_digit_relabel','whole_group_reassignment')):
        rng = random.Random(protocol['seed']+offset); tails = Counter(); hist = Counter()
        for _ in range(protocol['trials_per_null']):
            simulated, _ = evaluate(sample_null(clusters, kind, rng))
            for stat,value in observed.items():
                tails[stat] += simulated[stat] >= value
            # Family/source selection applied in each draw, compared with the selected observed score.
            tails['maximum_compared_to_primary_score'] += simulated['maximum_all_pairs_families'] >= observed['primary_avar_knightmare_anagrams']
            hist[simulated['maximum_all_pairs_families']] += 1
        out['nulls'][kind] = {'trials': protocol['trials_per_null'], 'tail_counts': dict(tails),
                             'plus_one_tail': {k:(v+1)/(protocol['trials_per_null']+1) for k,v in tails.items()},
                             'maximum_histogram': dict(sorted(hist.items()))}
        print(kind, out['nulls'][kind], flush=True)
    out['3478_equivalence_predictions'] = {
        family: sorted({w for words in clusters.values() for w in words
                        if signature(w,family) == signature('3478',family)}) for family in FAMILIES}
    out['identity_anchor_checks'] = {word: {'same_as_3478_under_whole_anagram': signature(word,'whole_anagram') == signature('3478','whole_anagram')}
                                      for word in ('4378','34334','486486')}
    out['translation_validated'] = False
    out['scope'] = 'All target groups exposed; structural comparison only. Finite multiplicity adjustment, not all community hypotheses. No semantic holdout.'
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--check', action='store_true'); args = p.parse_args()
    output = run(); path = ROOT/'results/round25_structure.json'
    if args.check:
        assert json.loads(path.read_text()) == json.loads(json.dumps(output)), 'replay mismatch'
    else:
        path.write_text(json.dumps(output, indent=2)+'\n')
