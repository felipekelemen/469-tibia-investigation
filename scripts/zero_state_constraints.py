#!/usr/bin/env python3
"""Exact conditional zero rules with metadata and changing state.

Raw-prefix state is recomputed for EVERY complete alignment. The true code
stream remains supplied. Raw-length seeds define consistency constraints,
not a self-contained causal encoder or a plaintext translation.
"""
import hashlib
import json

from zero_rule_constraints import alignments, serialize


FAMILIES = []
for seed in ['token_length', 'raw_length']:
    for modulus in [2, 4, 16]:
        FAMILIES.append({'name': f'code_{seed}_mod{modulus}', 'seed': seed, 'update': 'constant', 'modulus': modulus})
FAMILIES += [
    {'name': 'code_n_counter32', 'seed': 'token_length', 'update': 'token_counter', 'modulus': 32},
    {'name': 'code_m_raw16', 'seed': 'raw_length', 'update': 'raw_counter', 'modulus': 16},
    {'name': 'code_m_raw32', 'seed': 'raw_length', 'update': 'raw_counter', 'modulus': 32},
    {'name': 'code_n_raw16', 'seed': 'token_length', 'update': 'raw_counter', 'modulus': 16},
    {'name': 'code_n_sum16', 'seed': 'token_length', 'update': 'sum', 'modulus': 16},
    {'name': 'code_m_sum16', 'seed': 'raw_length', 'update': 'sum', 'modulus': 16},
    {'name': 'code_n_xor16', 'seed': 'token_length', 'update': 'xor', 'modulus': 16},
    {'name': 'code_m_xor16', 'seed': 'raw_length', 'update': 'xor', 'modulus': 16},
    {'name': 'code_n_cell16_blockparity', 'seed': 'token_length', 'update': 'block_phase', 'modulus': 2},
    {'name': 'code_shelf_mod16', 'seed': 'shelf_ordinal', 'update': 'constant', 'modulus': 16},
    {'name': 'code_shelf_sum16', 'seed': 'shelf_ordinal', 'update': 'sum', 'modulus': 16},
    {'name': 'code_shelf_raw16', 'seed': 'shelf_ordinal', 'update': 'raw_counter', 'modulus': 16},
]


def state_key(book, index, raw_position, prefix_sum, prefix_xor, spec):
    seed = (len(book['codes']) if spec['seed'] == 'token_length' else
            len(book['digits']) if spec['seed'] == 'raw_length' else book['shelf_ordinal'])
    mode, modulus = spec['update'], spec['modulus']
    code = book['codes'][index]
    if mode == 'block_phase':
        return (code, f'seed={seed % 2}', f'cell={index % 16}', f'block={index // 16 % 2}')
    value = (seed if mode == 'constant' else seed + index if mode == 'token_counter' else
             seed + raw_position if mode == 'raw_counter' else seed + prefix_sum if mode == 'sum' else
             seed ^ prefix_xor if mode == 'xor' else None)
    if value is None:
        raise ValueError('unknown state update')
    return (code, f'state={value % modulus}')


def path_rows(book, omitted, spec):
    mask = set(omitted)
    position, total, xor = 0, 0, 0
    result = []
    for i, code in enumerate(book['codes']):
        width = 1 if i in mask else 2
        if code.startswith('0'):
            result.append({'feature': state_key(book, i, position, total, xor, spec),
                           'omit': i in mask, 'book_id': book['id'], 'code_index': i,
                           'raw_start': position, 'raw_end': position + width})
        position += width
        total += int(code)
        xor ^= int(code)
    return result


def emit(book, spec, table, fallback):
    position, total, xor = 0, 0, 0
    mask, unseen = set(), []
    for i, code in enumerate(book['codes']):
        if code.startswith('0'):
            key = state_key(book, i, position, total, xor, spec)
            if key in table:
                omitted = table[key]
            else:
                if fallback is None:
                    raise ValueError('missing fitted state')
                omitted = fallback.get(code, False)
                unseen.append({'code_index': i, 'feature': list(key)})
            if omitted:
                mask.add(i)
        position += 1 if i in mask else 2
        total += int(code)
        xor ^= int(code)
    raw = serialize(book['codes'], mask)
    return {'book_id': book['id'], 'predicted_raw': raw, 'unseen_events': unseen,
            'raw_length_consistent': len(raw) == len(book['digits']), 'exact_raw': raw == book['digits']}


