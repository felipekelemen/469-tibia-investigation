import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from copied_benchmark_v4 import fixture,MODES
from copied_homophonic_v3 import TRAINING_PATHS
class ReheatedQualificationTests(unittest.TestCase):
    def test_new_source_authors_and_exact_known_key(self):
        for i in [0,15,29]:
            for mode in MODES:
                f=fixture(i,mode)
                self.assertIn(f['source'],['tom_sawyer','jane_eyre'])
                self.assertEqual(''.join(chr(f['key'][c]+65) for seq in f['hold'] for c in seq),f['truth'])
        self.assertTrue(all('benchmark_reference_v4' not in p for p in TRAINING_PATHS))
    def test_qualification_windows_disjoint(self):
        intervals={}
        for mode in ['copied_static_codes','ordinary']:
            for i in range(30):
                f=fixture(i,mode);size=256 if mode=='copied_static_codes' else 6692
                for x in f['source_offsets']:intervals.setdefault(f['source'],[]).append((x,x+size))
        for xs in intervals.values():
            xs.sort();self.assertTrue(all(a[1]<=b[0] for a,b in zip(xs,xs[1:])))
if __name__=='__main__':unittest.main()
