#!/usr/bin/env python3
"""Optional bounded public GET capture; offline evidence checks never need it.

Bodies stay in ignored historical_refresh. Captures are not image dates.
No challenge solving, credential/header capture, or automatic retry.
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/historical_refresh/round14'
MAX_BYTES = 8 * 1024 * 1024


def fetch(target, capture_dir=OUT):
    row = {'id': target['id'], 'requested_url': target['url'],
           'requested_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'method': 'one public HTTPS GET; inherited proxy/TLS trust; no retries'}
    req = urllib.request.Request(target['url'], headers={'User-Agent': 'Tibia469Research/1.0 source audit'})
    try:
        try:
            response = urllib.request.urlopen(req, timeout=20)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            body = response.read(MAX_BYTES + 1)
            row['http_status'] = response.code
            row['content_type'] = response.headers.get('Content-Type', '')
            row['http_last_modified'] = response.headers.get('Last-Modified')
            row['memento_datetime'] = response.headers.get('Memento-Datetime')
            final = urllib.parse.urlsplit(response.url)
            # Only static public source targets are requested; redact any
            # unexpected redirect query instead of publishing challenge tokens.
            row['final_url_without_query'] = urllib.parse.urlunsplit((final.scheme, final.netloc, final.path, '', ''))
        row['body_truncated'] = len(body) > MAX_BYTES
        body = body[:MAX_BYTES]
        row['bytes'] = len(body)
        row['sha256'] = hashlib.sha256(body).hexdigest()
        lower = body.lower() if 'html' in row['content_type'] else b''
        row['human_check_marker'] = any(marker in lower for marker in
                                        (b'cf-chl-', b'verify you are human', b'just a moment...', b'challenge-platform'))
        row['body_local_ignored'] = str((capture_dir / (target['id'] + '.body')).relative_to(ROOT))
        (capture_dir / (target['id'] + '.body')).write_bytes(body)
    except (OSError, urllib.error.URLError) as exc:
        row['network_error'] = type(exc).__name__
        row['network_error_text'] = str(exc)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--targets', default='data/history_round14_targets.json')
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.batch):
        raise ValueError('use a simple batch name')
    targets = json.loads((ROOT / args.targets).read_text())
    if args.ids:
        targets = [t for t in targets if t['id'] in args.ids]
    if not targets:
        raise ValueError('no requested source targets')
    OUT.mkdir(parents=True, exist_ok=True)
    record = OUT / (args.batch + '.json')
    if record.exists():
        raise RuntimeError('batch exists; preserve original capture')
    capture_dir = OUT / args.batch
    capture_dir.mkdir(exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda target: fetch(target, capture_dir), targets))
    record.write_text(json.dumps(rows, indent=2) + '\n')
    for r in rows:
        print(json.dumps({k: v for k, v in r.items() if k not in ('body_local_ignored', 'network_error_text')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
