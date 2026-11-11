#!/usr/bin/env python3
"""Broader independent-English scorer; V1/V2 code and protocols unchanged."""
import collections,functools,hashlib,pathlib,random,json
import numpy as np
from homophonic_benchmark import letters,encode,segments
from robust_homophonic import solve as bank_solve
ROOT=pathlib.Path(__file__).resolve().parents[1]
TRAINING_PATHS=['data/english_reference/alice.txt','data/benchmark_reference/frankenstein.txt',
 'data/benchmark_reference/pride_prejudice.txt','data/benchmark_reference/sherlock_holmes.txt',
 'data/benchmark_reference_v2/war_worlds.txt','data/benchmark_reference_v2/great_expectations.txt']
@functools.lru_cache(maxsize=1)
def build_model():
    counts=np.zeros(26**4,dtype=np.int64);rows=[]
    for path in TRAINING_PATHS:
        p=ROOT/path;full=letters(p)
        text=full[:int(.8*len(full))] if path.endswith('/alice.txt') else full[:100000]
        xs=np.asarray([ord(c)-65 for c in text],dtype=np.int64)
        ix=((xs[:-3]*26+xs[1:-2])*26+xs[2:-1])*26+xs[3:]
        counts+=np.bincount(ix,minlength=26**4)
        rows.append({'path':path,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'letters':len(text),
          'text_sha256':hashlib.sha256(text.encode()).hexdigest()})
    table=np.log10((counts+.01)/(int(counts.sum())+.01*26**4));table.setflags(write=False)
    return table,{'training_sources':rows,'tetragrams':int(counts.sum()),'observed_tetragrams':int(np.count_nonzero(counts)),
      'model_sha256':hashlib.sha256(table.astype('<f8').tobytes()).hexdigest(),'alpha':.01,
      'scope':'Previous development and opened qualification authors now training; no V3qualification author used.'}

def development_fixture(i):
    seed=80469000+i;rng=random.Random(seed);text=letters(ROOT/'data/benchmark_reference/frankenstein.txt')
    motifs=[text[x:x+256] for x in [rng.randrange(20000,len(text)-1000) for _ in range(8)]]
    encoded,key,allocation=encode(''.join(motifs),99,'skewed',seed);pools=[encoded[j*256:(j+1)*256] for j in range(8)]
    schedule=[rng.randrange(8) for _ in range(30)];plain=''.join(motifs[j] for j in schedule);codes=[c for j in schedule for c in pools[j]]
    return {'train':segments(codes[:5668]),'hold':segments(codes[5668:6692]),'truth':plain[5668:6692],'key':key,'seed':seed+900000}

def solve(seqs,table,seed,*,banks=2,frequency_weight=.5):
    return bank_solve(seqs,table,seed=seed,banks=banks,restarts=8,steps=100000,num_codes=100,max_temp=12,frequency_weight=frequency_weight)

def evaluate(f,fit):
    codes=[c for s in f['hold'] for c in s];truth=f['truth'];pred=''.join(chr(fit['mapping'][c]+65) for c in codes)
    return {'correct_letters':sum(a==b for a,b in zip(pred,truth)),'letters':len(truth),
       'accuracy':sum(a==b for a,b in zip(pred,truth))/len(truth),'preview':pred[:120],
       'truth_preview':truth[:120],'unseen_positions':sum(c not in {x for s in f['train'] for x in s} for c in codes),
       'known_key_exact':''.join(chr(f['key'][c]+65) for c in codes)==truth}
