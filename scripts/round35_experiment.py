#!/usr/bin/env python3
"""Hidden-key qualification of a frozen beam/scoring procedure, not game fitting."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import resource
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def distance(a, b):
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        row = [i]
        for j, y in enumerate(b, 1):
            row.append(min(row[-1] + 1, previous[j] + 1, previous[j - 1] + (x != y)))
        previous = row
    return previous[-1]


def binomial_interval(successes, trials, alpha=.05):
    """Clopper-Pearson via binomial-tail inversion, no scipy dependency."""
    if not trials:
        return None
    def tail(p, first, last):
        return sum(math.comb(trials, j) * p**j * (1 - p)**(trials - j)
                   for j in range(first, last + 1))
    def solve(fn, target, increasing):
        a, b = 0., 1.
        for _ in range(70):
            m = (a + b) / 2
            if (fn(m) < target) == increasing:
                a = m
            else:
                b = m
        return (a + b) / 2
    lower = 0. if successes == 0 else solve(lambda p: tail(p, successes, trials), alpha / 2, True)
    upper = 1. if successes == trials else solve(lambda p: tail(p, 0, successes), alpha / 2, False)
    return [lower, upper]


def limits(memory):
    def apply():
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_CPU, (32, 33))
    return apply


def run_fit(raw, version, protocol, binary, model):
    budget = protocol['budgets']
    command = [str(binary), str(model), str(version['beam']),
               str(budget['local_rows_per_group']), str(budget['compatibility_checks_per_fit']),
               str(budget['generated_extensions_per_depth']), str(budget['wall_seconds_per_fit']), *raw]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    try:
        p = subprocess.run(command, text=True, capture_output=True, timeout=35,
                           preexec_fn=limits(budget['address_space_bytes']))
        if p.returncode:
            output = {'status': 'process_failure', 'returncode': p.returncode, 'stderr': p.stderr[:500], 'top': []}
        else:
            output = json.loads(p.stdout)
    except subprocess.TimeoutExpired:
        output = {'status': 'limit', 'limit': 'outer_timeout', 'top': []}
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    output['wall_seconds'] = time.monotonic() - start
    output['child_cpu_seconds'] = after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime
    return output


def evaluate(case, fit, protocol):
    top = fit.get('top', [])
    best = top[0] if top else None
    observed = set(''.join(case['input']))
    gap = top[0]['score'] - top[1]['score'] if len(top) == 2 else None
    mean = best['score'] / len(case['input']) if best else None
    margin = (gap is not None and gap >= protocol['score']['minimum_best_second_key_gap']) or (
        len(top) == 1 and fit.get('pruned', 1) == 0)
    accepted = bool(best and fit['status'] == 'ranked' and margin and
                    mean >= protocol['score']['minimum_mean_log_score'])
    key = {str(d): u for d, u in enumerate(best['key']) if u} if best else {}
    # Audit returned candidates without consulting intended values.
    for candidate in top:
        candidate_key = {str(d): u for d, u in enumerate(candidate['key']) if u}
        assert observed <= set(candidate_key)
        assert [''.join(candidate_key[d] for d in raw) for raw in case['input']] == candidate['words']
        assert all(1 <= len(u) <= 3 for u in candidate_key.values())
    predictions = []
    for probe in case['probes']:
        missing = sorted(set(probe) - observed)
        predictions.append({'raw': probe, 'missing_digits': missing,
                            'output': ''.join(key[d] for d in probe) if best and not missing else None,
                            'accepted': accepted and not missing})
    expected = case['expected']
    exact = bool(best and expected is not None and best['words'] == expected)
    probe_accuracy = 0.
    if predictions and all(p['output'] is not None for p in predictions):
        error = sum(distance(p['output'], truth) for p, truth in zip(predictions, case['probe_truth']))
        denominator = sum(max(len(p['output']), len(truth)) for p, truth in zip(predictions, case['probe_truth']))
        probe_accuracy = 1. - error / denominator
    gate = protocol['gate']
    passed = accepted and exact and bool(predictions) and all(p['accepted'] for p in predictions) and probe_accuracy >= gate['minimum_reserved_probe_letter_accuracy']
    return {'id': case['id'], 'version': case['version'], 'scenario': case['scenario'],
            'fit': fit, 'mean_log_score': mean, 'retained_key_score_gap': gap,
            'training_candidate_accepted': accepted, 'input_exact': exact,
            'observed_key_exact': bool(best and expected is not None and all(key[d] == case['key'].get(d) for d in observed)),
            'probes': predictions, 'reserved_probe_letter_accuracy': probe_accuracy,
            'passes_positive_gate': bool(passed),
            'negative_false_acceptance': accepted and expected is None,
            'ambiguous_false_certainty': accepted and case['scenario'] == 'ambiguous_pair',
            'missing_symbol_false_prediction': case['scenario'] == 'missing_digit' and any(p['accepted'] for p in predictions)}


def summarize(rows, protocol):
    groups = defaultdict(list)
    for row in rows:
        groups[row['version'], row['scenario']].append(row)
    result = {}
    for (version, scenario), cases in sorted(groups.items()):
        passed = sum(r['passes_positive_gate'] for r in cases)
        false = sum(r['negative_false_acceptance'] for r in cases)
        row = {'cases': len(cases), 'passes': passed,
               'input_exact_top1': sum(r['input_exact'] for r in cases),
               'observed_key_exact_top1': sum(r['observed_key_exact'] for r in cases),
               'accepted_candidates': sum(r['training_candidate_accepted'] for r in cases),
               'false_acceptances': false,
               'ambiguous_false_certainties': sum(r['ambiguous_false_certainty'] for r in cases),
               'missing_symbol_false_predictions': sum(r['missing_symbol_false_prediction'] for r in cases),
               'status_counts': dict(Counter(r['fit']['status'] for r in cases)),
               'limit_counts': dict(Counter(r['fit'].get('limit') for r in cases if r['fit']['status'] == 'limit')),
               'cpu_seconds': sum(r['fit'].get('child_cpu_seconds', 0) for r in cases),
               'wall_seconds': sum(r['fit'].get('wall_seconds', 0) for r in cases)}
        if scenario.endswith('null') or scenario == 'within_group_shuffle':
            row['false_acceptance_CI95'] = binomial_interval(false, len(cases))
        result.setdefault(version, {})[scenario] = row
    decisions = {}
    for version, scenarios in result.items():
        complete = all(s in scenarios and scenarios[s]['cases'] == 30 for s in protocol['scenarios'])
        controls = complete and all(scenarios[s]['false_acceptances'] == 0 for s in ['uniform_null', 'within_group_shuffle'])
        safe = complete and scenarios['ambiguous_pair']['ambiguous_false_certainties'] == 0 and scenarios['missing_digit']['missing_symbol_false_predictions'] == 0
        decisions[version] = {'all_scenarios_present': complete,
            'negative_gate_passed': controls, 'ambiguity_and_missing_safety_passed': safe,
            'natural7_qualified': bool(complete and controls and safe and scenarios['natural7']['passes'] >= 27),
            'repeated21_qualified': bool(complete and controls and safe and scenarios['repeated21']['passes'] >= 27),
            'name_oov7_qualified': bool(complete and controls and safe and scenarios['name_oov7']['passes'] >= 27),
            'unspaced_qualified': False}
    return {'scenarios': result, 'decisions': decisions,
            'total_cpu_seconds': sum(r['fit'].get('child_cpu_seconds', 0) for r in rows),
            'total_fit_wall_seconds': sum(r['fit'].get('wall_seconds', 0) for r in rows)}


def run(directory):
    for manifest in ['data/round35_prerun_manifest.json', 'data/round35_execution_manifest.json']:
        for path, expected in json.loads((ROOT / manifest).read_text())['sha256'].items():
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
                raise ValueError('Frozen input changed: ' + path)
    protocol = json.loads((ROOT / 'data/round35_protocol.json').read_text())
    fixtures = json.loads((ROOT / 'data/round35_fixtures.json').read_text())
    directory.mkdir(exist_ok=False, parents=True)
    binary = directory / 'beam'
    subprocess.run(['g++', '-O2', '-std=c++17', str(ROOT / 'scripts/round35_beam.cpp'), '-o', str(binary)], check=True)
    rows = []
    for version in protocol['versions']:
        if version['id'] == 'v2' and summarize(rows, protocol)['decisions']['v1']['natural7_qualified']:
            break
        for case in fixtures['cases']:
            if case['version'] != version['id']:
                continue
            used = sum(r['fit'].get('wall_seconds', 0) for r in rows)
            if used >= protocol['budgets']['maximum_total_fit_wall_seconds']:
                fit = {'status': 'limit', 'limit': 'total_batch', 'top': []}
            elif case['scenario'] == 'unspaced':
                fit = {'status': 'unsupported_unspaced_training', 'top': []}
            else:
                # Deliberately pass only ciphertext groups and frozen model/configuration.
                fit = run_fit(case['input'], version, protocol, binary,
                              ROOT / 'data/round35_reference/language_model.txt')
            row = evaluate(case, fit, protocol)
            rows.append(row)
            with (directory / 'progress.jsonl').open('a') as stream:
                stream.write(json.dumps(row) + '\n')
            if len(rows) % 15 == 0:
                print(len(rows), case['id'], 'status', fit['status'], 'exact', row['input_exact'], flush=True)
        print(json.dumps(summarize(rows, protocol)['decisions'], indent=2), flush=True)
    out = {'round': 35, 'summary': summarize(rows, protocol), 'cases': rows,
           'translation_validated': False, 'game_messages_fitted': 0}
    (directory / 'qualification.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out['summary'], indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output.resolve())
