#!/usr/bin/env python3
"""Offline archive/source-chain checks, distinct from optional private HTML replay."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from round32_archive import unwrap_archive, verify_capture_identity

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


def verify_manifest(path):
    for name, expected in load(path)['sha256'].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Artifact changed: ' + name)


def audit():
    verify_manifest('data/round32_input_manifest.json')
    protocol = load('data/round32_protocol.json')
    discovery = load('data/round32_discovery_log.json')
    counts = Counter()
    for call in discovery['calls']:
        if not call['executed']:
            continue
        request = call['request']
        counts['search_queries'] += len(request.get('system2_search_query', []))
        counts['web_page_operations'] += sum(len(request.get(a, [])) for a in ['open', 'click', 'find'])
    rows = load('data/round32_http.json')
    by_id = {r['id']: r for r in rows}
    if len(by_id) != len(rows):
        raise ValueError('Duplicate HTTP identifiers')
    targets = []
    for name in discovery['target_batches']:
        targets.extend(load('data/round32_targets_' + name + '.json'))
    if [(r['id'], r['requested_url']) for r in rows] != [(r['id'], r['url']) for r in targets]:
        raise ValueError('HTTP requests do not match target batches')
    counts['targeted_http_gets'] = len(rows)
    for field, cap in protocol['limits'].items():
        if counts[field] > cap:
            raise ValueError('Source budget exceeded: ' + field)

    indices = load('data/round32_archive_index.json')
    for name, record in indices.items():
        if by_id[name]['http_status'] != 200 or record['body_sha256'] != by_id[name]['sha256']:
            raise ValueError('Index provenance mismatch')
    trace = load('data/round32_source_trace.json')
    inspection = load('data/round32_capture_inspection.json')
    primary = inspection['primary_exchanges']
    pair_results = []
    for chain in trace['chains']:
        available = indices[chain['availability']]['parsed_json']['archived_snapshots']['closest']
        if not available['available'] or available['status'] != '200':
            raise ValueError('Archive index does not advertise an available snapshot')
        cdx = indices[chain['cdx']]['parsed_json']
        records = [dict(zip(cdx[0], values)) for values in cdx[1:]]
        if len(chain['snapshots']) != 2 or chain['independent_interviews'] != 1:
            raise ValueError('Two date captures must remain one interview lineage')
        expected_first = unwrap_archive(available['url'])
        first = primary[chain['snapshots'][0]]
        if expected_first != {'original_url':first['original_url'], 'capture_chain':[first['capture_timestamp']]}:
            raise ValueError('Availability result differs from first recovered snapshot')
        hashes = []
        for name in chain['snapshots']:
            record = primary[name]
            verify_capture_identity(by_id[name], record['original_url'], record['capture_timestamp'])
            if not any(r['timestamp'] == record['capture_timestamp'] and r['original'] == record['original_url'] and r['statuscode'] == '200' for r in records):
                raise ValueError('Recovered snapshot absent from preserved CDX index')
            if record['answer_digit_runs']:
                raise ValueError('Unexpected new numeric answer')
            hashes.append(record['answer_sha256'])
        if len(set(hashes)) != 1:
            raise ValueError('Relevant answer differs between snapshots')
        if 'short_complete_answer' in chain:
            if hashlib.sha256(chain['short_complete_answer'].encode()).hexdigest() != hashes[0]:
                raise ValueError('Complete brief answer does not match extracted answer hash')
        pair_results.append({'lineage':chain['lineage'], 'captures':2, 'answer_hashes_equal':True, 'independent_interviews':1})
    if len({primary[x]['obvious_context_sha256'] for x in ['bdt_20180504','bdt_20190722']}) != 1:
        raise ValueError('BDT contextual passage changed')
    scans = inspection['literal_term_scans']
    if len(scans) != 8 or any(r['literal_dictionary_term_matches'] for r in scans):
        raise ValueError('Recorded literal-term scan result differs')
    if trace['dictionary']['original_attribution_recovered']:
        raise ValueError('Unresolved attribution must remain unresolved')
    if trace['new_numeric_or_plaintext_pairs'] or trace['new_mechanism_specified'] or trace['new_original_nontext_process']:
        raise ValueError('This round did not recover a semantic/production mechanism')
    if trace['mission_disposition'] != 'I' or trace['candidate_translation'] is not None:
        raise ValueError('Unsupported mission disposition')
    return {
        'round':32, 'basis':protocol['basis'], 'operations':dict(counts),
        'http_status_counts':dict(sorted(Counter(str(r.get('http_status','network_error')) for r in rows).items())),
        'http200_without_requested_content':['dictionary_reddit'],
        'recovered_original_interview_lineages':2, 'verified_primary_capture_bodies':4,
        'pairs':pair_results, 'bdt_future_civilisation_context_same_in_both_captures':True,
        'dictionary_visible_page_scans':8, 'dictionary_term_hits':0,
        'dictionary_creator_attribution':'unresolved_not_disproved',
        'new_attributable_numeric_answers':0, 'new_semantic_pairs':0,
        'cipher_experiments':'not_triggered_no_specific_mechanism_or_new_pairs',
        'candidate_translation':None, 'mission_disposition':'I',
        'scope':'Offline consistency of public records. Actual HTML extraction was performed separately on private preserved bodies. Source interpretation is explicit manual analysis; matching hashes do not prove a decoder or authorial intent.'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    result = audit()
    path = ROOT / 'results/round32_source_audit.json'
    if args.record:
        with path.open('x') as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    elif result != load('results/round32_source_audit.json'):
        raise ValueError('Recorded audit differs')
    if (ROOT / 'data/round32_result_manifest.json').exists():
        verify_manifest('data/round32_result_manifest.json')
    print(json.dumps(result, ensure_ascii=False, indent=2))
