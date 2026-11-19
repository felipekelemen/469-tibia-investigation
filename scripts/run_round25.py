#!/usr/bin/env python3
"""Verify integrity and repeat the finite structural-family experiment offline."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    for name in ('round25_manifest.json','round25_result_manifest.json'):
        manifest=json.loads((ROOT/'data'/name).read_text())
        for path,expected in manifest['sha256'].items():
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:
                raise ValueError('artifact changed: '+path)
    subprocess.run([sys.executable,str(ROOT/'scripts/round25_name_structure.py'),'--check'],cwd=ROOT,check=True)
    print('Round25: frozen artifacts verified and all structural nulls replayed offline.')
