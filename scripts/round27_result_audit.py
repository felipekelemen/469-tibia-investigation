#!/usr/bin/env python3
"""Post-fit overlap audit and paired baseline comparison; never changes gates."""
from collections import defaultdict
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(result, baseline):
    groups = defaultdict(list)
    for case in result['cases']:
        for row in case['held']:
            groups[case['scenario']].append({
                'case': case['id'], 'raw': row['raw'],
                'whole_raw_occurs_inside_training_group': any(row['raw'] in w for w in case['train']),
                'exact_certified': row['score']['exact_certified_form']})
    overlap = {}
    for scenario, rows in groups.items():
        novel = [r for r in rows if not r['whole_raw_occurs_inside_training_group']]
        overlap[scenario] = {'held_total': len(rows),
            'whole_raw_seen_as_training_substring': len(rows)-len(novel),
            'whole_raw_not_seen_as_training_substring': len(novel),
            'novel_raw_exact_certified': sum(r['exact_certified'] for r in novel),
            'rows': rows}
    old = {r['id']: r for r in baseline['cases']}
    paired = []
    for row in result['cases']:
        if row['scenario'] != 'sparse7_known_lexicon':
            continue
        before = old[row['id']]
        old_exact = sum(h['score']['exact_certified_form'] for h in before['held'])
        new_exact = sum(h['score']['exact_certified_form'] for h in row['held'])
        old_pass = all(h['score']['exact_certified_form'] and
                       h['score']['certified_unit_span_f1'] >= 0.95 for h in before['held'])
        paired.append({'id': row['id'], 'old_exact': old_exact, 'new_exact': new_exact,
            'old_pass': old_pass, 'new_pass': row['passes'],
            'old_states': before['enumeration']['states'], 'new_states': row['states']})
    return {'stage': 'Descriptive post-fit audit; not a new qualification threshold or corpus hypothesis',
        'overlap': overlap, 'paired_baseline': paired,
        'paired_summary': {'old_cases_passing': sum(r['old_pass'] for r in paired),
            'new_cases_passing': sum(r['new_pass'] for r in paired),
            'cases_with_more_certified_forms': sum(r['new_exact'] > r['old_exact'] for r in paired),
            'cases_with_fewer_certified_forms': sum(r['new_exact'] < r['old_exact'] for r in paired),
            'cases_with_equal_certified_forms': sum(r['new_exact'] == r['old_exact'] for r in paired)},
        'interpretation': 'Forms are distinct from training forms, but short numeric strings can recur inside longer groups. No plaintext values are supplied to fitting. This is a known-vocabulary benchmark, not independent author/prose validation or novel raw-fragment evidence.'}


if __name__ == '__main__':
    result = json.loads((ROOT/'results/round27_qualification.json').read_text())
    baseline = json.loads((ROOT/'results/round27_baseline.json').read_text())
    out = audit(result, baseline)
    (ROOT/'results/round27_overlap_audit.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: {x:y for x,y in v.items() if x!='rows'} for k,v in out['overlap'].items()}, indent=2))
    print(json.dumps(out['paired_summary'], indent=2))
