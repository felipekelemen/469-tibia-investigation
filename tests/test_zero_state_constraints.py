import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from book_metadata_audit import parse_listing
from zero_rule_constraints import alignments
from zero_state_constraints import FAMILIES, emit, path_rows, solve, state_key


class ZeroStateTests(unittest.TestCase):
    def test_raw_position_state_keeps_distinct_alignment_features(self):
        book = {'id': 'a', 'codes': ['00', '01'], 'digits': '001'}
        a = alignments(book)
        spec = next(s for s in FAMILIES if s['name'] == 'code_n_raw16')
        sequences = [path_rows(book, path, spec) for path in a['paths']]
        self.assertEqual(a['count'], 2)
        self.assertNotEqual(sequences[0][1]['feature'], sequences[1][1]['feature'])
        self.assertEqual(sequences[0][0]['feature'], sequences[1][0]['feature'])

    def test_existence_matches_independent_boolean_assignment_enumeration(self):
        books = [{'id': 'a', 'codes': ['00', '01'], 'digits': '001'},
                 {'id': 'b', 'codes': ['00', '01'], 'digits': '0001'}]
        aa = [alignments(b) for b in books]
        for name in ['code_token_length_mod2', 'code_n_raw16', 'code_raw_length_mod4']:
            spec = next(s for s in FAMILIES if s['name'] == name)
            options = [[path_rows(b, path, spec) for path in a['paths']] for b, a in zip(books, aa)]
            keys = sorted({row['feature'] for opts in options for rows in opts for row in rows})
            reference = False
            for flags in itertools.product([False, True], repeat=len(keys)):
                assignment = dict(zip(keys, flags))
                if all(any(all(assignment[row['feature']] == row['omit'] for row in rows) for rows in opts)
                       for opts in options):
                    reference = True
                    break
            fitted = solve(books, aa, spec)
            self.assertEqual(fitted['status'] == 'SAT', reference)
            if reference:
                table = {tuple(x['feature']): x['omit'] for x in fitted['table']}
                self.assertTrue(all(emit(b, spec, table, None)['exact_raw'] for b in books))

    def test_state_uses_only_the_declared_prefix_before_the_current_action(self):
        book = {'id': 'x', 'codes': ['11', '07', '22'], 'digits': '11722'}
        spec = next(s for s in FAMILIES if s['name'] == 'code_n_sum16')
        rows = path_rows(book, [1], spec)
        self.assertEqual(rows[0]['feature'], ('07', 'state=14'))  #3+11before07
        self.assertEqual(rows[0]['raw_start'], 2)
        self.assertEqual(state_key(book, 1, 2, 11, 11, spec), rows[0]['feature'])

    def test_listing_parser_keeps_copy_occurrences_and_continuation_digits(self):
        text = 'First Bookcase\n#1 123 (Book) 0123\n 456\n\nSecond Bookcase\n#2 1234 (Book) 0123456\n'
        rows = parse_listing(text)
        self.assertEqual(len(rows), 2)
        self.assertEqual([r['digits'] for r in rows], ['0123456', '0123456'])
        self.assertEqual([r['shelf_ordinal'] for r in rows], [1, 2])
        self.assertEqual([r['label'] for r in rows], ['123', '1234'])


if __name__ == '__main__':
    unittest.main()
