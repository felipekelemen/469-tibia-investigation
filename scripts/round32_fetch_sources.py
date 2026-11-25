#!/usr/bin/env python3
"""Bounded public GET captures for R32. Full response bodies remain ignored."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
from history_source_fetch import fetch

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', required=True)
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.batch):
        raise ValueError('Use a simple unused batch name')
    targets = json.loads((ROOT / args.targets).read_text())
    if not targets or any(not re.fullmatch(r'[A-Za-z0-9_-]+', r['id']) for r in targets):
        raise ValueError('Nonempty targets with simple identifiers required')
    if len({r['id'] for r in targets}) != len(targets):
        raise ValueError('Duplicate identifier')
    directory = ROOT / 'data/private/round32' / args.batch
    previous = sum(len(json.loads(p.read_text())) for p in directory.parent.glob('*/metadata.json'))
    if previous + len(targets) > 32:
        raise ValueError('Targeted HTTP budget exceeded')
    directory.mkdir(parents=True, exist_ok=False)
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda t: fetch(t, directory), targets))
    (directory / 'metadata.json').write_text(json.dumps(rows, indent=2) + '\n')
    for row in rows:
        print(row['id'], row.get('http_status', row.get('network_error')), row.get('bytes'))
