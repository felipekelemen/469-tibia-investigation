#!/usr/bin/env python3
"""Offline reproduction; all controls are rerun with --full, never overwritten."""
import argparse
import hashlib
import json
from round29_models import ROOT, compare, fit_english
from round29_experiment import verify_inputs, run, summarize
from round29_fixtures import create
from round29_corpus_audit import audit
from round29_certificates import verify
from round29_summary import build


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args()
    load=lambda p:json.loads((ROOT/p).read_text())
    verify_inputs()
    for path,sha in load('data/round29_result_manifest.json')['sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
    protocol=load('data/round29_protocol.json');fixtures=load('data/round29_fixtures.json')
    result=load('results/round29_qualification.json');language=fit_english(protocol['english_training_sources'])
    assert create(protocol)==fixtures
    assert {k:v for k,v in language.items() if k!='table'}==load('data/round29_english_model.json')
    assert summarize(result['rows'],protocol)==result['summary']
    assert audit(fixtures,result)==load('results/round29_corpus_audit.json')
    assert verify(result,fixtures,language)==load('results/round29_certificates.json')
    assert build()==load('results/round29_summary.json')
    if args.full:
        assert run(protocol,fixtures,language)==result
    else:
        for row in result['rows'][:8]:
            sequences=fixtures['cases'][0]['datasets'][row['profile']]
            assert compare(sequences[:50],sequences[50:],language)==row['comparison']
    print('Round29: frozen hashes, fixtures, language model, gates, source/copy audit, all50400selected-model document lengths and descriptive aggregates verified.'
          + (' All240corpora fully refitted.' if args.full else ' First8corpora refitted; use --full for all240.'))
