#!/usr/bin/env python3
"""Fixtures generated without consulting target fits or solver success."""
from collections import Counter
from pathlib import Path
import json,random,re
from unit_morphism_lexicon import banks,FAMILIES
ROOT=Path(__file__).resolve().parents[1]


def encode(form,key):
    paths={len(form):''}
    for i in range(len(form)-1,-1,-1):
        possible=[d+paths[i+len(u)] for d,u in key.items() if form.startswith(u,i) and i+len(u) in paths]
        if possible:paths[i]=min(possible)
    return paths.get(0)


def create():
    rng=random.Random(23639469);allbanks,meta=banks();local=[];global_cases=[]
    for family in FAMILIES:
        b=allbanks[family];forms=sorted(b.reverse)
        while sum(c['family']==family for c in local)<30:
            form=rng.choice(forms);units=[];i=0
            while i<len(form):
                options=[n for n in range(b.minimum,b.maximum+1) if n<=len(form)-i]
                if not options:break
                n=rng.choice(options);units.append(form[i:i+n]);i+=n
            if i!=len(form) or not 1<=len(set(units))<=10:continue
            digits=rng.sample(list('0123456789'),len(set(units)))
            mapping=dict(zip(sorted(set(units)),digits));key={d:u for u,d in mapping.items()}
            local.append({'family':family,'form':form,'raw':''.join(mapping[u] for u in units),'key':key})
        counts=Counter()
        for form in forms:
            for n in range(b.minimum,b.maximum+1):
                counts.update(form[i:i+n] for i in range(len(form)-n+1))
        pools={n:sorted((u for u in counts if len(u)==n),key=lambda u:(-counts[u],u))[:40] for n in range(b.minimum,b.maximum+1)}
        attempts=0;made=0
        while made<10:
            attempts+=1
            if attempts>10000:raise RuntimeError('generation exhausted: '+family)
            if b.minimum==b.maximum:units=rng.sample(pools[b.minimum],10)
            else:units=rng.sample(pools[1],6)+rng.sample(pools[2],2)+rng.sample(pools[3],2)
            rng.shuffle(units);key=dict(zip('0123456789',units))
            pattern=re.compile('(?:'+'|'.join(map(re.escape,units))+')+')
            eligible=[]
            for form in forms:
                if pattern.fullmatch(form):eligible.append((form,encode(form,key)))
            if len(eligible)<20 or set(''.join(raw for _,raw in eligible))!=set('0123456789'):continue
            rng.shuffle(eligible);train=eligible[:7];held=eligible[7:14]
            global_cases.append({'id':family+'_'+str(made),'family':family,'key':key,'train':[x[1] for x in train], 'train_forms':[x[0] for x in train], 'held':[x[1] for x in held],'held_forms':[x[0] for x in held], 'eligible_forms':len(eligible),'generation_attempt':attempts})
            made+=1
        print(family, 'generated',made,'global fixtures in',attempts,'attempts',flush=True)
    return {'selection':'Before fitting; frequent top40 units per allowed length, six length1/two length2/two length3 for variable families. Lexicographically first valid digit encoding. Need >=20 eligible distinct forms and all10digits used in eligible pool, not necessarily in seven discovery forms. No outcome-conditioned selection.','local':local,'global':global_cases,'lexicon':meta}

if __name__=='__main__':
    p=ROOT/'data/round23_fixtures.json'
    if p.exists():raise SystemExit('refusing to replace frozen fixtures')
    p.write_text(json.dumps(create(),ensure_ascii=False,indent=2)+'\n')
