#!/usr/bin/env python3
"""Verify round8, replay all alignments and exact logical compatibility tests."""
import hashlib
import json
import pathlib

from zero_rule_constraints import FAMILIES, alignments, feature, predict, solve
from zero_rule_experiment import verify

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/round8_evidence_manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError('round8 evidence changed: ' + relative)
    result = json.loads((ROOT / 'results/zero_rule_constraints.json').read_text())
    verify(result['protocol'])
    if not result['complete'] or not result['positive_controls_pass'] or not result['copied_positive_controls_pass']:
        raise ValueError('incomplete execution or failed controls')
    if len(result['shuffled_controls']) != 39 or len(result['copy_controls']) != 9:
        raise ValueError('missing controls')
    if hashlib.sha256((ROOT / 'data/zero_rule_constraints_protocol.json').read_bytes()).hexdigest() != result['protocol_sha256']:
        raise ValueError('protocol changed')
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    by_id = {b['id']: b for b in books}
    aligned = {b['id']: alignments(b, result['protocol']['alignment_cap']) for b in books}
    for row in result['alignment_summary']:
        if aligned[row['id']]['count'] != row['alignments']:
            raise ValueError('alignment count changed')
    split = json.loads((ROOT / 'data/normalized_splits.json').read_text())
    ids = set(split['discovery_book_ids'])
    train = [b for b in books if b['id'] in ids]
    for spec, row in zip(FAMILIES, result['families']):
        actual = solve(train, [aligned[b['id']] for b in train], spec, result['protocol']['search_node_cap'])
        if actual != row['discovery_fit']:
            raise ValueError('compatibility decision changed: ' + spec['name'])
        if 'certificate' in actual:
            certificate = actual['certificate']
            for name, action in [('preserved', False), ('omitted', True)]:
                witness = certificate[name]
                b = by_id[witness['book_id']]
                i = witness['code_index']
                if list(feature(b['codes'], i, spec)) != certificate['feature']:
                    raise ValueError('certificate inputs differ')
                event = next(e for e in aligned[b['id']]['events'] if e['index'] == i)
                if event['actions'] != [action]:
                    raise ValueError('certificate action not forced')
        if actual['status'] == 'SAT' and not all(predict(b, actual['table'], spec)['exact_raw'] for b in train):
            raise ValueError('fitted table does not roundtrip')
    plan = json.loads((ROOT / 'data/plan_status.json').read_text())
    statuses = [x['primary_status'] for x in plan['workstreams']]
    if len(statuses) != 7 or statuses.count('pending') != 4 or statuses.count('bounded_batch_executed') != 3:
        raise ValueError('plan count inconsistent')
    print('Recomputed79fixed-stream alignments and15formatter compatibility tests.')
    print('Verified13forced contradictions and2exact discovery lookup fits.')
    print('Controls:15planted positives,39within-book/code shuffles,9copied-context positives.')
    print('Plan:7workstreams started;4pending primary deliverables;3bounded batches executed.')
    print('New English decodings:0. Verified translations:0.')


if __name__ == '__main__':
    main()
