import itertools
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from periodic_result_summary import key_union_count

class KeyUnionTests(unittest.TestCase):
    def test_nested_and_crossed_partial_keys_count_union(self):
        self.assertEqual(key_union_count([[1,-1],[1,1]],2),10)
        self.assertEqual(key_union_count([[1,-1],[-1,1]],2),19)
        self.assertEqual(key_union_count([],8),0)
        self.assertEqual(key_union_count([[-1]*8],8),10**8)

    def test_small_union_matches_brute_force(self):
        keys=[[1,-1,3],[-1,2,3],[1,2,-1],[1,2,3]]
        brute=sum(any(all(v<0 or v==x for v,x in zip(k,key)) for k in keys) for key in itertools.product(range(10),repeat=3))
        self.assertEqual(key_union_count(keys,3),brute)

if __name__=='__main__':unittest.main()
