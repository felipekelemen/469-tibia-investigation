import collections,pathlib,random,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from residual_channel import entropy,shuffle_within_symbol,window_summary,transition_stats,positive_controls,orientation_bits,orientation_candidates,mismatch_kind,divergent_maximal_matches
class ResidualControls(unittest.TestCase):
    def test_shuffle_conserves_conditional_marginals(self):
        b={'id':'x','symbols':'ABABABABAB','codes':['01','04','02','05','03','06','01','04','02','05']}
        out=shuffle_within_symbol([b],random.Random(23))[0]
        self.assertEqual(b['symbols'],out['symbols'])
        self.assertEqual(collections.Counter(zip(b['symbols'],b['codes'])),collections.Counter(zip(out['symbols'],out['codes'])))
    def test_context_variation_detected(self):
        a={'id':'a','symbols':'ABCDEFGH','codes':['11']*8}
        b={'id':'b','symbols':'ABCDEFGH','codes':['11']*7+['22']}
        stats=window_summary([a,b],8)
        self.assertEqual(stats['windows_with_multiple_code_variants'],1)
        self.assertEqual(stats['mean_cross_book_exact_code_agreement_equal_window_weight'],0)
        b['codes']=a['codes'][:]
        stats=window_summary([a,b],8)
        self.assertEqual(stats['mean_cross_book_exact_code_agreement_equal_window_weight'],1)
    def test_rotation_positive_vs_iid(self):
        controls=positive_controls()
        self.assertEqual(controls['sorted_rotation']['numeric_sorted_cycle_rate'],1)
        self.assertEqual(controls['sorted_rotation']['conditional_next_code_entropy_bits'],0)
        self.assertGreater(controls['iid_homophones']['conditional_next_code_entropy_bits'],1.8)
        self.assertLess(controls['iid_homophones']['numeric_sorted_cycle_rate'],.35)
    def test_cross_book_only(self):
        a={'id':'a','symbols':'A'*12,'codes':['11']*12}
        self.assertEqual(window_summary([a],8)['unique_cross_book_repeated_windows'],0)
    def test_orientation_known_ascii(self):
        bits=[int(b) for c in b'HELLO WORLD' for b in f'{c:08b}']
        codes=['21' if b else '12' for b in bits]
        books=[{'id':'test','codes':codes,'symbols':'A'*len(codes)}]
        candidate=orientation_candidates(books)[0]
        self.assertEqual(candidate['preview_hex'],b'HELLO WORLD'.hex())
        self.assertEqual(candidate['english_ascii_fraction'],1)
        self.assertEqual(orientation_bits(['11','12','21','00']),[0,1])
    def test_mismatch_classes(self):
        self.assertEqual(mismatch_kind('19','91'),'reversal_19_91')
        self.assertEqual(mismatch_kind('34','43'),'other_digit_reversal')
        self.assertEqual(mismatch_kind('34','65'),'other_homophone_pair')
        self.assertEqual(mismatch_kind('34','34'),'same')
    def test_maximal_match_deduplicates_window_shifts(self):
        a={'id':'a','symbols':'A'*12,'codes':['12']*12}
        b={'id':'b','symbols':'A'*12,'codes':['12']*6+['21']+['12']*5}
        stats=divergent_maximal_matches([a,b],8)
        self.assertEqual(stats['examples_longest'][0]['length'],12)
        self.assertIn('other_digit_reversal',stats['mismatch_counts_over_unique_maximal_runs'])
    def test_entropy(self):
        self.assertAlmostEqual(entropy([1,1,1,1]),2)
        self.assertEqual(entropy([400]),0)
if __name__=='__main__':unittest.main()
