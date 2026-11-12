#!/usr/bin/env python3
"""Offline replay of round9 state constraints and metadata provenance."""
import hashlib
import json
import pathlib

from book_metadata_audit import parse_listing
from zero_rule_constraints import alignments
from zero_state_constraints import FAMILIES, solve
from zero_state_experiment import domain, positive_corpus, verify

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/round9_evidence_manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError('round9 artifact changed: ' + relative)
    result = json.loads((ROOT / 'results/zero_state_constraints.json').read_text())
    p = result['protocol']
    verify(p)
    if not result['complete'] or not result['all_positives_pass']:
        raise ValueError('incomplete state study or failed positive controls')
    if len(result['families']) != 18 or len(result['shuffled_controls']) != 39 or len(result['shelf_permutations']) != 39:
        raise ValueError('incomplete cases/controls')
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    ids = set(json.loads((ROOT / 'data/normalized_splits.json').read_text())['discovery_book_ids'])
    locations = json.loads((ROOT / 'data/book_location_listing.json').read_text())['locations']
    for spec, recorded in zip(FAMILIES, result['families']):
        corpus = domain(books, locations, spec)
        train = [b for b in corpus if b.get('origin_book_id', b['id']) in ids]
        fit = solve(train, [alignments(b, p['alignment_cap']) for b in train], spec, p['search_node_cap'])
        if json.loads(json.dumps(fit)) != recorded['fit']:
            raise ValueError('state fit changed: ' + spec['name'])
    for index, spec in enumerate(FAMILIES):
        corpus, retries = positive_corpus(spec, p['seed'] + index, p)
        expected = result['positive_controls'][index]
        if retries != expected['generator_retries'] or hashlib.sha256(json.dumps(corpus, sort_keys=True).encode()).hexdigest() != expected['dataset_sha256']:
            raise ValueError('positive fixture changed')
        if solve(corpus, [alignments(b, p['alignment_cap']) for b in corpus], spec, p['search_node_cap'])['status'] != 'SAT':
            raise ValueError('planted rule no longer recoverable')
    audit = json.loads((ROOT / 'results/book_metadata_audit.json').read_text())
    source_manifest = json.loads((ROOT / 'sources/manifest.json').read_text())
    arturo = next(x for x in source_manifest if x['name'] == 'arturo')
    for path, expected in audit['source_hashes'].items():
        relative = path.removeprefix('data/metadata_reference/arturo/')
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected or arturo['files'][relative] != expected:
            raise ValueError('metadata source snapshot differs from pinned upstream')
    ref = ROOT / 'data/metadata_reference/arturo'
    positions = json.loads((ref / 'data/book_positions.json').read_text())
    master = (ref / 'data/master_text.txt').read_text().strip()
    measured = audit['position_field']
    if sum(position < 0 for _, position, _ in positions) != measured['negative_offsets'] or sum(master.find(books[i]['digits']) == position for i, position, _ in positions) != measured['matches_current_master_find']:
        raise ValueError('position field provenance check changed')
    listing = parse_listing((ROOT / 'data/metadata_reference/arturo/docs/archive/Hellgate_Library.txt').read_text())
    if len(listing) != 71 or {x['digits'] for x in listing} != {x['digits'] for x in books}:
        raise ValueError('listing corpus match changed')
    for source in json.loads((ROOT / 'data/metadata_web_evidence.json').read_text())['sources']:
        if [b['id'] for b in books if b['digits'] == source['raw_digits']] != source['matching_corpus_book_ids']:
            raise ValueError('external transcription comparison changed')
    print('Replayed18state/metadata exclusions and18planted positive corpora.')
    print('Verified71listed occurrences,70unique texts,40shelves and two wiki text comparisons.')
    print('book_positions is not physical coordinates; excluded as a location key.')
    print('Historical recording: catalog only; human check blocked playback,0frames inspected.')
    print('New raw decoders:0. Verified translations:0.')


if __name__ == '__main__':
    main()
