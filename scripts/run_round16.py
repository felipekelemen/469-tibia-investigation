#!/usr/bin/env python3
"""Complete round16 replay, including all297 randomized dictionaries."""
import json

from wordcode_boundary_certificates import build as certificates
from wordcode_transfer_experiment import ROOT, main


if __name__ == '__main__':
    main(check=True)
    expected = json.loads((ROOT / 'results/round16_boundary_certificates.json').read_text())
    if certificates() != expected:
        raise ValueError('post-experiment boundary explanation changed')
    print('All 7 book-span certificates replayed. No corrected NPC text or English meanings inferred.')
