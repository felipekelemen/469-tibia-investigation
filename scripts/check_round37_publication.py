#!/usr/bin/env python3
"""Verify R37 public replay records and frozen artifacts, not source truth."""
import hashlib
import json
import re
from round36_experiment import ROOT, load, verify
from run_round37 import audit


def check():
    verify('data/round37_publication_manifest.json')
    result = audit()
    clean = load('results/round37_clean_replay.json')
    protocol = load('data/round37_replay_protocol.json')
    assert clean['round'] == 37 and clean['all_commands_passed']
    assert not clean['changed_or_removed_snapshot_files']
    assert clean['network_used'] is False and clean['external_reviewer'] is False
    assert [(r['id'],r['command']) for r in clean['jobs']] == [(r['id'],r['command']) for r in protocol['jobs']]
    for job in clean['jobs']:
        assert job['exit_code'] == 0 and not job['timed_out']
        data = (ROOT/job['log_path']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == job['log_sha256']
    replay = json.loads((ROOT/'results/round37_replay/round37_full.log').read_text())
    assert replay == dict(result, conditional_counts_repeated_now=True)
    testlog = (ROOT/'results/round37_replay/tests.log').read_text()
    number = int(re.search(r'Ran (\d+) tests in ',testlog).group(1))
    assert number == 337 and testlog.rstrip().endswith('OK')
    return {'round':37, 'public_artifacts_verified':True, 'tests_passed':number,
            'public_snapshot_files':clean['snapshot_files'], 'fresh_conditional_counts_reproduced':3,
            'new_validated_translation':None, 'mission_outcome':'I_inconclusive'}


if __name__ == '__main__':
    print(json.dumps(check(),indent=2))
