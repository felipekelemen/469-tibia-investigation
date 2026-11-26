#!/usr/bin/env python3
"""Audit bounded E1 source records; never certify meaning from metadata."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


def check_hash(path, expected):
    if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
        raise ValueError('Changed artifact: ' + path)


def audit(with_private=False):
    for manifest in ['data/round34_preretrieval_manifest.json',
                     'data/round34_input_manifest.json']:
        for path, expected in load(manifest)['sha256'].items():
            check_hash(path, expected)
    discovery = load('data/round34_discovery_log.json')
    counts = Counter()
    queries = []
    for call in discovery['calls']:
        kind = call['kind']
        expected = (len(call['queries']) if kind == 'search' else
                    len(call['params'][kind]) if kind in ('open', 'find') else 1)
        if call['operations'] != expected:
            raise ValueError('Miscounted operation')
        counts[kind] += expected
        if kind == 'search':
            queries.extend(call['queries'])
    if len(queries) != len(set(queries)):
        raise ValueError('Duplicated search query')
    counts['conservative_document_capture_budget_charge'] = sum(
        counts[k] for k in ['open', 'find', 'github_get', 'http_get'])
    if dict(counts) != discovery['counts']:
        raise ValueError('Discovery totals disagree')
    protocol = load('data/round34_protocol.json')
    if counts['search'] > protocol['limits']['distinct_search_queries']:
        raise ValueError('Query budget exceeded')
    if counts['conservative_document_capture_budget_charge'] > protocol['limits']['unique_documents_or_captures']:
        raise ValueError('Capture budget exceeded')
    rows = load('data/round34_http.json')
    targets = load('data/round34_http_targets.json')
    if [(r['id'], r['requested_url']) for r in rows] != [(t['id'], t['url']) for t in targets]:
        raise ValueError('HTTP targets disagree')
    if len(rows) != counts['http_get'] or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('HTTP count or identifier mismatch')
    pins = {r['repository_full_name']: r['sha'] for r in load('data/round31_upstream.json')['repositories']}
    upstream = load('data/round34_upstream.json')['reads']
    resolved = [r for r in upstream if r['sha'] is not None]
    if len(upstream) != counts['github_get'] or len(resolved) != 3:
        raise ValueError('Upstream coverage differs')
    if {r['repository']: r['sha'] for r in resolved} != pins:
        raise ValueError('Upstream pin changed')
    observations = load('data/round34_observations.json')
    checks = observations['illustrative_claim_checks']
    outputs = [bytes.fromhex(checks[0]['input']).decode('ascii'),
               ''.join(chr(n + checks[1]['offset']) for n in checks[1]['counts'])]
    if outputs != [c['expected_output'] for c in checks]:
        raise ValueError('Conditional arithmetic mismatch')
    sources = load('data/round34_sources.json')['sources']
    if len({s['id'] for s in sources}) != len(sources):
        raise ValueError('Duplicate source')
    matrix_source = next(s for s in sources if s['id'] == 'torg_matrix')
    if matrix_source['matrix'] != [[3, 1, 6, 1], [1, 2, 1, 1], [1, 1, 3, 1], [4, 6, 1, 1]]:
        raise ValueError('Old table transcription differs')
    private_hashes = 0
    if with_private:
        for call in discovery['calls']:
            if 'file' in call:
                check_hash(call['file'], call['sha256'])
                private_hashes += 1
        for row in rows:
            check_hash(row['body_local_ignored'], row['sha256'])
            private_hashes += 1
        html = (ROOT / 'data/private/round34/http/torg_compendium.body').read_text()
        start = html.index('id="post_3169247"')
        # The table is tied to its post_message container, not JSON-LD duplicates.
        body_start = html.index('id="post_message_3169247"', start)
        next_message = html.find('id="post_message_', body_start + 20)
        body = html[body_start:next_message if next_message >= 0 else None]
        table = '3 1 6 1<br />\n1 2 1 1<br />\n1 1 3 1<br />\n4 6 1 1'
        if body.count(table) != 1:
            raise ValueError('Visible post table absent or duplicated')
    progress = load('data/plan_progress_round34.json')
    if progress['mission_outcome'] != observations['mission_outcome']:
        raise ValueError('Mission status mismatch')
    return {
        'round': 34, 'stage': 'E1', 'counts': dict(counts),
        'http_status_counts': dict(Counter(str(r['http_status']) for r in rows)),
        'resolved_upstream_pins_unchanged': 3,
        'source_context_judgments': len(sources),
        'conditional_arithmetic_outputs': outputs,
        'conditional_outputs_are_translations': False,
        'private_hashes_checked': private_hashes,
        'manual_context_judgments_automatically_proven': False,
        'new_candidate_translation': observations['new_candidate_translation'],
        'mission_outcome': progress['mission_outcome'],
        'scope': 'Offline integrity/budget/arithmetic checks; no automated authorial authentication or semantic discovery.'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-private', action='store_true')
    parser.add_argument('--output', default='results/round34_source_audit.json')
    args = parser.parse_args()
    result = audit(args.with_private)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))
