import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from round36_experiment import decode_key
from round38_experiment import brute, canonical, segment_count


class AnchoredEnumeration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='469-r38-test-')
        cls.path = Path(cls.temp.name)
        cls.binary = cls.path/'enumerate'
        subprocess.run(['g++','-O2','-std=c++17',str(ROOT/'scripts/round38_enumerate.cpp'),'-o',str(cls.binary)],check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_case(self, groups, word, lexicon, anchor=0):
        lex = self.path/'lex';case = self.path/'case'
        lex.write_text('\n'.join(lexicon)+'\n')
        case.write_text(f'{len(groups)} {anchor} {word}\n'+'\n'.join(groups)+'\n')
        p = subprocess.run([str(self.binary),str(lex),str(case),'1'],capture_output=True,text=True,check=True)
        return json.loads(p.stdout)

    def test_repeated_digits_groups_and_unseen_digits(self):
        result = self.run_case(['01','01','010'],'AB',['AB','ABA'],1)
        self.assertTrue(result['complete'])
        self.assertEqual([decode_key(k) for k in result['keys']],[{'0':'A','1':'B'}])

    def test_variable_units_against_independent_whole_keys(self):
        for groups,word in [(['010','01'],'ABAAB'),(['012','202'],'ABAB')]:
            case = {'groups':groups,'anchor_index':0,'anchor_word':word,'lexicon':['ABAAB','ABA','AB','ABAB','AABB','BABA','AAA']}
            expected = brute(case)
            actual = self.run_case(groups,word,case['lexicon'])
            self.assertTrue(actual['complete'])
            self.assertEqual(actual['count'],len(expected))
            self.assertEqual({canonical(decode_key(k)) for k in actual['keys']},expected)
        self.assertGreater(self.run_case(['010','01'],'ABAAB',['ABAAB','ABA'])['count'],0)

    def test_empty_fit_and_invalid_input_are_different(self):
        zero = self.run_case(['010'],'AB',['AB'])
        self.assertTrue(zero['complete'])
        self.assertEqual(zero['count'],0)
        invalid = self.run_case(['X'],'AB',['AB'])
        self.assertFalse(invalid['complete'])
        self.assertIsNone(invalid['count'])

    def test_segmentation_counts_paths_without_inserting_letters(self):
        self.assertEqual(segment_count('AAAA',{'A','AA'}),5)
        self.assertEqual(segment_count('AB',{'A','AA'}),0)
        self.assertEqual(segment_count('AB',{'AB'}),1)


if __name__ == '__main__':
    unittest.main()
