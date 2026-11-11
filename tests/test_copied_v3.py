import pathlib,sys,unittest,hashlib
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from copied_homophonic_v3 import build_model,TRAINING_PATHS
from copied_benchmark_v3 import fixture,MODES
class CopiedQualificationTests(unittest.TestCase):
    def test_model_excludes_fresh_authors_and_has_no_source_bridge(self):
        table,meta=build_model()
        self.assertTrue(all('benchmark_reference_v3' not in p for p in TRAINING_PATHS))
        self.assertEqual(meta['tetragrams'],sum(r['letters']-3 for r in meta['training_sources']))
        self.assertEqual(meta['model_sha256'],hashlib.sha256(table.astype('<f8').tobytes()).hexdigest())
        self.assertAlmostEqual(float(np.sum(10**table)),1.0,places=10)
    def test_true_key_recovers_all_modes(self):
        for mode in MODES:
            f=fixture(16,mode);codes=[c for s in f['hold'] for c in s]
            self.assertEqual(len(codes),1024)
            self.assertEqual(''.join(chr(f['key'][c]+65) for c in codes),f['truth'])
    def test_source_windows_do_not_overlap_across_fixtures_or_ordinary(self):
        intervals={}
        for mode in ['copied_static_codes','ordinary']:
            for i in range(30):
                f=fixture(i,mode);n=256 if mode=='copied_static_codes' else 6692
                for start in f['source_offsets']:intervals.setdefault(f['source'],[]).append((start,start+n))
        for xs in intervals.values():
            xs.sort();self.assertTrue(all(a[1]<=b[0] for a,b in zip(xs,xs[1:])))
if __name__=='__main__':unittest.main()
