#!/usr/bin/env python3
"""Synthetic qualification; ground truth is used only for scoring after fitting."""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import hashlib
import json
from round27_fixtures import training_bank
from round27_witness_solver import Fit, emit, word_paths
from unit_morphism_lexicon import banks

ROOT = Path(__file__).resolve().parents[1]


def spans(chunks):
    out, start = set(), 0
    for chunk in chunks:
        out.add((start, start+len(chunk), chunk))
        start += len(chunk)
    return out


def score(raw, truth, truekey, prediction):
    expected = [truekey[d] for d in raw]
    exact = prediction['form_certified'] and prediction.get('form') == truth
    wrong = prediction['form_certified'] and prediction.get('form') != truth
    f1 = 0.0
    if prediction['chunks_certified']:
        predicted, actual = spans(prediction['chunks']), spans(expected)
        f1 = 2*len(predicted & actual)/(len(predicted)+len(actual))
        wrong = wrong or prediction['chunks'] != expected
    return {'exact_certified_form': bool(exact), 'confidently_wrong': bool(wrong),
            'certified_unit_span_f1': f1}


def fit_case(case, scenario, protocol, bank):
    train = case['train'][:7] if scenario == 'sparse7_known_lexicon' else case['train']
    if scenario == 'missing_digit':
        train = [w for w in train if case['missing_digit'] not in w]
    assert not set(train) & set(case['held'])
    # No true key, true forms or heldout lexical membership passed to Fit.
    fit = Fit(train, bank, protocol['budgets'])
    outputs = []
    for raw, form in zip(case['held'], case['held_forms']):
        p = fit.predict(raw)
        outputs.append({'raw': raw, 'truth': form, 'prediction': p,
                        'score': score(raw, form, case['key'], p)})
    names, boundaries = [], []
    if scenario == 'rich30_known_lexicon':
        for row in case['names']:
            assert row['form'] not in bank.reverse
            p = fit.predict(row['raw'])
            names.append({**row, 'prediction': p,
                'score': score(row['raw'], row['form'], case['key'], p)})
        for i in range(0, 10, 2):
            raw = ''.join(case['held'][i:i+2])
            true_words = case['held_forms'][i:i+2]
            oracle = word_paths(raw, case['key'], bank)
            assert oracle['paths'] >= 1
            # Boundary diagnostic does not spend additional query budget.
            learned = word_paths(raw, fit.key, bank) if fit.unique else None
            boundaries.append({'raw': raw, 'true_words': true_words,
                'oracle': oracle, 'learned': learned,
                'oracle_exact': oracle['unique_words'] == true_words,
                'learned_exact': learned is not None and learned['unique_words'] == true_words})
    # Audit every published witness against all training constraints.
    for query in fit.queries:
        if query['status'] == 'SAT':
            assert all(emit(w, query['key']) in bank.reverse for w in train)
    exact = sum(r['score']['exact_certified_form'] for r in outputs)/len(outputs)
    f1 = sum(r['score']['certified_unit_span_f1'] for r in outputs)/len(outputs)
    wrong = sum(r['score']['confidently_wrong'] for r in outputs)
    gate = protocol['gate']
    return {'id': case['id'], 'scenario': scenario, 'train': train,
        'observed_digits': sorted(set(''.join(train))), 'states': fit.used,
        'queries': fit.queries, 'global_key_unique': fit.unique,
        'observed_key_exact_when_unique': fit.unique and all(
            fit.key[d] == case['key'][d] for d in fit.model.digits),
        'full_key_exact_when_unique': fit.unique and fit.key == case['key'],
        'held': outputs, 'names': names, 'boundaries': boundaries,
        'certified_exact_fraction': exact, 'certified_unit_span_f1': f1,
        'confidently_wrong': wrong,
        'passes': exact >= gate['per_case_minimum_certified_exact_held_form_fraction']
                  and f1 >= gate['per_case_minimum_certified_unit_span_f1']
                  and wrong <= gate['maximum_confidently_wrong_predictions']}


def prefix_free(units):
    return all(not b.startswith(a) for a in units for b in units if a != b)


def prefix_parse(raw, units):
    parts = []
    while raw:
        matches = [u for u in units if raw.startswith(u)]
        if len(matches) != 1:
            return None
        parts.append(matches[0])
        raw = raw[len(parts[-1]):]
    return parts


