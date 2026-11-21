"""Equivalence of execution cache to frozen reference, including budget results."""
import itertools
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from unit_morphism_lexicon import Bank
from round27_witness_solver import Model, Fit
from round27_cached_model import cached_find


class CacheEquivalence(unittest.TestCase):
    def test_mixed_queries_and_limits_match_reference(self):
        for forms in [('AB', 'BA', 'ABA', 'AABB', 'BBAA'), ('A', 'AA', 'AAA'),
                      ('A', 'B', 'AB', 'BA', 'ABAB')]:
            bank = Bank('grapheme1_3', {f: {f} for f in forms}, {})
            bank.maximum = 2
            for words in [('01',), ('010',), ('00', '11'), ('01', '10')]:
                ordinary, cached = Model(words, bank), Model(words, bank)
                queries = [{}, {'different_key': {'0': 'A'}},
                           {'different_key': {'0': 'A', '1': 'AB'}}]
                queries += [{'different_form': (words[0], f)} for f in forms]
                for states, local_cap in itertools.product((0, 1, 5, 2000), (0, 1, 20000)):
                    for query in queries:
                        kwargs = dict(query, max_states=states, local_cap=local_cap)
                        self.assertEqual(ordinary.find(**kwargs), cached_find(cached, **kwargs))

    def test_fit_transfer_contract_is_unchanged(self):
        bank = Bank('grapheme1_3', {f: {f} for f in ('ABC', 'A', 'BC', 'B', 'AC')}, {})
        budgets = {'states_per_query': 2000, 'states_total_per_fit_and_transfers': 20000,
                   'local_assignments_per_state': 20000}
        ordinary = Fit(['01'], bank, budgets)
        predictions = [ordinary.predict(raw) for raw in ('01', '10', '010', '012')]
        with patch.object(Model, 'find', cached_find):
            cached = Fit(['01'], bank, budgets)
            actual = [cached.predict(raw) for raw in ('01', '10', '010', '012')]
        self.assertEqual(predictions, actual)
        self.assertEqual(ordinary.queries, cached.queries)
        self.assertEqual(ordinary.used, cached.used)


if __name__ == '__main__':
    unittest.main()
