#!/usr/bin/env python3
"""Exact finite word-code consistency, segmentation and literal wire codec.

Units remain numeric group IDs, without supplied English meanings. Prefix
conflicts are not automatically treated as failure of unique decodability.
"""
from collections import deque


def words_checked(words):
    words = sorted(set(words))
    if any(not w or any(c not in '0123456789' for c in w) for w in words):
        raise ValueError('nonempty ASCII digit codewords required')
    return words


def unique_decodability(words):
    words = words_checked(words)
    prefixes = [(a, b) for a in words for b in words if a != b and a.startswith(b)]
    queue, seen = deque(), set()
    for a, b in prefixes:
        state = (0, a[len(b):])
        if state not in seen:
            seen.add(state); queue.append((state, (a,), (b,)))
    while queue:
        (ahead, residual), left, right = queue.popleft()
        for word in words:
            a, b = (left, right + (word,)) if ahead == 0 else (left + (word,), right)
            if residual == word:
                assert a != b and ''.join(a) == ''.join(b)
                return {'uniquely_decodable': False, 'prefix_free': not prefixes,
                        'residual_states_visited': len(seen),
                        'witness': {'wire': ''.join(a), 'first': list(a), 'second': list(b)}}
            if residual.startswith(word):
                state = (ahead, residual[len(word):])
            elif word.startswith(residual):
                state = (1-ahead, word[len(residual):])
            else:
                continue
            if state not in seen:
                seen.add(state); queue.append((state, a, b))
    return {'uniquely_decodable': True, 'prefix_free': not prefixes,
            'residual_states_visited': len(seen), 'witness': None}


def make_index(words):
    words = words_checked(words)
    byfirst = {c: [] for c in '0123456789'}
    for i, word in enumerate(words):
        byfirst[word[0]].append((word, i))
    return words, byfirst


def matches(raw, i, index):
    for word, wi in index[raw[i]]:
        if raw.startswith(word, i):
            yield i+len(word), wi


def complete_parse(raw, words):
    words, index = make_index(words)
    if any(c not in '0123456789' for c in raw):
        raise ValueError('ASCII digit raw string required')
    counts = [0]*(len(raw)+1); counts[0] = 1
    parent = {}
    for i in range(len(raw)):
        if counts[i]:
            for end, wi in matches(raw, i, index):
                counts[end] += counts[i]
                parent.setdefault(end, (i, wi))
    path = []
    if counts[-1]:
        i = len(raw)
        while i:
            start, wi = parent[i]; path.append(words[wi]); i = start
        path.reverse()
        assert ''.join(path) == raw
    return {'count': counts[-1], 'one_path': path if counts[-1] else None,
            'unique_path': path if counts[-1] == 1 else None}


def gamma(n):
    if n < 1:
        raise ValueError('positive gamma integer required')
    b = bin(n)[2:]
    return '0'*(len(b)-1)+b


def read_gamma(bits, offset):
    start = offset
    while offset < len(bits) and bits[offset] == '0':
        offset += 1
    if offset == len(bits):
        raise ValueError('truncated gamma')
    width = offset-start+1
    if offset+width > len(bits):
        raise ValueError('truncated gamma value')
    return int(bits[offset:offset+width], 2), offset+width


def dictionary_wire(words):
    words = words_checked(words)
    return gamma(len(words)+1)+''.join(gamma(len(w)+1)+''.join(f'{int(c):04b}' for c in w) for w in words)


def decode_dictionary(bits):
    count, pos = read_gamma(bits, 0)
    words = []
    for _ in range(count-1):
        size, pos = read_gamma(bits, pos)
        chars = []
        for _ in range(size-1):
            if pos+4 > len(bits):
                raise ValueError('truncated dictionary digit')
            value = int(bits[pos:pos+4], 2); pos += 4
            if value > 9:
                raise ValueError('invalid dictionary digit')
            chars.append(str(value))
        words.append(''.join(chars))
    if pos != len(bits) or words != words_checked(words):
        raise ValueError('noncanonical dictionary or trailing bits')
    return words


def parse_and_encode(raw, words, keep_wire=True):
    words, index = make_index(words)
    if any(c not in '0123456789' for c in raw):
        raise ValueError('ASCII digit raw string required')
    n, width = len(raw), (len(words)-1).bit_length() if words else 0
    minlit, cost = [0]*(n+1), [0]*(n+1)
    literal_parent, wire_parent = [None]*n, [None]*n
    for i in range(n-1, -1, -1):
        minlit[i], literal_parent[i] = 1+minlit[i+1], (i+1, None)
        cost[i], wire_parent[i] = 5+cost[i+1], (i+1, None)
        for end, wi in matches(raw, i, index):
            if minlit[end] < minlit[i]:
                minlit[i], literal_parent[i] = minlit[end], (end, wi)
            if 1+width+cost[end] < cost[i]:
                cost[i], wire_parent[i] = 1+width+cost[end], (end, wi)
    header = gamma(n+1)
    raw_bits = 1+len(header)+4*n
    reference_bits = 1+len(header)+cost[0]
    use_references = reference_bits < raw_bits
    bits = None
    references = []
    if keep_wire:
        payload = []
        if use_references:
            i = 0
            while i < n:
                end, wi = wire_parent[i]
                if wi is None:
                    payload.append('0'+f'{int(raw[i]):04b}')
                else:
                    payload.append('1'+(format(wi, f'0{width}b') if width else ''))
                    references.append({'start': i, 'end': end, 'word': words[wi]})
                i = end
            bits = '1'+header+''.join(payload)
        else:
            bits = '0'+header+''.join(f'{int(c):04b}' for c in raw)
        assert len(bits) == min(raw_bits, reference_bits)
    return {'raw_bits': raw_bits, 'coded_bits': min(raw_bits, reference_bits),
            'reference_mode_bits': reference_bits, 'uses_references': use_references,
            'minimum_uncovered_digits': minlit[0], 'wire': bits,
            'references': references if keep_wire else None}


def decode_wire(bits, words):
    words = words_checked(words)
    if not bits or any(c not in '01' for c in bits):
        raise ValueError('binary bitstream required')
    mode = bits[0]
    length, pos = read_gamma(bits, 1); length -= 1
    width = (len(words)-1).bit_length() if words else 0
    out = []
    while sum(map(len, out)) < length:
        reference = False
        if mode == '1':
            if pos >= len(bits):
                raise ValueError('truncated token flag')
            reference = bits[pos] == '1'; pos += 1
        if reference:
            if not words or pos+width > len(bits):
                raise ValueError('invalid dictionary reference')
            wi = int(bits[pos:pos+width], 2) if width else 0; pos += width
            if wi >= len(words):
                raise ValueError('out of range reference')
            out.append(words[wi])
        else:
            if pos+4 > len(bits):
                raise ValueError('truncated raw digit')
            value = int(bits[pos:pos+4], 2); pos += 4
            if value > 9:
                raise ValueError('invalid raw digit')
            out.append(str(value))
    raw = ''.join(out)
    if len(raw) != length or pos != len(bits):
        raise ValueError('overshoot or trailing bits')
    return raw
