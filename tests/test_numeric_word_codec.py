import collections
import itertools
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from numeric_word_codec import (complete_parse, decode_dictionary, decode_wire,
    dictionary_wire, gamma, parse_and_encode, unique_decodability)
from wordcode_transfer_experiment import (KINDS, control_mapping, dictionaries,
    frequency_dictionary, substring_pools)


def classical_sp(words):
    """Independent set-iteration formulation, no oriented witness graph."""
    def quotient(a, b):
        return {y[len(x):] for x in a for y in b if y.startswith(x)}
    current = quotient(words, words)-{''}
    visited = set()
    while frozenset(current) not in visited:
        if '' in current:
            return False
        visited.add(frozenset(current))
        current = quotient(words, current) | quotient(current, words)
    return True


class WordCodeTests(unittest.TestCase):
    def test_prefix_conflict_is_not_ambiguity_and_cycles_terminate(self):
        for words in ({'0', '01'}, {'0', '01', '11'}):
            result = unique_decodability(words)
            self.assertFalse(result['prefix_free'])
            self.assertTrue(result['uniquely_decodable'])

    def test_constructive_ambiguity_really_has_two_distinct_parses(self):
        for words in ({'0', '01', '10'}, {'12', '3', '123'}):
            result = unique_decodability(words)
            self.assertFalse(result['uniquely_decodable'])
            witness = result['witness']
            self.assertNotEqual(witness['first'], witness['second'])
            self.assertEqual(''.join(witness['first']), witness['wire'])
            self.assertEqual(''.join(witness['second']), witness['wire'])
            self.assertGreater(complete_parse(witness['wire'], words)['count'], 1)

    def test_residual_graph_agrees_with_independent_sp_set_algorithm(self):
        candidates = ['0', '1', '00', '01', '10', '11', '001', '101']
        for size in range(1, 5):
            for words in itertools.combinations(candidates, size):
                self.assertEqual(unique_decodability(words)['uniquely_decodable'], classical_sp(set(words)), words)

    def test_dictionary_and_message_roundtrips_include_empty_and_unknowns(self):
        for words in ([], ['1'], ['01', '12', '345'], [str(i) for i in range(10)]):
            bits = dictionary_wire(words)
            self.assertEqual(decode_dictionary(bits), sorted(words))
            for raw in ('', '1', '010101', '1234512345000999'):
                packed = parse_and_encode(raw, words)
                self.assertEqual(decode_wire(packed['wire'], words), raw)

    def test_dp_matches_exhaustive_paths_for_small_strings(self):
        words = ['0', '01', '10', '101']
        width = (len(words)-1).bit_length()
        def brute(raw):
            if not raw:
                return 0, 0, 1
            literal_bits, literal_count, _ = brute(raw[1:])
            bit_candidates = [5+literal_bits]
            uncovered_candidates = [1+literal_count]
            complete_count = 0
            for word in words:
                if raw.startswith(word):
                    b, u, c = brute(raw[len(word):])
                    bit_candidates.append(1+width+b)
                    uncovered_candidates.append(u)
                    complete_count += c
            return min(bit_candidates), min(uncovered_candidates), complete_count
        for size in range(7):
            for seq in itertools.product('01', repeat=size):
                raw = ''.join(seq)
                payload, literals, count = brute(raw)
                packed = parse_and_encode(raw, words)
                self.assertEqual(packed['reference_mode_bits'], 1+len(gamma(size+1))+payload)
                self.assertEqual(packed['minimum_uncovered_digits'], literals)
                self.assertEqual(complete_parse(raw, words)['count'], count)

    def test_full_digit_coverage_does_not_imply_compression(self):
        packed = parse_and_encode('0123456789'*10, list('0123456789'))
        self.assertEqual(packed['minimum_uncovered_digits'], 0)
        self.assertFalse(packed['uses_references'])
        self.assertEqual(packed['coded_bits'], packed['raw_bits'])

    def test_wire_roundtrip_does_not_identify_ambiguous_unit_sequence(self):
        words = ['12', '3', '123']
        raw = '123'*5
        self.assertEqual(complete_parse(raw, words)['count'], 2**5)
        self.assertIsNone(complete_parse(raw, words)['unique_path'])
        self.assertEqual(decode_wire(parse_and_encode(raw, words)['wire'], words), raw)

    def test_invalid_or_truncated_bits_and_empty_codewords_rejected(self):
        with self.assertRaises(ValueError):
            unique_decodability([''])
        for bits in ('', '000', '0'+gamma(2)+'1111', '0'+gamma(1)+'0', '1'+gamma(2)+'111'):
            with self.assertRaises(ValueError):
                decode_wire(bits, ['1', '2', '3'])

    def test_randomized_dictionaries_preserve_budgets_and_shared_types(self):
        groups = [{'wire': w, 'provenance': [{'id': 'sample'}]} for w in ('0', '1', '67', '677', '3478', '4378')]
        pools = substring_pools([{'digits': '0123456789'*8}], {1, 2, 3, 4})
        for kind in KINDS:
            mapping = control_mapping(groups, kind, pools, random.Random(1648))
            self.assertEqual(len(set(mapping.values())), len(groups))
            self.assertEqual(collections.Counter(map(len, mapping.values())), collections.Counter(len(g['wire']) for g in groups))
            if kind == KINDS[1]:
                for a, b in mapping.items():
                    self.assertEqual(collections.Counter(a), collections.Counter(b))
        freq = frequency_dictionary([g['wire'] for g in groups], pools)
        self.assertEqual(collections.Counter(map(len, freq)), collections.Counter(len(g['wire']) for g in groups))


if __name__ == '__main__':
    unittest.main()
