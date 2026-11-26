#!/usr/bin/env python3
"""Offline verification, with an optional complete repeat of all new count jobs."""
import argparse
import json
from pathlib import Path
import tempfile
from round33_audit import ROOT,load,build,verify
from round33_experiment import compile_engine,qualify,run_case
from unit_morphism_lexicon import banks


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args()
    assert build()==load('results/round33_summary.json')
    publication=ROOT/'data/round33_result_manifest.json'
    if publication.exists():verify('data/round33_result_manifest.json')
    fixtures=load('data/round33_fixtures.json');protocol=load('data/round33_protocol.json')
    expected={r['id']:r for r in load('results/round33_counts.json')['cases']}
    selected=fixtures['cases'] if args.full else [r for r in fixtures['cases'] if r['id']=='knightmare']
    with tempfile.TemporaryDirectory(prefix='469-r33-replay-') as directory:
        binary=compile_engine(directory)
        tiny=qualify(binary,directory,fixtures,protocol)
        assert tiny==load('results/round33_count_qualification.json')
        lex=Path(directory)/'lexicon';lex.write_text(''.join(w+'\n' for w in sorted(banks()[0]['grapheme1_3'].reverse)))
        for case in selected:
            actual=run_case(binary,lex,case,directory,protocol['budgets'])
            prior=expected[case['id']]
            # Wall-clock timing is not a reproducible scientific result.
            assert {k:v for k,v in actual.items() if k!='elapsed_seconds'}=={k:v for k,v in prior.items() if k not in ['id','kind','elapsed_seconds']},case['id']
    print('R33:100independent tiny counts and',len(selected),'main count jobs reproduced; preserved results and independent total checked. No validated translation.')
