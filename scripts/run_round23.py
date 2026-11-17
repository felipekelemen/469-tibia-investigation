#!/usr/bin/env python3
"""Full offline repeat of round23; source snapshot is included with its license."""
from round23_experiment import load,sha,run
from round23_certificate_audit import build

if __name__=='__main__':
    for p,h in load('data/round23_result_manifest.json')['sha256'].items():
        if sha(p)!=h:raise ValueError('changed result artifact: '+p)
    run(check=True)
    if build()!=load('results/round23_certificate_audit.json'):raise ValueError('certificate mismatch')
    print('Round23 synthetic fixtures, target fits, controls and independent certificates replayed.')
