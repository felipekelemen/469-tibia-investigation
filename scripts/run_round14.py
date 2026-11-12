#!/usr/bin/env python3
"""Offline source-record checks, matrix compatibility and symbolic replay.

When original ignored captures exist, also re-extract their bytes. In an
archive-only checkout, do not pretend metadata checks re-read original HTML.
"""
import datetime
import collections
import hashlib
import json

from historical_matrix_checks import partial_matches, polynomial_determinant, polynomial_rows
from history_round14_build import BASE, BATCHES, ROOT, build
from matrix_experiments import MATRICES, determinant


def main():
    manifest = json.loads((ROOT / 'data/round14_evidence_manifest.json').read_text())
    for path, expected in manifest['sha256'].items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('round14 artifact changed: ' + path)
    sources = json.loads((ROOT / 'data/history_round14_sources.json').read_text())
    http = json.loads((ROOT / 'data/history_round14_http_manifest.json').read_text())
    analysis = json.loads((ROOT / 'results/history_round14_analysis.json').read_text())
    byid = {row['id']: row for row in http}
    if len(http) != 27 or len(byid) != 27 or any(row.get('human_check_marker') for row in http):
        raise ValueError('capture scope changed')
    cdx = json.loads((ROOT / 'data/history_round14_reference/cdx_old_domain_any_order.json').read_text())
    records = {row[2]: row for row in cdx[1:]}
    for row in sources['archived_old_table']:
        index = records[row['original_url']]
        if row['archive_timestamp'] != index[1] or row['payload_sha1_base32_computed'] != index[5]:
            raise ValueError('recorded archival digest/timestamp binding changed')
        if row['matrix'] != MATRICES['old'] or row['game_observation_date'] is not None:
            raise ValueError('archived table confused with game capture')
    if len(sources['archived_old_table']) != 2:
        raise ValueError('missing archived table attestations')
    pattern = sources['reported_partial_matrix']['matrix']
    candidate = {'old': MATRICES['old'], 'new': MATRICES['new'],
                 'reported2016': sources['later_2016_variant']['matrix']}
    compat = {name: partial_matches(matrix, pattern) for name, matrix in candidate.items()}
    if compat != analysis['compatibility'] or compat['old'] or not compat['new'] or not compat['reported2016']:
        raise ValueError('partial layout compatibility changed')
    if sources['reported_uncertain_full_matrix']['matrix_template'][3][1] is not None:
        raise ValueError('unknown lower count filled in silently')
    if sources['reported_uncertain_full_matrix']['full_counts_authenticated']:
        raise ValueError('typed claim promoted to full game counts')
    polynomial = polynomial_determinant(analysis['symbolic_family'])
    if polynomial_rows(polynomial) != analysis['symbolic_determinant_coefficients'] or polynomial != {(0, 0): -18}:
        raise ValueError('symbolic determinant identity changed')
    total = collections.Counter()
    for value in sum(analysis['symbolic_family'], []):
        power = (1, 0) if value == 'x' else (0, 1) if value == 'y' else (0, 0)
        total[power] += 1 if isinstance(value, str) else value
    if polynomial_rows(total) != analysis['total_skulls_polynomial']:
        raise ValueError('skull total polynomial changed')
    if len(analysis['numeric_independent_crosschecks']) != 121:
        raise ValueError('missing numeric algebra checks')
    for row in analysis['numeric_independent_crosschecks']:
        numeric = [[row['x'] if c == 'x' else row['y'] if c == 'y' else c for c in r]
                   for r in analysis['symbolic_family']]
        if determinant(numeric) != row['determinant'] or row['determinant'] != -18:
            raise ValueError('independent cofactor determinant disagrees')
    for key, event in [('appearance_change_report', sources['appearance_change_report']),
                       ('partial_matrix_report', sources['reported_partial_matrix']),
                       ('uncertain_matrix_report', sources['reported_uncertain_full_matrix'])]:
        days = (datetime.date.fromisoformat(sources['rename_anchor_date'])
                - datetime.date.fromisoformat(event['publication_timestamp_reported'][:10])).days
        if days != analysis['reported_dates_days_before_rename'][key] or event['game_capture_timestamp'] is not None:
            raise ValueError('date roles/differences changed')
    api = json.loads((ROOT / 'data/history_round14_reference/wiki_matrix_history.json').read_text())
    info = next(iter(api['query']['pages'].values()))['imageinfo'][0]
    first_image = sources['images'][0]
    if (info['sha1'], info['timestamp']) != (first_image['file_history_sha1'], first_image['file_history_upload_timestamp_reported']):
        raise ValueError('file-history metadata changed')
    if any(image['game_capture_timestamp'] is not None or image['full16cell_counts_authenticated'] for image in sources['images']):
        raise ValueError('image upload/HTTP date promoted to dated full game matrix')
    if sources['archive2008_first_response']['http_status'] != 200 or 'login' not in sources['archive2008_first_response']['classification'].lower():
        raise ValueError('HTTP200notice misclassified as source content')
    if any(analysis[key] for key in ('exact_transition_date_identified', 'full_new_counts_authenticated_before_rename',
                                     'rename_coincidence_demonstrated', 'verified_translations', 'new_plaintext_pairs')):
        raise ValueError('unexpected historical/semantic promotion')
    if all((BASE / (name + '.json')).exists() for name in BATCHES):
        for relative, content in build().items():
            if (ROOT / relative).read_bytes() != content:
                raise ValueError('original-byte extraction changed: ' + relative)
        print('Original local captures also rehashed/re-extracted, including2CDXmatched archived payloads and imageSHA1.')
    else:
        print('Offline metadata/numeric replay only; original ignoredHTML/images are not redistributed or re-read here.')
    print('Archived old table:documented in2008, not authenticated as a dated client-frame count.')
    print('Current reported partial layout:2010-04-10,135days before rename; no pre-rename archived body for this reply established.')
    print('Old matrix:0compatible3x3placements. New and2016variant:compatible; lower count remains unknown.')
    print('Symbolic determinant:-18for allx,y;121independent numeric cofactor checks pass.')
    print('Exact matrix transition date:unknown. Rename coincidence:not demonstrated. Verified translations:0.')


if __name__ == '__main__':
    main()
