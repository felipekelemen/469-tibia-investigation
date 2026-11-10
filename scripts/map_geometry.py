#!/usr/bin/env python3
"""Can predeclared numerical functions explain the imported label table?

Label names have no semantics here. A collision (same feature, different labels)
refutes an exact single-valued decoder from that feature alone.
"""
import collections,json,pathlib,random
from matrix_experiments import MATRICES,transpose
ROOT=pathlib.Path(__file__).resolve().parents[1]

def features():
    fs={
      'sum':lambda x,y:x+y,'product':lambda x,y:x*y,
      'xor':lambda x,y:x^y,'and':lambda x,y:x&y,'or':lambda x,y:x|y,
      'abs_difference':lambda x,y:abs(x-y),'square_sum':lambda x,y:x*x+y*y,
      'sum_product':lambda x,y:x*y+x+y,'triangular_unordered_pair':lambda x,y:10*min(x,y)+max(x,y)}
    for name,original in MATRICES.items():
        for orient,m in [('column',original),('transpose',transpose(original))]:
            fs[f'{name}_{orient}_lookup_mod4']=lambda x,y,m=m:m[x%4][y%4]
            for mod in [10,14,26,29,100]:
                for bitorder in ['low_first','high_first']:
                    def f(x,y,m=m,mod=mod,bitorder=bitorder):
                        bits=list(range(4)) if bitorder=='low_first' else list(reversed(range(4)))
                        return sum(((x>>bits[i])&1)*m[i][j]*((y>>bits[j])&1) for i in range(4) for j in range(4))%mod
                    fs[f'{name}_{orient}_bit_bilinear_{bitorder}_mod{mod}']=f
    return fs

def majority_accuracy(values,labels):
    groups=collections.defaultdict(collections.Counter)
    for v,label in zip(values,labels):groups[v][label]+=1
    return sum(max(c.values()) for c in groups.values())/len(labels)

def main():
    mapping=json.loads((ROOT/'data/normalized_code_map.json').read_text())
    codes=sorted(mapping);labels=[mapping[c] for c in codes];fs=features()
    vals={name:[f(int(c[0]),int(c[1])) for c in codes] for name,f in fs.items()}
    records={name:{'distinct_features':len(set(v)),'majority_accuracy_all_codes':majority_accuracy(v,labels),
                  'minimum_table_mismatches':round((1-majority_accuracy(v,labels))*len(codes))} for name,v in vals.items()}
    best=max(r['majority_accuracy_all_codes'] for r in records.values());rng=random.Random(4692026);null=[]
    for _ in range(999):
        shuffled=labels[:];rng.shuffle(shuffled)
        null.append(max(majority_accuracy(v,shuffled) for v in vals.values()))
    # Deterministic cross-validation on table entries, not books or plaintext.
    # Only features represented by >=2 codes can be predicted from another entry.
    for name,v in vals.items():
        seen=correct=0
        for i in range(len(codes)):
            pool=collections.Counter(labels[j] for j in range(len(codes)) if j!=i and v[j]==v[i])
            if pool:
                seen+=1; pred=sorted(pool,key=lambda a:(-pool[a],a))[0];correct+=pred==labels[i]
        records[name].update(leave_one_code_out_covered=seen,leave_one_code_out_correct=correct)
    out={'seed':4692026,'codes':len(codes),'candidate_count':len(fs),'features':records,
         'null':{'kind':'Shuffle label assignments across the99 codes; preserves exact label multiplicities; reselect maximum accuracy across all features',
                 'replicates':999,'observed_best':best,'mean_best':sum(null)/len(null),'max_best':max(null),
                 'p_upper':(1+sum(s>=best for s in null))/1000},
         'interpretation':'Low mismatch counts describe structure of an imported code table, not English. Any exact feature-only map is refuted when mismatches>0. No probabilistic model or multiple-stage decoder is excluded.',
         'limitations':['Imported code map learned from full public corpus; no external label ground truth.',
           'Unordered-pair feature encodes a large near-identity table; it is a high-capacity symmetry test, not a short cipher algorithm.',
           'Permutation tests here concern table-label geometry, not evidence of authorship or translation.']}
    (ROOT/'results/map_geometry.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'candidate_count':len(fs),'best':sorted(records.items(),key=lambda r:r[1]['majority_accuracy_all_codes'],reverse=True)[:4],'null':out['null']},indent=2))
if __name__=='__main__':main()
