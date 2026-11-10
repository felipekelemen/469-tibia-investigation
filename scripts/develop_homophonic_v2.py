#!/usr/bin/env python3
"""Development on V1's OPENED positives; never V2 qualification authors."""
import json,pathlib,time,random
import numpy as np
from cipher_battery import english_model
from homophonic_benchmark import fixture
from robust_homophonic import solve
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    table,_=english_model(ROOT/'data/english_reference/alice.txt')
    cases=[(99,'skewed',i) for i in [1,2,11,21]]+[(99,'balanced',0),(75,'skewed',0),(52,'balanced',0)]
    rows=[];started=time.monotonic()
    for n,d,i in cases:
        f=fixture(i,n,d);seed=f['seed']+500000
        # Bank0 reproduces the old first fit exactly; development may inspect true text.
        fit=solve(f['train_sequences'],table,seed=seed,banks=2)
        hold=[c for seq in f['hold_sequences'] for c in seq];truth=f['truth_hold']
        ac=[]
        for b in fit['banks']:
            decoded=''.join(chr(b['mapping'][c]+65) for c in hold)
            ac.append(sum(x==y for x,y in zip(decoded,truth))/len(truth))
        row={'codes':n,'distribution':d,'fixture':i,'seed':seed,'bank_accuracies':ac,
          'bank_training_objectives':[b['objective'] for b in fit['banks']],
          'selected_bank':fit['selected_bank'],'selected_accuracy':ac[fit['selected_bank']],
          'seconds':fit['total_runtime_seconds']}
        rows.append(row);print(json.dumps(row),flush=True)
    out={'stage':'DEVELOPMENT_ONLY_PREVIOUSLY_OPENED_QUALIFICATION','cases':rows,
      'selection':'two independent8restart banks; select training objective only','runtime_seconds':time.monotonic()-started,
      'warning':'These seven selected cases do not requalify V1 and do not estimate prospective performance.'}
    (ROOT/'results/homophonic_v2_development.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
