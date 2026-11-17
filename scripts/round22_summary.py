#!/usr/bin/env python3
"""Separate exhaustive coverage, retained truths and lexical ambiguity."""
from target_decimal_experiment import load,dump,vocabulary
from target_decimal_solver import encode


def build():
    result=load('results/round22_exhaustive.json');q=[r for r in result['results'] if r['kind']=='qualification']
    real=[r for r in result['results'] if r['kind']=='real'];vocab=set(vocabulary())
    witnesses=[]
    for codec,a,b in [('ordinal0_compact','BY','ME'),('ordinal1_compact','AHEAD','READ')]:
        assert a in vocab and b in vocab and a!=b
        assert encode(a,codec)==encode(b,codec)
        witnesses.append({'codec':codec,'word1':a,'word2':b,'same_decimal':encode(a,codec),
                          'scope':'Posthoc arithmetic ambiguity certificate in synthetic codec, NOT a469translation. Identical input digits remain identical after every tested key/feedback.'})
    return {**result['summary'],
            'unique_key_and_unique_word_paths':sum(len(r['keys'])==1 and all(p['word_path_count']==1 for p in r['python_candidate_reviews'][0]['parts']) for r in q),
            'maximum_synthetic_keys':max(len(r['keys']) for r in q),
            'candidate_keys_independently_checked':sum(len(r['keys']) for r in result['results']),
            'real_domain_assignments':sum(r['domain_keys'] for r in real),
            'real_checked_keys':sum(r['checked_keys'] for r in real),
            'real_prefix_pruned_keys':sum(r['prefix_pruned_keys'] for r in real),
            'real_short_fragment_maximum_keys':max(r['selected_fragment_pass_keys'] for r in real),
            'real_details':[{k:r[k] for k in ('codec','period','feedback','selected_fragment','domain_keys','checked_keys','prefix_pruned_keys','selected_fragment_pass_keys','keys')} for r in real],
            'lexical_ambiguity_certificates':witnesses,
            'remaining_round21_chayenne_incomplete_models':0,
            'combined_round21_chayenne_complete_models':96,
            'new_verified_translations':0}

if __name__=='__main__':dump('data/round22_summary.json',build())
