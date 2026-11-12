#!/usr/bin/env python3
"""Exact known-pair columnar key feasibility, including indistinguishable columns.

This is a relation between two supplied strings, not a ciphertext-only decoder
or a claim that either string is plaintext. Ragged rows have no padding.
"""
import collections
import functools
import math


def validate_key(key):
    if not key or sorted(key) != list(range(len(key))):
        raise ValueError('a permutation of column indices is required')


def encrypt(text, key):
    validate_key(key)
    return ''.join(text[column::len(key)] for column in key)


def decrypt(text, key):
    validate_key(key)
    n, w = len(text), len(key)
    columns = [''] * w
    cursor = 0
    for column in key:
        length = n // w + (column < n % w)
        columns[column] = text[cursor:cursor + length]
        cursor += length
    return ''.join(columns[c][r] for r in range((n + w - 1) // w)
                   for c in range(w) if r < len(columns[c]))


def infer(source, target, width, state_cap=100000, key_cap=256):
    if not 1 <= width <= len(source) or state_cap < 1 or key_cap < 1:
        raise ValueError('invalid width or caps')
    if len(source) != len(target) or collections.Counter(source) != collections.Counter(target):
        return {'status': 'UNSAT', 'states': 0, 'key_count': '0', 'keys_complete': True,
                'keys': [], 'certificate': 'Different length or character histogram.'}
    grouped = collections.defaultdict(list)
    for c in range(width):
        grouped[source[c::width]].append(c)
    classes = sorted(grouped)
    ids = [grouped[text] for text in classes]
    initial = tuple(map(len, ids))
    nodes = 0

    class BudgetExceeded(Exception):
        pass

    def edges(position, remaining):
        for i, text in enumerate(classes):
            if remaining[i] and target.startswith(text, position):
                updated = remaining[:i] + (remaining[i] - 1,) + remaining[i + 1:]
                yield i, position + len(text), updated

    @functools.lru_cache(maxsize=None)
    def count(position, remaining):
        nonlocal nodes
        nodes += 1
        if nodes > state_cap:
            raise BudgetExceeded
        if position == len(target):
            return int(not any(remaining))
        return sum(count(end, updated) for _, end, updated in edges(position, remaining))

    try:
        class_orders = count(0, initial)
    except BudgetExceeded:
        return {'status': 'UNRESOLVED_STATE_CAP', 'states': nodes, 'key_count': None,
                'keys_complete': False, 'keys': [], 'certificate': None}
    if not class_orders:
        return {'status': 'UNSAT', 'states': nodes, 'key_count': '0', 'keys_complete': True,
                'keys': [], 'certificate': 'Complete exact column-class segmentation found no path.'}
    # Indices of equal columns remain distinct keys: their equivalence on this
    # fit string need not persist on a new string or length.
    multiplicity = math.prod(math.factorial(n) for n in initial)
    total = class_orders * multiplicity
    keys = []

    def visit(position, remaining, used, prefix):
        if len(keys) >= key_cap:
            return
        if position == len(target):
            keys.append(prefix)
            return
        for group, end, updated in edges(position, remaining):
            if not count(end, updated):
                continue
            for column in ids[group]:
                if not used & (1 << column):
                    visit(end, updated, used | (1 << column), prefix + [column])
                    if len(keys) >= key_cap:
                        return

    visit(0, initial, 0, [])
    if any(encrypt(source, key) != target for key in keys):
        raise AssertionError('invalid key witness')
    return {'status': 'SAT', 'states': nodes, 'key_count': str(total), 'keys_complete': total <= key_cap,
            'keys': keys, 'certificate': None, 'column_classes': len(classes),
            'class_order_count': str(class_orders), 'equal_column_key_multiplicity': str(multiplicity)}


def apply(text, config, key):
    if config['reverse_input']:
        text = text[::-1]
    text = (encrypt if config['operation'] == 'encrypt' else decrypt)(text, key)
    return text[::-1] if config['reverse_output'] else text


def configurations(widths):
    return [{'width': w, 'operation': op, 'reverse_input': ri, 'reverse_output': ro}
            for w in widths for op in ('encrypt', 'decrypt') for ri in (False, True) for ro in (False, True)]


def fit_pair(source, target, widths=range(2, 33), state_cap=100000, key_cap=256):
    rows = []
    for config in configurations(widths):
        s = source[::-1] if config['reverse_input'] else source
        t = target[::-1] if config['reverse_output'] else target
        result = infer(s, t, config['width'], state_cap, key_cap) if config['operation'] == 'encrypt' else infer(t, s, config['width'], state_cap, key_cap)
        if any(apply(source, config, key) != target for key in result['keys']):
            raise AssertionError('oriented witness failed')
        rows.append({'config': config, 'result': result})
    fits = [r for r in rows if r['result']['status'] == 'SAT']
    unresolved = [r for r in rows if r['result']['status'] == 'UNRESOLVED_STATE_CAP']
    return {'parameterizations': len(rows), 'satisfiable_parameterizations': len(fits),
            'unresolved_parameterizations': len(unresolved),
            'status': 'SAT' if fits else 'UNRESOLVED_STATE_CAP' if unresolved else 'UNSAT',
            'fits': fits, 'unresolved': unresolved,
            'total_states': sum(r['result']['states'] for r in rows),
            'widths_with_exact_fit': sorted({r['config']['width'] for r in fits})}
