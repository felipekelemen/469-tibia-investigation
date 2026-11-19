#!/usr/bin/env python3
"""Reproduce selected published mechanics; never treat self-output as English GT."""
import argparse
import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import re

ROOT = Path(__file__).resolve().parents[1]


def upstream_functions():
    path = ROOT / 'data/round24_reference/c2_generative_mdl.py'
    tree = ast.parse(path.read_text())
    names = {'tile', 'gamma_bits', 'two_part_module_code'}
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in selected} == names
    env = {'math': math, 'log2': math.log2, 'Counter': Counter}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), env)
    return env


def encode_modules(strings, modules):
    """Independent JSON representation. All required literal payload is explicit."""
    inventory = [value for _, value, _ in modules]
    starts = {book: {} for book in strings}
    for index, value, occurrences in modules:
        for book, pos in occurrences:
            assert pos not in starts[book]
            assert strings[book][pos:pos + len(value)] == value
            starts[book][pos] = index
    books = {}
    for book, text in strings.items():
        items, literal, pos = [], '', 0
        while pos < len(text):
            if pos in starts[book]:
                if literal:
                    items.append(['literal', literal]); literal = ''
                index = starts[book][pos]
                items.append(['module', index]); pos += len(inventory[index])
            else:
                literal += text[pos]; pos += 1
        if literal:
            items.append(['literal', literal])
        books[book] = items
    return {'inventory': inventory, 'books': books}


def decode_modules(payload):
    # No corpus or original strings are supplied to this function.
    return {book: ''.join(payload['inventory'][v] if k == 'module' else v
                         for k, v in items) for book, items in payload['books'].items()}


def independent_bits(payload, alpha=10):
    gamma = lambda n: 2 * n.bit_length() - 1
    inventory, books = payload['inventory'], payload['books']
    model = gamma(len(inventory) + 1) + sum(gamma(len(s)) + len(s) * math.log2(alpha) for s in inventory)
    data = gamma(len(books) + 1)
    for items in books.values():
        data += gamma(len(items) + 1)
        for kind, value in items:
            data += 1
            if kind == 'module':
                data += math.log2(len(inventory)) if len(inventory) > 1 else 0
            else:
                data += gamma(len(value)) + len(value) * math.log2(alpha)
    return model + data


def ascii3_encode(text):
    assert all(ord(c) < 1000 for c in text)
    return ''.join(f'{ord(c):03d}' for c in text)


def ascii3_decode(text):
    assert len(text) % 3 == 0
    return ''.join(chr(int(text[i:i+3])) for i in range(0, len(text), 3))


def parses(text, codebook):
    """Keep attested spaces as boundaries; permit splitting inside each group."""
    def group(s):
        dp = {len(s): [()]}
        for pos in range(len(s)-1, -1, -1):
            dp[pos] = [(code,) + tail for code in codebook if s.startswith(code, pos)
                       for tail in dp.get(pos + len(code), [])]
        return dp[0]
    paths = [()]
    for word in re.findall(r'\d+', text):
        paths = [a + b for a in paths for b in group(word)]
    return paths


def phrase_audit(seed):
    claims = json.loads((ROOT/'data/round24_reference/phrase_claims.json').read_text())['sources']
    inventory = {r['id']: r['text'] for r in json.loads((ROOT/'data/source_validation_inventory.json').read_text())}
    table = {}
    for entries in claims.values():
        for code, word in entries.items():
            assert table.get(code, word) == word
            table[code] = word
    full = {}
    for name in claims:
        paths = parses(inventory[name], table)
        training = {c: w for source, entries in claims.items() if source != name for c, w in entries.items()}
        full[name] = {'numeric_parses': len(paths), 'published_outputs': [' '.join(table[c] for c in path) for path in paths],
                      'leave_source_out_parses': len(parses(inventory[name], training)),
                      'codes_retained_from_other_sources': sorted(set(claims[name]) & set(training))}
    rng = random.Random(seed)
    successes = Counter()
    for _ in range(999):
        labels = list(table.values()); rng.shuffle(labels)
        shuffled = dict(zip(table, labels))
        for name in claims:
            paths = parses(inventory[name], shuffled)
            successes['numeric_parse'] += bool(paths)
            # Model of the logically circular condition, NOT execution of the SQL gate.
            own_output = [' '.join(shuffled[c] for c in path) for path in paths]
            successes['self_output_equality'] += bool(paths) and own_output == own_output.copy()
    return {'table_entries': len(table), 'real_sources': full, 'null_label_permutations': 999,
            'null_source_evaluations': 999 * len(claims), 'null_passes': dict(successes),
            'scope': 'independent table parser and circularity demonstration; original database gate not run',
            'authenticated_english_pairs': 0, 'translation_validated': False}


def run():
    protocol = json.loads((ROOT/'data/round24_claim_protocol.json').read_text())
    rows = json.loads((ROOT/'data/normalized_books.json').read_text())
    real = {r['id']: r['digits'] for r in sorted(rows, key=lambda r: int(r['id']))}
    sentences = json.loads((ROOT/'data/round24_reference/english_control.json').read_text())
    english = {str(i): sentences[i % 8] + ' ' + sentences[(i * 3 + 1) % 8] for i in range(70)}
    encoded = {k: ascii3_encode(v) for k, v in english.items()}
    rng = random.Random(protocol['seed'])
    shuffled = {}
    for key, value in encoded.items():
        digits = list(value); rng.shuffle(digits); shuffled[key] = ''.join(digits)
    uniform = {k: ''.join(rng.choice('0123456789') for _ in v) for k, v in real.items()}
    upstream = upstream_functions()
    results = {}
    for name, strings in [('real', real), ('english_ascii3', encoded), ('english_shuffled', shuffled), ('uniform', uniform)]:
        modules, coverage = upstream['tile'](strings, protocol['module_min_length'])
        payload = encode_modules(strings, modules)
        recovered = decode_modules(json.loads(json.dumps(payload)))
        assert recovered == strings
        cost = upstream['two_part_module_code'](strings, list(strings), protocol['module_min_length'], protocol['module_alphabet_size'])
        computed = independent_bits(payload)
        assert math.isclose(computed, cost['TOTAL'], abs_tol=1e-7)
        if name == 'english_ascii3':
            assert {k: ascii3_decode(v) for k, v in recovered.items()} == english
        count = sum(map(len, strings.values()))
        results[name] = {'books': len(strings), 'digits': count, 'roundtrip_books': len(recovered),
                         'covered_digits': sum(sum(v) for v in coverage.values()),
                         'raw_fixed_alphabet_bits': count * math.log2(10),
                         'upstream_cost': cost, 'independently_recomputed_total_bits': computed,
                         'payload_sha256': hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()}
        print(name, cost['M'], round(cost['TOTAL'], 3), flush=True)
    return {'module_reproduction': results, 'phrases': phrase_audit(protocol['seed'] + 1),
            'interpretation': 'lossless compression with fitted inventory and literals is compatible with known English; no original generator authenticated',
            'translation_validated': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    output = run(); path = ROOT/'results/round24_claims.json'
    if args.check:
        assert json.loads(path.read_text()) == output, 'replay mismatch'
    else:
        path.write_text(json.dumps(output, indent=2)+'\n')
