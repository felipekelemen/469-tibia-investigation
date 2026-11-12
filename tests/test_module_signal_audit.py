import pathlib,sys,unittest,random
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from module_signal_audit import encode_codes,literal_codes,fit_inventory,parse,decompose,aggregate
class ModuleAuditTests(unittest.TestCase):
    def test_lossless_reference_and_literal_parse(self):
        motif=encode_codes(range(8));text=motif+encode_codes([12])+motif
        tokens,bits=parse(text,[motif],99)
        self.assertEqual(''.join(t['text'] for t in tokens),text)
        self.assertEqual(sum(len(t['text']) for t in tokens if t['kind']=='reference'),16)
        self.assertEqual(literal_codes(motif),list(range(8)))
    def test_no_cross_book_module_learning_or_scoring(self):
        train=[encode_codes([0,1,2,3]),encode_codes([4,5,6,7])]
        self.assertEqual(fit_inventory(train,99),[])
        groups=[[{'kind':'literal','text':encode_codes([x]),'dictionary_index':None} for x in range(4)] for _ in range(2)]
        r=aggregate(groups,list(range(26)),np.zeros(26**4))
        self.assertEqual(r['windows'],2)
    def test_unseen_hold_does_not_modify_discovery_inventory(self):
        motif=encode_codes(range(8));dictionary=fit_inventory([motif*5],99)
        self.assertTrue(dictionary);before=list(dictionary)
        held=encode_codes(range(8,16));tokens,_=parse(held,dictionary,99)
        self.assertEqual(before,dictionary)
        self.assertTrue(all(t['kind']=='literal' for t in tokens))
    def test_internal_score_invariant_under_whole_token_order(self):
        table=np.random.default_rng(76).normal(-5,1,26**4)
        a={'kind':'reference','text':encode_codes(range(8)),'dictionary_index':0}
        b={'kind':'reference','text':encode_codes(range(8,16)),'dictionary_index':1}
        literal={'kind':'literal','text':encode_codes([1]),'dictionary_index':None}
        first=decompose([a,literal,b,a],list(range(26)),table)
        second=decompose([b,a,literal,a],list(range(26)),table)
        self.assertEqual(first['categories']['internal_module']['windows'],15)
        self.assertAlmostEqual(first['categories']['internal_module']['score_sum'],second['categories']['internal_module']['score_sum'],places=10)
        self.assertNotEqual(first['categories']['module_boundary']['score_sum'],second['categories']['module_boundary']['score_sum'])
if __name__=='__main__':unittest.main()
