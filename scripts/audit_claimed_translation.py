#!/usr/bin/env python3
"""Apply published v7 literally, no anagrams, inserted words or spelling repairs."""
import json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    mapping=json.loads((ROOT/'sources/arturo/data/mapping_v7.json').read_text())
    books=json.loads((ROOT/'data/normalized_books.json').read_text())
    literal=[''.join(mapping.get(c,'?') for c in b['codes']) for b in books]
    phrases=['TUN DIE REIST EN ER','IM MIN HEIME DIE URALTE STEIN','TRAUT IST LEICH AN BERUCHTIG','DEN EN DE REDER KOENIG','SALZBERG','ORANGENSTRASSE','GOTTDIENER','WEICHSTEIN']
    out={'method':'Published mapping_v7 applied to kimlage reconstruction; spaces only removed in exact phrase matching. Tokenization differs from Arturo CADST, so this is a transfer test, not reproduction of its training score.',
      'unmapped_symbols':sum(s.count('?') for s in literal),
      'exact_claimed_phrase_counts':{p:sum(s.count(p.replace(' ','')) for s in literal) for p in phrases},
      'literal_examples':[{'book_id':books[i]['id'],'text':literal[i]} for i in range(5)],
      'holdout_status':'Mapping was fitted on the public corpus. No part of these books is independent validation of this mapping.',
      'conclusion':'A mapping application and word coverage do not establish readable prose. Anagrams, substitutions, deletions and narrative repairs require separately specified deterministic rules and independent holdout.'}
    (ROOT/'results/claimed_translation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
