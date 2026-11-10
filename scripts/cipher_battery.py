#!/usr/bin/env python3
"""Finite exploratory cipher search. Scores are rankings, never translations."""
import argparse, collections, hashlib, itertools, json, math, pathlib, random, re
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
SEED=4693478

def english_model(path):
    raw=path.read_text(encoding='utf-8-sig')
    # Remove Gutenberg boilerplate, keep only letters, and freeze model before cipher search.
    if '*** START OF THE PROJECT GUTENBERG EBOOK' in raw:
        raw=raw.split('*** START OF THE PROJECT GUTENBERG EBOOK',1)[1].split('***',1)[1]
    raw=raw.split('*** END OF THE PROJECT GUTENBERG EBOOK',1)[0]
    text=re.sub('[^A-Z]','',raw.upper())
    cut=int(len(text)*.8); train=text[:cut]; positive=text[cut:]
    counts=collections.Counter(train[i:i+4] for i in range(len(train)-3))
    denom=sum(counts.values())+.01*26**4
    table=np.full(26**4,math.log10(.01/denom))
    for k,v in counts.items():
        x=[ord(c)-65 for c in k]; index=((x[0]*26+x[1])*26+x[2])*26+x[3]
        table[index]=math.log10((v+.01)/denom)
    return table,positive

def score(seq,table):
    if len(seq)<4:return float('-inf')
    seq=np.asarray(seq,dtype=np.int64)
    inds=((seq[:-3]*26+seq[1:-2])*26+seq[2:-1])*26+seq[3:]
    return float(np.mean(table[inds]))

def columnar_order(n,width):
    return [i for col in range(width) for i in range(col,n,width)]

def rail_order(n,rails):
    period=2*(rails-1)
    return sorted(range(n),key=lambda i:min(i%period,period-i%period))

def inverse_order(order):
    return np.argsort(order).tolist()

def make_candidates():
    candidates=[]
    for base in ['codes','digits','symbols']:
        for a in range(26):
            if math.gcd(a,26)==1:
                for b in range(26):candidates.append({'family':'affine','base':base,'a':a,'b':b})
        for word in ['469','3478','BEHOLDER','BONELORD']:
            key=[int(c) if c.isdigit() else ord(c)-65 for c in word]
            for sign in [-1,1]:candidates.append({'family':'vigenere','base':base,'key':key,'sign':sign})
        for width in range(2,17):
            for inverse in [False,True]:candidates.append({'family':'columnar','base':base,'width':width,'inverse':inverse})
        for rails in range(2,9):
            for inverse in [False,True]:candidates.append({'family':'rail','base':base,'rails':rails,'inverse':inverse})
    return candidates

def transform(seq,candidate):
    seq=np.asarray(seq,dtype=np.int64)%26
    family=candidate['family']
    if family=='affine':return (candidate['a']*seq+candidate['b'])%26
    if family=='vigenere':
        key=np.resize(candidate['key'],len(seq));return (seq+candidate['sign']*key)%26
    order=columnar_order(len(seq),candidate['width']) if family=='columnar' else rail_order(len(seq),candidate['rails'])
    if candidate['inverse']:order=inverse_order(order)
    return seq[order]

def records(books):
    out=[]
    for b in books:
        out.append({'id':b['id'],'codes':np.array([int(x) for x in b['codes']],dtype=np.int64),
                    'digits':np.array([int(c) for c in b['digits']],dtype=np.int64),
                    'symbols':np.array([ord(c)-65 if c!='*' else 26 for c in b['symbols']],dtype=np.int64)})
    return out

def corpus_score(books,candidate,table):
    sizes=[max(0,len(b[candidate['base']])-3) for b in books]
    return sum(score(transform(b[candidate['base']],candidate),table)*n for b,n in zip(books,sizes))/sum(sizes)

def shuffled(books,rng,mode):
    out=[]
    for b in books:
        r={'id':b['id']}
        for base in ['codes','digits','symbols']:
            x=b[base].tolist()
            if mode=='uniform':x=[rng.randrange(10 if base=='digits' else 100 if base=='codes' else 27) for _ in x]
            elif mode=='shuffle':rng.shuffle(x)
            elif mode=='blocks':
                parts=[x[i:i+8] for i in range(0,len(x),8)];rng.shuffle(parts);x=list(itertools.chain.from_iterable(parts))
            r[base]=np.asarray(x,dtype=np.int64)
        out.append(r)
    return out

