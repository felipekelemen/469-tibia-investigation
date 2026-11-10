import pathlib,sys,unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from cipher_battery import transform,score,english_model,columnar_order,rail_order
ROOT=pathlib.Path(__file__).resolve().parents[1]
class CipherTests(unittest.TestCase):
    def test_ragged_columnar_known_vector(self):
        # ABCDEFG, 3 columns -> ADGBECF; inverse recovers original.
        seq=np.arange(7)
        self.assertEqual(transform(seq,{'family':'columnar','width':3,'inverse':False}).tolist(),[0,3,6,1,4,2,5])
        self.assertEqual(transform([0,3,6,1,4,2,5],{'family':'columnar','width':3,'inverse':True}).tolist(),list(range(7)))
    def test_vigenere_known_vector(self):
        # Classical ATTACKATDAWN + LEMON = LXFOPVEFRNHR.
        seq=[ord(c)-65 for c in 'ATTACKATDAWN'];key=[ord(c)-65 for c in 'LEMON']
        out=transform(seq,{'family':'vigenere','key':key,'sign':1})
        self.assertEqual(''.join(chr(int(x)+65) for x in out),'LXFOPVEFRNHR')
    def test_scorer_positive_control(self):
        table,text=english_model(ROOT/'data/english_reference/alice.txt')
        seq=np.array([ord(c)-65 for c in text]);shuffled=seq.copy();np.random.default_rng(469).shuffle(shuffled)
        self.assertGreater(score(seq,table),score(shuffled,table)+1)
    def test_holdout_no_shared_16_digits(self):
        import json
        books=json.loads((ROOT/'data/normalized_books.json').read_text());splits=json.loads((ROOT/'data/normalized_splits.json').read_text())
        train={b['digits'][i:i+16] for b in books if b['id'] in splits['discovery_book_ids'] for i in range(len(b['digits'])-15)}
        hold={b['digits'][i:i+16] for b in books if b['id'] in splits['holdout_book_ids'] for i in range(len(b['digits'])-15)}
        self.assertFalse(train&hold)
if __name__=='__main__':unittest.main()
