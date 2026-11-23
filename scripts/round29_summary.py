#!/usr/bin/env python3
"""Post-fit descriptive aggregation; no refitting, new thresholds or ranking."""
from collections import Counter
import json
import statistics
from round29_models import ROOT


def span(values):
    return {'mean':statistics.mean(values),'min':min(values),'max':max(values)}


def build():
    load=lambda p:json.loads((ROOT/p).read_text())
    results=load('results/round29_qualification.json')
    fixtures=load('data/round29_fixtures.json')
    by_rep={c['replicate']:c for c in fixtures['cases']}
    profiles={}
    for profile,cell in results['summary']['profiles'].items():
        rows=[r for r in results['rows'] if r['profile']==profile]
        authors={}
        for name in sorted({r['author'] for r in rows}):
            subset=[r for r in rows if r['author']==name]
            authors[name]={'cases':len(subset),
                'total_confusion':dict(Counter(r['comparison']['total_winner'] for r in subset)),
                'predictive_confusion':dict(Counter(r['comparison']['predictive_winner'] for r in subset))}
        profiles[profile]={**cell,'authors':authors,
            'T_minus_N_total_bits':span([r['comparison']['models']['T']['total_bits']-r['comparison']['models']['N']['total_bits'] for r in rows]),
            'T_minus_N_held_bits':span([r['comparison']['models']['T']['held_data_bits']-r['comparison']['models']['N']['held_data_bits'] for r in rows]),
            'selected_text_key_equals_affine_fixture_relabeling':sum(r['comparison']['selected']['T']['key']==by_rep[r['replicate']]['true_affine_decode_key'] for r in rows),
            'held_coverage_raw12':span([r['overlap'][0]['held_digits_covered']/r['overlap'][0]['held_digits'] for r in rows]),
            'held_coverage_raw24':span([r['overlap'][1]['held_digits_covered']/r['overlap'][1]['held_digits'] for r in rows])}
    return {'round':29,'profiles':profiles,
        'total_rule_confusion':{truth:dict(Counter(r['comparison']['total_winner'] for r in results['rows'] if r['expected']==truth)) for truth in 'TNM'},
        'predictive_rule_confusion':{truth:dict(Counter(r['comparison']['predictive_winner'] for r in results['rows'] if r['expected']==truth)) for truth in 'TNM'},
        'general_origin_application_eligible':results['summary']['general_origin_application_eligible'],
        'new_game_candidates':[],'translation_validated':False,
        'scope':'N for shuffled modules is a predeclared structural-control label: composition comes from English, and this is not a proof that all text information is absent. Separate per-author counts are descriptive; no per-author qualification claimed.'}


if __name__=='__main__':
    path=ROOT/'results/round29_summary.json'
    if path.exists():raise ValueError('Refuse to replace summary')
    path.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n')
    print('Post-fit descriptive summary saved.')
