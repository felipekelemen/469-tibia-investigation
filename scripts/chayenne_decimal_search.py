#!/usr/bin/env python3
"""Bounded exact lexical segmentation and digit-key search for unspaced fragments."""
import argparse
import math
import random
from target_decimal_experiment import ROOT, load, dump, sha, vocabulary, transfer
from target_decimal_solver import Solver, FAMILIES, merge, dictionary_parse_count
from independent_word_validator import body, words

SEED=203613


def solve(groups, solver, node_limit=10000, solution_limit=1000):
    if not groups or any(not g or not g.isascii() or not g.isdigit() for g in groups):
        raise ValueError('nonempty decimal fragments required')
    observed=set(''.join(groups)); nodes=0; capped=False; solutions=set(); seen=set()
    domains={}
    for gi,g in enumerate(groups):
        for pos in range(len(g)):
            domains[gi,pos]=[(end,d) for end in range(pos+1,len(g)+1) for d in solver.domain(g[pos:end])]

    def visit(gi,pos,mapping):
        nonlocal nodes,capped
        state=(gi,pos,mapping)
        if state in seen or capped:
            return
        if nodes>=node_limit or len(solutions)>=solution_limit:
            capped=True; return
        seen.add(state); nodes+=1
        if set(dict(mapping)) == observed:
            remaining=[groups[gi][pos:]]+groups[gi+1:] if gi<len(groups) else []
            if all(dictionary_parse_count(g,solver,mapping)>0 for g in remaining):
                solutions.add(mapping)
            return
        if gi==len(groups):
            solutions.add(mapping); return
        if pos==len(groups[gi]):
            visit(gi+1,0,mapping); return
        for end,extension in domains[gi,pos]:
            new=merge(mapping,extension)
            if new is not None:
                visit(gi,end,new)
    visit(0,0,())
    return {'complete':not capped,'nodes':nodes,'mappings':[list(map(list,m)) for m in sorted(solutions)],
            'full_key_count':sum(math.factorial(10-len(m)) for m in solutions)}


def build():
    vocab=vocabulary(); vset=set(vocab); solvers={f:Solver(vocab,f) for f in FAMILIES}
    docs={n:words(body(ROOT/f'data/word_validator_reference/{n}.txt')) for n in ('wizard_oz','peter_pan')}
    starts={n:[i for i in range(len(d)-6) if all(w in vset for w in d[i:i+6])] for n,d in docs.items()}
    from target_decimal_solver import encode
    positives=[]
    for fi,(family,solver) in enumerate(solvers.items()):
        rng=random.Random(SEED+fi)
        for trial in range(10):
            name=('wizard_oz','peter_pan')[trial%2]; start=rng.choice(starts[name]); w=docs[name][start:start+6]
            digits=list('0123456789'); rng.shuffle(digits); enc=dict(zip('0123456789',digits)); truth={v:k for k,v in enc.items()}
            raw=[''.join(enc[c] for c in encode(''.join(part),family)) for part in (w[:3],w[3:])]
            result=solve(raw,solver)
            positives.append({'family':family,'trial':trial,'source':name,'start':start,'words':w,'groups':raw,
                              'complete':result['complete'],'nodes':result['nodes'],'full_keys':result['full_key_count'],
                              'truth_retained':any(all(truth[k]==v for k,v in m) for m in result['mappings'])})
        print('Unspaced controls:',family,flush=True)
    inv={r['id']:r for r in load('data/source_validation_inventory.json')}
    groups=[inv[k]['text'] for k in ('chayenne_2009_part1','chayenne_2009_part2')]
    solutions={f:solve(groups,s) for f,s in solvers.items()}
    print('Chayenne:',{f:(s['complete'],s['full_key_count'],s['nodes']) for f,s in solutions.items()},flush=True)
    books=load('data/normalized_books.json'); ids=set(load('data/normalized_splits.json')['discovery_book_ids'])
    pools=[[b['digits'][i:i+n] for b in books if b['id'] in ids for i in range(len(b['digits'])-n+1)] for n in (36,13)]
    controls=[]
    for ki,kind in enumerate(('within_fragment_shuffle','two_copied_fragments')):
        rng=random.Random(SEED+100+ki)
        rows=[]
        for trial in range(19):
            if ki:
                altered=[rng.choice(p) for p in pools]
            else:
                altered=[]
                for g in groups:
                    chars=list(g); rng.shuffle(chars); altered.append(''.join(chars))
            fits={f:solve(altered,s) for f,s in solvers.items()}
            rows.append({'trial':trial,'groups':altered,'fits':{f:{'complete':r['complete'],'nodes':r['nodes'],'full_keys':r['full_key_count']} for f,r in fits.items()}})
        controls.append({'kind':kind,'rows':rows})
        print('Unspaced nulls:',kind,flush=True)
    return {'positives':positives,'groups':groups,'solutions':solutions,
            'transfer':transfer(solutions,solvers,groups,True),'controls':controls,
            'new_verified_translations':0,'scope':'Conditional dictionary segmentation under bounded key search; incomplete is unresolved, never exclusion or unique translation.'}


def freeze():
    if (ROOT/'data/round20_chayenne_manifest.json').exists(): raise ValueError('already frozen')
    paths=['data/round20_chayenne_protocol.json','data/round20_evidence_manifest.json','scripts/chayenne_decimal_search.py',
           'data/normalized_books.json','data/normalized_splits.json']
    dump('data/round20_chayenne_manifest.json',{'stage':'Before direct unspaced search','sha256':{p:sha(p) for p in paths}})


def run(check=False):
    for manifest in ('data/round20_evidence_manifest.json','data/round20_chayenne_manifest.json'):
        for p,h in load(manifest)['sha256'].items():
            if sha(p)!=h: raise ValueError('changed input: '+p)
    result=build()
    if check:
        if result!=load('results/round20_chayenne_decimal.json'): raise ValueError('replay mismatch')
    else:
        dump('results/round20_chayenne_decimal.json',result)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--freeze',action='store_true'); p.add_argument('--check',action='store_true'); a=p.parse_args()
    if a.freeze: freeze()
    else: run(a.check)
