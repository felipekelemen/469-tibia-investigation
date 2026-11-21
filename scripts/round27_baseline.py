#!/usr/bin/env python3
"""Exploratory paired measurement of the unchanged R23 enumerator."""
from pathlib import Path
import hashlib
import json
from round27_experiment import score, verify_manifest
from round27_fixtures import training_bank
from round27_witness_solver import emit
from unit_morphism_solver import solve

ROOT = Path(__file__).resolve().parents[1]


def run():
    verify_manifest('round27_experiment_manifest.json')
    verify_manifest('round27_baseline_manifest.json')
    protocol = json.loads((ROOT/'data/round27_protocol.json').read_text())
    fixtures = json.loads((ROOT/'data/round27_fixtures.json').read_text())
    bank = training_bank(protocol)
    results = []
    for case in fixtures['cases']:
        if case['kind'] != 'base':
            continue
        solution = solve(case['train'][:7], bank, max_states=2000,
                         max_solutions=2000, local_cap=20000)
        keys = solution.pop('keys')
        held = []
        for raw, truth in zip(case['held'], case['held_forms']):
            p = {'form_certified': False, 'chunks_certified': False}
            if solution['complete'] and keys:
                forms = {emit(raw, key) for key in keys}
                chunks = {tuple(key[d] for d in raw) for key in keys}
                if len(forms) == 1:
                    p.update(form_certified=True, form=next(iter(forms)))
                if len(chunks) == 1:
                    p.update(chunks_certified=True, chunks=list(next(iter(chunks))))
            held.append({'raw': raw, 'prediction': p, 'score': score(raw, truth, case['key'], p)})
        row = {'id': case['id'], 'enumeration': solution, 'enumerated_keys': len(keys),
               'true_key_in_enumeration': case['key'] in keys, 'held': held}
        results.append(row)
        print(case['id'], 'complete', solution['complete'], 'keys', len(keys),
              'truth_present', row['true_key_in_enumeration'], flush=True)
    out = {'round': 27, 'role': 'exploratory paired baseline; not a second qualification',
           'cases': results, 'summary': {
           'cases': len(results),
           'complete': sum(c['enumeration']['complete'] for c in results),
           'true_key_in_enumeration': sum(c['true_key_in_enumeration'] for c in results),
           'states': sum(c['enumeration']['states'] for c in results),
           'held_exact_certified': sum(h['score']['exact_certified_form'] for c in results for h in c['held']),
           'confidently_wrong': sum(h['score']['confidently_wrong'] for c in results for h in c['held'])}}
    path = ROOT/'results/round27_baseline.json'
    assert not path.exists()
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(out['summary'], indent=2), flush=True)


if __name__ == '__main__':
    run()
