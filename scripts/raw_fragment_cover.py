#!/usr/bin/env python3
"""Exact raw-fragment covering, with no inherited token boundaries or meanings."""


def cover(raw, books, minimum=1, maximum=96):
    n = len(raw)
    best = [None] * (n + 1)
    paths = [None] * (n + 1)
    best[n] = (0, 0)
    paths[n] = []
    for start in range(n - 1, -1, -1):
        best[start] = (best[start + 1][0] + 1, best[start + 1][1])
        paths[start] = [{'raw_start': start, 'raw_end': start + 1, 'literal': raw[start], 'source': None}] + paths[start + 1]
        for end in range(start + minimum, min(n, start + maximum) + 1):
            text = raw[start:end]
            witness = None
            for book in books:
                position = book['digits'].find(text)
                if position >= 0:
                    witness = {'book_id': book['id'], 'raw_start': position, 'raw_end': position + len(text)}
                    break
            if witness is not None:
                cost = (best[end][0], best[end][1] + 1)
                if cost < best[start]:
                    best[start] = cost
                    paths[start] = [{'raw_start': start, 'raw_end': end, 'literal': text, 'source': witness}] + paths[end]
    assert ''.join(x['literal'] for x in paths[0]) == raw
    byid = {b['id']: b for b in books}
    for row in paths[0]:
        if row['source']:
            s = row['source']
            assert byid[s['book_id']]['digits'][s['raw_start']:s['raw_end']] == row['literal']
    return {'minimum': minimum, 'uncovered_raw_digits': best[0][0], 'copied_pieces': best[0][1],
            'path': paths[0], 'scope': 'Raw string copies only; no code stream or plaintext inferred.'}
