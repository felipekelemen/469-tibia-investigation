#!/usr/bin/env python3
"""Compare raw copying with source token boundaries, without guessing target codes."""
import hashlib
import json
import pathlib

from zero_rule_constraints import alignments

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    diagnosis = json.loads((ROOT / 'results/kharos_copy_diagnosis.json').read_text())
    target = json.loads((ROOT / 'data/external_book_round10.json').read_text())['digits']
    offsets = {}
    for b in books:
        alternatives = []
        for omitted in alignments(b)['paths']:
            mask = set(omitted)
            positions = [0]
            for i, _ in enumerate(b['codes']):
                positions.append(positions[-1] + (1 if i in mask else 2))
            alternatives.append({value: i for i, value in enumerate(positions)})
        offsets[b['id']] = alternatives
    rows = []
    for piece in diagnosis['observed'][0]['path']:
        raw = piece['literal']
        matches = []
        compatible = []
        for b in books:
            start = b['digits'].find(raw)
            while start >= 0:
                end = start + len(raw)
                matches.append({'book_id': b['id'], 'raw_start': start, 'raw_end': end})
                for aindex, positions in enumerate(offsets[b['id']]):
                    if start in positions and end in positions:
                        compatible.append({'book_id': b['id'], 'raw_start': start, 'raw_end': end,
                                           'alignment_index': aindex,
                                           'codes': b['codes'][positions[start]:positions[end]]})
                start = b['digits'].find(raw, start + 1)
        assert target[piece['raw_start']:piece['raw_end']] == raw
        rows.append({'target_raw_start': piece['raw_start'], 'target_raw_end': piece['raw_end'],
                     'raw_length': len(raw), 'raw': raw, 'raw_occurrences': len(matches),
                     'has_source_code_boundary_match': bool(compatible),
                     'compatible_code_boundary_witnesses': compatible[:5],
                     'unique_boundary_code_sequences': len({tuple(x['codes']) for x in compatible})})
    out = {'diagnostic_result_sha256': hashlib.sha256((ROOT / 'results/kharos_copy_diagnosis.json').read_bytes()).hexdigest(),
           'pieces': rows, 'pieces_without_any_source_code_boundary_match': sum(not x['has_source_code_boundary_match'] for x in rows),
           'first16digits_boundary_match': rows[0]['has_source_code_boundary_match'],
           'limits': ['Representative minimum raw cover, not a reconstruction of author editing history.',
                      'Failure of fragment-boundary transfer does not disprove a cipher; texts can be clipped, spliced, altered or tokenized differently.',
                      'No whole target code sequence or English plaintext was inferred.'], 'verified_translations': 0}
    (ROOT / 'results/kharos_boundary_audit.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'pieces': len(rows), 'without_boundary_match': out['pieces_without_any_source_code_boundary_match'],
                      'first16digits_boundary_match': out['first16digits_boundary_match']}, indent=2))


if __name__ == '__main__':
    main()
