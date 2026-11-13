#!/usr/bin/env python3
"""Nonmutating full replay of development, selection, qualification and proofs."""
import hidden_unit_benchmark as benchmark
from hidden_unit_diagnostics import build as diagnostics


def main():
    for path, expected in benchmark.load('data/round17_result_manifest.json')['sha256'].items():
        if benchmark.sha(path) != expected:
            raise ValueError('published artifact changed: '+path)
    # Run original development/selection code with an in-memory output sink;
    # do not overwrite the prospective qualification manifest during replay.
    captured = {}
    original_dump = benchmark.dump
    benchmark.dump = lambda path, value: captured.__setitem__(path, value)
    try:
        benchmark.develop()
    finally:
        benchmark.dump = original_dump
    for path, obj in captured.items():
        if benchmark.load(path) != obj:
            raise ValueError('development/selection replay changed: '+path)
    qualification = benchmark.qualification()
    if qualification != benchmark.load('results/round17_qualification.json'):
        raise ValueError('qualification replay changed')
    if benchmark.adversarial_certificate() != benchmark.load('results/round17_identifiability_certificate.json'):
        raise ValueError('prefix-code ambiguity certificate changed')
    if diagnostics() != benchmark.load('results/round17_failure_diagnostics.json'):
        raise ValueError('failure diagnostic changed')
    print('Round17: all288development fits,360qualification fits and720paired target evaluations replayed.')
    print('Known dictionaries were never supplied to learners; no game data fitted or decoded.')
    print('Game application: '+qualification['game_application'])


if __name__ == '__main__':
    main()
