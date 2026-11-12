#!/usr/bin/env python3
"""Verify recorded round6 evidence without reopening calibration or fitting keys."""
import hashlib
import json
import pathlib

from word_validator_experiment import verify
from zero_restoration_audit import parse_summary, self_checks

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/round6_evidence_manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('round6 evidence changed: ' + relative)
    protocol = json.loads((ROOT / 'data/word_validator_protocol.json').read_text())
    verify(protocol)
    lexical = json.loads((ROOT / 'results/word_validator_audit.json').read_text())
    if len(lexical['qualification_trials']) != 600 or len(lexical['all_books']) != 70:
        raise ValueError('incomplete word validator audit')
    for row in lexical['all_books']:
        if row['segmented'].replace(' ', '') != row['literal']:
            raise ValueError('letter repair found')
    # Independently recompute the inexpensive structural DP; never pick English.
    inventory = set(json.loads((ROOT / 'data/normalized_code_map.json').read_text()))
    books = json.loads((ROOT / 'data/normalized_books.json').read_text())
    zero = json.loads((ROOT / 'results/zero_restoration_audit.json').read_text())
    recorded = {row['id']: row for row in zero['raw_parse_counts']}
    self_checks()
    for book in books:
        current = parse_summary(book['digits'], inventory)
        for field in ['segmentation_path_count', 'min_tokens', 'max_tokens']:
            if current[field] != recorded[book['id']][field]:
                raise ValueError('raw parser result changed')
    module = json.loads((ROOT / 'results/module_signal_audit.json').read_text())
    print('Round6 hashes, 600 qualification scores and 70 lossless readings verified.')
    print('Raw segmentation DP recomputed for 70 books; synthetic checks passed.')
    print('Module null:', module['module_null_feasibility'])
    print('Word judge qualified:', lexical['global_gate_passes'])
    print('Verified translations:', lexical['verified_translations'])
    print('No key optimization or calibration reopened.')


if __name__ == '__main__':
    main()
