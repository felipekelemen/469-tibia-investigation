#!/usr/bin/env python3
"""Explain frozen round16 endpoint results with explicit source emissions.

Post-experiment descriptive certificates only. Neighboring book digits are
not inserted into the NPC text, translated or proposed as corrected speech.
"""
import json

from wordcode_transfer_experiment import ABLATE, ROOT, dump, inventory
from zero_rule_constraints import alignments


def build():
    entries, _ = inventory()
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    targets = {r['id']: r['text'].rstrip('.!') for r in entries if r['id'] in ABLATE}
    records = []
    for target_id, target in targets.items():
        for b in books:
            start = b['digits'].find(target)
            if start < 0:
                continue
            paths = alignments(b)['paths']
            while start >= 0:
                end = start+len(target)
                for ai, omitted in enumerate(paths):
                    mask, cursor, emissions = set(omitted), 0, []
                    for i, code in enumerate(b['codes']):
                        wire = code[1:] if i in mask else code
                        emissions.append({'index': i, 'code': code, 'wire': wire,
                                          'start': cursor, 'end': cursor+len(wire)})
                        cursor += len(wire)
                    assert ''.join(e['wire'] for e in emissions) == b['digits']
                    parent = [e for e in emissions if e['start'] < end and e['end'] > start]
                    a, z = parent[0]['start'], parent[-1]['end']
                    records.append({'target_id': target_id, 'target': target, 'book_id': b['id'],
                                    'raw_start': start, 'raw_end': end, 'alignment_index': ai,
                                    'source_omitted_indices': list(omitted),
                                    'parent_raw_start': a, 'parent_raw_end': z,
                                    'parent_emissions': parent,
                                    'left_book_remainder': b['digits'][a:start],
                                    'right_book_remainder': b['digits'][end:z],
                                    'start_is_code_boundary': a == start,
                                    'end_is_code_boundary': z == end})
                start = b['digits'].find(target, start+1)
    observed_codes = {c for b in books for c in b['codes']}
    alternatives = []
    for target_id, target in targets.items():
        if len(target) % 2 == 0:
            pairs = [target[i:i+2] for i in range(0, len(target), 2)]
            alternatives.append({'target_id': target_id, 'fixed_pairs': pairs,
                                 'all_codes_in_imported_inventory': all(c in observed_codes for c in pairs)})
    return {'records': records, 'standalone_pair_counterexamples': alternatives,
            'scope': 'Every compatible imported alignment for the two predeclared copied shouts. Parent code spans are observed book context, not corrected NPC speech, an inferred decoder or English.'}


if __name__ == '__main__':
    result = build()
    dump('results/round16_boundary_certificates.json', result)
    print('Explicit boundary certificates:' + str(len(result['records'])))
