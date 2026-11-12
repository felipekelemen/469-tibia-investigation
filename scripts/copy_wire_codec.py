#!/usr/bin/env python3
"""Two exact conditional prefix codecs; no language score or inferred plaintext.

The source books AND their compatible boundary annotations are shared side
information. Reported bits encode a target conditional on those sources.
"""
import hashlib

from zero_rule_constraints import alignments


def width(n):
    if n < 1:
        raise ValueError('nonempty address space required')
    return (n - 1).bit_length()


def fixed(value, n):
    if not 0 <= value < n:
        raise ValueError('address outside space')
    return format(value, f'0{width(n)}b') if width(n) else ''


def gamma(value):
    if value < 1:
        raise ValueError('positive gamma integer required')
    binary = bin(value)[2:]
    return '0' * (len(binary) - 1) + binary


def prepare(books, maximum=96):
    if not books or maximum < 1 or any(not b['digits'] for b in books):
        raise ValueError('nonempty sources and positive maximum required')
    offsets = []
    for b in books:
        a = alignments(b)
        if not a['count'] or not a['enumeration_complete']:
            raise ValueError('source alignments must be complete and nonempty')
        positions = []
        for omitted in a['paths']:
            mask = set(omitted)
            p = [0]
            for i in range(len(b['codes'])):
                p.append(p[-1] + (1 if i in mask else 2))
            positions.append(p)
        offsets.append(positions)
    return {'books': books, 'offsets': offsets, 'maximum': maximum}


def reference(context, family, book, start, count, alignment=0):
    b = context['books'][book]
    prefix = '1' + fixed(book, len(context['books']))
    if family == 'raw':
        return prefix + fixed(start, len(b['digits'])) + gamma(count)
    if family == 'codes':
        return (prefix + fixed(alignment, len(context['offsets'][book]))
                + fixed(start, len(b['codes'])) + gamma(count))
    raise ValueError('unknown family')


def build_index(context, family):
    index = {}

    def put(raw, bits, witness):
        previous = index.get(raw)
        if previous is None or (len(bits), bits) < (len(previous[0]), previous[0]):
            index[raw] = (bits, witness)

    for bi, b in enumerate(context['books']):
        if family == 'raw':
            for start in range(len(b['digits'])):
                for end in range(start + 1, min(len(b['digits']), start + context['maximum']) + 1):
                    put(b['digits'][start:end], reference(context, family, bi, start, end - start),
                        {'book_index': bi, 'raw_start': start, 'raw_end': end})
        elif family == 'codes':
            for ai, positions in enumerate(context['offsets'][bi]):
                for start in range(len(b['codes'])):
                    for end in range(start + 1, len(b['codes']) + 1):
                        if positions[end] - positions[start] > context['maximum']:
                            break
                        put(b['digits'][positions[start]:positions[end]],
                            reference(context, family, bi, start, end - start, ai),
                            {'book_index': bi, 'alignment_index': ai, 'code_start': start,
                             'code_end': end, 'raw_start': positions[start], 'raw_end': positions[end]})
        else:
            raise ValueError('unknown family')
    return index


class Reader:
    def __init__(self, bits):
        if set(bits) - {'0', '1'}:
            raise ValueError('binary stream required')
        self.bits, self.pos = bits, 0

    def take(self, n):
        if self.pos + n > len(self.bits):
            raise ValueError('truncated bitstream')
        text = self.bits[self.pos:self.pos + n]
        self.pos += n
        return int(text, 2) if n else 0

    def address(self, n):
        result = self.take(width(n))
        if result >= n:
            raise ValueError('invalid fixed-width address')
        return result

    def integer(self):
        zeros = 0
        while self.take(1) == 0:
            zeros += 1
        return (1 << zeros) + self.take(zeros)


def decode(bits, context):
    r = Reader(bits)
    family = 'raw' if r.take(1) == 0 else 'codes'
    length = r.integer() - 1
    output = ''
    while len(output) < length:
        if r.take(1) == 0:
            digit = r.take(4)
            if digit > 9:
                raise ValueError('invalid digit')
            output += str(digit)
        else:
            bi = r.address(len(context['books']))
            b = context['books'][bi]
            if family == 'raw':
                start = r.address(len(b['digits']))
                count = r.integer()
                end = start + count
                if end > len(b['digits']):
                    raise ValueError('reference outside book')
                text = b['digits'][start:end]
            else:
                ai = r.address(len(context['offsets'][bi]))
                start = r.address(len(b['codes']))
                count = r.integer()
                if start + count > len(b['codes']):
                    raise ValueError('reference outside book')
                p = context['offsets'][bi][ai]
                text = b['digits'][p[start]:p[start + count]]
            if len(text) > context['maximum']:
                raise ValueError('reference exceeds protocol maximum')
            output += text
        if len(output) > length:
            raise ValueError('target length exceeded')
    if r.pos != len(bits):
        raise ValueError('trailing bits')
    return output


def encode(raw, context, family, index=None):
    if set(raw) - set('0123456789'):
        raise ValueError('ASCII digits required')
    if family not in ('raw', 'codes'):
        raise ValueError('unknown family')
    if index is None:
        index = build_index(context, family)
    n = len(raw)
    best, ways, choice = [0] * (n + 1), [0] * (n + 1), [None] * n
    ways[n] = 1
    for start in range(n - 1, -1, -1):
        bits = '0' + fixed(int(raw[start]), 16)
        best[start], ways[start], choice[start] = 5 + best[start + 1], ways[start + 1], (start + 1, bits, None)
        for end in range(start + 1, min(n, start + context['maximum']) + 1):
            match = index.get(raw[start:end])
            if match is None:
                continue
            token, witness = match
            cost = len(token) + best[end]
            if cost < best[start]:
                best[start], ways[start], choice[start] = cost, ways[end], (end, token, witness)
            elif cost == best[start]:
                ways[start] += ways[end]
    header = ('0' if family == 'raw' else '1') + gamma(n + 1)
    payload, path, start = [], [], 0
    while start < n:
        end, bits, witness = choice[start]
        payload.append(bits)
        path.append({'target_start': start, 'target_end': end, 'raw': raw[start:end],
                     'token_bits': len(bits), 'witness': witness})
        start = end
    bitstream = header + ''.join(payload)
    if decode(bitstream, context) != raw or len(bitstream) != len(header) + best[0]:
        raise AssertionError('lossless prefix codec failed')
    return {'family': family, 'raw_length': n, 'bits': len(bitstream), 'header_bits': len(header),
            'literal_digits': sum(x['target_end'] - x['target_start'] for x in path if x['witness'] is None),
            'references': sum(x['witness'] is not None for x in path),
            'minimum_cost_parses_after_cheapest_witness_deduplication': str(ways[0]),
            'bitstream': bitstream, 'bitstream_sha256': hashlib.sha256(bitstream.encode()).hexdigest(),
            'path': path, 'roundtrip_verified': True}
