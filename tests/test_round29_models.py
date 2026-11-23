import copy
import itertools
import math
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from round29_models import (KEYS, compare, copy_dictionary, digit_models, document_costs,
    fit_english, overlap, pair_string, paths_cost, unpair)
from round29_fixtures import encrypt


class Round29Models(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language=fit_english(['data/english_reference/alice.txt'])

    def test_affine_roundtrips_all_keys(self):
        plain='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for a,b in KEYS:
            table=[pow(a,-1,26)*(i-b)%26 for i in range(26)]
            encrypted=encrypt(plain,table)
            decoded=''.join(chr(65+(a*int(encrypted[i:i+2])+b)%26) for i in range(0,len(encrypted),2))
            self.assertEqual(decoded,plain)

    def test_all_text_probabilities_normalize_and_escape_resets(self):
        table=self.language['table']
        self.assertTrue(np.allclose(np.exp2(-table).sum(axis=2),1))
        self.assertTrue(np.allclose(table[:,:,26:],-math.log2(1/16/74)))

    def test_numeric_probabilities_and_exact_count_headers(self):
        models=digit_models(['001','10'])
        self.assertTrue(np.allclose(np.exp2(-models['tables']).sum(axis=2),1))
        self.assertEqual(models['counts'][:2],[3,2])
        self.assertEqual(models['transitions'][1][0],1)
        # No transition from document1 ending1 to document2 starting1.
        self.assertEqual(models['transitions'][1][1],0)
        self.assertEqual(models['parameter_bits'][1],5+3+8)

    def test_pair_bytes_and_odd_tail_are_lossless(self):
        raw=''.join(f'{i:02d}' for i in range(100))+'7'
        self.assertEqual(unpair(pair_string(raw))+raw[-1],raw)
        numeric=digit_models(['001122'])
        costs=document_costs('7',self.language,numeric,[])
        # gamma(2)=3, arithmetic termination2, one uniformly coded odd digit.
        self.assertAlmostEqual(costs[0,0],5+math.log2(10))

    def test_copy_dp_matches_exhaustive_short_paths(self):
        tokens='ABCABCA';dictionary=['ABC','BC','A']
        literals=np.array([[2.+i%3,3.] for i in range(len(tokens))])
        def brute(pos,column):
            if pos==len(tokens):return 0.
            choices=[1+literals[pos,column]+brute(pos+1,column)]
            choices.extend(3+brute(pos+len(s),column) for s in dictionary if tokens.startswith(s,pos))
            return min(choices)
        actual=paths_cost(literals,tokens,dictionary)
        self.assertTrue(np.allclose(actual,[brute(0,i) for i in range(2)]))

    def test_held_data_cannot_change_keys_parameters_or_dictionary(self):
        train=['0011223344556677'*4,'1213141516171819'*4]
        a=compare(train,['9999999999'],self.language)
        b=compare(train,['0102030405'*4],self.language)
        self.assertEqual(a['dictionary'],b['dictionary'])
        self.assertEqual(a['numeric_parameters'],b['numeric_parameters'])
        self.assertEqual(a['selected']['T'],b['selected']['T'])
        self.assertEqual(a['selected']['N'],b['selected']['N'])
        for field in ['key','text_copy','numeric_base','numeric_copy']:
            self.assertEqual(a['selected']['M'][field],b['selected']['M'][field])
        for family in 'TNM':
            self.assertEqual(a['models'][family]['train_data_bits'],b['models'][family]['train_data_bits'])
            model=a['models'][family]
            self.assertAlmostEqual(model['total_bits'],sum(model[x] for x in ['common_program_and_count_bits','parameter_and_selector_bits','train_data_bits','held_data_bits']))

    def test_copy_dictionary_contains_only_training_substrings(self):
        train=['0123456789'*30,'9876543210'*30]
        dictionary,paid=copy_dictionary(train)
        self.assertGreater(paid,0)
        self.assertTrue(all(any(s in pair_string(t) for t in train) for s in dictionary))

    def test_overlap_counts_covered_positions_once(self):
        result=overlap(['ABABAB'],['ABABABX'],4)
        self.assertEqual(result['exact_window_hits'],3)
        self.assertEqual(result['held_digits_covered'],6)


if __name__=='__main__':unittest.main()
