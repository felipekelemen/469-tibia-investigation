#!/usr/bin/env python3
"""Reporting audit: count unions of partial key cylinders, never sum overlaps."""
from functools import lru_cache
from target_decimal_experiment import load,dump


def key_union_count(keys,period):
    keys=tuple(sorted(set(tuple(k) for k in keys)))
    if any(len(k)!=period or any(v not in range(-1,10) for v in k) for k in keys):
        raise ValueError('invalid partial key')
    @lru_cache(None)
    def count(rows):
        if not rows:return 0
        if any(all(v<0 for v in row) for row in rows):return 10**len(rows[0])
        return sum(count(tuple(sorted(set(row[1:] for row in rows if row[0] in (-1,v))))) for v in range(10))
    return count(keys)


def build():
    result=load('results/round21_periodic_decimal.json')
    game={}
    for name,g in result['game'].items():
        counts={m:key_union_count(f['keys'],len(f['keys'][0])) if f['keys'] else 0 for m,f in g['fits'].items()}
        game[name]={'complete_models':sum(f['complete'] for f in g['fits'].values()),
                    'incomplete_models':[m for m,f in g['fits'].items() if not f['complete']],
                    'found_distinct_keys_within_models':sum(counts.values()),
                    'models_with_any_key':[m for m,n in counts.items() if n],
                    'scope':'Distinct within each model; aliases across models remain. If a model is incomplete, found keys are lower bounds only.'}
    controls=[]
    for c in result['controls']:
        rows=c['rows']
        controls.append({'target':c['target'],'kind':c['kind'],'datasets':len(rows),
                         'datasets_all_models_complete':sum(r['all_complete'] for r in rows),
                         'datasets_with_any_found_key':sum(any(f['full_key_count'] for f in r['fits'].values()) for r in rows),
                         'incomplete_model_searches':sum(not f['complete'] for r in rows for f in r['fits'].values())})
    unspaced=result['qualification']['unspaced']
    return {'qualification':result['qualification']['summary'],
            'unspaced_parser_fixtures':{'total':len(unspaced),'complete':sum(r['complete'] for r in unspaced),
                                       'true_key_retained':sum(r['truth_retained'] for r in unspaced)},
            'game':game,'controls':controls,'total_null_datasets':sum(c['datasets'] for c in controls),
            'bookkeeping_note':'Raw full_key_count sums completions of partial keys. With unknown word resets these cylinders may overlap, so raw counts can overcount distinct keys. This report counts their exact union within each real model; null summaries use only nonempty existence, which is unaffected. Search/expansion caps stay conservative.',
            'new_verified_translations':0}

if __name__=='__main__':dump('data/round21_summary.json',build())
