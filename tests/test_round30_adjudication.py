import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from round30_adjudicate import ROOT,adjudicate,qualifies,build


class Round30Adjudication(unittest.TestCase):
    def test_unknown_or_partial_evidence_cannot_pass(self):
        self.assertFalse(qualifies({'decoder':'met','attestation':'not_established'},['decoder','attestation']))
        self.assertFalse(qualifies({'decoder':'met','attestation':'contradicted'},['decoder','attestation']))
        with self.assertRaises(ValueError):qualifies({'decoder':True},['decoder'])
        with self.assertRaises(ValueError):qualifies({'decoder':'met'},['decoder','attestation'])

    def test_text_and_nontext_scopes_are_not_collapsed(self):
        fixture={'translation_requirements':['a'],'nontext_requirements':['b'],
                 'candidate_families':[{'id':'x','requirements':{'a':'met'}}],
                 'nontext_claims':[{'id':'y','requirements':{'b':'met'}}]}
        self.assertEqual(adjudicate(fixture)['mission_outcome'],'T_and_G_require_separate_scopes')
        fixture['nontext_claims'][0]['requirements']['b']='not_established'
        self.assertEqual(adjudicate(fixture)['mission_outcome'],'T_scoped')

    def test_current_claims_preserve_inconclusive_status_and_unfinished_fit(self):
        result=build()
        self.assertEqual(result['mission_outcome'],'I_inconclusive')
        self.assertFalse(result['translation_mission_closed'])
        self.assertEqual(result['pending_prior_main_fits'],[{'source':'knightmare','family':'grapheme1_3','returned_lexical_keys':1769,'status':'bounded_search_not_exhaustive'}])


if __name__=='__main__':unittest.main()
