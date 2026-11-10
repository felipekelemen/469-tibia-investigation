import pathlib,sys,unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from robust_homophonic import solve
from fast_homophonic import solve as solve_v1
class RobustSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.table=np.random.default_rng(61).normal(-5,1,26**4)
    def test_bank_zero_reproduces_single_search(self):
        seqs=[[0,1,2,0,3,1,2,3]*4]
        kw={'seed':17,'restarts':1,'steps':400,'num_codes':4}
        a=solve(seqs,self.table,banks=2,**kw);b=solve_v1(seqs,self.table,**kw)
        self.assertEqual(a['banks'][0]['mapping'],b['mapping'])
        self.assertEqual(a['banks'][0]['objective'],b['objective'])
    def test_winner_uses_independent_training_objective(self):
        seqs=[[0,1,2,0,1,3]*6,[3,0,3,1,3,2]*4]
        r=solve(seqs,self.table,seed=99,banks=2,restarts=1,steps=300,num_codes=4)
        counts=np.bincount(np.concatenate(seqs),minlength=4);n=sum(map(len,seqs))
        weights=10**self.table;expected=weights.reshape(26,-1).sum(axis=1)/weights.sum()
        values=[]
        for b in r['banks']:
            mapping=b['mapping'];raw=0
            for seq in seqs:
                x=[mapping[c] for c in seq]
                for i in range(len(x)-3):
                    a,c,d,e=x[i:i+4];raw+=self.table[((a*26+c)*26+d)*26+e]
            observed=np.bincount(mapping,weights=counts,minlength=26)
            obj=raw-2*np.sum((observed-n*expected)**2/(n*expected+5))
            self.assertAlmostEqual(obj,b['objective'],places=7);values.append(obj)
        self.assertEqual(r['selected_bank'],int(np.argmax(values)))
    def test_no_search_banks_rejected(self):
        with self.assertRaises(ValueError):solve([[0,0,0,0]],self.table,banks=0)
if __name__=='__main__':unittest.main()
