import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from npc_framing_census import all_paths_short, fibonacci_count, parse_count


class FramingCountTests(unittest.TestCase):
    def test_all100_fibonacci_identity_for_different_digits(self):
        inventory = [f'{i:02d}' for i in range(100)]
        for length in range(8):
            for seq in itertools.product('039', repeat=length):
                raw = ''.join(seq)
                self.assertEqual(parse_count(raw, inventory), fibonacci_count(length))

    def test_observed_inventory_changes_count_without_manufacturing_zero_parses(self):
        full = [f'{i:02d}' for i in range(100)]
        partial = [w for w in full if w != '39']
        self.assertEqual(parse_count('39', full), 2)
        self.assertEqual(parse_count('39', partial), 1)
        self.assertEqual(all_paths_short('39', partial), [['03', '09']])

    def test_recursive_enumeration_and_dp_agree_for_short_anchors(self):
        inventory = [f'{i:02d}' for i in range(100) if i != 39]
        for raw in ('1', '0', '3478', '486486', '0039'):
            self.assertEqual(len(all_paths_short(raw, inventory)), parse_count(raw, inventory))

    def test_counts_emission_paths_not_distinct_code_id_sequences(self):
        inventory = [f'{i:02d}' for i in range(100)]
        paths = all_paths_short('000', inventory)
        self.assertEqual(len(paths), 3)
        self.assertEqual(len({tuple(path) for path in paths}), 2)
        self.assertEqual(parse_count('000', inventory), 3)


if __name__ == '__main__':
    unittest.main()
