#!/usr/bin/env python3
"""Fixed development grid; old12 stress cases already opened, not qualification."""
import json,pathlib,time
from concurrent.futures import ThreadPoolExecutor
from copied_homophonic_v3 import build_model,development_fixture,solve,evaluate
from fast_homophonic import library
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    table,meta=build_model();library();started=time.monotonic();allrows=[];summary=[]
    # Grid fixed before development outputs; no V3qualification data read.
    for config in [{'banks':2,'frequency_weight':2.0},{'banks':2,'frequency_weight':.5},
                   {'banks':4,'frequency_weight':2.0},{'banks':4,'frequency_weight':.5}]:
        with ThreadPoolExecutor(max_workers=2) as pool:
            fs=[development_fixture(i) for i in range(12)]
            futures=[pool.submit(solve,f['train'],table,seed=f['seed'],**config) for f in fs]
            rows=[]
            for i,(f,fut) in enumerate(zip(fs,futures)):
                fit=fut.result();r=evaluate(f,fit);r.update(fixture=i,config=config,seconds=fit['total_runtime_seconds'],train_score=fit['train_score'])
                rows.append(r);allrows.append(r);print(json.dumps({'config':config,'fixture':i,'accuracy':r['accuracy']}),flush=True)
        s={'config':config,'passes95':sum(r['accuracy']>=.95 for r in rows),'mean_accuracy':sum(r['accuracy'] for r in rows)/12,
           'min_accuracy':min(r['accuracy'] for r in rows)}
        summary.append(s)
        (ROOT/'results/copied_v3_development_checkpoint.json').write_text(json.dumps({'complete':False,'summary':summary,'trials':allrows},indent=2)+'\n')
    # Selection solely on opened DEVELOPMENT, never fresh qualification.
    selected=max(summary,key=lambda s:(s['passes95'],s['mean_accuracy'],-s['config']['banks']))
    r={'complete':True,'model':meta,'trials':allrows,'summary':summary,'selected':selected,
       'runtime_seconds':time.monotonic()-started,'limits':['Development only; previous opened copied stress cases.','Choosing hyperparameters on these truths is explicitly training, not validation.']}
    (ROOT/'results/copied_v3_development.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
