#!/usr/bin/env python3
"""Verify/resume completed V3/V4 studies without changing frozen protocols."""
import json,pathlib,hashlib
from copied_benchmark_v3 import run as run3,verify as verify3
from copied_benchmark_v4 import run as run4,verify as verify4
from copied_v3_gate import assess as assess3
from copied_v4_gate import assess as assess4
from qualified_tibia_v4 import run as search4
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for n,verify,run,assess in [(3,verify3,run3,assess3),(4,verify4,run4,assess4)]:
        protocol=ROOT/f'data/copied_benchmark_v{n}_protocol.json';p=json.loads(protocol.read_text());verify(p)
        result=ROOT/f'results/copied_benchmark_v{n}.json'
        if not result.exists():run()
        gate=assess();(ROOT/f'results/copied_v{n}_gate.json').write_text(json.dumps(gate,indent=2)+'\n')
        print('V'+str(n),'gate',gate['gate_passed'])
    if not assess4()['gate_passed']:
        print('V4qualification failed: no newgame fit.');return
    result=ROOT/'results/qualified_tibia_search_v4.json'
    if not result.exists():search4()
    else:
        r=json.loads(result.read_text());protocol=ROOT/'data/protocols/qualified_search_v4.json'
        if not r['complete'] or r['protocol_sha256']!=digest(protocol):raise ValueError('incomplete or changedP04result')
        for f,h in r['protocol']['implementation_hashes'].items():
            if digest(ROOT/f)!=h:raise ValueError('P04implementation changed:'+f)
        for source,field in [('data/normalized_books.json','input_sha256'),('data/normalized_splits.json','split_sha256')]:
            if digest(ROOT/source)!=r['protocol'][field]:raise ValueError('P04input changed')
        for mode in r['protocol']['nulls']:
            if len(r['controls'][mode]['trials'])!=99:raise ValueError('incompletecontrols')
        print('Recorded V4qualifiedsearch verified; no rerun.')
if __name__=='__main__':main()
