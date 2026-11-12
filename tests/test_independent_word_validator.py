import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from independent_word_validator import WordModel,words,build_model
from copied_homophonic_v3 import build_model as char_model
class IndependentWordValidatorTests(unittest.TestCase):
    def test_spaces_only_even_for_unknown_names(self):
        m=WordModel([['THE','CAT','SAT','ON','THE','MAT']]*40)
        for text in ['THECATSATONTHEMAT','BONELORD','XYZZYTHECAT']:
            r=m.segment(text);self.assertEqual(''.join(t['text'] for t in r['tokens']),text)
            self.assertEqual(r['segmented'].replace(' ',''),text)
        with self.assertRaises(ValueError):m.segment('THE-CAT')
    def test_bigram_score_distinguishes_identical_word_multiset(self):
        sentence=['THE','CAT','SAT','ON','THE','MAT'];m=WordModel([sentence]*100)
        natural=''.join(sentence);permuted=''.join(['MAT','THE','ON','SAT','CAT','THE'])
        a=m.segment(natural);b=m.segment(permuted)
        self.assertLess(a['cost_per_letter'],b['cost_per_letter'])
        self.assertEqual(a['known_fraction'],b['known_fraction'])
    def test_documents_do_not_create_cross_source_word_transitions(self):
        m=WordModel([['ALPHA','BETA'],['GAMMA','DELTA']],min_count=1)
        self.assertEqual(m.transitions.get('BETA',{}).get('GAMMA',0),0)
        self.assertEqual(words("I don't know Harker's name."),['I','DONT','KNOW','HARKERS','NAME'])
    def test_word_training_source_hashes_disjoint_from_character_model(self):
        _,word=build_model();_,char=char_model()
        self.assertTrue({r['source_sha256'] for r in word['training_sources']}.isdisjoint({r['source_sha256'] for r in char['training_sources']}))
if __name__=='__main__':unittest.main()
