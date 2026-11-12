import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from raw_parser_long_context import LongContextLanguage, decode
from raw_digit_decoder import omission_probability
from test_raw_digit_decoder import example_key


class FourthOrderExample:
    order = 4

    def log_probability(self, history, letter):
        preferred = sum((i + 1) * c for i, c in enumerate(history)) % 26
        return math.log(.5 if letter == preferred else .5 / 25)


class LongContextTests(unittest.TestCase):
    def test_fourth_order_dynamic_program_matches_enumeration(self):
        key, probabilities = example_key()
        language = FourthOrderExample()
        raw = '0010110010'
        weights = []
        def visit(position, history, probability):
            if position == len(raw):
                weights.append(probability / 128)
                return
            for width in [1, 2]:
                if position + width > len(raw):
                    continue
                code = int(raw[position:position + width])
                if not probabilities[code]:
                    continue
                action = .3 if width == 1 else (.7 if code < 10 else 1)
                p = probabilities[code] * action * math.exp(language.log_probability(history, key[code])) * (127 / 128)
                visit(position + width, (history + (key[code],))[-4:], probability * p)
        visit(0, (), 1)
        fit = decode(raw, key, probabilities, language, 'iid_0.3')
        self.assertAlmostEqual(fit['log_evidence'], math.log(sum(weights)), places=10)
        self.assertAlmostEqual(fit['best_log_probability'], math.log(max(weights)), places=10)

    def test_interpolated_probabilities_sum_to_one_for_seen_and_unseen_context(self):
        for order, backoff in [(4, 1), (6, 10)]:
            model = LongContextLanguage(order, backoff)
            for text in ['', 'THE', 'OFTHE', 'QZXQZX']:
                history = tuple(ord(c) - 65 for c in text[-order:])
                self.assertAlmostEqual(sum(math.exp(model.log_probability(history, c)) for c in range(26)), 1, places=10)


if __name__ == '__main__':
    unittest.main()
