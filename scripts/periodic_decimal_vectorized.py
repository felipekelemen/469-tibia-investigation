#!/usr/bin/env python3
"""Equivalent prefix search with NumPy compatibility filtering in original order."""
import argparse
import numpy as np
from periodic_decimal_solver import Model,positions,summary
from periodic_decimal_fast import fast_segment
from periodic_decimal_experiment import run
from target_decimal_experiment import ROOT,load,dump,sha


def fast_unspaced(self,groups,node_limit=20000,solution_limit=2000):
    if not groups:raise ValueError('groups required')
    contexts=positions(groups);domains={}
    for gi,raw in enumerate(groups):
        for pos in range(len(raw)):
            offset=contexts[gi][0]+pos;previous=int(raw[pos-1]) if pos else contexts[gi][1]
            rows=[(end,d) for end in range(pos+1,len(raw)+1) for d in self.domain(raw[pos:end],offset,previous)]
            domains[gi,pos]=(np.array([r[0] for r in rows],dtype=np.int32),
                             np.array([r[1] for r in rows],dtype=np.int16).reshape((-1,self.period)))
    seen=set();found=set();nodes=0;capped=False
    def visit(gi,pos,key):
        nonlocal nodes,capped
        state=(gi,pos,key)
        if state in seen or capped:return
        if nodes>=node_limit or len(found)>=solution_limit:capped=True;return
        seen.add(state);nodes+=1
        if gi==len(groups):found.add(key);return
        if pos==len(groups[gi]):visit(gi+1,0,key);return
        if -1 not in key:
            remaining=[(groups[gi][pos:],contexts[gi][0]+pos,int(groups[gi][pos-1]) if pos else contexts[gi][1])]
            remaining += [(groups[j],*contexts[j]) for j in range(gi+1,len(groups))]
            if all(self.segment(g,key,off,prev)['word_path_count'] for g,off,prev in remaining):found.add(key)
            return
        ends,rows=domains[gi,pos];current=np.array(key,dtype=np.int16)
        valid=np.all((rows<0)|(current<0)|(rows==current),axis=1)
        nextkeys=np.maximum(rows[valid],current).tolist()
        for end,new in zip(ends[valid].tolist(),nextkeys):visit(gi,end,tuple(new))
    visit(0,0,(-1,)*self.period)
    return summary(found,nodes,capped)


def freeze():
    if (ROOT/'data/round21_vectorized_manifest.json').exists():raise ValueError('already frozen')
    paths=['data/round21_evidence_manifest.json','data/round21_optimization_manifest.json',
           'scripts/periodic_decimal_vectorized.py','tests/test_periodic_vectorized_equivalence.py']
    dump('data/round21_vectorized_manifest.json',{'stage':'After profiling, before final vectorized full run',
        'reason':'Profiling one declared control/model found12035359Python merge calls. Batch compatibility filtering keeps candidate order and exact state/key budgets. No scientific parameter changed. Earlier reference and suffix-only full batches were interrupted and not combined.',
        'sha256':{p:sha(p) for p in paths}})


def vectorized_run(check=False):
    for manifest in ('data/round21_optimization_manifest.json','data/round21_vectorized_manifest.json'):
        for p,h in load(manifest)['sha256'].items():
            if sha(p)!=h:raise ValueError('optimization changed: '+p)
    segment,unspaced=Model.segment,Model.solve_unspaced
    try:
        Model.segment=fast_segment;Model.solve_unspaced=fast_unspaced
        run(check)
    finally:Model.segment=segment;Model.solve_unspaced=unspaced

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.freeze:freeze()
    else:vectorized_run(a.check)
