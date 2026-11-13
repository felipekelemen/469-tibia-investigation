#!/usr/bin/env python3
"""Full nonmutating replay of exact context inference and NPC count census."""
import context_evidence_experiment as context
import npc_framing_census as framing


if __name__ == '__main__':
    context.main(check=True)
    for path, expected in framing.load('data/round18_framing_manifest.json')['sha256'].items():
        if framing.sha(path) != expected:
            raise ValueError('framing input changed: '+path)
    if framing.build() != framing.load('results/round18_npc_framing.json'):
        raise ValueError('NPC/book framing census changed')
    print('All750condition/budget fits and exact NPC/book counts replayed; no game meanings inferred.')
