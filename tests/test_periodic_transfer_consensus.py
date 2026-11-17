from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from periodic_decimal_solver import Codebook,Model
from periodic_decimal_experiment import spaced_transfer

class PeriodicConsensusTests(unittest.TestCase):
    def setUp(self):
        self.model=Model(Codebook(['A'],'ordinal1_compact'),1,'word',0)
        self.models={self.model.name:self.model}

    def test_out_of_dictionary_key_blocks_apparent_consensus(self):
        fits={self.model.name:{'complete':True,'keys':[[0],[1]],'full_key_count':2}}
        pred=spaced_transfer(['1'],fits,self.models)
        self.assertEqual(pred['possible_words'],[['A']])
        self.assertEqual(pred['empty_predictions'],[1])
        self.assertEqual(pred['strict_consensus'],[None])

    def test_no_key_is_not_vacuous_agreement(self):
        fits={self.model.name:{'complete':True,'keys':[],'full_key_count':0}}
        self.assertEqual(spaced_transfer(['1'],fits,self.models)['strict_consensus'],[None])

    def test_truncated_search_blocks_unique_claim(self):
        fits={self.model.name:{'complete':False,'keys':[[0]],'full_key_count':1}}
        pred=spaced_transfer(['1'],fits,self.models)
        self.assertEqual(pred['strict_consensus'],[None])
        self.assertEqual(pred['incomplete_models'],[self.model.name])

if __name__=='__main__':unittest.main()
