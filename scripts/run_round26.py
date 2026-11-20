#!/usr/bin/env python3
"""Offline mathematical replay; original source-body checks only when present."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    for name in ('round26_experiment_manifest.json','round26_result_manifest.json'):
        for path,expected in json.loads((ROOT/'data'/name).read_text())['sha256'].items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:raise ValueError('changed artifact: '+path)
    for row in json.loads((ROOT/'data/round26_prior_catalog.json').read_text())['prior_families']:
        if hashlib.sha256((ROOT/row['artifact']).read_bytes()).hexdigest()!=row['artifact_sha256']:raise ValueError('changed prior result: '+row['artifact'])
    subprocess.run([sys.executable,str(ROOT/'scripts/round26_matrix_consistency.py'),'--check'],cwd=ROOT,check=True)
    captures=[r for p in ROOT.glob('data/round26_http_*.json') for r in json.loads(p.read_text())]
    if captures and all((ROOT/r.get('body_local_ignored','missing')).is_file() for r in captures):
        from round26_source_audit import run
        assert run()==json.loads((ROOT/'results/round26_sources.json').read_text())
        print('Original local HTTP bytes and extracted facts checked.')
    else:print('Source-body replay skipped: HTTP bodies not distributed. Metadata integrity verified only.')
    print('Round26 matrix consistency, synthetic controls and result integrity replayed.')
