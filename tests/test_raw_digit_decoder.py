import itertools
import math
import pathlib
import random
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from raw_digit_decoder import (CharacterLanguage, UniformLanguage, decode,
                               measures, omission_probability, serialize)
from raw_parser_benchmark import order_control
import numpy as np


def example_key():
    # One unique code per letter, plus a homophone for A and B.
    key = [-1] * 100
    probs = [0.0] * 100
    for letter in range(26):
        key[letter + 10] = letter
        probs[letter + 10] = 1.0
    for code, letter in [(0, 0), (1, 1)]:
        key[code] = letter
        probs[code] = probs[letter + 10] = .5
    return key, probs


class RawDigitDecoderTests(unittest.TestCase):
    def test_forward_and_viterbi_match_exhaustive_path_weights(self):
        key, probs = example_key()
        lm = UniformLanguage()
        for rule in ['iid_0.3', 'previous_mod3']:
            for raw in ['001011', '10110', '001', '']:
                paths = []
                def enumerate_paths(position, previous, score, rows):
                    if position == len(raw):
                        paths.append((score * (1 / 128), rows))
                        return
                    # Enumerate all boundary subsets directly, independent of DP.
                    for width in [1, 2]:
                        if position + width > len(raw):
                            continue
                        code = int(raw[position:position + width])
                        if probs[code] == 0:
                            continue
                        q = omission_probability(rule, previous)
                        action = q if width == 1 else (1 - q if code < 10 else 1)
                        weight = probs[code] * action / 26 * (127 / 128)
                        if weight:
                            enumerate_paths(position + width, code % 3, score * weight,
                                            rows + [(position, position + width, code)])
                enumerate_paths(0, -1, 1.0, [])
                fit = decode(raw, key, probs, lm, rule)
                self.assertEqual(fit['possible'], bool(paths))
                if paths:
                    self.assertAlmostEqual(fit['log_evidence'], math.log(sum(p[0] for p in paths)), places=11)
                    self.assertAlmostEqual(fit['best_log_probability'], math.log(max(p[0] for p in paths)), places=11)
                    self.assertAlmostEqual(fit['map_path_posterior'], max(p[0] for p in paths) / sum(p[0] for p in paths), places=11)

    def test_unambiguous_known_rule_recovers_without_supplied_count(self):
        key, probs = example_key()
        codes = [10, 11, 23, 0, 1, 12]
        raw, path = serialize(codes, 'never', random.Random(7))
        fit = decode(raw, key, probs, UniformLanguage(), 'never')
        self.assertEqual(fit['path'], path)
        self.assertEqual(fit['literal'], 'ABNABC')
        self.assertEqual(measures(fit, path, 'ABNABC')['character_edit_accuracy'], 1)
        for row in fit['path']:
            self.assertEqual(row['end'] - row['start'], 2)

    def test_context_can_remove_paths_and_inputs_are_not_silently_cleaned(self):
        key, probs = example_key()
        self.assertFalse(decode('1', key, probs, UniformLanguage(), 'previous_mod3')['possible'])
        self.assertTrue(decode('1', key, probs, UniformLanguage(), 'always')['possible'])
        with self.assertRaises(ValueError):
            decode('10 11', key, probs, UniformLanguage(), 'never')
        with self.assertRaises(ValueError):
            decode('１０', key, probs, UniformLanguage(), 'never')
        bad = probs[:]
        bad[10] = .9
        with self.assertRaises(ValueError):
            decode('10', key, bad, UniformLanguage(), 'never')

    def test_normalized_markov_rows_and_boundary_metric_ignore_shared_endpoints(self):
        joint = np.arange(1, 26 ** 4 + 1, dtype=float)
        joint /= joint.sum()
        model = CharacterLanguage(np.log10(joint))
        for history in [(), (0,), (0, 1), (0, 1, 2)]:
            self.assertAlmostEqual(sum(math.exp(model.log_probability(history, c)) for c in range(26)), 1)
        truth = [{'start': 0, 'end': 2, 'code': 10, 'omitted': False}]
        actual = {'possible': True, 'path': [{'start': 0, 'end': 1, 'code': 1}, {'start': 1, 'end': 2, 'code': 0}],
                  'literal': 'BA', 'map_path_posterior': .8}
        result = measures(actual, truth, 'A')
        self.assertEqual(result['boundary_f1'], 0)
        self.assertEqual(result['character_edit_accuracy'], .5)

    def test_order_controls_preserve_codes_and_obey_the_declared_zero_rule(self):
        codes = [0, 1, 12, 14, 2, 3, 18, 21, 4, 5, 11, 13, 6, 7, 22, 8, 9]
        for rule in ['never', 'always', 'iid_0.3', 'previous_mod3']:
            raw, path = serialize(codes, rule, random.Random(469))
            for mode in ['shuffle_codes', 'blocks8_codes']:
                craw, cpath, reordered = order_control(codes, path, rule, mode, 1234)
                self.assertCountEqual(reordered, codes)
                pieces = [f"{r['code']:02d}"[1:] if r['omitted'] else f"{r['code']:02d}" for r in cpath]
                self.assertEqual(''.join(pieces), craw)
                if rule != 'previous_mod3':
                    self.assertEqual(len(craw), len(raw))
                    self.assertCountEqual([(r['code'], r['omitted']) for r in cpath],
                                          [(r['code'], r['omitted']) for r in path])
                else:
                    previous = -1
                    for r in cpath:
                        self.assertEqual(r['omitted'], r['code'] < 10 and previous == 1)
                        previous = r['code'] % 3


if __name__ == '__main__':
    unittest.main()
