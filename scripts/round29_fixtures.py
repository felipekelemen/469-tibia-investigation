#!/usr/bin/env python3
"""Thirty new-author windows, paired controls, explicit provenance and seeds."""
from pathlib import Path
import json
import random
from round29_models import ROOT, KEYS, letters


def encrypt(plain, table):
    return ''.join(f'{table[ord(c)-65]:02d}' for c in plain)


def create(protocol):
    rng=random.Random(protocol['fixtures']['seed'])
    records=json.loads((ROOT/'data/round29_reference/SOURCES.json').read_text())
    references=[letters(r['path'],r['encoding']) for r in records]
    books=json.loads((ROOT/'data/normalized_books.json').read_text())
    lengths=[2*(len(b['digits'])//2) for b in books]
    needed=sum(lengths)//2
    cases=[]
    for rep in range(30):
        author=rep%2;start=10000+(rep//2)*(needed+1024)
        plain=references[author][start:start+needed]
        assert len(plain)==needed and needed>=768
        a,b=rng.choice(KEYS)
        table=[(pow(a,-1,26)*(i-b))%26 for i in range(26)]
        permutation=list(range(26))
        while True:
            rng.shuffle(permutation)
            if all(permutation!=[(pow(x,-1,26)*(i-y))%26 for i in range(26)] for x,y in KEYS):
                break
        modules=[plain[i:i+32] for i in range(0,768,32)]
        shuffled=[]
        for text in modules:
            chars=list(text);rng.shuffle(chars);shuffled.append(''.join(chars))
        datasets={k:[] for k in protocol['fixtures']['profiles']}
        module_draws=[];cursor=0
        for index,n in enumerate(lengths):
            piece=plain[cursor:cursor+n//2];cursor+=n//2
            raw=encrypt(piece,table)
            uniform=''.join(str(rng.randrange(10)) for _ in range(n))
            markov=str(rng.randrange(10))
            while len(markov)<n:
                u=rng.random();last=int(markov[-1])
                markov+=str(last if u<.65 else (last+1)%10 if u<.85 else rng.randrange(10))
            selected=[];copied='';scrambled=''
            while len(copied)<n//2:
                j=rng.randrange(16 if index<50 else 24)
                selected.append(j);copied+=modules[j];scrambled+=shuffled[j]
            copied=copied[:n//2];scrambled=scrambled[:n//2]
            module_draws.append(selected)
            outputs={'text_affine':raw,'text_copied':encrypt(copied,table),
                'numeric_uniform':uniform,'numeric_markov':markov,
                'numeric_shuffled_modules':encrypt(scrambled,table),
                'mixed':raw if index%2==0 else markov,
                'text_permutation_challenge':encrypt(piece,permutation),
                'copied_permutation_challenge':encrypt(copied,permutation)}
            for name,value in outputs.items():
                assert len(value)==n
                datasets[name].append(value)
        cases.append({'replicate':rep,'source':records[author]['path'],'author':records[author]['author'],
            'start_letter':start,'end_letter':start+needed,'plaintext':plain,
            'true_affine_decode_key':[a,b],'permutation_encrypt_table':permutation,
            'modules':modules,'shuffled_modules':shuffled,'module_draws':module_draws,
            'datasets':datasets})
    return {'seed':protocol['fixtures']['seed'],'train_documents':50,
            'original_book_digit_lengths':[len(b['digits']) for b in books],
            'synthetic_digit_lengths':lengths,'source_windows':30,'corpora':240,'cases':cases}


if __name__=='__main__':
    path=ROOT/'data/round29_fixtures.json'
    if path.exists():raise ValueError('Refuse to replace fixtures')
    protocol=json.loads((ROOT/'data/round29_protocol.json').read_text())
    result=create(protocol)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Frozen',result['source_windows'],'windows and',result['corpora'],'paired corpora.')
