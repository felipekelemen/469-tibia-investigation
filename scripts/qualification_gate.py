#!/usr/bin/env python3
"""Recompute the preregistered gate from complete trials; fail closed.

No optimizer, Tibia corpus or fitted key is loaded here.
"""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]

def evaluate(result,protocol):
    if result.get('complete') is not True:raise ValueError('qualification incomplete')
    if result.get('frozen_protocol')!=protocol:raise ValueError('embedded protocol differs')
    expected={(s['codes'],s['distribution']) for s in protocol['scenarios']}
    if len(expected)!=len(protocol['scenarios']):raise ValueError('duplicate protocol scenarios')
    groups={s:{} for s in expected}
    for row in result['trials']:
        key=(row['scenario']['codes'],row['scenario']['distribution']);i=row['fixture']
        if key not in groups or i in groups[key]:raise ValueError('unexpected or duplicate trial')
        if type(i) is not int or not 0<=i<protocol['fixtures_per_scenario']:raise ValueError('invalid fixture index')
        n=row['holdout_letters'];correct=row['correct_holdout_letters']
        if n!=protocol['holdout_letters'] or type(correct) is not int or not 0<=correct<=n:raise ValueError('invalid truth-based accuracy counts')
        accuracy=correct/n
        if abs(accuracy-row['character_accuracy'])>1e-12:raise ValueError('accuracy field inconsistent with counts')
        groups[key][i]=accuracy
    reports=[]
    for key,trials in sorted(groups.items()):
        if set(trials)!=set(range(protocol['fixtures_per_scenario'])):raise ValueError('missing qualification trials')
        passes=sum(a>=protocol['gate']['minimum_holdout_character_accuracy'] for a in trials.values())
        reports.append({'codes':key[0],'distribution':key[1],'passed_fixtures':passes,'required_passes':protocol['gate']['minimum_pass_count'],
                        'fixtures':len(trials),'passes_gate':passes>=protocol['gate']['minimum_pass_count']})
    success=all(r['passes_gate'] for r in reports)
    return {'scenario_results':reports,'gate_passed':success,'p04_status':'ELIGIBLE_FOR_MATCHED_NULL_EXPLORATION' if success else 'BLOCKED_INSUFFICIENT_QUALIFICATION',
      'decision_rule':'all six predeclared synthetic scenarios must pass; no rounding, tuning or post-hoc scenario removal',
      'translation_status':'NO_VERIFIED_TRANSLATION','limits':['Passing is necessary for this pipeline, not sufficient to validate a real translation.',
      'A failed synthetic gate does not reject homophonic substitution or demonstrate no meaning in469.']}

def main():
    from homophonic_benchmark import verify
    protocol_path=ROOT/'data/homophonic_benchmark_protocol.json';result_path=ROOT/'results/homophonic_benchmark.json'
    protocol=json.loads(protocol_path.read_text());verify(protocol)
    result=json.loads(result_path.read_text());digest=hashlib.sha256(protocol_path.read_bytes()).hexdigest()
    if result['protocol_sha256']!=digest:raise ValueError('protocol hash mismatch')
    out=evaluate(result,protocol);out.update(protocol_sha256=digest,result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest())
    (ROOT/'results/p04_gate.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
