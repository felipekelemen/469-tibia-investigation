from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from chayenne_decimal_search import solve
from target_decimal_solver import Solver, encode

class UnspacedTests(unittest.TestCase):
    def test_segmentation_and_one_shared_key_without_internal_spaces(self):
        solver=Solver(['HELLO','WORLD','A','TEST'],'ascii_upper')
        table=str.maketrans('0123456789','9876543210')
        raw=[encode(w,'ascii_upper').translate(table) for w in ['HELLOWORLD','ATEST']]
        result=solve(raw,solver)
        self.assertTrue(result['complete'])
        self.assertTrue(any(all(str(9-int(k))==v for k,v in m) for m in result['mappings']))

    def test_emoticon_boundary_forbids_code_crossing(self):
        self.assertFalse(solve(['6','5'],Solver(['A'],'ascii_upper'))['mappings'])
        self.assertTrue(solve(['65'],Solver(['A'],'ascii_upper'))['mappings'])

    def test_budget_is_exposed_even_with_no_candidates_yet(self):
        result=solve(['12'],Solver(['A','B'],'ordinal1_compact'),node_limit=0)
        self.assertFalse(result['complete'])

if __name__=='__main__': unittest.main()
