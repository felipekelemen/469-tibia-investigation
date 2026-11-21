#!/usr/bin/env python3
"""Integrity, exact certificates and diagnostic replay; --full refits all cases."""
from pathlib import Path
import argparse
import json
import tempfile
from round27_experiment import (ROOT, diagnostics, fit_case, run, summarize, verify_manifest)
from round27_fixtures import training_bank
from round27_witness_solver import emit


def check(full=False):
    verify_manifest('round27_experiment_manifest.json')
    verify_manifest('round27_result_manifest.json')
    protocol = json.loads((ROOT/'data/round27_protocol.json').read_text())
    fixtures = json.loads((ROOT/'data/round27_fixtures.json').read_text())
    result = json.loads((ROOT/'results/round27_qualification.json').read_text())
    assert summarize(result['cases'], protocol) == result['summary']
    assert diagnostics(fixtures) == result['diagnostics']
    bank = training_bank(protocol)
    assert fit_case(fixtures['cases'][0], protocol['scenarios'][0], protocol, bank) == result['cases'][0]
    for case in result['cases']:
        for query in case['queries']:
            if query['status'] != 'SAT':
                continue
            key = query['key']
            assert all(emit(raw, key) in bank.reverse for raw in case['train'])
            exclude = query['exclusion']
            if 'different_key' in exclude:
                assert any(key[d] != u for d, u in exclude['different_key'].items())
            if 'different_form' in exclude:
                raw, form = exclude['different_form']
                assert emit(raw, key) != form
    if full:
        with tempfile.TemporaryDirectory(prefix='round27-') as temp:
            run(Path(temp))
            replay = json.loads((Path(temp)/'round27_qualification.json').read_text())
            assert replay == result
    print('Round27: hashes, aggregates, SAT witnesses, 60 diagnostics and first fit replayed.'
          + (' All 120 fits reproduced.' if full else ' Use --full to refit all 120 cases.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    check(parser.parse_args().full)
