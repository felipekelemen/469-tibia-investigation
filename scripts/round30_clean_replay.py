#!/usr/bin/env python3
"""Replay selected historical checks from a committed, cache-free Git archive."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import signal
import subprocess
import tarfile
import tempfile
import time
from round30_audit import ROOT, verify_inputs


def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run(commit):
    verify_inputs()
    protocol=json.loads((ROOT/'data/round30_protocol.json').read_text())
    full=subprocess.check_output(['git','rev-parse',commit],cwd=ROOT,text=True).strip()
    temp=Path(tempfile.mkdtemp(prefix='469-round30-'))
    archive=temp/'snapshot.tar';snapshot=temp/'snapshot';snapshot.mkdir()
    subprocess.run(['git','archive','--format=tar','--output='+str(archive),full],cwd=ROOT,check=True)
    with tarfile.open(archive) as stream:stream.extractall(snapshot,filter='data')
    assert not (snapshot/'sources/s2ward').exists()
    verify_inputs(snapshot)
    before=hashes(snapshot)
    output=ROOT/'results/round30_replay';output.mkdir(exist_ok=True)
    rows=[]
    for job in protocol['clean_replays']:
        identifier=job['id'];runtime=temp/'runtime'/identifier;runtime.mkdir(parents=True)
        env=dict(os.environ,TMPDIR=str(runtime),PYTHONDONTWRITEBYTECODE='1',PYTHONPATH='',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        logfile=output/(identifier+'.log');start=time.monotonic();timeout=False
        print('Starting clean replay:',identifier,flush=True)
        with logfile.open('w') as log:
            process=subprocess.Popen(job['command'],cwd=snapshot,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=process.wait(timeout=1800)
            except subprocess.TimeoutExpired:
                timeout=True;os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                code=process.returncode
        row={'id':identifier,'command':job['command'],'scope':job['scope'],'exit_code':code,
             'timed_out':timeout,'seconds':round(time.monotonic()-start,3),
             'log_path':str(logfile.relative_to(ROOT)),'log_sha256':hashlib.sha256(logfile.read_bytes()).hexdigest(),
             'fresh_runtime_files':hashes(runtime)}
        rows.append(row)
        (temp/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
        print('Finished',identifier,'exit',code,'seconds',row['seconds'],flush=True)
    after=hashes(snapshot)
    changed=[p for p,h in before.items() if after.get(p)!=h]
    created=sorted(set(after)-set(before))
    result={'input_commit':full,'snapshot_path':str(snapshot),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'python':platform.python_version(),'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
        'tracked_snapshot_files':len(before),'changed_or_removed_snapshot_files':changed,'created_snapshot_files':created,
        'all_commands_passed':all(r['exit_code']==0 and not r['timed_out'] for r in rows),'jobs':rows,
        'scope':'Same-environment internal replay from a fresh committed archive; no third-party replication or claim that all29rounds were recomputed.',
        'omitted_original_http_bodies':'Ignored HTML/source captures are not included; inspect round26log for explicit metadata-only source verification.'}
    path=ROOT/'results/round30_clean_replay.json'
    if path.exists():raise ValueError('Refuse to replace completed replay')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print('Clean replay complete; all passed:',result['all_commands_passed'],'changed tracked files:',changed,flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--commit',required=True);args=parser.parse_args()
    run(args.commit)
