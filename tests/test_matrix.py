import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from matrix_experiments import determinant, inverse, transform, MATRICES

class MatrixTests(unittest.TestCase):
    def test_hill_known_vector(self):
        # Standard textbook GYBNQKURP matrix: ACT -> POH in A=0.
        matrix=[[6,24,1],[13,16,10],[20,17,15]]
        self.assertEqual(transform([0,2,19],matrix,26),[15,14,7])
        self.assertEqual(transform([15,14,7],inverse(matrix,26),26),[0,2,19])

    def test_composite_modulus_roundtrip(self):
        for matrix in MATRICES.values():
            for modulus in (10,26,27,29,256):
                inv=inverse(matrix,modulus)
                if inv is not None:
                    for value in range(modulus):
                        block=[value,(value+1)%modulus,(value*3)%modulus,(value*7)%modulus]
                        self.assertEqual(transform(transform(block,matrix,modulus),inv,modulus),block)

    def test_noninvertibility(self):
        self.assertIsNone(inverse([[2,0],[0,1]],26))
        self.assertEqual(transform([0,0,0,0],MATRICES['new'],26),
                         transform([13,13,0,0],MATRICES['new'],26))

    def test_no_implicit_padding(self):
        self.assertEqual(transform([1,2,3],MATRICES['old'],26),[])

if __name__=='__main__':unittest.main()
