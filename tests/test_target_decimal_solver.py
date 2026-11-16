import itertools
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from target_decimal_solver import Solver, complete_keys, encode, extension, letter_parse, merge

class TargetDecimalTests(unittest.TestCase):
    def test_nonbijective_and_conflicting_assignments_rejected(self):
        self.assertIsNone(extension('12','11'))
        self.assertIsNone(merge((('1','2'),),(('3','2'),)))
        self.assertIsNone(merge((('1','2'),),(('1','3'),)))

    def test_csp_matches_brute_force_on_small_observed_alphabet(self):
        solver=Solver(['A','B','C','AA','AB','BA','BB','CC','ABC','BBA','CCA'], 'ordinal1_compact')
        groups=['78','887']
        expected=[]
        for a,b in itertools.permutations('0123456789',2):
            key=(('7',a),('8',b))
            if all(solver.words_for(g,key) for g in groups): expected.append([list(x) for x in key])
        result=solver.solve(groups)
        self.assertTrue(expected)
        self.assertTrue(result['complete'])
        self.assertEqual(result['mappings'],expected)

    def test_known_key_retained_and_transferred_without_refit(self):
        solver=Solver(['HELLO','WORLD','TEST'], 'ascii_upper')
        perm=str.maketrans('0123456789','9876543210')
        raw=[encode(w,'ascii_upper').translate(perm) for w in ['HELLO','WORLD']]
        result=solver.solve(raw)
        keys=complete_keys(result)
        self.assertTrue(keys)
        self.assertTrue(any(solver.words_for(encode('TEST','ascii_upper').translate(perm),key)==['TEST'] for key in keys))

    def test_budget_exhaustion_is_not_unsatisfiability(self):
        result=Solver(['A','I'],'ordinal1_compact').solve(['0'],node_limit=0)
        self.assertFalse(result['complete'])
        self.assertIsNone(complete_keys(result))

    def test_leading_zeroes_and_ambiguous_decimal_parsing_retained(self):
        identity=dict(zip('0123456789','0123456789'))
        self.assertEqual(encode('A','ordinal0_fixed2'),'00')
        self.assertEqual(encode('A','ascii_lower_fixed3'),'097')
        self.assertEqual(letter_parse('11','ordinal1_compact',identity)['count'],2)
        self.assertIsNone(letter_parse('11','ordinal1_compact',identity)['unique_literal'])
        self.assertEqual(letter_parse('6573','ascii_upper',identity)['unique_literal'],'AI')

    def test_unused_key_digits_remain_multiple_completions(self):
        result=Solver(['A'],'ordinal1_compact').solve(['0'])
        self.assertEqual(result['full_key_count'],362880)
        self.assertIsNone(complete_keys(result,limit=20000))

if __name__=='__main__': unittest.main()
