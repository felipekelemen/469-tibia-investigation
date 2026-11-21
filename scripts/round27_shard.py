#!/usr/bin/env python3
"""Run a disjoint index range using the unchanged frozen experiment functions."""
import argparse
import json
from pathlib import Path
from round27_experiment import ROOT, fit_case, verify_manifest
from round27_fixtures import training_bank


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, required=True)
    parser.add_argument('--stop', type=int, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--cached', action='store_true')
    args = parser.parse_args()
    assert 0 <= args.start < args.stop <= 60
    verify_manifest('round27_experiment_manifest.json')
    protocol = json.loads((ROOT/'data/round27_protocol.json').read_text())
    fixtures = json.loads((ROOT/'data/round27_fixtures.json').read_text())
    if args.cached:
        from round27_cached_model import enable
        enable()
    if args.output.exists() and not args.resume:
        raise ValueError('Existing shard requires explicit --resume')
    existing = [json.loads(line) for line in args.output.read_text().splitlines()] if args.output.exists() else []
    completed = {(r['id'], r['scenario']) for r in existing}
    assert len(completed) == len(existing)
    expected = {(c['id'], s) for c in fixtures['cases'][args.start:args.stop]
                for s in (protocol['scenarios'][:3] if c['kind'] == 'base' else protocol['scenarios'][3:])}
    assert completed <= expected
    bank = training_bank(protocol)
    for case in fixtures['cases'][args.start:args.stop]:
        scenarios = protocol['scenarios'][:3] if case['kind'] == 'base' else protocol['scenarios'][3:]
        for scenario in scenarios:
            if (case['id'], scenario) in completed:
                continue
            row = fit_case(case, scenario, protocol, bank)
            with args.output.open('a') as stream:
                stream.write(json.dumps(row, ensure_ascii=False)+'\n')
            print(case['id'], scenario, 'pass', row['passes'], 'exact',
                  row['certified_exact_fraction'], 'states', row['states'], flush=True)
