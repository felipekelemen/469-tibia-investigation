import itertools
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from context_constraint_solver import (FrameParser, KeySet, ResourceLimit,
    consensus_decode, constraints_from_frames, normalize)
from context_evidence_experiment import (CUTS, fixed_key_words, generate_blocks)


def greedy_decode(raw, words):
    """Independent fixed-key prefix decoder for exhaustive small-key oracle."""
    path, pos = [], 0
    while pos < len(raw):
        matching = [w for w in words if raw.startswith(w, pos)]
        if not matching:
            return None
        if len(matching) != 1:
            raise AssertionError('test oracle key is not prefix-free')
        path.append(matching[0]); pos += len(matching[0])
    return path


class ContextConstraintTests(unittest.TestCase):
    def test_full_value_dnf_is_tautology_and_factors_unseen_keys(self):
        frame = [((0, v),) for v in range(3)]
        self.assertEqual(normalize(frame, [set(range(3))]*32), ((),))
        model = KeySet(32, [frame])
        self.assertEqual(model.count(), 3**32)
        self.assertEqual(model.nodes, 1)

    def test_shared_variable_correlations_are_not_multiplied_as_independent(self):
        equal01 = [((0, v), (1, v)) for v in range(3)]
        equal12 = [((1, v), (2, v)) for v in range(3)]
        model = KeySet(3, [equal01, equal12])
        self.assertEqual(model.count(), 3)
        self.assertEqual(model.count(((0, 1), (2, 2))), 0)
        self.assertEqual(model.count(((0, 1),)), 1)

    def test_inconsistency_distinct_from_unique_and_unknown(self):
        self.assertEqual(KeySet(3, [[((0, 0),)], [((0, 1),)]]).count(), 0)
        self.assertEqual(KeySet(3, [[((i, 0),)] for i in range(3)]).count(), 1)
        self.assertEqual(KeySet(3, []).count(), 27)

    def test_caps_raise_instead_of_returning_partial_unique_counts(self):
        frame = [((0, 0), (1, 0)), ((0, 1), (1, 1))]
        with self.assertRaises(ResourceLimit):
            KeySet(2, [frame], node_cap=1).count()
        blocks = generate_blocks(random.Random(18), 2)
        with self.assertRaises(ResourceLimit):
            FrameParser(blocks, path_cap=1).paths(blocks[0])

    def test_csp_and_consensus_match_exhaustive_independent_keys(self):
        rng = random.Random(1818)
        for case in range(12):
            blocks = generate_blocks(rng, 4)
            parser = FrameParser(blocks)
            truth = tuple(rng.randrange(3) for _ in range(4))
            key_words = fixed_key_words(blocks, truth)
            frames = [''.join(rng.choice(key_words) for _ in range(2)) for _ in range(case % 5)]
            model = KeySet(4, constraints_from_frames(parser, frames))
            survivors = []
            for key in itertools.product(range(3), repeat=4):
                words = fixed_key_words(blocks, key)
                if all(greedy_decode(raw, words) is not None for raw in frames):
                    survivors.append((key, words))
            self.assertEqual(model.count(), len(survivors))
            for i in range(4):
                for value in range(3):
                    self.assertEqual(model.count(((i, value),)), sum(key[i] == value for key, _ in survivors))
            for raw in (blocks[0], ''.join(key_words[:3])):
                expected = {tuple(path) for _, words in survivors if (path := greedy_decode(raw, words)) is not None}
                actual = consensus_decode(parser, model, raw)
                self.assertEqual({tuple(p['units']) for p in actual['possible_paths']}, expected)
                self.assertEqual(actual['status'], 'unique' if len(expected) == 1 else 'ambiguous' if expected else 'inconsistent')

    def test_bad_framing_can_be_consistent_until_counterevidence_arrives(self):
        blocks = generate_blocks(random.Random(31), 4)
        parser = FrameParser(blocks)
        true_frame, bad_frame = blocks[0][:4], blocks[0][:5]
        wrong = KeySet(4, constraints_from_frames(parser, [bad_frame]))
        self.assertEqual(wrong.count(), 3**3)
        self.assertEqual(wrong.count(((0, 0),)), 0)
        conflict = KeySet(4, constraints_from_frames(parser, [bad_frame, true_frame]))
        self.assertEqual(conflict.count(), 0)


if __name__ == '__main__':
    unittest.main()
