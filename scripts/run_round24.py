#!/usr/bin/env python3
"""Offline replay: verify frozen inputs/results, then recompute numeric audits."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


if __name__ == '__main__':
    for name in ('anagram', 'claim', 'result'):
        manifest = json.loads((ROOT/f'data/round24_{name}_manifest.json').read_text())
        for path, expected in manifest['sha256'].items():
            actual = hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError('artifact changed: '+path)
    for script in ('round24_anagram_audit.py', 'round24_claim_audit.py'):
        subprocess.run([sys.executable, str(ROOT/'scripts'/script), '--check'], cwd=ROOT, check=True)
    print('Round24: frozen artifacts verified; numeric results reproduced without network or upstream database.')
