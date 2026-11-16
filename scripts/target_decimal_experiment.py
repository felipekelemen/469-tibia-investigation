#!/usr/bin/env python3
"""Frozen targeted English search with lexical scope and transfer held separate."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re

from independent_word_validator import body, words
from target_decimal_solver import Solver, FAMILIES, complete_keys, encode, letter_parse, dictionary_parse_count

ROOT = Path(__file__).resolve().parents[1]
SEED = 204693478


def load(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def dump(path, value):
    (ROOT/path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def vocabulary():
    tokens = [w for name in ('secret_garden', 'my_man_jeeves')
              for w in words(body(ROOT/f'data/word_validator_reference/{name}.txt'))]
    return sorted({w for w in tokens if len(w) > 1 or w in ('A', 'I')})


def search(groups, solvers):
    return {family: solver.solve(groups) for family, solver in solvers.items()}


def transfer(solutions, solvers, groups, unspaced=False):
    rows = []; incomplete = []
    for family, solution in solutions.items():
        keys = complete_keys(solution)
        if keys is None:
            incomplete.append(family); continue
        for key in keys:
            row = {'family': family, 'cipher_to_decimal': dict(key)}
            row['letter_parses'] = [letter_parse(g, family, key) for g in groups]
            if unspaced:
                row['dictionary_segmentation_counts'] = [dictionary_parse_count(g, solvers[family], key) for g in groups]
            else:
                row['word_candidates'] = [solvers[family].words_for(g, key) for g in groups]
            rows.append(row)
    return {'rows': rows, 'incomplete_families': incomplete,
            'scope': 'All fitting keys applied unchanged. Empty rows are no surviving fitted key, not decoded empty text. Lexical coverage is not grammar.'}


def qualification(solvers, vocab):
    docs = {name: words(body(ROOT/f'data/word_validator_reference/{name}.txt')) for name in ('wizard_oz', 'peter_pan')}
    starts = {(name, n): [i for i in range(len(doc)-n-7) if all(w in vocab for w in doc[i:i+n])]
              for name, doc in docs.items() for n in (7, 20)}
    rows = []
    for fi, (family, solver) in enumerate(solvers.items()):
        for n in (7, 20):
            rng = random.Random(SEED+fi*100+n)
            for trial in range(30):
                name = ('wizard_oz', 'peter_pan')[trial % 2]
                start = rng.choice(starts[name, n]); doc = docs[name]
                fit, held = doc[start:start+n], doc[start+n:start+n+7]
                shuffled = list('0123456789'); rng.shuffle(shuffled)
                encryption = dict(zip('0123456789', shuffled)); true_key = {v:k for k,v in encryption.items()}
                enc = lambda w: ''.join(encryption[c] for c in encode(w, family))
                fitraw, heldraw = list(map(enc, fit)), list(map(enc, held))
                solution = solver.solve(fitraw)
                retained = any(all(true_key[k] == v for k,v in m) for m in solution['mappings'])
                keys = complete_keys(solution)
                candidate_sets = [sorted({w for key in keys for w in solver.words_for(g, key)}) for g in heldraw] if keys is not None else None
                wrong = sum(len(c) == 1 and c != [w] for c,w in zip(candidate_sets, held)) if candidate_sets is not None else 0
                correct = sum(c == [w] for c,w in zip(candidate_sets, held)) if candidate_sets is not None else 0
                literal = []
                if keys is not None:
                    for g, w in zip(heldraw, held):
                        parsings = [letter_parse(g, family, key) for key in keys]
                        literal.append(bool(parsings) and all(p['unique_literal'] == w for p in parsings))
                rows.append({'family':family,'fit_words':n,'trial':trial,'source':name,'start_word':start,
                             'truth_fit':fit,'truth_held':held,'raw_fit':fitraw,'raw_held':heldraw,
                             'true_cipher_to_decimal':true_key,'complete':solution['complete'],
                             'key_transfer_complete':keys is not None,'nodes':solution['nodes'],
                             'partial_key_count':len(solution['mappings']),'full_key_count':solution['full_key_count'],
                             'truth_retained':retained,'held_oov':sum(w not in vocab for w in held),
                             'held_unique_correct':correct,'held_wrong_singleton':wrong,
                             'literal_unique_correct':sum(literal),'held_word_candidates':candidate_sets})
    summary = []
    for family in solvers:
        for n in (7, 20):
            cell = [r for r in rows if r['family'] == family and r['fit_words'] == n]
            inlex = sum(7-r['held_oov'] for r in cell)
            good = sum(r['held_unique_correct'] for r in cell)
            wrong = sum(r['held_wrong_singleton'] for r in cell)
            eligible = all(r['complete'] and r['key_transfer_complete'] and r['truth_retained'] for r in cell)
            summary.append({'family':family,'fit_words':n,'fixtures':len(cell),'all_complete_truth_retained':eligible,
                            'held_total':210,'held_in_lexicon':inlex,'held_unique_correct':good,
                            'held_wrong_singletons':wrong,'literal_unique_correct':sum(r['literal_unique_correct'] for r in cell),
                            'gate_pass':eligible and wrong == 0 and good >= .9*inlex})
    return {'summary':summary,'rows':rows,'scope':'New seeded fixtures from previously used external authors; not new unseen source authors. Fit spans conditioned on lexicon inclusion; held words unfiltered. Family supplied; this does not qualify unknown-family English detection.'}


def build():
    vocab = vocabulary(); solvers = {f: Solver(vocab, f) for f in FAMILIES}
    q = qualification(solvers, set(vocab))
    print('Qualification complete:', sum(r['gate_pass'] for r in q['summary']), '/14 cells', flush=True)
    inv = {r['id']: r for r in load('data/source_validation_inventory.json')}
    avar = re.findall(r'\d+', inv['avar_tar_poem']['text'])
    knight = re.findall(r'\d+', inv['knightmare_2012']['text'])
    chayenne = [inv[k]['text'] for k in ('chayenne_2009_part1','chayenne_2009_part2')]
    inputs = {'avar_prefix10':avar[:10], 'knightmare7':knight, 'avar_full20_diagnostic':avar}
    game = {}
    for name, groups in inputs.items():
        fits = search(groups, solvers)
        held = avar[10:] if name == 'avar_prefix10' else avar
        game[name] = {'fit_groups':groups, 'solutions':fits,
                      'avar_transfer':transfer(fits, solvers, held),
                      'knightmare_transfer':transfer(fits, solvers, knight),
                      'chayenne_transfer':transfer(fits, solvers, chayenne, True)}
        print(name, {f:s['full_key_count'] for f,s in fits.items()}, flush=True)
    controls = []
    for ti, name in enumerate(('avar_prefix10','knightmare7')):
        groups = inputs[name]
        for ki, kind in enumerate(('all_digit_shuffle', 'within_distinct_word_shuffle')):
            rng = random.Random(SEED+10000+ti*100+ki)
            trials = []
            for trial in range(99):
                if kind == 'all_digit_shuffle':
                    chars = list(''.join(groups)); rng.shuffle(chars); offset = 0; changed = []
                    for g in groups:
                        changed.append(''.join(chars[offset:offset+len(g)])); offset += len(g)
                else:
                    mapping = {}
                    for g in sorted(set(groups)):
                        chars = list(g); rng.shuffle(chars); mapping[g] = ''.join(chars)
                    changed = [mapping[g] for g in groups]
                fits = search(changed, solvers)
                trials.append({'trial':trial,'groups':changed,'complete':all(s['complete'] for s in fits.values()),
                               'partial_keys':{f:len(s['mappings']) for f,s in fits.items()},
                               'full_keys':sum(s['full_key_count'] for s in fits.values())})
            controls.append({'target':name,'kind':kind,'replicates':99,
                             'with_any_key':sum(r['full_keys'] > 0 for r in trials),'all_complete':all(r['complete'] for r in trials), 'rows':trials})
    # Search is invariant to an arbitrary bijective relabeling of ciphertext digits.
    renamed = {}; rename = str.maketrans('0123456789','7654321098')
    for name, groups in inputs.items():
        fits = search([g.translate(rename) for g in groups], solvers)
        renamed[name] = {f:{'full_keys':s['full_key_count'],'complete':s['complete'],
                           'count_matches':s['full_key_count'] == game[name]['solutions'][f]['full_key_count']} for f,s in fits.items()}
    return {'lexicon_size':len(vocab),'qualification':q,'game':game,'controls':controls,
            'global_relabel_invariance':renamed,'new_verified_translations':0,
            'scope':'All exclusions conditional on fixed lexicon, letter codecs, digit bijection and word boundaries. No lore completion, grammar inference or independent semantic validation.'}


def freeze():
    path = ROOT/'data/round20_evidence_manifest.json'
    if path.exists():
        raise ValueError('already frozen')
    files = ['data/round20_protocol.json','scripts/target_decimal_solver.py','scripts/target_decimal_experiment.py',
             'scripts/independent_word_validator.py','data/source_validation_inventory.json']
    files += [f'data/word_validator_reference/{n}.txt' for n in ('secret_garden','my_man_jeeves','wizard_oz','peter_pan')]
    dump('data/round20_evidence_manifest.json', {'stage':'Before benchmark and target search', 'sha256':{p:sha(p) for p in files}})


def run(check=False):
    for p,h in load('data/round20_evidence_manifest.json')['sha256'].items():
        if sha(p) != h:
            raise ValueError('frozen input changed: '+p)
    result = build()
    if check:
        if result != load('results/round20_target_decimal.json'):
            raise ValueError('replay mismatch')
    else:
        dump('results/round20_target_decimal.json', result)
    print('Full replay matches.' if check else 'Results saved; literal candidates require independent review.', flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--freeze',action='store_true'); parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.freeze:
        freeze()
    else:
        run(args.check)
