#!/usr/bin/env python3
"""Extract factual source records from retained captures; do not publish bodies.

--check requires original ignored captures and independently recomputes their
hashes/extraction. The offline round verifier uses the public numeric records.
"""
import argparse
import base64
import collections
import datetime
import hashlib
import json
import pathlib
import re

from historical_matrix_checks import partial_matches, polynomial_determinant, polynomial_rows
from history_source_extract import comment, visible_text
from matrix_experiments import MATRICES, determinant

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/historical_refresh/round14'
BATCHES = ('initial', 'images', 'chronology', 'archive', 'archive_pages', 'archive_domains')
ANCHOR = '2010-08-23'


def encoded(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode()


def source_stamp(selected):
    return {k: v for k, v in selected.items() if k != 'text_local_only'}


def build():
    captures = [row for name in BATCHES for row in json.loads((BASE / (name + '.json')).read_text())]
    byid = {row['id']: row for row in captures}
    if len(captures) != len(byid):
        raise ValueError('duplicate capture IDs')

    def body(ident):
        row = byid[ident]
        content = (ROOT / row['body_local_ignored']).read_bytes()
        if hashlib.sha256(content).hexdigest() != row['sha256'] or len(content) != row['bytes']:
            raise ValueError('original captured bytes changed: ' + ident)
        return content

    # Verify EVERY retained response, including HTTP errors and non-JSON bodies.
    for ident in byid:
        body(ident)
    cdx = json.loads(body('cdx_old_domain_any_order'))
    index = {row[2]: row for row in cdx[1:]}
    archived = []
    for ident, page in [('archive2008_page3', 3), ('archive2008_page47', 47)]:
        payload = body(ident)
        original = f'http://forum.tibia.org.pl:80/showthread.php?t=265100&page={page}'
        row = index[original]
        digest = base64.b32encode(hashlib.sha1(payload).digest()).decode()
        if digest != row[5]:
            raise ValueError('CDX archived-payload digest mismatch')
        text = visible_text(payload.decode('iso8859_2'))
        position = text.index('macierz:')
        numeric_rows = re.findall(r'(?m)^[ \t]*(\d)[ \t]+(\d)[ \t]+(\d)[ \t]+(\d)[ \t]*\r?$', text[position:position + 180])
        matrix = [[int(x) for x in r] for r in numeric_rows]
        if matrix != MATRICES['old']:
            raise ValueError('archived table extraction failed')
        stated_date = re.search(r'\b(\d{2})-(\d{2})-(\d{4}),\s*\d{2}:\d{2}', text)
        if stated_date is None:
            raise ValueError('archived publication-date extraction failed')
        day, month, year = map(int, stated_date.groups())
        publication_date = datetime.date(year, month, day).isoformat()
        archived.append({'capture_id': ident, 'original_url': original, 'replay_url': byid[ident]['requested_url'],
                         'archive_timestamp': row[1], 'post_publication_date_reported': publication_date,
                         'post_author_display_name': 'amadheus', 'same_quoted_first_post': True,
                         'payload_sha1_base32_computed': digest, 'cdx_payload_digest': row[5],
                         'payload_matches_index': True, 'matrix': matrix,
                         'evidence_kind': 'Archived community quotation of a matrix, not a game capture.',
                         'game_observation_date': None})

    appearance = comment(body('torg2009_page46').decode(), 'nie widać już wszystkich czaszek', author='Tibiarz')
    counted = comment(body('torg2010_page58').decode(), 'Policzyłem nową macierz', author='shoq')
    partial = [[int(x) for x in r] for r in re.findall(r'\|\s*(\d)\s+(\d)\s+(\d)\s*\|', counted['text_local_only'])]
    if len(partial) != 3:
        raise ValueError('expected one3x3reported block')
    uncertain = comment(body('torg2010_page59').decode(), 'Macierz wygląda tak:', author='shoq',
                        published_prefix='2010-04-11T11:46')
    rows = re.findall(r'(?m)^([\dx])\s+([\dx])\s+([\dx])\s+([\dx])\r?$', uncertain['text_local_only'])[:4]
    template = [[None if x == 'x' else int(x) for x in r] for r in rows]
    if len(template) != 4 or 'x >= 5' not in uncertain['text_local_only']:
        raise ValueError('uncertain full-table extraction failed')
    correction = comment(body('torg2010_page59').decode(), 'Nie licz', author='shoq', published_prefix='2010-04-11T10:00')
    algebra_claim = comment(body('torg2010_page59').decode(), 'wyznacznik = -18', published_prefix='2010-04-11T11:07')
    later = comment(body('torg2016').decode(), '3161', author='Avarion')
    later_rows = re.findall(r'(?m)^([1-9])\s+([1-9])\s+([1-9])\s+([1-9])\s*$', later['text_local_only'])
    later_matrix = [[int(x) for x in r] for r in later_rows]
    if len(later_matrix) != 4:
        raise ValueError('2016variant extraction failed')
    tutorial = visible_text(body('tutorial2010').decode('iso8859_1'))
    if not re.search(r'Última edição por\s+Commodoro;\s+29-08-2010', tutorial):
        raise ValueError('tutorial edit-date extraction failed')
    archived_notice = visible_text(body('archive2008_thread').decode('iso8859_2'))
    if 'Nie jesteś zalogowany albo nie masz uprawnień' not in archived_notice:
        raise ValueError('archived login response classification changed')

    api_bytes = body('wiki_matrix_history')
    api = json.loads(api_bytes)
    page = next(iter(api['query']['pages'].values()))
    info = page['imageinfo'][0]
    image = body('wiki_matrix_image')
    if hashlib.sha1(image).hexdigest() != info['sha1']:
        raise ValueError('wiki filebytes do not match image-history SHA1')
    images = [{'capture_id': 'wiki_matrix_image', 'source_url': info['url'],
               'file_history_upload_timestamp_reported': info['timestamp'],
               'file_history_sha1': info['sha1'], 'download_sha1_matches_history': True,
               'download_sha256': hashlib.sha256(image).hexdigest(),
               'size': len(image), 'width': info['width'], 'height': info['height'],
               'image_history_entries_returned': len(page['imageinfo']),
               'http_last_modified': byid['wiki_matrix_image']['http_last_modified'],
               'game_capture_timestamp': None, 'visually_inspected': True,
               'full16cell_counts_authenticated': False},
              {'capture_id': 's2ward_matrix_image', 'source_url': byid['s2ward_matrix_image']['requested_url'],
               'http_last_modified': byid['s2ward_matrix_image']['http_last_modified'],
               'download_sha256': byid['s2ward_matrix_image']['sha256'],
               'game_capture_timestamp': None, 'visually_inspected': True,
               'full16cell_counts_authenticated': False}]
    events = {'rename_anchor_date': ANCHOR,
              'anchor_status': 'Date from previously audited community patch/creature sources; no new primary announcement retrieved this round.',
              'archived_old_table': archived,
              'appearance_change_report': {**source_stamp(appearance), 'source_id': 'torg2009_page46',
                                            'scope': 'Reports changed appearance/occlusion after an unspecified update; no numeric full matrix or game-capture date.'},
              'reported_partial_matrix': {**source_stamp(counted), 'source_id': 'torg2010_page58',
                                           'post_id': '4148484', 'matrix': partial,
                                           'pre_rename_archived_body_verified': False},
              'reported_uncertain_full_matrix': {**source_stamp(uncertain), 'source_id': 'torg2010_page59',
                                                 'matrix_template': template, 'source_variable': 'x at row4column2',
                                                 'unknown_cell_1based': [4, 2], 'unknown_lower_bound_reported': 5,
                                                 'full_counts_authenticated': False},
              'reported_count_correction': {**source_stamp(correction), 'source_id': 'torg2010_page59',
                                              'scope': 'Corrects visible5to6, while leaving the lower pile uncertain; no definitive lower6.'},
              'reported_algebra_claim': {**source_stamp(algebra_claim), 'source_id': 'torg2010_page59',
                                         'claim': 'Determinant stays-18when the two questioned entries change.'},
              'later_2016_variant': {**source_stamp(later), 'source_id': 'torg2016', 'matrix': later_matrix,
                                      'attachments_ids': [353136, 353137], 'attachment_image_bodies_obtained': False},
              'tutorial2010': {'source_id': 'tutorial2010', 'publication_date_reported': '2010-04-30',
                                 'last_edit_date_reported': '2010-08-29', 'linked_map_http_status': byid['tutorial2010_map']['http_status'],
                                 'usable_pre_rename_matrix_capture': False},
              'images': images,
              'archive2008_first_response': {'source_id': 'archive2008_thread', 'http_status': 200,
                                              'classification': 'Archived login/permissions notice; no usable matrix content.'},
              'archive_search_complete': False,
              'source_confidence': 'Archived2008table is authenticated as source content. Current2009/2010publication metadata is circumstantial for historical state. No full dated client-frame matrix obtained.'}
    symbolic = [[1, 1, 1, 1], [1, 3, 'x', 1], [1, 1, 4, 1], [4, 'y', 1, 1]]
    polynomial = polynomial_determinant(symbolic)
    sum_polynomial = collections.Counter()
    for value in sum(symbolic, []):
        power = (1, 0) if value == 'x' else (0, 1) if value == 'y' else (0, 0)
        sum_polynomial[power] += 1 if isinstance(value, str) else value
    numeric = []
    for x in range(11):
        for y in range(11):
            concrete = [[x if value == 'x' else y if value == 'y' else value for value in row] for row in symbolic]
            numeric.append({'x': x, 'y': y, 'determinant': determinant(concrete)})
    anchor_date = datetime.date.fromisoformat(ANCHOR)
    dated = {name: (anchor_date - datetime.date.fromisoformat(item['publication_timestamp_reported'][:10])).days
             for name, item in [('appearance_change_report', appearance), ('partial_matrix_report', counted),
                                ('uncertain_matrix_report', uncertain)]}
    analysis = {'provided_matrices': MATRICES, 'reported_partial_matrix': partial,
                'compatibility': {name: partial_matches(matrix, partial)
                                  for name, matrix in {**MATRICES, 'reported2016': later_matrix}.items()},
                'compatibility_scope': 'Exact match under8D4views and4contiguous3x3placements in each4x4candidate. This checks typed source claims, not automatic skull recognition.',
                'symbolic_family': symbolic, 'variable_positions_1based': {'x': [2, 3], 'y': [4, 2]},
                'symbolic_determinant_coefficients': polynomial_rows(polynomial),
                'numeric_independent_crosschecks': numeric,
                'total_skulls_polynomial': polynomial_rows(sum_polynomial),
                'reported_dates_days_before_rename': dated,
                'reported2016_differences_from_provided_new': [
                    {'row': r + 1, 'column': c + 1, 'provided': MATRICES['new'][r][c], 'reported2016': later_matrix[r][c]}
                    for r in range(4) for c in range(4) if MATRICES['new'][r][c] != later_matrix[r][c]],
                'exact_transition_date_identified': False,
                'full_new_counts_authenticated_before_rename': False,
                'rename_coincidence_demonstrated': False,
                'interpretation': 'Pre-rename reported partial layout is contrary circumstantial evidence to coincident replacement; no exact transition date, full count authentication, or ciphertext-English claim.',
                'verified_translations': 0, 'new_plaintext_pairs': 0}
    excerpt = '\n'.join(' '.join(map(str, row)) for row in MATRICES['old']) + '\n'
    return {
        'data/history_round14_http_manifest.json': encoded(captures),
        'data/history_round14_sources.json': encoded(events),
        'data/history_round14_reference/wiki_matrix_history.json': api_bytes,
        'data/history_round14_reference/cdx_old_domain_any_order.json': body('cdx_old_domain_any_order'),
        'data/history_round14_reference/archive2008_matrix_numeric_excerpt.txt': excerpt.encode(),
        'results/history_round14_analysis.json': encoded(analysis)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = build()
    for relative, content in outputs.items():
        path = ROOT / relative
        if args.check:
            if path.read_bytes() != content:
                raise ValueError('source re-extraction differs: ' + relative)
        else:
            if path.exists():
                raise RuntimeError('preserve existing artifact: ' + relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print('Re-extracted original captured source hashes,2archived table payloads, reported dates, image metadata and exact matrix checks.')
    print('Publication, archive, upload, HTTPmodified and game-capture dates kept distinct. No game-capture date established.')


if __name__ == '__main__':
    main()
