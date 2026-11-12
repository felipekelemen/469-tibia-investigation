#!/usr/bin/env python3
"""Offline complete replay of source-conserving code constraints and provenance."""
import collections
import hashlib
import json
import random
import re

from conserved_code_experiment import (PROTOCOL, RESULT, ROOT, anagram_groups,
                                       digest, fixture, trial, truth_source, verify)
from conserved_code_parser import source_inventories
from omission_set_reference import enumerate_parses
from raw_copy_parser import raw_novelty


def main():
    manifest = json.loads((ROOT / 'data/round12_evidence_manifest.json').read_text())
    for path, expected in manifest['sha256'].items():
        if digest(ROOT / path) != expected:
            raise ValueError('round12 artifact changed: ' + path)
    p = json.loads(PROTOCOL.read_text())
    verify(p)
    r = json.loads(RESULT.read_text())
    if not r['complete'] or r['protocol_sha256'] != digest(PROTOCOL):
        raise ValueError('incomplete result or changed protocol')
    source = truth_source()
    if len(r['positives']) != 60:
        raise ValueError('missing positive fixtures')
    for row in r['positives']:
        f = fixture(row['fixture'], row['kind'])
        if f['raw'] != row['raw'] or f['truth_codes'] != row['truth_codes']:
            raise ValueError('positive truth changed')
        if trial(f['raw'], source, p) != row['trials']:
            raise ValueError('positive parsing changed')
        for mode in row['trials']:
            if row['unique_truth_recoveries'][mode] != (row['trials'][mode]['unique_codes'] == f['truth_codes']):
                raise ValueError('incorrect recovery classification')
        if row['fixture'] in (0, 15):
            ref = enumerate_parses(f['raw'], source)
            codes = row['trials']['code_multiset']
            if not ref['complete'] or len(ref['solutions']) != sum(int(x['path_count']) for x in codes['inventories']):
                raise ValueError('independent positive path count disagrees')
            if f['truth_codes'] not in [s['codes'] for s in ref['solutions']]:
                raise ValueError('independent enumerator missed a positive truth')
    for gate in r['gates']:
        rows = [row for row in r['positives'] if row['kind'] == gate['kind']]
        feasible = sum(row['trials'][gate['mode']]['status'] == 'SAT' and row['trials'][gate['mode']]['all_counts_complete'] for row in rows)
        unique = sum(row['unique_truth_recoveries'][gate['mode']] for row in rows)
        if feasible != gate['feasible_complete'] or unique != gate['unique_exact']:
            raise ValueError('gate counts disagree')
        if gate['feasibility_pass'] != (feasible == 30) or gate['recovery_pass'] != (unique >= 27):
            raise ValueError('gate verdict changed')
    raw = json.loads((ROOT / 'data/external_book_round10.json').read_text())['digits']
    if collections.Counter(raw) != collections.Counter(source['digits']) or len(raw) != 137:
        raise ValueError('digit conservation changed')
    if trial(raw, source, p) != r['target']:
        raise ValueError('target constraints changed')
    ref = enumerate_parses(raw, source)
    if ref != r['independent_reference'] or ref['patterns'] != 54740 or ref['solutions']:
        raise ValueError('independent target enumeration changed')
    # Tiny direct UNSAT certificate for unchanged wire tokens: only51starts
    # the target; no remaining wire token can start its suffix59... .
    inventory = source_inventories(source, 'wire_multiset')[0]
    matches = [(code, forms[0]) for code, _, forms in inventory if raw.startswith(forms[0])]
    if matches != [(51, '51')] or any(raw[2:].startswith(forms[0]) for _, _, forms in inventory):
        raise ValueError('prefix contradiction changed')
    for null in r['nulls']:
        if len(null['trials']) != 99:
            raise ValueError('missing order controls')
        for i, row in enumerate(null['trials']):
            units = list(raw) if null['mode'] == 'digit_shuffle' else [raw[j:j + 8] for j in range(0, len(raw), 8)]
            random.Random(p['nulls']['seed'] + i).shuffle(units)
            if trial(''.join(units), source, p) != row['trials']:
                raise ValueError('order control changed')
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    byid = {b['id']: b for b in books}
    if anagram_groups(books) != r['anagram_groups'] or len(r['secondary_pairs']) != 10:
        raise ValueError('anagram pair inventory changed')
    for row in r['secondary_pairs']:
        if trial(byid[row['target']]['digits'], byid[row['source']], p) != row['trials']:
            raise ValueError('secondary pair changed')
        if collections.Counter(byid[row['source']]['codes']) == collections.Counter(byid[row['target']]['codes']):
            raise ValueError('supplied code histograms unexpectedly match')
    alternative = next(row for row in r['secondary_pairs'] if row['source'] == '58' and row['target'] == '59')
    code_map = json.loads((ROOT / 'data/normalized_code_map.json').read_text())
    unique = alternative['trials']['code_multiset']['unique_codes']
    if unique is None or len(unique) != 139 or len(byid['59']['codes']) != 138:
        raise ValueError('secondary alternative code count changed')
    if ''.join(code_map[f'{c:02d}'] for c in unique) == byid['59']['symbols']:
        raise ValueError('secondary alternative symbol sequence unexpectedly matches')
    external = json.loads((ROOT / 'data/external_samples_round12.json').read_text())
    audit = json.loads((ROOT / 'results/external_source_audit_round12.json').read_text())
    item = next(x for x in external if x['id'] == 'your_true_colour_2012')
    digits = re.sub('[^0-9]', '', item['text'])
    if len(digits) != 21 or hashlib.sha256(digits.encode()).hexdigest() != audit['numeric_sha256']:
        raise ValueError('external numeric transcription changed')
    if raw_novelty(digits, books, lengths=(4, 5, 8, 12, 16)) != audit['raw_novelty']:
        raise ValueError('external source overlap changed')
    if r['conditional_v4_literal'] is not None or r['new_key_fits'] or r['verified_translations']:
        raise ValueError('unexpected semantic output')
    print('Replayed60mechanical positives,198paired order controls and10directed real anagram pairs in both modes.')
    print('Kharos/book22: identical137digit histograms; both conservation models UNSAT, counts complete.')
    print('Independent omitted-index enumeration:54740patterns,0solutions;4positive reference replays also pass.')
    print('Your True Colour:21digits, official indexed provenance, no attested English gloss.')
    print('New key fits:0. English target outputs:0. Verified translations:0.')


if __name__ == '__main__':
    main()
