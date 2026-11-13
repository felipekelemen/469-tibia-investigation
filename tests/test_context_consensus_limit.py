from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from context_constraint_solver import FrameParser, KeySet, consensus_decode, constraints_from_frames
from context_evidence_experiment import generate_blocks


class ConditionalConsensusTests(unittest.TestCase):
    def test_false_framing_can_force_a_unique_but_incorrect_prediction(self):
        blocks = generate_blocks(random.Random(18001), 4)
        parser = FrameParser(blocks)
        true_units = [blocks[0][:4], blocks[0][4:]]
        model = KeySet(4, constraints_from_frames(parser, [blocks[0][:5]]))
        result = consensus_decode(parser, model, blocks[0])
        self.assertEqual(result['status'], 'unique')
        self.assertNotEqual(result['prediction'], true_units)
        self.assertEqual(result['prediction'], [blocks[0][:5], blocks[0][5:]])


if __name__ == '__main__':
    unittest.main()
