#!/usr/bin/env python3
"""Fail-closed, truth-count qualification gate for copiedV4; no469 fitting."""
import json,pathlib,hashlib
from copied_benchmark_v4 import verify
ROOT=pathlib.Path(__file__).resolve().parents[1]
def evaluate(r,p):
    if r.get('complete') is not True or r.get('frozen_protocol')!=p:raise ValueError('incomplete or wrongprotocol')
    groups={m:{} for m in p['modes']}
    for t in r['trials']:
        mode=t['scenario']['distribution'];i=t['fixture'];n=t['holdout_letters'];correct=t['correct_holdout_letters']
        if mode not in groups or i in groups[mode] or type(i)is not int or not 0<=i<p['fixtures_per_mode']:raise ValueError('badtrial')
        if type(correct)is not int or n!=p['holdout_letters'] or not 0<=correct<=n:raise ValueError('badaccuracycount')
        if abs(correct/n-t['character_accuracy'])>1e-12:raise ValueError('badaccuracy')
        if not t['known_key_exact']:raise ValueError('invalidpositivefixture')
        groups[mode][i]=correct/n
    summaries=[]
    for mode,rows in groups.items():
        if set(rows)!=set(range(p['fixtures_per_mode'])):raise ValueError('missingtrials')
        passes=sum(x>=p['gate']['minimum_holdout_character_accuracy'] for x in rows.values())
        summaries.append({'mode':mode,'passed':passes,'required':p['gate']['minimum_pass_count'],'passes':passes>=p['gate']['minimum_pass_count']})
    return {'gate_passed':all(s['passes'] for s in summaries),'summaries':summaries,
      'scope':'99skewed copiedstatic, copiedresampled, ordinary literarypositives only; no translation inferred'}
def assess():
    path=ROOT/'data/copied_benchmark_v4_protocol.json';p=json.loads(path.read_text());verify(p)
    result=ROOT/'results/copied_benchmark_v4.json';r=json.loads(result.read_text());h=hashlib.sha256(path.read_bytes()).hexdigest()
    if r['protocol_sha256']!=h:raise ValueError('protocolhash')
    out=evaluate(r,p);out.update(protocol_sha256=h,result_sha256=hashlib.sha256(result.read_bytes()).hexdigest());return out
if __name__=='__main__':
    out=assess();(ROOT/'results/copied_v4_gate.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
