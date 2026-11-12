#!/usr/bin/env python3
"""Exact multiset-conserving raw parsing, conditional on a supplied source.

Counts omission/segmentation paths, not plaintexts. Exhaustion is UNSAT only
when complete. A state or stream cap never establishes uniqueness.
"""
import collections
import functools

from zero_rule_constraints import alignments


def source_inventories(book, mode):
    counts = collections.Counter(book['codes'])
    if mode == 'code_multiset':
        return [tuple((int(code), count, (code, code[1:]) if code.startswith('0') else (code,))
                      for code, count in sorted(counts.items()))]
    if mode != 'wire_multiset':
        raise ValueError('unknown conservation mode')
    a = alignments(book)
    if not a['count'] or not a['enumeration_complete']:
        raise ValueError('source alignments incomplete or impossible')
    inventories = set()
    for omitted in a['paths']:
        mask = set(omitted)
        counts = collections.Counter((int(c), c[1:] if i in mask else c) for i, c in enumerate(book['codes']))
        inventories.add(tuple((code, count, (wire,)) for (code, wire), count in sorted(counts.items())))
    return sorted(inventories)


def solve(raw, inventory, state_cap=1000000, stream_cap=256):
    if set(raw) - set('0123456789') or state_cap < 1 or stream_cap < 1:
        raise ValueError('invalid raw or caps')
    for code, count, forms in inventory:
        if not 0 <= code <= 99 or count < 1 or not forms or len(set(forms)) != len(forms):
            raise ValueError('invalid inventory')
        if any(w not in (f'{code:02d}', f'{code:02d}'[1:] if code < 10 else f'{code:02d}') for w in forms):
            raise ValueError('invalid wire form')
    initial = tuple(item[1] for item in inventory)
    lengths_min = tuple(min(map(len, item[2])) for item in inventory)
    lengths_max = tuple(max(map(len, item[2])) for item in inventory)
    nodes = 0

    class BudgetExceeded(Exception):
        pass

    def edges(position, remaining):
        for i, (code, _, forms) in enumerate(inventory):
            if not remaining[i]:
                continue
            for wire in forms:
                if raw.startswith(wire, position):
                    updated = remaining[:i] + (remaining[i] - 1,) + remaining[i + 1:]
                    yield position + len(wire), updated, code, wire

    @functools.lru_cache(maxsize=None)
    def count_paths(position, remaining):
        nonlocal nodes
        nodes += 1
        if nodes > state_cap:
            raise BudgetExceeded
        available = len(raw) - position
        if not sum(remaining):
            return int(available == 0)
        if not sum(c * w for c, w in zip(remaining, lengths_min)) <= available <= sum(c * w for c, w in zip(remaining, lengths_max)):
            return 0
        return sum(count_paths(end, updated) for end, updated, _, _ in edges(position, remaining))

    try:
        total = count_paths(0, initial)
    except BudgetExceeded:
        return {'status': 'UNRESOLVED_STATE_CAP', 'states': nodes, 'path_count': None,
                'count_complete': False, 'streams_complete': False, 'streams': [], 'unique_codes': None}
    if not total:
        return {'status': 'UNSAT', 'states': nodes, 'path_count': '0', 'count_complete': True,
                'streams_complete': True, 'streams': [], 'unique_codes': None}

    @functools.lru_cache(maxsize=None)
    def outputs(position, remaining):
        if not sum(remaining):
            return {()}, True
        streams, complete = set(), True
        for end, updated, code, _ in edges(position, remaining):
            if not count_paths(end, updated):
                continue
            suffixes, suffix_complete = outputs(end, updated)
            complete &= suffix_complete
            streams.update((code,) + suffix for suffix in suffixes)
            if len(streams) > stream_cap:
                complete = False
                streams = set(sorted(streams)[:stream_cap])
        return streams, complete

    streams, complete = outputs(0, initial)
    return {'status': 'SAT', 'states': nodes, 'path_count': str(total), 'count_complete': True,
            'streams_complete': complete, 'streams': [list(s) for s in sorted(streams)],
            'unique_codes': list(next(iter(streams))) if complete and len(streams) == 1 else None}


def solve_source(raw, source, mode, state_cap=1000000, stream_cap=256):
    rows = [solve(raw, inventory, state_cap, stream_cap) for inventory in source_inventories(source, mode)]
    status = 'SAT' if any(r['status'] == 'SAT' for r in rows) else 'UNSAT' if all(r['status'] == 'UNSAT' for r in rows) else 'UNRESOLVED_STATE_CAP'
    complete = all(r['count_complete'] and r['streams_complete'] for r in rows)
    streams = {tuple(s) for r in rows for s in r['streams']}
    # A partially explored alternative inventory prevents a uniqueness claim.
    return {'mode': mode, 'status': status, 'source_inventory_alternatives': len(rows),
            'all_counts_complete': all(r['count_complete'] for r in rows),
            'all_streams_complete': complete, 'distinct_retained_code_streams': len(streams),
            'unique_codes': list(next(iter(streams))) if complete and len(streams) == 1 else None,
            'inventories': rows}
