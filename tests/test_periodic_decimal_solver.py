import itertools
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from periodic_decimal_solver import Codebook,Model,completions,positions

class PeriodicDecimalTests(unittest.TestCase):
    def test_key_sets_match_independent_brute_force(self):
        book=Codebook(['A','B','AB','BA','BAB','AA'],'ordinal1_compact')
        for reset in ('word','stream'):
            for feedback in (0,1):
                model=Model(book,2,reset,feedback); groups=model.encrypt(['AB','BAB'],(3,7))
                expected=[]
                for key in itertools.product(range(10),repeat=2):
                    if all(model.words(raw,key,*ctx) for raw,ctx in zip(groups,positions(groups))):expected.append(key)
                self.assertTrue(expected)
                actual=completions(model.solve(groups))
                self.assertEqual(sorted(actual),expected)

    def test_hand_checked_feedback_and_reset(self):
        book=Codebook(['A','B'],'ordinal1_compact')
        self.assertEqual(Model(book,2,'stream',1).encrypt(['A','B'],(3,7)),['4','3'])
        self.assertEqual(Model(book,2,'word',1).encrypt(['A','B'],(3,7)),['4','5'])
        self.assertEqual(Model(book,2,'stream',0).decrypt_digits('3',(3,7),1,4),'6')

    def test_held_group_needs_correct_offset_and_previous_ciphertext(self):
        model=Model(Codebook(['HELLO','WORLD'],'ordinal1_compact'),4,'stream',1)
        raw=model.encrypt(['HELLO','WORLD'],(3,4,7,8))
        self.assertEqual(model.words(raw[1],(3,4,7,8),len(raw[0]),int(raw[0][-1])),['WORLD'])

    def test_unspaced_key_retained_with_word_resets_and_feedback(self):
        for reset in ('word','stream'):
            model=Model(Codebook(['HELLO','WORLD','TEST'],'ordinal1_compact'),2,reset,1)
            raw=model.encrypt(['HELLO','WORLD','TEST'],(4,6))
            result=model.solve_unspaced([''.join(raw[:2]),raw[2]])
            self.assertTrue(result['complete']); self.assertIn((4,6),completions(result))
            self.assertEqual(model.segment(''.join(raw[:2]),(4,6))['unique_words'],['HELLO','WORLD'])

    def test_incomplete_and_unseen_phases_not_silently_completed(self):
        model=Model(Codebook(['A'],'ordinal1_compact'),8,'word',0)
        self.assertFalse(model.solve(['1'],node_limit=0)['complete'])
        result=model.solve(['1']); self.assertEqual(result['full_key_count'],10**7)
        self.assertIsNone(completions(result))

    def test_nonbijective_phase_assignments_are_allowed(self):
        model=Model(Codebook(['ABC'],'ordinal1_compact'),3,'word',0)
        self.assertIn((4,4,4),completions(model.solve(['567'])))

    def test_known_key_does_not_force_missing_words_into_lexicon(self):
        model=Model(Codebook(['A'],'ordinal1_compact'),1,'stream',0)
        self.assertEqual(model.words('2',(0,)),[])
        self.assertEqual(model.segment('2',(0,))['word_path_count'],0)

if __name__=='__main__':unittest.main()
