from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from source_copy_seams import find_splits, inherited, occurrences, witnesses


class SourceCopySeamTests(unittest.TestCase):
    def test_recover_split_without_being_given_its_position(self):
        books = [{'id': 'a', 'digits': '123456'}, {'id': 'b', 'digits': '789012'}]
        rows = find_splits('345789', books, True)
        self.assertEqual([r['cut'] for r in rows], [3])
        self.assertEqual(rows[0]['address_combinations'], 1)

    def test_complete_copy_has_many_splits_not_a_unique_word_boundary(self):
        books = [{'id': 'a', 'digits': '123456'}]
        self.assertEqual([r['cut'] for r in find_splits('123456', books)], list(range(1, 6)))

    def test_repeated_sources_multiply_addresses_not_cut_positions(self):
        books = [{'id': str(i), 'digits': raw} for i, raw in enumerate(['123456', '123456', '789012', '789012'])]
        rows = find_splits('345789', books, True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['address_combinations'], 4)

    def test_source_book_ends_never_create_a_full_match(self):
        books = [{'id': 'a', 'digits': '1234'}, {'id': 'b', 'digits': '5678'}]
        self.assertFalse(witnesses(books, '3456'))
        self.assertEqual([r['cut'] for r in find_splits('12345678', books)], [4])
        self.assertEqual(list(occurrences('000', '00')), [0, 1])

    def test_boundaries_from_different_zero_alignments_cannot_be_mixed(self):
        books = [{'id': 'a', 'codes': ['00', '00'], 'digits': '000'}]
        self.assertFalse(inherited(books, [{'book_id': 'a', 'start': 1, 'end': 2}])['compatible_witnesses'])
        result = inherited(books, [{'book_id': 'a', 'start': 0, 'end': 1}])
        self.assertEqual(len(result['compatible_witnesses']), 1)
        self.assertEqual(result['distinct_numeric_code_sequences'], [['00']])


if __name__ == '__main__':
    unittest.main()
