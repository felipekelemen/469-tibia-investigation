#!/usr/bin/env python3
"""Finite whole-integer radix/affine codecs; exact lexical compatibility only."""
from functools import lru_cache
import math
import re
from unit_morphism_lexicon import banks

CODECS = ('bijective26', 'canonical26', 'space27')
FRAMINGS = ('runs', 'utterance')
KEYS = tuple((a, b) for a in range(26) if math.gcd(a, 26) == 1 for b in range(26))


def values(raw, codec):
    if codec not in CODECS or not re.fullmatch(r'[0-9]+', raw):
        raise ValueError('Declared codec and decimal digits required')
    n = int(raw)
    if codec == 'bijective26' and n == 0:
        return None
    if n == 0:
        return (0,)
    out = []
    base = 27 if codec == 'space27' else 26
    while n:
        n, remainder = divmod(n - (codec == 'bijective26'), base)
        out.append(remainder)
    return tuple(reversed(out))


def render(symbols, codec, key):
    if symbols is None:
        return None
    a, b = key
    return ''.join(' ' if codec == 'space27' and x == 0 else
        chr(65+(a*(x-1 if codec == 'space27' else x)+b)%26) for x in symbols)


def decode(raw, codec, key):
    return render(values(raw, codec), codec, key)


def encode(plain, codec, key, padding=0):
    """Reject lossy canonical26 cases rather than dropping leading letters."""
    if codec not in CODECS or not re.fullmatch(r'[A-Z ]+', plain):
        raise ValueError('Uppercase letters and spaces required')
    a, b = key
    if (a, b) not in KEYS or padding < 0:
        raise ValueError('Declared affine key and nonnegative padding required')
    inverse = pow(a, -1, 26)
    symbols = []
    for c in plain:
        if c == ' ':
            if codec == 'space27':
                symbols.append(0)
        else:
            x = inverse*(ord(c)-65-b)%26
            symbols.append(x+1 if codec in ('bijective26', 'space27') else x)
    if not symbols or (codec == 'canonical26' and len(symbols)>1 and symbols[0]==0):
        raise ValueError('Unrepresentable or lossy leading symbol')
    if codec == 'space27' and len(symbols)>1 and symbols[0]==0:
        raise ValueError('Leading space requires unavailable length metadata')
    n = 0
    for value in symbols:
        n = n*(27 if codec == 'space27' else 26)+value
    return '0'*padding+str(n)


def frames(groups, framing):
    if framing not in FRAMINGS:
        raise ValueError('Declared framing required')
    return list(groups) if framing == 'runs' else [''.join(groups)]


class Lexicon:
    def __init__(self, words=None):
        self.words = frozenset(banks()[0]['grapheme1_3'].reverse if words is None else words)
        self.trie = {}
        for word in sorted(self.words):
            node = self.trie
            for c in word:
                node = node.setdefault(c, {})
            node[''] = word

    @lru_cache(maxsize=200000)
    def parse(self, text, explicit_spaces=False):
        if explicit_spaces:
            words = text.split()
            good = all(word in self.words for word in words)
            return {'paths': int(good), 'unique_words': words if good else None}
        if not text:
            return {'paths': 0, 'unique_words': None}
        n = len(text)
        counts, previous = [0]*(n+1), [None]*(n+1)
        counts[0] = 1
        for start in range(n):
            if not counts[start]:
                continue
            node = self.trie
            for end in range(start+1, n+1):
                node = node.get(text[end-1])
                if node is None:
                    break
                if '' in node:
                    counts[end] += counts[start]
                    previous[end] = (start, node['']) if counts[end] == 1 else None
        words = None
        if counts[-1] == 1:
            words, end = [], n
            while end:
                start, word = previous[end]
                words.append(word)
                end = start
            words.reverse()
        return {'paths': counts[-1], 'unique_words': words}


def fit(groups, codec, framing, lexicon):
    prepared = [values(raw, codec) for raw in frames(groups, framing)]
    accepted = []
    failures = []
    for key in KEYS:
        bad = None
        letters = 0
        for i, v in enumerate(prepared):
            if v is None:
                bad = {'frame': i, 'reason': 'zero_not_bijective26'}
                break
            literal = render(v, codec, key)
            letters += len(literal.replace(' ', ''))
            if not lexicon.parse(literal, codec == 'space27')['paths']:
                bad = {'frame': i, 'reason': 'no_complete_lexical_parse', 'literal': literal}
                break
        if bad is None and not letters:
            bad = {'frame': None, 'reason': 'no_letters'}
        if bad is None:
            accepted.append(list(key))
        failures.append(bad)
    return {'codec': codec, 'framing': framing, 'complete': True,
            'keys_examined': len(KEYS), 'keys': accepted,
            'first_failure_per_key': failures}


def literal_output(groups, codec, framing, key, lexicon):
    literals = [decode(raw, codec, key) for raw in frames(groups, framing)]
    if any(s is None for s in literals):
        return {'literal_frames': literals, 'letter_string': None,
                'word_paths': 0, 'unique_words': None}
    parses = [lexicon.parse(s, codec == 'space27') for s in literals]
    paths = math.prod(p['paths'] for p in parses)
    words = [w for p in parses for w in p['unique_words']] if paths == 1 else None
    return {'literal_frames': literals, 'letter_string': ''.join(literals).replace(' ', ''),
            'word_paths': paths, 'unique_words': words}


def predict(groups, codec, framing, keys, lexicon):
    outputs = [literal_output(groups, codec, framing, key, lexicon) for key in keys]
    strings = [o['letter_string'] for o in outputs]
    length = len(strings[0]) if strings and strings[0] is not None else None
    if length is None or any(s is None or len(s) != length for s in strings):
        return {'status': 'no_common_length_or_no_key', 'certified': None,
                'unique_literal': None, 'unique_words': None, 'outputs': outputs}
    certified = ''.join(strings[0][i] if len({s[i] for s in strings}) == 1 else '?'
                        for i in range(length))
    unique_literal = strings[0] if len(set(strings)) == 1 else None
    # space27 encodes boundaries: unknown lexical items must not erase them.
    if codec == 'space27':
        word_lists = [[w for frame in o['literal_frames'] for w in frame.split()] for o in outputs]
    else:
        word_lists = [o['unique_words'] for o in outputs]
    unique_words = word_lists[0] if word_lists[0] is not None and all(
        words == word_lists[0] for words in word_lists) else None
    return {'status': 'letter_consensus' if unique_literal is not None else 'partial_letter_consensus',
            'certified': certified, 'unique_literal': unique_literal,
            'unique_words': unique_words, 'outputs': outputs}
