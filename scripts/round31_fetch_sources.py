#!/usr/bin/env python3
"""Optional one-shot public retrieval; preserve full bodies only in ignored storage."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
from history_source_fetch import fetch

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.batch):
        raise ValueError('Use a simple new batch name')
    targets = json.loads((ROOT / 'data/round31_fetch_targets.json').read_text())
    directory = ROOT / 'data/private/round31' / args.batch
    directory.mkdir(parents=True, exist_ok=False)
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda target: fetch(target, directory), targets))
    (directory / 'metadata.json').write_text(json.dumps(rows, indent=2) + '\n')
    for row in rows:
        print(row['id'], row.get('http_status', row.get('network_error')), row.get('bytes'))
