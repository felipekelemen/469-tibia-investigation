import itertools
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from round37_experiment import pair_decode, variants
from unit_morphism_solver import word_extensions


class ClaimMechanics(unittest.TestCase):
    def test_padding_preserves_leading_zero_and_punctuation_boundaries(self):
        self.assertEqual(pair_decode('0 01, 123! 00', {'00':'*','01':'A','23':'B'}),
                         (['00','01','0123','00'], ['*','A','AB','*']))
        with self.assertRaises(KeyError):
            pair_decode('99', {'00':'*'})

    def test_ordered_and_permuted_rules_are_distinct(self):
        table = {'V':['V','OOL'], 'F':['F']}
        self.assertEqual(set(variants('VF', table)), {'VF','OOLF'})
        relaxed = variants('VF', table, True)
        self.assertEqual(set(relaxed), {'VF','OOLF','FV','FOOL'})
        self.assertEqual(relaxed['FOOL'], {'base_order':'FV','units':['F','OOL']})

    def test_counts_are_distinct_strings_and_wildcard_is_explicit(self):
        self.assertEqual(len(variants('VV', {'V':['A','AA']}, True)), 3)
        self.assertEqual(set(variants('*A', {'*':['A','B'],'A':['A']})), {'AA','BA'})
        with self.assertRaises(KeyError):
            variants('*', {})

    def test_partitions_against_independent_whole_keys(self):
        # Positive and negative artificial cases; repeated digits cannot vary.
        domains = ['A','B','AA','AB','BA','BB']
        for raw in ['01','010','001']:
            for word in ['ABA','AAAA','BAB','AB','BBA']:
                expected = set()
                for a,b in itertools.product(domains, repeat=2):
                    key = {'0':a,'1':b}
                    if ''.join(key[d] for d in raw) == word:
                        expected.add(tuple(sorted(key.items())))
                actual = {tuple(sorted(k.items())) for k in word_extensions(raw, word, 1, 2)}
                self.assertEqual(actual, expected)
        self.assertIn({'0':'A','1':'B'}, list(word_extensions('010','ABA',1,2)))
        self.assertEqual(list(word_extensions('90871','WIT',1,3)), [])


if __name__ == '__main__':
    unittest.main()
