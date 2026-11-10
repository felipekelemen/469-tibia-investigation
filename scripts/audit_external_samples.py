#!/usr/bin/env python3
"""Content novelty screening, not authentication or semantic validation.

No canonical reading, tokenization or translation is inferred by this script.
"""
import hashlib,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]

def locations(text,needle):
    start=0
    while True:
        i=text.find(needle,start)
        if i<0:return
        yield i
        start=i+1

def shared_mask(sample,books,k):
    known={b['digits'][i:i+k] for b in books for i in range(len(b['digits'])-k+1)}
    covered=set()
    for i in range(len(sample)-k+1):
        if sample[i:i+k] in known:covered.update(range(i,i+k))
    return covered

def main():
    bookpath=ROOT/'data/normalized_books.json';books=json.loads(bookpath.read_text())
    inputs=json.loads((ROOT/'data/external_samples_screen.json').read_text());results=[]
    for sample in inputs:
        digits=re.sub('[^0-9]','',sample['text']);whole=[]
        for b in books:
            whole.extend({'book_id':b['id'],'raw_digit_start':i} for i in locations(b['digits'],digits))
        coverage={str(k):len(shared_mask(digits,books,k)) for k in [8,12,16,24]}
        results.append({'id':sample['id'],'digits':digits,'digit_count':len(digits),'literal_matches':whole,'literal_match_count':len(whole),
          'positions_covered_by_shared_kgrams':coverage,
          'content_novelty_status':'REUSED_CONTENT_NOT_INDEPENDENT' if whole else 'WHOLE_STRING_ABSENT_NOT_PROOF_OF_INDEPENDENCE',
          'previously_exposed':sample['previously_exposed']})
    out={'input_books_sha256':hashlib.sha256(bookpath.read_bytes()).hexdigest(),'samples':results,
         'limits':['A distinct historical source can independently attest reused content without supplying independent holdout content.',
           'No full match does not establish novelty, common code, plaintext or temporal independence.',
           'Only raw exact matches and raw kgram coverage are checked; transformed/motif-level dependencies remain.',
           'These samples have already been publicly discussed; none is a prospective blind test.']}
    (ROOT/'results/external_samples_screen.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps([{'id':r['id'],'matches':r['literal_match_count'],'digits':r['digit_count'],'coverage12':r['positions_covered_by_shared_kgrams']['12']} for r in results],indent=2))
if __name__=='__main__':main()
