import collections
import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from conserved_code_parser import solve, solve_source, source_inventories
from omission_set_reference import enumerate_parses


class ConservedParserTests(unittest.TestCase):
    def test_known_reordering_is_recovered(self):
        source = {'id': 'x', 'digits': '123456', 'codes': ['12', '34', '56']}
        for mode in ('wire_multiset', 'code_multiset'):
            r = solve_source('561234', source, mode)
            self.assertEqual(r['unique_codes'], [56, 12, 34])

    def test_same_digit_histogram_does_not_imply_code_reordering(self):
        source = {'id': 'x', 'digits': '123456', 'codes': ['12', '34', '56']}
        self.assertEqual(collections.Counter(source['digits']), collections.Counter('132456'))
        self.assertEqual(solve_source('132456', source, 'code_multiset')['status'], 'UNSAT')

    def test_changed_zero_actions_distinguish_the_hypotheses(self):
        source = {'id': 'x', 'digits': '102', 'codes': ['01', '02']}
        self.assertEqual(solve_source('012', source, 'wire_multiset')['status'], 'UNSAT')
        self.assertEqual(solve_source('012', source, 'code_multiset')['unique_codes'], [1, 2])

    def test_counts_are_paths_and_not_necessarily_distinct_streams(self):
        inventory = ((0, 2, ('00', '0')),)
        result = solve('000', inventory)
        self.assertEqual(result['path_count'], '2')
        self.assertEqual(result['unique_codes'], [0, 0])

    def test_caps_never_claim_failure_or_uniqueness(self):
        inventory = ((0, 1, ('00', '0')), (1, 1, ('01', '1')))
        result = solve('001', inventory, state_cap=1)
        self.assertEqual(result['status'], 'UNRESOLVED_STATE_CAP')
        self.assertIsNone(result['unique_codes'])
        # Two distinct streams: 1|11 and 11|1 with the same multiset.
        result = solve('111', ((1, 1, ('01', '1')), (11, 1, ('11',))), stream_cap=1)
        self.assertEqual(result['status'], 'SAT')
        self.assertFalse(result['streams_complete'])
        self.assertIsNone(result['unique_codes'])

    def test_all_compatible_source_inventory_forms_are_retained(self):
        source = {'id': 'x', 'digits': '001', 'codes': ['00', '01']}
        self.assertEqual(len(source_inventories(source, 'wire_multiset')), 2)
        self.assertEqual(solve_source('001', source, 'wire_multiset')['status'], 'SAT')

    def test_dp_agrees_with_exhaustive_token_permutations(self):
        inventory = ((1, 1, ('01', '1')), (0, 2, ('00', '0')))
        # Independent brute force enumerates indexed copies, then deduplicates
        # identical (code,form) paths to avoid counting repeated inventory items.
        expected = collections.defaultdict(set)
        for order in set(itertools.permutations((1, 0, 0))):
            for forms in itertools.product(*(('01', '1') if c else ('00', '0') for c in order)):
                expected[''.join(forms)].add(tuple(zip(order, forms)))
        for n in range(1, 7):
            for chars in itertools.product('01', repeat=n):
                raw = ''.join(chars)
                result = solve(raw, inventory)
                self.assertEqual(int(result['path_count']), len(expected[raw]))
                self.assertEqual({tuple(s) for s in result['streams']}, {tuple(c for c, _ in path) for path in expected[raw]})

    def test_independent_reference_finds_true_ambiguous_parses(self):
        source = {'id': 'x', 'codes': ['01', '11']}
        result = enumerate_parses('111', source)
        self.assertTrue(result['complete'])
        self.assertEqual(result['patterns'], 2)
        self.assertEqual({tuple(r['codes']) for r in result['solutions']}, {(1, 11), (11, 1)})
        self.assertEqual(enumerate_parses('222', source)['solutions'], [])

    def test_independent_reference_reports_budget_and_length(self):
        source = {'id': 'x', 'codes': ['01', '11']}
        self.assertFalse(enumerate_parses('111', source, maximum_patterns=1)['complete'])
        self.assertEqual(enumerate_parses('12345', source)['solutions'], [])


if __name__ == '__main__':
    unittest.main()
