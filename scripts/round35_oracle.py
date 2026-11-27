#!/usr/bin/env python3
"""Gold-assisted counterexamples to the frozen score; not a decoder."""
import itertools
import json
import math
from pathlib import Path
import time
from unit_morphism_solver import word_extensions

ROOT = Path(__file__).resolve().parents[1]


class LanguageModel:
    def __init__(self, path):
        with path.open() as stream:
            n = int(next(stream))
            self.words, self.counts = [], []
            for _ in range(n):
                w, c = next(stream).split()
                self.words.append(w); self.counts.append(int(c))
            self.ids = {w: i for i, w in enumerate(self.words)}
            self.pairs = {}
            for _ in range(int(next(stream))):
                a, b, c = map(int, next(stream).split()); self.pairs[a, b] = c
        self.total = sum(self.counts[1:]); self.v = len(self.words) - 1

    def score(self, forms):
        prev, total = 0, 0.
        for word in forms:
            i = self.ids[word]
            total += .35 * math.log((self.counts[i] + .1) / (self.total + .1 * self.v))
            total += .65 * math.log((self.pairs.get((prev, i), 0) + .1) / (self.counts[prev] + .1 * self.v))
            prev = i
        return total


def emit(raw, key):
    return ''.join(key[d] for d in raw)


def segmentation_counterexample(case, cap):
    pairs = sorted(set(zip(case['input'], case['expected'])), key=lambda p: (-len(p[0]), p))
    states, witness, limited = 0, None, False

    def visit(i, key):
        nonlocal states, witness, limited
        if witness or limited:
            return
        if states >= cap:
            limited = True; return
        states += 1
        if i == len(pairs):
            if any(emit(raw, key) != truth for raw, truth in zip(case['probes'], case['probe_truth'])):
                witness = dict(key)
            return
        raw, form = pairs[i]
        for extended in word_extensions(raw, form, 1, 3, key):
            visit(i + 1, extended)
            if witness or limited:
                break
    visit(0, {})
    return {'states': states, 'status': 'witness' if witness else 'limit' if limited else 'complete_no_counterexample', 'key': witness}


def run():
    protocol = json.loads((ROOT / 'data/round35_oracle_protocol.json').read_text())
    cases = [c for c in json.loads((ROOT / 'data/round35_fixtures.json').read_text())['cases'] if c['scenario'] == 'natural7']
    model = LanguageModel(ROOT / 'data/round35_reference/language_model.txt')
    units = [''.join(chars) for n in (1, 2, 3) for chars in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=n)]
    results = []
    start = time.process_time()
    for case in cases:
        true_score = model.score(case['expected'])
        same = segmentation_counterexample(case, protocol['limits']['segmentation_states_per_case'])
        different, tried = None, 0
        for digit in sorted(case['key']):
            affected = [i for i, raw in enumerate(case['input']) if digit in raw]
            for unit in units:
                if unit == case['key'][digit]:
                    continue
                tried += 1
                key = dict(case['key']); key[digit] = unit
                forms = list(case['expected'])
                for i in affected:
                    forms[i] = emit(case['input'][i], key)
                    if forms[i] not in model.ids:
                        break
                else:
                    score = model.score(forms)
                    if score >= true_score and any(emit(raw, key) != truth for raw, truth in zip(case['probes'], case['probe_truth'])):
                        different = {'key': key, 'forms': forms, 'score': score}
                        break
            if different:
                break
        witnesses = []
        for kind, candidate in [('same_plaintext', same['key']), ('single_digit_replacement', different['key'] if different else None)]:
            if candidate is None:
                continue
            forms = [emit(raw, candidate) for raw in case['input']]
            assert all(w in model.ids for w in forms)
            assert all(1 <= len(u) <= 3 for u in candidate.values())
            score = model.score(forms)
            assert score >= true_score
            probe_index = next(i for i, (raw, truth) in enumerate(zip(case['probes'], case['probe_truth'])) if emit(raw, candidate) != truth)
            witnesses.append({'kind': kind, 'key': candidate, 'training_output': forms, 'score': score,
                              'probe_index': probe_index, 'probe_output': emit(case['probes'][probe_index], candidate),
                              'probe_truth': case['probe_truth'][probe_index]})
        results.append({'id': case['id'], 'true_score': true_score,
                        'true_mean_score': true_score / 7,
                        'true_below_acceptance_threshold': true_score / 7 < -10,
                        'same_plaintext_search_status': same['status'],
                        'same_plaintext_states': same['states'],
                        'single_digit_keys_visited': tried,
                        'single_digit_neighborhood_exhausted': different is None,
                        'witnesses': witnesses})
    summary = {'cases': len(results),
               'true_below_acceptance_threshold': sum(r['true_below_acceptance_threshold'] for r in results),
               'same_plaintext_transfer_counterexamples': sum(any(w['kind'] == 'same_plaintext' for w in r['witnesses']) for r in results),
               'single_digit_equal_or_better_score_counterexamples': sum(any(w['kind'] == 'single_digit_replacement' for w in r['witnesses']) for r in results),
               'either_counterexample': sum(bool(r['witnesses']) for r in results),
               'threshold_or_counterexample_obstruction': sum(r['true_below_acceptance_threshold'] or bool(r['witnesses']) for r in results),
               'segmentation_limits': sum(r['same_plaintext_search_status'] == 'limit' for r in results),
               'cpu_seconds': time.process_time() - start}
    output = {'round': 35, 'diagnostic': 'gold_assisted_not_blind_recovery', 'summary': summary, 'cases': results,
              'scope': 'Verified finite witnesses against the unchanged score/model; absence of a witness is not global identifiability. No game ciphertext was fitted.'}
    (ROOT / 'results/round35_oracle.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    run()
