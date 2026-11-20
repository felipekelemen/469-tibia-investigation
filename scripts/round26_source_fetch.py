#!/usr/bin/env python3
"""Optional public research captures; no overwrites, bodies kept local/ignored."""
from concurrent.futures import ThreadPoolExecutor
import argparse,json
from pathlib import Path
from history_source_fetch import fetch
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--targets',required=True);a=p.parse_args()
    if not a.batch.isalnum():raise ValueError('simple batch name required')
    directory=ROOT/'data/historical_refresh/round26'/a.batch;directory.mkdir(parents=True,exist_ok=False)
    targets=json.loads((ROOT/a.targets).read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda t:fetch(t,directory),targets))
    (ROOT/f'data/round26_http_{a.batch}.json').write_text(json.dumps(rows,indent=2)+'\n')
    for row in rows:print(row['id'],row.get('http_status',row.get('network_error')),row.get('bytes'),flush=True)
