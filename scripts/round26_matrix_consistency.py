#!/usr/bin/env python3
"""Conditional cross-key consistency, not a plaintext decoder or historical proof."""
from collections import Counter
from itertools import permutations, product
from math import gcd
from pathlib import Path
import argparse, hashlib, json, random, re
from matrix_experiments import inverse, transpose

ROOT=Path(__file__).resolve().parents[1]


def determinant_permutations(matrix):
    n=len(matrix); total=0
    for p in permutations(range(n)):
        sign=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        value=sign
        for i,j in enumerate(p):value*=matrix[i][j]
        total+=value
    return total


def mv(matrix,vector,modulus):
    return tuple(sum(a*b for a,b in zip(row,vector))%modulus for row in matrix)


def mm(left,right,modulus):
    return [[sum(left[i][k]*right[k][j] for k in range(len(right)))%modulus
             for j in range(len(right[0]))] for i in range(len(left))]


def later_matrix(x=6,y=6):
    return [[1,1,1,1],[1,3,x,1],[1,1,4,1],[4,y,1,1]]


def difference(a,b):
    return [[x-y for x,y in zip(ra,rb)] for ra,rb in zip(a,b)]


def analytic_kernel(modulus,orientation,x=6,y=6):
    """Solve Dv=0 by triangular equations; row convention solves D^T v=0."""
    output=set()
    for s in range(modulus):
        if 2*s%modulus:continue
        for t in range(modulus):
            if orientation=='column':v=(s,0,0,t)
            elif orientation=='row_as_transpose':
                second=(6-y)*t%modulus
                v=(s,second,(5*s+(1-x)*second)%modulus,t)
            else:raise ValueError(orientation)
            output.add(v)
    return output


def encode(values,matrix,modulus):
    if len(values)%len(matrix):raise ValueError('complete blocks required')
    return [v for i in range(0,len(values),len(matrix)) for v in mv(matrix,values[i:i+len(matrix)],modulus)]


def brute_kernel(matrix,modulus):
    return {v for v in product(range(modulus),repeat=len(matrix)) if not any(mv(matrix,v,modulus))}


def synthetic_controls(protocol,old,new):
    rng=random.Random(protocol['seed']); text=re.sub('[^A-Z]','',(ROOT/'data/english_reference/alice.txt').read_text().upper())
    cases=[]
    for modulus in protocol['moduli']:
        alphabet='ABCDEFGHIKLMNOPQRSTUVWXYZ' if modulus==25 else 'ABCDEFGHIJKLMNOPQRSTUVWXYZ .?'
        plain=text.replace('J','I') if modulus==25 else text
        for trial in range(30):
            attempts=0
            while True:
                attempts+=1
                if attempts>10000:raise RuntimeError('control budget exceeded')
                aflat=sum(old,[]).copy();rng.shuffle(aflat);a=[aflat[i:i+4] for i in range(0,16,4)]
                ai=inverse(a,modulus)
                if ai is not None:break
            bflat=sum(new,[]).copy();rng.shuffle(bflat);b=[bflat[i:i+4] for i in range(0,16,4)]
            assert Counter(sum(a,[]))==Counter(sum(old,[])) and Counter(sum(b,[]))==Counter(sum(new,[]))
            start=rng.randrange(len(plain)-200); values=[alphabet.index(c) for c in plain[start:start+200]]
            relation=mm(b,ai,modulus);cold=encode(values,a,modulus);cnew=encode(values,b,modulus)
            predicted=encode(cold,relation,modulus);assert predicted==cnew
            corrupt=cnew.copy();corrupt[0]=(corrupt[0]+1)%modulus;assert predicted!=corrupt
            canonical=[]
            for orientation in protocol['orientations']:
                aa,bb=(old,new) if orientation=='column' else (transpose(old),transpose(new))
                cc=mm(bb,inverse(aa,modulus),modulus)
                assert encode(encode(values,aa,modulus),cc,modulus)==encode(values,bb,modulus)
                canonical.append(orientation)
            cases.append({'modulus':modulus,'trial':trial,'draws_until_old_invertible':attempts,
                          'old_control':a,'later_control':b,'plaintext_offset':start,'plaintext_length':len(values),
                          'english_sha256':hashlib.sha256(plain[start:start+200].encode()).hexdigest(),
                          'changed_ciphertext_prediction_exact':True,'perturbed_output_rejected':True,
                          'canonical_orientations_exact':canonical})
    return cases


