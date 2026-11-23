#!/usr/bin/env python3
"""Run frozen origin-discrimination controls before permitting any game scoring."""
from collections import Counter
import hashlib
import json
import numpy as np
from round29_models import ROOT, compare, fit_english, overlap

LABELS={'text_affine':'T','text_copied':'T','numeric_uniform':'N','numeric_markov':'N',
        'numeric_shuffled_modules':'N','mixed':'M','text_permutation_challenge':'T',
        'copied_permutation_challenge':'T'}


def verify_inputs():
    manifest=json.loads((ROOT/'data/round29_experiment_manifest.json').read_text())
    for name,sha in manifest['sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name


def summarize(rows, protocol):
    cells={}
    for profile,truth in LABELS.items():
        subset=[r for r in rows if r['profile']==profile]
        cells[profile]={'expected':truth,'cases':len(subset),
            'total_correct':sum(r['comparison']['total_winner']==truth for r in subset),
            'predictive_correct':sum(r['comparison']['predictive_winner']==truth for r in subset),
            'total_confusion':dict(Counter(r['comparison']['total_winner'] for r in subset)),
            'predictive_confusion':dict(Counter(r['comparison']['predictive_winner'] for r in subset)),
            'true_affine_key_recovered':sum(r['true_affine_key_recovered'] for r in subset)}
    needed=protocol['gate']['minimum_correct_per_profile']
    eligible={kind:all(v['cases']==30 and v[kind+'_correct']>=needed for v in cells.values())
              for kind in ['total','predictive']}
    restricted={kind:all(v['cases']==30 and v[kind+'_correct']>=needed for k,v in cells.items() if 'challenge' not in k)
                for kind in ['total','predictive']}
    return {'profiles':cells,'general_origin_application_eligible':eligible,
            'six_in_family_profiles_pass':restricted,'gate_required_per_profile':needed,
            'semantic_translation_validated':False}


def run(protocol, fixtures, language):
    rows=[]
    for case in fixtures['cases']:
        for name,truth in LABELS.items():
            sequences=case['datasets'][name];train,held=sequences[:50],sequences[50:]
            comparison=compare(train,held,language)
            rows.append({'replicate':case['replicate'],'profile':name,'expected':truth,'author':case['author'],
                'comparison':comparison,'true_affine_key_recovered':comparison['selected']['T']['key']==case['true_affine_decode_key'] if 'challenge' not in name and truth=='T' else False,
                'overlap':[overlap(train,held,k) for k in [12,24]]})
        print('Completed replicate',case['replicate']+1,'/30; corpora',len(rows),flush=True)
    return {'round':29,'rows':rows,'summary':summarize(rows,protocol),
            'counts':{'corpora':len(rows),'source_windows':len(fixtures['cases']),
                      'configurations_per_corpus':624+6+3744},
            'limitations':['Paired profiles and shared external language model; not240independent English sources.',
              'T is a finite cipher family, N is a predictive statistical code, neither is an authenticated account of original authorship.',
              'Description lengths depend on shared language/interpreter conventions; no claim of universal minimum complexity.']}


if __name__=='__main__':
    verify_inputs()
    protocol=json.loads((ROOT/'data/round29_protocol.json').read_text())
    fixtures=json.loads((ROOT/'data/round29_fixtures.json').read_text())
    language=fit_english(protocol['english_training_sources'])
    reference=json.loads((ROOT/'data/round29_english_model.json').read_text())
    assert {k:v for k,v in language.items() if k!='table'}==reference
    out=ROOT/'results/round29_qualification.json'
    if out.exists():raise ValueError('Refuse to replace completed qualification')
    result=run(protocol,fixtures,language)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['summary'],indent=2),flush=True)
