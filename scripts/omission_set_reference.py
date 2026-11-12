#!/usr/bin/env python3
"""Independent bounded reference: enumerate target omitted-token index sets."""
import collections
import itertools
import math


def enumerate_parses(raw, source, maximum_patterns=1000000):
    n = len(source['codes'])
    omitted_count = 2 * n - len(raw)
    if not 0 <= omitted_count <= n:
        return {'complete': True, 'patterns': 0, 'solutions': []}
    patterns = math.comb(n, omitted_count)
    if patterns > maximum_patterns:
        return {'complete': False, 'patterns': patterns, 'solutions': None}
    inventory = collections.Counter(source['codes'])
    solutions = []
    for indices in itertools.combinations(range(n), omitted_count):
        missing = set(indices)
        remaining = inventory.copy()
        position, codes, wires = 0, [], []
        for i in range(n):
            width = 1 if i in missing else 2
            wire = raw[position:position + width]
            code = '0' + wire if width == 1 else wire
            if not remaining[code]:
                break
            remaining[code] -= 1
            codes.append(int(code))
            wires.append(wire)
            position += width
        else:
            if position != len(raw) or any(remaining.values()):
                raise AssertionError('reference conservation failed')
            solutions.append({'codes': codes, 'wires': wires, 'omitted_indices': list(indices)})
    return {'complete': True, 'patterns': patterns, 'solutions': solutions}
