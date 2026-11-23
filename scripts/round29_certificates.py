#!/usr/bin/env python3
"""Pure-Python forward DP verifies all selected descriptions, not optimal selection."""
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def gamma(n):
    return 2*n.bit_length()-1


def score(raw,family,key,base,copied,language,numeric,dictionary):
    pairs=[int(raw[i:i+2]) for i in range(0,len(raw)-1,2)]
    def digit_cost(i):
        value=int(raw[i])
        if base=='uniform':return math.log2(10)
        if base=='iid':counts=numeric['counts']
        elif i==0:counts=numeric['starts']
        else:counts=numeric['transitions'][int(raw[i-1])]
        return -math.log2((counts[value]+.5)/(sum(counts)+5))
    costs=[]
    for i,value in enumerate(pairs):
        if family=='N':costs.append(digit_cost(2*i)+digit_cost(2*i+1));continue
        if value>=26:costs.append(-math.log2(1/16/74));continue
        a,b=key;letter=(a*value+b)%26
        counts=language['bigram'][(a*pairs[i-1]+b)%26] if i and pairs[i-1]<26 else language['unigram']
        costs.append(-math.log2((15/16)*(counts[letter]+.5)/(sum(counts)+13)))
    if copied:
        lengths=[len(s)//2 for s in dictionary]
        reference=1+(math.ceil(math.log2(len(dictionary))) if len(dictionary)>1 else 0)
        dp=[math.inf]*(len(pairs)+1);dp[0]=0
        for i in range(len(pairs)):
            dp[i+1]=min(dp[i+1],dp[i]+1+costs[i])
            for entry,n in zip(dictionary,lengths):
                if raw.startswith(entry,2*i):dp[i+n]=min(dp[i+n],dp[i]+reference)
        cost=dp[-1]
    else:cost=sum(costs)
    if len(raw)%2:cost+=math.log2(10) if family=='T' else digit_cost(len(raw)-1)
    return gamma(len(raw)+1)+2+cost


def verify(qualification,fixtures,language):
    lookup={c['replicate']:c for c in fixtures['cases']};maximum=0.;documents=0
    program=sum(gamma((ROOT/p).stat().st_size+1)+8*(ROOT/p).stat().st_size for p in
                ['scripts/round29_models.py','scripts/generative_comparison.py'])
    for row in qualification['rows']:
        sequences=lookup[row['replicate']]['datasets'][row['profile']]
        result=row['comparison'];selected=result['selected'];numeric=result['numeric_parameters'];dictionary=result['dictionary']
        dcost=gamma(len(dictionary)+1)+sum(gamma(len(s)//2)+7*(len(s)//2) for s in dictionary)
        assert dcost==result['dictionary_bits']
        e=language['parameter_bits'];t=selected['T'];n=selected['N'];m=selected['M']
        ncost={'uniform':0,'iid':sum(gamma(v+1) for v in numeric['counts']),
               'markov1':sum(gamma(v+1) for v in numeric['starts'])+sum(gamma(v+1) for r in numeric['transitions'] for v in r)}
        headers={'T':12+e+(dcost if t['copy'] else 0),
                 'N':5+ncost[n['base']]+(dcost if n['copy'] else 0),
                 'M':15+e+ncost[m['numeric_base']]+(dcost if m['text_copy'] or m['numeric_copy'] else 0)}
        for family in 'TNM':
            assert headers[family]==result['models'][family]['parameter_and_selector_bits']
            assert program+gamma(51)+gamma(21)==result['models'][family]['common_program_and_count_bits']
        for i,s in enumerate(sequences):
            tv=score(s,'T',t['key'],None,t['copy'],language,numeric,dictionary)
            nv=score(s,'N',None,n['base'],n['copy'],language,numeric,dictionary)
            mt=score(s,'T',m['key'],None,m['text_copy'],language,numeric,dictionary)
            mn=score(s,'N',None,m['numeric_base'],m['numeric_copy'],language,numeric,dictionary)
            for family,value in [('T',tv),('N',nv),('M',1+min(mt,mn))]:
                error=abs(value-result['models'][family]['per_document_bits'][i]);maximum=max(maximum,error)
                assert error<1e-8,(row['replicate'],row['profile'],i,family,error)
            documents+=1
    return {'selected_model_documents_checked':documents,'model_document_lengths_checked':3*documents,
            'max_absolute_bit_difference':maximum,'all_within_tolerance':True,
            'tolerance_bits':1e-8,'method':'Independent scalar probabilities and forward DP vs vectorized backward DP. Verifies selected codes/headers, not all fitted choices or semantic origin.'}


if __name__=='__main__':
    from round29_experiment import verify_inputs
    verify_inputs()
    load=lambda p:json.loads((ROOT/p).read_text())
    result=verify(load('results/round29_qualification.json'),load('data/round29_fixtures.json'),load('data/round29_english_model.json'))
    path=ROOT/'results/round29_certificates.json'
    if path.exists():raise ValueError('Refuse to replace certificates')
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
