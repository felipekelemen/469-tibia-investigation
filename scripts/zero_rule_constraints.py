#!/usr/bin/env python3
"""Exact formatter constraints conditional on imported code streams.

No English score. All compatible zero alignments are retained. A deterministic
table can be rejected by a contradiction, without treating copied events as
independent samples or claiming that the imported parse is the true cipher.
"""
import collections


FAMILIES = ([{'name': 'code', 'left': 0, 'right': 0, 'period': 0}] +
            [{'name': f'code_prev{n}', 'left': n, 'right': 0, 'period': 0} for n in [1, 2, 3, 4, 8]] +
            [{'name': 'code_next1', 'left': 0, 'right': 1, 'period': 0}] +
            [{'name': f'window{n}', 'left': n, 'right': n, 'period': 0} for n in [1, 3, 8]] +
            [{'name': f'code_phase{n}', 'left': 0, 'right': 0, 'period': n} for n in [2, 4, 8, 16]] +
            [{'name': 'code_prev1_phase16', 'left': 1, 'right': 0, 'period': 16}])


def feature(codes, index, spec):
    key = tuple('<s>' if j < 0 else '</s>' if j >= len(codes) else codes[j]
                for j in range(index - spec['left'], index + spec['right'] + 1))
    return key + (f"phase={index % spec['period']}",) if spec['period'] else key


def serialize(codes, omitted):
    return ''.join(c[1:] if i in omitted else c for i, c in enumerate(codes))


def alignment_edges(codes, raw, index, position):
    code = codes[index]
    if raw.startswith(code, position):
        yield position + 2, False
    if code.startswith('0') and raw.startswith(code[1:], position):
        yield position + 1, True


def alignments(book, cap=4096):
    """Count all fixed-code alignments and derive forced actions by forward/backward."""
    codes, raw = book['codes'], book['digits']
    n, m = len(codes), len(raw)
    forward = [collections.Counter() for _ in range(n + 1)]
    forward[0][0] = 1
    for i in range(n):
        for position, count in forward[i].items():
            for end, _ in alignment_edges(codes, raw, i, position):
                if end <= m:
                    forward[i + 1][end] += count
    count = forward[n][m]
    backward = [set() for _ in range(n + 1)]
    backward[n] = {m}
    for i in range(n - 1, -1, -1):
        backward[i] = {position for position in forward[i]
                       if any(end in backward[i + 1] for end, _ in alignment_edges(codes, raw, i, position))}
    events = []
    for i, code in enumerate(codes):
        if not code.startswith('0'):
            continue
        possible = set()
        witnesses = {}
        for position in forward[i]:
            for end, omitted in alignment_edges(codes, raw, i, position):
                if end in backward[i + 1]:
                    possible.add(omitted)
                    witnesses.setdefault(omitted, {'raw_start': position, 'raw_end': end,
                                                   'wire': raw[position:end]})
        events.append({'book_id': book['id'], 'index': i, 'code': code,
                       'actions': sorted(possible), 'witnesses': witnesses})
    paths = None
    if count <= cap:
        paths = []
        def visit(i, position, omitted):
            if i == n:
                if position == m:
                    paths.append(tuple(omitted))
                return
            for end, action in alignment_edges(codes, raw, i, position):
                if end in backward[i + 1]:
                    visit(i + 1, end, omitted + [i] if action else omitted)
        visit(0, 0, [])
        assert len(paths) == count
        assert all(serialize(codes, set(path)) == raw for path in paths)
    return {'id': book['id'], 'count': count, 'events': events, 'paths': paths,
            'enumeration_complete': paths is not None}


