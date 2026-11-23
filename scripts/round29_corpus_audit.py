#!/usr/bin/env python3
"""Copy dependencies only; never assign origin from an unqualified model."""
from collections import defaultdict
import json
from round29_models import ROOT, overlap, letters
from round28_experiment import source_inputs


def components(books,k=12):
    parent=list(range(len(books)));owner={}
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,book in enumerate(books):
        s=book['digits']
        for word in {s[j:j+k] for j in range(len(s)-k+1)}:
            if word in owner:parent[find(i)]=find(owner[word])
            else:owner[word]=i
    groups=defaultdict(list)
    for i,book in enumerate(books):groups[find(i)].append(book['id'])
    return sorted(groups.values(),key=lambda g:(-len(g),g))


def audit(fixtures, qualification):
    sources=json.loads((ROOT/'data/round29_reference/SOURCES.json').read_text())
    texts={s['path']:letters(s['path'],s['encoding']) for s in sources}
    intervals=defaultdict(list)
    for row in fixtures['cases']:
        start,end=row['start_letter'],row['end_letter']
        assert texts[row['source']][start:end]==row['plaintext']
        assert all(end<=a or start>=b for a,b in intervals[row['source']])
        intervals[row['source']].append((start,end))
    books=json.loads((ROOT/'data/normalized_books.json').read_text())
    groups=components(books)
    priority=[]
    for source,record in source_inputs().items():
        for value in record['groups']:
            if len(value)<12:continue
            hits=[]
            for book in books:
                start=book['digits'].find(value)
                while start>=0:
                    hits.append({'book':book['id'],'offset':start})
                    start=book['digits'].find(value,start+1)
            priority.append({'source':source,'digits':value,'occurrences':hits})
    return {'round':29,'semantic_translation_validated':False,
        'source_windows_verified':len(fixtures['cases']),'nonoverlapping_source_positions':True,
        'paired_profiles_per_window':8,'book_components_raw12':groups,
        'independent_book_component_holdout_possible':len(groups)>1,
        'exposed_first50_last20_overlap':[overlap([b['digits'] for b in books[:50]],
                                                  [b['digits'] for b in books[50:]],k) for k in [12,24]],
        'priority_groups_at_least12_digits':priority,
        'qualification':qualification['summary']['general_origin_application_eligible'],
        'game_origin_model_scoring':'not_performed_gate_failed' if not any(qualification['summary']['general_origin_application_eligible'].values()) else 'requires_separate_exposed_application_record',
        'game_origin_label':None,'original_nontextual_generator_authenticated':False,
        'limit':'All game data already exposed. Connected copies do not establish semantic plaintext or independent validation.'}


if __name__=='__main__':
    from round29_experiment import verify_inputs
    verify_inputs()
    fixtures=json.loads((ROOT/'data/round29_fixtures.json').read_text())
    qualification=json.loads((ROOT/'results/round29_qualification.json').read_text())
    result=audit(fixtures,qualification)
    path=ROOT/'results/round29_corpus_audit.json'
    if path.exists():raise ValueError('Refuse to replace corpus audit')
    path.write_text(json.dumps(result,indent=2)+'\n')
    print('Copy components:',list(map(len,result['book_components_raw12'])))
    print('Game scoring:',result['game_origin_model_scoring'])
