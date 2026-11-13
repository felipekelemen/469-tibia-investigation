#!/usr/bin/env python3
"""Round17: hidden vocabulary, train-only fits and prospectively frozen gate.

Fixture generator owns truth. The learner API receives raw digit messages
only. Qualification authors never select algorithm parameters.
"""
import argparse
import collections
import functools
import hashlib
import json
from pathlib import Path
import random
import re
import time

from hidden_unit_segmenter import (fit_bpe, fit_periodic, fit_unigram, segment)
from numeric_word_codec import complete_parse, unique_decodability

ROOT = Path(__file__).resolve().parents[1]
SEED = 17469486
FAMILIES = ('fixed2_character_units', 'variable3to8_word_units')
STYLES = ('contiguous', 'copied16chunks')
TARGETS = ('closed_later_source', 'permuted_closed_units')
DEV = ('data/word_validator_reference/wizard_oz.txt', 'data/word_validator_reference/peter_pan.txt')
QUAL = ('data/segmentation_reference/dorian_gray.txt', 'data/segmentation_reference/age_innocence.txt')


def load(path):
    return json.loads((ROOT / path).read_text())


def dump(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def fingerprint(obj):
    def rounded(x):
        if isinstance(x, dict):
            return {k: rounded(v) for k, v in x.items()}
        if isinstance(x, list):
            return [rounded(v) for v in x]
        return round(x, 10) if isinstance(x, float) else x
    return hashlib.sha256(json.dumps(rounded(obj), sort_keys=True).encode()).hexdigest()


@functools.lru_cache(maxsize=None)
def words(path):
    text = (ROOT / path).read_text(encoding='utf-8-sig')
    if '*** START OF THE PROJECT GUTENBERG' in text:
        text = text.split('*** START OF THE PROJECT GUTENBERG', 1)[1].split('***', 1)[1]
    if '*** END OF THE PROJECT GUTENBERG' in text:
        text = text.split('*** END OF THE PROJECT GUTENBERG', 1)[0]
    return re.findall('[a-z]+', text.lower())


def prefix_key(labels, rng):
    key = {}
    for label in sorted(labels):
        for _ in range(100000):
            code = ''.join(rng.choice('0123456789') for _ in range(rng.randrange(3, 9)))
            if all(not old.startswith(code) and not code.startswith(old) for old in key.values()):
                key[label] = code; break
        else:
            raise ValueError('prefix key budget exhausted')
    return key


def fixture(index, family, style, stage):
    refs = DEV if stage == 'development' else QUAL
    source = refs[index % 2]
    offset = 1000+(index//2)*2048 if stage == 'development' else 5000+(index//2)*512
    stream = words(source)[offset:offset+12000]
    if len(stream) != 12000:
        raise ValueError('reference too short for frozen fixture window')
    seed = SEED+(0 if stage == 'development' else 1000000)+index*100+FAMILIES.index(family)*10
    rng = random.Random(seed)
    if family == FAMILIES[0]:
        chars = ''.join(stream)
        count = 80
        base = [list(chars[i*count:(i+1)*count]) for i in range(70)]
        tail = list(chars[70*count:])
        values = rng.sample(range(100), 26)
        key = dict(zip('abcdefghijklmnopqrstuvwxyz', (f'{x:02d}' for x in values)))
    else:
        counts = collections.Counter(stream[:6000])
        top = sorted(counts, key=lambda w: (-counts[w], w))[:64]
        vocabulary = set(top)
        filtered = [w for w in stream if w in vocabulary]
        count = 32
        base = [filtered[i*count:(i+1)*count] for i in range(70)]
        tail = filtered[70*count:]
        key = prefix_key(vocabulary, rng)
    if any(len(s) != count for s in base):
        raise ValueError('short training messages')
    if style == STYLES[1]:
        choice = [rng.randrange(70) for _ in range(16)]
        base = [base[choice[i % 16]] for i in range(70)]
        rng.shuffle(base)
    seen = {unit for row in base for unit in row}
    later = [unit for unit in tail if unit in seen][:8*count]
    if len(later) != 8*count:
        raise ValueError('short closed target')
    permuted = list(later); random.Random(seed+50000).shuffle(permuted)
    train = [''.join(key[u] for u in row) for row in base]
    targets = {}
    for name, units in zip(TARGETS, (later, permuted)):
        rows = [units[i*count:(i+1)*count] for i in range(8)]
        targets[name] = [{'raw': ''.join(key[u] for u in row), 'true_units': [key[u] for u in row]} for row in rows]
    # Labels, true vocabulary and positions stay in the generator/scorer,
    # never in fit_family's arguments.
    return {'train': train, 'targets': targets, 'metadata': {
        'stage': stage, 'case': index, 'source': source, 'source_word_offset': offset,
        'seed': seed, 'family': family, 'training_style': style,
        'train_messages': len(train), 'distinct_train_messages': len(set(train)),
        'train_digits': sum(map(len, train)), 'seen_true_unit_types': len(seen),
        'train_sha256': fingerprint(train), 'target_sha256': fingerprint(targets),
        'true_key_sha256': fingerprint(key)}}


def metrics(targets, paths, model):
    true_bound, pred_bound, true_spans, pred_spans = set(), set(), set(), set()
    exact, in_lexicon, true_tokens = 0, 0, 0
    lexicon = set(model['units'])
    for ri, (row, path) in enumerate(zip(targets, paths)):
        if ''.join(path) != row['raw']:
            raise ValueError('learner changed target digits')
        exact += path == row['true_units']
        true_tokens += len(row['true_units'])
        in_lexicon += sum(w in lexicon for w in row['true_units'])
        for seq, cuts, spans in ((row['true_units'], true_bound, true_spans), (path, pred_bound, pred_spans)):
            pos = 0
            for unit in seq:
                end = pos+len(unit); spans.add((ri, pos, end))
                if end < len(row['raw']):
                    cuts.add((ri, end))
                pos = end
    def prf(truth, predicted):
        hits = len(truth & predicted)
        p, r = hits/max(1, len(predicted)), hits/max(1, len(truth))
        return {'precision': p, 'recall': r, 'f1': 2*p*r/(p+r) if p+r else 0.,
                'correct': hits, 'predicted': len(predicted), 'true': len(truth)}
    boundary, spans = prf(true_bound, pred_bound), prf(true_spans, pred_spans)
    return {'boundary': boundary, 'unit_span': spans, 'exact_messages': exact,
            'messages': len(targets), 'true_surface_in_model_fraction': in_lexicon/true_tokens,
            'passed': boundary['f1'] >= .95 and spans['f1'] >= .95}


def configs():
    result = [{'id': 'periodic_mdl', 'kind': 'periodic'}]
    for kind in ('bpe', 'unigram'):
        for budget in (128, 256):
            for dedup in (False, True):
                result.append({'id': f'{kind}_{budget}_'+('dedup' if dedup else 'weighted'),
                               'kind': kind, 'budget': budget, 'deduplicate': dedup})
    return result


def fit_family(train, config, cache):
    if config['kind'] == 'periodic':
        return fit_periodic(train)
    key = (config['budget'], config['deduplicate'])
    if key not in cache:
        cache[key] = fit_bpe(train, *key)
    base = cache[key]
    return base if config['kind'] == 'bpe' else fit_unigram(train, base)


def evaluate_fixture(f, config, cache, all_targets):
    model = fit_family(f['train'], config, cache)
    target_names = TARGETS if all_targets else TARGETS[:1]
    return {'config': config['id'], 'model_sha256': fingerprint(model),
            'learned_unit_count': len(model['units']), 'selected_width': model.get('width'),
            'targets': {name: metrics(f['targets'][name], [segment(row['raw'], model) for row in f['targets'][name]], model)
                        for name in target_names}}


def summarize(rows, config_id, target_style):
    out = []
    for family in FAMILIES:
        for style in STYLES:
            values = [next(v for v in r['fits'] if v['config'] == config_id)['targets'][target_style]
                      for r in rows if r['metadata']['family'] == family and r['metadata']['training_style'] == style]
            passed = sum(v['passed'] for v in values)
            out.append({'family': family, 'training_style': style, 'target_style': target_style,
                        'cases': len(values), 'passes': passed,
                        'mean_boundary_f1': sum(v['boundary']['f1'] for v in values)/len(values),
                        'mean_span_f1': sum(v['unit_span']['f1'] for v in values)/len(values),
                        'gate_passed': len(values) == 30 and passed >= 27})
    return out


def verify_inputs():
    for path, expected in load('data/round17_development_manifest.json')['sha256'].items():
        if sha(path) != expected:
            raise ValueError('frozen development input changed: '+path)


def freeze():
    if (ROOT / 'data/round17_development_manifest.json').exists():
        raise ValueError('already frozen')
    files = ['data/round17_protocol.json', 'scripts/hidden_unit_segmenter.py',
             'scripts/hidden_unit_benchmark.py', 'scripts/numeric_word_codec.py',
             'data/segmentation_reference/SOURCES.json', *DEV, *QUAL]
    dump('data/round17_development_manifest.json', {'stage': 'Before development and qualification',
                                                   'sha256': {p: sha(p) for p in files}})


def develop():
    verify_inputs()
    rows = []
    for i in range(8):
        for family in FAMILIES:
            for style in STYLES:
                f = fixture(i, family, style, 'development')
                cache = {}
                fits = [evaluate_fixture(f, c, cache, False) for c in configs()]
                rows.append({'metadata': f['metadata'], 'fits': fits})
        print('development case '+str(i)+' complete', flush=True)
    summaries = {c['id']: summarize(rows, c['id'], TARGETS[0]) for c in configs()}
    def rank(config):
        values = summaries[config['id']]
        means = [(v['mean_boundary_f1']+v['mean_span_f1'])/2 for v in values]
        return (-min(means), -sum(means)/len(means), config.get('budget', 0), config['id'])
    chosen = [configs()[0]]
    for kind in ('bpe', 'unigram'):
        chosen.append(min((c for c in configs() if c['kind'] == kind), key=rank))
    result = {'rows': rows, 'summaries': summaries, 'selected': chosen,
              'selection': 'Development only: highest worst-cell mean of boundary/spanF1, then macro mean, smaller budget, deterministic ID.'}
    dump('results/round17_development.json', result)
    manifest = load('data/round17_development_manifest.json')
    dump('data/round17_qualification_manifest.json', {'stage': 'Selected after development, before qualification',
        'selected': chosen, 'sha256': {**manifest['sha256'], 'results/round17_development.json': sha('results/round17_development.json')}})
    print('selected '+json.dumps(chosen), flush=True)


def adversarial_certificate():
    first, second = ['21', '34', '56'], ['2134', '56']
    training = ['2134', '562134', '2134562134']
    return {'dictionary_A': first, 'dictionary_B': second,
            'A_unique_decodability': unique_decodability(first), 'B_unique_decodability': unique_decodability(second),
            'training': [{'raw': raw, 'A': complete_parse(raw, first), 'B': complete_parse(raw, second)} for raw in training],
            'new_combination': {'raw': '2156', 'A': complete_parse('2156', first), 'B': complete_parse('2156', second)},
            'same_raw_different_boundaries': {'raw': '213456', 'A': complete_parse('213456', first), 'B': complete_parse('213456', second)},
            'scope': 'Two prefix-free lexicons explain identical training data with different unit boundaries. True unit count and English meanings not supplied. This is a constructive identifiability limit, not a claim about real469.'}


def qualification():
    for path, expected in load('data/round17_qualification_manifest.json')['sha256'].items():
        if sha(path) != expected:
            raise ValueError('qualification input changed: '+path)
    selected = load('data/round17_qualification_manifest.json')['selected']
    rows = []
    for i in range(30):
        for family in FAMILIES:
            for style in STYLES:
                f = fixture(i, family, style, 'qualification')
                cache = {}
                fits = [evaluate_fixture(f, c, cache, True) for c in selected]
                rows.append({'metadata': f['metadata'], 'fits': fits})
        print('qualification case '+str(i)+' complete', flush=True)
    summary = {c['id']: [v for t in TARGETS for v in summarize(rows, c['id'], t)] for c in selected}
    passing = [c['id'] for c in selected if all(v['gate_passed'] for v in summary[c['id']])]
    return {'rows': rows, 'summaries': summary, 'selected_configs': selected, 'all_cells_passing_learners': passing,
            'game_application': 'BLOCKED_QUALIFICATION_FAILED' if not passing else 'ELIGIBLE_FOR_NUMERIC_UNIT_INFERENCE_ONLY',
            'limits': ['No true vocabulary, key, count, labels or cuts supplied to learners.',
                       '30case windows overlap; keys independent, only2newauthors; copied training deliberate.',
                       'Variable targets are filtered English word streams, not coherent prose. Permuted controls preserve units, not grammar.',
                       'Closed targets contain only true units seen in train; no open-vocabulary robustness claim.',
                       'No zero omissions, variable framing, transposition or homophonic emissions in these fixtures.',
                       'Boundary recovery cannot identify English meanings. No game sample is semantic validation.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--develop', action='store_true')
    parser.add_argument('--qualify', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    elif args.develop:
        develop()
    elif args.qualify:
        if (ROOT / 'results/round17_qualification.json').exists():
            raise ValueError('qualification already opened; use replay script, never retune/reopen as new test')
        start = time.monotonic()
        result = qualification()
        dump('results/round17_qualification.json', result)
        dump('results/round17_identifiability_certificate.json', adversarial_certificate())
        dump('results/round17_execution.json', {'qualification_seconds': round(time.monotonic()-start, 3),
            'train_fits': 360, 'paired_target_evaluations': 720,
            'game_application': result['game_application'], 'verified_translations': 0})
        print('qualification complete '+result['game_application'], flush=True)
    else:
        parser.error('use --freeze, --develop or --qualify')
