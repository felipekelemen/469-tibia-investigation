#!/usr/bin/env python3
"""Descriptive post-fit aggregation and source-overlap audit; no new fitting."""
from collections import Counter
from pathlib import Path
import json
from round28_fixtures import source_words

ROOT = Path(__file__).resolve().parents[1]


def build():
    fixtures = json.loads((ROOT/'data/round28_fixtures.json').read_text())
    qualification = json.loads((ROOT/'results/round28_qualification.json').read_text())
    targets = json.loads((ROOT/'results/round28_targets.json').read_text())
    nulls = json.loads((ROOT/'results/round28_nulls.json').read_text())
    sources = json.loads((ROOT/'data/round28_reference/SOURCES.json').read_text())
    words = {source['path']: source_words(source) for source in sources}
    used, overlap = {}, []
    trains = [w['train_words'] for w in fixtures['windows']]
    for window in fixtures['windows']:
        positions = set(range(window['start_word'], window['end_word']))
        existing = used.setdefault(window['source'], set())
        assert not existing & positions
        existing.update(positions)
        assert words[window['source']][window['start_word']:window['end_word']] == window['train_words']+window['held_words']
        held, train = window['held_words'], window['train_words']
        n = len(held)
        overlap.append({'id': window['id'], 'profile': window['profile'],
            'held_sequence_in_own_training': any(train[i:i+n] == held for i in range(len(train)-n+1)),
            'held_sequence_in_any_training': any(t[i:i+n] == held for t in trains for i in range(len(t)-n+1))})
    profile_overlap = {}
    for profile in sorted({w['profile'] for w in fixtures['windows']}):
        rows = [r for r in overlap if r['profile'] == profile]
        profile_overlap[profile] = {'windows': len(rows),
            'held_sequence_repeated_own': sum(r['held_sequence_in_own_training'] for r in rows),
            'held_sequence_repeated_any': sum(r['held_sequence_in_any_training'] for r in rows)}
    return {'round': 28, 'translation_validated': False,
        'new_semantic_candidates': [], 'lexical_witness_count': len(targets['lexical_candidates']),
        'qualification': {'fits': len(qualification['cases']),
            'source_windows': len(fixtures['windows']),
            'cells': len(qualification['summary']),
            'known_family_letter_cells_qualified': sum(c['known_family_letter_qualified'] for c in qualification['summary']),
            'letter_cases_passed': sum(c['passes'] for c in qualification['cases']),
            'full_keys_exact_unique': sum(c['full_key_unique_exact'] for c in qualification['cases']),
            'exact_word_sequences': sum(c['word_boundaries_and_words_exact'] for c in qualification['cases']),
            'confidently_wrong_letters': sum(c['certified_wrong_letters'] for c in qualification['cases']),
            'unknown_family_selection_qualified': False},
        'overlap_audit': {'nonoverlapping_source_positions': True, 'profiles': profile_overlap, 'windows': overlap,
            'scope':'Paired codecs share windows; short common phrases can recur. Each fit has its own key and receives only its own training ciphertext.'},
        'controls': {family: {'replicates': r['replicates'],
            'replicates_with_any_full_lexical_source': sum(int(k)>0 and v or 0 for k,v in r['maximum_statistic_histogram'].items()),
            'p_upper': r['plus_one_upper_tail'], 'changed_sources': r['changed_sources'],
            'distinct_outputs': r['distinct_outputs']} for family, r in nulls['families'].items()},
        'limits': ['Frozen lexicon and six declared radix/framing models with312affine keys; not all English or all ciphers.',
                   'No authoritative game plaintext, new game source or authenticated original generator.',
                   'Chayenne copies remain exposed dependent material; no semantic holdout claimed.']}


if __name__ == '__main__':
    result = build()
    (ROOT/'results/round28_summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['qualification'], indent=2))
