#!/usr/bin/env python3
"""Equivalent lexical DP: decrypt each reachable suffix once, not each edge.

The frozen reference search/model code stays unchanged. Only repeated work in
Model.segment is removed; order, counts, samples and search budgets are retained.
"""
import argparse
from periodic_decimal_solver import Model
from periodic_decimal_experiment import run
from target_decimal_experiment import ROOT,load,dump,sha


def fast_segment(self,raw,key,offset=0,previous=0):
    counts=[0]*(len(raw)+1);counts[0]=1
    samples=[None]*(len(raw)+1);samples[0]=[]
    stream=self.decrypt_digits(raw,key,offset,previous) if raw and self.reset=='stream' else None
    for i in range(len(raw)):
        if not counts[i]:continue
        suffix=stream[i:] if stream is not None else self.decrypt_digits(raw[i:],key)
        for n in self.book.lengths:
            if i+n>len(raw):break
            candidates=self.book.reverse.get(suffix[:n],[])
            if candidates:
                counts[i+n]+=counts[i]*len(candidates)
                if samples[i+n] is None:samples[i+n]=samples[i]+[candidates[0]]
    return {'word_path_count':counts[-1],'unique_words':samples[-1] if counts[-1]==1 else None}


def freeze():
    if (ROOT/'data/round21_optimization_manifest.json').exists():raise ValueError('already frozen')
    paths=['scripts/periodic_decimal_fast.py','tests/test_periodic_fast_equivalence.py','data/round21_evidence_manifest.json']
    dump('data/round21_optimization_manifest.json',{'reason':'Performance-only suffix-decryption DP replacing repeated edge decryption. Original reference code retained. Initial reference full batch interrupted during Chayenne before final results/nulls; no new model or larger budget.',
                                                  'sha256':{p:sha(p) for p in paths}})


def fast_run(check=False):
    for p,h in load('data/round21_optimization_manifest.json')['sha256'].items():
        if sha(p)!=h:raise ValueError('optimized implementation changed: '+p)
    original=Model.segment
    try:
        Model.segment=fast_segment
        run(check)
    finally:Model.segment=original

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.freeze:freeze()
    else:fast_run(a.check)
