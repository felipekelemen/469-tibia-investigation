#!/usr/bin/env python3
"""Finite periodic decimal-key constraints with optional ciphertext feedback."""
from collections import defaultdict
from functools import lru_cache
from itertools import product
import numpy as np
from target_decimal_solver import encode

CODECS=('ordinal0_compact','ordinal1_compact','ascii_lower_compact')


def merge(a,b):
    if any(x>=0 and y>=0 and x!=y for x,y in zip(a,b)):
        return None
    return tuple(max(x,y) for x,y in zip(a,b))


def positions(groups):
    offset=0; previous=0; out=[]
    for raw in groups:
        out.append((offset,previous)); offset+=len(raw); previous=int(raw[-1])
    return out


class Codebook:
    def __init__(self,words,codec):
        self.codec=codec; self.reverse=defaultdict(list); bylen=defaultdict(list)
        for word in sorted(set(words)):
            raw=encode(word,codec); self.reverse[raw].append(word)
        for raw in self.reverse:
            bylen[len(raw)].append([int(c) for c in raw])
        self.arrays={n:np.array(v,dtype=np.int16) for n,v in bylen.items()}
        self.lengths=sorted(bylen)

    @lru_cache(maxsize=8192)
    def constraints(self,raw,period):
        values=self.arrays.get(len(raw))
        if values is None: return ()
        delta=(np.array([int(c) for c in raw],dtype=np.int16)-values)%10
        valid=np.ones(len(delta),dtype=bool)
        for j in range(period,len(raw)):
            valid &= delta[:,j]==delta[:,j%period]
        chosen=delta[valid,:min(period,len(raw))]
        if not len(chosen): return ()
        keys=np.full((len(chosen),period),-1,dtype=np.int16)
        keys[:,:chosen.shape[1]]=chosen
        return tuple(tuple(map(int,r)) for r in np.unique(keys,axis=0))


