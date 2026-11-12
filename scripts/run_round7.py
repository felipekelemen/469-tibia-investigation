#!/usr/bin/env python3
"""Verify round7 artifacts and replay32conditional parses, without key search."""
import hashlib
import json
import math
import pathlib

from copied_homophonic_v3 import build_model
from raw_digit_decoder import CharacterLanguage, decode as decode_v1
from raw_parser_benchmark import fixture as fixture_v1, passes, verify as verify_v1
from raw_parser_benchmark_v2 import fixture as fixture_v2, verify as verify_v2
from raw_parser_long_context import LongContextLanguage, decode as decode_v2

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/round7_evidence_manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise ValueError('round7 evidence changed: ' + relative)
    replayed = 0
    for version, factory, decoder, verify in [(1, fixture_v1, decode_v1, verify_v1), (2, fixture_v2, decode_v2, verify_v2)]:
        result = json.loads((ROOT / f'results/raw_parser_v{version}.json').read_text())
        p = json.loads((ROOT / f'data/raw_parser_v{version}_protocol.json').read_text())
        verify(p)
        if hashlib.sha256((ROOT / f'data/raw_parser_v{version}_protocol.json').read_bytes()).hexdigest() != result['protocol_sha256']:
            raise ValueError('protocol fingerprint changed')
        if not result['complete'] or len(result['trials']) != 240 or len(result['summaries']) != 8:
            raise ValueError('incomplete qualification')
        language = CharacterLanguage(build_model()[0]) if version == 1 else LongContextLanguage(**p['selected_model'])
        for summary in result['summaries']:
            rows = [r for r in result['trials'] if r['length'] == summary['length'] and r['true_rule'] == summary['rule']]
            if len(rows) != 30 or any(len(r['controls']) != 2 for r in rows):
                raise ValueError('missing cases/controls')
            for mode, recorded in summary['modes'].items():
                if sum(passes(r[mode], p) for r in rows) != recorded['passed']:
                    raise ValueError('qualification count changed')
            for i in [0, 15]:  # both new authors, each length and rule
                row = next(r for r in rows if r['fixture'] == i)
                f = factory(i, row['length'])
                decoded = decoder(row['evaluation_raw'], f['key'], f['probabilities'], language, row['true_rule'])
                if decoded['literal'] != row['oracle']['literal']:
                    raise ValueError('replay literal changed')
                if not math.isclose(decoded['log_evidence'], row['oracle']['log_evidence'], abs_tol=1e-8):
                    raise ValueError('replay evidence changed')
                replayed += 1
        print('V' + str(version), 'oracle gate:', result['oracle_gate_passes'],
              'selected-rule gate:', result['selected_rule_gate_passes'])
    print('Verified480positive qualification cases and960paired order controls.')
    print('Replayed', replayed, 'known-key raw parses; no hidden boundary/count input.')
    print('Unknown-key searches:0. Verified469translations:0.')


if __name__ == '__main__':
    main()
