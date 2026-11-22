"""Leakage, exact-enumeration and reporting contracts for frozen round28 data."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from round28_certificates import independent_decode
from round28_experiment import verify_inputs, source_inputs
from run_round28 import check_nulls


class Round28Artifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads((ROOT/'data/round28_fixtures.json').read_text())
        cls.qualification = json.loads((ROOT/'results/round28_qualification.json').read_text())
        cls.targets = json.loads((ROOT/'results/round28_targets.json').read_text())

    def test_input_hashes_and_source_window_nonoverlap(self):
        verify_inputs()
        used = {}
        for row in self.fixtures['windows']:
            existing = used.setdefault(row['source'], set())
            positions = set(range(row['start_word'], row['end_word']))
            self.assertFalse(existing & positions)
            existing.update(positions)
        counts = Counter((r['profile'], r['author']) for r in self.fixtures['windows'])
        self.assertEqual(len(counts), 6)
        self.assertEqual(set(counts.values()), {15})
        for source in json.loads((ROOT/'data/round28_reference/SOURCES.json').read_text()):
            self.assertEqual(hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest(), source['sha256'])

    def test_truth_and_held_predictions_by_independent_arithmetic(self):
        by_id = {c['id']: c for c in self.qualification['cases']}
        self.assertEqual(len(by_id), 540)
        for fixture in self.fixtures['cases']:
            result = by_id[fixture['id']]
            self.assertIn(fixture['key'], result['fit']['keys'])
            self.assertEqual(result['fit']['keys_examined'], 312)
            for stage in ('train', 'held'):
                literal = ''.join(independent_decode(raw, fixture['codec'], fixture['key'])
                                  for raw in fixture[stage]).replace(' ', '')
                self.assertEqual(literal, ''.join(fixture[stage+'_words']))
            certified = result['prediction']['certified'] or '?'*len(result['held_truth'])
            for c, t in zip(certified, result['held_truth']):
                if c != '?':
                    self.assertEqual(c, t)
            if result['prediction']['unique_words'] is not None:
                self.assertEqual(result['prediction']['unique_words'], fixture['held_words'])

    def test_qualification_gates_are_per_cell_not_pooled(self):
        cells = {}
        for row in self.qualification['cases']:
            cells.setdefault((row['profile'], row['codec'], row['framing']), []).append(row)
        self.assertEqual(len(cells), 18)
        for summary in self.qualification['summary']:
            rows = cells[(summary['profile'], summary['codec'], summary['framing'])]
            self.assertEqual(len(rows), 30)
            passed = sum(r['certified_letter_accuracy'] >= 0.95 and r['certified_wrong_letters'] == 0 for r in rows)
            self.assertEqual(passed, summary['cases_passing_letter_gate'])
            self.assertEqual(summary['known_family_letter_qualified'], passed >= 27 and not any(r['certified_wrong_letters'] for r in rows))

    def test_nulls_repeat_all_models_and_preserve_declared_properties(self):
        nulls = json.loads((ROOT/'results/round28_nulls.json').read_text())
        books = json.loads((ROOT/'data/normalized_books.json').read_text())
        check_nulls(nulls, source_inputs(), books,
                    self.targets['full_source_search']['maximum_fully_lexical_sources_one_config'])

    def test_candidate_catalogue_contains_every_full_source_key(self):
        expected = {(name, s['codec'], s['framing'], tuple(k))
                    for name, models in self.targets['full_source_search']['sources'].items()
                    for s in models for k in s['keys']}
        actual = {(r['source'], r['codec'], r['framing'], tuple(r['key']))
                  for r in self.targets['lexical_candidates']}
        self.assertEqual(expected, actual)
        self.assertFalse(self.targets['translation_validated'])


if __name__ == '__main__':
    unittest.main()
