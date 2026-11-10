#!/usr/bin/env python3
"""Optional fresh fetch, preserving original evidence. Pages may change.

Uses standard inherited proxy/TLS settings; never weakens certificate verification.
Results go to an ignored directory, leaving recorded evidence untouched.
"""
import datetime,hashlib,json,pathlib,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'data/historical_refresh';out.mkdir(exist_ok=True)
    rows=[]
    for i,old in enumerate(json.loads((ROOT/'data/historical_sources/manifest.json').read_text())):
        row={'url':old['url'],'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        try:
            req=urllib.request.Request(old['url'],headers={'User-Agent':'Tibia469Research/1.0 (source audit)'})
            with urllib.request.urlopen(req,timeout=20) as response:
                body=response.read();row.update(status=response.status,final_url=response.url)
        except urllib.error.HTTPError as exc:
            body=exc.read();row.update(status=exc.code,final_url=exc.url)
        except (OSError,urllib.error.URLError) as exc:
            row['error']=str(exc);rows.append(row);continue
        filename=f'{i:02d}.html';(out/filename).write_bytes(body)
        row.update(file=filename,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),matches_recorded_hash=hashlib.sha256(body).hexdigest()==old['sha256'])
        rows.append(row)
    (out/'manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
