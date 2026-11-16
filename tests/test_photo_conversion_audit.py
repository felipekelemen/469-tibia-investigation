import collections
import itertools
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from photo_conversion_audit import (CodeLines, calibrated_models, evaluate,
    mask_match, numeric_rows, projection, randomized_rows)


class PhotoConversionTests(unittest.TestCase):
    def test_all_column_orders_recover_numeric_validation_without_using_ys(self):
        anchor = {'x': 737, 'y': 469}
        for order in itertools.permutations(range(3)):
            values = [[469, 42, 737], [400, 11, 652], [407, 12, 653]]
            rows = [[i+1, *(row[j] for j in order)] for i, row in enumerate(values)]
            expected = (order.index(2)+1, order.index(0)+1)
            self.assertEqual(calibrated_models(rows, anchor), [expected])
            tests = [{'x_mask': '652', 'y_mask': '400'}, {'x_mask': '653', 'y_mask': '407'}]
            self.assertTrue(all(r['unique_correct'] for r in evaluate(projection(rows, *expected), tests)))

    def test_duplicate_sources_remain_ambiguous_even_with_a_matching_label(self):
        rows = [[1, 400, 0, 652], [2, 401, 1, 652]]
        out = evaluate(projection(rows, 3, 1), [{'x_mask': '652', 'y_mask': '400'}])[0]
        self.assertEqual(out['predicted_values'], [400, 401])
        self.assertFalse(out['unique_correct'])

    def test_numeric_source_parser_rejects_code_and_wrong_arity(self):
        self.assertEqual(numeric_rows('\ufeff1 0 100\r\n\r\n10\t0\t102'), [[1, 1, 0, 100], [3, 10, 0, 102]])
        for raw in ('', '1 2', '1 2 3 4', '-1 2 3', 'eval(1) 2 3'):
            with self.assertRaises(ValueError):
                numeric_rows(raw)

    def test_html_code_lines_preserve_data_not_ui_line_numbers(self):
        p = CodeLines()
        p.feed('<ol><li><div class="de1">1&nbsp;0 <span>100</span></div></li>'
               '<li><div class="de1">10 0 102</div></li></ol><div>999</div>')
        self.assertEqual(numeric_rows('\n'.join(p.lines)), [[1, 1, 0, 100], [2, 10, 0, 102]])

    def test_controls_preserve_calibration_domain_and_target_histogram(self):
        rows = [[i+1, 200+i, i % 2, 600+i] for i in range(20)]+[[21, 469, 9, 737]]
        for cyclic in (False, True):
            out = randomized_rows(rows, (3, 1), {'x': 737, 'y': 469}, random.Random(19), cyclic)
            self.assertEqual(out[-1], rows[-1])
            self.assertEqual([r[3] for r in out], [r[3] for r in rows])
            self.assertEqual(collections.Counter(r[1] for r in out), collections.Counter(r[1] for r in rows))
            self.assertNotEqual(out[:-1], rows[:-1])

    def test_unknown_mask_does_not_become_an_observation(self):
        self.assertTrue(mask_match(473, '47?'))
        self.assertFalse(mask_match(4730, '47?'))
        self.assertFalse(mask_match(489, '47?'))


if __name__ == '__main__':
    unittest.main()
