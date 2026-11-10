import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from structural_experiments import lcg_fits,recurrence2_fits,occurrences
class GeneratorControls(unittest.TestCase):
    def test_lcg_positive_and_perturbation(self):
        seq=[3]
        for _ in range(80):seq.append((21*seq[-1]+17)%100)
        self.assertIn((21,17),lcg_fits([seq]))
        seq[-1]=(seq[-1]+1)%100
        self.assertEqual(lcg_fits([seq]),[])
    def test_second_order_positive(self):
        seq=[7,31]
        for _ in range(70):seq.append((13*seq[-1]+17*seq[-2]+3)%100)
        self.assertIn((13,17,3),recurrence2_fits([seq]))
    def test_overlap_counts(self):
        self.assertEqual(occurrences('1111','11'),3)
if __name__=='__main__':unittest.main()
