from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from hidden_unit_diagnostics import equal_mdl_lexicons
from numeric_word_codec import complete_parse


class HiddenUnitIdentifiabilityTests(unittest.TestCase):
    def test_two_same_size_prefix_codes_have_equal_cost_and_different_cuts(self):
        c = equal_mdl_lexicons()
        self.assertEqual(len(c['dictionary_A']), 64)
        self.assertEqual(len(c['dictionary_B']), 64)
        self.assertTrue(c['A_decodability']['prefix_free'])
        self.assertTrue(c['B_decodability']['prefix_free'])
        self.assertTrue(all(3 <= len(w) <= 8 for w in c['dictionary_A']+c['dictionary_B']))
        self.assertEqual(set(c['A_unit_counts'].values()), {35})
        self.assertEqual(set(c['B_unit_counts'].values()), {35})
        self.assertEqual(c['A_mdl_objective'], c['B_mdl_objective'])
        row = c['same_raw_different_cuts']
        self.assertEqual(row['A']['count'], 1)
        self.assertEqual(row['B']['count'], 1)
        self.assertNotEqual(row['A']['unique_path'], row['B']['unique_path'])
        self.assertEqual(c['new_combination']['A']['count'], 1)
        self.assertEqual(c['new_combination']['B']['count'], 0)

    def test_all_observed_training_messages_have_same_true_unit_count_in_both_models(self):
        c = equal_mdl_lexicons()
        self.assertEqual(len(c['training_raw']), 70)
        for raw in c['training_raw']:
            for key in (c['dictionary_A'], c['dictionary_B']):
                result = complete_parse(raw, key)
                self.assertEqual(result['count'], 1)
                self.assertEqual(len(result['unique_path']), 32)
                self.assertEqual(''.join(result['unique_path']), raw)


if __name__ == '__main__':
    unittest.main()
