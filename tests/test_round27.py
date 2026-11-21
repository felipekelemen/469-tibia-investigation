import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from unit_morphism_lexicon import Bank
from round27_witness_solver import Fit, Model, emit, word_paths
from round27_fixtures import encode_random
import random


def bank(forms, maximum=2):
    b = Bank('grapheme1_3', {f: {f} for f in forms}, {})
    b.maximum = maximum
    return b


BUDGET = {'states_per_query': 2000, 'states_total_per_fit_and_transfers': 20000,
          'local_assignments_per_state': 20000}


class WitnessTests(unittest.TestCase):
    def test_exhaustive_query_matches_brute_force(self):
        units = ['A', 'B', 'AA', 'AB', 'BA', 'BB']
        for vocabulary in [('AA', 'BB'), ('ABA', 'AABB', 'BBAA'), ('AB', 'BA', 'ABAB')]:
            b = bank(vocabulary)
            for words in [('01',), ('010',), ('00', '11'), ('01', '10')]:
                model = Model(words, b)
                all_keys = [dict(zip(sorted(model.digits), us))
                            for us in itertools.product(units, repeat=len(model.digits))]
                valid = [k for k in all_keys if all(emit(w, k) in b.reverse for w in words)]
                seen = []
                def visit_keys(key):
                    # Individual exclusions check SAT and UNSAT, including no solutions.
                    out = model.find(different_key=key)
                    expected = [k for k in valid if any(k[d] != u for d, u in key.items())]
                    self.assertEqual(out['status'], 'SAT' if expected else 'UNSAT')
                    if expected:
                        self.assertIn(out['key'], expected)
                for key in all_keys:
                    visit_keys(key)
                for form in ('AA', 'ABA', 'ABAB'):
                    out = model.find(different_form=(words[0], form))
                    expected = [k for k in valid if emit(words[0], k) != form]
                    self.assertEqual(out['status'], 'SAT' if expected else 'UNSAT')

    def test_budget_is_unknown(self):
        self.assertEqual(Model(['01'], bank(['AB'])).find(max_states=0)['status'], 'UNKNOWN')
        fit = Fit(['01'], bank(['AB', 'BA']), dict(BUDGET, states_per_query=0))
        self.assertFalse(fit.predict('01')['form_certified'])

    def test_form_consensus_does_not_imply_chunk_consensus(self):
        fit = Fit(['01'], bank(['ABC']), BUDGET)
        prediction = fit.predict('01')
        self.assertFalse(fit.unique)
        self.assertTrue(prediction['form_certified'])
        self.assertFalse(prediction['chunks_certified'])
        self.assertEqual(prediction['form'], 'ABC')

    def test_transfer_outside_lexicon_is_allowed(self):
        fit = Fit(['0', '1', '01'], bank(['A', 'B', 'AB'], 1), BUDGET)
        self.assertTrue(fit.unique)
        result = fit.predict('010')
        self.assertTrue(result['form_certified'])
        self.assertEqual(result['form'], 'ABA')

    def test_missing_digit_and_invalid_queries(self):
        fit = Fit(['0'], bank(['A'], 1), BUDGET)
        self.assertEqual(fit.predict('01')['status'], 'unknown_digits')
        with self.assertRaises(ValueError):
            fit.model.find(different_key={'1': 'B'})

    def test_homophonic_digits_are_permitted(self):
        fit = Fit(['0', '1'], bank(['A'], 1), BUDGET)
        self.assertTrue(fit.unique)
        self.assertEqual(fit.key, {'0': 'A', '1': 'A'})

    def test_distinct_compatible_keys_force_abstention(self):
        fit = Fit(['0'], bank(['A', 'B'], 1), BUDGET)
        out = fit.predict('00')
        self.assertEqual(out['status'], 'ambiguous_form')
        self.assertNotEqual(out['form'], out['counterexample_form'])
        self.assertFalse(out['form_certified'])

    def test_word_cuts_cannot_split_a_unit(self):
        b = bank(['A', 'BC', 'ABC'])
        self.assertEqual(word_paths('01', {'0': 'AB', '1': 'C'}, b)['paths'], 1)
        self.assertEqual(word_paths('01', {'0': 'A', '1': 'BC'}, b)['paths'], 2)

    def test_ambiguous_spelling_is_retained(self):
        b = Bank('grapheme1_3', {'AB': {'FIRST', 'SECOND'}}, {})
        self.assertEqual(word_paths('01', {'0': 'A', '1': 'B'}, b)['paths'], 2)

    def test_randomized_encoding_roundtrips_and_can_use_aliases(self):
        key = {'0': 'AB', '1': 'A', '2': 'B', '3': 'AB'}
        rng = random.Random(27)
        raws = [encode_random('ABAB', key, rng) for _ in range(100)]
        self.assertTrue(all(emit(r, key) == 'ABAB' for r in raws))
        self.assertTrue({'0', '3'} <= set(''.join(raws)))


if __name__ == '__main__':
    unittest.main()