class Model:
    def __init__(self,book,period,reset,feedback):
        if not 1<=period<=8 or reset not in ('word','stream') or feedback not in (0,1):
            raise ValueError('invalid declared model')
        self.book=book; self.period=period; self.reset=reset; self.feedback=feedback
        self.name=f'{book.codec}/p{period}/{reset}/feedback{feedback}'

    def prepare(self,raw,offset=0,previous=0):
        if not raw or not raw.isascii() or not raw.isdigit(): raise ValueError('decimal digits required')
        if self.reset=='word': offset=0; previous=0
        result=[]
        for char in raw:
            current=int(char); result.append(str((current-self.feedback*previous)%10)); previous=current
        return ''.join(result),offset%self.period

    def domain(self,raw,offset=0,previous=0):
        adjusted,phase=self.prepare(raw,offset,previous)
        result=[]
        for key in self.book.constraints(adjusted,self.period):
            rotated=[-1]*self.period
            for i,v in enumerate(key): rotated[(i+phase)%self.period]=v
            result.append(tuple(rotated))
        return sorted(result)

    def decrypt_digits(self,raw,key,offset=0,previous=0):
        if len(key)!=self.period or any(v<0 for v in key): raise ValueError('complete key required')
        adjusted,phase=self.prepare(raw,offset,previous)
        return ''.join(str((int(c)-key[(i+phase)%self.period])%10) for i,c in enumerate(adjusted))

    def words(self,raw,key,offset=0,previous=0):
        return self.book.reverse.get(self.decrypt_digits(raw,key,offset,previous),[])

    def encrypt(self,words,key):
        result=[]; offset=0; previous=0
        for word in words:
            if self.reset=='word': offset=0; previous=0
            raw=''
            for c in encode(word,self.book.codec):
                value=(int(c)+key[offset%self.period]+self.feedback*previous)%10
                raw+=str(value); previous=value; offset+=1
            result.append(raw)
        return result

    def solve(self,groups,node_limit=20000,solution_limit=2000):
        if not groups: raise ValueError('groups required')
        contexts=positions(groups)
        domains=[self.domain(raw,*ctx) for raw,ctx in zip(groups,contexts)]
        domains=sorted(set(tuple(d) for d in domains),key=lambda d:(len(d),d))
        found=set(); seen=set(); nodes=0; capped=False
        def visit(key):
            nonlocal nodes,capped
            if key in seen or capped:return
            if nodes>=node_limit or len(found)>=solution_limit: capped=True; return
            seen.add(key); nodes+=1; unresolved=[]
            for domain in domains:
                allowed={m for d in domain if (m:=merge(key,d)) is not None}
                if not allowed:return
                if key not in allowed: unresolved.append(allowed)
            if not unresolved: found.add(key); return
            for child in sorted(min(unresolved,key=lambda x:(len(x),sorted(x)))): visit(child)
        visit((-1,)*self.period)
        return summary(found,nodes,capped)

    def segment(self,raw,key,offset=0,previous=0):
        counts=[0]*(len(raw)+1); counts[0]=1; samples=[None]*(len(raw)+1); samples[0]=[]
        for i in range(len(raw)):
            if not counts[i]:continue
            for n in self.book.lengths:
                if i+n>len(raw):break
                candidates=self.words(raw[i:i+n],key,offset+i,int(raw[i-1]) if i else previous)
                if candidates:
                    counts[i+n]+=counts[i]*len(candidates)
                    if samples[i+n] is None:samples[i+n]=samples[i]+[candidates[0]]
        return {'word_path_count':counts[-1], 'unique_words':samples[-1] if counts[-1]==1 else None}

    def solve_unspaced(self,groups,node_limit=20000,solution_limit=2000):
        if not groups:raise ValueError('groups required')
        contexts=positions(groups); domains={}
        for gi,raw in enumerate(groups):
            for pos in range(len(raw)):
                offset=contexts[gi][0]+pos; previous=int(raw[pos-1]) if pos else contexts[gi][1]
                domains[gi,pos]=[(end,d) for end in range(pos+1,len(raw)+1)
                                 for d in self.domain(raw[pos:end],offset,previous)]
        seen=set(); found=set(); nodes=0; capped=False
        def visit(gi,pos,key):
            nonlocal nodes,capped
            state=(gi,pos,key)
            if state in seen or capped:return
            if nodes>=node_limit or len(found)>=solution_limit:capped=True;return
            seen.add(state);nodes+=1
            if gi==len(groups):found.add(key);return
            if pos==len(groups[gi]):visit(gi+1,0,key);return
            if -1 not in key:
                remaining=[(groups[gi][pos:],contexts[gi][0]+pos,int(groups[gi][pos-1]) if pos else contexts[gi][1])]
                remaining += [(groups[j],*contexts[j]) for j in range(gi+1,len(groups))]
                if all(self.segment(g,key,off,prev)['word_path_count'] for g,off,prev in remaining): found.add(key)
                return
            for end,d in domains[gi,pos]:
                new=merge(key,d)
                if new is not None:visit(gi,end,new)
        visit(0,0,(-1,)*self.period)
        return summary(found,nodes,capped)


def summary(keys,nodes,capped):
    return {'complete':not capped,'nodes':nodes,'keys':[list(k) for k in sorted(keys)],
            'full_key_count':sum(10**k.count(-1) for k in keys)}


def completions(result,limit=2000):
    if not result['complete'] or result['full_key_count']>limit:return None
    out=[]
    for key in result['keys']:
        holes=[i for i,v in enumerate(key) if v<0]
        for fill in product(range(10),repeat=len(holes)):
            new=key[:]
            for i,v in zip(holes,fill):new[i]=v
            out.append(tuple(new))
    return out


def catalog(words):
    books={f:Codebook(words,f) for f in CODECS}
    return {m.name:m for book in books.values() for p in range(1,9) for reset in ('word','stream') for fb in (0,1)
            for m in [Model(book,p,reset,fb)]}
