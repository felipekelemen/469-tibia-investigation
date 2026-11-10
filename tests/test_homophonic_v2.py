import pathlib,sys,unittest,collections,random
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from homophonic_benchmark_v2 import fixture,TRAIN_N,HOLD_N
from homophonic_benchmark import fixture as old_fixture
from qualified_tibia_search import null_data
class FreshQualificationTests(unittest.TestCase):
    def test_new_authors_and_disjoint_source_excerpts(self):
        oldhashes={old_fixture(i,52,'balanced')['plain_excerpt_sha256'] for i in range(30)}
        intervals=collections.defaultdict(list)
        for i in range(30):
            f=fixture(i,99,'skewed');self.assertNotIn(f['text_hash'],oldhashes)
            self.assertIn(f['source'],['war_worlds','great_expectations'])
            intervals[f['source']].append((f['offset'],f['offset']+TRAIN_N+HOLD_N))
        for xs in intervals.values():
            xs.sort();self.assertTrue(all(a[1]<=b[0] for a,b in zip(xs,xs[1:])))
    def test_true_key_reconstruction_and_unseen_accounting(self):
        f=fixture(16,99,'skewed');codes=[c for seq in f['hold'] for c in seq]
        self.assertEqual(''.join(chr(f['true_key'][c]+65) for c in codes),f['truth_hold'])
        seen={c for seq in f['train'] for c in seq}
        self.assertEqual(f['unseen_positions'],sum(c not in seen for c in codes))
    def test_matched_nulls_preserve_book_lengths_and_histograms(self):
        original=[[1,2,1,3,1,2,1,4,1],[8,8,9,8,9,8]]
        snapshot=[s[:] for s in original]
        for mode in ['shuffle','bigrams','blocks8']:
            out=null_data(original,random.Random(773),mode)
            self.assertEqual([len(s) for s in out],[len(s) for s in original])
            self.assertEqual([collections.Counter(s) for s in out],[collections.Counter(s) for s in original])
            if mode=='bigrams':
                for a,b in zip(original,out):
                    self.assertEqual(collections.Counter(zip(a,a[1:])),collections.Counter(zip(b,b[1:])))
                    self.assertEqual((a[0],a[-1]),(b[0],b[-1]))
        self.assertEqual(original,snapshot)
if __name__=='__main__':unittest.main()
