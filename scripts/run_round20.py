#!/usr/bin/env python3
"""Verify artifacts and replay all targeted decimal-search experiments."""
from target_decimal_experiment import load, sha, run
from chayenne_decimal_search import run as run_chayenne

if __name__=='__main__':
    for p,h in load('data/round20_result_manifest.json')['sha256'].items():
        if sha(p)!=h: raise ValueError('result artifact changed: '+p)
    run(check=True)
    run_chayenne(check=True)
    print('Spaced and unspaced searches replayed: 490 synthetic fixtures, 434 null datasets. No verified English translation.')
