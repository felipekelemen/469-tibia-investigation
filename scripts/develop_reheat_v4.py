#!/usr/bin/env python3
"""V3 opened failures become development; no V4reference access."""
import json,pathlib,time
from concurrent.futures import ThreadPoolExecutor
from copied_homophonic_v3 import build_model,evaluate
from copied_benchmark_v3 import fixture
from robust_homophonic import solve
from fast_homophonic import library
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    table,_=build_model();library();start=time.monotonic();records=json.loads((ROOT/'results/copied_benchmark_v3.json').read_text())['trials']
    failures=[t['fixture'] for t in records if t['scenario']['distribution']=='copied_static_codes' and t['character_accuracy']<.95]
    cases=[(i,'copied_static_codes') for i in failures]+[(1,'copied_static_codes'),(0,'ordinary'),(16,'ordinary')]
    allrows=[];summaries=[]
    for temperature in [40,80,120]:
        fs=[fixture(i,m) for i,m in cases]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futs=[pool.submit(solve,f['train'],table,seed=f['seed']+700000,banks=2,max_temp=temperature) for f in fs]
            rows=[]
            for (i,mode),f,future in zip(cases,fs,futs):
                fit=future.result();r=evaluate(f,fit);r.update(fixture=i,mode=mode,temperature=temperature,seconds=fit['total_runtime_seconds']);rows.append(r);allrows.append(r)
                print(temperature,i,mode,r['accuracy'],flush=True)
        summaries.append({'temperature':temperature,'passes95':sum(t['accuracy']>=.95 for t in rows),'mean':sum(t['accuracy'] for t in rows)/len(rows),'minimum':min(t['accuracy'] for t in rows)})
    chosen=max(summaries,key=lambda s:(s['passes95'],s['mean'],-s['temperature']))
    result={'complete':True,'role':'development onV3openedqualification, notindependentvalidation','cases':cases,'trials':allrows,'summary':summaries,'selected':chosen,'runtime_seconds':time.monotonic()-start}
    (ROOT/'results/reheat_v4_development.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(summaries,indent=2),flush=True)
if __name__=='__main__':main()
