import itertools
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORDS=['3478','67','90871','97664','3466','0','345']


class IndependentContractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='469-r33-independent-test-')
        cls.binary=Path(cls.tmp.name)/'audit'
        subprocess.run(['g++','-O2','-std=c++17',str(ROOT/'scripts/round33_independent.cpp'),'-o',str(cls.binary)],check=True,capture_output=True)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_whole_key_length_enumeration(self):
        digits=sorted(set(''.join(WORDS)))
        for maximum in [5,7]:
            lex={'A'*n for n in range(1,maximum+1)}
            expected=sum(all(sum(dict(zip(digits,lengths))[d] for d in w)<=maximum for w in WORDS) for lengths in itertools.product(range(1,4),repeat=len(digits)))
            path=Path(self.tmp.name)/'lex';path.write_text('\n'.join(sorted(lex))+'\n')
            out=json.loads(subprocess.check_output([str(self.binary),str(path)],text=True))
            self.assertEqual(int(out['count']),expected)

    def test_zero_local_domain(self):
        path=Path(self.tmp.name)/'lex';path.write_text('A\nB\n')
        out=json.loads(subprocess.check_output([str(self.binary),str(path)],text=True))
        self.assertEqual(out['count'],'0')


if __name__=='__main__':unittest.main()