def diagnostics(fixtures):
    hidden = []
    for row in fixtures['hidden_vocabulary']:
        a, b = row['a'], row['b']
        pa, pb = prefix_parse(row['train'], a), prefix_parse(row['train'], b)
        assert prefix_free(a) and prefix_free(b) and pa and pb
        assert ''.join(pa) == ''.join(pb) == row['train']
        assert len(a) == len(b) == 3 and sum(map(len, a)) == sum(map(len, b)) == 12
        assert sorted(Counter(pa).values()) == sorted(Counter(pb).values()) == [3, 3, 3]
        assert spans(pa) != spans(pb)
        assert prefix_parse(row['novel'], a) and prefix_parse(row['novel'], b) is None
        hidden.append({'same_training_bytes': True, 'different_boundaries': True,
                       'same_unit_histogram_and_length_cost': True,
                       'novel_accepted_by_a_only': True})
    phonebank = banks()[0]['phone1_3']
    phonetic = []
    for row in fixtures['phonetic']:
        form = emit(row['raw'], row['key'])
        labels = phonebank.reverse.get(form, [])
        assert form == row['form'] and labels == row['spellings'] and len(labels) >= 2
        phonetic.append({'raw': row['raw'], 'phones': phonebank.render(form),
                         'spellings': labels, 'unique_spelling': None,
                         'known_key_phone_recovery': True})
    return {'hidden_vocabulary_certificates': hidden, 'known_key_phonetic_ambiguity': phonetic}


def summarize(rows, protocol):
    groups = defaultdict(list)
    for row in rows:
        groups[row['scenario']].append(row)
    summary = {}
    for scenario, cases in sorted(groups.items()):
        held = [h for c in cases for h in c['held']]
        counts = Counter(h['prediction']['status'] for h in held)
        passed = sum(c['passes'] for c in cases)
        summary[scenario] = {'cases': len(cases), 'cases_passing': passed,
            'qualified': len(cases) == protocol['gate']['cases_per_scenario'] and
                         passed >= protocol['gate']['minimum_cases_passing'] and
                         not any(c['confidently_wrong'] for c in cases),
            'full_keys_exact_certified': sum(c['full_key_exact_when_unique'] for c in cases),
            'observed_keys_exact_certified': sum(c['observed_key_exact_when_unique'] for c in cases),
            'held_total': len(held),
            'held_exact_certified': sum(h['score']['exact_certified_form'] for h in held),
            'confidently_wrong': sum(h['score']['confidently_wrong'] for h in held),
            'prediction_statuses': dict(sorted(counts.items())),
            'query_statuses': dict(Counter(q['status'] for c in cases for q in c['queries'])),
            'states_total': sum(c['states'] for c in cases)}
    base = groups['rich30_known_lexicon']
    names = [n for c in base for n in c['names']]
    boundary = [b for c in base for b in c['boundaries']]
    summary['withheld_names'] = {'total': len(names),
        'exact_certified': sum(n['score']['exact_certified_form'] for n in names),
        'confidently_wrong': sum(n['score']['confidently_wrong'] for n in names)}
    summary['paired_unspaced_test_boundaries'] = {'streams': len(boundary),
        'oracle_unique_exact': sum(b['oracle_exact'] for b in boundary),
        'oracle_ambiguous': sum(b['oracle']['paths'] > 1 for b in boundary),
        'learned_unique_exact': sum(b['learned_exact'] for b in boundary),
        'cases_all_five_oracle_exact': sum(all(b['oracle_exact'] for b in c['boundaries']) for c in base),
        'cases_all_five_learned_exact': sum(all(b['learned_exact'] for b in c['boundaries']) for c in base)}
    return summary


def verify_manifest(filename):
    manifest = json.loads((ROOT/'data'/filename).read_text())
    for path, expected in manifest['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != expected:
            raise ValueError('Changed frozen input: '+path)


def run(output):
    verify_manifest('round27_experiment_manifest.json')
    protocol = json.loads((ROOT/'data/round27_protocol.json').read_text())
    fixtures = json.loads((ROOT/'data/round27_fixtures.json').read_text())
    bank = training_bank(protocol)
    rows = []
    output.mkdir(parents=True, exist_ok=True)
    progress = output/'round27_progress.jsonl'
    if progress.exists():
        raise ValueError('Refusing to reuse an existing run; choose fresh --output')
    for case in fixtures['cases']:
        scenarios = protocol['scenarios'][:3] if case['kind'] == 'base' else protocol['scenarios'][3:]
        for scenario in scenarios:
            row = fit_case(case, scenario, protocol, bank)
            rows.append(row)
            with progress.open('a') as stream:
                stream.write(json.dumps(row, ensure_ascii=False)+'\n')
            print(case['id'], scenario, 'pass', row['passes'], 'exact',
                  row['certified_exact_fraction'], 'states', row['states'], flush=True)
    out = {'round': 27, 'translation_validated': False,
           'summary': summarize(rows, protocol), 'cases': rows,
           'diagnostics': diagnostics(fixtures)}
    (output/'round27_qualification.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(out['summary'], indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'results')
    args = parser.parse_args()
    run(args.output)
