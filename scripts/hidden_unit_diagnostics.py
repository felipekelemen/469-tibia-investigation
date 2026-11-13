#!/usr/bin/env python3
"""Post-qualification explanation; no retuning, new learner or game fitting."""
import collections

from hidden_unit_benchmark import (FAMILIES, STYLES, fixture, fingerprint, load,
                                   dump)
from hidden_unit_segmenter import fixed_tokens, fit_periodic, mdl_counts
from numeric_word_codec import complete_parse, unique_decodability


def equal_mdl_lexicons():
    common = ['0'+f'{i:04d}' for i in range(61)]
    a, b = ['1234', '5678', '9012']+common, ['12345', '678', '9012']+common
    # 70messages x32units, each of64types used35times. Both lexicons fit
    # every message with the same token counts and equal dictionary costs.
    first = ['1234', '5678', '9012']+common[:29]
    second = common[29:]
    training = [''.join(first if i % 2 == 0 else second) for i in range(70)]
    parsed_a = [complete_parse(raw, a) for raw in training]
    parsed_b = [complete_parse(raw, b) for raw in training]
    assert all(r['count'] == 1 for r in parsed_a+parsed_b)
    ca = collections.Counter(w for row in parsed_a for w in row['unique_path'])
    cb = collections.Counter(w for row in parsed_b for w in row['unique_path'])
    assert len(ca) == len(cb) == 64 and set(ca.values()) == set(cb.values()) == {35}
    return {'dictionary_A': a, 'dictionary_B': b,
            'A_decodability': unique_decodability(a), 'B_decodability': unique_decodability(b),
            'training_raw': training, 'messages': len(training), 'units_per_message': 32,
            'A_unit_counts': dict(ca), 'B_unit_counts': dict(cb),
            'A_mdl_objective': mdl_counts(ca), 'B_mdl_objective': mdl_counts(cb),
            'new_combination': {'raw': '12349012', 'A': complete_parse('12349012', a), 'B': complete_parse('12349012', b)},
            'same_raw_different_cuts': {'raw': '123456789012', 'A': complete_parse('123456789012', a), 'B': complete_parse('123456789012', b)},
            'scope': 'Constructive ambiguity with both keys prefix-free,64types,allused35times,3..8digit units and32units/message. No English labels. A distributional counterexample, not a claim that these artificial numbers are469.'}


def build():
    qualification = load('results/round17_qualification.json')
    widths = {}
    for style in STYLES:
        widths[style] = dict(collections.Counter(str(fit['selected_width']) for row in qualification['rows']
            if row['metadata']['family'] == FAMILIES[0] and row['metadata']['training_style'] == style
            for fit in row['fits'] if fit['config'] == 'periodic_mdl'))
    examples = []
    for i in (0, 1):
        f = fixture(i, FAMILIES[0], STYLES[1], 'qualification')
        fitted = fit_periodic(f['train'])
        oracle_counts = collections.Counter(w for raw in f['train'] for w in fixed_tokens(raw, 2))
        original = next(row for row in qualification['rows'] if row['metadata'] == f['metadata'])
        recorded = next(v for v in original['fits'] if v['config'] == 'periodic_mdl')
        assert fingerprint(fitted) == recorded['model_sha256']
        examples.append({'case': i, 'source': f['metadata']['source'], 'selected_width': fitted['width'],
                         'selected_objective': fitted['train_objective'],
                         'true_width2_objective': mdl_counts(oracle_counts)+4,
                         'true_width_supplied_only_for_diagnostic': True})
    return {'width_histogram_character_fixture': widths, 'known_truth_comparisons': examples,
            'equal_mdl_same_cardinality_counterexample': equal_mdl_lexicons(),
            'stage': 'Post-qualification explanatory diagnostics; no changed parameters or game application.'}


if __name__ == '__main__':
    dump('results/round17_failure_diagnostics.json', build())
    print('Failure explanation and equal-cost64unit counterexample saved.')
