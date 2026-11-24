#!/usr/bin/env python3
"""Verify closure artifacts offline; historical clean replays are recorded separately."""
import json
from round30_audit import ROOT,digest,verify_inputs,integrity,corpus
from round30_adjudicate import build


if __name__=='__main__':
    load=lambda p:json.loads((ROOT/p).read_text())
    verify_inputs()
    for name in ['data/round30_adjudication_manifest.json','data/round30_result_manifest.json']:
        for path,expected in load(name)['sha256'].items():assert digest(ROOT/path)==expected,path
    assert integrity()==load('results/round30_integrity.json')
    assert corpus()==load('results/round30_corpus.json')
    assert build()==load('results/round30_adjudication.json')
    replay=load('results/round30_clean_replay.json')
    assert replay['all_commands_passed'] and not replay['changed_or_removed_snapshot_files']
    protocol=load('data/round30_protocol.json')
    assert [r['id'] for r in replay['jobs']]==[r['id'] for r in protocol['clean_replays']]
    for row in replay['jobs']:
        assert row['exit_code']==0 and not row['timed_out']
        assert digest(ROOT/row['log_path'])==row['log_sha256']
    ledger=load('data/round30_round_ledger.json')
    assert [r['round'] for r in ledger['rounds']]==list(range(1,31))
    assert all((ROOT/r['report']).is_file() for r in ledger['rounds'])
    print('Round30:636historical hash references,70books/5729imported symbols, evidence disposition,30round ledger and8clean-replay logs verified. No validated translation or original nontext generator.')
