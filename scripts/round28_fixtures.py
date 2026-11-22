#!/usr/bin/env python3
"""New-author nonoverlapping windows, fixed before search and target decoding."""
from pathlib import Path
import json
import random
import re
from round28_radix import CODECS, FRAMINGS, KEYS, Lexicon, encode

ROOT = Path(__file__).resolve().parents[1]


def source_words(record):
    text = (ROOT/record['path']).read_bytes().decode(record['encoding'])
    start = re.search(r'\*\*\*\s*START OF[^\n]*\*\*\*', text)
    end = re.search(r'\*\*\*\s*END OF[^\n]*\*\*\*', text)
    if not start or not end or start.end() >= end.start():
        raise ValueError('Missing or reversed public-domain body markers')
    return [re.sub('[^A-Z]', '', word.upper()) for word in
            re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)*", text[start.end():end.start()])]


def plain_frames(words, framing):
    return list(words) if framing == 'runs' else [' '.join(words)]


def create(protocol):
    rng = random.Random(protocol['positive_seed'])
    records = json.loads((ROOT/'data/round28_reference/SOURCES.json').read_text())
    lexicon = Lexicon()
    windows, used = [], {record['path']: set() for record in records}
    for profile, rules in protocol['positive_profiles'].items():
        for record in records:
            words = source_words(record)
            width = rules['train_words']+rules['held_words']
            made = 0
            for attempt in range(1, protocol['generator_attempt_limit_per_profile_author']+1):
                start = rng.randrange(len(words)-width+1)
                positions = set(range(start, start+width))
                if positions & used[record['path']]:
                    continue
                train = words[start:start+rules['train_words']]
                held = words[start+rules['train_words']:start+width]
                if not all(word in lexicon.words for word in train):
                    continue
                low, high = rules['train_letter_range']
                if not low <= sum(map(len, train)) <= high:
                    continue
                if rules['held_letter_range']:
                    low, high = rules['held_letter_range']
                    if not low <= sum(map(len, held)) <= high:
                        continue
                used[record['path']].update(positions)
                windows.append({'id': f'{profile}_{len(windows):02d}', 'profile': profile,
                    'source': record['path'], 'author': record['author'],
                    'start_word': start, 'end_word': start+width,
                    'train_words': train, 'held_words': held,
                    'generation_attempt': attempt})
                made += 1
                if made == 15:
                    break
            if made != 15:
                raise RuntimeError('Frozen generation budget exhausted')
    cases = []
    for window in windows:
        for codec in CODECS:
            for framing in FRAMINGS:
                train = plain_frames(window['train_words'], framing)
                held = plain_frames(window['held_words'], framing)
                allowed = list(KEYS)
                if codec == 'canonical26':
                    forbidden = {ord(s.replace(' ', '')[0])-65 for s in train+held
                                 if len(s.replace(' ', '')) > 1}
                    allowed = [key for key in KEYS if key[1] not in forbidden]
                key = rng.choice(allowed)
                train_raw = [encode(s, codec, key, rng.randrange(3)) for s in train]
                held_raw = [encode(s, codec, key, rng.randrange(3)) for s in held]
                cases.append({'id': window['id']+'_'+codec+'_'+framing,
                    'window_id': window['id'], 'profile': window['profile'],
                    'codec': codec, 'framing': framing, 'key': list(key),
                    'allowed_generator_keys': len(allowed),
                    'train': train_raw, 'held': held_raw,
                    'train_words': window['train_words'], 'held_words': window['held_words']})
    return {'selection': 'No solver outcome used.90nonoverlapping windows paired across6settings; discovery vocabulary-conditioned, held vocabulary unfiltered.',
            'windows': windows, 'cases': cases}


if __name__ == '__main__':
    protocol = json.loads((ROOT/'data/round28_protocol.json').read_text())
    out = ROOT/'data/round28_fixtures.json'
    if out.exists():
        raise ValueError('Refusing to replace frozen fixtures')
    fixtures = create(protocol)
    out.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2)+'\n')
    print('Frozen', len(fixtures['windows']), 'windows and', len(fixtures['cases']), 'fits')
