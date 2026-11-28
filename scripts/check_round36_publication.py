#!/usr/bin/env python3
"""Verify published replay metadata and historical integrity, not semantics."""
import hashlib
import json
from pathlib import Path
from run_round36 import audit

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT/path).read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check():
    for path, expected in load('data/round36_publication_manifest.json')['sha256'].items():
        assert sha((ROOT/path).read_bytes()) == expected,path
    actual = audit()
    assert actual == load('results/round36_audit.json')
    full = load('results/round36_full_replay.json')
    assert {k:v for k,v in full.items() if k != 'replay'} == actual
    assert all(full['replay'].values())
    clean = load('results/round36_clean_replay.json')
    protocol = load('data/round36_e6_protocol.json')
    assert clean['round'] == 36 and clean['all_commands_passed']
    assert not clean['changed_or_removed_snapshot_files']
    assert [(j['id'],j['command']) for j in clean['jobs']] == [(j['id'],j['command']) for j in protocol['jobs']]
    for job in clean['jobs']:
        assert job['exit_code'] == 0 and not job['timed_out']
        assert sha((ROOT/job['log_path']).read_bytes()) == job['log_sha256']
    correction = load('data/round36_replay_metadata_correction.json')
    assert sha((ROOT/correction['artifact']).read_bytes()) == correction['corrected_sha256']
    original = dict(clean,round=35)
    assert sha((json.dumps(original,indent=2)+'\n').encode()) == correction['original_sha256']
    wrapper = ROOT/'scripts/round36_clean_replay.py'
    assert sha(wrapper.read_bytes()) == correction['wrapper_corrected_sha256']
    assert sha(wrapper.read_bytes().replace(b"'round': 36",b"'round': 35")) == correction['wrapper_original_sha256']
    assert clean['snapshot_sha256']['scripts/round36_clean_replay.py'] == correction['wrapper_original_sha256']
    verification = load('results/round36_verification.json')
    assert verification['snapshot_files'] == clean['snapshot_files']
    assert verification['tests_passed'] == 333
    assert 'Ran 333 tests in' in (ROOT/'results/round36_replay/tests.log').read_text()
    assert (ROOT/'results/round36_replay/tests.log').read_text().rstrip().endswith('OK')
    return dict(round=36,mission_outcome='I_inconclusive',public_audit_passed=True,
                tests_passed=333,complete_censuses=6,conditional_counts_reproduced=22,
                editorial_metadata_correction_verified=True,new_validated_translation=None)


if __name__ == '__main__':
    print(json.dumps(check(),indent=2))
