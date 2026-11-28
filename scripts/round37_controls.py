#!/usr/bin/env python3
"""Previously exposed, fixed R36 shuffles; descriptive conditional counts only."""
import gzip
import json
from pathlib import Path
from round36_experiment import ROOT, GROUPS, load, verify


def calculate():
    verify('data/round37_controls_manifest.json')
    rows = []
    for fixture in load('data/round36_fixtures.json')['targets']:
        path = ROOT/'results/round36'/(fixture['id']+'.json.gz')
        value = json.loads(gzip.decompress(path.read_bytes()))
        assert value['complete']
        cells = []
        for claim in load('data/round37_claims.json')['anchor_claims']:
            index = GROUPS.index(claim['raw'])
            group = value['marginals'][index]
            n = next((int(r[1]) for r in group['rows'] if r[0] == claim['word']), 0)
            cells.append({'anchor_position':index, 'control_raw':group['raw'], 'word':claim['word'],
                          'conditional_keys':n, 'fraction_of_admissible_keys':n/int(value['count']) if int(value['count']) else None})
        rows.append({'id':fixture['id'], 'kind':fixture['kind'], 'groups':fixture['words'],
                     'unconditioned_keys':int(value['count']), 'claims':cells})
    return {'round':37, 'cases':rows,
            'scope':'Previously exposed fixed controls, selected before new conditioned counts; descriptive only. Fractions count uniformly weighted lexical keys, not probabilities of meaning. No new decoder or significance test.'}


if __name__ == '__main__':
    p = ROOT/'results/round37_controls.json'
    assert not p.exists()
    value = calculate()
    p.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(value,indent=2))
