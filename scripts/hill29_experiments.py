#!/usr/bin/env python3
"""Bounded Hill mod29 screening with a frozen external English 29-gram model."""
import argparse, collections, hashlib, json, math, pathlib, random, re
import numpy as np
from matrix_experiments import MATRICES, inverse, transpose
ROOT=pathlib.Path(__file__).resolve().parents[1]
ALPHABET='ABCDEFGHIJKLMNOPQRSTUVWXYZ .?'
SEED=290469

def normalize_english(raw):
    if '*** START OF THE PROJECT GUTENBERG EBOOK' in raw:
        raw=raw.split('*** START OF THE PROJECT GUTENBERG EBOOK',1)[1].split('***',1)[1]
    raw=raw.split('*** END OF THE PROJECT GUTENBERG EBOOK',1)[0]
    return re.sub(r' +',' ',re.sub('[^A-Z .?]',' ',raw.upper())).strip()

def encode(text):return np.array([ALPHABET.index(c) for c in text],dtype=np.int64)
def render(seq):return ''.join(ALPHABET[int(i)] for i in seq)

def english_model29(path):
    text=normalize_english(path.read_text(encoding='utf-8-sig'))
    cut=int(len(text)*.8);train=text[:cut];positive=text[cut:]
    counts=collections.Counter(train[i:i+4] for i in range(len(train)-3))
    denom=sum(counts.values())+.01*29**4
    table=np.full(29**4,math.log10(.01/denom))
    for k,n in counts.items():
        x=[ALPHABET.index(c) for c in k]
        table[((x[0]*29+x[1])*29+x[2])*29+x[3]]=math.log10((n+.01)/denom)
    return table,positive

def score29(seq,table):
    x=np.asarray(seq,dtype=np.int64)
    if len(x)<4:return float('-inf')
    return float(np.mean(table[((x[:-3]*29+x[1:-2])*29+x[2:-1])*29+x[3:]]))

def transform29(values,operator,preserve_tail=False):
    values=np.asarray(values,dtype=np.int64)%29
    n=len(values)//4*4
    out=(values[:n].reshape(-1,4)@np.asarray(operator,dtype=np.int64).T)%29
    flat=out.reshape(-1)
    return np.concatenate([flat,values[n:]]) if preserve_tail else flat

def candidates():
    out=[]
    for name,matrix in MATRICES.items():
        for orientation,mat in [('column',matrix),('row',transpose(matrix))]:
            for direction,op in [('forward',mat),('inverse',inverse(mat,29))]:
                for layer in ['digits1','digits2_offset0','digits2_offset1','codes','symbols']:
                    for base in [0,1]:
                        for offset in range(4):
                            out.append({'matrix':name,'orientation':orientation,'direction':direction,'layer':layer,'input_base':base,'symbol_offset':offset,'operator':op})
    return out

def records(books):
    out=[]
    for b in books:
        d=b['digits'];out.append({'id':b['id'],
          'digits1':np.array([int(c) for c in d]),
          'digits2_offset0':np.array([int(d[i:i+2]) for i in range(0,len(d)-1,2)]),
          'digits2_offset1':np.array([int(d[i:i+2]) for i in range(1,len(d)-1,2)]),
          'codes':np.array([int(c) for c in b['codes']]),
          'symbols':np.array([ALPHABET.index(c) if c!='*' else 28 for c in b['symbols']])})
    return out

def apply_record(b,c):
    x=(b[c['layer']][c['symbol_offset']:]-c['input_base'])%29
    return transform29(x,c['operator'])

def corpus_score(books,c,table):
    total=0.;n=0
    for b in books:
        x=apply_record(b,c);w=len(x)-3
        if w>0:total+=score29(x,table)*w;n+=w
    return total/n if n else float('-inf')

def block_null(books,rng):
    """Per-layer block8 null; layers are not claimed to be joint generated data."""
    out=[]
    for b in books:
        row={'id':b['id']}
        for layer,x in b.items():
            if layer=='id':continue
            chunks=[x[i:i+8] for i in range(0,len(x),8)];rng.shuffle(chunks)
            row[layer]=np.concatenate(chunks)
        out.append(row)
    return out

