#!/usr/bin/env python3
"""Audit community position fields before using them as possible cipher inputs."""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def source_path(relative):
    return ROOT / 'data/metadata_reference/arturo' / relative.removeprefix('sources/arturo/')


def parse_listing(text):
    rows = []
    shelf, ordinal = None, 0
    current = None
    for line in text.splitlines():
        line = line.strip()
        if re.fullmatch(r'[A-Za-z-]+ Bookcase', line):
            if current:
                rows.append(current)
                current = None
            shelf = line
            ordinal += 1
        else:
            match = re.fullmatch(r'#\s*(\d+)\s+(\d+)\s+\(Book\)\s+([\d \t]+)', line)
            if match:
                if current:
                    rows.append(current)
                current = {'library_number': int(match[1]), 'label': match[2],
                           'shelf_name': shelf, 'shelf_ordinal': ordinal,
                           'digits': re.sub(r'\s', '', match[3])}
            elif current and re.fullmatch(r'[0-9 \t]+', line):
                current['digits'] += re.sub(r'\s', '', line)
    if current:
        rows.append(current)
    return rows


def main():
    paths = ['sources/arturo/data/README.md', 'sources/arturo/data/book_positions.json',
             'sources/arturo/data/bookcase_mapping.json', 'sources/arturo/data/master_text.txt',
             'sources/arturo/scripts/experimental/master_text.py',
             'sources/arturo/docs/archive/Hellgate_Library.txt']
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    bydigits = {b['digits']: b['id'] for b in books}
    text = source_path(paths[-1]).read_text()
    listing = parse_listing(text)
    locations = []
    for row in listing:
        if row['digits'] not in bydigits:
            raise ValueError('listing book not an exact corpus match')
        locations.append({'origin_book_id': bydigits[row['digits']], 'library_number': row['library_number'],
                          'label': row['label'], 'shelf_name': row['shelf_name'], 'shelf_ordinal': row['shelf_ordinal']})
    upstream = json.loads(source_path('sources/arturo/data/bookcase_mapping.json').read_text())
    actual = {(x['library_number'], int(x['origin_book_id']), x['shelf_name']) for x in locations}
    expected = {(x['library_number'], x['books_json_index'], x['bookcase']) for x in upstream}
    if actual != expected:
        raise ValueError('independent listing parse disagrees with upstream mapping')
    positions = json.loads(source_path('sources/arturo/data/book_positions.json').read_text())
    master = source_path('sources/arturo/data/master_text.txt').read_text().strip()
    source = source_path('sources/arturo/scripts/experimental/master_text.py').read_text()
    if 'pos = master.find(books[i])' not in source or 'book_positions.append((i, pos, len(books[i])))' not in source:
        raise ValueError('expected position generator evidence changed')
    manifest = json.loads((ROOT / 'sources/manifest.json').read_text())
    commit = next(r['commit'] for r in manifest if r['name'] == 'arturo')
    out = {'input_sha256': hashlib.sha256((ROOT / 'data/normalized_books.json').read_bytes()).hexdigest(),
           'upstream_commit': commit, 'source_hashes': {str(source_path(p).relative_to(ROOT)): hashlib.sha256(source_path(p).read_bytes()).hexdigest() for p in paths},
           'upstream_relative_paths': paths,
           'position_field': {'rows': len(positions), 'negative_offsets': sum(p < 0 for _, p, _ in positions),
                              'matches_current_master_find': sum(master.find(books[i]['digits']) == p for i, p, _ in positions),
                              'actual_semantics': 'String offsets computed by master.find, with-1for unfound strings; not physical world positions.',
                              'advertised_semantics': 'Upstream dataREADME calls it in-game physical position metadata.',
                              'accepted_as_physical_coordinates': False,
                              'additional_limit': 'Offsets also fail to agree with the current master_text artifact; do not silently realign or treat as coordinates.'},
           'listing': {'occurrences': len(locations), 'unique_corpus_books': len({x['origin_book_id'] for x in locations}),
                       'shelves': len({x['shelf_ordinal'] for x in locations}), 'all_content_matches_exact': True,
                       'classification': 'Community shelf listing ordinal, not authenticated per-book x/y/z coordinates.',
                       'duplicate_occurrences': [x for x in locations if sum(y['origin_book_id'] == x['origin_book_id'] for y in locations) > 1]},
           'limits': ['Exact agreement among repository files does not authenticate a game location or establish a cryptographic use.',
                      'Library ordinals are categorical site-list metadata and may differ across wiki naming schemes.',
                      'Raw length is observable from digits. Code length comes from imported tokenization and is an oracle input for raw-decoder claims.'],
           'implementation_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    (ROOT / 'data/book_location_listing.json').write_text(json.dumps({'source_commit': commit, 'locations': locations,
        'scope': out['listing']['classification']}, indent=2) + '\n')
    (ROOT / 'results/book_metadata_audit.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'positions': out['position_field'], 'listing': out['listing']}, indent=2))


if __name__ == '__main__':
    main()
