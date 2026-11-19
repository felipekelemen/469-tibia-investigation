from collections import Counter
from itertools import permutations
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from round24_anagram_audit import adjacent_probability, bag_probability, cut, sig, statistics
from round24_claim_audit import ascii3_decode, ascii3_encode, decode_modules, encode_modules, independent_bits, parses, upstream_functions
from round24_context_audit import group_matches, visible


class Round24AuditTests(unittest.TestCase):
    def test_hypergeometric_matches_exhaustive_permutations(self):
        draws = set(permutations('0012334'))
        first = sum(sig(''.join(d[:3])) == sig('013') for d in draws)/len(draws)
        pair = sum(sig(''.join(d[:3])) == sig('013') and sig(''.join(d[3:5])) == sig('23') for d in draws)/len(draws)
        self.assertAlmostEqual(bag_probability('0012334', '013'), first)
        self.assertAlmostEqual(adjacent_probability('0012334', '013', '23'), pair)
        self.assertEqual(bag_probability('000', '01'), 0)

    def test_anagrams_require_whole_groups_and_order(self):
        knight = ['3478', '345']
        self.assertEqual(statistics(['13478', '0345'], knight)['all_knight_signatures'], 0)
        self.assertEqual(statistics(['4378', '453'], knight)['named_pair_adjacent'], 1)
        self.assertEqual(statistics(['453', '4378'], knight)['named_pair_adjacent'], 0)
        for a in permutations('3478'):
            for b in permutations('345'):
                self.assertEqual(statistics([''.join(a), ''.join(b)], knight)['all_knight_signatures'], 2)

    def test_partition_does_not_drop_digits(self):
        words = cut(list('012345678'), [2, 3, 4])
        self.assertEqual(list(map(len, words)), [2, 3, 4])
        self.assertEqual(Counter(''.join(words)), Counter('012345678'))
        with self.assertRaises(AssertionError):
            cut(list('12345'), [2, 2])

    def test_payload_decodes_without_original_and_matches_bit_cost(self):
        strings = {'a': '012301230123', 'b': '012399', 'c': '888'}
        upstream = upstream_functions(); modules, _ = upstream['tile'](strings, 4)
        payload = encode_modules(strings, modules)
        self.assertEqual(decode_modules(payload), strings)
        expected = upstream['two_part_module_code'](strings, list(strings), 4, 10)['TOTAL']
        self.assertTrue(math.isclose(independent_bits(payload), expected))
        # Removing external literal data changes reconstruction, even with all modules retained.
        payload['books']['c'] = []
        self.assertNotEqual(decode_modules(payload), strings)

    def test_zero_module_and_english_roundtrip(self):
        upstream = upstream_functions(); strings = {'x': ascii3_encode('A secret!')}
        modules, _ = upstream['tile'](strings, 1000)
        self.assertEqual(modules, [])
        payload = encode_modules(strings, modules)
        self.assertEqual(ascii3_decode(decode_modules(payload)['x']), 'A secret!')
        cost = upstream['two_part_module_code'](strings, list(strings), 1000, 10)['TOTAL']
        self.assertAlmostEqual(cost, independent_bits(payload))

    def test_parser_enforces_source_spaces_and_does_not_guess(self):
        table = {'12': 'first', '3': 'second'}
        self.assertEqual(parses('123!', table), [('12', '3')])
        self.assertEqual(parses('1 23!', table), [])
        self.assertEqual(parses('1234', table), [])
        self.assertEqual(parses('123!', {'12': 'other', '3': 'words'}), parses('123!', table))

    def test_html_scripts_cannot_supply_evidence(self):
        text = visible('<p>3478 67</p><script>3478 67</script><style>3478 67</style>')
        self.assertEqual(group_matches(text, '3478 67'), 1)
        self.assertEqual(group_matches('13478 67', '3478 67'), 0)


if __name__ == '__main__':
    unittest.main()
