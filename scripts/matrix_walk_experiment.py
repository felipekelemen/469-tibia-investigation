#!/usr/bin/env python3
"""Frozen small position-ranking family. Exploratory, no semantic promotion."""
import hashlib,json,pathlib,random,time
import numpy as np
from cipher_battery import english_model,score
from matrix_experiments import MATRICES
from residual_channel import shuffle_within_symbol
ROOT=pathlib.Path(__file__).resolve().parents[1]
SEED=7346926

def scan_order(g):
    out=[]
    for i in range(16):
        r,c=divmod(i,4)
        if g>=4:c=3-c
        for _ in range(g%4):r,c=c,3-r
        out.append(4*r+c)
    return out

def block_order(matrix,g,descending):
    m=MATRICES[matrix];scan=scan_order(g)
    return sorted(scan,key=lambda i:(-1 if descending else 1)*m[i//4][i%4])

def permute(seq,order,inverse=False):
    a=np.asarray(seq,dtype=np.int64);out=a.copy();order=np.asarray(order)
    if inverse:order=np.argsort(order)
    n=len(a)//16*16
    if n:out[:n]=a[:n].reshape(-1,16)[:,order].reshape(-1)
    return out

def configs():
    return [(m,g,d,inv,rep) for m in ['old','new'] for g in range(8) for d in [False,True] for inv in [False,True] for rep in ['symbols','codes','codes_minus1']]

def reprs(books):
    return [{'id':b['id'],'symbols':np.asarray([ord(c)-65 if c!='*' else 26 for c in b['symbols']])%26,
             'codes':np.asarray([int(c) for c in b['codes']])%26,
             'codes_minus1':(np.asarray([int(c) for c in b['codes']])-1)%26} for b in books]

def mean_score(books,c,table):
    m,g,d,inv,rep=c;order=block_order(m,g,d);total=0;count=0
    for b in books:
        n=max(0,len(b[rep])-3)
        if n:total+=score(permute(b[rep],order,inv),table)*n;count+=n
    return total/count

def fit(train,hold,table):
    best=max(configs(),key=lambda c:mean_score(train,c,table))
    return {'config':best,'train_score':mean_score(train,best,table),'holdout_score':mean_score(hold,best,table)}

def block_null(books,rng):
    out=[]
    for b in books:
        # One common code-position permutation per book preserves linkage of representations.
        n=len(b['codes']);blocks=[list(range(i,min(i+8,n))) for i in range(0,n,8)]
        rng.shuffle(blocks);ix=[i for bl in blocks for i in bl]
        out.append({'id':b['id'],'codes':[b['codes'][i] for i in ix], 'symbols':''.join(b['symbols'][i] for i in ix)})
    return out

def main():
    start=time.monotonic();protocol=ROOT/'data/protocols/matrix_walk_v1.json';frozen=json.loads(protocol.read_text())
    books=json.loads((ROOT/'data/normalized_books.json').read_text());split=json.loads((ROOT/'data/normalized_splits.json').read_text())
    tr=[b for b in books if b['id'] in split['discovery_book_ids']];ho=[b for b in books if b['id'] in split['holdout_book_ids']]
    table,positive=english_model(ROOT/'data/english_reference/alice.txt');observed=fit(reprs(tr),reprs(ho),table)
    controls={}
    for mode in frozen['nulls']:
        vals=[]
        for i in range(frozen['nulls'][mode]):
            rng=random.Random(SEED+i+(0 if mode=='block8' else 10000))
            f=block_null if mode=='block8' else shuffle_within_symbol
            vals.append(fit(reprs(f(tr,rng)),reprs(f(ho,rng)),table))
        controls[mode]={'trials':vals,'holdout_upper_tail_p':(1+sum(v['holdout_score']>=observed['holdout_score'] for v in vals))/(1+len(vals))}
    # Known-permutation positive: encrypt outside model-fitting English; solve ONLY on training then test.
    plain=np.asarray([ord(c)-65 for c in positive[:6500]])
    truecfg=('old',3,False,False,'symbols');order=block_order(*truecfg[:3])
    # Keep source train/hold separate before encryption to avoid crossing boundary effects.
    ptrain=plain[:5500];ptest=plain[5500:];ctrain=permute(ptrain,order,True);ctest=permute(ptest,order,True)
    a=[{'id':'positive_train',**{k:ctrain for k in ['symbols','codes','codes_minus1']}}]
    b=[{'id':'positive_hold',**{k:ctest for k in ['symbols','codes','codes_minus1']}}]
    pos=fit(a,b,table);cfg=pos['config'];pred=permute(ctest,block_order(*cfg[:3]),cfg[3])
    pos.update({'holdout_characters':len(ptest),'character_accuracy':float(np.mean(pred==ptest)),
      'known_key_roundtrip':bool(np.array_equal(permute(ctest,order),ptest)),
      'warning':'Controlled family-member positive only, no arbitrary-key transposition power claim.'})
    c=observed['config'];out={'protocol':frozen,'protocol_sha256':hashlib.sha256(protocol.read_bytes()).hexdigest(),'seed':SEED,'candidate_count':len(configs()),'observed':observed,'controls':controls,'positive':pos,
      'literal_holdout':[{'id':b['id'],'output':''.join(chr(int(x)+65) for x in permute(b[c[4]],block_order(*c[:3]),c[3]))} for b in reprs(ho)],
      'runtime_seconds':time.monotonic()-start,'verdict':'NO_VERIFIED_TRANSLATION',
      'limits':['Existing public corpus and tiny dependent holdout are already exposed; no prospective confirmation.',
        'A ranking of skull counts as positions is a conjecture, not an attested key.',
        'Conditional null leaves every symbols representation unchanged, so not all candidate families have variation in that null.',
        '192 finite variants only; mod26 projection loses code information; symbol labels carry no established meaning.',
        'One synthetic family positive is not the homophonic P02 qualification gate.']}
    (ROOT/'results/matrix_walk.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'observed':observed,'p':{k:v['holdout_upper_tail_p'] for k,v in controls.items()},'positive':pos,'runtime':out['runtime_seconds']},indent=2))
if __name__=='__main__':main()
