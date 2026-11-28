#!/usr/bin/env python3
"""Exact anchor census and arithmetic qualification, never a translator."""
import argparse
from collections import Counter
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import resource
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ['3478', '67', '90871', '97664', '3466', '0', '345']


def load(path):
    return json.loads((ROOT / path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify(path):
    for name, expected in load(path)['sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name


def emit(raw, key):
    return ''.join(key[d] for d in raw)


def decode_key(numbers):
    out = {}
    for d, n in enumerate(numbers):
        if not n:
            continue
        unit = ''
        while n:
            n, rem = divmod(n, 27)
            assert 1 <= rem <= 26
            unit = chr(64 + rem) + unit
        assert 1 <= len(unit) <= 3
        out[str(d)] = unit
    return out


def prepare():
    rng = random.Random(load('data/round36_protocol.json')['qualification']['seed'])
    cases = []
    for alphabet, kind in [('A', 'unary'), ('AB', 'binary')]:
        max_word = 15 if kind == 'unary' else 5
        vocabulary = [''.join(chars) for n in range(1, max_word + 1)
                      for chars in itertools.product(alphabet, repeat=n)]
        for planted in [True, False]:
            for i in range(15):
                lex = {w for w in vocabulary if rng.random() < .55}
                truth = None
                if planted:
                    while True:
                        truth = {d: ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 3)))
                                 for d in '013456789'}
                        if kind == 'binary':
                            truth.update({d: rng.choice(alphabet) for d in '0146789'})
                            truth['3'] = ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 2)))
                        forms = [emit(g, truth) for g in GROUPS]
                        if all(len(w) <= max_word for w in forms):
                            lex.update(forms)
                            break
                if not lex:
                    lex.add('A')
                cases.append({'id': f'{kind}_{"planted" if planted else "random"}_{i:02d}',
                              'lexicon': sorted(lex), 'groups': GROUPS, 'true_key': truth})
    old = load('data/round33_fixtures.json')['cases']
    targets = [c for c in old if c['id'] == 'knightmare'] + [c for c in old if c['kind'] == 'within_word_shuffle'][:5]
    return {'tiny': cases, 'targets': targets, 'scope': '60 arithmetic tests,6exposed real/control inputs; no decoder qualification.'}


def brute(case):
    """Independent whole-key enumeration; no partitions, joins or C++ tables."""
    lex = set(case['lexicon'])
    alphabet = sorted(set(''.join(lex)))
    groups = case['groups']
    ds = sorted(set(''.join(groups)))
    longest = max(map(len, lex))
    domains = []
    for d in ds:
        maximum = min([3] + [(longest - (len(g) - g.count(d))) // g.count(d) for g in groups if d in g])
        domains.append([''.join(s) for n in range(1, maximum + 1)
                        for s in itertools.product(alphabet, repeat=n)])
    hist = [dict() for _ in groups]
    total = visited = 0
    for combination in itertools.product(*domains):
        visited += 1
        key = dict(zip(ds, combination))
        output = tuple(emit(g, key) for g in groups)
        if not all(w in lex for w in output):
            continue
        total += 1
        for i, word in enumerate(output):
            if word not in hist[i]:
                hist[i][word] = [0, output, False]
            row = hist[i][word]
            row[0] += 1
            row[2] |= row[1] != output
    return {'count': total, 'visited': visited,
            'marginals': [{w: (r[0], r[2]) for w, r in h.items()} for h in hist]}


def memory_limit():
    cap = load('data/round36_protocol.json')['budgets']['address_space_bytes']
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))


def invoke(command):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    try:
        p = subprocess.run(list(map(str, command)), text=True, capture_output=True,
                           timeout=300, preexec_fn=memory_limit)
        result = json.loads(p.stdout) if p.returncode == 0 else {
            'complete': False, 'count': None, 'reason': 'process_failure', 'returncode': p.returncode}
    except subprocess.TimeoutExpired:
        result = {'complete': False, 'count': None, 'reason': 'wall_limit'}
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    result['resources'] = {'wall_seconds': time.monotonic() - started,
                           'child_cpu_seconds': after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime}
    return result


def check_witnesses(result, groups, lexicon):
    if not result['complete']:
        return 0
    witnesses = 0
    for i, histogram in enumerate(result['marginals']):
        assert histogram['raw'] == groups[i]
        assert sum(int(r[1]) for r in histogram['rows']) == int(result['count'])
        assert len({r[0] for r in histogram['rows']}) == len(histogram['rows'])
        for word, count, first, second in histogram['rows']:
            assert int(count) > 0
            outputs = []
            for codes in [first, second]:
                if codes is None:
                    continue
                key = decode_key(codes)
                assert set(key) == set(''.join(groups))
                output = [emit(g, key) for g in groups]
                assert output[i] == word and all(w in lexicon for w in output)
                outputs.append(output)
                witnesses += 1
            if second is not None:
                assert outputs[0] != outputs[1] and int(count) >= 2
    return witnesses