def forced_conflict(books, aligned, spec):
    buckets = {}
    for book, a in zip(books, aligned):
        for event in a['events']:
            if len(event['actions']) != 1:
                continue
            key = feature(book['codes'], event['index'], spec)
            action = event['actions'][0]
            bucket = buckets.setdefault(key, {})
            witness = {'book_id': book['id'], 'code_index': event['index'], 'code': event['code'],
                       'forced_action': action, 'alignment_count': a['count'],
                       **event['witnesses'][action]}
            bucket.setdefault(action, witness)
            if len(bucket) == 2:
                return {'feature': list(key), 'preserved': bucket[False], 'omitted': bucket[True],
                        'scope': 'Both opposite actions are forced across every compatible alignment of their books.'}
    return None


def solve(books, aligned, spec, node_cap=100000):
    """Existence of ANY shared Boolean table f(feature)->omit, not a classifier."""
    conflict = forced_conflict(books, aligned, spec)
    if conflict:
        return {'status': 'UNSAT_FORCED_CONFLICT', 'certificate': conflict, 'nodes': 0}
    if any(not a['enumeration_complete'] for a in aligned):
        return {'status': 'UNRESOLVED_ALIGNMENT_CAP', 'nodes': 0}
    options = []
    for book, a in zip(books, aligned):
        assignments = {}
        for omitted in a['paths']:
            omitted_set = set(omitted)
            assignment = {}
            valid = True
            for event in a['events']:
                key = feature(book['codes'], event['index'], spec)
                value = event['index'] in omitted_set
                if key in assignment and assignment[key] != value:
                    valid = False
                    break
                assignment[key] = value
            if valid:
                frozen = tuple(sorted(assignment.items()))
                assignments.setdefault(frozen, tuple(omitted))
        if not assignments:
            return {'status': 'UNSAT_WITHIN_BOOK', 'book_id': book['id'],
                    'all_alignments_checked': a['count'], 'nodes': 0}
        options.append((book['id'], [(dict(items), path) for items, path in assignments.items()]))
    nodes = 0
    class SearchLimit(Exception):
        pass
    def search(remaining, table, chosen):
        nonlocal nodes
        nodes += 1
        if nodes > node_cap:
            raise SearchLimit()
        if not remaining:
            return table, chosen
        available = []
        for book_id, candidates in remaining:
            compatible = [(a, path) for a, path in candidates
                          if all(key not in table or table[key] == value for key, value in a.items())]
            if not compatible:
                return None
            available.append((book_id, compatible))
        book_id, candidates = min(available, key=lambda item: (len(item[1]), item[0]))
        rest = [item for item in available if item[0] != book_id]
        for assignment, path in candidates:
            result = search(rest, {**table, **assignment}, {**chosen, book_id: list(path)})
            if result is not None:
                return result
        return None
    try:
        solution = search(options, {}, {})
    except SearchLimit:
        return {'status': 'UNRESOLVED_SEARCH_CAP', 'nodes': nodes}
    if solution is None:
        return {'status': 'UNSAT_EXHAUSTIVE', 'nodes': nodes}
    table, chosen = solution
    for book in books:
        omitted = {i for i, code in enumerate(book['codes'])
                   if code.startswith('0') and table[feature(book['codes'], i, spec)]}
        assert serialize(book['codes'], omitted) == book['digits']
    return {'status': 'SAT', 'nodes': nodes,
            'table': [{'feature': list(key), 'omit': value} for key, value in sorted(table.items())],
            'chosen_omitted_indices': chosen,
            'observed_parameters': len(table), 'scope': 'Exact serialization of supplied code streams; not raw parsing or translation.'}


def predict(book, table_rows, spec):
    table = {tuple(row['feature']): row['omit'] for row in table_rows}
    omitted, unseen = set(), 0
    for i, code in enumerate(book['codes']):
        if code.startswith('0'):
            key = feature(book['codes'], i, spec)
            unseen += key not in table
            if table.get(key, False):  # predeclared unseen default: preserve zero
                omitted.add(i)
    raw = serialize(book['codes'], omitted)
    return {'book_id': book['id'], 'unseen_events': unseen,
            'predicted_raw': raw, 'exact_raw': raw == book['digits']}
