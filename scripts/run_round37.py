#!/usr/bin/env python3
"""Offline audit; --full also repeats the three compiled conditional counts."""
import argparse
import hashlib
import json
from pathlib import Path

from round36_experiment import ROOT, load, verify
from round37_experiment import article_check, calculate
from round37_controls import calculate as control_counts


def audit(full=False):
    for manifest in ['data/round37_input_manifest.json','data/round37_execution_manifest.json',
                     'data/round37_controls_manifest.json','data/round37_result_manifest.json']:
        verify(manifest)
    claims = load('data/round37_claims.json')
    result = load('results/round37_claim_checks.json')
    assert article_check(claims) == result['article160']
    controls = control_counts()
    assert controls == load('results/round37_controls.json')
    for row, conditioned in zip(result['anchors']['claims'], controls['cases'][0]['claims']):
        assert row['word'] == conditioned['word'] and row['raw'] == conditioned['control_raw']
        assert row['marginal_count'] == conditioned['conditional_keys'] == int(row['fresh_count']['count'])
        assert row['counts_match'] and row['fresh_count']['complete']
    discovery = load('data/round37_discovery_log.json')
    limits = load('data/round37_protocol.json')['limits']
    counts = discovery['counts']
    assert counts['search'] == discovery['distinct_queries'] == len(set(discovery['queries'])) == 12
    assert counts['search'] <= limits['distinct_search_queries']
    assert counts['web_open_click_find'] <= limits['web_open_click_find_operations']
    assert counts['direct_http'] == len(discovery['http']) <= limits['direct_HTTP_captures']
    assert discovery['queries'][:8] == load('data/round37_protocol.json')['initial_queries']
    assert not discovery['prior_query_inventory']['literal_repeats']
    table = load('data/round37_article_extract.json')
    assert table['relevant_pair_map'] == claims['article160']['relevant_pair_map']
    private_capture = ROOT/'data/private/round37/find01.json'
    if private_capture.exists():
        from round37_sources import collect, article_extract
        assert collect() == discovery and article_extract() == table
    sources = load('data/round37_sources.json')
    assert sources['independent_author_authenticated_numeric_English_pairs'] == 0
    assert sources['accepted_new_translators'] == sources['new_original_nontextual_processes'] == 0
    if full:
        assert calculate() == result, 'Fresh results differ'
    return {'round':37, 'search_queries':counts['search'], 'web_page_operations':counts['web_open_click_find'],
            'http_attempts':counts['direct_http'], 'claims_counted':len(result['anchors']['claims']),
            'previously_exposed_shuffle_controls':len(controls['cases'])-1,
            'article_expansion_enumeration_reproduced':True,
            'conditional_counts_repeated_now':full, 'scientific_outputs_match':True,
            'source_classifications':'Recorded judgments, not authenticated by hash verification',
            'new_validated_translation':None, 'mission_outcome':'I_inconclusive'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    print(json.dumps(audit(args.full),indent=2))
