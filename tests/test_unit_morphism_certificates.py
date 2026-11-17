import itertools
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from round23_certificate_audit import assignments,independent_fixed_fit
from unit_morphism_lexicon import Bank
from unit_morphism_solver import solve,word_extensions,key_tuple

class IndependentUnitCertificateTests(unittest.TestCase):
    def test_length_vectors_agree_with_recursive_enumerator(self):
        forms=[''.join(x) for n in range(1,7) for x in itertools.product('AB',repeat=n)]
        for raw in ('00','01','010','011','012'):
            scalar=set(assignments(raw,forms,1,2))
            recursive={key_tuple(k) for f in forms for k in word_extensions(raw,f,1,2)}
            self.assertEqual(scalar,recursive)

    def test_fixed_join_preserves_all_keys(self):
        b=Bank('digraph',{f:{f} for f in ('ABAB','ABCD','CDAB','CDCD','AB','CD')},{})
        words=['01','0','00']
        self.assertEqual(independent_fixed_fit(words,b),[key_tuple(k) for k in solve(words,b)['keys']])

if __name__=='__main__':unittest.main()
