#!/usr/bin/env python3
"""Recompute V2 gate; preserve failed V1 unchanged."""
import hashlib,json,pathlib
from qualification_gate import evaluate
from homophonic_benchmark_v2 import verify
ROOT=pathlib.Path(__file__).resolve().parents[1]
def assess():
    path=ROOT/'data/homophonic_benchmark_v2_protocol.json';p=json.loads(path.read_text());verify(p)
    result_path=ROOT/'results/homophonic_benchmark_v2.json';r=json.loads(result_path.read_text())
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    if r['protocol_sha256']!=h:raise ValueError('V2protocol hash mismatch')
    out=evaluate(r,p);out.update(version='p02-v2',protocol_sha256=h,result_sha256=hashlib.sha256(result_path.read_bytes()).hexdigest())
    return out
if __name__=='__main__':
    out=assess();(ROOT/'results/p04_gate_v2.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
