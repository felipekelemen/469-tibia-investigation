#!/usr/bin/env python3
"""Development-only higher-order parser; V1 frozen code is unchanged."""
import collections
import functools
import hashlib
import math

from copied_homophonic_v3 import TRAINING_PATHS
from homophonic_benchmark import ROOT, letters
from raw_digit_decoder import edges, logadd, validate_key


@functools.lru_cache(maxsize=1)
def statistics():
    counts = [None] + [collections.Counter() for _ in range(7)]
    sources = []
    for relative in TRAINING_PATHS:
        text = letters(ROOT / relative)
        text = text[:int(.8 * len(text))] if relative.endswith('/alice.txt') else text[:100000]
        for n in range(1, 8):
            counts[n].update(text[i:i + n] for i in range(len(text) - n + 1))
        sources.append({'path': relative, 'letters': len(text),
                        'source_sha256': hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                        'text_sha256': hashlib.sha256(text.encode()).hexdigest()})
    totals = [None] * 7
    for n in range(1, 7):
        totals[n] = collections.Counter()
        for gram, count in counts[n + 1].items():
            totals[n][gram[:-1]] += count
    return counts, totals, sources


class LongContextLanguage:
    def __init__(self, order, backoff):
        if order not in [4, 6] or backoff not in [1, 10]:
            raise ValueError('outside fixed development grid')
        self.order = order
        self.backoff = backoff
        self.counts, self.totals, self.sources = statistics()
        self.total_letters = sum(self.counts[1].values())

    @functools.lru_cache(maxsize=300000)
    def log_probability(self, history, letter):
        c = chr(letter + 65)
        probability = (self.counts[1][c] + .01) / (self.total_letters + .26)
        text = ''.join(chr(x + 65) for x in history)
        for width in range(1, min(len(text), self.order) + 1):
            context = text[-width:]
            probability = (self.counts[width + 1][context + c] + self.backoff * probability) / (self.totals[width][context] + self.backoff)
        return math.log(probability)


def decode(raw, key, probabilities, language, rule):
    """Exact forward/Viterbi with enough history for this language's order."""
    validate_key(key, probabilities)
    if any(c not in '0123456789' for c in raw):
        raise ValueError('raw ASCII digits required')
    states = [{} for _ in range(len(raw) + 1)]
    states[0][((), -1)] = (0.0, 0.0, None)
    for position in range(len(raw)):
        for (history, previous), (forward, best, node) in states[position].items():
            for end, code, omitted, letter, emission in edges(raw, position, key, probabilities, rule, previous):
                weight = emission + language.log_probability(history, letter) + math.log(127 / 128)
                target = ((history + (letter,))[-language.order:], code % 3)
                old = states[end].get(target, (-math.inf, -math.inf, None))
                candidate = best + weight
                selected_node = (node, position, end, code, omitted) if candidate > old[1] else old[2]
                states[end][target] = (logadd(old[0], forward + weight), max(old[1], candidate), selected_node)
    if not states[-1]:
        return {'possible': False, 'log_evidence': None, 'path': [], 'literal': ''}
    evidence = -math.inf
    for forward, _, _ in states[-1].values():
        evidence = logadd(evidence, forward)
    _, best, node = max(states[-1].values(), key=lambda row: row[1])
    evidence += math.log(1 / 128)
    best += math.log(1 / 128)
    path = []
    while node is not None:
        node, start, end, code, omitted = node
        path.append({'start': start, 'end': end, 'code': code, 'omitted': omitted})
    path.reverse()
    literal = ''.join(chr(key[r['code']] + 65) for r in path)
    if ''.join(f"{r['code']:02d}"[1:] if r['omitted'] else f"{r['code']:02d}" for r in path) != raw:
        raise AssertionError('roundtrip failed')
    return {'possible': True, 'log_evidence': evidence, 'best_log_probability': best,
            'map_path_posterior': math.exp(min(0.0, best - evidence)),
            'path': path, 'literal': literal,
            'maximum_states_at_position': max(map(len, states))}