def summarize(result):
    if not result['complete']:
        return {'complete': False, 'reason': result['reason']}
    total = int(result['count'])
    out = []
    for group in result['marginals']:
        rows = group['rows']
        counts = [int(r[1]) for r in rows]
        minimum = min(counts, default=None)
        maximum = max(counts, default=None)
        out.append({'raw': group['raw'], 'possible_word_forms': len(rows),
                    'minimum_remaining_keys': minimum, 'maximum_remaining_keys': maximum,
                    'minimum_count_words': [r[0] for r in rows if int(r[1]) == minimum],
                    'maximum_count_words': [r[0] for r in rows if int(r[1]) == maximum],
                    'anchor_words_with_unique_key': sum(int(r[1]) == 1 for r in rows),
                    'anchor_words_with_unique_whole_message': sum(r[3] is None for r in rows),
                    'keys_in_unique_message_anchor_cells': sum(int(r[1]) for r in rows if r[3] is None),
                    'hypothetical_uniform_key_expected_remaining': sum(n*n for n in counts) / total if total else None,
                    'hypothetical_uniform_key_information_bits': -sum((n/total)*math.log2(n/total) for n in counts) if total else None})
    return {'complete': True, 'observed_digit_keys': total, 'groups': out,
            'probability_interpretation': 'Uniform weighting of admissible keys only; not a posterior over intended meanings or words.'}


def run(directory):
    verify('data/round36_input_manifest.json')
    verify('data/round36_execution_manifest.json')
    directory.mkdir(exist_ok=False, parents=True)
    started = time.monotonic()
    fixtures = load('data/round36_fixtures.json')
    binary, counter = directory / 'anchors', directory / 'counter'
    for source, target in [('scripts/round36_anchors.cpp', binary), ('scripts/round33_count.cpp', counter)]:
        subprocess.run(['g++', '-O2', '-std=c++17', str(ROOT / source), '-o', str(target)], check=True)
    qualification = []
    lexpath = directory / 'lexicon.txt'
    for case in fixtures['tiny']:
        lexpath.write_text('\n'.join(case['lexicon'])+'\n')
        actual = invoke([binary, lexpath, *case['groups']])
        expected = brute(case)
        assert actual['complete'] and int(actual['count']) == expected['count'], case['id']
        for a, b in zip(actual['marginals'], expected['marginals']):
            assert {r[0]: (int(r[1]), r[3] is not None) for r in a['rows']} == b, case['id']
        checked = check_witnesses(actual, case['groups'], set(case['lexicon']))
        qualification.append({'id': case['id'], 'count': actual['count'], 'whole_keys_enumerated': expected['visited'],
                              'all_marginal_counts_and_message_uniqueness_match': True, 'witnesses_checked': checked})
    save(directory / 'qualification.json', qualification)
    print('Arithmetic qualification:', len(qualification), 'cases passed', flush=True)
    from unit_morphism_lexicon import banks
    words = sorted(banks()[0]['grapheme1_3'].reverse)
    lexpath.write_text('\n'.join(words)+'\n')
    summaries = []
    main = None
    for case in fixtures['targets']:
        if time.monotonic() - started >= load('data/round36_protocol.json')['budgets']['total_wall_seconds']:
            result = {'complete': False, 'count': None, 'reason': 'batch_wall_limit'}
        else:
            result = invoke([binary, lexpath, *case['words']])
        witness_count = check_witnesses(result, case['words'], set(words))
        artifact = directory / (case['id'] + '.json.gz')
        artifact.write_bytes(gzip.compress(json.dumps(result, separators=(',', ':')).encode(), mtime=0))
        summary = dict(id=case['id'], kind=case['kind'], **summarize(result),
                       witnesses_checked=witness_count, resources=result.get('resources'))
        summaries.append(summary)
        print(json.dumps({k:v for k,v in summary.items() if k != 'groups'}), flush=True)
        if case['id'] == 'knightmare':
            main = result
    checks = []
    if main and main['complete']:
        requests = set()
        for group in main['marginals']:
            rows = group['rows']
            if rows:
                chosen = [min(rows, key=lambda r:r[0]), min(rows, key=lambda r:(int(r[1]),r[0])),
                          min(rows, key=lambda r:(-int(r[1]),r[0]))]
                requests.update((group['raw'],r[0],r[1]) for r in chosen)
        requests.update(('3478', name, '0') for name in ['BEHOLDER','BONELORD'])
        for raw, word, expected in sorted(requests):
            input_path = directory / 'forced.txt'
            input_path.write_text('7\n'+'\n'.join(g+' '+(word if g == raw else '-') for g in GROUPS)+'\n')
            if time.monotonic() - started >= load('data/round36_protocol.json')['budgets']['total_wall_seconds']:
                actual = {'complete': False, 'count': None, 'reason': 'batch_wall_limit'}
            else:
                actual = invoke([counter, lexpath, input_path])
            checks.append({'raw': raw, 'word': word, 'expected': expected, 'result': actual,
                           'matches': bool(actual['complete'] and actual['count'] == expected)})
    save(directory / 'independent_checks.json', checks)
    save(directory / 'summary.json', {'round':36, 'qualification_cases':len(qualification),
         'targets':summaries,'independent_conditional_checks':len(checks),
         'independent_checks_all_complete_and_matching':bool(checks) and all(c['matches'] for c in checks),
         'translation_validated':False, 'new_semantic_candidate':None,
         'budget_wall_seconds_including_qualification':time.monotonic()-started})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.prepare:
        path = ROOT / 'data/round36_fixtures.json'
        assert not path.exists()
        save(path, prepare())
    else:
        assert args.output
        run(args.output.resolve())