def solve(books, aligned, spec, node_cap=100000):
    if any(not a['enumeration_complete'] for a in aligned):
        return {'status': 'UNRESOLVED_ALIGNMENT_CAP', 'nodes': 0}
    prepared = []
    forced = {}
    for book, a in zip(books, aligned):
        candidates = {}
        rejected = []
        for path_index, path in enumerate(a['paths']):
            table, witnesses = {}, {}
            conflict = None
            for row in path_rows(book, path, spec):
                key, value = row['feature'], row['omit']
                if key in table and table[key] != value:
                    conflict = {'feature': list(key), 'first': witnesses[key], 'second': row,
                                'alignment_index': path_index}
                    break
                table[key] = value
                witnesses.setdefault(key, row)
            if conflict:
                rejected.append(conflict)
            else:
                signature = tuple(sorted(table.items()))
                candidates.setdefault(signature, (table, witnesses, path_index, list(path)))
        if not candidates:
            return {'status': 'UNSAT_WITHIN_BOOK', 'book_id': book['id'], 'nodes': 0,
                    'raw_alignment_count': a['count'], 'all_alignment_conflicts': rejected}
        options = list(candidates.values())
        # A key is forced by this book only if EVERY compatible complete
        # alignment assigns it the same value. Missing keys are not forced.
        common = set(options[0][0])
        for table, _, _, _ in options[1:]:
            common.intersection_update(table)
        for key in sorted(common):
            values = {option[0][key] for option in options}
            if len(values) != 1:
                continue
            value = values.pop()
            witness = {'book_id': book['id'], 'omit': value,
                       'event': options[0][1][key], 'raw_alignment_count': a['count'],
                       'compatible_option_count': len(options),
                       'model_rejected_alignment_count': len(rejected)}
            if key in forced and forced[key]['omit'] != value:
                return {'status': 'UNSAT_FORCED_CONFLICT', 'nodes': 0,
                        'certificate': {'feature': list(key), 'first': forced[key], 'second': witness}}
            forced.setdefault(key, witness)
        prepared.append((book['id'], options))
    nodes = 0
    class SearchLimit(Exception):
        pass
    def search(todo, table, chosen):
        nonlocal nodes
        nodes += 1
        if nodes > node_cap:
            raise SearchLimit()
        if not todo:
            return table, chosen
        available = []
        for bid, candidates in todo:
            valid = [o for o in candidates if all(k not in table or table[k] == v for k, v in o[0].items())]
            if not valid:
                return None
            available.append((bid, valid))
        bid, options = min(available, key=lambda x: (len(x[1]), x[0]))
        rest = [r for r in available if r[0] != bid]
        for assignment, _, path_index, path in options:
            result = search(rest, {**table, **assignment}, {**chosen, bid: {'alignment_index': path_index, 'omitted': path}})
            if result is not None:
                return result
        return None
    try:
        found = search(prepared, {}, {})
    except SearchLimit:
        return {'status': 'UNRESOLVED_SEARCH_CAP', 'nodes': nodes}
    if found is None:
        return {'status': 'UNSAT_EXHAUSTIVE', 'nodes': nodes}
    table, chosen = found
    if not all(emit(book, spec, table, None)['exact_raw'] for book in books):
        raise AssertionError('fitted state table failed replay')
    return {'status': 'SAT', 'nodes': nodes, 'observed_parameters': len(table),
            'table': [{'feature': list(k), 'omit': v} for k, v in sorted(table.items())],
            'chosen_alignments': chosen}


def planted_action(key, seed):
    material = json.dumps([seed, key], separators=(',', ':')).encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], 'big') / 2**64 < .3


def planted_encode(book, spec, seed):
    position, total, xor = 0, 0, 0
    mask = set()
    for i, code in enumerate(book['codes']):
        if code.startswith('0') and planted_action(state_key(book, i, position, total, xor, spec), seed):
            mask.add(i)
        position += 1 if i in mask else 2
        total += int(code)
        xor ^= int(code)
    return serialize(book['codes'], mask), sorted(mask)
