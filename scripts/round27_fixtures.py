#!/usr/bin/env python3
"""Freeze seeded synthetic inputs before fitting; never select by recovery."""
from collections import Counter
from pathlib import Path
import json
import random
import re
from unit_morphism_lexicon import banks, Bank

ROOT = Path(__file__).resolve().parents[1]


def training_bank(protocol):
    original = banks()[0]['grapheme1_3']
    excluded = set(protocol['name_labels'])
    return Bank('grapheme1_3', {f: set(ws) - excluded
        for f, ws in original.reverse.items() if set(ws) - excluded}, original.labels)


def encode_random(form, key, rng):
    paths = {len(form): ''}
    for i in range(len(form)-1, -1, -1):
        possible = [d + paths[i+len(u)] for d, u in key.items()
                    if form.startswith(u, i) and i+len(u) in paths]
        if possible:
            paths[i] = rng.choice(possible)
    return paths.get(0)


def create(protocol):
    rng = random.Random(protocol['seed'])
    bank = training_bank(protocol)
    forms = sorted(bank.reverse)
    counts = Counter()
    # Pools retain the previously declared complete CMU orthographic reference.
    for form in sorted(banks()[0]['grapheme1_3'].reverse):
        for n in (1, 2, 3):
            counts.update(form[i:i+n] for i in range(len(form)-n+1))
    pools = {n: sorted((u for u in counts if len(u) == n),
                      key=lambda u: (-counts[u], u))[:40] for n in (1, 2, 3)}
    result = {'seed': protocol['seed'], 'pools': pools, 'cases': [], 'attempts': {}}
    for kind in ('base', 'homophonic'):
        made = 0
        for attempt in range(1, protocol['fixture_budget']['max_generation_attempts_per_family']+1):
            units = rng.sample(pools[1], 6) + rng.sample(pools[2], 2) + rng.sample(pools[3], 2)
            rng.shuffle(units)
            if kind == 'homophonic':
                units[-1] = units[0]
            key = dict(zip('0123456789', units))
            pattern = re.compile('(?:' + '|'.join(map(re.escape, units)) + ')+')
            names = [f for f in protocol['name_labels'] if pattern.fullmatch(f)]
            if not names:
                continue
            eligible = [f for f in forms if pattern.fullmatch(f)]
            if len(eligible) < 60:
                continue
            encoded = {f: encode_random(f, key, rng) for f in eligible}
            if set(''.join(encoded.values())) != set(key):
                continue
            selected, seen, remaining = [], set(), set(eligible)
            for _ in range(7):
                f = min(remaining, key=lambda w: (-len(set(encoded[w])-seen),
                        -len(set(encoded[w])), -len(encoded[w]), w))
                selected.append(f)
                seen.update(encoded[f])
                remaining.remove(f)
            if seen != set(key):
                continue
            rest = sorted(remaining)
            rng.shuffle(rest)
            train_forms, held_forms = selected + rest[:23], rest[23:33]
            train = [encoded[f] for f in train_forms]
            held = [encoded[f] for f in held_forms]
            possibilities = [d for d in sorted(key)
                if sum(d not in raw for raw in train) >= 7 and any(d in raw for raw in held)]
            if not possibilities:
                continue
            missing = possibilities[0]
            result['cases'].append({'id': f'{kind}_{made:02d}', 'kind': kind,
                'key': key, 'train': train, 'train_forms': train_forms,
                'held': held, 'held_forms': held_forms,
                'names': [{'raw': encode_random(f, key, rng), 'form': f} for f in names],
                'missing_digit': missing, 'generation_attempt': attempt,
                'eligible_forms': len(eligible)})
            made += 1
            print('fixture', kind, made, 'attempt', attempt, flush=True)
            if made == protocol['fixture_budget'][kind+'_cases']:
                break
        result['attempts'][kind] = attempt
        if made != protocol['fixture_budget'][kind+'_cases']:
            raise RuntimeError(f'Frozen generation budget exhausted: {kind}, {made}')
    # Diagnostics drawn without consulting solver outcomes.
    phonebank = banks()[0]['phone1_3']
    eligible = [f for f in sorted(phonebank.reverse)
                if len(phonebank.reverse[f]) >= 2 and len(set(f)) <= 10]
    result['phonetic'] = []
    for form in rng.sample(eligible, 30):
        digits = rng.sample(list('0123456789'), len(set(form)))
        mapping = dict(zip(sorted(set(form)), digits))
        result['phonetic'].append({'form': form, 'raw': ''.join(mapping[u] for u in form),
            'key': {d: u for u, d in mapping.items()}, 'spellings': phonebank.reverse[form]})
    result['hidden_vocabulary'] = []
    for _ in range(30):
        digits = list('0123456789')
        rng.shuffle(digits)
        trans = str.maketrans('0123456789', ''.join(digits))
        result['hidden_vocabulary'].append({
            'a': [s.translate(trans) for s in ['1234', '5678', '9012']],
            'b': [s.translate(trans) for s in ['12345', '678', '9012']],
            'train': ('123456789012'*3).translate(trans),
            'novel': '12349012'.translate(trans)})
    return result


if __name__ == '__main__':
    path = ROOT/'data/round27_fixtures.json'
    if path.exists():
        raise SystemExit('Refusing to replace frozen fixtures')
    protocol = json.loads((ROOT/'data/round27_protocol.json').read_text())
    fixtures = create(protocol)
    path.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2)+'\n')
