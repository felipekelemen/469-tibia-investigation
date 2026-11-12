#!/usr/bin/env python3
"""Verify frozen evidence and replay exact prefix coding; --full replays all fixtures."""
import argparse
import hashlib
import json
import random

from copy_wire_experiment import (PROTOCOL, RESULT, ROOT, SEED, components,
                                  digest, fit, fixture, pair, verify)


def main(full=False):
    manifest = json.loads((ROOT / 'data/round11_evidence_manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if digest(ROOT / relative) != expected:
            raise ValueError('round11 artifact changed: ' + relative)
    p = json.loads(PROTOCOL.read_text())
    result = json.loads(RESULT.read_text())
    verify(p)
    if not result['complete'] or result['protocol_sha256'] != digest(PROTOCOL):
        raise ValueError('incomplete experiment or changed protocol')
    if len(result['positive_controls']) != 60:
        raise ValueError('expected60paired source conditions')
    for gate in result['gates']:
        rows = [r['trials'][gate['cut']] for r in result['positive_controls'] if r['content'] == gate['content']]
        count = sum(r['preferred'] == gate['expected'] for r in rows)
        if count != gate['correct'] or (count >= 27) != gate['passes']:
            raise ValueError('incorrect mechanism gate')
    if result['all_mechanism_gates_pass'] != all(g['passes'] for g in result['gates']):
        raise ValueError('incorrect global gate')
    replayed = 0
    for row in result['positive_controls']:
        if not full and row['fixture'] not in (0, 15):
            continue
        f = fixture(row['fixture'], row['content'])
        if hashlib.sha256(json.dumps(f['books'], sort_keys=True).encode()).hexdigest() != row['source_books_sha256']:
            raise ValueError('fixture source changed')
        if f['truth_copy_spans'] != row['truth_copy_spans']:
            raise ValueError('synthetic cutting truth changed')
        context, indices = fit(f['books'], p)
        for cut in p['cuts']:
            if pair(f['targets'][cut], context, indices) != row['trials'][cut]:
                raise ValueError('fixture outcome changed')
            replayed += 1
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    raw = json.loads((ROOT / 'data/external_book_round10.json').read_text())['digits']
    context, indices = fit(books, p)
    if pair(raw, context, indices, full=True) != result['target']:
        raise ValueError('external target changed')
    for null in result['target_controls']:
        if len(null['trials']) != 99:
            raise ValueError('missing controls')
        for i, recorded in enumerate(null['trials']):
            rng = random.Random(SEED + 100000 + i)
            units = list(raw) if null['mode'] == 'digit_shuffle' else [raw[j:j + 8] for j in range(0, len(raw), 8)]
            rng.shuffle(units)
            if pair(''.join(units), context, indices) != recorded:
                raise ValueError('control outcome changed')
        rank = (1 + sum(r['delta_code_minus_raw_bits'] >= result['target']['delta_code_minus_raw_bits'] for r in null['trials'])) / 100
        if rank != null['exploratory_upper_rank']:
            raise ValueError('rank changed')
    comps = components(books)
    if [len(g) for g in comps] != [68, 2]:
        raise ValueError('raw16 dependency graph changed')
    for group, fold in zip(comps, result['raw16_component_folds'], strict=True):
        train = [b for i, b in enumerate(books) if i not in group]
        context, indices = fit(train, p)
        for index, row in zip(group, fold['targets'], strict=True):
            if {'id': books[index]['id'], **pair(books[index]['digits'], context, indices)} != row:
                raise ValueError('component prediction changed')
        for family in ('raw', 'codes'):
            if sum(r['codecs'][family]['bits'] for r in fold['targets']) != fold['total_bits'][family]:
                raise ValueError('component total changed')
    if result['verified_translations'] or result['english_outputs'] or result['new_key_fits']:
        raise ValueError('unexpected semantic claim')
    print(f'Verified120paired mechanism targets, replayed{replayed}; all198nulls and70component-held targets replayed.')
    print('All replayed prefix bitstreams decode exactly to raw digits. Conditional source libraries are shared side information.')
    print('Mechanism gates:', result['all_mechanism_gates_pass'])
    print('External target bits:', {f: r['bits'] for f, r in result['target']['codecs'].items()})
    print('English outputs:0. New key fits:0. Verified translations:0.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    main(parser.parse_args().full)
