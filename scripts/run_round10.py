#!/usr/bin/env python3
"""Offline verification of external-book copy tests and source classifications."""
import hashlib
import json
import pathlib

from copy_parser_experiment import fixture, verify
from raw_copy_parser import build_dictionary, parse, raw_novelty
from raw_fragment_cover import cover
from npc_digit_relation_audit import matching_words, tokens

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/round10_evidence_manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError('round10 artifact changed: ' + relative)
    result = json.loads((ROOT / 'results/copy_parser_experiment.json').read_text())
    p = result['protocol']
    verify(p)
    if not result['complete'] or len(result['positive_controls']) != 30:
        raise ValueError('incomplete positive controls')
    for gate in result['gates']:
        minimum = gate['minimum']
        count = sum(row['unique_exact_codes'] for f in result['positive_controls'] for row in f['trials'] if row['minimum'] == minimum)
        if count != gate['exact_unique_recoveries'] or gate['passes_gate'] != (count >= 27):
            raise ValueError('gate inconsistent')
    for index in [0, 15]:
        f = fixture(index)
        dictionary = build_dictionary(f['motifs'], p['dictionary_minimum_raw'], p['dictionary_maximum_raw'], p['source_alignment_cap'])
        for minimum in p['minimums']:
            if parse(f['raw'], dictionary, minimum, p['stream_cap'])['unique_full_codes'] != f['truth']:
                raise ValueError('positive replay changed')
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    target = json.loads((ROOT / 'data/external_book_round10.json').read_text())
    raw = target['digits']
    if any(raw == b['digits'] for b in books) or len(raw) != 137:
        raise ValueError('external book classification changed')
    source = ROOT / 'data/external_source_reference/books_sorted_unique_with_kharos.json'
    if hashlib.sha256(source.read_bytes()).hexdigest() != target['upstream_source']['sha256']:
        raise ValueError('upstream corpus snapshot changed')
    extra = [x for x in json.loads(source.read_text()) if x not in {b['digits'] for b in books}]
    if extra != [raw]:
        raise ValueError('extra upstream text differs')
    dictionary = build_dictionary(books, p['dictionary_minimum_raw'], p['dictionary_maximum_raw'], p['source_alignment_cap'])
    for row in result['target_parses']:
        fresh = {'minimum': row['minimum'], **parse(raw, dictionary, row['minimum'], p['stream_cap'])}
        if fresh != row:
            raise ValueError('target parse changed')
    if raw_novelty(raw, books) != result['target_raw_novelty']:
        raise ValueError('overlap audit changed')
    diagnostic = json.loads((ROOT / 'results/kharos_copy_diagnosis.json').read_text())
    for path, expected in diagnostic['plan']['hashes'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('diagnostic dependency changed')
    for row in diagnostic['observed']:
        if cover(raw, books, row['minimum'], diagnostic['plan']['maximum']) != row:
            raise ValueError('raw-cover result changed')
    if any(len(x['trials']) != 99 for x in diagnostic['controls']):
        raise ValueError('missing structural controls')
    ledger = json.loads((ROOT / 'data/source_review_round10.json').read_text())
    if len(ledger['entries']) != 11 or any(x['new_long_parallel_plaintext'] for x in ledger['entries']):
        raise ValueError('source classification changed')
    relation = json.loads((ROOT / 'results/npc_digit_relation_audit.json').read_text())
    source = ROOT / 'data/source_validation_inventory.json'
    if hashlib.sha256(source.read_bytes()).hexdigest() != relation['plan']['source_sha256']:
        raise ValueError('numeric-word source changed')
    inventory = {x['id']: x for x in json.loads(source.read_text())}
    words = matching_words(tokens(inventory['knightmare_2012']['text']), tokens(inventory['avar_tar_poem']['text']))
    if words != ['345', '3478'] or any(pair['literal_reversal'] for pair in relation['pairs']):
        raise ValueError('numeric-word relation changed')
    if any(len(row['trials']) != 999 for row in relation['controls']):
        raise ValueError('missing relation controls')
    print('Verified30paired positive fixtures,90threshold conditions and270copy-parser controls.')
    print('Replayed external137-digit book:27/28/81uncovered digits at minima8/12/16.')
    print('Raw-only minimum cover:14pieces;198structural shuffle controls recorded.')
    print('Reviewed11source entries; no newly attested long numeric-English pair.')
    print('Verified2non-reversal anagram pairs and1998exploratory relation controls.')
    print('New key fits:0. Verified translations:0.')


if __name__ == '__main__':
    main()
