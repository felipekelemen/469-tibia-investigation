#!/usr/bin/env python3
"""Raw-fragment -> supplied-code dictionary parser. No language scoring.

Each entry comes from inside one source book at compatible code boundaries.
The objective minimizes uncovered raw digits, then copied pieces. Uniqueness
is conditional on this finite dictionary/objective, never a semantic claim.
"""
from zero_rule_constraints import alignments, serialize


def build_dictionary(books, minimum=8, maximum=96, alignment_cap=4096):
    entries = {}
    source_alignments = 0
    for b in books:
        a = alignments(b, alignment_cap)
        if not a['count'] or not a['enumeration_complete']:
            raise ValueError('invalid source or incomplete source alignments')
        source_alignments += a['count']
        codes = b['codes']
        for alignment_index, omitted in enumerate(a['paths']):
            mask = set(omitted)
            offsets = [0]
            for i in range(len(codes)):
                offsets.append(offsets[-1] + (1 if i in mask else 2))
            if offsets[-1] != len(b['digits']):
                raise AssertionError('bad source alignment')
            for start in range(len(codes)):
                for end in range(start + 1, len(codes) + 1):
                    length = offsets[end] - offsets[start]
                    if length > maximum:
                        break
                    if length < minimum:
                        continue
                    raw = b['digits'][offsets[start]:offsets[end]]
                    output = tuple(int(c) for c in codes[start:end])
                    variants = entries.setdefault(raw, {})
                    if output not in variants:
                        local_mask = [i - start for i in omitted if start <= i < end]
                        if serialize(codes[start:end], set(local_mask)) != raw:
                            raise AssertionError('dictionary witness failed roundtrip')
                        variants[output] = {'source_book_id': b['id'], 'source_code_start': start,
                                            'source_code_end': end, 'source_raw_start': offsets[start],
                                            'source_raw_end': offsets[end], 'alignment_index': alignment_index,
                                            'omitted_relative_indices': local_mask}
    return {'entries': entries, 'minimum': minimum, 'maximum': maximum,
            'source_books': len(books), 'source_alignments': source_alignments}


def parse(raw, dictionary, minimum, stream_cap=512):
    if any(c not in '0123456789' for c in raw):
        raise ValueError('raw ASCII digits required')
    if minimum < dictionary['minimum'] or stream_cap < 1:
        raise ValueError('invalid minimum/cap')
    n = len(raw)
    edges = [[] for _ in range(n)]
    for start in range(n):
        #100..109 are unknown raw-digit markers, never code IDs or letters.
        edges[start].append({'end': start + 1, 'codes': (100 + int(raw[start]),),
                             'cost': (1, 0), 'witness': None})
        for end in range(start + minimum, min(n, start + dictionary['maximum']) + 1):
            variants = dictionary['entries'].get(raw[start:end], {})
            for codes, witness in sorted(variants.items()):
                edges[start].append({'end': end, 'codes': codes, 'cost': (0, 1), 'witness': witness})
    best = [None] * (n + 1)
    best[n] = (0, 0)
    optimal = [[] for _ in range(n)]
    counts = [0] * (n + 1)
    counts[n] = 1
    streams = [set() for _ in range(n + 1)]
    streams[n] = {()}
    complete = [True] * (n + 1)
    for start in range(n - 1, -1, -1):
        def cost(edge):
            tail = best[edge['end']]
            return (edge['cost'][0] + tail[0], edge['cost'][1] + tail[1])
        best[start] = min(cost(e) for e in edges[start])
        optimal[start] = [e for e in edges[start] if cost(e) == best[start]]
        for edge in optimal[start]:
            end = edge['end']
            counts[start] += counts[end]
            complete[start] &= complete[end]
            for suffix in streams[end]:
                streams[start].add(edge['codes'] + suffix)
            if len(streams[start]) > stream_cap:
                complete[start] = False
                streams[start] = set(sorted(streams[start])[:stream_cap])
    # Representative path chosen by fixed ordering only, never English.
    path = []
    start = 0
    while start < n:
        edge = optimal[start][0]
        path.append({'raw_start': start, 'raw_end': edge['end'], 'raw': raw[start:edge['end']],
                     'codes': list(edge['codes']) if edge['witness'] else None, 'witness': edge['witness']})
        start = edge['end']
    if ''.join(x['raw'] for x in path) != raw:
        raise AssertionError('target reconstruction failed')
    unique = next(iter(streams[0])) if best[0][0] == 0 and complete[0] and len(streams[0]) == 1 else None
    return {'raw_length': n, 'uncovered_raw_digits': best[0][0], 'copied_pieces': best[0][1],
            'optimal_dictionary_paths': str(counts[0]), 'stream_enumeration_complete': complete[0],
            'retained_distinct_streams': len(streams[0]), 'streams': [list(s) for s in sorted(streams[0])],
            'unique_full_codes': None if unique is None else list(unique),
            'representative_path': path,
            'scope': 'Codes are labels inherited from source fragments. Residual digits and alternative parses are not repaired.'}


def raw_novelty(raw, source_books, lengths=(8, 12, 16, 24)):
    rows = []
    for k in lengths:
        known = {b['digits'][i:i + k] for b in source_books for i in range(len(b['digits']) - k + 1)}
        windows = [(i, raw[i:i + k]) for i in range(max(0, len(raw) - k + 1))]
        novel = [i for i, text in windows if text not in known]
        rows.append({'raw_k': k, 'windows': len(windows), 'novel_windows': len(novel),
                     'novel_window_starts': novel, 'shared_window_fraction': 1 - len(novel) / len(windows) if windows else None})
    return rows
