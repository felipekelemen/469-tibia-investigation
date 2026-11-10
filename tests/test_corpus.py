"""Meaningful invariants for extraction, lossless roundtrip and leakage masking."""
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_corpus import align_omissions, novel_fragments, shared_components

class CorpusTests(unittest.TestCase):
    def test_zero_omission_is_lossless_for_every_book(self):
        records=json.loads((ROOT/'data/normalized_books.json').read_text())
        self.assertEqual(len(records),70)
        self.assertEqual(sum(len(r['symbols']) for r in records),5729)
        for r in records:
            omitted=set(r['omitted_zero_code_indices'])
            self.assertTrue(all(r['codes'][i].startswith('0') for i in omitted))
            actual=''.join(c[1:] if i in omitted else c for i,c in enumerate(r['codes']))
            self.assertEqual(actual,r['digits'])
        self.assertEqual(sum(len(r['omitted_zero_code_indices']) for r in records),195)

    def test_alignment_rejects_nonzero_deletion(self):
        self.assertEqual(align_omissions('123',['12','34']),(None,0))
        self.assertEqual(align_omissions('123',['01','23']),((0,),1))
        self.assertEqual(align_omissions('000',['00','00'])[1],2)

    def test_components_include_transitive_reuse(self):
        self.assertEqual(shared_components(['abcd','cdef','efgh','zzzz'],2),[[0,1,2],[3]])

    def test_fragment_mask_removes_shared_context(self):
        strings=['ABCDE12345','ABCDEqqqqq12345rrrrr']
        fs=novel_fragments(strings,[0],[1],5)
        self.assertEqual([f['digits'] for f in fs],['qqqqq','rrrrr'])

    def test_reported_book_split_has_no_shared_16grams(self):
        books=json.loads((ROOT/'data/normalized_books.json').read_text())
        split=json.loads((ROOT/'data/normalized_splits.json').read_text())
        def grams(ids):
            return {r['digits'][i:i+16] for r in books if r['id'] in ids
                    for i in range(len(r['digits'])-15)}
        self.assertFalse(grams(split['discovery_book_ids']) & grams(split['holdout_book_ids']))
        self.assertTrue(split['holdout_book_ids'])

    def test_fragment_split_has_no_shared_12grams(self):
        books=json.loads((ROOT/'data/normalized_books.json').read_text())
        protocol=json.loads((ROOT/'data/normalized_splits.json').read_text())['fragment_protocol']
        train={r['digits'][i:i+12] for r in books if r['id'] in protocol['discovery_book_ids']
               for i in range(len(r['digits'])-11)}
        for f in protocol['eligible_fragments']:
            self.assertFalse(train & {f['digits'][i:i+12] for i in range(len(f['digits'])-11)})

if __name__ == '__main__':
    unittest.main()
