import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from round33_experiment import compile_engine,run_case,brute_count


class ExactCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='469-r33-tests-')
        cls.binary=compile_engine(cls.temp.name)
        cls.budgets={'per_fit_wall_seconds':10,'per_fit_address_space_bytes':3221225472}

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def count(self,words,lexicon,forced=None):
        path=Path(self.temp.name)/'lex.txt';path.write_text('\n'.join(lexicon)+'\n')
        out=run_case(self.binary,path,{'words':words,'forced':forced or {}},self.temp.name,self.budgets)
        self.assertTrue(out['complete'],out)
        return out

    def test_independent_whole_key_enumeration(self):
        cases=[(['01','110','2'],['A','B','AB','BA','AAA','ABB','BAA']),
               (['012','20','00'],['ABA','BAB','AAAA','BBB','BA','AA']),
               (['010','101'],['ABA','BAB','AAAAAA','BBBBBB'])]
        for words,lex in cases:self.assertEqual(int(self.count(words,lex)['count']),brute_count(words,lex))

    def test_disconnected_private_variables_multiply(self):
        self.assertEqual(self.count(['0','1'],['A','B'])['count'],'4')

    def test_shared_repeated_digit_is_one_assignment(self):
        self.assertEqual(self.count(['00'],['AA','BB','AB'])['count'],'2')

    def test_homophones_are_allowed(self):
        self.assertEqual(self.count(['01'],['AA'])['count'],'1')

    def test_unseen_digits_not_counted(self):
        out=self.count(['3'],['A','B']);self.assertEqual(out['count'],'2');self.assertEqual(out['observed_mask'],8)

    def test_duplicate_forms_and_groups_do_not_multiply(self):
        self.assertEqual(self.count(['0','0'],['A','A','B'])['count'],'2')

    def test_impossible_and_forced_forms(self):
        self.assertEqual(self.count(['00'],['AB'])['count'],'0')
        self.assertEqual(self.count(['01'],['AB','BA'],{'01':'AB'})['count'],'1')
        self.assertEqual(self.count(['01'],['AB','BA'],{'01':'AA'})['count'],'0')


if __name__=='__main__':unittest.main()
