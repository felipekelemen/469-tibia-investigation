#!/usr/bin/env python3
"""Offline consistency audit of R31's bounded source investigation.

This validates preserved evidence records, not attribution or semantic truth.
Full HTML retrieval/reinspection is optional and separately reported.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from round31_extract import digit_runs

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def verify_manifest(path):
    for name, expected in load(path)['sha256'].items():
        if sha(name) != expected:
            raise ValueError('Input changed: ' + name)


def audit():
    verify_manifest('data/round31_input_manifest.json')
    protocol = load('data/round31_protocol.json')
    log = load('data/round31_discovery_log.json')
    counts = Counter()
    rejected = []
    for call in log['calls']:
        if not call['executed']:
            rejected.append(call['id'])
            continue
        request = call['request']
        counts['search_queries_total'] += len(request.get('search_query', [])) + len(request.get('system2_search_query', []))
        for action in ['open', 'click', 'find']:
            counts[action] += len(request.get(action, []))
    counts['page_opens_total'] = sum(counts[k] for k in ['open', 'click', 'find'])
    counts['followup_assets_or_api_requests'] = log['http_requests']
    for name, limit in protocol['limits'].items():
        if counts[name] > limit:
            raise ValueError('Source budget exceeded: ' + name)

    http = load('data/round31_http.json')
    targets = load('data/round31_fetch_targets.json')
    if len(http) != counts['followup_assets_or_api_requests']:
        raise ValueError('HTTP request count changed')
    if [(r['id'], r['requested_url']) for r in http] != [(r['id'], r['url']) for r in targets]:
        raise ValueError('HTTP target mismatch')
    sources = load('data/round31_sources.json')['sources']
    source_by_id = {r['id']: r for r in sources}
    if len(source_by_id) != len(sources):
        raise ValueError('Duplicate source id')
    for row in http:
        if source_by_id[row['id']]['url'] != row['requested_url']:
            raise ValueError('Source URL mismatch')

    decisions = load('data/round31_source_decisions.json')
    inspection = load('data/round31_capture_inspection.json')
    reply = decisions['teyrata']['language_reply_complete']
    lexical = re.sub(r'\s*(?::\)|🙂)$', '', reply)
    lexical_hash = hashlib.sha256(lexical.encode()).hexdigest()
    if digit_runs(reply):
        raise ValueError('Unexpected digits in complete Teyrata answer')
    if len(inspection['teyrata']) != 3:
        raise ValueError('Expected three captured representations of one exchange')
    for row in inspection['teyrata']:
        if row['answer_digit_runs'] or row['lexical_reply_sha256'] != lexical_hash:
            raise ValueError('Teyrata representation mismatch')
    if decisions['teyrata']['independent_utterances'] != 1:
        raise ValueError('Copies must not be treated as independent utterances')
    if decisions['knightmare']['excerpt_is_complete_answer']:
        raise ValueError('Short Knightmare excerpt is not the complete answer')
    if inspection['knightmare']['answer_digit_runs']:
        raise ValueError('Unexpected new digits in recorded full answer')

    inventory = {r['id']: r for r in load('data/source_validation_inventory.json')}
    for key in decisions['chayenne']['inventory_ids']:
        row = inspection['chayenne'][key]
        if row['digits'] != inventory[key]['text'] or row['raw_html_occurrences'] < 1:
            raise ValueError('Chayenne inventory mismatch')
    old = load('data/round24_upstream_heads.json')
    upstream = load('data/round31_upstream.json')['repositories']
    # Pins are taken from the frozen R24 records, not inferred from branch names.
    old_shas = {r['repository']: r['remote_head'] for r in old}
    if len(upstream) != 3 or {r['repository_full_name']: r['sha'] for r in upstream} != old_shas:
        raise ValueError('Upstream latest-listed commit comparison differs')
    for name in ['teyrata', 'knightmare', 'chayenne']:
        if decisions[name]['semantic_pair_supplied'] or decisions[name]['original_generation_supplied']:
            raise ValueError('This source audit has no authenticated semantic/production anchor')
    if decisions['mission_disposition'] != 'I' or decisions['candidate_translation'] is not None:
        raise ValueError('Unsupported mission disposition')
    return {
        'round': 31, 'basis': protocol['basis'],
        'audit_scope': 'Offline consistency of source records and manual decisions; not fresh web retrieval or proof of meaning.',
        'operation_counts': dict(counts), 'rejected_calls_not_counted': rejected,
        'source_records': len(sources),
        'direct_http_status_counts': dict(sorted(Counter(str(r.get('http_status', 'network_error')) for r in http).items())),
        'upstream_latest_listed_commits_matching_R24': len(upstream),
        'teyrata_captured_representations': 3, 'teyrata_distinct_interview_exchanges': 1,
        'teyrata_language_answer_digits': [],
        'chayenne_existing_digit_lengths': [len(inspection['chayenne'][key]['digits']) for key in decisions['chayenne']['inventory_ids']],
        'new_attributable_numeric_responses_recovered': 0,
        'conditional_cipher_experiments': 'not_triggered_no_new_digits',
        'new_semantic_pairs': 0, 'original_production_descriptions': 0,
        'candidate_translation': None, 'mission_disposition': 'I',
        'limits': 'The original English2014interview and two attributed creator-quote sources remain unrecovered. Absence in this search is not global absence or a proof of undecipherability.'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true', help='Write once; refuse overwriting a completed result')
    args = parser.parse_args()
    actual = audit()
    path = ROOT / 'results/round31_source_audit.json'
    if args.record:
        with path.open('x') as handle:
            handle.write(json.dumps(actual, ensure_ascii=False, indent=2) + '\n')
    elif actual != load('results/round31_source_audit.json'):
        raise ValueError('Recorded audit mismatch')
    publication = ROOT / 'data/round31_result_manifest.json'
    if publication.exists():
        verify_manifest('data/round31_result_manifest.json')
    print(json.dumps(actual, ensure_ascii=False, indent=2))
