#!/usr/bin/env python3
"""Exact partial-layout compatibility and symbolic determinant verification.

No English model, fitted cipher, image-count recognition, or historical dating.
"""
import collections
import itertools


def rotate(matrix):
    return [list(row) for row in zip(*matrix[::-1])]


def views(matrix):
    for reflected in (False, True):
        current = [row[::-1] for row in matrix] if reflected else [row[:] for row in matrix]
        for turns in range(4):
            yield reflected, turns, current
            current = rotate(current)


def partial_matches(matrix, pattern):
    """Exact numeric pattern, all D4 views and every contiguous placement."""
    rows, cols = len(pattern), len(pattern[0])
    matches = []
    for reflected, turns, oriented in views(matrix):
        for r in range(len(oriented) - rows + 1):
            for c in range(len(oriented[0]) - cols + 1):
                if all(oriented[r + i][c + j] == pattern[i][j] for i in range(rows) for j in range(cols)):
                    matches.append({'reflected': reflected, 'quarter_turns': turns,
                                    'row_offset': r, 'column_offset': c})
    return matches


def multiply(a, b):
    product = collections.Counter()
    for (ax, ay), av in a.items():
        for (bx, by), bv in b.items():
            product[(ax + bx, ay + by)] += av * bv
    return {key: value for key, value in product.items() if value}


def polynomial_determinant(matrix):
    """Leibniz expansion over exact integers and variables x,y, any small N."""
    n = len(matrix)
    if not n or any(len(row) != n for row in matrix):
        raise ValueError('nonempty square matrix required')
    output = collections.Counter()
    for permutation in itertools.permutations(range(n)):
        parity = sum(permutation[i] > permutation[j] for i in range(n) for j in range(i + 1, n))
        term = {(0, 0): -1 if parity % 2 else 1}
        for row, column in enumerate(permutation):
            value = matrix[row][column]
            factor = {(1, 0): 1} if value == 'x' else {(0, 1): 1} if value == 'y' else {(0, 0): value}
            term = multiply(term, factor)
        for key, value in term.items():
            output[key] += value
    return {key: value for key, value in output.items() if value}


def polynomial_rows(polynomial):
    return [{'x_power': key[0], 'y_power': key[1], 'coefficient': value}
            for key, value in sorted(polynomial.items())]


def evaluate(polynomial, x, y):
    return sum(coefficient * x ** power_x * y ** power_y
               for (power_x, power_y), coefficient in polynomial.items())
