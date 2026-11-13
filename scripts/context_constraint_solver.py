#!/usr/bin/env python3
"""Exact set-valued inference for a supplied family of shared cut variables.

An observation is a raw frame. Its parse paths are DNF cubes assigning cuts.
Conjoin frames globally; keep all compatible keys, with explicit resource caps.
"""
import collections
import math


class ResourceLimit(RuntimeError):
    pass


def prefix_certificate(blocks, cuts=(4, 5, 6)):
    prefixes = []
    for block in blocks:
        if len(block) != 10 or any(c not in '0123456789' for c in block):
            raise ValueError('10digit parent blocks required')
        prefixes.append(block[:3])
        prefixes.extend(block[k:k+3] for k in cuts)
    return len(prefixes) == len(set(prefixes))


class FrameParser:
    def __init__(self, blocks, cuts=(4, 5, 6), path_cap=4096):
        if not prefix_certificate(blocks, cuts):
            raise ValueError('candidate prefixes do not certify fixed-key prefix freedom')
        self.blocks, self.cuts, self.path_cap = list(blocks), tuple(cuts), path_cap
        self.index = collections.defaultdict(list)
        for i, block in enumerate(blocks):
            for ci, cut in enumerate(cuts):
                for word in (block[:cut], block[cut:]):
                    self.index[word[0]].append((word, i, ci))

    def paths(self, raw):
        if not raw or any(c not in '0123456789' for c in raw):
            raise ValueError('nonempty numeric frame required')
        out = {}
        def visit(pos, assigned, words):
            if pos == len(raw):
                signature = (tuple(sorted(assigned.items())), tuple(words))
                out[signature] = {'cube': signature[0], 'units': signature[1]}
                if len(out) > self.path_cap:
                    raise ResourceLimit('raw-frame parse-path cap exceeded')
                return
            for word, variable, value in self.index.get(raw[pos], ()):
                if variable in assigned and assigned[variable] != value:
                    continue
                if raw.startswith(word, pos):
                    updated = dict(assigned); updated[variable] = value
                    visit(pos+len(word), updated, words+[word])
        visit(0, {}, [])
        return list(out.values())


def normalize(cubes, domains):
    """Absorption plus exact complete-value merging; never drops a constraint."""
    terms = set()
    for cube in cubes:
        if any(value not in domains[var] for var, value in cube):
            continue
        reduced = frozenset((var, value) for var, value in cube if len(domains[var]) > 1)
        terms.add(reduced)
    while True:
        if frozenset() in terms:
            return ((),)
        reduced = {term for term in terms if not any(other < term for other in terms)}
        buckets = collections.defaultdict(set)
        for term in reduced:
            for var, value in term:
                buckets[(var, term-{(var, value)})].add(value)
        additions = {rest for (var, rest), values in buckets.items() if values == domains[var]}
        new = reduced | additions
        if new == terms:
            return tuple(sorted(tuple(sorted(term)) for term in new))
        terms = new


class KeySet:
    def __init__(self, variables, constraints, values=3, node_cap=100000):
        self.variables, self.values, self.node_cap = variables, values, node_cap
        self.constraints = tuple(tuple(tuple(cube) for cube in frame) for frame in constraints)
        self.cache, self.nodes = {}, 0

    def count(self, pins=()):
        domains = [set(range(self.values)) for _ in range(self.variables)]
        for var, value in pins:
            if value not in domains[var]:
                return 0
            domains[var] = {value}
        return self._count(tuple(tuple(sorted(d)) for d in domains))

    def _count(self, state):
        if state in self.cache:
            return self.cache[state]
        self.nodes += 1
        if self.nodes > self.node_cap:
            raise ResourceLimit('exact-key search-node cap exceeded')
        domains = [set(d) for d in state]
        while True:
            frames, changed = [], False
            for original in self.constraints:
                frame = normalize(original, domains)
                if not frame:
                    self.cache[state] = 0; return 0
                if frame == ((),):
                    continue
                frames.append(frame)
                common = set.intersection(*(set(var for var, _ in cube) for cube in frame))
                for var in common:
                    allowed = {dict(cube)[var] for cube in frame}
                    remaining = domains[var] & allowed
                    if not remaining:
                        self.cache[state] = 0; return 0
                    if remaining != domains[var]:
                        domains[var] = remaining; changed = True
            if not changed:
                break
        if not frames:
            result = math.prod(len(d) for d in domains)
        else:
            appearances = collections.Counter(var for frame in frames for cube in frame for var, _ in cube if len(domains[var]) > 1)
            variable = min(appearances, key=lambda i: (-appearances[i], i))
            result = 0
            for value in sorted(domains[variable]):
                branch = [tuple(sorted(d)) for d in domains]; branch[variable] = (value,)
                result += self._count(tuple(branch))
        self.cache[state] = result
        return result

    def supported_domains(self):
        return [[v for v in range(self.values) if self.count(((i, v),))] for i in range(self.variables)]


def constraints_from_frames(parser, frames):
    return [[path['cube'] for path in parser.paths(raw)] for raw in frames]


def consensus_decode(parser, keyset, raw):
    viable = []
    for path in parser.paths(raw):
        count = keyset.count(path['cube'])
        if count:
            viable.append({'units': list(path['units']), 'compatible_keys': count})
    unique = {tuple(p['units']) for p in viable}
    return {'status': 'inconsistent' if not unique else 'unique' if len(unique) == 1 else 'ambiguous',
            'prediction': list(next(iter(unique))) if len(unique) == 1 else None,
            'possible_paths': viable}
