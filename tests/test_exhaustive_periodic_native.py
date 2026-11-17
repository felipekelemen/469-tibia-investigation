import itertools
from pathlib import Path
import random
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from exhaustive_periodic_native import run_native
from periodic_decimal_solver import Codebook,Model,completions,positions
from periodic_decimal_fast import fast_segment
from target_decimal_solver import encode

class NativeExhaustiveTests(unittest.TestCase):
    def test_matches_independent_full_key_enumeration(self):
        words=['A','I','AN','AND','AA','IT','IN','TO','ON','THE']
        for codec in ('ordinal0_compact','ordinal1_compact'):
            book=Codebook(words,codec);tasks=[];truth=[]
            for p in (1,2,3):
                for feedback in (0,1):
                    model=Model(book,p,'stream',feedback);key=tuple(range(p))
                    raw=model.encrypt(['AND','THE','IT'],key);groups=[''.join(raw[:2]),raw[2]]
                    tasks.append({'id':f'p{p}f{feedback}','period':p,'feedback':feedback,'groups':groups})
                    candidates=[]
                    for k in itertools.product(range(10),repeat=p):
                        if all(fast_segment(model,g,k,*ctx)['word_path_count'] for g,ctx in zip(groups,positions(groups))):
                            candidates.append(''.join(map(str,k)))
                    truth.append(candidates)
            for row,expected in zip(run_native(book.reverse,tasks),truth):
                self.assertEqual(row['keys'],expected)
                self.assertEqual(row['domain_keys'],row['checked_keys']+row['prefix_pruned_keys'])

    def test_matches_frozen_python_search_with_later_shorter_fragment(self):
        rng=random.Random(2222)
        for codec in ('ordinal0_compact','ordinal1_compact'):
            book=Codebook(['HELLO','WORLD','TEST','AND','A','I'],codec);tasks=[];expected=[]
            for p in (4,6,7,8):
                for feedback in (0,1):
                    model=Model(book,p,'stream',feedback);key=tuple(rng.randrange(10) for _ in range(p))
                    raw=model.encrypt(['HELLO','WORLD','AND','TEST'],key);groups=[''.join(raw[:3]),raw[3]]
                    fit=model.solve_unspaced(groups,node_limit=200000,solution_limit=20000)
                    self.assertTrue(fit['complete'])
                    expected.append(sorted(''.join(map(str,k)) for k in completions(fit,20000)))
                    tasks.append({'id':f'p{p}f{feedback}','period':p,'feedback':feedback,'groups':groups})
            for row,keys in zip(run_native(book.reverse,tasks),expected):self.assertEqual(row['keys'],keys)

    def test_multiple_word_segmentations_do_not_duplicate_keys(self):
        rows=run_native(['1','11'],[{'id':'ambiguous','period':2,'feedback':0,'groups':['11','11']}])
        self.assertEqual(rows[0]['keys'],['00'])
        self.assertEqual(rows[0]['selected_fragment'],0)

    def test_dictionary_prefix_is_not_a_complete_word(self):
        rows=run_native(['1234'],[{'id':'prefix','period':2,'feedback':0,'groups':['12','34']}])
        self.assertEqual(rows[0]['keys'],[])

    def test_empty_domain_and_leading_zero_keys(self):
        rows=run_native(['01'],[{'id':'zero','period':2,'feedback':0,'groups':['01','01']}])
        self.assertEqual(rows[0]['keys'],['00'])
        self.assertEqual(rows[0]['checked_keys'],1)
        self.assertEqual(rows[0]['prefix_pruned_keys'],99)

if __name__=='__main__':unittest.main()
