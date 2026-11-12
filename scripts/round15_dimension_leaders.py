#!/usr/bin/env python3
"""Descriptive dimension-specific summaries of the already frozen family.

Post-search diagnostic only: no new keys, language model or semantic claims;
no dimension-specific p-values. Primary nulls searched the entire family.
"""
import json

from dimension_name_experiments import (ROOT, decode, dump, language_model,
    numeric_pairs, search)


def build():
    bank = json.loads((ROOT / 'data/round15_candidate_catalog.json').read_text())['candidates']
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    split = json.loads((ROOT / 'data/normalized_splits.json').read_text())
    selected = json.loads((ROOT / 'results/round15_matrix_search.json').read_text())['branches']
    rows = []
    for branch in selected:
        q, layer = branch['q'], branch['layer']
        model = language_model(q)
        values = [numeric_pairs(b['digits']) if layer == 'raw_fixed_pairs_offset0' else list(map(int, b['codes'])) for b in books]
        train = [arr for arr, b in zip(values, books) if b['id'] in split['discovery_book_ids']]
        for n in (3, 4, 5):
            subset = [c for c in bank if (c['q'], c['n']) == (q, n)]
            if not subset:
                continue
            c, score = search(train, subset, model)
            out = decode(values, c)
            rows.append(dict(q=q, layer=layer, n=n, candidate_count=len(subset),
                             selected_id=c['id'], train_score=score,
                             books=[dict(id=b['id'], output=t) for b, t in zip(books, out)]))
    return dict(scope='Descriptive post-search dimension summaries of frozen candidates; no new fitted rules or dimension-specific significance claims.', branches=rows)


if __name__ == '__main__':
    result = build()
    dump('results/round15_dimension_leaders.json', result)
    print('Dimension-specific leaders saved:' + str(len(result['branches'])))
