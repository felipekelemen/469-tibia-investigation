from pathlib import Path
import random
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from periodic_decimal_solver import CODECS,Codebook,Model
from periodic_decimal_vectorized import fast_unspaced

class VectorizedPrefixTests(unittest.TestCase):
    def test_reference_search_equivalence_including_order_sensitive_caps(self):
        rng=random.Random(21111)
        for codec in CODECS:
            book=Codebook(['A','I','AN','AND','HELLO','WORLD','THE','TEST','IN','IT','IS','TO','ON','AA'],codec)
            for period in range(1,9):
                key=tuple(rng.randrange(10) for _ in range(period))
                for reset in ('word','stream'):
                    for fb in (0,1):
                        model=Model(book,period,reset,fb)
                        raw=model.encrypt(['HELLO','AND','THE','WORLD'],key)
                        groups=[''.join(raw[:2]),''.join(raw[2:])]
                        changed=groups[:];changed[1]=changed[1][::-1]
                        for target in (groups,changed):
                            for nodes,keys in ((3,2),(2000,2000)):
                                self.assertEqual(fast_unspaced(model,target,nodes,keys),model.solve_unspaced(target,nodes,keys))

if __name__=='__main__':unittest.main()
