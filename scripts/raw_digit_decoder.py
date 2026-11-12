#!/usr/bin/env python3
"""Exact finite-state raw-digit parsing with a SUPPLIED homophonic key.

This is a conditional parser, not a key breaker or a translator for 469.
No true token count, boundaries, omissions or plaintext reach decode().
"""
import functools
import math

import numpy as np

RULES = ('never', 'always', 'iid_0.1', 'iid_0.3', 'iid_0.5',
         'iid_0.7', 'iid_0.9', 'previous_mod3')


def logadd(a, b):
    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    top = max(a, b)
    return top + math.log1p(math.exp(min(a, b) - top))


def omission_probability(rule, previous_mod3):
    if rule == 'never':
        return 0.0
    if rule == 'always':
        return 1.0
    if rule == 'previous_mod3':
        return float(previous_mod3 == 1)  # beginning of message uses -1
    if rule in RULES and rule.startswith('iid_'):
        return float(rule[4:])
    raise ValueError('unknown zero rule')


class CharacterLanguage:
    """Normalized order3 Markov transitions, including normalized short prefixes."""
    def __init__(self, log10_joint):
        joint = np.power(10.0, np.asarray(log10_joint).reshape(26, 26, 26, 26))
        if not np.isfinite(joint).all() or np.any(joint <= 0):
            raise ValueError('finite positive smoothed language table required')
        self.tables = []
        for order in range(4):
            counts = joint.sum(axis=tuple(range(order + 1, 4))) if order < 3 else joint
            self.tables.append(np.log(counts / counts.sum(axis=-1, keepdims=True)))

    @functools.lru_cache(maxsize=100000)
    def log_probability(self, history, letter):
        return float(self.tables[len(history)][history + (letter,)])


class UniformLanguage:
    def log_probability(self, history, letter):
        return -math.log(26)


def validate_key(key, emission_probabilities):
    if len(key) != 100 or len(emission_probabilities) != 100:
        raise ValueError('100 key/probability slots required')
    sums = [0.0] * 26
    for code, (letter, p) in enumerate(zip(key, emission_probabilities)):
        if not math.isfinite(p) or p < 0:
            raise ValueError('invalid code emission probability')
        if p > 0:
            if not isinstance(letter, (int, np.integer)) or not 0 <= letter < 26:
                raise ValueError('active code has no letter')
            sums[letter] += p
    if any(abs(total - 1) > 1e-9 for total in sums):
        raise ValueError('P(code|letter) must sum to one for each letter')


def edges(raw, position, key, probabilities, rule, previous_mod3):
    """Order is pair then singleton; ties retain the first encountered path."""
    q = omission_probability(rule, previous_mod3)
    options = []
    if position + 2 <= len(raw):
        code = int(raw[position:position + 2])
        action_p = 1.0 if code >= 10 else 1 - q
        options.append((position + 2, code, False, action_p))
    options.append((position + 1, int(raw[position]), True, q))
    for end, code, omitted, action_p in options:
        if probabilities[code] > 0 and action_p > 0:
            yield end, code, omitted, key[code], math.log(probabilities[code]) + math.log(action_p)


def decode(raw, key, probabilities, language, rule, *, stop_probability=1 / 128):
    validate_key(key, probabilities)
    omission_probability(rule, -1)
    if not 0 < stop_probability < 1:
        raise ValueError('message stop probability must be between zero and one')
    continuation = math.log1p(-stop_probability)
    if any(c not in '0123456789' for c in raw):
        raise ValueError('raw ASCII digits required, no cleaning')
    # State: last <=3 decoded letters and previous numeric code modulo3.
    # (forward logsum, Viterbi logscore, immutable backpointer)
    states = [{} for _ in range(len(raw) + 1)]
    states[0][((), -1)] = (0.0, 0.0, None)
    for position in range(len(raw)):
        for (history, previous), (forward, best, node) in states[position].items():
            for end, code, omitted, letter, emission in edges(raw, position, key, probabilities, rule, previous):
                weight = emission + language.log_probability(history, letter) + continuation
                target = ((history + (letter,))[-3:], code % 3)
                old = states[end].get(target, (-math.inf, -math.inf, None))
                candidate_score = best + weight
                candidate_node = (node, position, end, code, omitted) if candidate_score > old[1] else old[2]
                states[end][target] = (logadd(old[0], forward + weight), max(old[1], candidate_score), candidate_node)
    if not states[-1]:
        return {'possible': False, 'log_evidence': None, 'path': [], 'literal': ''}
    final = list(states[-1].values())
    evidence = -math.inf
    for forward, _, _ in final:
        evidence = logadd(evidence, forward)
    _, best, node = max(final, key=lambda row: row[1])
    evidence += math.log(stop_probability)
    best += math.log(stop_probability)
    path = []
    while node is not None:
        previous, start, end, code, omitted = node
        path.append({'start': start, 'end': end, 'code': code, 'omitted': omitted})
        node = previous
    path.reverse()
    literal = ''.join(chr(key[row['code']] + 65) for row in path)
    serialized = ''.join(f"{row['code']:02d}"[1:] if row['omitted'] else f"{row['code']:02d}" for row in path)
    if serialized != raw:
        raise AssertionError('decoder did not roundtrip')
    return {'possible': True, 'log_evidence': evidence, 'best_log_probability': best,
            'map_path_posterior': math.exp(min(0.0, best - evidence)),
            'literal': literal, 'path': path,
            'maximum_states_at_position': max(map(len, states))}


def serialize(codes, rule, rng):
    """Known-rule synthetic encoder. Returns truth metadata for evaluation ONLY."""
    raw = []
    path = []
    position = 0
    previous = -1
    for code in codes:
        omitted = code < 10 and rng.random() < omission_probability(rule, previous)
        piece = f'{code:02d}'[1:] if omitted else f'{code:02d}'
        raw.append(piece)
        path.append({'start': position, 'end': position + len(piece), 'code': code, 'omitted': omitted})
        position += len(piece)
        previous = code % 3
    return ''.join(raw), path


def edit_distance(a, b):
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (x != y)))
        previous = current
    return previous[-1]


def measures(decoded, truth_path, truth_literal):
    if not decoded['possible']:
        return {'possible': False, 'boundary_f1': 0.0, 'code_span_f1': 0.0, 'character_edit_accuracy': 0.0, 'exact_path': False}
    def f1(a, b):
        return 2 * len(a & b) / (len(a) + len(b)) if a or b else 1.0
    actual = decoded['path']
    boundaries = lambda rows: {row['end'] for row in rows[:-1]}
    spans = lambda rows: {(row['start'], row['end'], row['code']) for row in rows}
    return {'possible': True, 'boundary_f1': f1(boundaries(actual), boundaries(truth_path)),
            'code_span_f1': f1(spans(actual), spans(truth_path)),
            'character_edit_accuracy': 1 - edit_distance(decoded['literal'], truth_literal) / max(1, len(decoded['literal']), len(truth_literal)),
            'exact_path': actual == truth_path, 'predicted_tokens': len(actual), 'true_tokens': len(truth_path),
            'map_path_posterior': decoded['map_path_posterior']}
