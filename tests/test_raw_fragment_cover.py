import itertools
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from raw_fragment_cover import cover


class RawFragmentCoverTests(unittest.TestCase):
    def test_piece_minimum_matches_exhaustive_partitions(self):
        books = [{'id': 'a', 'digits': '0011'}, {'id': 'b', 'digits': '101'}]
        for length in range(1, 7):
            for digits in itertools.product('01', repeat=length):
                raw = ''.join(digits)
                costs = []
                for flags in itertools.product([False, True], repeat=length - 1):
                    starts = [0] + [i + 1 for i, flag in enumerate(flags) if flag] + [length]
                    pieces = [raw[a:b] for a, b in zip(starts, starts[1:])]
                    if all(any(piece in source['digits'] for source in books) for piece in pieces):
                        costs.append(len(pieces))
                self.assertEqual(cover(raw, books)['copied_pieces'], min(costs))

    def test_long_minimum_retains_residual_instead_of_repairing_it(self):
        fit = cover('12349', [{'id': 'a', 'digits': '123456'}], minimum=4)
        self.assertEqual(fit['uncovered_raw_digits'], 1)
        self.assertEqual(fit['copied_pieces'], 1)
        self.assertEqual(''.join(x['literal'] for x in fit['path']), '12349')


if __name__ == '__main__':
    unittest.main()
