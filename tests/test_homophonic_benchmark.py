import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from homophonic_benchmark import encode,fixture,excerpt,TRAIN_N,HOLD_N
class BenchmarkTests(unittest.TestCase):
    def test_cipher_known_key_roundtrip_and_disjoint_pools(self):
        text='ABCDEFGHIJKLMNOPQRSTUVWXYZ'*4
        for n in [52,75,99]:
            for d in ['balanced','skewed']:
                codes,key,allocation=encode(text,n,d,83)
                self.assertEqual(''.join(chr(key[c]+65) for c in codes),text)
                self.assertEqual(sum(allocation),n)
                self.assertTrue(all(a>=1 for a in allocation))
                self.assertEqual(sum(k>=0 for k in key),n)
    def test_codes_are_not_adjacent_letter_ids(self):
        xs,key,_=encode('ABCDEFGHIJKLMNOPQRSTUVWXYZ'*5,52,'balanced',10)
        self.assertNotEqual([c//2 for c in xs],[ord(c)-65 for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'*5])
    def test_qualification_source_excerpts_do_not_overlap(self):
        intervals={}
        for i in range(30):
            text,source,start=excerpt(i)
            self.assertEqual(len(text),TRAIN_N+HOLD_N)
            for a,b in intervals.setdefault(source,[]):self.assertTrue(start>=b or start+len(text)<=a)
            intervals[source].append((start,start+len(text)))
    def test_truth_not_derived_from_current_fixture_training(self):
        f=fixture(0,99,'skewed')
        self.assertEqual(sum(map(len,f['train_sequences'])),TRAIN_N)
        self.assertEqual(sum(map(len,f['hold_sequences'])),HOLD_N)
        self.assertEqual(len(f['truth_hold']),HOLD_N)
        self.assertEqual(f['seen_code_hold_fraction'],1-f['hold_unseen_positions']/HOLD_N)
if __name__=='__main__':unittest.main()
