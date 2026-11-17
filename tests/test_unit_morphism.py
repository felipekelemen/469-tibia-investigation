import itertools
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from unit_morphism_lexicon import Bank,syllabify
from unit_morphism_solver import word_extensions,word_pattern,solve,decode_word,decode_stream,key_tuple


def bank(forms,family='grapheme1_3'):
    return Bank(family,{f:{f} for f in forms},{})


class UnitMorphismTests(unittest.TestCase):
    def test_partition_does_not_select_first_regex_parse(self):
        got={key_tuple(k) for k in word_extensions('01','ABC',1,3)}
        self.assertEqual(got,{(('0','A'),('1','BC')),(('0','AB'),('1','C'))})

    def test_repeat_equality_and_homophony(self):
        self.assertEqual(list(word_extensions('00','AB',1,3)),[])
        self.assertIn({'0':'A','1':'A'},list(word_extensions('01','AA',1,3)))
        self.assertEqual(list(word_extensions('010','ABABA',1,3,{'0':'AB'})),[])

    def test_regex_matches_exhaustive_partitions(self):
        for raw in ['0','00','01','010','011','012']:
            for known in [{},{'0':'A'},{'1':'AB'}]:
                p=word_pattern(raw,1,2,known)
                for n in range(1,7):
                    for letters in itertools.product('AB',repeat=n):
                        f=''.join(letters)
                        self.assertEqual(bool(p.fullmatch(f)),bool(list(word_extensions(raw,f,1,2,known))),(raw,f,known))

    def test_solver_agrees_with_brute_force(self):
        b=bank(['A','B','AB','BA','ABA','BAB','AABB','BABA'])
        units=[''.join(x) for n in range(1,4) for x in itertools.product('AB',repeat=n)]
        words=['01','10','001']
        expected={key_tuple({'0':a,'1':z}) for a,z in itertools.product(units,repeat=2) if all(''.join({'0':a,'1':z}[d] for d in w) in b.reverse for w in words)}
        out=solve(words,b)
        self.assertTrue(out['complete']);self.assertEqual({key_tuple(k) for k in out['keys']},expected)

    def test_local_root_empty_certificate(self):
        out=solve(['00','01'],bank(['AB']))
        self.assertTrue(out['complete']);self.assertEqual(out['keys'],[])
        self.assertEqual(out['root_impossible_groups'],['00'])

    def test_caps_do_not_report_rejection(self):
        b=bank(['A','B','AB','BA'])
        for kwargs in [{'max_states':1},{'max_solutions':1},{'local_cap':1}]:
            out=solve(['0'],b,**kwargs)
            self.assertFalse(out['complete']);self.assertIsNotNone(out['limit'])

    def test_crib_and_unseen_digits(self):
        b=bank(['AB','BA','A','B'])
        out=solve(['01','0'],b,cribs={'01':['AB']})
        self.assertEqual(out['keys'],[{'0':'A','1':'B'}])
        self.assertEqual(decode_word('2',out['keys'][0],b)['status'],'unknown_digits')

    def test_stream_preserves_paths_and_homophones(self):
        b=Bank('grapheme1_3',{'A':{'A'},'B':{'B'},'AB':{'AB','ALT'}},{})
        result=decode_stream('01',{'0':'A','1':'B'},b)
        self.assertEqual(result['word_paths'],3);self.assertIsNone(result['unique_words'])
        self.assertEqual(decode_stream('2',{},b)['status'],'unknown_digits')
        self.assertEqual(decode_stream('0',{'0':'C'},b)['word_paths'],0)
        self.assertEqual(decode_stream('0',{'0':'A'},b)['unique_words'],['A'])

    def test_operational_syllabification(self):
        self.assertEqual(syllabify(('A','S','T','A'),{'A'},{(),('T',),('S','T')}),(('A',),('S','T','A')))
        self.assertEqual(syllabify(('A','S','T','A'),{'A'},{(),('T',)}),(('A','S'),('T','A')))
        self.assertIsNone(syllabify(('S','T'),{'A'},{()}))

if __name__=='__main__':unittest.main()
