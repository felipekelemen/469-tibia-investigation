#!/usr/bin/env python3
"""Aggregate exact count certificates and retain every incomplete outcome."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from unit_morphism_lexicon import banks

ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text())


def verify(path):
    for name,sha in load(path)['sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:raise ValueError('Changed artifact: '+name)


def build():
    verify('data/round33_input_manifest.json');verify('data/round33_independent_manifest.json')
    fixtures=load('data/round33_fixtures.json');rows=load('results/round33_counts.json')['cases']
    assert [r['id'] for r in rows]==[r['id'] for r in fixtures['cases']]
    by_id={r['id']:r for r in rows};bank=banks()[0]['grapheme1_3']
    for f in fixtures['cases']:
        r=by_id[f['id']]
        if r['complete']:
            count=int(r['count']);assert count>=f.get('previous_returned_keys',0)
            if 'expected_count' in f:assert str(count)==f['expected_count']
            if f['kind']=='known_key_regression':assert count>=1
        else:assert r['count'] is None and r['reason']
    qualification=load('results/round33_count_qualification.json')
    assert len(qualification['cases'])==100 and qualification['all_counts_match']
    assert all(r['independent_count']==r['engine_count'] for r in qualification['cases'])
    independent=load('results/round33_independent_count.json');real=by_id['knightmare']
    assert independent['complete'] and real['complete'] and independent['count']==real['count']
    old=next(r for r in load('results/round23_targets.json')['targets'] if r['id']=='knightmare' and r['family']=='grapheme1_3')
    keys={tuple(sorted(k.items())) for k in old['keys']};assert len(keys)==len(old['keys'])==1769
    for key in keys:
        k=dict(key);assert set(k)==set(''.join(old['words']))
        assert all(''.join(k[d] for d in word) in bank.reverse for word in old['words'])
    observed=sorted(set(''.join(old['words'])));missing=sorted(set('0123456789')-set(observed))
    chay=[r for r in load('data/source_validation_inventory.json') if r['source_group']=='chayenne_interview']
    summaries={}
    for kind in dict.fromkeys(r['kind'] for r in rows):
        subset=[r for r in rows if r['kind']==kind];done=[r for r in subset if r['complete']]
        counts=[int(r['count']) for r in done]
        summaries[kind]={'cases':len(subset),'complete':len(done),'incomplete':len(subset)-len(done),
                         'zero':sum(n==0 for n in counts),'positive':sum(n>0 for n in counts),
                         'min_complete_count':str(min(counts)) if counts else None,
                         'max_complete_count':str(max(counts)) if counts else None}
    return {'round':33,'main_jobs':len(rows),'completed_jobs':sum(r['complete'] for r in rows),
            'incomplete_reasons':dict(Counter(r['reason'] for r in rows if not r['complete'])),
            'knightmare_observed_digit_keys':real['count'],'count_agrees_with_independent_contraction':True,
            'key_count_is_not_distinct_plaintext_count':True,'observed_digits':observed,'unobserved_digits':missing,
            'old1769distinct_keys_rechecked':len(keys),'tiny_independent_count_checks':100,
            'chayenne_sources_requiring_missing_digit':[r['id'] for r in chay if set(r['text'])&set(missing)],
            'per_kind':summaries,'significance_or_rank_test':None,
            'comparison_limits':'Previous shuffle cases are reused/exposed; uniform controls can observe a different number of digits. Counts of observed-digit assignments are descriptive, not language scores or an independent significance test.',
            'candidate_translation':None,'mission_disposition':'I',
            'scope':'Exact finite lexical counting. R23Knightmare and completed shuffle counts now closed; prior bounded files preserved. No English/semantic translator qualified. Incomplete control counts remain unknown.'}


if __name__=='__main__':
    result=build();path=ROOT/'results/round33_summary.json'
    if path.exists():assert load('results/round33_summary.json')==result
    else:
        with path.open('x') as f:f.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
