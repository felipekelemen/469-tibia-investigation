#!/usr/bin/env python3
"""Post-hoc diagnosis of worst DEVELOPMENT stress case; no parameter changes."""
import json,pathlib,random
import numpy as np
from homophonic_benchmark import letters,encode,segments
from cipher_battery import english_model,score
from robust_homophonic import solve
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    records=json.loads((ROOT/'results/copied_prose_stress_v2.json').read_text())['trials']
    worst=min(records,key=lambda r:r['character_accuracy']);i=worst['fixture'];seed=80469000+i;rng=random.Random(seed)
    plain=letters(ROOT/'data/benchmark_reference/frankenstein.txt')
    motifs=[plain[x:x+256] for x in [rng.randrange(20000,len(plain)-1000) for _ in range(8)]]
    encoded,key,_=encode(''.join(motifs),99,'skewed',seed);pools=[encoded[j*256:(j+1)*256] for j in range(8)]
    schedule=[rng.randrange(8) for _ in range(30)];text=''.join(motifs[j] for j in schedule);codes=[c for j in schedule for c in pools[j]]
    tr=segments(codes[:5668]);hold=codes[5668:6692];table,_=english_model(ROOT/'data/english_reference/alice.txt')
    fit=solve(tr,table,seed=seed+900000,banks=2)
    decoded=''.join(chr(fit['mapping'][c]+65) for c in hold)
    assert decoded[:100]==worst['preview'],'fixture reproduction drift'
    def objective(mapping):
        xs=[[mapping[c] for c in seq] for seq in tr];n=sum(map(len,xs))
        raw=sum(score(s,table)*(len(s)-3) for s in xs)
        probs=10**table;expected=probs.reshape(26,-1).sum(axis=1)/probs.sum()
        observed=np.bincount([c for seq in xs for c in seq],minlength=26)
        penalty=float(np.sum((observed-n*expected)**2/(n*expected+5)))
        return {'raw_tetragram_sum':raw,'frequency_penalty':penalty,'objective':raw-2*penalty}
    true=objective(key);found=objective(fit['mapping'])
    assert abs(found['objective']-fit['objective'])<1e-5
    r={'role':'posthoc development diagnosis, worst of12 stress fixtures; exact repeated run, no new seed or tuning',
       'fixture':i,'seed':seed,'truth':true,'found':found,'holdout_accuracy':worst['character_accuracy'],
       'true_objective_minus_found':true['objective']-found['objective'],
       'interpretation':'True key scores higher than returned key: search insufficiency' if true['objective']>found['objective'] else 'Wrong returned key scores at least as high as truth: objective mismatch',
       'limits':['Only one selected development case; neither universal mechanism diagnosis nor independent qualification.']}
    (ROOT/'results/copied_prose_diagnosis_v2.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
