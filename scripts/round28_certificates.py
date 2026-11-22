#!/usr/bin/env python3
"""Independent positional-polynomial and reverse-DP audit of real constraints."""
from pathlib import Path
import json
import math
from unit_morphism_lexicon import banks

ROOT = Path(__file__).resolve().parents[1]


def independent_decode(raw, codec, key):
    number = int(raw)
    base = 27 if codec == 'space27' else 26
    if codec == 'bijective26':
        if number == 0:
            return None
        length = 1
        while number > 26*(26**length-1)//25:
            length += 1
        residual = number-(26**length-1)//25
    else:
        length = 1
        while number >= base**length:
            length += 1
        residual = number
    digits = []
    for exponent in range(length-1, -1, -1):
        digit = residual//base**exponent
        residual -= digit*base**exponent
        digits.append(digit)
    assert residual == 0
    offset = int(codec == 'bijective26')
    assert sum((d+offset)*base**i for i, d in enumerate(reversed(digits))) == number
    a, b = key
    return ''.join(' ' if codec == 'space27' and d == 0 else
                   chr(65+(a*(d-1 if codec == 'space27' else d)+b)%26) for d in digits)


def reverse_word_paths(text, codec, words, lengths):
    if codec == 'space27':
        return int(all(w in words for w in text.split()))
    if not text:
        return 0
    counts = [0]*(len(text)+1)
    counts[-1] = 1
    for start in range(len(text)-1, -1, -1):
        for size in lengths:
            end = start+size
            if end > len(text):
                break
            if text[start:end] in words:
                counts[start] += counts[end]
    return counts[0]


def audit(targets):
    words = frozenset(banks()[0]['grapheme1_3'].reverse)
    lengths = sorted(set(map(len, words)))
    keys = [(a, b) for a in range(26) if math.gcd(a, 26) == 1 for b in range(26)]
    jobs = []
    for name, solves in targets['full_source_search']['sources'].items():
        for solve in solves:
            jobs.append((name, 'whole_source', targets['raw_sources'][name]['groups'], solve))
    for discovery in targets['discoveries']:
        if discovery['discovery'] is not None:
            jobs.append((discovery['source'], 'prefix_discovery', discovery['training_groups'], discovery['discovery']))
    records = []
    for name, role, groups, solve in jobs:
        codec, framing = solve['codec'], solve['framing']
        frames = groups if framing == 'runs' else [''.join(groups)]
        accepted, checked = [], 0
        for index, key in enumerate(keys):
            failure, letters = None, 0
            for i, raw in enumerate(frames):
                decoded = independent_decode(raw, codec, key)
                checked += 1
                if decoded is None:
                    failure = {'frame': i, 'reason': 'zero_not_bijective26'}
                    break
                letters += len(decoded.replace(' ', ''))
                if not reverse_word_paths(decoded, codec, words, lengths):
                    failure = {'frame': i, 'reason': 'no_complete_lexical_parse', 'literal': decoded}
                    break
            if failure is None and not letters:
                failure = {'frame': None, 'reason': 'no_letters'}
            assert failure == solve['first_failure_per_key'][index]
            if failure is None:
                accepted.append(list(key))
        assert accepted == solve['keys']
        assert solve['complete'] and solve['keys_examined'] == len(keys)
        records.append({'source': name, 'role': role, 'codec': codec, 'framing': framing,
            'keys_exhaustively_checked': len(keys), 'frames_checked': checked,
            'accepted_keys': accepted, 'all_first_failure_certificates_match': True})
    return {'method': 'Length intervals and positional powers, without importing radix decoder; reverse word-length DP instead of trie. Same frozen lexical source.',
            'jobs': records, 'total_key_cases_checked': sum(r['keys_exhaustively_checked'] for r in records),
            'semantic_scope': 'Exact arithmetic/lexical compatibility only, not independently attested English translation'}


if __name__ == '__main__':
    targets = json.loads((ROOT/'results/round28_targets.json').read_text())
    result = audit(targets)
    path = ROOT/'results/round28_certificates.json'
    if path.exists():
        raise ValueError('Refusing to overwrite certificate audit')
    path.write_text(json.dumps(result, indent=2)+'\n')
    print('Independent exact audit:', result['total_key_cases_checked'], 'key cases')
