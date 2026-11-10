import collections,copy,json,pathlib,random,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from generative_comparison import (compare,decode_copy,dictionary_bits,fit_dictionary,
    fit_markov,fit_variant_models,gamma_bits,markov_bits,parse_copy,evaluate_variants)

class GenerativeCodingTests(unittest.TestCase):
    def test_hand_calculated_copy_code_and_roundtrip(self):
        parsed=parse_copy('ABC',['AB'],'ABC')
        # gamma(length+1)=5, one1-bit reference, one3-bit literal.
        self.assertEqual(parsed['bits'],9)
        self.assertEqual(decode_copy(parsed['tokens'],['AB']),'ABC')
        self.assertEqual(dictionary_bits(['AB'],'ABC'),3+3+4)
    def test_fixed_dictionary_does_not_learn_from_reserved(self):
        dictionary=fit_dictionary(['ABCD'*80],'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        before=list(dictionary)
        parsed=parse_copy('WXYZ'*80,dictionary,'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.assertEqual(dictionary,before)
        self.assertTrue(all(k=='literal' for k,_ in parsed['tokens']))
        self.assertEqual(decode_copy(parsed['tokens'],dictionary),'WXYZ'*80)
    def test_no_cross_book_motif_or_transition(self):
        self.assertEqual(fit_dictionary(['AB','CD']*20,'ABCD'),[])
        model=fit_markov(['AB','CD'],'ABCD')
        self.assertEqual(model['transitions']['B']['C'],0)
    def test_markov_prediction_does_not_update_count_model(self):
        model=fit_markov(['AAAA'],'ABC')
        before=copy.deepcopy(model)
        self.assertGreater(markov_bits('BCBC',model),0)
        self.assertEqual(model,before)
    def test_variant_prediction_does_not_update_fit(self):
        fit=fit_variant_models([{'symbols':'AAAA','codes':['11','22','11','22']}])
        before=copy.deepcopy(fit)
        allowed={'A':{'11','22'},'B':{'33','44'}}
        result=evaluate_variants([{'symbols':'BBBB','codes':['33','44','33','44']}],fit,allowed)
        self.assertEqual(fit,before)
        self.assertEqual(result['symbol_marginal']['positions'],4)
    def test_copy_assembly_can_have_short_valid_description(self):
        rng=random.Random(534)
        motifs=[''.join(rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(32)) for _ in range(4)]
        seq=''.join(motifs[i%4] for i in range(120))
        r=compare([seq[:2048]],[seq[2048:]],'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.assertLess(r['total_two_part_bits']['copy'],r['total_two_part_bits']['uniform'])
        self.assertGreater(r['reserved']['reference_symbol_fraction'],.9)
if __name__=='__main__':unittest.main()
