#!/usr/bin/env python3
"""Known-family letter recovery; boundary recovery is a separate measurement."""
from collections import defaultdict
from pathlib import Path
import json
from round28_radix import Lexicon, fit, predict

ROOT = Path(__file__).resolve().parents[1]


def run(protocol, fixtures, lexicon):
    cases = []
    for fixture in fixtures['cases']:
        codec, framing = fixture['codec'], fixture['framing']
        trained = fit(fixture['train'], codec, framing, lexicon)
        assert fixture['key'] in trained['keys'], 'True key lost in a generated control'
        prediction = predict(fixture['held'], codec, framing, trained['keys'], lexicon)
        truth = ''.join(fixture['held_words'])
        certified = prediction['certified']
        assert certified is None or len(certified) == len(truth)
        correct = sum(c == t for c, t in zip(certified or '?'*len(truth), truth))
        wrong = sum(c != '?' and c != t for c, t in zip(certified or '?'*len(truth), truth))
        accuracy = correct/len(truth)
        trained.pop('first_failure_per_key')
        cases.append({'id': fixture['id'], 'profile': fixture['profile'],
            'codec': codec, 'framing': framing, 'fit': trained,
            'true_key_retained': True, 'full_key_unique_exact': trained['keys'] == [fixture['key']],
            'held_truth': truth, 'prediction': prediction,
            'certified_letter_accuracy': accuracy, 'certified_wrong_letters': wrong,
            'full_literal_exact': prediction['unique_literal'] == truth,
            'word_boundaries_and_words_exact': prediction['unique_words'] == fixture['held_words'],
            'held_words_outside_training_lexicon': [w for w in fixture['held_words'] if w not in lexicon.words],
            'passes': accuracy >= protocol['gate']['minimum_certified_held_letter_accuracy'] and wrong == 0})
        if len(cases)%30 == 0:
            print('qualification', len(cases), '/', len(fixtures['cases']), flush=True)
    cells = defaultdict(list)
    for case in cases:
        cells[(case['profile'], case['codec'], case['framing'])].append(case)
    summary = []
    for key, rows in sorted(cells.items()):
        passed = sum(r['passes'] for r in rows)
        wrong = sum(r['certified_wrong_letters'] for r in rows)
        summary.append({'profile': key[0], 'codec': key[1], 'framing': key[2],
            'cases': len(rows), 'cases_passing_letter_gate': passed,
            'known_family_letter_qualified': len(rows) == 30 and passed >= 27 and wrong == 0,
            'full_keys_unique_exact': sum(r['full_key_unique_exact'] for r in rows),
            'full_literals_exact': sum(r['full_literal_exact'] for r in rows),
            'exact_word_boundaries': sum(r['word_boundaries_and_words_exact'] for r in rows),
            'certified_wrong_letters': wrong,
            'held_words_outside_lexicon': sum(len(r['held_words_outside_training_lexicon']) for r in rows)})
    return {'scope': 'Known codec and framing, vocabulary-conditioned discovery, new-author windows. Does not qualify unknown-model selection, English detection or Tibia translation.',
            'cases': cases, 'summary': summary}


if __name__ == '__main__':
    from round28_experiment import verify_inputs
    verify_inputs()
    path = ROOT/'results/round28_qualification.json'
    if path.exists():
        raise ValueError('Refusing to replace qualification result')
    protocol = json.loads((ROOT/'data/round28_protocol.json').read_text())
    fixtures = json.loads((ROOT/'data/round28_fixtures.json').read_text())
    result = run(protocol, fixtures, Lexicon())
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result['summary'], indent=2))
