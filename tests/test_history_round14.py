import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from historical_matrix_checks import evaluate, partial_matches, polynomial_determinant, views
from history_source_extract import comment, visible_text


class HistoricalMatrixTests(unittest.TestCase):
    def test_symbolic_method_retains_nonconstant_terms(self):
        polynomial = polynomial_determinant([['x', 1], [1, 'y']])
        self.assertEqual(polynomial, {(1, 1): 1, (0, 0): -1})
        self.assertEqual(evaluate(polynomial, 3, 7), 20)

    def test_symbolic_singular_and_triangular_examples(self):
        self.assertEqual(polynomial_determinant([['x', 2], ['x', 2]]), {})
        self.assertEqual(polynomial_determinant([[2, 'x', 1], [0, 3, 'y'], [0, 0, 5]]), {(0, 0): 30})

    def test_all_eight_views_preserve_distinct_numeric_cells(self):
        matrix = [[4 * r + c for c in range(4)] for r in range(4)]
        oriented = [m for _, _, m in views(matrix)]
        self.assertEqual(len({tuple(map(tuple, m)) for m in oriented}), 8)
        self.assertTrue(all(sorted(sum(m, [])) == list(range(16)) for m in oriented))

    def test_partial_match_finds_a_rotated_noncorner_window(self):
        matrix = [[4 * r + c for c in range(4)] for r in range(4)]
        pattern = [[5, 6, 7], [9, 10, 11]]
        for _, _, transformed in views(matrix):
            self.assertTrue(partial_matches(transformed, pattern))

    def test_a_central_contradiction_cannot_be_removed_by_cropping(self):
        matrix = [[1] * 4 for _ in range(4)]
        matrix[1][1] = 2
        self.assertEqual(partial_matches(matrix, [[1] * 3 for _ in range(3)]), [])


class SourceExtractionTests(unittest.TestCase):
    def test_publication_metadata_is_never_a_capture_date(self):
        data = {'@type': 'DiscussionForumPosting', 'comment': [
            {'@type': 'Comment', 'datePublished': '2010-04-10T15:24:23+0200',
             'author': {'name': 'a'}, 'text': 'matrix &gt; 1'}]}
        source = '<script type="application/ld+json">' + json.dumps(data) + '</script><p>visible</p>'
        result = comment(source, 'matrix >', author='a')
        self.assertEqual(result['publication_timestamp_reported'], '2010-04-10T15:24:23+0200')
        self.assertIsNone(result['game_capture_timestamp'])
        self.assertIsNone(result['historical_body_archive_timestamp'])
        self.assertNotIn('matrix', visible_text(source))

    def test_ambiguous_or_missing_comment_is_not_silently_selected(self):
        rows = [{'@type': 'Comment', 'datePublished': '2010-04-10', 'text': 'matrix'}] * 2
        source = '<script type="application/ld+json">' + json.dumps(rows) + '</script>'
        with self.assertRaises(ValueError):
            comment(source, 'matrix')
        with self.assertRaises(ValueError):
            comment(source, 'absent')


if __name__ == '__main__':
    unittest.main()
