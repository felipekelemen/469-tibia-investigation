import copy,pathlib,sys,unittest,tempfile,contextlib,io
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import copied_v3_gate as g3
import copied_v4_gate as g4
import qualified_tibia_v3 as q3
import qualified_tibia_v4 as q4
class CopiedGateTests(unittest.TestCase):
    def fixture(self):
        p={'modes':['copied_static_codes','copied_fresh_homophones','ordinary'],'fixtures_per_mode':30,'holdout_letters':100,
          'gate':{'minimum_holdout_character_accuracy':.95,'minimum_pass_count':27}}
        rows=[{'scenario':{'codes':99,'distribution':m},'fixture':i,'holdout_letters':100,'correct_holdout_letters':95 if i<27 else 94,
          'character_accuracy':.95 if i<27 else .94,'known_key_exact':True} for m in p['modes'] for i in range(30)]
        return p,{'complete':True,'frozen_protocol':copy.deepcopy(p),'trials':rows}
    def test_exact_gate_and_one_missing_success(self):
        for module in [g3,g4]:
            p,r=self.fixture();self.assertTrue(module.evaluate(r,p)['gate_passed'])
            r['trials'][26].update(correct_holdout_letters=94,character_accuracy=.94)
            r['overall_gate_passes']=True
            self.assertFalse(module.evaluate(r,p)['gate_passed'])
    def test_duplicate_or_invalid_positive_cannot_open_gate(self):
        p,r=self.fixture();r['trials'][-1]=copy.deepcopy(r['trials'][-2])
        with self.assertRaises(ValueError):g4.evaluate(r,p)
        p,r=self.fixture();r['trials'][0]['known_key_exact']=False
        with self.assertRaises(ValueError):g4.evaluate(r,p)
    def test_gate_failure_prevents_corpus_read_and_fit(self):
        for module in [q3,q4]:
            with tempfile.TemporaryDirectory() as d:
                root=pathlib.Path(d);(root/'results').mkdir()
                with patch.object(module,'ROOT',root),patch.object(module,'assess',return_value={'gate_passed':False}),patch.object(module,'fit',side_effect=AssertionError('forbidden')) as fitter,contextlib.redirect_stdout(io.StringIO()):
                    module.run();fitter.assert_not_called()
                self.assertFalse((root/'data').exists())
if __name__=='__main__':unittest.main()
