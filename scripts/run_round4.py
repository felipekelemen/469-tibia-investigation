#!/usr/bin/env python3
"""Resume only complete stages; do not overwrite a frozen finished study."""
import hashlib,json,pathlib
from homophonic_benchmark_v2 import run as qualify,verify
from qualification_gate_v2 import assess
from qualified_tibia_search import run as search
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    p=json.loads((ROOT/'data/homophonic_benchmark_v2_protocol.json').read_text());verify(p)
    result=ROOT/'results/homophonic_benchmark_v2.json'
    if not result.exists():qualify()
    gate=assess();(ROOT/'results/p04_gate_v2.json').write_text(json.dumps(gate,indent=2)+'\n')
    if not gate['gate_passed']:
        print('Qualification did not pass globally; P04not run.');return
    path=ROOT/'results/qualified_tibia_search_v2.json'
    if not path.exists():search()
    else:
        r=json.loads(path.read_text())
        if not r['complete']:raise ValueError('incompleteP04result')
        prot=ROOT/'data/protocols/qualified_search_v2.json'
        if r['protocol_sha256']!=hashlib.sha256(prot.read_bytes()).hexdigest():raise ValueError('P04protocolchanged')
        for source,h in r['protocol']['implementation_hashes'].items():
            if hashlib.sha256((ROOT/source).read_bytes()).hexdigest()!=h:raise ValueError('P04implementation changed:'+source)
        for source,field in [('data/normalized_books.json','input_sha256'),('data/normalized_splits.json','split_sha256')]:
            if hashlib.sha256((ROOT/source).read_bytes()).hexdigest()!=r['protocol'][field]:raise ValueError('P04input changed:'+source)
        for mode in r['protocol']['nulls']:
            if len(r['controls'][mode]['trials'])!=r['protocol']['replicates_each']:raise ValueError('P04controlsincomplete')
        print('Complete recorded P04verified; no rerun.')
if __name__=='__main__':main()
