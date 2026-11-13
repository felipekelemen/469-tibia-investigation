import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hidden_unit_segmenter import (fit_bpe, fit_periodic, fit_unigram, fixed_tokens,
                                  merge_pair, segment, viterbi)
from hidden_unit_benchmark import adversarial_certificate, metrics


class HiddenUnitTests(unittest.TestCase):
    def test_bpe_never_learns_pairs_across_message_boundaries(self):
        model = fit_bpe(['12']*20+['34']*20, 32)
        self.assertNotIn('23', model['units'])
        self.assertNotIn(['2', '3'], model['rules'])
        self.assertEqual(segment('1234', model), ['12', '34'])

    def test_overlapping_bpe_pair_merge_does_not_drop_digits(self):
        self.assertEqual(merge_pair(list('111'), ('1', '1')), ['11', '1'])
        self.assertEqual(merge_pair(list('11111'), ('1', '1')), ['11', '11', '1'])

    def test_periodic_parser_preserves_incomplete_tail(self):
        self.assertEqual(fixed_tokens('12345', 2), ['12', '34', '5'])
        model = fit_periodic(['123456789']*7+['12789']*4)
        self.assertEqual(''.join(segment('1234567', model)), '1234567')

    def test_viterbi_agrees_with_exhaustive_segmentations(self):
        costs = {'0': 2.3, '1': 2.8, '01': 1.4, '10': 2.0, '001': 1.9}
        def brute(raw):
            if not raw:
                return 0.
            return min(cost+brute(raw[len(word):]) for word, cost in costs.items() if raw.startswith(word))
        for length in range(7):
            for seq in itertools.product('01', repeat=length):
                raw = ''.join(seq)
                path, score = viterbi(raw, costs)
                self.assertEqual(''.join(path), raw)
                self.assertAlmostEqual(score, brute(raw), places=11)

    def test_unigram_reconstructs_novel_digit_combinations(self):
        train = ['123456123456']*5+['561234123456']*4
        bpe = fit_bpe(train, 32)
        model = fit_unigram(train, bpe)
        path = segment('651234561', model)
        self.assertEqual(''.join(path), '651234561')
        self.assertTrue(all(w in model['units'] for w in path))

    def test_metric_excludes_message_ends_and_keeps_document_identity(self):
        target = [{'raw': '1234', 'true_units': ['12', '34']}]*2
        model = {'units': ['12', '34', '1234']}
        wrong = metrics(target[:1], [['1234']], model)
        self.assertEqual(wrong['boundary']['f1'], 0.)
        self.assertEqual(wrong['unit_span']['f1'], 0.)
        half = metrics(target, [['12', '34'], ['1234']], model)
        self.assertEqual(half['boundary']['correct'], 1)
        self.assertEqual(half['boundary']['true'], 2)
        self.assertAlmostEqual(half['boundary']['f1'], 2/3)

    def test_unique_parse_given_key_does_not_identify_hidden_key(self):
        c = adversarial_certificate()
        self.assertTrue(c['A_unique_decodability']['prefix_free'])
        self.assertTrue(c['B_unique_decodability']['prefix_free'])
        for row in c['training']:
            self.assertEqual(row['A']['count'], 1)
            self.assertEqual(row['B']['count'], 1)
        self.assertEqual(c['new_combination']['A']['count'], 1)
        self.assertEqual(c['new_combination']['B']['count'], 0)
        row = c['same_raw_different_boundaries']
        self.assertNotEqual(row['A']['unique_path'], row['B']['unique_path'])


if __name__ == '__main__':
    unittest.main()
