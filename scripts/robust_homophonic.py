#!/usr/bin/env python3
"""V2 independent search banks; select strictly by training objective.

V1 source, score model and its original qualification stay frozen.
"""
from fast_homophonic import solve as solve_v1
BANK_SEED_STRIDE=1000003

def solve(train_sequences,table,seed=46940000,*,banks=2,restarts=8,steps=100000,num_codes=100,max_temp=12.0,frequency_weight=2.0):
    if type(banks) is not int or banks<1:raise ValueError('banks must be positive integer')
    runs=[]
    for bank in range(banks):
        result=solve_v1(train_sequences,table,seed=seed+BANK_SEED_STRIDE*bank,restarts=restarts,steps=steps,
          num_codes=num_codes,max_temp=max_temp,frequency_weight=frequency_weight)
        runs.append(result)
    # Deterministic ties favor the first bank. No test data, true key or decoded text enters selection.
    chosen=max(range(banks),key=lambda i:runs[i]['objective'])
    best=dict(runs[chosen]);best.update(selected_bank=chosen,banks=runs,total_runtime_seconds=sum(r['runtime_seconds'] for r in runs))
    return best
