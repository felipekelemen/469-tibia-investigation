#!/usr/bin/env python3
"""Check consistency of the v3 closure dossier; not semantic authentication."""
import hashlib
import json
from pathlib import Path
import re
from run_round35 import audit

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


def check():
    for path, expected in load('data/round35_closure_manifest.json')['sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    assert audit() == load('results/round35_audit.json')
    replay = load('results/round35_clean_replay.json')
    protocol = load('data/round35_e6_protocol.json')
    assert replay['all_commands_passed'] and not replay['changed_or_removed_snapshot_files']
    assert [(j['id'], j['command']) for j in replay['jobs']] == [(j['id'], j['command']) for j in protocol['jobs']]
    for job in replay['jobs']:
        assert job['exit_code'] == 0 and not job['timed_out']
        path = ROOT / job['log_path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == job['log_sha256']
    text = (ROOT / 'results/round35_replay/tests.log').read_text()
    tests = int(re.search(r'Ran (\d+) tests? in', text).group(1))
    assert text.rstrip().endswith('OK')
    full = load('results/round35_full_replay.json')
    assert {k:v for k,v in full.items() if k != 'full_replay'} == load('results/round35_audit.json')
    assert full['full_replay']['scientific_outputs_identical']
    assert full['full_replay']['qualification_rows_replayed'] == 480
    dossier = load('data/mission_conclusion_v3.json')
    progress = load('data/plan_progress_round35.json')
    assert dossier['stages'] == progress['stages']
    assert dossier['cycle_closed'] and dossier['mission_outcome'] == 'I_inconclusive'
    assert not dossier['translation_validated'] and not dossier['original_nontextual_process_authenticated']
    assert not dossier['universal_impossibility_proved']
    assert all(row['outcome'] == 'I' and row['validated_translation'] is None for row in dossier['sources'])
    original = load('data/round30_evidence_catalog.json')['priority_sources']
    assert [(r['id'],r['input_literal']) for r in dossier['sources'][:4]] == [(r['id'],r['input_literal']) for r in original]
    for row in dossier['sources']:
        assert all((ROOT / p).is_file() for p in row['evidence'])
    assert dossier['verification']['tests_passed'] == tests
    return {'mission_outcome': dossier['mission_outcome'], 'cycle_closed': True,
            'stages_disposed': len(dossier['stages']), 'sources_disposed': len(dossier['sources']),
            'clean_replay_jobs_passed': len(replay['jobs']), 'tests_passed': tests,
            'scope': 'Consistency, integrity and numerical reproduction; source authenticity and semantic conclusions remain explicitly adjudicated judgments.'}


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2))
