from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from round30_audit import alignments,corpus,integrity,verify_inputs


class Round30Audit(unittest.TestCase):
    def test_forward_alignment_counts_ambiguity_without_selecting_path(self):
        self.assertEqual(alignments('000',['00','00']),2)
        self.assertEqual(alignments('00',['00','00']),1)
        self.assertEqual(alignments('01',['01']),1)
        self.assertEqual(alignments('1',['01']),1)

    def test_only_leading_zero_omission_is_allowed(self):
        for raw,codes in [('2',['12']),('1',['10']),('12',['01']),('01',['11'])]:
            self.assertEqual(alignments(raw,codes),0)
        with self.assertRaises(ValueError):alignments('1',['1'])

    def test_packaged_sources_reconstruct_all_books(self):
        r=corpus()
        self.assertEqual((r['books'],r['digits'],r['imported_symbols']),(70,11263,5729))
        self.assertEqual(r['omitted_leading_zeros'],195)
        self.assertEqual(len(r['ambiguous_alignment_book_ids']),9)

    def test_frozen_closure_inputs(self):
        verify_inputs()

    def test_manifest_audit_accounts_for_every_reference(self):
        r=integrity()
        self.assertEqual(sum(r['statuses'].values()),r['reference_count'])
        self.assertEqual(r['reference_count'],sum(len(m['checks']) for m in r['manifests']))
        for m in r['manifests']:
            for c in m['checks']:
                self.assertEqual(c['status']=='match',c['expected']==c['actual'])


if __name__=='__main__':unittest.main()
