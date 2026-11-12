#!/usr/bin/env python3
"""Offline round15 replay. --full also refits every randomized candidate bank.

Default replay regenerates positives, refits observed branches, checks each
recorded null winner's literal score and p. It does not independently certify
that each null winner is maximal; use --full for that complete replay.
"""
import argparse
import json
import math
import random

from dimension_name_experiments import (ROOT, SEED, algebra, catalog, decode, digraphs,
    external_predictions, fixed_score, language_model, numeric_pairs, qualifications,
    randomized, search, sha)
from round15_dimension_leaders import build as dimension_leaders


def require(value, message):
    if not value:
        raise ValueError(message)


def same_score(a, b):
    # NumPy may reduce a single gathered row and a batched strided row in a
    # different order. This is far below meaningful model score differences.
    return a == b if a is None or b is None else math.isclose(a, b, rel_tol=0., abs_tol=1e-11)


def main(full=False):
    manifest = json.loads((ROOT / 'data/round15_evidence_manifest.json').read_text())
    for path, expected in manifest['sha256'].items():
        require(sha(path) == expected, 'frozen input changed: ' + path)
    result_manifest = json.loads((ROOT / 'data/round15_result_manifest.json').read_text())
    for path, expected in result_manifest['sha256'].items():
        require(sha(path) == expected, 'result artifact changed: ' + path)
    protocol = json.loads((ROOT / 'data/round15_protocol.json').read_text())
    frozen_catalog = json.loads((ROOT / 'data/round15_candidate_catalog.json').read_text())
    bank = catalog()
    require(bank == frozen_catalog['candidates'], 'catalog changed')
    models = {q: language_model(q) for q in {c['q'] for c in bank}}
    positive = qualifications(bank, models, protocol)
    require(positive == json.loads((ROOT / 'results/round15_qualification.json').read_text()), 'positive replay changed')
    require(all(r['gate_passed'] for r in positive['summary']), 'qualification failed')
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    split = json.loads((ROOT / 'data/normalized_splits.json').read_text())
    discovery = [i for i, b in enumerate(books) if b['id'] in split['discovery_book_ids']]
    held = [i for i, b in enumerate(books) if b['id'] in split['holdout_book_ids']]
    inventory = json.loads((ROOT / 'data/source_validation_inventory.json').read_text())
    kharos = json.loads((ROOT / 'data/external_book_round10.json').read_text())
    dimension = json.loads((ROOT / 'results/round15_dimension_analysis.json').read_text())
    require(dimension == dict(algebra=algebra(), digraphs=digraphs(books, inventory)), 'algebra/digraph replay changed')
    require(dimension_leaders() == json.loads((ROOT / 'results/round15_dimension_leaders.json').read_text()), 'dimension leader replay changed')
    result = json.loads((ROOT / 'results/round15_matrix_search.json').read_text())
    require(result['complete'] and len(result['branches']) == 4, 'incomplete game search')
    for row in result['branches']:
        values = [numeric_pairs(b['digits']) if row['layer'] == 'raw_fixed_pairs_offset0' else [int(c) for c in b['codes']] for b in books]
        q, c = row['q'], bank[row['winner_id']]
        qbank = [v for v in bank if v['q'] == q]
        selected, maximum = search([values[i] for i in discovery], qbank, models[q])
        require(selected['id'] == c['id'] and same_score(maximum, row['train_score']), 'observed winner changed')
        require(same_score(fixed_score([values[i] for i in held], c, models[q]), row['exposed_holdout_score']), 'holdout score changed')
        require(decode(values, c) == [r['output'] for r in row['books']], 'literal game outputs changed')
        if row['layer'] == 'raw_fixed_pairs_offset0':
            require(row['external_unfitted'] == external_predictions(c, inventory, kharos), 'external prediction changed')
        for control in row['nulls']:
            rng = random.Random(SEED + protocol['nulls']['families'].index(control['kind']))
            for trial in control['results']:
                null = randomized(values, control['kind'], rng)
                winner = bank[trial['selected_id']]
                require(same_score(fixed_score([null[i] for i in discovery], winner, models[q]), trial['train_max']), 'null winner score changed')
                require(same_score(fixed_score([null[i] for i in held], winner, models[q]), trial['exposed_holdout_score']), 'null held score changed')
                if full:
                    fitted, score = search([null[i] for i in discovery], qbank, models[q])
                    require(fitted['id'] == winner['id'] and same_score(score, trial['train_max']), 'null maximum changed')
            p = (1+sum(r['train_max'] >= row['train_score'] for r in control['results']))/(1+len(control['results']))
            require(p == control['train_familywise_empirical_p'], 'empirical p changed')
            require(min(1., 4*p) == control['four_branch_bonferroni_p'], 'branch correction changed')
    print('Round15: 1860 candidates; 150/150 exact held synthetic recoveries; 4 observed refits; 468 null winner scores; algebra and external literals replayed.')
    print('Null maximality: ' + ('all 468 full family refits repeated.' if full else 'recorded/hash-bound; use --full to refit all 468 families.'))
    print('No independently verified game translation. Exposed split and unproved input parsers remain limitations.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    main(parser.parse_args().full)