def homophonic_anneal(books,holdout,table,rng,restarts=4,steps=5000):
    # Independent arbitrary code->letter mapping, fitted only on discovery books.
    seq=np.concatenate([b['codes'] for b in books]);edges=[];offset=0
    for b in books:
        edges.extend(range(offset,offset+len(b['codes'])-3));offset+=len(b['codes'])
    edges=np.array(edges); quad=seq[edges[:,None]+np.arange(4)]
    def objective(mapping):
        t=mapping[quad];return float(np.mean(table[((t[:,0]*26+t[:,1])*26+t[:,2])*26+t[:,3]]))
    best=-float('inf'); best_map=None
    for restart in range(restarts):
        mapping=np.array([rng.randrange(26) for _ in range(100)]);current=objective(mapping)
        for j in range(steps):
            idx=rng.randrange(100);old=mapping[idx];mapping[idx]=rng.randrange(26)
            proposed=objective(mapping);temperature=.12*(1-j/steps)+.001
            if proposed>=current or rng.random()<math.exp((proposed-current)/temperature):current=proposed
            else:mapping[idx]=old
            if current>best:best=current;best_map=mapping.copy()
    hscore=sum(score(best_map[b['codes']],table)*(len(b['codes'])-3) for b in holdout)/sum(len(b['codes'])-3 for b in holdout)
    return {'train_score':best,'holdout_score':hscore,'mapping':{f'{i:02d}':chr(int(v)+65) for i,v in enumerate(best_map)},
            'holdout_output':[{'id':b['id'],'output':''.join(chr(int(v)+65) for v in best_map[b['codes']])} for b in holdout],
            'restarts':restarts,'steps_each':steps,'warning':'Limited stochastic search, not an exhaustive homophonic attack. No optimizer-matched null calibration; output is not a translation.'}

def run(nulls):
    books=json.loads((ROOT/'data/normalized_books.json').read_text())
    splits=json.loads((ROOT/'data/normalized_splits.json').read_text())
    train_ids=set(splits['discovery_book_ids']);hold_ids=set(splits['holdout_book_ids'])
    train=records([b for b in books if b['id'] in train_ids]);hold=records([b for b in books if b['id'] in hold_ids])
    table,positive=english_model(ROOT/'data/english_reference/alice.txt'); rng=random.Random(SEED)
    candidates=make_candidates();ranked=sorted(((corpus_score(train,c,table),c) for c in candidates),key=lambda t:t[0],reverse=True)
    best=ranked[0][1];test_score=corpus_score(hold,best,table)
    controls={}
    for mode in ['uniform','shuffle','blocks']:
        trials=[]
        for _ in range(nulls):
            nt=shuffled(train,rng,mode);nh=shuffled(hold,rng,mode)
            nscore,nkey=max(((corpus_score(nt,c,table),c) for c in candidates),key=lambda t:t[0])
            trials.append({'train_best':nscore,'holdout_of_train_selected':corpus_score(nh,nkey,table)})
        vals=[x['holdout_of_train_selected'] for x in trials]
        controls[mode]={'replicates':nulls,'trials':trials,'holdout_mean':float(np.mean(vals)),'holdout_sd':float(np.std(vals)),
                        'empirical_upper_tail_p':(1+sum(x>=test_score for x in vals))/(nulls+1)}
    plain=np.array([ord(c)-65 for c in positive]);scrambled=plain.copy();np.random.default_rng(SEED).shuffle(scrambled)
    homo=homophonic_anneal(train,hold,table,rng)
    result={'seed':SEED,'numpy_version':np.__version__,'scorer':{'source':'https://www.gutenberg.org/cache/epub/11/pg11.txt','sha256':hashlib.sha256((ROOT/'data/english_reference/alice.txt').read_bytes()).hexdigest(),
          'model':'log10 tetragrams with .01 additive smoothing; first80% model, last20% positive control; A-Z only; averaged within books'},
          'split':{'train_ids':sorted(train_ids,key=int),'holdout_ids':sorted(hold_ids,key=int),'criterion':splits['criterion'],
                   'holdout_code_count':sum(len(b['codes']) for b in hold),'warning':'Tiny holdout, no verified plaintext, short/transformed repeats may remain; historical public exposure means not prospectively blind.'},
          'candidate_count':len(candidates),'best_train_candidate':best,'train_best':ranked[0][0],'holdout_of_train_selected':test_score,
          'top10_train':[{'score':s,'candidate':c} for s,c in ranked[:10]],'controls':controls,
          'positive_control_score':score(plain,table),'shuffled_positive_control_score':score(scrambled,table),'homophonic':homo,
          'selected_holdout_output':[{'id':b['id'],'output':''.join(chr(int(x)+65) for x in transform(b[best['base']],best))} for b in hold],
          'verdict':'NO_VERIFIED_TRANSLATION','limits':['Finite parameter grids only; no rejection of complete cipher families.','No paired game English ground truth.','English reference is literary English, not specifically Tibia language.','All interpretations of symbol letters are arbitrary; * maps to26 then mod26 in simple tests.','Control p values concern a scoring statistic only, with coarse resolution; no evidence of semantic accuracy.','Uniform, per-book per-layer symbol-shuffle and eight-symbol-block-shuffle nulls used. Block null retains within-block sequences but is not an exact bigram-preserving null.']}
    (ROOT/'results/cipher_battery.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['candidate_count','train_best','holdout_of_train_selected','positive_control_score','shuffled_positive_control_score','verdict']},indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--nulls',type=int,default=19);args=ap.parse_args();run(args.nulls)
