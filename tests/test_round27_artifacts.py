"""Artifact, leakage and certificate-contract checks, separate from qualification."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from round27_experiment import verify_manifest
from round27_witness_solver import emit
from round27_fixtures import training_bank


class Round27Artifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads((ROOT/'data/round27_protocol.json').read_text())
        cls.fixtures = json.loads((ROOT/'data/round27_fixtures.json').read_text())
        cls.result = json.loads((ROOT/'results/round27_qualification.json').read_text())
        cls.bank = training_bank(cls.protocol)

    def test_manifests_and_all_predeclared_cases(self):
        for filename in ('round27_experiment_manifest.json', 'round27_baseline_manifest.json',
                         'round27_result_manifest.json'):
            verify_manifest(filename)
        expected = {(c['id'], s) for c in self.fixtures['cases']
                    for s in (self.protocol['scenarios'][:3] if c['kind'] == 'base'
                              else self.protocol['scenarios'][3:])}
        observed = [(r['id'], r['scenario']) for r in self.result['cases']]
        self.assertEqual(len(observed), 120)
        self.assertEqual(set(observed), expected)

    def test_fixture_truth_is_admissible_without_word_leakage(self):
        self.assertEqual(len(self.fixtures['cases']), 60)
        for c in self.fixtures['cases']:
            self.assertEqual(len(set(c['key'].values())), 10 if c['kind'] == 'base' else 9)
            self.assertEqual(set(''.join(c['train'][:7])), set('0123456789'))
            self.assertFalse(set(c['train_forms']) & set(c['held_forms']))
            self.assertFalse(set(c['train']) & set(c['held']))
            self.assertEqual(len(c['train_forms']), len(set(c['train_forms'])))
            for raw, form in zip(c['train']+c['held'], c['train_forms']+c['held_forms']):
                self.assertEqual(emit(raw, c['key']), form)
                self.assertIn(form, self.bank.reverse)
            for name in c['names']:
                self.assertNotIn(name['form'], self.bank.reverse)
                self.assertEqual(emit(name['raw'], c['key']), name['form'])
            self.assertGreaterEqual(sum(c['missing_digit'] not in w for w in c['train']), 7)
            self.assertTrue(any(c['missing_digit'] in w for w in c['held']))

    def test_certified_outputs_and_counterexamples_obey_contract(self):
        truth = {c['id']: c for c in self.fixtures['cases']}
        budgets = self.protocol['budgets']
        for c in self.result['cases']:
            self.assertEqual(c['states'], sum(q['states'] for q in c['queries']))
            self.assertLessEqual(c['states'], budgets['states_total_per_fit_and_transfers'])
            for q in c['queries']:
                self.assertLessEqual(q['states'], budgets['states_per_query'])
                if q['status'] == 'UNKNOWN':
                    self.assertIn(q['limit'], ('states', 'local_assignments'))
                if q['status'] == 'SAT':
                    self.assertTrue(all(emit(w, q['key']) in self.bank.reverse for w in c['train']))
            for row in c['held'] + c['names']:
                p = row['prediction']
                if p['form_certified']:
                    self.assertEqual(p['form'], emit(row['raw'], truth[c['id']]['key']))
                if p['chunks_certified']:
                    self.assertEqual(p['chunks'], [truth[c['id']]['key'][d] for d in row['raw']])
                if p['status'] == 'unknown_digits':
                    self.assertTrue(set(row['raw']) - set(''.join(c['train'])))
                    self.assertFalse(p['form_certified'])
                if p['status'] == 'ambiguous_form':
                    k = p['counterexample_key']
                    self.assertTrue(all(emit(w, k) in self.bank.reverse for w in c['train']))
                    self.assertNotEqual(emit(row['raw'], k), p['form'])
                    self.assertFalse(p['form_certified'])

    def test_baseline_cannot_use_truth_from_incomplete_enumeration(self):
        result = json.loads((ROOT/'results/round27_baseline.json').read_text())
        self.assertEqual(len(result['cases']), 30)
        for c in result['cases']:
            if c['enumeration']['complete']:
                self.assertTrue(c['true_key_in_enumeration'])
            else:
                self.assertTrue(all(not h['prediction']['form_certified'] for h in c['held']))


if __name__ == '__main__':
    unittest.main()
