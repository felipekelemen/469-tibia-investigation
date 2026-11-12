import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from raw_copy_parser import build_dictionary, parse, raw_novelty


class RawCopyTests(unittest.TestCase):
    def test_new_arrangement_recovers_codes_without_target_boundaries(self):
        sources = [{'id': 'a', 'codes': ['12', '34', '56'], 'digits': '123456'},
                   {'id': 'b', 'codes': ['78', '90', '11'], 'digits': '789011'}]
        dictionary = build_dictionary(sources, minimum=4)
        result = parse('1234789011', dictionary, minimum=4)
        self.assertEqual(result['unique_full_codes'], [12, 34, 78, 90, 11])
        self.assertEqual(result['uncovered_raw_digits'], 0)
        self.assertEqual(result['copied_pieces'], 2)
        self.assertEqual(''.join(x['raw'] for x in result['representative_path']), '1234789011')

    def test_dictionary_never_invents_source_cross_book_fragments(self):
        sources = [{'id': 'a', 'codes': ['12', '34'], 'digits': '1234'},
                   {'id': 'b', 'codes': ['56', '78'], 'digits': '5678'}]
        dictionary = build_dictionary(sources, minimum=4)
        self.assertNotIn('3456', dictionary['entries'])
        self.assertEqual(parse('3456', dictionary, minimum=4)['uncovered_raw_digits'], 4)
        novelty = raw_novelty('3456', sources, [4])[0]
        self.assertEqual(novelty['novel_windows'], 1)

    def test_equal_raw_different_codes_are_retained_and_caps_do_not_fake_uniqueness(self):
        sources = [{'id': 'a', 'codes': ['12', '34'], 'digits': '1234'},
                   {'id': 'b', 'codes': ['01', '02', '03', '04'], 'digits': '1234'}]
        dictionary = build_dictionary(sources, minimum=4)
        fit = parse('1234', dictionary, minimum=4)
        self.assertEqual(fit['retained_distinct_streams'], 2)
        self.assertIsNone(fit['unique_full_codes'])
        capped = parse('1234', dictionary, minimum=4, stream_cap=1)
        self.assertFalse(capped['stream_enumeration_complete'])
        self.assertIsNone(capped['unique_full_codes'])

    def test_fragment_witnesses_roundtrip_and_incomplete_source_alignment_is_rejected(self):
        source = {'id': 'a', 'codes': ['00', '01', '12'], 'digits': '00112'}
        dictionary = build_dictionary([source], minimum=3)
        for raw, variants in dictionary['entries'].items():
            for codes, witness in variants.items():
                omitted = set(witness['omitted_relative_indices'])
                serialized = ''.join(str(c) if i in omitted else f'{c:02d}' for i, c in enumerate(codes))
                self.assertEqual(raw, serialized)
        with self.assertRaises(ValueError):
            build_dictionary([source], minimum=3, alignment_cap=1)


if __name__ == '__main__':
    unittest.main()
