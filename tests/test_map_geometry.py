import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from map_geometry import features,majority_accuracy
class GeometryTests(unittest.TestCase):
    def test_conflict_requires_error(self):
        self.assertEqual(majority_accuracy([0,0,1],['A','B','C']),2/3)
    def test_consistent_feature_can_recover_labels(self):
        self.assertEqual(majority_accuracy([0,0,1,1],['A','A','B','B']),1)
    def test_bilinear_basis_vectors_and_orientation(self):
        fs=features()
        self.assertEqual(fs['old_column_bit_bilinear_low_first_mod26'](1,4),6)
        self.assertEqual(fs['old_transpose_bit_bilinear_low_first_mod26'](1,4),1)
if __name__=='__main__':unittest.main()
