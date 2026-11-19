from collections import Counter
from itertools import combinations
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from round25_name_structure import FAMILIES, evaluate, sample_null, shared_nonidentical, signature, signature_map


class Round25StructureTests(unittest.TestCase):
    def test_selected_pairs_require_different_restricted_operations(self):
        self.assertEqual(signature('3478','pair_mirror'),signature('4378','pair_mirror'))
        self.assertNotEqual(signature('345','pair_mirror'),signature('453','pair_mirror'))
        self.assertEqual(signature('345','cyclic_rotation'),signature('453','cyclic_rotation'))
        self.assertNotEqual(signature('3478','cyclic_rotation'),signature('4378','cyclic_rotation'))

    def test_padding_does_not_equate_different_original_lengths(self):
        for family in FAMILIES:
            self.assertNotEqual(signature('123',family),signature('0123',family))

    def test_exact_copies_and_multiple_variants_do_not_inflate_score(self):
        a = signature_map(['123','123','231'],'whole_anagram')
        b = signature_map(['123','312'],'whole_anagram')
        self.assertEqual(len(shared_nonidentical(a,b)),1)
        self.assertEqual(shared_nonidentical(signature_map(['123'],'identity'),signature_map(['123'],'identity')), {})

    def test_digit_pool_preserves_cluster_counts_and_slot_lengths(self):
        clusters={'a':['1123','456'], 'b':['987','987','11000']}
        changed=sample_null(clusters,'cluster_digit_pool',random.Random(23))
        for key in clusters:
            self.assertEqual(Counter(''.join(clusters[key])),Counter(''.join(changed[key])))
            self.assertEqual(list(map(len,clusters[key])),list(map(len,changed[key])))

    def test_relabeling_preserves_all_equality_relations_within_cluster(self):
        clusters={'a':['1123','456','1123'], 'b':['987','11000']}
        changed=sample_null(clusters,'cluster_digit_relabel',random.Random(24))
        for key in clusters:
            old,new=''.join(clusters[key]),''.join(changed[key])
            for i in range(len(old)):
                for j in range(len(old)):
                    self.assertEqual(old[i]==old[j],new[i]==new[j])

    def test_group_reassignment_preserves_global_words_and_local_lengths(self):
        clusters={'a':['123','1234','456'], 'b':['789','7654','123']}
        changed=sample_null(clusters,'whole_group_reassignment',random.Random(25))
        self.assertEqual(Counter(w for g in clusters.values() for w in g), Counter(w for g in changed.values() for w in g))
        for key in clusters:
            self.assertEqual(list(map(len,clusters[key])),list(map(len,changed[key])))

    def test_max_statistic_matches_independent_pair_enumeration(self):
        rng=random.Random(26)
        for _ in range(30):
            clusters={k:[''.join(rng.choice('123') for _ in range(3)) for _ in range(3)] for k in ('avar','knightmare','third')}
            maximum=0
            for family in FAMILIES:
                for a,b in combinations(clusters,2):
                    hits={signature(x,family) for x in clusters[a] for y in clusters[b]
                          if x!=y and signature(x,family)==signature(y,family)}
                    maximum=max(maximum,len(hits))
            self.assertEqual(evaluate(clusters)[0]['maximum_all_pairs_families'],maximum)


if __name__ == '__main__':
    unittest.main()
