#!/usr/bin/env python3
"""Exploratory NPC word relations; never assigns English meanings.

Community-selected anagram correspondences are tested structurally with two
controls. Within-word shuffles preserve the tested statistic by construction.
"""
import collections
import hashlib
import json
import pathlib
import random
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLAN = ROOT / 'data/npc_digit_relation_plan.json'


def tokens(text):
    return re.findall(r'[0-9]+', text)


def signature(word):
    return ''.join(sorted(word))


def matching_words(source, target):
    available = {signature(w) for w in target if len(w) >= 3}
    return sorted({w for w in source if len(w) >= 3 and signature(w) in available})


def main():
    if PLAN.exists():
        raise RuntimeError('relation plan exists; preserve prior exploration')
    source = ROOT / 'data/source_validation_inventory.json'
    byid = {x['id']: x for x in json.loads(source.read_text())}
    knight = tokens(byid['knightmare_2012']['text'])
    poem = tokens(byid['avar_tar_poem']['text'])
    poll = tokens(byid['official_poll_2020_option_c']['text'])
    plan = {'role': 'Exploratory follow-up to a community-selected correspondence, not blind semantic validation.',
            'comparison': 'Distinct whole Knightmare tokens of length>=3 whose sorted digits equal a whole Avar token.',
            'controls': {'replicates': 999, 'seed': 106690000,
                         'global_relabel': 'Uniform bijection of digits1..9, with0fixed, applied to all poem tokens. Preserves lengths, repetition/equality structure, zero positions and histogram shape, but not counts attached to specific nonzero labels.',
                         'within_word_shuffle': 'Shuffle digits inside each unique poem word, use the same transformed word at each repetition. Preserves exact per-word digit multisets and the statistic itself.'},
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'implementation_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
            'limits': ['Community attention selected these pairs and relation type; reported ranks are exploratory.',
                       'Anagram equality is not reversal, a unique permutation, shared meaning or an English gloss.',
                       'No tested relation supplies a general translator or new semantic validation.']}
    PLAN.write_text(json.dumps(plan, indent=2) + '\n')
    matched = matching_words(knight, poem)
    observed = len(matched)
    controls = []
    for mode in ['global_relabel', 'within_word_shuffle']:
        rows = []
        for i in range(999):
            rng = random.Random(plan['controls']['seed'] + i + (10000 if mode == 'within_word_shuffle' else 0))
            if mode == 'global_relabel':
                digits = list('123456789')
                rng.shuffle(digits)
                mapping = dict(zip('0123456789', ['0'] + digits))
                transformed = [''.join(mapping[c] for c in w) for w in poem]
            else:
                mapping = {}
                for w in sorted(set(poem)):
                    chars = list(w)
                    rng.shuffle(chars)
                    mapping[w] = ''.join(chars)
                transformed = [mapping[w] for w in poem]
                assert [signature(w) for w in transformed] == [signature(w) for w in poem]
            value = len(matching_words(knight, transformed))
            rows.append({'replicate': i, 'matched_source_words': value})
        controls.append({'mode': mode, 'trials': rows,
                         'exploratory_upper_tail_rank': (1 + sum(x['matched_source_words'] >= observed for x in rows)) / 1000,
                         'statistic_invariant': len({x['matched_source_words'] for x in rows}) == 1})
    pairs = [{'knightmare': w, 'avar': t, 'same_digit_multiset': True,
              'literal_reversal': w[::-1] == t} for w in matched for t in sorted(set(poem)) if signature(w) == signature(t)]
    shared = sorted(set(poem) & set(poll))
    assert '3478'[::-1] == '8743' and signature('3478') == signature('4378')
    out = {'plan': plan, 'plan_sha256': hashlib.sha256(PLAN.read_bytes()).hexdigest(),
           'numeric_word_counts': {'knightmare': len(knight), 'avar': len(poem), 'poll': len(poll)},
           'matched_distinct_knightmare_words': observed, 'pairs': pairs,
           'exact_shared_avar_poll_words': shared,
           'controls': controls, 'english_glosses_inferred': 0, 'verified_translations': 0}
    (ROOT / 'results/npc_digit_relation_audit.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'pairs': pairs, 'shared_avar_poll': shared,
                      'controls': [{k: x[k] for k in ['mode', 'exploratory_upper_tail_rank', 'statistic_invariant']} for x in controls]}, indent=2))


if __name__ == '__main__':
    main()
