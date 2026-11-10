import collections,pathlib,random,sys,unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from homophonic_controls import euler_shuffle,bigrams,encode_homophonic,decode_known,null_records
class HomophonicControlsTests(unittest.TestCase):
    def test_euler_counts_and_endpoints(self):
        for text in ['ABACABADABACABAB','AAAAAAA','ABCD','ABABACA','A','']:
            for seed in range(20):
                out=euler_shuffle(text,random.Random(seed))
                self.assertEqual(len(out),len(text));self.assertEqual(collections.Counter(out),collections.Counter(text));self.assertEqual(bigrams(out),bigrams(text))
                if text:self.assertEqual((out[0],out[-1]),(text[0],text[-1]))
    def test_euler_can_randomize_branching_graph(self):
        xs=list('ABACADABACADABACAD')
        variants={tuple(euler_shuffle(xs,random.Random(i))) for i in range(20)}
        self.assertGreater(len(variants),1)
    def test_synthetic_known_key_exact_recovery(self):
        text='ATTACKATDAWNTHEREISNOSPOON'*20
        coded=encode_homophonic(text,random.Random(469))
        self.assertEqual(decode_known(coded),text)
        for letter in set(text):
            allowed={2*(ord(letter)-65),2*(ord(letter)-65)+1}
            self.assertEqual({int(c) for c,l in zip(coded,text) if l==letter},allowed)
    def test_bigram_null_records_preserve_original(self):
        b={'id':'a','codes':np.array([1,2,1,3,1,2,1,3,1])};before=b['codes'].copy()
        out=null_records([b],random.Random(469),'bigrams')[0]
        self.assertTrue(np.array_equal(before,b['codes']))
        self.assertEqual(bigrams(out['codes'].tolist()),bigrams(before.tolist()))
if __name__=='__main__':unittest.main()
