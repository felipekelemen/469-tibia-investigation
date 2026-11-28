import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from round36_experiment import GROUPS, brute, check_witnesses


class ExactAnchorChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='469-r36-test-')
        cls.path = Path(cls.temp.name)
        cls.binary = cls.path / 'anchors'
        subprocess.run(['g++','-O2','-std=c++17',str(ROOT/'scripts/round36_anchors.cpp'),
                        '-o',str(cls.binary)],check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_case(self, case):
        lex = self.path / 'lexicon'
        lex.write_text('\n'.join(case['lexicon'])+'\n')
        p = subprocess.run([str(self.binary),str(lex),*case['groups']],
                           check=True,capture_output=True,text=True)
        return json.loads(p.stdout)

    def test_variable_emissions_counts_and_message_variation_against_bruteforce(self):
        fixtures = json.loads((ROOT/'data/round36_fixtures.json').read_text())
        for index in [0,30]:
            case = fixtures['tiny'][index]
            expected = brute(case)
            actual = self.run_case(case)
            self.assertTrue(actual['complete'])
            self.assertGreater(expected['count'],0)
            self.assertEqual(int(actual['count']),expected['count'])
            for a,b in zip(actual['marginals'],expected['marginals']):
                self.assertEqual({r[0]:(int(r[1]),r[3] is not None) for r in a['rows']},b)
            self.assertGreater(check_witnesses(actual,case['groups'],set(case['lexicon'])),0)

    def test_reject_same_scope_with_invalid_length(self):
        groups = GROUPS.copy()
        groups[5] = '00'
        actual = self.run_case({'groups':groups,'lexicon':['A','AA']})
        self.assertFalse(actual['complete'])
        self.assertIsNone(actual['count'])
        self.assertEqual(actual['reason'],'unsupported_topology')

    def test_empty_model_is_complete_zero_not_limit(self):
        actual = self.run_case({'groups':GROUPS,'lexicon':['A']})
        self.assertTrue(actual['complete'])
        self.assertEqual(actual['count'],'0')
        self.assertTrue(all(not g['rows'] for g in actual['marginals']))


if __name__ == '__main__':
    unittest.main()
