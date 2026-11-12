import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from zero_restoration_audit import parse_summary, serialize


class RawSegmentationTests(unittest.TestCase):
    def test_dp_matches_exhaustive_boundary_enumeration(self):
        inventory = {'00', '01', '10'}
        for length in range(7):
            for digits in itertools.product('01', repeat=length):
                raw = ''.join(digits)
                lengths = []
                # Enumerate every partition independently of the DP recurrence.
                for cuts in itertools.product([False, True], repeat=max(0, length - 1)):
                    starts = [0] + [i + 1 for i, cut in enumerate(cuts) if cut] + [length]
                    pieces = [raw[a:b] for a, b in zip(starts, starts[1:])]
                    if not raw:
                        pieces = []
                    if all((len(p) == 1 and '0' + p in inventory) or
                           (len(p) == 2 and p in inventory) for p in pieces):
                        lengths.append(len(pieces))
                result = parse_summary(raw, inventory)
                self.assertEqual(int(result['segmentation_path_count']), len(lengths))
                self.assertEqual(result['min_tokens'], min(lengths))
                self.assertEqual(result['max_tokens'], max(lengths))

    def test_no_admissible_path_is_distinct_from_empty_input(self):
        impossible = parse_summary('99', {'01'})
        self.assertEqual(impossible['segmentation_path_count'], '0')
        self.assertIsNone(impossible['minimum_token_witness'])
        self.assertEqual(parse_summary('', {'01'})['segmentation_path_count'], '1')

    def test_all_single_digits_demonstrate_policy_scope(self):
        raw = '0012398765'
        codes = ['0' + digit for digit in raw]
        policy = {f'0{i}': True for i in range(10)}
        self.assertEqual(serialize(codes, policy), raw)
        # Exhausting policies on one fixed stream cannot exclude other streams.
        self.assertNotEqual(serialize(['00', '12'], policy), raw)


if __name__ == '__main__':
    unittest.main()
