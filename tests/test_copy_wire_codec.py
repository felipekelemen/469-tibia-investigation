import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from copy_wire_codec import Reader, build_index, decode, encode, gamma, prepare, reference


class CopyWireTests(unittest.TestCase):
    def setUp(self):
        self.books = [{'id': 'a', 'digits': '1234567812345678',
                       'codes': ['12', '34', '56', '78'] * 2},
                      {'id': 'b', 'digits': '001', 'codes': ['00', '01']}]
        self.context = prepare(self.books, 96)

    def test_gamma_roundtrip(self):
        for n in range(1, 1000):
            reader = Reader(gamma(n))
            self.assertEqual(reader.integer(), n)
            self.assertEqual(reader.pos, len(reader.bits))

    def test_both_codecs_roundtrip_empty_literals_and_copies(self):
        for family in ('raw', 'codes'):
            index = build_index(self.context, family)
            for text in ('', '9', '999999999', '23456781234567', '00112345678001'):
                result = encode(text, self.context, family, index)
                self.assertEqual(decode(result['bitstream'], self.context), text)
                self.assertEqual(result['bits'], len(result['bitstream']))

    def test_all_ambiguous_alignments_are_addressable(self):
        self.assertEqual(len(self.context['offsets'][1]), 2)
        for ai in range(2):
            bits = '1' + gamma(4) + reference(self.context, 'codes', 1, 0, 2, ai)
            self.assertEqual(decode(bits, self.context), '001')

    def test_decoder_rejects_corruption(self):
        for bits in ('', '0', '00', '0' + gamma(2) + '01111'):
            with self.assertRaises(ValueError):
                decode(bits, self.context)
        valid = encode('12', self.context, 'raw')['bitstream']
        with self.assertRaises(ValueError):
            decode(valid + '1', self.context)

    def test_dp_matches_exhaustive_short_targets(self):
        for family in ('raw', 'codes'):
            index = build_index(self.context, family)

            def exhaustive(text):
                if not text:
                    return 0
                candidates = [5 + exhaustive(text[1:])]
                for end in range(1, len(text) + 1):
                    if text[:end] in index:
                        candidates.append(len(index[text[:end]][0]) + exhaustive(text[end:]))
                return min(candidates)

            for length in range(5):
                for chars in itertools.product('12', repeat=length):
                    text = ''.join(chars)
                    result = encode(text, self.context, family, index)
                    self.assertEqual(result['bits'] - result['header_bits'], exhaustive(text))

    def test_one_source_zero_bit_address_and_reference_limit(self):
        context = prepare(self.books[:1], 3)
        for family in ('raw', 'codes'):
            result = encode('1234567812345678', context, family)
            self.assertTrue(all(x['target_end'] - x['target_start'] <= 3 for x in result['path']))
            self.assertTrue(result['roundtrip_verified'])


if __name__ == '__main__':
    unittest.main()
