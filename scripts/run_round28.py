#!/usr/bin/env python3
"""Offline integrity, full real-target and independent-certificate replay."""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
from round28_experiment import (ROOT, identifier, null_search, real_search,
                                source_inputs, verify_inputs)
from round28_radix import CODECS, FRAMINGS, KEYS, Lexicon
from round28_qualification import run as qualify
from round28_certificates import audit


def canonical(value):
    return json.loads(json.dumps(value))


def check_nulls(nulls, sources, books, real_stat):
    for family, result in nulls['families'].items():
        statistics = []
        for row in result['rows']:
            configs = Counter()
            for name, groups in row['groups'].items():
                original = sources[name]['groups']
                assert list(map(len, groups)) == list(map(len, original))
                assert row['changed'][name] == (groups != original)
                if family == 'global_shuffle':
                    assert Counter(''.join(groups)) == Counter(''.join(original))
                if family == 'distinct_group_shuffle':
                    assert all(Counter(a) == Counter(b) for a, b in zip(groups, original))
                if family in ('distinct_group_shuffle', 'book_substrings'):
                    mapping = {}
                    for before, after in zip(original, groups):
                        assert before not in mapping or mapping[before] == after
                        mapping[before] = after
                if family == 'book_substrings':
                    assert all(any(g in b['digits'] for b in books) for g in groups)
                solves = row['scan']['sources'][name]
                assert {(s['codec'], s['framing']) for s in solves} == set(
                    (c, f) for c in CODECS for f in FRAMINGS)
                for solve in solves:
                    assert solve['complete'] and solve['keys_examined'] == 312
                    assert len({tuple(k) for k in solve['keys']}) == len(solve['keys'])
                    for key in solve['keys']:
                        assert tuple(key) in KEYS
                        configs[identifier(solve['codec'], solve['framing'], key)] += 1
            maximum = max(configs.values(), default=0)
            assert maximum == row['scan']['maximum_fully_lexical_sources_one_config']
            assert dict(configs) == row['scan']['source_counts_per_surviving_config']
            assert sorted(k for k, n in configs.items() if n == len(sources)) == row['scan']['shared_configs_all_sources']
            statistics.append(maximum)
        assert result['replicates'] == len(result['rows']) == 99
        assert result['maximum_statistic_histogram'] == {str(k):v for k,v in Counter(statistics).items()}
        assert result['plus_one_upper_tail'] == (1+sum(s >= real_stat for s in statistics))/100
        for name in sources:
            assert result['changed_sources'][name] == sum(r['changed'][name] for r in result['rows'])
            assert result['distinct_outputs'][name] == len({tuple(r['groups'][name]) for r in result['rows']})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    verify_inputs()
    for path, sha in json.loads((ROOT/'data/round28_result_manifest.json').read_text())['sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, path
    protocol = json.loads((ROOT/'data/round28_protocol.json').read_text())
    fixtures = json.loads((ROOT/'data/round28_fixtures.json').read_text())
    qualification = json.loads((ROOT/'results/round28_qualification.json').read_text())
    targets = json.loads((ROOT/'results/round28_targets.json').read_text())
    nulls = json.loads((ROOT/'results/round28_nulls.json').read_text())
    lexicon, sources = Lexicon(), source_inputs()
    books = json.loads((ROOT/'data/normalized_books.json').read_text())
    assert canonical(real_search(protocol, sources, books, lexicon)) == targets
    assert audit(targets) == json.loads((ROOT/'results/round28_certificates.json').read_text())
    first = qualify(protocol, {'cases': fixtures['cases'][:1]}, lexicon)
    assert first['cases'][0] == qualification['cases'][0]
    check_nulls(nulls, sources, books, targets['full_source_search']['maximum_fully_lexical_sources_one_config'])
    if args.full:
        assert canonical(qualify(protocol, fixtures, lexicon)) == qualification
        assert canonical(null_search(protocol, sources, books, lexicon,
            targets['full_source_search']['maximum_fully_lexical_sources_one_config'])) == nulls
    print('Round28: input/result integrity, all real fits, independent certificates, first positive and null invariants passed.'
          + (' All540positive fits and396joint null replicates replayed.' if args.full else ' Use --full for all positives/nulls.'))
