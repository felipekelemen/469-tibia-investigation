#!/usr/bin/env python3
"""Finite two-part codes with shared copy facilities; no semantic classifier claim.

Lengths are ideal arithmetic-code lengths plus two termination bits per document.
The common decoder program and every fitted parameter/dictionary are charged.
"""
from collections import Counter
from pathlib import Path
import math
import re
import numpy as np
from generative_comparison import fit_dictionary, gamma_bits

ROOT = Path(__file__).resolve().parents[1]
KEYS = tuple((a, b) for a in range(26) if math.gcd(a, 26) == 1 for b in range(26))


def letters(path, encoding='utf-8-sig'):
    raw = (ROOT/path).read_bytes().decode(encoding)
    start = re.search(r'\*\*\*\s*START OF[^\n]*\*\*\*', raw)
    end = re.search(r'\*\*\*\s*END OF[^\n]*\*\*\*', raw)
    if not start or not end or start.end() >= end.start():
        raise ValueError('Missing Gutenberg body boundaries')
    return re.sub('[^A-Z]', '', raw[start.end():end.start()].upper())


def pair_string(digits):
    return ''.join(chr(int(digits[i:i+2])) for i in range(0, len(digits)-1, 2))


def unpair(tokens):
    return ''.join(f'{ord(c):02d}' for c in tokens)


def fit_english(paths):
    unigram = np.zeros(26, dtype=np.int64)
    bigram = np.zeros((26, 26), dtype=np.int64)
    for path in paths:
        text = letters(path)[:100000]
        for c in text:
            unigram[ord(c)-65] += 1
        for a, b in zip(text, text[1:]):
            bigram[ord(a)-65, ord(b)-65] += 1
    costs = sum(gamma_bits(int(n)+1) for n in unigram)
    costs += sum(gamma_bits(int(n)+1) for n in bigram.flat)
    rows = np.vstack([(bigram+.5)/(bigram.sum(axis=1)[:, None]+13),
                      (unigram+.5)/(unigram.sum()+13)])
    # Each pair >=26 is an explicit escape. Previous escapes reset letter context.
    table = np.full((312, 27, 100), -math.log2((1/16)/74))
    for i, (a, b) in enumerate(KEYS):
        decoded = (a*np.arange(26)+b)%26
        table[i, :26, :26] = -np.log2((15/16)*rows[decoded[:, None], decoded[None, :]])
        table[i, 26, :26] = -np.log2((15/16)*rows[26, decoded])
    return {'unigram': unigram.tolist(), 'bigram': bigram.tolist(),
            'parameter_bits': costs, 'table': table}


def digit_models(train):
    counts, starts, trans = np.zeros(10, int), np.zeros(10, int), np.zeros((10,10), int)
    for s in train:
        if s:
            starts[int(s[0])] += 1
        for c in s:
            counts[int(c)] += 1
        for a,b in zip(s,s[1:]):
            trans[int(a),int(b)] += 1
    uniform = np.full((11,10), math.log2(10))
    iid = np.tile(-np.log2((counts+.5)/(counts.sum()+5)), (11,1))
    markov = np.vstack([-np.log2((trans+.5)/(trans.sum(axis=1)[:,None]+5)),
                        -np.log2((starts+.5)/(starts.sum()+5))])
    parameters = [0, sum(gamma_bits(int(x)+1) for x in counts),
                  sum(gamma_bits(int(x)+1) for x in starts)+
                  sum(gamma_bits(int(x)+1) for x in trans.flat)]
    return {'tables': np.array([uniform, iid, markov]), 'parameter_bits': parameters,
            'counts': counts.tolist(), 'starts': starts.tolist(), 'transitions': trans.tolist()}


def copy_dictionary(train):
    # Existing deterministic discovery-only greedy algorithm; never sees holdout.
    dictionary = fit_dictionary([pair_string(s) for s in train], list(map(chr,range(100))), max_entries=64)
    paid = gamma_bits(len(dictionary)+1)+sum(gamma_bits(len(s))+7*len(s) for s in dictionary)
    return dictionary, paid


def paths_cost(literal_costs, tokens, dictionary):
    """Exact shortest prefix-code path for every model column, context already known.

    Literal: flag0 then arithmetic pair. Reference: flag1 + fixedwidth index.
    Every copied pair updates context through its decoded digits, as a literal does.
    """
    n, width = len(tokens), literal_costs.shape[1]
    dp = np.zeros((n+1, width))
    ref_bits = 1+(math.ceil(math.log2(len(dictionary))) if len(dictionary)>1 else 0)
    index = {}
    for entry in dictionary:
        index.setdefault(entry[0], []).append(entry)
    for i in range(n-1,-1,-1):
        dp[i] = 1+literal_costs[i]+dp[i+1]
        for entry in index.get(tokens[i],[]):
            if tokens.startswith(entry,i):
                dp[i] = np.minimum(dp[i], ref_bits+dp[i+len(entry)])
    return dp[0]


