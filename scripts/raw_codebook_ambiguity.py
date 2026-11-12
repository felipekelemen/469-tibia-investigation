#!/usr/bin/env python3
"""Finite constructive collisions, not a claim that469lacks meaning."""
import hashlib
import itertools
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def representations(code, mode):
    if mode == 'never':
        return [code]
    if mode == 'always':
        return [code[1:] if code.startswith('0') else code]
    if mode == 'optional_iid':
        return [code, code[1:]] if code.startswith('0') else [code]
    raise ValueError(mode)


def audit(inventory, mode):
    options = [(code, raw) for code in sorted(inventory) for raw in representations(code, mode)]
    wires = sorted({raw for _, raw in options})
    prefix_free = not any(a != b and b.startswith(a) for a in wires for b in wires)
    seen = {}
    collision = None
    for count in [1, 2]:
        for pieces in itertools.product(options, repeat=count):
            codes = [code for code, _ in pieces]
            raw = ''.join(part for _, part in pieces)
            prior = seen.get(raw)
            current = {'codes': codes, 'wire_pieces': [part for _, part in pieces]}
            if prior is not None and prior['codes'] != codes:
                collision = {'raw': raw, 'first': prior, 'second': current}
                break
            seen.setdefault(raw, current)
        if collision:
            break
    return {'mode': mode, 'wire_codewords': len(wires), 'prefix_free': prefix_free,
            'collision': collision,
            'verdict': 'noninjective_without_additional_constraints' if collision else
                       'uniquely_decodable_by_fixed_pairs' if prefix_free else 'not_resolved_by_this_finite_test'}


def main():
    path = ROOT / 'data/normalized_code_map.json'
    inventory = set(json.loads(path.read_text()))
    rows = [audit(inventory, mode) for mode in ['never', 'always', 'optional_iid']]
    # Verify the constructive witnesses independently of the collision search.
    for row in rows:
        if row['collision']:
            c = row['collision']
            for side in ['first', 'second']:
                witness = c[side]
                assert ''.join(witness['wire_pieces']) == c['raw']
                assert all(part in representations(code, row['mode'])
                           for code, part in zip(witness['codes'], witness['wire_pieces']))
            assert c['first']['codes'] != c['second']['codes']
    out = {'inventory_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
           'implementation_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           'inventory_codes': len(inventory), 'results': rows,
           'scope': 'Memoryless fixed-pair/always-omit/optional-IID serialization of the imported inventory only.',
           'limits': ['Constructive source-code ambiguity, not proof of multiple grammatical English meanings.',
                      'Does not establish that real469uses this inventory or omission model.',
                      'Contextual, framed, keyed, checksum or linguistic constraints can resolve some collisions; not assessed by this memoryless codebook test.',
                      'Statistical decoding can perform well despite noninjectivity, but cannot guarantee exact recovery of every possible source sequence without extra constraints.']}
    (ROOT / 'results/raw_codebook_ambiguity.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(rows, indent=2))


if __name__ == '__main__':
    main()
