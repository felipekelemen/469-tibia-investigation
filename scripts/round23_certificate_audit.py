#!/usr/bin/env python3
"""Post-fit audit by explicit length vectors, independent of regex/CSP code."""
from itertools import product
from collections import defaultdict
from pathlib import Path
import argparse,json
from unit_morphism_lexicon import banks
ROOT=Path(__file__).resolve().parents[1]

def assignments(raw,forms,minimum,maximum):
    digits=sorted(set(raw));bylen=defaultdict(list)
    for f in forms:bylen[len(f)].append(f)
    for lengths in product(range(minimum,maximum+1),repeat=len(digits)):
        size=dict(zip(digits,lengths));total=sum(size[d] for d in raw)
        spans=[];position=0
        for d in raw:spans.append((d,position,position+size[d]));position+=size[d]
        for form in bylen.get(total,[]):
            key={};valid=True
            for d,start,end in spans:
                unit=form[start:end]
                if d in key and key[d]!=unit:valid=False;break
                key[d]=unit
            if valid:yield tuple(sorted(key.items()))

def independent_fixed_fit(words,b):
    domains=[]
    for w in dict.fromkeys(words):
        domain=set(assignments(w,b.reverse,b.minimum,b.maximum))
        domains.append(domain)
    domains.sort(key=len);keys={()}
    for domain in domains:
        new=set()
        for old in keys:
            k=dict(old)
            for extension in domain:
                e=dict(extension)
                if all(k[d]==u for d,u in extension if d in k):new.add(tuple(sorted((k|e).items())))
        keys=new
        if not keys:break
    return sorted(keys)

def build():
    targets=json.loads((ROOT/'results/round23_targets.json').read_text())
    bs,_=banks();local=[];fixed=[];seen=set()
    for row in targets['targets']:
        if row['root_impossible_groups']:
            b=bs[row['family']]
            raw=min(row['root_impossible_groups'],key=lambda w:(len(set(w)),len(w),w))
            if (row['family'],raw) in seen:continue
            seen.add((row['family'],raw))
            found=list(assignments(raw,b.reverse,b.minimum,b.maximum))
            assert not found
            local.append({'family':row['family'],'raw':raw,'dictionary_forms_checked':len(b.reverse),'explicit_length_vectors':(b.maximum-b.minimum+1)**len(set(raw)),'assignments':len(found)})
        elif row['complete'] and not row['keys'] and bs[row['family']].minimum==bs[row['family']].maximum:
            keys=independent_fixed_fit(row['words'],bs[row['family']]);assert not keys
            fixed.append({'family':row['family'],'id':row['id'],'method':'explicit chunk-length enumeration followed by natural join of per-word assignments','keys':len(keys)})
    # All returned keys must respect every training word; no lexicographic candidate is promoted.
    real=[]
    for row in targets['targets']:
        b=bs[row['family']]
        allvalid=all(all(''.join(k[d] for d in w) in b.reverse for w in row['words']) for k in row['keys'])
        assert allvalid
        real.append({'family':row['family'],'id':row['id'],'returned_keys':len(row['keys']),'every_returned_key_verified':allvalid})
    return {'scope':'Post-fit independent arithmetic audit; not another hypothesis search, semantic qualification or blinded validation. Length-vector enumeration does not import unit_morphism_solver.','local_empty_certificates':local,'fixed_joint_empty_certificates':fixed,'returned_key_checks':real}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();result=build();path=ROOT/'results/round23_certificate_audit.json'
    if a.check:
        assert json.loads(path.read_text())==result
    else:path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2))
