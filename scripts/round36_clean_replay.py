#!/usr/bin/env python3
"""Run frozen E6 checks in a public-only copy, preserving logs and hashes."""
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    protocol = json.loads((ROOT / 'data/round36_e6_protocol.json').read_text())
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')[:-1]
    added = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')[:-1]
    names = sorted(set(tracked + [p for p in added if 'round36' in p]))
    assert all(not p.startswith('data/private/') and 'round36_reference/language_model.txt' not in p for p in names)
    inputs = {p: sha(ROOT / p) for p in names}
    logs = ROOT / 'results/round36_replay'
    logs.mkdir(exist_ok=True)
    jobs = []
    def memory_cap():
        limit = protocol['max_address_space_per_process_bytes']
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='469-r36-public-') as name:
        snapshot = Path(name)
        for path in names:
            target = snapshot / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        for job in protocol['jobs']:
            start = time.monotonic()
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            before = usage.ru_utime + usage.ru_stime
            log = logs / (job['id'] + '.log')
            timed_out = False
            with log.open('w') as stream:
                try:
                    completed = subprocess.run(job['command'], cwd=snapshot, stdout=stream,
                                               stderr=subprocess.STDOUT, env=environment,
                                               preexec_fn=memory_cap,
                                               timeout=protocol['timeout_seconds_per_job'])
                    code = completed.returncode
                except subprocess.TimeoutExpired:
                    code, timed_out = None, True
            usage = resource.getrusage(resource.RUSAGE_CHILDREN)
            record = dict(job, exit_code=code, timed_out=timed_out,
                          wall_seconds=time.monotonic() - start,
                          child_cpu_seconds=usage.ru_utime + usage.ru_stime - before,
                          log_path=str(log.relative_to(ROOT)), log_sha256=sha(log))
            jobs.append(record)
            print(json.dumps(record), flush=True)
            if code != 0:
                break
        changed = [p for p, expected in inputs.items() if not (snapshot / p).is_file() or sha(snapshot / p) != expected]
        if Path('/tmp/469-e6-round36-replay.json').exists() and any(j['id'] == 'round36_full' and j['exit_code'] == 0 for j in jobs):
            shutil.copyfile('/tmp/469-e6-round36-replay.json', ROOT / 'results/round36_full_replay.json')
    result = {'round': 36, 'stage': 'E6', 'snapshot_files': len(inputs),
              'snapshot_sha256': inputs, 'jobs': jobs, 'changed_or_removed_snapshot_files': changed,
              'all_commands_passed': len(jobs) == len(protocol['jobs']) and all(j['exit_code'] == 0 for j in jobs) and not changed,
              'external_reviewer': False, 'network_used': False,
              'scope': 'Clean file snapshot on the same runtime; no claim of independent institution or clean operating system.'}
    (ROOT / 'results/round36_clean_replay.json').write_text(json.dumps(result,indent=2)+'\n')
    assert result['all_commands_passed'], result


if __name__ == '__main__':
    run()
