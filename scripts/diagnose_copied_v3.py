#!/usr/bin/env python3
"""Post-hoc true-vs-returned objective audit; no extra fitting or new seeds."""
import hashlib,json,pathlib,collections
import numpy as np
from copied_homophonic_v3 import build_model
from copied_benchmark_v3 import fixture,verify
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    protocol=json.loads((ROOT/'data/copied_benchmark_v3_protocol.json').read_text());verify(protocol)
    path=ROOT/'results/copied_benchmark_v3.json';result=json.loads(path.read_text());table,_=build_model()
    probabilities=10**table;expected=probabilities.reshape(26,-1).sum(axis=1)/probabilities.sum();weight=protocol['solver_config']['frequency_weight']
    def objective(seqs,mapping):
        n=sum(map(len,seqs));raw=0;counts=np.zeros(26,dtype=np.int64);quads=0
        for seq in seqs:
            x=np.asarray([mapping[c] for c in seq],dtype=np.int64);counts+=np.bincount(x,minlength=26)
            ix=((x[:-3]*26+x[1:-2])*26+x[2:-1])*26+x[3:];raw+=float(table[ix].sum());quads+=len(ix)
        penalty=float(np.sum((counts-n*expected)**2/(n*expected+5)))
        return {'raw_score':raw,'quad_mean':raw/quads,'frequency_penalty':penalty,'objective':raw-weight*penalty}
    rows=[]
    for row in result['trials']:
        if row['character_accuracy']>=.95:continue
        mode=row['scenario']['distribution'];f=fixture(row['fixture'],mode)
        assert f['text_sha256']==row['text_sha256']
        found=objective(f['train'],row['mapping']);truth=objective(f['train'],f['key'])
        assert abs(found['quad_mean']-row['train_score'])<1e-8
        groups=collections.defaultdict(set)
        for seq in f['train']:
            for c in seq:groups[f['key'][c]].add(c)
        pairs=sum(len(codes)*(len(codes)-1)//2 for codes in groups.values())
        rows.append({'fixture':row['fixture'],'mode':mode,'source':row['source'],'accuracy':row['character_accuracy'],
          'unseen_test_positions':f['unseen_positions'],'true_key':truth,'returned_key':found,
          'true_minus_returned_objective':truth['objective']-found['objective'],
          'observed_codes':len({c for seq in f['train'] for c in seq}),
          'latent_homophone_pairs_with_common_true_letter':pairs,
          'diagnosis':'search insufficiency: true key has higher training objective' if truth['objective']>found['objective'] else 'objective mismatch: wrong returned key beats true key'})
    out={'role':'posthoc audit ofopenedqualificationfailures; notqualification or tuning',
      'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'additional_fits':0,'failures':rows,
      'search_insufficiency_count':sum(r['true_minus_returned_objective']>0 for r in rows),
      'objective_mismatch_count':sum(r['true_minus_returned_objective']<=0 for r in rows),
      'limits':['Known true key supplies a witness, not a proof of global optimality.',
        'A true-higher witness isolates failure of this finite search, not an absence of other objective errors.',
        'These qualification outcomes are now opened; future tuning requires a new qualification set.']}
    (ROOT/'results/copied_v3_diagnosis.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'count':len(rows),'search_insufficiency':out['search_insufficiency_count'],'objective_mismatch':out['objective_mismatch_count'],
      'gaps':[(r['fixture'],r['true_minus_returned_objective']) for r in rows]},indent=2))
if __name__=='__main__':main()
