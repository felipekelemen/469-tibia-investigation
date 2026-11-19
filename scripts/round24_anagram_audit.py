#!/usr/bin/env python3
"""Audit a public Avar/Knightmare anagram claim; no English labels inferred."""
from collections import Counter
from pathlib import Path
from math import comb,prod,sqrt
import argparse,hashlib,json,random,re
ROOT=Path(__file__).resolve().parents[1]

def sig(w):return ''.join(sorted(w))
def bag_probability(pool,word):
    counts=Counter(pool);wanted=Counter(word)
    if len(word)>len(pool) or any(counts[d]<n for d,n in wanted.items()):return 0.0
    return prod(comb(counts[d],n) for d,n in wanted.items())/comb(len(pool),len(word))
def adjacent_probability(pool,first,second):
    p=bag_probability(pool,first);remaining=list(pool)
    if p==0:return 0.0
    for c in first:remaining.remove(c)
    return p*bag_probability(remaining,second)
def statistics(words,knight):
    signatures=[sig(w) for w in words];present=set(signatures)
    return {'named_pair_anywhere':int(sig('3478') in present and sig('345') in present),
            'all_knight_signatures':len({sig(w) for w in knight if len(w)>=3}&present),
            'named_pair_adjacent':int(any(a==sig('3478') and b==sig('345') for a,b in zip(signatures,signatures[1:])))}
def cut(chars,lengths):
    out=[];i=0
    for n in lengths:out.append(''.join(chars[i:i+n]));i+=n
    assert i==len(chars)
    return out

def run():
    p=json.loads((ROOT/'data/round24_anagram_protocol.json').read_text())
    inventory={r['id']:r['text'] for r in json.loads((ROOT/'data/source_validation_inventory.json').read_text())}
    avar=re.findall(r'\d+',inventory['avar_tar_poem']);knight=re.findall(r'\d+',inventory['knightmare_2012'])
    observed=statistics(avar,knight);pool=list(''.join(avar));lengths=list(map(len,avar))
    unique=list(dict.fromkeys(avar));unique_pool=list(''.join(unique));unique_lengths=list(map(len,unique))
    matches=[{'avar_group_index':i,'avar':a,'knightmare':k} for i,a in enumerate(avar) for k in knight if len(k)>=3 and sig(a)==sig(k)]
    counts=Counter(pool)
    analytic={k:{'eligible_positions':sum(len(w)==len(k) for w in avar),'one_position_probability':bag_probability(pool,k),'expected_matching_positions':sum(len(w)==len(k) for w in avar)*bag_probability(pool,k)} for k in ('3478','345')}
    adjacent_positions=[i for i,(a,b) in enumerate(zip(avar,avar[1:])) if (len(a),len(b))==(4,3)]
    fixed_adj=adjacent_probability(pool,'3478','345')
    output={'protocol_sha256':hashlib.sha256((ROOT/'data/round24_anagram_protocol.json').read_bytes()).hexdigest(),'observed':observed,'matches':matches,'analytic_pooled_occurrences':{'named_words':analytic,'adjacent_eligible_positions':adjacent_positions,'probability_for_one_fixed_disjoint_pair':fixed_adj,'any_adjacent_probability_if_one_eligible_position':fixed_adj if len(adjacent_positions)==1 else None},'nulls':{}}
    for offset,kind in enumerate(('pooled_occurrences','pooled_unique_words','digit_relabel')):
        rng=random.Random(p['seed']+offset);tails=Counter();hist=Counter()
        for _ in range(p['trials_per_null']):
            if kind=='pooled_occurrences':
                arr=pool.copy();rng.shuffle(arr);words=cut(arr,lengths)
            elif kind=='pooled_unique_words':
                arr=unique_pool.copy();rng.shuffle(arr);mapping=dict(zip(unique,cut(arr,unique_lengths)));words=[mapping[w] for w in avar]
            else:
                arr=list('0123456789');rng.shuffle(arr);table=str.maketrans('0123456789',''.join(arr));words=[w.translate(table) for w in avar]
            stats=statistics(words,knight);hist[stats['all_knight_signatures']]+=1
            for name,value in stats.items():tails[name]+=int(value>=observed[name])
        output['nulls'][kind]={'trials':p['trials_per_null'],'tail_counts':dict(tails),'monte_carlo_plus_one_tail':{name:(tails[name]+1)/(p['trials_per_null']+1) for name in observed},'all_match_histogram':dict(sorted(hist.items()))}
        print(kind,output['nulls'][kind],flush=True)
    rng=random.Random(p['seed']+3)
    for _ in range(30):
        words=[]
        for w in avar:
            chars=list(w);rng.shuffle(chars);words.append(''.join(chars))
        assert statistics(words,knight)==observed
    output['within_word_invariant']={'checked_fixtures':30,'analytic_reason':'sorting a word is unchanged by a permutation of its characters','tail_probability':1.0,'informative_null':False}
    output['translation_validated']=False
    return output
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();out=run();path=ROOT/'results/round24_anagram.json'
    if args.check:assert json.loads(path.read_text())==json.loads(json.dumps(out)), 'replay mismatch'
    else:path.write_text(json.dumps(out,indent=2)+'\n')
