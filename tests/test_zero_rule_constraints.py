import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from zero_rule_constraints import FAMILIES, alignments, feature, predict, serialize, solve


class ZeroConstraintTests(unittest.TestCase):
    def test_counts_and_action_support_match_exhaustive_omission_vectors(self):
        for codes in itertools.product(['00', '01', '10'], repeat=3):
            zero = [i for i, c in enumerate(codes) if c.startswith('0')]
            by_raw = {}
            for flags in itertools.product([False, True], repeat=len(zero)):
                omitted = tuple(i for i, flag in zip(zero, flags) if flag)
                by_raw.setdefault(serialize(codes, set(omitted)), set()).add(omitted)
            for raw, expected in by_raw.items():
                fit = alignments({'id': 'x', 'codes': codes, 'digits': raw})
                self.assertEqual(fit['count'], len(expected))
                self.assertEqual(set(fit['paths']), expected)
                for event in fit['events']:
                    self.assertEqual(set(event['actions']), {event['index'] in omitted for omitted in expected})

    def test_ambiguous_actions_are_not_independently_assignable(self):
        books = [{'id': 'a', 'codes': ['00', '01'], 'digits': '001'},
                 {'id': 'b', 'codes': ['00', '01'], 'digits': '0001'}]
        aligned = [alignments(b) for b in books]
        self.assertEqual(aligned[0]['count'], 2)
        fit = solve(books, aligned, FAMILIES[0])
        self.assertEqual(fit['status'], 'UNSAT_EXHAUSTIVE')

    def test_ambiguous_positive_retains_a_complete_valid_assignment(self):
        books = [{'id': 'a', 'codes': ['00', '01'], 'digits': '001'}]
        result = solve(books, [alignments(books[0])], FAMILIES[0])
        self.assertEqual(result['status'], 'SAT')
        self.assertTrue(predict(books[0], result['table'], FAMILIES[0])['exact_raw'])

    def test_forced_conflict_is_not_cured_by_copying_samples(self):
        a = {'id': 'a', 'codes': ['11', '07', '22'], 'digits': '110722'}
        b = {'id': 'b', 'codes': ['11', '07', '22'], 'digits': '11722'}
        for spec in FAMILIES:
            books = [a, b] + [dict(a, id=str(i)) for i in range(10)]
            result = solve(books, [alignments(x) for x in books], spec)
            self.assertEqual(result['status'], 'UNSAT_FORCED_CONFLICT')
            self.assertEqual(result['certificate']['preserved']['forced_action'], False)
            self.assertEqual(result['certificate']['omitted']['forced_action'], True)

    def test_caps_are_unresolved_and_book_start_features_do_not_cross_boundaries(self):
        book = {'id': 'a', 'codes': ['00', '01'], 'digits': '001'}
        a = alignments(book, cap=1)
        self.assertEqual(a['count'], 2)
        self.assertEqual(solve([book], [a], FAMILIES[0])['status'], 'UNRESOLVED_ALIGNMENT_CAP')
        left = {'left': 2, 'right': 1, 'period': 16}
        self.assertEqual(feature(['01', '12'], 0, left), ('<s>', '<s>', '01', '12', 'phase=0'))


if __name__ == '__main__':
    unittest.main()
