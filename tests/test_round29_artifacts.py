import json
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from round29_models import ROOT, KEYS, letters
from round29_fixtures import encrypt
from round29_experiment import summarize, verify_inputs


class Round29Artifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load=lambda p:json.loads((ROOT/p).read_text())
        cls.fixtures=load('data/round29_fixtures.json')
        cls.result=load('results/round29_qualification.json')
        cls.protocol=load('data/round29_protocol.json')

    def test_frozen_inputs_unchanged(self):
        verify_inputs()

    def test_known_plaintext_and_out_of_family_keys(self):
        for case in self.fixtures['cases']:
            a,b=case['true_affine_decode_key']
            table=[pow(a,-1,26)*(i-b)%26 for i in range(26)]
            self.assertEqual(encrypt(case['plaintext'],table),''.join(case['datasets']['text_affine']))
            perm=case['permutation_encrypt_table']
            self.assertEqual(sorted(perm),list(range(26)))
            self.assertTrue(all(perm!=[pow(x,-1,26)*(i-y)%26 for i in range(26)] for x,y in KEYS))

    def test_matched_copy_and_shuffle_structure(self):
        for case in self.fixtures['cases']:
            from collections import Counter
            for a,b in zip(case['modules'],case['shuffled_modules']):
                self.assertEqual(Counter(a),Counter(b))
            a,b=case['true_affine_decode_key'];table=[pow(a,-1,26)*(i-b)%26 for i in range(26)]
            for i,draws in enumerate(case['module_draws']):
                self.assertTrue(all(0<=j<(16 if i<50 else 24) for j in draws))
                n=self.fixtures['synthetic_digit_lengths'][i]//2
                for field,module_field in [('text_copied','modules'),('numeric_shuffled_modules','shuffled_modules')]:
                    plain=''.join(case[module_field][j] for j in draws)[:n]
                    self.assertEqual(encrypt(plain,table),case['datasets'][field][i])

    def test_source_windows_do_not_overlap(self):
        sources=json.loads((ROOT/'data/round29_reference/SOURCES.json').read_text())
        for record in sources:
            text=letters(record['path'],record['encoding'])
            intervals=[]
            for case in self.fixtures['cases']:
                if case['source']!=record['path']:continue
                a,b=case['start_letter'],case['end_letter']
                self.assertEqual(text[a:b],case['plaintext'])
                self.assertTrue(all(b<=c or a>=d for c,d in intervals));intervals.append((a,b))
            self.assertEqual(len(intervals),15)

    def test_gates_and_total_costs_match_all_rows(self):
        self.assertEqual(summarize(self.result['rows'],self.protocol),self.result['summary'])
        self.assertEqual(len(self.result['rows']),240)
        for row in self.result['rows']:
            for v in row['comparison']['models'].values():
                self.assertEqual(len(v['per_document_bits']),70)
                self.assertTrue(all(math.isfinite(x) and x>=0 for x in v['per_document_bits']))
                self.assertAlmostEqual(v['total_bits'],v['common_program_and_count_bits']+v['parameter_and_selector_bits']+v['train_data_bits']+v['held_data_bits'])

    def test_failed_gate_does_not_label_game_origin(self):
        audit=json.loads((ROOT/'results/round29_corpus_audit.json').read_text())
        if not any(self.result['summary']['general_origin_application_eligible'].values()):
            self.assertEqual(audit['game_origin_model_scoring'],'not_performed_gate_failed')
            self.assertIsNone(audit['game_origin_label'])
            self.assertFalse(audit['original_nontextual_generator_authenticated'])


if __name__=='__main__':unittest.main()
