import collections
import math
from pathlib import Path
import random
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from dimension_name_experiments import (ALPHABETS, MATRICES, PARTIAL, WHITEN, algebra,
    alphabet, catalog, decode, decoded_batch, encode, framed, numeric_pairs,
    password_matrix, randomized)
from matrix_experiments import determinant, inverse, transform


class DimensionNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = catalog()

    def test_vectorized_decoder_against_scalar_with_boundaries_and_each_whitening(self):
        rng = random.Random(5415)
        for n, q in {(c['n'], c['q']) for c in self.bank}:
            values = [[rng.randrange(100) for _ in range(37)], [rng.randrange(100) for _ in range(21)]]
            for mode in WHITEN:
                c = next(c for c in self.bank if (c['n'], c['q'], c['whitening']) == (n, q, mode))
                expected = []
                for arr in values:
                    end = len(arr)//n*n
                    row = arr[:end]
                    key = [int('3478'[i % 4]) for i in range(end)]
                    if mode == WHITEN[1]:
                        row = [x+k for x, k in zip(row, key)]
                    elif mode == WHITEN[2]:
                        row = [x-k for x, k in zip(row, key)]
                    out = transform(row, c['operator'], q)
                    if mode == WHITEN[3]:
                        out = [(x+k) % q for x, k in zip(out, key)]
                    elif mode == WHITEN[4]:
                        out = [(x-k) % q for x, k in zip(out, key)]
                    expected.append(''.join(c['output_alphabet'][x] for x in out))
                self.assertEqual(decode(values, c), expected)

    def test_cipher_roundtrip_all_dimensions_moduli_modes_and_output_maps(self):
        rng = random.Random(3478)
        for n, q in {(c['n'], c['q']) for c in self.bank}:
            for mode in WHITEN:
                for keyword in ('', 'BEHOLDER', 'BONELORD'):
                    c = next(c for c in self.bank if (c['n'], c['q'], c['whitening'], c['output_alphabet']) ==
                             (n, q, mode, alphabet(q, keyword)))
                    text = ''.join(rng.choice(ALPHABETS[q]) for _ in range(n*19))
                    values = encode(text, c, rng)
                    self.assertTrue(all(0 <= x <= 99 for x in values))
                    raw = ''.join(f'{v:02d}' for v in values)
                    self.assertEqual(decode([numeric_pairs(raw)], c), [text])

    def test_singular_password_4_is_structural(self):
        for word in ('BEHOLDER', 'BONELORD'):
            for q in ALPHABETS:
                for base in (0, 1):
                    m = password_matrix(word, 4, q, base)
                    self.assertEqual(m[:2], m[2:])
                    self.assertEqual(determinant(m), 0)

    def test_unknown_five_border_is_not_inferable_from_four(self):
        results = algebra()
        self.assertTrue(all(r['determinant'] == 0 for r in results['hypothetical_5_borders']))
        for r in results['nonuniform_5_witnesses']:
            self.assertEqual(r['determinant'], determinant(MATRICES[r['base']])*r['t'])
            self.assertTrue(math.gcd(r['determinant'], 29) == 1)

    def test_hill_inverse_witnesses_composite_modulus(self):
        for c in self.bank[::41]:
            q, n = c['q'], c['n']
            inv = inverse(c['operator'], q)
            for i in range(n):
                basis = [int(j == i) for j in range(n)]
                self.assertEqual(transform(transform(basis, c['operator'], q), inv, q), basis)

    def test_control_invariants_and_global_repeat_preservation(self):
        values = [list(range(100))*2, [0, 3, 7, 0, 3, 7]]
        for kind in ('within_book_value_shuffle', 'within_book_60_value_block_shuffle'):
            out = randomized(values, kind, random.Random(15))
            for a, b in zip(values, out):
                self.assertEqual(collections.Counter(a), collections.Counter(b))
        out = randomized(values, 'global_bijective_digit_relabel_of_two_digit_codes', random.Random(15))
        self.assertEqual(len(set(out[0])), 100)
        self.assertEqual(out[0][:100], out[0][100:])
        self.assertEqual(out[1][:3], out[1][3:])

    def test_windows_never_score_across_book_boundary(self):
        blocks, phase, windows = framed([list(range(8)), list(range(10))], 3)
        self.assertEqual(list(windows), [0, 1, 2, 6, 7, 8, 9, 10, 11])
        self.assertEqual(list(phase), list(np.arange(6) % 4) + list(np.arange(9) % 4))

    def test_catalog_has_no_arbitrary_five_skull_keys_or_singular_operators(self):
        for c in self.bank:
            self.assertTrue(math.gcd(determinant(c['operator']), c['q']) == 1)
            if c['n'] == 5:
                self.assertTrue(all(a['kind'] == 'conjectured_password' for a in c['aliases']))


if __name__ == '__main__':
    unittest.main()
