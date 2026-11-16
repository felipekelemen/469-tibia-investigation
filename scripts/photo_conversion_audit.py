#!/usr/bin/env python3
"""Numeric source audit: no plaintext labels, learned arithmetic or image repair.

The full source HTML/images stay ignored. Public normalized rows are numeric
identifier facts only; no server binary, logs or original file are distributed.
"""
import argparse
import collections
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import random
import re
import time

ROOT = Path(__file__).resolve().parents[1]
SEED = 19737469


def load(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def dump(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def numeric_rows(text):
    result = []
    for line_number, line in enumerate(text.lstrip('\ufeff').splitlines(), 1):
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*([0-9]+)\s+([0-9]+)\s+([0-9]+)\s*', line)
        if not match:
            raise ValueError('non-numeric3column source line: '+str(line_number))
        result.append([line_number, *map(int, match.groups())])
    if not result:
        raise ValueError('empty numeric table')
    return result


class CodeLines(HTMLParser):
    def __init__(self):
        super().__init__(); self.lines = []; self.current = None; self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.current is not None:
                self.depth += 1
            elif 'de1' in dict(attrs).get('class', '').split():
                self.current = []; self.depth = 1

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'div' and self.current is not None:
            self.depth -= 1
            if self.depth == 0:
                self.lines.append(''.join(self.current)); self.current = None


def prepare():
    manifest = load('data/round19_http_manifest.json')
    byid = {r['id']: r for r in manifest}
    for key in ('conversion_raw', 'conversion_html', 'fb_original_mirror', 'fb_oriented_mirror'):
        row = byid[key]
        if row.get('http_status') != 200 or row.get('body_truncated') or row.get('human_check_marker'):
            raise ValueError('unusable source: '+key)
        if sha(row['body_local_ignored']) != row['sha256']:
            raise ValueError('captured bytes changed: '+key)
    raw = (ROOT / byid['conversion_raw']['body_local_ignored']).read_text(encoding='utf-8-sig')
    rows = numeric_rows(raw)
    parsed = CodeLines()
    parsed.feed((ROOT / byid['conversion_html']['body_local_ignored']).read_text())
    html_rows = numeric_rows('\n'.join(parsed.lines))
    if [r[1:] for r in rows] != [r[1:] for r in html_rows]:
        raise ValueError('raw/HTML extraction disagreement')
    dump('data/round19_conversion_numeric.json', {'source_url': byid['conversion_raw']['requested_url'],
        'source_raw_sha256': byid['conversion_raw']['sha256'],
        'columns': ['raw_file_line_1based', 'column1', 'column2', 'column3'], 'rows': rows,
        'raw_html_numeric_agreement': True,
        'scope': 'Normalized public numeric identifier facts; same paste, not two independent sources. Claimed server provenance/function not authenticated by extraction. No original server assets/code/logs redistributed.'})
    print('Numeric source prepared; no photo-pair comparison performed.', flush=True)


def projection(rows, source, target):
    result = collections.defaultdict(set)
    for row in rows:
        result[row[source]].add(row[target])
    return dict(result)


def calibrated_models(rows, anchor):
    return [(a, b) for a in (1, 2, 3) for b in (1, 2, 3) if a != b
            and anchor['y'] in projection(rows, a, b).get(anchor['x'], set())]


def evaluate(mapping, validation):
    records = []
    for pair in validation:
        x, y = int(pair['x_mask']), int(pair['y_mask'])
        candidates = sorted(mapping.get(x, set()))
        records.append({'x': x, 'observed_y': y, 'predicted_values': candidates,
                        'unique_correct': candidates == [y]})
    return records


def mask_match(value, mask):
    text = str(value)
    return len(text) == len(mask) and all(a == '?' or a == b for a, b in zip(mask, text))


def masked_predictions(mapping, rows):
    result = []
    for row in rows:
        if row['role'] in ('visible_validation', 'calibration'):
            continue
        matches = [(x, y) for x, ys in sorted(mapping.items()) for y in sorted(ys)
                   if (row['x_mask'] is None or mask_match(x, row['x_mask'])) and mask_match(y, row['y_mask'])]
        result.append({**row, 'compatible_table_pairs': matches,
                       'status': 'conditional_prediction_only_not_new_transcription',
                       'used_for_visible_validation': False})
    return result


def randomized_rows(rows, model, anchor, rng, cyclic):
    a, b = model
    transformed = [r[:] for r in rows]
    eligible = sorted((i for i, r in enumerate(rows) if r[a] != anchor['x']), key=lambda i: (rows[i][a], i))
    labels = [rows[i][b] for i in eligible]
    if cyclic:
        shift = rng.randrange(1, len(labels))
        labels = labels[shift:]+labels[:shift]
    else:
        rng.shuffle(labels)
    for i, value in zip(eligible, labels):
        transformed[i][b] = value
    return transformed


def build():
    source = load('data/round19_conversion_numeric.json')
    rows = source['rows']
    photo = load('data/round19_photo_transcription.json')
    validation = [r for r in photo['rows'] if r['role'] == 'visible_validation']
    models = calibrated_models(rows, photo['calibration'])
    comparisons = []
    for a, b in models:
        mapping = projection(rows, a, b)
        outcomes = evaluate(mapping, validation)
        witnesses = []
        for pair in outcomes:
            witnesses.append({'x': pair['x'], 'y': pair['observed_y'],
                              'source_rows': [row for row in rows if row[a] == pair['x'] and row[b] == pair['observed_y']]})
        comparisons.append({'source_column': a, 'target_column': b,
                            'visible_validation': outcomes,
                            'unique_correct': sum(r['unique_correct'] for r in outcomes),
                            'source_witnesses': witnesses,
                            'masked_diagnostics': masked_predictions(mapping, photo['rows'])})
    observed = max((r['unique_correct'] for r in comparisons), default=0)
    controls = []
    for kind, cyclic in (('row_output_permutation', False), ('ordered_output_cyclic_shift', True)):
        rng = random.Random(SEED+int(cyclic))
        maxima = []
        for _ in range(999):
            scores = []
            for model in models:
                changed = randomized_rows(rows, model, photo['calibration'], rng, cyclic)
                outcomes = evaluate(projection(changed, *model), validation)
                scores.append(sum(v['unique_correct'] for v in outcomes))
            maxima.append(max(scores, default=0))
        controls.append({'kind': kind, 'replicates': 999, 'max_scores': maxima,
                         'empirical_p': (1+sum(v >= observed for v in maxima))/1000,
                         'scope': 'Conditional on calibrated projections; numeric correspondence only. Not a semantic translation test or independent source-authentication claim.'})
    return {'source_row_count': len(rows), 'calibration': photo['calibration'],
            'calibrated_models': [list(m) for m in models], 'visible_validation_pairs': len(validation),
            'models': comparisons, 'maximum_unique_correct': observed, 'controls': controls,
            'new_verified_translations': 0,
            'scope': 'Frozen simple column projections. No English decoded, no image values completed as facts, no authentication of original2011post or claimed file/game semantics.'}


def freeze():
    if (ROOT / 'data/round19_evidence_manifest.json').exists():
        raise ValueError('already frozen')
    files = ['data/round19_protocol.json', 'data/round19_photo_transcription.json',
             'data/round19_http_manifest.json', 'data/round19_source_targets.json',
             'data/round19_conversion_numeric.json', 'scripts/photo_conversion_audit.py']
    dump('data/round19_evidence_manifest.json', {'stage': 'Before photo-table projection comparison',
                                              'sha256': {p: sha(p) for p in files}})


def main(check=False):
    for path, expected in load('data/round19_evidence_manifest.json')['sha256'].items():
        if sha(path) != expected:
            raise ValueError('frozen input changed: '+path)
    if check:
        for path, expected in load('data/round19_result_manifest.json')['sha256'].items():
            if sha(path) != expected:
                raise ValueError('result artifact changed: '+path)
    start = time.monotonic()
    result = build()
    if check:
        if result != load('results/round19_photo_conversion.json'):
            raise ValueError('full comparison/control replay mismatch')
    else:
        dump('results/round19_photo_conversion.json', result)
        dump('results/round19_execution.json', {'seconds': round(time.monotonic()-start, 3),
            'new_verified_translations': 0, 'control_replicates': 1998})
    print(json.dumps({'calibrated_models': result['calibrated_models'],
                      'visible_validation_pairs': result['visible_validation_pairs'],
                      'maximum_unique_correct': result['maximum_unique_correct'],
                      'replay': check}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.prepare:
        prepare()
    elif args.freeze:
        freeze()
    elif args.run or args.check:
        main(args.check)
    else:
        parser.error('use --prepare, --freeze, --run or --check')
