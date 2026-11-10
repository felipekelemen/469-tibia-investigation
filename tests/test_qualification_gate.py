import copy,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from qualification_gate import evaluate
class QualificationGateTests(unittest.TestCase):
    def fixture(self):
        p={'scenarios':[{'codes':99,'distribution':'skewed'}],'fixtures_per_scenario':30,'holdout_letters':100,
           'gate':{'minimum_holdout_character_accuracy':.95,'minimum_pass_count':27}}
        trials=[{'scenario':p['scenarios'][0],'fixture':i,'holdout_letters':100,'correct_holdout_letters':95,'character_accuracy':.95} for i in range(30)]
        return p,{'complete':True,'frozen_protocol':copy.deepcopy(p),'trials':trials}
    def test_exact_preregistered_boundary(self):
        p,r=self.fixture()
        for row in r['trials'][27:]:row.update(correct_holdout_letters=94,character_accuracy=.94)
        self.assertTrue(evaluate(r,p)['gate_passed'])
        r['trials'][26].update(correct_holdout_letters=94,character_accuracy=.94)
        r['overall_gate_passes']=True
        self.assertFalse(evaluate(r,p)['gate_passed'])
    def test_incomplete_or_duplicated_trials_fail_closed(self):
        p,r=self.fixture();r['complete']=False
        with self.assertRaises(ValueError):evaluate(r,p)
        r['complete']=True;r['trials'][-1]=copy.deepcopy(r['trials'][0])
        with self.assertRaises(ValueError):evaluate(r,p)
    def test_false_accuracy_cannot_open_gate(self):
        p,r=self.fixture();r['trials'][0]['correct_holdout_letters']=20
        with self.assertRaises(ValueError):evaluate(r,p)
if __name__=='__main__':unittest.main()
