#!/usr/bin/env python3
"""Post-result deductions from all enumerated keys; not additional cipher fitting."""
from collections import Counter
import gzip
import json
from round36_experiment import ROOT, decode_key, emit, load
from round38_experiment import canonical, save, segment_count
from unit_morphism_lexicon import banks
from unit_morphism_solver import word_extensions


def calculate():
    values = json.loads(gzip.decompress((ROOT/'results/round38/real_keys.json.gz').read_bytes()))
    assert values['complete'] and values['count']==3976
    keys = [decode_key(k) for k in values['keys']]
    units = {d:dict(sorted(Counter(k[d] for k in keys).items())) for d in sorted(keys[0])}
    support = sorted({emit('3466',k) for k in keys})
    # Second implementation: explicit word partitions, rather than a trie.
    projected = {canonical({d:k[d] for d in '3456'}) for k in keys}
    independent = {canonical(k) for first in word_extensions('345','FOOL',1,3)
                   for word in support for k in word_extensions('3466',word,1,3,first)}
    assert independent == projected
    lexicon = set(banks()[0]['grapheme1_3'].reverse)
    lengths = sorted({len(w) for w in lexicon})
    certificates = []
    for target in load('data/round38_fixtures.json')['transfer']:
        for raw in dict.fromkeys(target['groups']):
            if set(raw)-set(keys[0]):continue
            predictions = {emit(raw,k) for k in keys}
            if len(predictions)==1:
                output = next(iter(predictions))
                if output not in lexicon and segment_count(output,lexicon,lengths)==0:
                    certificates.append({'source_id':target['id'],'source_group':target['source_group'],
                                         'raw':raw,'unanimous_literal':output,'keys_checked':len(keys),
                                         'word_lexical':False,'dictionary_segmentation_paths':0,
                                         'depends_on_digit2':False})
    controls = load('results/round38/controls.json')
    ranges = {}
    for family in load('data/round38_protocol.json')['controls']['families']:
        rows = [r['result'] for r in controls if r['family']==family]
        positive = sum((r['count'] if r['complete'] else r.get('partial_keys',0))>0 for r in rows)
        exceeds = sum((r['count'] if r['complete'] else r.get('partial_keys',0))>=3976 for r in rows)
        ranges[family] = {
            'positive_count_lower_bound':positive,
            'positive_count_upper_bound':positive+sum(not r['complete'] and not r.get('partial_keys',0) for r in rows),
            'at_least_real_count_lower_bound':exceeds,
            'at_least_real_count_upper_bound':exceeds+sum(not r['complete'] and r.get('partial_keys',0)<3976 for r in rows),
            'limited_reason_counts':dict(Counter(r['reason'] for r in rows if not r['complete']))}
    return {'round':38,'stage':'Post-result deterministic deductions; no new parameters or fits',
            'unit_marginals':units,'3466_support':support,'independent_local_partition_projection_matches':True,
            'projected_3456_keys':[dict(k) for k in sorted(projected)],
            'unchangeable_fragment_obstructions':certificates,'control_count_bounds':ranges,
            'scope':'Bounds concern the finite sampled controls, not confidence intervals. Fragment obstructions exclude extending these conditional keys within the declared lexical model, even if missing digit2were later filled; do not reject word-code or anagram models.'}


if __name__ == '__main__':
    save(ROOT/'results/round38/deductions.json',calculate())