def document_costs(digits, language, numeric, dictionary):
    tokens = pair_string(digits)
    vs = np.array(list(map(ord,tokens)), dtype=int)
    previous = np.r_[26, np.where(vs[:-1]<26, vs[:-1],26)] if len(vs) else np.array([],int)
    text = language['table'][:,previous,vs].T
    digit_cost = np.empty((len(digits),3))
    previous_digit = 10
    for i, c in enumerate(digits):
        digit_cost[i] = numeric['tables'][:, previous_digit, int(c)]
        previous_digit = int(c)
    nontext = digit_cost[:2*len(vs)].reshape(len(vs),2,3).sum(axis=1)
    literal = np.column_stack([text, nontext])
    plain, copied = literal.sum(axis=0), paths_cost(literal,tokens,dictionary)
    # Odd tail is fully paid and never part of a pair/reference; lengths fix its location.
    tail = np.r_[np.full(312, math.log2(10)),digit_cost[-1]] if len(digits)%2 else 0
    framing = gamma_bits(len(digits)+1)+2
    return np.stack([plain+tail+framing, copied+tail+framing])


def common_program_bits():
    paths = ['scripts/round29_models.py','scripts/generative_comparison.py']
    return sum(gamma_bits((ROOT/p).stat().st_size+1)+8*(ROOT/p).stat().st_size for p in paths)


def compare(train, held, language):
    numeric = digit_models(train)
    dictionary, dictionary_bits = copy_dictionary(train)
    costs = np.stack([document_costs(s,language,numeric,dictionary) for s in train+held])
    nt = len(train)
    # Columns are (copy flag, key/base). All key and envelope selection uses discovery.
    tc = costs[:,:,:312].reshape(len(costs),624)
    nc = costs[:,:,312:].reshape(len(costs),6)
    text_headers = np.array([2+1+9+language['parameter_bits']+(dictionary_bits if i>=312 else 0) for i in range(624)])
    number_headers = np.array([2+2+1+numeric['parameter_bits'][i%3]+(dictionary_bits if i>=3 else 0) for i in range(6)])
    ti = int(np.argmin(text_headers+tc[:nt].sum(axis=0)))
    ni = int(np.argmin(number_headers+nc[:nt].sum(axis=0)))
    mixed_fit = np.empty((624,6))
    mixed_headers = np.empty_like(mixed_fit)
    for j in range(6):
        # Shared dictionary paid once; every document pays its own one-bit route.
        mixed_headers[:,j] = [2+9+2+2+language['parameter_bits']+numeric['parameter_bits'][j%3]+(dictionary_bits if i>=312 or j>=3 else 0) for i in range(624)]
        mixed_fit[:,j] = mixed_headers[:,j]+(1+np.minimum(tc[:nt],nc[:nt,j,None])).sum(axis=0)
    mi,mj = map(int,np.unravel_index(np.argmin(mixed_fit),mixed_fit.shape))
    selected = {'T':(text_headers[ti],tc[:,ti]),
                'N':(number_headers[ni],nc[:,ni]),
                'M':(mixed_headers[mi,mj],1+np.minimum(tc[:,mi],nc[:,mj]))}
    common = common_program_bits()+gamma_bits(len(train)+1)+gamma_bits(len(held)+1)
    output = {}
    for label,(header,data) in selected.items():
        output[label] = {'common_program_and_count_bits':common,'parameter_and_selector_bits':float(header),
            'train_data_bits':float(data[:nt].sum()),'held_data_bits':float(data[nt:].sum()),
            'total_bits':float(common+header+data.sum()),'per_document_bits':data.tolist()}
    order = ('T','N','M')
    return {'models':output,
        'total_winner':min(order,key=lambda k:output[k]['total_bits']),
        'predictive_winner':min(order,key=lambda k:output[k]['held_data_bits']),
        'selected':{'T':{'key':list(KEYS[ti%312]),'copy':ti>=312},
                    'N':{'base':('uniform','iid','markov1')[ni%3],'copy':ni>=3},
                    'M':{'key':list(KEYS[mi%312]),'text_copy':mi>=312,
                         'numeric_base':('uniform','iid','markov1')[mj%3],'numeric_copy':mj>=3,
                         'text_routes':[bool(a<=b) for a,b in zip(tc[:,mi],nc[:,mj])]}},
        'dictionary':[unpair(s) for s in dictionary], 'dictionary_bits':dictionary_bits,
        'numeric_parameters':{k:v for k,v in numeric.items() if k!='tables'},
        'train_digits':sum(map(len,train)),'held_digits':sum(map(len,held)),
        'selection_scope':'All312keys, copy choices and numeric bases selected using discovery costs only. Total and predictive winners are separate frozen evaluation rules.'}


def overlap(train, held, k=12):
    known={s[i:i+k] for s in train for i in range(len(s)-k+1)}
    coverage, windows, hits = 0,0,0
    for s in held:
        mask=set()
        for i in range(len(s)-k+1):
            windows+=1
            if s[i:i+k] in known:
                hits+=1;mask.update(range(i,i+k))
        coverage+=len(mask)
    return {'k':k,'held_windows':windows,'exact_window_hits':hits,
            'held_digits_covered':coverage,'held_digits':sum(map(len,held))}
