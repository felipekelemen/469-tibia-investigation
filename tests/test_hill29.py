import pathlib,sys,unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from hill29_experiments import ALPHABET,ROOT,encode,render,english_model29,score29,transform29,candidates,normalize_english
from matrix_experiments import MATRICES,inverse,transpose
class Hill29Tests(unittest.TestCase):
    def test_punctuation_and_ragged_roundtrip(self):
        source='BEHOLDER BONELORD. REALLY? YES'
        for matrix in MATRICES.values():
            for operator in [matrix,transpose(matrix)]:
                for length in range(len(source)-4,len(source)+1):
                    x=encode(source[:length]);encrypted=transform29(x,operator,True)
                    self.assertTrue(np.array_equal(transform29(encrypted,inverse(operator,29),True),x))
                    self.assertEqual(render(x),source[:length])
    def test_no_silent_padding_in_screen(self):
        self.assertEqual(len(transform29(encode('HELLO'),MATRICES['new'])),4)
    def test_frozen_model_sensitive_to_english(self):
        model,positive=english_model29(ROOT/'data/english_reference/alice.txt')
        x=encode(positive);y=x.copy();np.random.default_rng(29).shuffle(y)
        self.assertGreater(score29(x,model),score29(y,model)+1.)
        self.assertGreater(score29(x,model),score29(encode('?'*len(x)),model))
    def test_explicit_grid(self):
        self.assertEqual(len(candidates()),320)
        self.assertEqual(len(ALPHABET),29)
        self.assertEqual(normalize_english('Hello,   world!\nWHY?'),'HELLO WORLD WHY?')
if __name__=='__main__':unittest.main()
