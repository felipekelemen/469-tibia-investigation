#!/usr/bin/env python3
"""Exact digit-permutation CSP, preserving lexical and numeric ambiguity."""
from collections import defaultdict
from itertools import permutations
import math

FAMILIES = ('ordinal0_compact', 'ordinal0_fixed2', 'ordinal1_compact',
            'ordinal1_fixed2', 'ascii_upper', 'ascii_lower_compact', 'ascii_lower_fixed3')
DIGITS = '0123456789'


def encode(word, family):
    if family not in FAMILIES or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for c in word):
        raise ValueError('declared family and uppercase letters required')
    base = 0 if family.startswith('ordinal0') else 1
    values = [ord(c)-65+base if family.startswith('ordinal') else
              ord(c)+(32 if family.startswith('ascii_lower') else 0) for c in word]
    width = 2 if family.endswith('fixed2') else 3 if family.endswith('fixed3') else 0
    return ''.join(str(v).zfill(width) for v in values)


def pattern(text):
    seen = {}
    return tuple(seen.setdefault(c, len(seen)) for c in text)


def extension(cipher, plain):
    if len(cipher) != len(plain) or pattern(cipher) != pattern(plain):
        return None
    return tuple(sorted(dict(zip(cipher, plain)).items()))


def merge(first, second):
    result = dict(first)
    used = {v: k for k, v in result.items()}
    for k, v in second:
        if (k in result and result[k] != v) or (v in used and used[v] != k):
            return None
        result[k] = v; used[v] = k
    return tuple(sorted(result.items()))


class Solver:
    def __init__(self, words, family):
        self.family = family
        self.index = defaultdict(list)
        self.reverse = defaultdict(list)
        for word in sorted(set(words)):
            raw = encode(word, family)
            self.index[pattern(raw)].append((raw, word))
            self.reverse[raw].append(word)

    def domain(self, raw):
        return sorted({extension(raw, encoded) for encoded, _ in self.index.get(pattern(raw), [])})

    def solve(self, groups, node_limit=200000, solution_limit=20000):
        groups = sorted(set(groups))
        if not groups or any(not g or any(c not in DIGITS for c in g) for g in groups):
            raise ValueError('nonempty decimal groups required')
        domains = {g: self.domain(g) for g in groups}
        solutions = set(); seen = set(); nodes = 0; truncated = False

        def visit(mapping):
            nonlocal nodes, truncated
            if mapping in seen or truncated:
                return
            if nodes >= node_limit or len(solutions) >= solution_limit:
                truncated = True; return
            nodes += 1; seen.add(mapping)
            remaining = []
            for group, domain in domains.items():
                allowed = {v for d in domain if (v := merge(mapping, d)) is not None}
                if not allowed:
                    return
                if mapping not in allowed:
                    remaining.append(allowed)
            if not remaining:
                solutions.add(mapping); return
            chosen = min(remaining, key=lambda d: (len(d), sorted(d)))
            for candidate in sorted(chosen):
                visit(candidate)
        visit(())
        return {'complete': not truncated, 'nodes': nodes,
                'domain_counts': {g: len(d) for g, d in domains.items()},
                'mappings': [list(map(list, m)) for m in sorted(solutions)],
                'full_key_count': sum(math.factorial(10-len(m)) for m in solutions)}

    def words_for(self, raw, mapping):
        mapping = dict(mapping)
        if not set(raw) <= mapping.keys():
            raise ValueError('mapping lacks target digits')
        return self.reverse.get(''.join(mapping[c] for c in raw), [])


def complete_keys(solution, limit=20000):
    if not solution['complete'] or solution['full_key_count'] > limit:
        return None
    keys = []
    for mapping in solution['mappings']:
        mapping = dict(mapping)
        absent = sorted(set(DIGITS)-mapping.keys())
        free = sorted(set(DIGITS)-set(mapping.values()))
        for values in permutations(free):
            keys.append(tuple(sorted({**mapping, **dict(zip(absent, values))}.items())))
    return keys


def letter_parse(raw, family, mapping):
    """All possible letter parses counted, with a literal only when unique."""
    mapping = dict(mapping)
    plain = ''.join(mapping[c] for c in raw)
    table = [(encode(c, family), c) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
    counts = [0]*(len(plain)+1); counts[0] = 1
    sample = ['']+[None]*len(plain)
    for i in range(len(plain)):
        if not counts[i]:
            continue
        for code, char in table:
            if plain.startswith(code, i):
                end = i+len(code)
                counts[end] += counts[i]
                if sample[end] is None:
                    sample[end] = sample[i]+char
    return {'count': counts[-1], 'unique_literal': sample[-1] if counts[-1] == 1 else None}


def dictionary_parse_count(raw, solver, mapping):
    mapping = dict(mapping)
    plain = ''.join(mapping[c] for c in raw)
    counts = [0]*(len(plain)+1); counts[0] = 1
    lengths = sorted({len(k) for k in solver.reverse})
    for i in range(len(plain)):
        if counts[i]:
            for n in lengths:
                if i+n > len(plain):
                    break
                counts[i+n] += counts[i]*len(solver.reverse.get(plain[i:i+n], ()))
    return counts[-1]
