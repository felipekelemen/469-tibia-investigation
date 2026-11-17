from pathlib import Path
import random
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from periodic_decimal_solver import CODECS,Codebook,Model
from periodic_decimal_fast import fast_segment

class FastSegmentEquivalenceTests(unittest.TestCase):
    def test_reference_equivalence_across_all_models_and_perturbations(self):
        rng=random.Random(21001)
        vocabulary=['A','I','AN','AND','THE','HELLO','WORLD','TEST','IN','ON','AT','AS','TO','IT','IS','ME','MY']
        for codec in CODECS:
            book=Codebook(vocabulary,codec)
            for period in range(1,9):
                key=tuple(rng.randrange(10) for _ in range(period))
                for reset in ('word','stream'):
                    for fb in (0,1):
                        model=Model(book,period,reset,fb)
                        groups=model.encrypt(['HELLO','WORLD','AND','THE','TEST'],key)
                        raw=''.join(groups[1:]);offset=len(groups[0]);previous=int(groups[0][-1])
                        shuffled=list(raw);rng.shuffle(shuffled)
                        for target in (raw,''.join(shuffled),raw[:-1],''):
                            self.assertEqual(fast_segment(model,target,key,offset,previous),model.segment(target,key,offset,previous))

    def test_ambiguous_word_paths_are_not_collapsed(self):
        model=Model(Codebook(['A','AA'],'ordinal1_compact'),1,'word',0)
        self.assertEqual(fast_segment(model,'111',(0,)),model.segment('111',(0,)))
        self.assertEqual(fast_segment(model,'111',(0,))['word_path_count'],3)
        self.assertIsNone(fast_segment(model,'111',(0,))['unique_words'])

if __name__=='__main__':unittest.main()
