#!/usr/bin/env python3
"""Optional bounded public MediaWiki history fetch; bodies stay local/ignored."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from history_source_fetch import fetch

ROOT = Path(__file__).resolve().parents[1]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--batch', required=True)
    parser.add_argument('--revision-ids', nargs='+', type=int); a = parser.parse_args()
    if not a.batch.isalnum():
        raise ValueError('simple batch name required')
    out = ROOT/'data/historical_refresh/round25'/a.batch
    out.mkdir(parents=True, exist_ok=False)
    base = {'action':'query', 'format':'json', 'formatversion':'2', 'prop':'revisions',
            'titles':'Bonelord (Nostalgia)', 'rvprop':'ids|timestamp|comment|sha1', 'rvlimit':'20'}
    specs = [('nostalgia_2022_2023', {'rvstart':'2024-01-01T00:00:00Z', 'rvend':'2022-01-01T00:00:00Z'}),
             ('nostalgia_2012', {'rvdir':'newer', 'rvstart':'2011-01-01T00:00:00Z', 'rvend':'2013-01-01T00:00:00Z',
                                  'rvprop':'ids|timestamp|comment|sha1|content', 'rvslots':'main', 'rvlimit':'10'})]
    targets = [{'id':id, 'url':'https://www.tibiawiki.com.br/api.php?'+urlencode(base|params)} for id,params in specs]
    if a.revision_ids:
        params = {'action':'query', 'format':'json', 'formatversion':'2', 'prop':'revisions',
                  'revids':'|'.join(map(str,a.revision_ids)), 'rvprop':'ids|timestamp|comment|sha1|content', 'rvslots':'main'}
        targets = [{'id':'selected_revisions','url':'https://www.tibiawiki.com.br/api.php?'+urlencode(params)}]
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(lambda t:fetch(t,out),targets))
    for row in rows:
        path = ROOT/row.get('body_local_ignored','missing')
        if path.is_file():
            try:
                payload = json.loads(path.read_text())
                row['api_error'] = payload.get('error')
                row['has_continuation'] = bool(payload.get('continue'))
                row['revision_metadata'] = []
                for page in payload.get('query',{}).get('pages',[]):
                    for r in page.get('revisions',[]):
                        text = r.get('slots',{}).get('main',{}).get('content','')
                        row['revision_metadata'].append({k:r[k] for k in ('revid','parentid','timestamp','sha1') if k in r}|
                                                        {'content_returned':bool(text), 'contains_3478': '3478' in text if text else None})
            except (ValueError, UnicodeError):
                row['json_parse_failed'] = True
        print(row['id'], row.get('http_status',row.get('network_error')), flush=True)
    (ROOT/f'data/round25_history_http_{a.batch}.json').write_text(json.dumps(rows,indent=2)+'\n')
