#!/usr/bin/env python3
"""Capture preselected public URLs; no access-control workarounds."""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def run(attempt,targets,output):
    records=[]
    for target in json.loads((ROOT/targets).read_text()):
        path=ROOT/'data/private/round37'/('http'+str(attempt)+'_'+target['id']+'.body')
        assert not path.exists(),'Preserve previous captures'
        before=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            with urllib.request.urlopen(target['url'],timeout=25) as response:
                status=response.status;url=response.url;headers=dict(response.headers);body=response.read()
            error=None
        except urllib.error.HTTPError as exception:
            status=exception.code;url=exception.url;headers=dict(exception.headers);body=exception.read();error=str(exception)
        except Exception as exception:
            status=None;url=target['url'];headers={};body=b'';error=str(exception)
        path.write_bytes(body)
        records.append(dict(target,retrieved_at_utc=before,status=status,final_url=url,
                            content_type=headers.get('Content-Type'),bytes=len(body),
                            sha256=hashlib.sha256(body).hexdigest(),error=error,
                            body_local_ignored=str(path.relative_to(ROOT))))
        print(target['id'],status,len(body),flush=True)
    (ROOT/output).write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--attempt',type=int,default=1)
    parser.add_argument('--targets',default='data/round37_http_targets.json')
    parser.add_argument('--output',default='data/round37_http_retry.json')
    args=parser.parse_args()
    run(args.attempt,args.targets,args.output)
