import pathlib,sys,unittest,tempfile,contextlib,io,json
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import qualified_tibia_search as q
class SearchGuardTests(unittest.TestCase):
    def test_failed_qualification_never_reads_game_data_or_fits(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);(root/'results').mkdir()
            # No corpus exists in this root: a premature read would fail this test.
            with patch.object(q,'ROOT',root),patch.object(q,'assess',return_value={'gate_passed':False}),patch.object(q,'fit',side_effect=AssertionError('forbidden fit')) as fitter,contextlib.redirect_stdout(io.StringIO()):
                q.run();fitter.assert_not_called()
            self.assertFalse((root/'data').exists())
            self.assertEqual(json.loads((root/'results/p04_gate_v2.json').read_text()),{'gate_passed':False})
if __name__=='__main__':unittest.main()
