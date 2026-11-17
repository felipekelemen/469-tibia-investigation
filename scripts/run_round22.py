#!/usr/bin/env python3
"""Full offline recompile/replay, exact coverage and independent candidate review."""
from target_decimal_experiment import load,sha
from round22_exhaustive_experiment import run
from round22_summary import build

if __name__=='__main__':
    for p,h in load('data/round22_result_manifest.json')['sha256'].items():
        if sha(p)!=h:raise ValueError('changed result artifact: '+p)
    run(check=True)
    if build()!=load('data/round22_summary.json'):raise ValueError('summary mismatch')
    print('All828finite-key fits and ambiguity/coverage certificates replayed.')
