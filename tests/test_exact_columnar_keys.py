import itertools
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from exact_columnar_keys import apply, decrypt, encrypt, fit_pair, infer
from columnar_prefix_audit import prefix_certificate


class ExactColumnarTests(unittest.TestCase):
    def test_known_ragged_vector(self):
        self.assertEqual(encrypt('ABCDEFGHIJK', [2, 0, 3, 1]), 'CGKAEIDHBFJ')
        self.assertEqual(decrypt('CGKAEIDHBFJ', [2, 0, 3, 1]), 'ABCDEFGHIJK')

    def test_exact_solver_agrees_with_exhaustive_small_keyspaces(self):
        for source in ('0123456', '0000000', '0101010', '0011011'):
            for width in range(2, 5):
                expected = {}
                for key in itertools.permutations(range(width)):
                    expected.setdefault(encrypt(source, key), set()).add(key)
                for target, keys in expected.items():
                    result = infer(source, target, width)
                    self.assertEqual(int(result['key_count']), len(keys))
                    self.assertEqual({tuple(k) for k in result['keys']}, keys)
                    self.assertTrue(result['keys_complete'])
                    for key in keys:
                        self.assertEqual(decrypt(target, key), source)

    def test_histogram_equality_is_not_sufficient(self):
        self.assertEqual(infer('1234567', '1324567', 3)['status'], 'UNSAT')

    def test_identical_columns_are_not_collapsed_into_a_unique_key(self):
        result = infer('0' * 137, '0' * 137, 16, key_cap=3)
        self.assertEqual(result['key_count'], str(math.factorial(16)))
        self.assertEqual(len(result['keys']), 3)
        self.assertFalse(result['keys_complete'])

    def test_state_budget_never_claims_unsat(self):
        result = infer('1234567', encrypt('1234567', [2, 0, 1]), 3, state_cap=1)
        self.assertEqual(result['status'], 'UNRESOLVED_STATE_CAP')
        self.assertIsNone(result['key_count'])

    def test_oriented_forward_and_inverse_witnesses(self):
        source, key = '01234567890123', [2, 0, 3, 1]
        for op in ('encrypt', 'decrypt'):
            for ri, ro in itertools.product((False, True), repeat=2):
                config = {'operation': op, 'width': 4, 'reverse_input': ri, 'reverse_output': ro}
                target = apply(source, config, key)
                result = fit_pair(source, target, widths=[4])
                row = next(r for r in result['fits'] if r['config'] == config)
                self.assertIn(key, row['result']['keys'])

    def test_invalid_parameters(self):
        for key in ([], [0, 0], [1, 2]):
            with self.assertRaises(ValueError):
                encrypt('123', key)
        self.assertEqual(infer('1234', '123', 2)['status'], 'UNSAT')
        with self.assertRaises(ValueError):
            infer('12', '12', 3)

    def test_independent_prefix_audit_never_rejects_valid_oriented_examples(self):
        source, key = '01234567890123', [2, 0, 3, 1]
        for op in ('encrypt', 'decrypt'):
            for ri, ro in itertools.product((False, True), repeat=2):
                config = {'operation': op, 'width': 4, 'reverse_input': ri, 'reverse_output': ro}
                target = apply(source, config, key)
                self.assertIsNone(prefix_certificate(source, target, config))

    def test_independent_prefix_mismatch_is_a_concrete_witness(self):
        config = {'operation': 'encrypt', 'width': 3, 'reverse_input': False, 'reverse_output': False}
        source, target = '1234567', '1324567'
        result = prefix_certificate(source, target, config)
        self.assertIsNotNone(result)
        self.assertEqual(len(result['witnesses']), 3)
        for witness in result['witnesses']:
            self.assertNotEqual(witness['column_digit'], witness['required_prefix_digit'])


if __name__ == '__main__':
    unittest.main()
