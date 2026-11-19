#!/usr/bin/env python3
"""Optional public GET capture. Full page bodies remain local and ignored."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse,json
from history_source_fetch import fetch
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--targets',required=True);p.add_argument('--batch',required=True);a=p.parse_args()
    if not a.batch.replace('_','').isalnum():raise ValueError('simple batch name required')
    out=ROOT/'data/historical_refresh/round24'/a.batch
    if out.exists():raise ValueError('refusing to overwrite captures')
    out.mkdir(parents=True)
    targets=json.loads((ROOT/a.targets).read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda t:fetch(t,out),targets))
    (ROOT/f'data/round24_http_{a.batch}.json').write_text(json.dumps(rows,indent=2)+'\n')
    for r in rows:print(r['id'],r.get('http_status',r.get('network_error')),r.get('bytes'))
