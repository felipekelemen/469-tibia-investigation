import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from round35_experiment import binomial_interval, evaluate


class BeamIndependentChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='469-r35-test-')
        cls.path = Path(cls.directory.name)
        cls.binary = cls.path / 'beam'
        subprocess.run(['g++', '-O2', '-std=c++17', str(ROOT / 'scripts/round35_beam.cpp'),
                        '-o', str(cls.binary)], check=True)
        cls.units = [''.join(t) for n in (1, 2, 3) for t in itertools.product('ab', repeat=n)]
        cls.vocabulary = ['<s>'] + sorted(cls.units)
        cls.counts = [50] + [i + 2 for i in range(len(cls.units))]
        cls.model = cls.path / 'model.txt'
        cls.model.write_text(str(len(cls.vocabulary)) + '\n' + '\n'.join(
            f'{w} {c}' for w, c in zip(cls.vocabulary, cls.counts)) + '\n0\n')

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def fit(self, groups, rowcap=100000):
        p = subprocess.run([str(self.binary), str(self.model), '1024', str(rowcap),
                            '1000000', '100000', '10', *groups],
                           text=True, capture_output=True, check=True)
        return json.loads(p.stdout)

    def test_rank_and_count_against_whole_key_bruteforce(self):
        groups = ['01', '10', '001']
        ids = {w: i for i, w in enumerate(self.vocabulary)}
        oracle = []
        for a, b in itertools.product(self.units, repeat=2):
            key = {'0': a, '1': b}
            forms = [''.join(key[d] for d in raw) for raw in groups]
            if not all(f in ids for f in forms):
                continue
            score, prev = 0., 0
            for form in forms:
                i = ids[form]
                score += .35 * math.log((self.counts[i] + .1) / (sum(self.counts[1:]) + .1 * len(self.units)))
                score += .65 * math.log(.1 / (self.counts[prev] + .1 * len(self.units)))
                prev = i
            oracle.append((score, key, forms))
        result = self.fit(groups)
        self.assertEqual(result['pruned'], 0)
        self.assertEqual(result['retained'], len(oracle))
        self.assertAlmostEqual(result['top'][0]['score'], max(o[0] for o in oracle), places=11)
        for candidate in result['top']:
            key = {str(i): u for i, u in enumerate(candidate['key']) if u}
            match = [o for o in oracle if o[1] == key]
            self.assertEqual(len(match), 1)
            self.assertAlmostEqual(candidate['score'], match[0][0], places=11)

    def test_unobserved_digit_is_not_assigned(self):
        result = self.fit(['0', '00'])
        self.assertTrue(result['top'])
        for row in result['top']:
            self.assertTrue(row['key'][0])
            self.assertEqual(row['key'][1:], [''] * 9)

    def test_truncation_is_not_zero_solutions(self):
        result = self.fit(['01'], rowcap=1)
        self.assertEqual(result['status'], 'limit')
        self.assertEqual(result['limit'], 'local_rows')
        self.assertEqual(result['top'], [])

    def test_binomial_zero_event_interval_matches_closed_form(self):
        low, high = binomial_interval(0, 30)
        self.assertEqual(low, 0.)
        self.assertAlmostEqual(high, 1 - .025 ** (1 / 30), places=12)
        self.assertAlmostEqual(binomial_interval(30, 30)[0], .025 ** (1 / 30), places=12)


if __name__ == '__main__':
    unittest.main()
