#!/usr/bin/env python3
"""Round15: explicit finite matrix/password family, no guessed skull borders.

Run --freeze before --run. All selected output literals are retained. The
family search, including whitening and output alphabet, is repeated for nulls.
"""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import re
import time

import numpy as np

from historical_matrix_checks import views
from hill29_experiments import normalize_english
from matrix_experiments import MATRICES, determinant, inverse, transpose

ROOT = Path(__file__).resolve().parents[1]
ALPHABETS = {25: 'ABCDEFGHIKLMNOPQRSTUVWXYZ', 26: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
             29: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ .?'}
PARTIAL = [[1, 1, 1], [1, 3, 6], [1, 1, 4]]
WORDS = ('BEHOLDER', 'BONELORD')
WHITEN = ('none', 'pre_plus_3478', 'pre_minus_3478', 'post_plus_3478', 'post_minus_3478')
SEED = 153478


def dump(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def normalized(raw, q):
    text = normalize_english(raw)
    if q != 29:
        text = re.sub('[^A-Z]', '', text)
    return text.replace('J', 'I') if q == 25 else text


def alphabet(q, keyword):
    canonical = ALPHABETS[q]
    return ''.join(dict.fromkeys(keyword + canonical)) if keyword else canonical


def password_matrix(word, n, q, base):
    text = (word * ((n*n + len(word)-1)//len(word)))[:n*n]
    seq = [ALPHABETS[q].index(c) + base for c in text]
    return [seq[i:i+n] for i in range(0, n*n, n)]


def key_records():
    rows = []
    for name, m in [('reported3', PARTIAL), *MATRICES.items()]:
        for reflected, turns, oriented in views(m):
            for q in (25, 26, 29):
                rows.append(dict(kind='reported_table', name=name, n=len(m), q=q,
                                 reflected=reflected, turns=turns, matrix=oriented,
                                 eligible_fresh=(len(m) == 3 or q == 25)))
    for n in (3, 4, 5):
        for word in WORDS:
            for q in ALPHABETS:
                for base in (0, 1):
                    m = password_matrix(word, n, q, base)
                    for transposed in (False, True):
                        rows.append(dict(kind='conjectured_password', name=word, n=n, q=q,
                                         ordinal_base=base, transposed=transposed,
                                         matrix=transpose(m) if transposed else m, eligible_fresh=True))
    for row in rows:
        row['determinant'] = determinant(row['matrix'])
        row['invertible'] = math.gcd(row['determinant'], row['q']) == 1
    return rows


def catalog():
    unique = {}
    for key in key_records():
        if not key['invertible'] or not key['eligible_fresh']:
            continue
        q = key['q']
        for direction in ('forward', 'inverse'):
            op = key['matrix'] if direction == 'forward' else inverse(key['matrix'], q)
            op = [[x % q for x in row] for row in op]
            for keyword in ('', *WORDS):
                out = alphabet(q, keyword)
                for whitening in WHITEN:
                    signature = (q, tuple(map(tuple, op)), out, whitening)
                    alias = {k: v for k, v in key.items() if k not in ('matrix', 'invertible', 'eligible_fresh')}
                    alias.update(direction=direction, output_keyword=keyword)
                    if signature in unique:
                        unique[signature]['aliases'].append(alias)
                    else:
                        unique[signature] = dict(q=q, n=key['n'], operator=op,
                                                 output_alphabet=out, whitening=whitening, aliases=[alias])
    result = list(unique.values())
    for i, c in enumerate(result):
        c['id'] = i
    return result


def framed(values, n):
    blocks, phases, windows, cursor = [], [], [], 0
    for arr in values:
        length = len(arr)//n*n
        blocks.extend(np.asarray(arr[:length], dtype=np.int64).reshape(-1, n))
        phases.extend(np.arange(length) % 4)
        windows.extend(range(cursor, cursor + max(0, length-3)))
        cursor += length
    return (np.asarray(blocks, dtype=np.int64).reshape(-1, n),
            np.asarray(phases, dtype=np.int64), np.asarray(windows, dtype=np.int64))


def decoded_batch(prepared, candidates):
    x, phase, _ = prepared
    if not len(x):
        return np.empty((len(candidates), 0), dtype=np.int64)
    q = candidates[0]['q']
    ops = np.asarray([c['operator'] for c in candidates], dtype=np.int64)
    raw = np.einsum('kij,bj->kbi', ops, x).reshape(len(candidates), -1)
    key = np.asarray([3, 4, 7, 8], dtype=np.int64)[phase]
    pre = np.einsum('kij,bj->kbi', ops, key.reshape(-1, candidates[0]['n'])).reshape(len(candidates), -1)
    pre_sign = np.asarray([1 if c['whitening'] == WHITEN[1] else -1 if c['whitening'] == WHITEN[2] else 0 for c in candidates])
    post_sign = np.asarray([1 if c['whitening'] == WHITEN[3] else -1 if c['whitening'] == WHITEN[4] else 0 for c in candidates])
    raw = (raw + pre_sign[:, None]*pre + post_sign[:, None]*key) % q
    maps = np.asarray([[ALPHABETS[q].index(ch) for ch in c['output_alphabet']] for c in candidates])
    return np.take_along_axis(maps, raw, axis=1)


def language_model(q):
    raw = normalized((ROOT / 'data/english_reference/alice.txt').read_text(encoding='utf-8-sig'), q)
    text = raw[:int(.8*len(raw))]
    counts = collections.Counter(text[i:i+4] for i in range(len(text)-3))
    denom = sum(counts.values()) + .01*q**4
    table = np.full(q**4, math.log10(.01/denom))
    for gram, count in counts.items():
        index = 0
        for ch in gram:
            index = q*index + ALPHABETS[q].index(ch)
        table[index] = math.log10((count+.01)/denom)
    return table


def search(values, bank, model):
    scores = np.full(len(bank), -np.inf)
    for n in sorted({c['n'] for c in bank}):
        prepared = framed(values, n)
        win = prepared[2]
        group = [i for i, c in enumerate(bank) if c['n'] == n]
        for start in range(0, len(group), 96):
            ids = group[start:start+96]
            out = decoded_batch(prepared, [bank[i] for i in ids])
            if not len(win):
                continue
            q = bank[0]['q']
            indices = ((out[:, win]*q + out[:, win+1])*q + out[:, win+2])*q + out[:, win+3]
            scores[ids] = model[indices].mean(axis=1)
    winner = int(np.argmax(scores))
    return bank[winner], float(scores[winner])


def decode(values, c):
    result = []
    for arr in values:
        seq = decoded_batch(framed([arr], c['n']), [c])[0]
        result.append(''.join(ALPHABETS[c['q']][int(i)] for i in seq))
    return result


def fixed_score(values, c, model):
    prepared = framed(values, c['n'])
    out = decoded_batch(prepared, [c])[0]
    w = prepared[2]
    if not len(w):
        return None
    q = c['q']
    return float(model[((out[w]*q+out[w+1])*q+out[w+2])*q+out[w+3]].mean())


def encode(text, c, rng):
    n, q = c['n'], c['q']
    if len(text) % n:
        raise ValueError('positive fixture length must be divisible by block size')
    residue = np.asarray([c['output_alphabet'].index(ch) for ch in text], dtype=np.int64)
    key = np.asarray([3, 4, 7, 8])[np.arange(len(text)) % 4]
    if c['whitening'] == WHITEN[3]:
        residue -= key
    elif c['whitening'] == WHITEN[4]:
        residue += key
    inv = np.asarray(inverse(c['operator'], q))
    values = (residue.reshape(-1, n) @ inv.T).reshape(-1) % q
    if c['whitening'] == WHITEN[1]:
        values = (values-key) % q
    elif c['whitening'] == WHITEN[2]:
        values = (values+key) % q
    return [int(x) + q*rng.randrange((99-int(x))//q+1) for x in values]


def numeric_pairs(text):
    return [int(text[i:i+2]) for i in range(0, len(text)-1, 2)]


def qualifications(bank, models, protocol):
    rng = random.Random(SEED)
    references = {name: (ROOT / 'data/word_validator_reference' / name).read_text(encoding='utf-8-sig')
                  for name in protocol['positive_controls']['references']}
    rows = []
    for n, q in sorted({(c['n'], c['q']) for c in bank}):
        eligible = [c for c in bank if (c['n'], c['q']) == (n, q)]
        qbank = [c for c in bank if c['q'] == q]
        for trial in range(30):
            author = list(references)[trial % len(references)]
            text = normalized(references[author], q)
            cut = len(text)//2
            a = rng.randrange(cut-300)
            b = rng.randrange(cut, len(text)-180)
            train, held = text[a:a+300], text[b:b+180]
            truth = eligible[rng.randrange(len(eligible))]
            train_values, held_values = encode(train, truth, rng), encode(held, truth, rng)
            raw = ''.join(f'{x:02d}' for x in train_values)
            assert numeric_pairs(raw) == train_values
            fitted, score = search([numeric_pairs(raw)], qbank, models[q])
            prediction = decode([held_values], fitted)[0]
            acc = sum(x == y for x, y in zip(prediction, held))/len(held)
            rows.append(dict(n=n, q=q, trial=trial, reference=author, train_offset=a, held_offset=b,
                             true_id=truth['id'], selected_id=fitted['id'], train_score=score,
                             held_accuracy=acc, held_exact=prediction == held))
    summary = []
    for n, q in sorted({(r['n'], r['q']) for r in rows}):
        group = [r for r in rows if (r['n'], r['q']) == (n, q)]
        passed = sum(r['held_accuracy'] >= .95 for r in group)
        summary.append(dict(n=n, q=q, cases=len(group), recovered_ge95=passed,
                            exact=sum(r['held_exact'] for r in group), gate_passed=passed >= 27))
    return dict(summary=summary, cases=rows,
                scope='Operational closed-family test, known modulus. No omitted zeros; two already exposed authors; not authentication of game English or an unknown raw parser.')


def algebra():
    matrices = []
    for name, m in [('reported3', PARTIAL), *MATRICES.items()]:
        d = determinant(m)
        matrices.append(dict(name=name, n=len(m), matrix=m, determinant=d,
                             invertible={str(q): math.gcd(d, q) == 1 for q in (10, 25, 26, 29)}))
    borders = []
    for name, m in MATRICES.items():
        for fill in (0, 1):
            for r0 in (0, 1):
                for c0 in (0, 1):
                    extended = [[fill]*5 for _ in range(5)]
                    for r in range(4):
                        for c in range(4):
                            extended[r+r0][c+c0] = m[r][c]
                    borders.append(dict(base=name, fill=fill, offset=[r0, c0], determinant=determinant(extended)))
    witnesses = []
    for name, m in MATRICES.items():
        for t in (1, 2):
            extended = [row + [0] for row in m] + [[0, 0, 0, 0, t]]
            witnesses.append(dict(base=name, t=t, matrix=extended, determinant=determinant(extended)))
    lookup = []
    for name, m in [('reported3', PARTIAL), *MATRICES.items()]:
        for reflected, turns, oriented in views(m):
            chosen = [sum(oriented, [])[digit-1] for digit in (3, 4, 7, 8)]
            lookup.append(dict(name=name, reflected=reflected, turns=turns, counts=chosen,
                               distinct=len(set(chosen)), four_distinct_digraphs_possible=len(set(chosen)) == 4))
    return dict(matrices=matrices, hypothetical_5_borders=borders,
                nonuniform_5_witnesses=witnesses, count_only_digraph_lookup=lookup,
                missing_5_counts=dict(if_only_3_known=16, if_4_known=9),
                literal_coordinates={str(n): {'base0_3478_valid': all(int(d) < n for d in '3478'),
                                             'base1_3478_valid': all(1 <= int(d) <= n for d in '3478')}
                                     for n in (3, 4, 5)},
                limits='A 3x3 matrix may contain weight6: weights are not coordinate labels. Unknown borders are not tested as real Hellgate keys. No rejection of multilayer or positional lookup systems.')


def digraphs(books, inventory):
    result = []
    for word in WORDS:
        mapping = dict(zip('3478', [word[i:i+2] for i in range(0, 8, 2)]))
        def render(text):
            return ''.join(mapping.get(c, '??') if c.isdigit() else c for c in text)
        all_digits = ''.join(b['digits'] for b in books)
        numeric_tokens = [(r['id'], w) for r in inventory if r['canonical_candidate']
                          for w in re.findall(r'\d+', r['text'])]
        resolved = [dict(source=i, token=w, prediction=render(w), fitted_crib_reuse=w == '3478')
                    for i, w in numeric_tokens if all(c in mapping for c in w)]
        result.append(dict(assumed_name=word, mapping=mapping,
                           self_name_prediction=render('486486'), avar4378_prediction=render('4378'),
                           known_digit_coverage=sum(c in mapping for c in all_digits)/len(all_digits),
                           resolved_npc_tokens=resolved,
                           npc_predictions=[dict(id=r['id'], output=render(r['text'])) for r in inventory if r['canonical_candidate']],
                           interpretation='3478 expansion is fitted by construction. Unknown digits remain??; short words and copies of3478 are not independent validation. Entity-reference1 does not supply a digraph.'))
    return result


def randomized(values, kind, rng):
    if kind == 'global_bijective_digit_relabel_of_two_digit_codes':
        labels = list(range(10)); rng.shuffle(labels)
        mapping = [10*labels[x//10]+labels[x % 10] for x in range(100)]
        return [[mapping[x] for x in arr] for arr in values]
    out = []
    for arr in values:
        if kind == 'within_book_value_shuffle':
            row = list(arr); rng.shuffle(row)
        else:
            blocks = [arr[i:i+60] for i in range(0, len(arr), 60)]
            rng.shuffle(blocks)
            row = [x for block in blocks for x in block]
        out.append(row)
    return out


def external_predictions(c, inventory, kharos):
    def predict(text, words):
        chunks = re.findall(r'\d+', text) if words else [''.join(re.findall(r'\d', text))]
        values = [numeric_pairs(chunk) for chunk in chunks]
        out = decode(values, c)
        return dict(output=' | '.join(out), uninterpreted=[dict(odd_raw_digit=chunk[-1:] if len(chunk) % 2 else '',
                                                               incomplete_codes=arr[len(arr)//c['n']*c['n']:])
                                                          for chunk, arr in zip(chunks, values)])
    return dict(kharos=predict(kharos['digits'], False),
                npcs=[dict(id=r['id'], whole=predict(r['text'], False), by_word=predict(r['text'], True))
                      for r in inventory if r['canonical_candidate']],
                scope='Unfitted external literal predictions on fixed-pair representation only; raw parser unproved; no semantic gloss. Word framing can discard most short tokens, explicitly counted.')


def freeze():
    bank = catalog()
    dump('data/round15_candidate_catalog.json', dict(keys=key_records(), candidates=bank))
    files = ['data/round15_protocol.json', 'data/round15_candidate_catalog.json',
             'scripts/dimension_name_experiments.py', 'scripts/matrix_experiments.py',
             'scripts/historical_matrix_checks.py', 'scripts/hill29_experiments.py',
             'data/normalized_books.json', 'data/normalized_splits.json', 'data/source_validation_inventory.json',
             'data/external_book_round10.json', 'data/english_reference/alice.txt',
             'data/word_validator_reference/wizard_oz.txt', 'data/word_validator_reference/peter_pan.txt',
             'data/history_round14_sources.json']
    dump('data/round15_evidence_manifest.json', dict(sha256={p: sha(p) for p in files},
                                                   stage='Protocol and implementation frozen before game scoring'))
    print(json.dumps(dict(candidates=len(bank), cells=dict(collections.Counter(f"{c['n']}x{c['n']}_mod{c['q']}" for c in bank)))), flush=True)


def run():
    started = time.monotonic()
    manifest = json.loads((ROOT / 'data/round15_evidence_manifest.json').read_text())
    for path, expected in manifest['sha256'].items():
        if sha(path) != expected:
            raise ValueError('frozen artifact changed: ' + path)
    protocol = json.loads((ROOT / 'data/round15_protocol.json').read_text())
    bank = json.loads((ROOT / 'data/round15_candidate_catalog.json').read_text())['candidates']
    if bank != catalog():
        raise ValueError('catalog regeneration differs')
    models = {q: language_model(q) for q in sorted({c['q'] for c in bank})}
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    split = json.loads((ROOT / 'data/normalized_splits.json').read_text())
    discovery = [i for i, b in enumerate(books) if b['id'] in split['discovery_book_ids']]
    held = [i for i, b in enumerate(books) if b['id'] in split['holdout_book_ids']]
    inventory = json.loads((ROOT / 'data/source_validation_inventory.json').read_text())
    kharos = json.loads((ROOT / 'data/external_book_round10.json').read_text())
    qualification = qualifications(bank, models, protocol)
    dump('results/round15_qualification.json', qualification)
    print('qualification ' + json.dumps(qualification['summary']), flush=True)
    outputs = []
    for layer in protocol['input_layers']:
        values = [numeric_pairs(b['digits']) if layer == 'raw_fixed_pairs_offset0' else [int(c) for c in b['codes']] for b in books]
        for q, model in models.items():
            qbank = [c for c in bank if c['q'] == q]
            winner, score = search([values[i] for i in discovery], qbank, model)
            held_score = fixed_score([values[i] for i in held], winner, model)
            out = decode(values, winner)
            row = dict(layer=layer, q=q, candidate_count=len(qbank), winner_id=winner['id'],
                       train_score=score, exposed_holdout_score=held_score,
                       books=[dict(id=b['id'], output=text, decoded_characters=len(text),
                                   uninterpreted_codes=arr[len(arr)//winner['n']*winner['n']:],
                                   odd_raw_digit=(b['digits'][-1:] if len(b['digits']) % 2 else '') if layer == 'raw_fixed_pairs_offset0' else None)
                              for b, arr, text in zip(books, values, out)], nulls=[])
            if layer == 'raw_fixed_pairs_offset0':
                row['external_unfitted'] = external_predictions(winner, inventory, kharos)
            else:
                row['external_unfitted'] = {'status': 'not_applicable_imported_parser_undefined_on_external_samples'}
            for kind in protocol['nulls']['families']:
                rng = random.Random(SEED + protocol['nulls']['families'].index(kind))
                null_rows = []
                for trial in range(protocol['nulls']['replicates_each']):
                    null = randomized(values, kind, rng)
                    selected, maximum = search([null[i] for i in discovery], qbank, model)
                    null_rows.append(dict(trial=trial, selected_id=selected['id'], train_max=maximum,
                                          exposed_holdout_score=fixed_score([null[i] for i in held], selected, model)))
                p = (1+sum(r['train_max'] >= score for r in null_rows))/(1+len(null_rows))
                row['nulls'].append(dict(kind=kind, replicates=len(null_rows), results=null_rows,
                                        train_familywise_empirical_p=p,
                                        four_branch_bonferroni_p=min(1., 4*p)))
            outputs.append(row)
            dump('results/round15_matrix_search.json', dict(branches=outputs, complete=False))
            print(json.dumps(dict(layer=layer, q=q, winner=winner['id'], train_score=score,
                                  p=[r['train_familywise_empirical_p'] for r in row['nulls']])), flush=True)
    dump('results/round15_matrix_search.json', dict(branches=outputs, complete=True,
         interpretation='No significance or English score establishes meaning. Qualification status applies per dimension/modulus. Exposed 68+2 split is not blind or independent; no generic Hill exclusion. No omitted-zero inference.'))
    dump('results/round15_dimension_analysis.json', dict(algebra=algebra(), digraphs=digraphs(books, inventory)))
    dump('results/round15_execution.json', dict(duration_seconds=round(time.monotonic()-started, 3),
         catalog_candidates=len(bank), positive_controls=len(qualification['cases']),
         null_fits=len(outputs)*3*protocol['nulls']['replicates_each'],
         frozen_manifest_sha256=sha('data/round15_evidence_manifest.json')))
    print('complete', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    elif args.run:
        run()
    else:
        parser.error('use --freeze or --run')
