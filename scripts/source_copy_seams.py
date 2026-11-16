#!/usr/bin/env python3
"""A game-corpus-derived candidate family: exact raw two-copy joins.

Published cut is used only by scorer/control generator, not find_splits.
No plaintext language score or meaning is inferred.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random

from zero_rule_constraints import alignments

ROOT = Path(__file__).resolve().parents[1]
SEED = 193609


def load(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def dump(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def occurrences(raw, needle):
    start = raw.find(needle)
    while start >= 0:
        yield start
        start = raw.find(needle, start+1)


def witnesses(library, raw):
    return [{'book_id': b['id'], 'start': start, 'end': start+len(raw)}
            for b in library for start in occurrences(b['digits'], raw)]


def find_splits(raw, library, details=False):
    found = []
    for cut in range(1, len(raw)):
        left, right = raw[:cut], raw[cut:]
        if not any(left in b['digits'] for b in library) or not any(right in b['digits'] for b in library):
            continue
        row = {'cut': cut, 'lengths': [cut, len(raw)-cut], 'both_pieces_at_least12': min(cut, len(raw)-cut) >= 12}
        if details:
            row['left_witnesses'], row['right_witnesses'] = witnesses(library, left), witnesses(library, right)
            row['address_combinations'] = len(row['left_witnesses'])*len(row['right_witnesses'])
        found.append(row)
    return found


def inherited(library, hits):
    byid = {b['id']: b for b in library}
    out = []
    for hit in hits:
        b = byid[hit['book_id']]
        for ai, omitted in enumerate(alignments(b)['paths']):
            omitted = set(omitted); offsets = [0]
            for i in range(len(b['codes'])):
                offsets.append(offsets[-1]+(1 if i in omitted else 2))
            positions = {v: i for i, v in enumerate(offsets)}
            if hit['start'] in positions and hit['end'] in positions:
                out.append({**hit, 'alignment_index': ai,
                            'codes': b['codes'][positions[hit['start']]:positions[hit['end']]]})
    return {'compatible_witnesses': out,
            'distinct_numeric_code_sequences': [list(v) for v in sorted({tuple(r['codes']) for r in out})],
            'scope': 'Conditional inherited book alignments; no new universal raw->codes decoder.'}


def build():
    inventory = {r['id']: r for r in load('data/source_validation_inventory.json')}
    pieces = [inventory[k]['text'] for k in ('chayenne_2009_part1', 'chayenne_2009_part2')]
    raw, published_cut = ''.join(pieces), len(pieces[0])
    books = load('data/normalized_books.json'); split = load('data/normalized_splits.json')
    primary = [b for b in books if b['id'] in split['discovery_book_ids']]
    cases = {}
    for name, library in (('discovery68', primary), ('all70', books)):
        cuts = find_splits(raw, library, True)
        for row in cuts:
            row['left_inherited'] = inherited(library, row['left_witnesses'])
            row['right_inherited'] = inherited(library, row['right_witnesses'])
        cases[name] = {'one_book_full_answer_witnesses': witnesses(library, raw),
                       'two_piece_splits': cuts, 'published_cut_recovered': any(v['cut'] == published_cut for v in cuts)}
    pools = [[b['digits'][i:i+length] for b in primary for i in range(len(b['digits'])-length+1)]
             for length in map(len, pieces)]
    controls = []
    for ki, kind in enumerate(('global_digit_bijection', 'digit_shuffle', 'two_copied_fragments')):
        rng = random.Random(SEED+ki)
        rows = []
        for trial in range(999):
            if kind == 'global_digit_bijection':
                labels = list('0123456789'); rng.shuffle(labels)
                target = raw.translate(str.maketrans('0123456789', ''.join(labels)))
            elif kind == 'digit_shuffle':
                chars = list(raw); rng.shuffle(chars); target = ''.join(chars)
            else:
                target = rng.choice(pools[0])+rng.choice(pools[1])
            cuts = [v['cut'] for v in find_splits(target, primary)]
            rows.append({'trial': trial, 'cuts': cuts, 'original_or_generated_cut_included': published_cut in cuts,
                         'unique_correct_cut': cuts == [published_cut]})
        if kind == 'two_copied_fragments':
            assert all(r['original_or_generated_cut_included'] for r in rows)
        controls.append({'kind': kind, 'replicates': 999,
                         'has_any_two_copy_cover': sum(bool(r['cuts']) for r in rows),
                         'unique_correct_cut': sum(r['unique_correct_cut'] for r in rows), 'rows': rows})
    return {'target_numeric': raw, 'published_cut': published_cut, 'published_piece_lengths': list(map(len, pieces)),
            'library_results': cases, 'controls': controls,
            'reversed_piece_order_splits': find_splits(pieces[1]+pieces[0], primary, True),
            'new_verified_translations': 0,
            'scope': 'Already exposed interview and corpus; mechanical exact-copy seam only. Address multiplicity/substring reuse is not independent semantic validation or proof of editing history.'}


def freeze():
    if (ROOT / 'data/round19_copy_boundary_manifest.json').exists():
        raise ValueError('already frozen')
    files = ['data/round19_copy_boundary_protocol.json', 'scripts/source_copy_seams.py',
             'scripts/zero_rule_constraints.py', 'data/source_validation_inventory.json',
             'data/normalized_books.json', 'data/normalized_splits.json']
    dump('data/round19_copy_boundary_manifest.json', {'stage': 'Before new copy-seam enumeration',
                                                   'sha256': {p: sha(p) for p in files}})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    elif args.run:
        for path, expected in load('data/round19_copy_boundary_manifest.json')['sha256'].items():
            if sha(path) != expected:
                raise ValueError('frozen seam input changed: '+path)
        dump('results/round19_copy_seams.json', build())
        print('All raw cuts and2997controls executed; no English meaning inferred.')
    else:
        parser.error('use --freeze or --run')
