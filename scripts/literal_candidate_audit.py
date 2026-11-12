#!/usr/bin/env python3
"""Literal fixed-V4 audit. This is not an automatic English/meaning detector.

Assistant linguistic review covers all70outputs. Short probes illustrate why dictionary hits
and repeated fragments are not translation evidence. No lore bonus or key fit.
"""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
# These probes were recorded after literal inspection: exploratory illustrations,
# not a preregistered language test, candidate selection metric or p value.
PROBES=['BUT I WAS','I WAS','THE SAND','WAS TO THE','IN THE','THE NAME',
        'OF THE','AND THEN','ALL THE SAND','THE OTHER','THERE']

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def raw_offsets(book):
    omitted=set(book['omitted_zero_code_indices']);pieces=[];offsets=[0]
    for i,c in enumerate(book['codes']):
        if i in omitted:
            if not c.startswith('0'):raise ValueError('invalid omitted leading zero')
            piece=c[1:]
        else:piece=c
        pieces.append(piece);offsets.append(offsets[-1]+len(piece))
    if ''.join(pieces)!=book['digits']:raise ValueError('serialized codes do not roundtrip')
    return offsets

def hits(text,needle):
    i=0
    while True:
        i=text.find(needle,i)
        if i<0:return
        yield i;i+=1

def run():
    path=ROOT/'results/qualified_tibia_search_v4.json';input_path=ROOT/'data/normalized_books.json'
    mapping=json.loads(path.read_text())['observed']['mapping']
    books=json.loads(input_path.read_text());split=json.loads((ROOT/'data/normalized_splits.json').read_text())
    discovery=set(split['discovery_book_ids']);literals=[];probe_hits={p:[] for p in PROBES}
    for b in books:
        text=''.join(chr(mapping[int(c)]+65) for c in b['codes']);offsets=raw_offsets(b)
        role='discovery_used_for_mapping' if b['id'] in discovery else 'previously_exposed_reserved'
        literals.append({'book_id':b['id'],'role':role,'code_count':len(b['codes']),
          'raw_digit_count':len(b['digits']),'literal':text,'source_digits_sha256':hashlib.sha256(b['digits'].encode()).hexdigest(),
          'alignment_count_capped_2':b['alignment_count_capped_2']})
        for phrase in PROBES:
            needle=phrase.replace(' ','')
            for start in hits(text,needle):
                end=start+len(needle);a,z=offsets[start],offsets[end]
                assert text[start:end]==needle
                probe_hits[phrase].append({'book_id':b['id'],'role':role,'code_start':start,'code_end_exclusive':end,
                  'original_raw_digit_start':a,'original_raw_digit_end_exclusive':z,'original_raw_digits':b['digits'][a:z],
                  'reconstructed_codes':b['codes'][start:end],'literal':text[start:end],'spaces_only_display':phrase,
                  'context':text[max(0,start-12):min(len(text),end+18)],
                  'book_zero_alignment_ambiguous':b['alignment_count_capped_2']>1})
    out={'input_sha256':digest(input_path),'mapping_result_sha256':digest(path),'mapping':mapping,
      'book_count':len(books),'total_literal_letters':sum(len(b['literal']) for b in literals),'books':literals,
      'review':{'kind':'literal linguistic review by assistant; no automatic grammar/coherence classifier claimed',
        'substantive_candidate_minimum_words':6,'substantive_candidate_minimum_letters':25,
        'allowed_display_transformations':'spaces and punctuation only; same concatenated letters',
        'not_permitted':'letter insertions/deletions/substitutions, anagrams, revised key, lore-word scoring bonus',
        'substantive_candidates':[],
        'conclusion':'No long grammatical continuous English reading independently compatible with Tibia lore was identified in these70fixed outputs.',
        'scope':'Rejects promotion of these literal outputs as candidate translations; does not exclude other decoding mechanisms.'},
      'short_probe_examples':{p:{'occurrences':len(v),'hits':v} for p,v in probe_hits.items()},
      'near_match_warning':{'desired_phrase':'ALL THE SAND','literal_recurrent_form':'ALLETHESAND',
        'required_disallowed_repair':'delete the extra E','status':'not a literal match and not a translation'},
      'limits':['All source books were publicly exposed and mapping was selected on68books; the2reservedbooks are correlated.',
        'Probe lists are posthoc illustrations, not independent confirmation; their hits often reuse the same module.',
        'Raw digit boundaries use the chosen imported leading-zero reconstruction; nine wholebook alignments are ambiguous.',
        'Recognizable function words or proper-name-like strings are not a phrase meaning or a canonical gloss.',
        'No externally attested English plaintext is supplied for these books.']}
    (ROOT/'results/literal_candidate_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'books':len(books),'letters':out['total_literal_letters'],'substantive_candidates':0,
      'probes':{p:len(v) for p,v in probe_hits.items()}},indent=2))
    return out
if __name__=='__main__':run()
