#!/usr/bin/env python3
"""Summarize conditional parsing; never relabel benchmark prose as Tibia text."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    versions = []
    for version in [1, 2]:
        path = ROOT / f'results/raw_parser_v{version}.json'
        r = json.loads(path.read_text())
        if not r['complete']:
            raise ValueError('qualification incomplete')
        modes = {}
        for mode in r['summaries'][0]['modes']:
            rows = r['trials']
            modes[mode] = {'passed_95percent_cases': sum(s['modes'][mode]['passed'] for s in r['summaries']),
                           'exact_plaintexts': sum(row[mode]['literal'] == row['truth_literal'] for row in rows),
                           'exact_paths': sum(row[mode]['exact_path'] for row in rows),
                           'mean_character_edit_accuracy': sum(row[mode]['character_edit_accuracy'] for row in rows) / len(rows)}
        controls = []
        for label in ['shuffle_codes', 'blocks8_codes']:
            rows = [c for row in r['trials'] for c in row['controls'] if c['mode'] == label]
            controls.append({'mode': label, 'cases': len(rows),
                             'exact_oracle_plaintexts': sum(c['oracle']['literal'] == c['truth_literal'] for c in rows),
                             'exact_oracle_paths': sum(c['oracle']['exact_path'] for c in rows),
                             'oracle_mean_character_edit_accuracy': sum(c['oracle']['character_edit_accuracy'] for c in rows) / len(rows),
                             'wrong_oracle_paths_with_posterior_gt95': sum(not c['oracle']['exact_path'] and c['oracle']['map_path_posterior'] > .95 for c in rows),
                             'wrong_oracle_plaintexts_with_path_posterior_gt95': sum(c['oracle']['literal'] != c['truth_literal'] and c['oracle']['map_path_posterior'] > .95 for c in rows)})
        versions.append({'version': version, 'result_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'positive_cases': len(r['trials']), 'distinct_source_excerpts': 60,
                         'oracle_gate_passes': r['oracle_gate_passes'],
                         'selected_rule_gate_passes': r['selected_rule_gate_passes'],
                         'modes': modes, 'correct_rule_selected': sum(row['true_rule'] == row['selected_rule'] for row in r['trials']),
                         'controls': controls})
    out = {'versions': versions, 'unknown_key_searches': 0, 'verified_469_translations': 0,
           'limits': ['95percent structural recovery is not exact plaintext recovery or semantic validation.',
                      'All keys and code emission probabilities supplied; no game text or new official gloss used.',
                      'Confidence concerns latent paths under an approximate model; controls can preserve some meaningful substrings.']}
    (ROOT / 'results/raw_parser_summary.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