def run():
    p=json.loads((ROOT/'data/round26_protocol.json').read_text()); matrices=p['matrix_inputs'];a=matrices['old'];b=matrices['later']
    out={'determinants':{k:determinant_permutations(v) for k,v in matrices.items() if v is not None},
         'physical5_authenticated':False,'difference':difference(a,b),'algebra':[],'small_exhaustive_checks':[],'corpus_diagnostics':[]}
    for m in range(2,8):
        for x,y in ((6,6),(5,5),(0,9),(9,0)):
            d=difference(a,later_matrix(x,y))
            for orientation in p['orientations']:
                operator=d if orientation=='column' else transpose(d)
                expected=analytic_kernel(m,orientation,x,y);actual=brute_kernel(operator,m)
                assert actual==expected and len(actual)==m*gcd(2,m)
                out['small_exhaustive_checks'].append({'modulus':m,'x':x,'y':y,'orientation':orientation,
                                                       'vectors_checked':m**4,'kernel_size':len(actual),'exact':True})
    books=json.loads((ROOT/'data/normalized_books.json').read_text())
    for m in p['moduli']:
        for orientation in p['orientations']:
            aa,bb=(a,b) if orientation=='column' else (transpose(a),transpose(b))
            ai=inverse(aa,m);assert ai is not None
            relation=mm(bb,ai,m);kernel=analytic_kernel(m,orientation)
            outputs={mv(aa,v,m) for v in kernel};assert len(outputs)==len(kernel)
            for v in kernel:assert mv(aa,v,m)==mv(bb,v,m)
            out['algebra'].append({'modulus':m,'orientation':orientation,'old_invertible':True,
                                    'later_invertible':inverse(bb,m) is not None,'cross_key_ciphertext_operator':relation,
                                    'unchanged_plaintext_vectors':len(kernel),'unchanged_ciphertext_vectors':len(outputs),
                                    'domain_vectors':m**4,'uniform_domain_fraction':len(outputs)/m**4})
            for representation in ('raw_pairs','imported_codes'):
                rows=[]
                for book in books:
                    if representation=='raw_pairs':
                        raw=book['digits']; values=[int(raw[i:i+2])%m for i in range(0,len(raw)-1,2)];digit_tail=raw[-1:] if len(raw)%2 else ''
                    else:values=[int(c)%m for c in book['codes']];digit_tail=None
                    blocks=[tuple(values[i:i+4]) for i in range(0,len(values)-3,4)]
                    compatible=[v in outputs for v in blocks]
                    # Independently check the ciphertext update operator rather than plaintext enumeration.
                    assert compatible==[mv(relation,v,m)==v for v in blocks]
                    bad=next((i for i,v in enumerate(compatible) if not v),None)
                    rows.append({'id':book['id'],'complete_blocks':len(blocks),'compatible_blocks':sum(compatible),
                                 'all_complete_blocks_compatible':bool(blocks) and all(compatible),
                                 'first_incompatible_block':None if bad is None else {'index':bad,'values':list(blocks[bad]),'predicted_after_key_change':list(mv(relation,blocks[bad],m))},
                                 'unprocessed_value_tail':values[len(blocks)*4:],'unprocessed_raw_digit_tail':digit_tail})
                out['corpus_diagnostics'].append({'modulus':m,'orientation':orientation,'representation':representation,
                    'complete_blocks':sum(r['complete_blocks'] for r in rows),'compatible_blocks':sum(r['compatible_blocks'] for r in rows),
                    'books_all_complete_blocks_compatible':sum(r['all_complete_blocks_compatible'] for r in rows),'books':rows})
    out['synthetic_controls']=synthetic_controls(p,a,b)
    out['translation_validated']=False
    out['interpretation']='A conditional same-plaintext/same-ciphertext Hill model has strong constraints. No paired historical book versions authenticated; current-corpus incompatibility does not prove actual matrix changes were unrelated to encryption.'
    return out


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();output=run()
    path=ROOT/'results/round26_matrix_consistency.json'
    if args.check:assert json.loads(path.read_text())==output,'replay mismatch'
    else:path.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'determinants':output['determinants'],'small_exhaustive_checks':len(output['small_exhaustive_checks']),
                      'synthetic_cases':len(output['synthetic_controls']),'diagnostics':[{k:v for k,v in r.items() if k!='books'} for r in output['corpus_diagnostics']]},indent=2))
