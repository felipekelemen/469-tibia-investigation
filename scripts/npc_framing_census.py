#!/usr/bin/env python3
"""Conditional numeric-stream ambiguity under framing, without English labels."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


def dump(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def parse_count(raw, inventory):
    full, short = set(inventory), {w[1:] for w in inventory if w.startswith('0')}
    counts = [0]*(len(raw)+1); counts[0] = 1
    for i in range(len(raw)):
        if raw[i:i+1] in short:
            counts[i+1] += counts[i]
        if raw[i:i+2] in full:
            counts[i+2] += counts[i]
    return counts[-1]


def fibonacci_count(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a+b
    return a


def all_paths_short(raw, inventory):
    if len(raw) > 8:
        raise ValueError('only small illustrative strings enumerated')
    inventory = set(inventory)
    def paths(i):
        if i == len(raw):
            return [[]]
        out = []
        code = '0'+raw[i]
        if code in inventory:
            out.extend([code]+tail for tail in paths(i+1))
        if raw[i:i+2] in inventory:
            out.extend([raw[i:i+2]]+tail for tail in paths(i+2))
        return out
    return paths(0)


def build():
    books = load('data/normalized_books.json')
    inventories = {'observed99': sorted({code for b in books for code in b['codes']}),
                   'all100': [f'{i:02d}' for i in range(100)]}
    entries = [r for r in load('data/source_validation_inventory.json') if r['canonical_candidate']]
    npcs = []
    for r in entries:
        groups = re.findall(r'\d+', r['text']); raw = ''.join(groups)
        values = {}
        for name, inventory in inventories.items():
            unframed = parse_count(raw, inventory)
            counts = [parse_count(w, inventory) for w in groups]
            framed = math.prod(counts)
            if name == 'all100':
                assert unframed == fibonacci_count(len(raw))
                assert counts == [fibonacci_count(len(w)) for w in groups]
            values[name] = {'unspaced_count_decimal': str(unframed),
                            'framed_count_decimal': str(framed),
                            'group_counts_decimal': list(map(str, counts)),
                            'log2_count_reduction': math.log2(unframed)-math.log2(framed)}
        npcs.append({'id': r['id'], 'source_group': r['source_group'], 'numeric_groups': groups,
                     'counts': values})
    book_rows = []
    for b in books:
        values = {name: str(parse_count(b['digits'], inv)) for name, inv in inventories.items()}
        assert int(values['all100']) == fibonacci_count(len(b['digits']))
        book_rows.append({'id': b['id'], 'digits': len(b['digits']), 'counts_decimal': values})
    examples = {raw: all_paths_short(raw, inventories['observed99']) for raw in ('1', '0', '3478', '486486')}
    return {'inventories': inventories, 'npc_rows': npcs, 'book_rows': book_rows,
            'short_numeric_examples': examples,
            'scope': 'Conditional memoryless leading-zero omission inventory only. Counts of numeric streams, not English meanings; framing boundaries are assumptions; all100count depends only on length. Not the earlier79alignments of fixed imported streams.'}


def freeze():
    if (ROOT / 'data/round18_framing_manifest.json').exists():
        raise ValueError('already frozen')
    files = ['data/round18_framing_protocol.json', 'scripts/npc_framing_census.py',
             'data/source_validation_inventory.json', 'data/normalized_books.json']
    dump('data/round18_framing_manifest.json', {'stage': 'Before new computed framing counts',
                                              'sha256': {p: sha(p) for p in files}})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    elif args.run:
        for path, expected in load('data/round18_framing_manifest.json')['sha256'].items():
            if sha(path) != expected:
                raise ValueError('framing input changed: '+path)
        dump('results/round18_npc_framing.json', build())
        print('Conditional NPC/book framing counts saved; no English meanings inferred.')
    else:
        parser.error('use --freeze or --run')
