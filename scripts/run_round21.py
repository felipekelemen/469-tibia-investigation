#!/usr/bin/env python3
"""Verify round21 artifacts and fully replay the accelerated equivalent search."""
from target_decimal_experiment import load,sha
from periodic_decimal_vectorized import vectorized_run
from periodic_result_summary import build

if __name__=='__main__':
    for p,h in load('data/round21_result_manifest.json')['sha256'].items():
        if sha(p)!=h:raise ValueError('changed result artifact: '+p)
    vectorized_run(check=True)
    if build()!=load('data/round21_summary.json'):raise ValueError('summary mismatch')
    print('Full model, control and key-union summary replay verified.')
