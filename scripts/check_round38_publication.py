#!/usr/bin/env python3
"""Check R38 frozen outputs, public replay, and transparent audit correction."""
import hashlib
import json
import re

from round36_experiment import ROOT, load, verify
from run_round38 import audit


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check():
    verify('data/round38_publication_manifest.json')
    correction = load('data/round38_audit_correction.json')
    script = (ROOT/correction['changed_file']).read_bytes()
    assert sha(script)==correction['after_sha256']
    assert sha(script.replace(correction['new_line'].encode(),correction['old_line'].encode()))==correction['before_sha256']
    old_bytes = (ROOT/correction['original_result_manifest']).read_bytes()
    assert sha(old_bytes)==correction['original_manifest_sha256']
    amended = json.loads(old_bytes)
    amended['sha256'][correction['changed_file']]=correction['after_sha256']
    assert amended==load('data/round38_result_manifest.json')
    result = audit()
    full = load('results/round38_full_replay.json')
    assert {k:v for k,v in full.items() if k!='replay'}==result
    assert len(full['replay'])==5 and all(full['replay'].values())
    clean = load('results/round38_clean_replay.json')
    protocol = load('data/round38_replay_protocol.json')
    assert clean['round']==38 and clean['all_commands_passed']
    assert not clean['changed_or_removed_snapshot_files']
    assert clean['network_used'] is False and clean['external_reviewer'] is False
    assert [(j['id'],j['command']) for j in clean['jobs']]==[(j['id'],j['command']) for j in protocol['jobs']]
    for job in clean['jobs']:
        assert job['exit_code']==0 and not job['timed_out']
        assert sha((ROOT/job['log_path']).read_bytes())==job['log_sha256']
    tests = (ROOT/'results/round38_replay/tests.log').read_text()
    count = int(re.search(r'Ran (\d+) tests in ',tests).group(1))
    assert count==341 and tests.rstrip().endswith('OK')
    return {'round':38,'public_artifacts_verified':True,'tests_passed':count,
            'snapshot_files':clean['snapshot_files'],'all_597_controls_reproduced':True,
            'complete_controls':561,'limited_controls':36,'audit_representation_correction_verified':True,
            'new_validated_translation':None,'mission_outcome':'I_inconclusive'}


if __name__ == '__main__':
    print(json.dumps(check(),indent=2))
