#!/usr/bin/env python3
"""Bounded structural falsification; no semantic assertions or fitted translations."""
import collections, json, math, pathlib, random
ROOT=pathlib.Path(__file__).resolve().parents[1]

def lcg_fits(sequences, modulus=100):
    """All a,c satisfying x[t+1]=(a*x[t]+c) mod m, reset at books."""
    candidates={(a,c) for a in range(modulus) for c in range(modulus)}
    for xs in sequences:
        for x,y in zip(xs,xs[1:]):
            candidates={p for p in candidates if (p[0]*x+p[1])%modulus==y}
            if not candidates:return []
    return sorted(candidates)

def recurrence2_fits(sequences, modulus=100):
    candidates=None
    for xs in sequences:
        for x,y,z in zip(xs,xs[1:],xs[2:]):
            if candidates is None:
                candidates={(a,b,(z-a*y-b*x)%modulus) for a in range(modulus) for b in range(modulus)}
            else:candidates={p for p in candidates if (p[0]*y+p[1]*x+p[2])%modulus==z}
            if not candidates:return []
    return sorted(candidates or [])

def occurrences(seq,needle):
    return sum(seq[i:i+len(needle)]==needle for i in range(len(seq)-len(needle)+1))

def main():
    books=json.loads((ROOT/'data/normalized_books.json').read_text())
    seqs=[[int(c) for c in b['codes']] for b in books]
    raw=[b['digits'] for b in books]
    rng=random.Random(4693478)
    needles=['3478','43153','34784','653','768','90871','97664']
    counts={w:sum(occurrences(s,w) for s in raw) for w in needles}
    null={w:[] for w in needles}
    # Local per-book digit shuffle and independent null preserve length and frequencies.
    for _ in range(999):
        shuffled=[]
        for s in raw:
            chars=list(s);rng.shuffle(chars);shuffled.append(''.join(chars))
        for w in needles:null[w].append(sum(occurrences(s,w) for s in shuffled))
    # Code shuffle additionally preserves two-digit vocabulary and digit-pair correlations.
    code_null={w:[] for w in needles}
    for _ in range(999):
        texts=[]
        for b in books:
            cs=list(b['codes']);rng.shuffle(cs);texts.append(''.join(cs))
        for w in needles:code_null[w].append(sum(occurrences(s,w) for s in texts))
    block_null={w:[] for w in needles}
    for _ in range(999):
        texts=[]
        for s in raw:
            blocks=[s[i:i+16] for i in range(0,len(s),16)];rng.shuffle(blocks);texts.append(''.join(blocks))
        for w in needles:block_null[w].append(sum(occurrences(s,w) for s in texts))
    out={'seed':4693478,'replicates':999,
         'generator_tests':{'domain':'imported reconstructed 00..99 codes; no arbitrary coordinate remapping; per-book resets',
          'lcg_mod100':lcg_fits(seqs),'affine_order2_mod100':recurrence2_fits(seqs)},
         'honeminas':{'vectors':[[4,3,1,5,3],[3,4,7,8,4]],'dot_product':sum(x*y for x,y in zip([4,3,1,5,3],[3,4,7,8,4])),
          'limit':'Literal dot-product convention only. Undefined g,a,m,p and gate energy equation do not specify a decoder.'},
         'substring_tests':{}}
    for w in needles:
        def summary(vals):return {'mean':sum(vals)/len(vals),'min':min(vals),'max':max(vals),
          'p_upper_one_sided':(1+sum(v>=counts[w] for v in vals))/1000,
          'p_lower_one_sided':(1+sum(v<=counts[w] for v in vals))/1000}
        out['substring_tests'][w]={'observed_raw':counts[w], 'digit_shuffle':summary(null[w]),'code_shuffle_padded':summary(code_null[w]),'block16_shuffle':summary(block_null[w])}
    out['limitations']=['Code-shuffle uses padded reconstructed digits (11458 versus11263), a sensitivity check, not calibrated identical-sample inference.',
      'Repeated motifs inflate effective sample size; raw substring enrichment is not semantic evidence.',
      'Seven prelisted needles and two tails; p values exploratory, uncorrected; no translation claimed.',
      'LCG rejections cover these exact recurrences only, not nonlinear, hidden-state or remapped generators.']
    (ROOT/'results/structural.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
