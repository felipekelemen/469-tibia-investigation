import pathlib,sys,unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from fast_homophonic import solve,delta_score
class IncrementalSolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table=np.random.default_rng(139).normal(-5,1,26**4)
    def full(self,seqs,mapping):
        s=0
        for seq in seqs:
            chars=[mapping[c] for c in seq]
            for i in range(len(chars)-3):
                a,b,c,d=chars[i:i+4];s+=self.table[((a*26+b)*26+c)*26+d]
        return s
    def test_delta_matches_independent_full_score(self):
        rng=np.random.default_rng(871)
        seqs=[rng.integers(0,8,150).tolist(),[1,1,1,1,1,1],rng.integers(0,8,29).tolist(),[3,2]]
        mapping=rng.integers(0,26,8).tolist()
        for code in range(8):
            newletter=int(rng.integers(0,26));changed=mapping.copy();changed[code]=newletter
            expected=self.full(seqs,changed)-self.full(seqs,mapping)
            self.assertAlmostEqual(delta_score(seqs,self.table,mapping,code,newletter),expected,places=8)
    def test_sequence_boundaries_and_fullscore_audit(self):
        seqs=[[0,1,0,1,2],[2,2,2,2],[1,0]]
        result=solve(seqs,self.table,seed=90,restarts=2,steps=1200,num_codes=4)
        self.assertEqual(result['scored_tetragrams'],3)
        self.assertAlmostEqual(result['train_score'],self.full(seqs,result['mapping'])/3,places=10)
        self.assertLess(result['incremental_score_drift'],1e-6)
    def test_determinism_and_unseen_code_slots(self):
        seqs=[[0,2,0,2,0,2,0,2]]
        args=dict(seed=400,restarts=2,steps=300,num_codes=100)
        a=solve(seqs,self.table,**args);b=solve(seqs,self.table,**args)
        self.assertEqual(a['mapping'],b['mapping']);self.assertEqual(a['train_score'],b['train_score'])
        self.assertEqual(len(a['mapping']),100)
    def test_invalid_or_no_evidence_inputs_rejected(self):
        for seqs in [[],[[0,1,2]],[[0,-1,2,3]],[[0,1.5,2,3]],[[0,1,2,100000000000]]]:
            with self.assertRaises(ValueError):solve(seqs,self.table,steps=10,restarts=1)
if __name__=='__main__':unittest.main()
