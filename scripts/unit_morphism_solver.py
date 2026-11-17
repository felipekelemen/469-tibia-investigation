#!/usr/bin/env python3
"""Exact memoryless digit-to-unit morphisms with honest finite search budgets."""
import re


def key_tuple(key):
    return tuple(sorted(key.items()))


def word_extensions(raw, form, minimum, maximum, known=None):
    """All compatible assignments, including every variable-length partition."""
    key=dict(known or {})
    def visit(i,j):
        if i==len(raw):
            if j==len(form):yield dict(key)
            return
        rest=raw[i:]
        low=sum(len(key[d]) if d in key else minimum for d in rest)
        high=sum(len(key[d]) if d in key else maximum for d in rest)
        if not low<=len(form)-j<=high:return
        d=raw[i]
        if d in key:
            unit=key[d]
            if form.startswith(unit,j):yield from visit(i+1,j+len(unit))
        else:
            for n in range(minimum,maximum+1):
                unit=form[j:j+n]
                if len(unit)!=n:continue
                key[d]=unit
                yield from visit(i+1,j+n)
            key.pop(d,None)
    yield from visit(0,0)


def word_pattern(raw,minimum,maximum,key):
    parts=[];seen=set()
    for d in raw:
        if d in key:parts.append(re.escape(key[d]))
        elif d in seen:parts.append('(?P=d'+d+')')
        else:
            parts.append('(?P<d'+d+'>[\\s\\S]{'+str(minimum)+','+str(maximum)+'})');seen.add(d)
    return re.compile(''.join(parts))


def solve(words,bank,cribs=None,max_states=2000,max_solutions=2000,local_cap=20000):
    words=list(dict.fromkeys(words));cribs=cribs or {}
    domains=[]
    for raw in words:
        forms=cribs.get(raw)
        if forms is None:
            forms=[f for n in bank.lengths if len(raw)*bank.minimum<=n<=len(raw)*bank.maximum for f in bank.by_length[n]]
        pattern=word_pattern(raw,bank.minimum,bank.maximum,{})
        domains.append(tuple(f for f in forms if f in bank.reverse and pattern.fullmatch(f)))
    root_counts={w:len(fs) for w,fs in zip(words,domains)}
    empty=[w for w,fs in zip(words,domains) if not fs]
    out={'complete':True,'limit':None,'states':0,'keys':[], 'root_form_counts':root_counts,'root_impossible_groups':empty}
    if empty:return out
    seen=set();solutions=set()
    class Budget(Exception):pass
    def fail(reason):
        out['complete']=False;out['limit']=reason
        raise Budget
    def search(key,ds):
        kt=key_tuple(key)
        if kt in seen:return
        if len(seen)>=max_states:fail('states')
        seen.add(kt)
        filtered=[];choices=[]
        for idx,(raw,fs) in enumerate(zip(words,ds)):
            if all(d in key for d in raw):
                form=''.join(key[d] for d in raw)
                if form not in fs:return
                filtered.append((form,))
            else:
                pattern=word_pattern(raw,bank.minimum,bank.maximum,key)
                matches=tuple(f for f in fs if pattern.fullmatch(f))
                if not matches:return
                filtered.append(matches);choices.append((len(matches),idx))
        if not choices:
            if kt not in solutions:
                if len(solutions)>=max_solutions:fail('solutions')
                solutions.add(kt)
            return
        _,idx=min(choices);raw=words[idx]
        extensions=set()
        for form in filtered[idx]:
            for newkey in word_extensions(raw,form,bank.minimum,bank.maximum,key):
                nk=key_tuple(newkey)
                if nk in extensions:continue
                if len(extensions)>=local_cap:fail('local_assignments')
                extensions.add(nk)
                search(newkey,filtered)
    try:search({},domains)
    except Budget:pass
    out['states']=len(seen);out['keys']=[dict(k) for k in sorted(solutions)]
    return out


def decode_word(raw,key,bank):
    missing=sorted(set(raw)-set(key))
    if missing:return {'status':'unknown_digits','missing':missing}
    form=''.join(key[d] for d in raw)
    return {'status':'lexical' if form in bank.reverse else 'outside_lexicon','units':bank.render(form),'words':bank.reverse.get(form,[])}


def decode_stream(raw,key,bank):
    missing=sorted(set(raw)-set(key))
    if missing:return {'status':'unknown_digits','missing':missing}
    form=''.join(key[d] for d in raw)
    # Exact DAG of word boundaries. Counts include spelling multiplicity/homophones.
    n=len(form);counts=[0]*(n+1);counts[n]=1;edges={}
    for start in range(n-1,-1,-1):
        here=[]
        for size in bank.lengths:
            end=start+size
            if end>n:break
            ws=bank.reverse.get(form[start:end],[])
            if ws and counts[end]:
                here.append({'end':end,'words':ws});counts[start]+=len(ws)*counts[end]
        if here:edges[str(start)]=here
    reachable={0};stack=[0]
    while stack:
        for edge in edges.get(str(stack.pop()),[]):
            if edge['end'] not in reachable:reachable.add(edge['end']);stack.append(edge['end'])
    edges={k:v for k,v in edges.items() if int(k) in reachable}
    unique=None
    if counts[0]==1:
        unique=[];i=0
        while i<n:
            edge=edges[str(i)][0];unique+=edge['words'];i=edge['end']
    return {'status':'lexical' if counts[0] else 'outside_lexicon','units':bank.render(form),'word_paths':counts[0], 'unique_words':unique,'word_dag':edges}
