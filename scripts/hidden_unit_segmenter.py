#!/usr/bin/env python3
"""Unsupervised numeric-unit learners. Inputs: digit messages and fixed budgets.

No corpus paths, English model, lore, true vocabulary or cut positions exist in
this module. MDL is an entropy/dictionary-cost objective, not a binary codec.
"""
import collections
import math

DIGITS = tuple('0123456789')


def checked(messages, deduplicate=False):
    messages = list(messages)
    if not messages or any(not s or any(c not in DIGITS for c in s) for s in messages):
        raise ValueError('nonempty list of nonempty digit messages required')
    return list(dict.fromkeys(messages)) if deduplicate else messages


def gamma_bits(n):
    return 2*n.bit_length()-1


def storage(word):
    return 4*len(word)+gamma_bits(len(word)+1)


def mdl_counts(counts):
    counts = {w: c for w, c in counts.items() if c}
    total = sum(counts.values())
    entropy = sum(c*math.log2(total/c) for c in counts.values()) if total else 0.
    lexicon = gamma_bits(len(counts)+1)+sum(storage(w)+gamma_bits(c+1) for w, c in counts.items())
    return entropy+lexicon


def fixed_tokens(raw, width):
    return [raw[i:i+width] for i in range(0, len(raw), width)]


def fit_periodic(messages):
    messages = checked(messages)
    trials = []
    for width in range(1, 13):
        counts = collections.Counter(w for raw in messages for w in fixed_tokens(raw, width))
        trials.append((mdl_counts(counts)+4, width, counts))
    score, width, counts = min(trials, key=lambda r: (r[0], r[1]))
    return {'kind': 'periodic', 'width': width, 'train_objective': score,
            'units': sorted(counts), 'messages': len(messages)}


def merge_pair(tokens, pair):
    out, i = [], 0
    while i < len(tokens):
        if i+1 < len(tokens) and (tokens[i], tokens[i+1]) == pair:
            out.append(tokens[i]+tokens[i+1]); i += 2
        else:
            out.append(tokens[i]); i += 1
    return out


def fit_bpe(messages, budget=256, deduplicate=False):
    messages = checked(messages, deduplicate)
    sequences = [list(raw) for raw in messages]
    vocab, rules = set(DIGITS), []
    while len(vocab) < budget:
        counts = collections.Counter((a, b) for seq in sequences for a, b in zip(seq, seq[1:])
                                     if len(a)+len(b) <= 12)
        if not counts:
            break
        pair = min(counts, key=lambda p: (-counts[p], p))
        if counts[pair] < 2:
            break
        rules.append(list(pair)); vocab.add(''.join(pair))
        sequences = [merge_pair(seq, pair) for seq in sequences]
    counts = collections.Counter(w for seq in sequences for w in seq)
    return {'kind': 'bpe', 'budget': budget, 'deduplicate': deduplicate,
            'units': sorted(vocab), 'rules': rules, 'messages': len(messages),
            'train_objective': mdl_counts(counts)}


def make_trie(words):
    trie = {}
    for word in words:
        node = trie
        for c in word:
            node = node.setdefault(c, {})
        node['word'] = word
    return trie


def viterbi(raw, costs, trie=None):
    trie = trie or make_trie(costs)
    best = [math.inf]*(len(raw)+1); best[len(raw)] = 0.
    choice = [None]*len(raw)
    for i in range(len(raw)-1, -1, -1):
        node, end = trie, i
        while end < len(raw) and raw[end] in node:
            node = node[raw[end]]; end += 1
            if 'word' in node:
                word = node['word']; value = costs[word]+best[end]
                if value < best[i]:
                    best[i], choice[i] = value, word
    if not math.isfinite(best[0]):
        raise ValueError('vocabulary cannot cover raw input')
    result, i = [], 0
    while i < len(raw):
        result.append(choice[i]); i += len(choice[i])
    return result, best[0]


def unigram_costs(vocab, counts):
    total = sum(counts.values())+.1*len(vocab)
    return {w: -math.log2((counts.get(w, 0)+.1)/total)+storage(w)/max(1, counts.get(w, 0))
            for w in vocab}


def fit_unigram(messages, bpe_model):
    messages = checked(messages, bpe_model['deduplicate'])
    vocab = bpe_model['units']; trie = make_trie(vocab)
    counts = collections.Counter()
    for raw in messages:
        for i in range(len(raw)):
            node, end = trie, i
            while end < len(raw) and raw[end] in node:
                node = node[raw[end]]; end += 1
                if 'word' in node:
                    counts[node['word']] += 1
    snapshots = []
    for iteration in range(8):
        costs = unigram_costs(vocab, counts)
        paths = [viterbi(raw, costs, trie)[0] for raw in messages]
        new_counts = collections.Counter(w for path in paths for w in path)
        # The predictive model is evaluated on the segmentation it actually
        # induces, not just the previous iteration's cheaper count table.
        score = mdl_counts(new_counts)
        snapshots.append((score, iteration, dict(costs), dict(new_counts)))
        counts = new_counts
    score, iteration, costs, counts = min(snapshots, key=lambda row: (row[0], row[1]))
    return {'kind': 'unigram', 'budget': bpe_model['budget'], 'deduplicate': bpe_model['deduplicate'],
            'units': vocab, 'costs': costs, 'train_counts': counts, 'train_objective': score,
            'selected_iteration': iteration, 'messages': len(messages)}


def segment(raw, model):
    if any(c not in DIGITS for c in raw):
        raise ValueError('ASCII digits required')
    if model['kind'] == 'periodic':
        result = fixed_tokens(raw, model['width'])
    elif model['kind'] == 'bpe':
        result = list(raw)
        for pair in model['rules']:
            result = merge_pair(result, tuple(pair))
    elif model['kind'] == 'unigram':
        result = viterbi(raw, model['costs'])[0]
    else:
        raise ValueError('unknown learner')
    if ''.join(result) != raw:
        raise AssertionError('segmenter changed raw data')
    return result