def main(nulls=39):
    source=ROOT/'data/normalized_books.json';books=json.loads(source.read_text())
    splits=json.loads((ROOT/'data/normalized_splits.json').read_text());train_ids=set(splits['discovery_book_ids']);hold_ids=set(splits['holdout_book_ids'])
    train=records([b for b in books if b['id'] in train_ids]);hold=records([b for b in books if b['id'] in hold_ids])
    table,positive=english_model29(ROOT/'data/english_reference/alice.txt')
    cs=candidates();ranked=sorted([(corpus_score(train,c,table),c) for c in cs],key=lambda r:r[0],reverse=True)
    best=ranked[0][1];observed=corpus_score(hold,best,table);rng=random.Random(SEED)
    controls=[]
    for i in range(nulls):
        tr=block_null(train,rng);ho=block_null(hold,rng)
        score,c=max([(corpus_score(tr,k,table),k) for k in cs],key=lambda r:r[0])
        controls.append({'replicate':i,'train_max':score,'holdout_of_train_selected':corpus_score(ho,c,table),'candidate':{k:v for k,v in c.items() if k!='operator'}})
    plain=encode(positive[:257]);checks=[]
    for name,matrix in MATRICES.items():
        for orientation,op in [('column',matrix),('row',transpose(matrix))]:
            ciphertext=transform29(plain,op,True);restored=transform29(ciphertext,inverse(op,29),True)
            checks.append({'matrix':name,'orientation':orientation,'characters':len(plain),'encrypted_blocks':len(plain)//4,'unencrypted_tail':len(plain)%4,'exact_roundtrip':bool(np.array_equal(plain,restored))})
    positive_values=encode(positive);scrambled=positive_values.copy();np.random.default_rng(SEED).shuffle(scrambled)
    result={'seed':SEED,'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'alphabet':ALPHABET,'modulus':29,
      'model':{'type':'external English tetragrams over all29 output symbols, .01 additive smoothing; spaces/punctuation retained so punctuation cannot be dropped to improve score','source':'data/english_reference/alice.txt','source_sha256':hashlib.sha256((ROOT/'data/english_reference/alice.txt').read_bytes()).hexdigest(),'train_first_fraction':.8,'positive_last_fraction':.2,'minimum_window_log10':float(table.min()),'positive_control':score29(positive_values,table),'shuffled_positive_control':score29(scrambled,table)},
      'conventions':{'input_values':'all input values explicitly reduced mod29 after subtracting base0 or1; row0 letters A0 and mask*=28','offsets':'raw digit pairs offsets0/1 then block-symbol offsets0..3; restored codes and symbols offsets0..3; reset at each book','tail':'all incomplete blocks discarded in screening, no invented padding; positive roundtrip preserves trailing1..3 symbols unchanged, explicitly identified','scoring':'mean log10 tetragram probabilities, within books only, weighted by surviving window count; any space/period/question participates normally'},
      'split':{'train_ids':sorted(train_ids,key=int),'holdout_ids':sorted(hold_ids,key=int),'criterion':splits['criterion'],'holdout_codes':sum(len(b['codes']) for b in hold),'limitation':'Two correlated held-out books, one component; only61 codes, globally imported row0 representation not discovered independently.'},
      'candidate_count':len(cs),'best_train':{'score':ranked[0][0],'candidate':best},'holdout_of_train_selected':observed,'top10_train':[{'score':s,'candidate':c} for s,c in ranked[:10]],
      'holdout_output':[{'id':b['id'],'output':render(apply_record(b,best)),'symbols_used':len(apply_record(b,best))} for b in hold],
      'controls':{'type':'8-input-symbol block shuffle within books and layers, retaining within-block sequences, length and named-value counts; not a jointly consistent raw/code/symbol generative model','replicates':nulls,'selection':'Complete same candidate search in every control; select in train only, compare holdout score','trials':controls,'upper_tail_p':(1+sum(r['holdout_of_train_selected']>=observed for r in controls))/(nulls+1)},
      'positive_cipher_roundtrips':checks,'status':'NO_VERIFIED_TRANSLATION','limits':['Finite family only, no exhaustive rejection of matrices or multilayer ciphers.','29-symbol alphabet and row0 mask assignment are explicit hypotheses, not established meanings.','Scorer calibrated on literary English; coherent game English and official paired plaintext remain required.','Holdout tiny and correlated; p is descriptive of local-language score, never probability of translation.','Block shuffling retains local motifs but neither all long repeats nor exact bigram counts.']}
    (ROOT/'results/hill29.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'candidate_count':len(cs),'train':ranked[0][0],'holdout':observed,'p':result['controls']['upper_tail_p'],'positive':result['model']['positive_control'],'shuffled_positive':result['model']['shuffled_positive_control'],'all_roundtrips':all(c['exact_roundtrip'] for c in checks),'status':result['status']},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--nulls',type=int,default=39);a=p.parse_args();main(a.nulls)
