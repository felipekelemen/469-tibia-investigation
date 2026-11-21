#!/usr/bin/env python3
"""Aggregate all predeclared fits using the frozen functions, with no selection."""
import argparse
import json
from pathlib import Path
from round27_experiment import ROOT, diagnostics, summarize, verify_manifest


def merge(parts, output):
    verify_manifest('round27_experiment_manifest.json')
    verify_manifest('round27_execution_manifest.json')
    protocol = json.loads((ROOT/'data/round27_protocol.json').read_text())
    fixtures = json.loads((ROOT/'data/round27_fixtures.json').read_text())
    expected = [(c['id'], s) for c in fixtures['cases']
                for s in (protocol['scenarios'][:3] if c['kind'] == 'base' else protocol['scenarios'][3:])]
    rows = [json.loads(line) for path in parts for line in path.read_text().splitlines()]
    by_id = {(r['id'], r['scenario']): r for r in rows}
    if len(rows) != len(by_id) or set(by_id) != set(expected):
        raise ValueError('Duplicate, missing, or undeclared fits')
    ordered = [by_id[key] for key in expected]
    result = {'round': 27, 'translation_validated': False,
              'summary': summarize(ordered, protocol), 'cases': ordered,
              'diagnostics': diagnostics(fixtures)}
    if output.exists():
        raise ValueError('Refusing to overwrite result')
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--parts', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'results/round27_qualification.json')
    args = parser.parse_args()
    merge(args.parts, args.output)
