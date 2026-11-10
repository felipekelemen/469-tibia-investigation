import pathlib,sys,unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from matrix_walk_experiment import scan_order,block_order,permute,configs
class MatrixWalkTests(unittest.TestCase):
    def test_known_weight_order_with_stable_ties(self):
        self.assertEqual(block_order('old',0,False),[1,3,4,6,7,8,9,11,14,15,5,0,10,12,2,13])
    def test_ragged_roundtrip_and_unchanged_tail(self):
        for length in [0,1,15,16,17,31,32,49]:
            x=np.arange(length);order=block_order('new',5,True)
            y=permute(x,order);self.assertTrue(np.array_equal(permute(y,order,True),x))
            self.assertTrue(np.array_equal(x[length//16*16:],y[length//16*16:]))
    def test_geometries_are_eight_distinct_permutations(self):
        scans=[scan_order(g) for g in range(8)]
        self.assertEqual(len({tuple(s) for s in scans}),8)
        self.assertTrue(all(sorted(s)==list(range(16)) for s in scans))
if __name__=='__main__':unittest.main()
