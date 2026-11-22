import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from round28_radix import CODECS, KEYS, Lexicon, decode, encode, fit, predict, values


class RadixTests(unittest.TestCase):
    def test_known_numerals(self):
        self.assertEqual(decode('26', 'canonical26', (1, 0)), 'BA')
        self.assertEqual(decode('0', 'canonical26', (1, 0)), 'A')
        self.assertEqual(decode('26', 'bijective26', (1, 0)), 'Z')
        self.assertEqual(decode('27', 'bijective26', (1, 0)), 'AA')
        self.assertEqual(decode('702', 'bijective26', (1, 0)), 'ZZ')
        self.assertEqual(decode('703', 'bijective26', (1, 0)), 'AAA')
        self.assertEqual(decode('27', 'space27', (1, 0)), 'A ')
        self.assertEqual(decode('0', 'space27', (1, 0)), ' ')
        self.assertIsNone(decode('0', 'bijective26', (1, 0)))

    def test_independent_polynomial_identity(self):
        for codec in CODECS:
            for number in list(range(500)) + [10**35+17, 10**100-1]:
                result = values(str(number), codec)
                if result is None:
                    self.assertEqual((number, codec), (0, 'bijective26'))
                    continue
                base = 27 if codec == 'space27' else 26
                offset = int(codec == 'bijective26')
                recovered = sum((x+offset)*base**i for i, x in enumerate(reversed(result)))
                self.assertEqual(recovered, number)
                self.assertEqual(result, values('000'+str(number), codec))

    def test_all_affine_keys_are_invertible(self):
        self.assertEqual(len(KEYS), 312)
        for key in KEYS:
            for codec in CODECS:
                plain = 'THE QUICK BROWN FOX'
                try:
                    raw = encode(plain, codec, key, padding=2)
                except ValueError:
                    self.assertEqual(codec, 'canonical26')
                    self.assertEqual(key[1], ord('T')-65)
                    continue
                expected = plain if codec == 'space27' else plain.replace(' ', '')
                self.assertEqual(decode(raw, codec, key), expected)

    def test_canonical_leading_symbol_is_not_invented(self):
        with self.assertRaises(ValueError):
            encode('AB', 'canonical26', (1, 0))
        self.assertEqual(decode('1', 'canonical26', (1, 0)), 'B')
        self.assertEqual(encode('A', 'canonical26', (1, 0)), '0')

    def test_lexical_ambiguity_is_counted(self):
        lex = Lexicon(['A', 'BC', 'ABC'])
        self.assertEqual(lex.parse('ABC')['paths'], 2)
        self.assertIsNone(lex.parse('ABC')['unique_words'])
        self.assertEqual(lex.parse('ABC', True)['paths'], 1)
        self.assertEqual(lex.parse('A  BC', True)['unique_words'], ['A', 'BC'])
        self.assertEqual(lex.parse('AB', True)['paths'], 0)

    def test_complete_key_filter_matches_naive_word_partitioning(self):
        words = {'A', 'I', 'BE', 'CAB', 'BEE', 'BAD', 'AB'}
        lex = Lexicon(words)
        def possible(s):
            if not s:
                return True
            return any(s.startswith(w) and possible(s[len(w):]) for w in words)
        for codec in CODECS:
            groups = [encode(w, codec, (1, 0)) for w in ('CAB', 'BEE')]
            expected = []
            for key in KEYS:
                decoded = [decode(g, codec, key) for g in groups]
                valid = all(all(w in words for w in s.split()) if codec == 'space27'
                            else possible(s) for s in decoded)
                if valid and any(s.replace(' ', '') for s in decoded):
                    expected.append(list(key))
            self.assertEqual(fit(groups, codec, 'runs', lex)['keys'], expected)

    def test_no_key_or_all_spaces_is_not_a_translation(self):
        lex = Lexicon(['A'])
        self.assertEqual(fit(['0'], 'space27', 'runs', lex)['keys'], [])
        self.assertEqual(predict(['1'], 'canonical26', 'runs', [], lex)['status'],
                         'no_common_length_or_no_key')

    def test_transfer_does_not_require_heldout_dictionary_membership(self):
        lex = Lexicon(['A', 'B'])
        for codec in CODECS:
            raw = encode('XYZZY', codec, (1, 0))
            p = predict([raw], codec, 'runs', [[1, 0]], lex)
            self.assertEqual(p['unique_literal'], 'XYZZY')
            self.assertEqual(p['unique_words'], ['XYZZY'] if codec == 'space27' else None)

    def test_partial_consensus_does_not_choose_a_key(self):
        lex = Lexicon(['A', 'B', 'D'])
        p = predict(['1'], 'canonical26', 'runs', [[1, 0], [3, 0]], lex)
        self.assertEqual(p['certified'], '?')
        self.assertIsNone(p['unique_literal'])


if __name__ == '__main__':
    unittest.main()
