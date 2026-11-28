#!/usr/bin/env python3
"""Check conditional claims; no scoring, semantic selection, or new translation."""
import gzip
import itertools
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile

from round36_experiment import ROOT, GROUPS, invoke, load, verify
from unit_morphism_lexicon import banks
from unit_morphism_solver import word_extensions, word_pattern


def pair_decode(message, table):
    groups = re.findall(r'[0-9]+', message)
    padded = [('0' if len(g) % 2 else '') + g for g in groups]
    words = [''.join(table[g[i:i+2]] for i in range(0, len(g), 2)) for g in padded]
    return padded, words


def variants(word, expansions, permute=False):
    """Distinct strings, with one deterministic construction witness per string.

    Expanded chunks remain intact. Permute base symbols only, before expansion.
    This finite subset does not model every possible interpretation of anagram.
    """
    orders = sorted(set(itertools.permutations(word))) if permute else [tuple(word)]
    outputs = {}
    for order in orders:
        for parts in itertools.product(*(expansions[c] for c in order)):
            outputs.setdefault(''.join(parts), {'base_order': ''.join(order), 'units': list(parts)})
    return outputs


def article_check(claims):
    c = claims['article160']
    padded, literal = pair_decode(claims['numeric_message'], c['relevant_pair_map'])
    assert ' '.join(literal) == c['reported_literal']
    target = c['adjusted_claim'].split()
    assert len(literal) == len(target) == len(GROUPS)
    modes = {}
    for label, permute in [('ordered', False), ('permuted_base_symbols', True)]:
        rows = []
        for raw, base, wanted in zip(GROUPS, literal, target):
            choices = variants(base, c['expansions'], permute)
            rows.append({'raw': raw, 'literal': base, 'claimed': wanted,
                         'distinct_local_strings': len(choices),
                         'claim_is_reachable': wanted in choices,
                         'claim_witness': choices.get(wanted)})
        modes[label] = {'groups': rows,
                        'independent_position_choice_product': math.prod(r['distinct_local_strings'] for r in rows),
                        'complete_claim_reachable': all(r['claim_is_reachable'] for r in rows)}
    return {'padded_groups': padded, 'literal': ' '.join(literal), 'adjusted_claim': c['adjusted_claim'],
            'modes': modes,
            'scope': 'Exact finite reconstruction, allowing occurrence-specific expansions. Cartesian counts are strings with fixed word boundaries, not probabilities, fixed keys, grammatical sentences, or new candidates. No unknown text decoded.'}


def anchor_checks(claims):
    lexicon = set(banks()[0]['grapheme1_3'].reverse)
    reference = json.loads(gzip.decompress((ROOT/'results/round36/knightmare.json.gz').read_bytes()))
    assert reference['complete']
    marginals = {g['raw']: {r[0]: int(r[1]) for r in g['rows']} for g in reference['marginals']}
    rows = []
    with tempfile.TemporaryDirectory(prefix='469-r37-') as name:
        temp = Path(name)
        binary = temp/'counter'
        subprocess.run(['g++', '-O2', '-std=c++17', str(ROOT/'scripts/round33_count.cpp'), '-o', str(binary)], check=True)
        lexpath, inputpath = temp/'lexicon', temp/'input'
        lexpath.write_text('\n'.join(sorted(lexicon))+'\n')
        for claim in claims['anchor_claims']:
            raw, word = claim['raw'], claim['word']
            inputpath.write_text(str(len(GROUPS))+'\n'+''.join(g+' '+(word if g == raw else '-')+'\n' for g in GROUPS))
            fresh = invoke([binary, lexpath, inputpath])
            assert fresh['complete'], fresh
            expected = marginals[raw].get(word, 0)
            assert int(fresh['count']) == expected
            isolated = list(word_extensions(raw, word, 1, 3))
            row = dict(raw=raw, word=word, word_in_lexicon=word in lexicon,
                       isolated_assignments=isolated, marginal_count=expected,
                       fresh_count={k:v for k,v in fresh.items() if k != 'resources'},
                       counts_match=True)
            if word == 'KNOWLEDGE':
                assert len(isolated) == 1
                pattern = word_pattern('3466', 1, 3, isolated[0])
                row['forced_3466'] = {'regex': pattern.pattern,
                                      'lexical_matches': sorted(w for w in lexicon if pattern.fullmatch(w))}
            if len(word) < len(raw):
                row['length_certificate'] = {'minimum_output_letters': len(raw), 'claimed_letters': len(word)}
            rows.append(row)
    return {'total_unconditioned_keys': int(reference['count']), 'lexicon_forms': len(lexicon), 'claims': rows,
            'scope': 'R33/R36 fixed nonempty 1..3 letters per observed digit, numeric group equals lexical word. Zero rejects this conjunction only; does not reject arbitrary word codes or variable pair rules.'}


def calculate():
    verify('data/round37_input_manifest.json')
    verify('data/round37_execution_manifest.json')
    claims = load('data/round37_claims.json')
    return {'round': 37, 'article160': article_check(claims), 'anchors': anchor_checks(claims),
            'new_validated_translation': None, 'mission_outcome': 'I_inconclusive'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Preserve existing results'
    result = calculate()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
