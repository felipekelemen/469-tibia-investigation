#!/usr/bin/env python3
"""Natural-source fixtures selected by encoding eligibility, never solver score."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
from unit_morphism_lexicon import banks

ROOT = Path(__file__).resolve().parents[1]


def body(path):
    text = (ROOT / path).read_text().replace('\u2019', "'")
    start = re.search(r'\*\*\* START OF .*?\*\*\*', text)
    end = re.search(r'\*\*\* END OF .*?\*\*\*', text)
    if not start or not end or start.end() >= end.start():
        raise ValueError('Unrecognized Gutenberg boundaries: ' + path)
    return text[start.end():end.start()]


def words(text):
    return [w.replace("'", '').lower() for w in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)*", text)]


def merge_units(forms, maximum=30, protect=()):
    tokens = [list(w) for w in forms]
    for _ in range(maximum + 1):
        vocabulary = set(u for word in tokens for u in word)
        if len(vocabulary) <= 10 and any(len(u) > 1 for u in vocabulary):
            return tokens
        if _ == maximum:
            return None
        counts = Counter((a, b) for word in tokens for a, b in zip(word, word[1:])
                         if len(a + b) <= 3 and a not in protect and b not in protect)
        if not counts:
            return None
        choices = []
        for pair, frequency in counts.items():
            merged = []
            for word in tokens:
                out, i = [], 0
                while i < len(word):
                    if i + 1 < len(word) and (word[i], word[i + 1]) == pair:
                        out.append(word[i] + word[i + 1]); i += 2
                    else:
                        out.append(word[i]); i += 1
                merged.append(out)
            size = len(set(u for word in merged for u in word))
            choices.append((size, -frequency, pair, merged))
        tokens = min(choices)[3]
    return None


def assign(tokens, rng):
    vocabulary = sorted(set(u for word in tokens for u in word))
    labels = rng.sample(list('0123456789'), len(vocabulary))
    key = dict(zip(labels, vocabulary))
    inverse = {u: d for d, u in key.items()}
    raw = [''.join(inverse[u] for u in word) for word in tokens]
    return key, raw


def emit(raw, key):
    return ''.join(key[d] for d in raw)


def train_model(protocol, lexicon):
    output = ROOT / 'data/round35_reference'
    output.mkdir(exist_ok=True)
    counts, pairs = Counter(), Counter()
    for path in protocol['language_model_sources']:
        for sentence in re.split(r'[.!?]+', body(path)):
            tokens = words(sentence)
            if not tokens:
                continue
            counts.update(tokens)
            pairs.update(zip(['<s>'] + tokens, tokens))
    # Unknown CMU words retain smoothing; qualification text contributes nothing.
    vocabulary = ['<s>'] + lexicon
    index = {w: i for i, w in enumerate(vocabulary)}
    lines = [str(len(vocabulary))]
    starts = sum(c for (a, _), c in pairs.items() if a == '<s>')
    lines.extend(f'{w} {starts if w == "<s>" else counts[w]}' for w in vocabulary)
    eligible_pairs = [(index[a], index[b], c) for (a, b), c in pairs.items()
                      if a in index and b in index]
    lines.append(str(len(eligible_pairs)))
    lines.extend(f'{a} {b} {c}' for a, b, c in sorted(eligible_pairs))
    (output / 'language_model.txt').write_text('\n'.join(lines) + '\n')
    return len(eligible_pairs)


def prepare(protocol):
    rng = random.Random(protocol['fixtures']['seed'])
    lexicon = sorted(w.lower() for w in banks()[0]['grapheme1_3'].reverse)
    lexical = set(lexicon)
    model_pairs = train_model(protocol, lexicon)
    sources, base = [], {'v1': [], 'v2': []}
    used_forms = set()
    for path in protocol['qualification_sources']:
        all_sentences = [(i, words(s)) for i, s in enumerate(re.split(r'[.!?]+', body(path)))
                         if len(words(s)) == 7]
        rng.shuffle(all_sentences)
        selected = []
        reasons = Counter()
        for sentence_index, forms in all_sentences[:protocol['fixtures']['max_candidate_sentences_per_author']]:
            reasons['attempted'] += 1
            if tuple(forms) in used_forms:
                reasons['duplicate'] += 1; continue
            if not all(w in lexical for w in forms):
                reasons['outside_lexicon'] += 1; continue
            tokens = merge_units(forms, protocol['fixtures']['maximum_bpe_merges'])
            if tokens is None:
                reasons['greedy_encoder_no_inventory'] += 1; continue
            types = set(u for word in tokens for u in word)
            if len(types) < protocol['fixtures']['unit_types_minimum']:
                reasons['too_few_types'] += 1; continue
            key, raw = assign(tokens, rng)
            assert [emit(w, key) for w in raw] == forms
            digits = sorted(key)
            probes = []
            while len(probes) < protocol['fixtures']['probe_count']:
                p = ''.join(rng.choice(digits) for _ in range(protocol['fixtures']['probe_units']))
                if p not in raw and p not in probes:
                    probes.append(p)
            selected.append({'source': path, 'sentence_index': sentence_index,
                             'forms': forms, 'raw': raw, 'key': key,
                             'probes': probes, 'probe_truth': [emit(p, key) for p in probes]})
            used_forms.add(tuple(forms))
            if len(selected) == 30:
                break
        sources.append({'source': path, 'whole_seven_word_segments': len(all_sentences),
                        'eligibility_counts': dict(reasons), 'selected': len(selected)})
        if len(selected) != 30:
            raise ValueError('Frozen encoder eligibility quota not reached: ' + json.dumps(sources[-1]))
        base['v1'].extend(selected[:15]); base['v2'].extend(selected[15:])
    cases = []
    for version, examples in base.items():
        for i, original in enumerate(examples):
            record = dict(original, base_id=f'{version}_{i:02d}')
            for scenario in ['natural7', 'repeated21', 'unspaced', 'name_oov7',
                             'missing_digit', 'uniform_null', 'within_group_shuffle']:
                row = dict(record, id=f'{version}_{scenario}_{i:02d}', version=version,
                           scenario=scenario, input=list(original['raw']), expected=list(original['forms']))
                if scenario == 'repeated21':
                    row['input'] *= 3; row['expected'] *= 3
                elif scenario == 'unspaced':
                    row['input'] = [''.join(row['input'])]
                elif scenario == 'name_oov7':
                    # A synthetic proper-name token; never called natural-source prose.
                    digits = sorted(row['key'])
                    for _ in range(1000):
                        name_raw = ''.join(rng.choice(digits) for _ in range(5))
                        name = emit(name_raw, row['key'])
                        if name not in lexical:
                            break
                    else:
                        raise ValueError('Could not make an out-of-lexicon name')
                    row['input'][3] = name_raw; row['expected'][3] = name
                    row['synthetic_name'] = name
                elif scenario == 'missing_digit':
                    removed = min(row['key'], key=lambda d: (sum(d in w for w in row['input']), d))
                    kept = [(r, f) for r, f in zip(row['input'], row['expected']) if removed not in r]
                    assert kept
                    row['input'], row['expected'] = map(list, zip(*kept))
                    row['removed_digit'] = removed
                    row['probes'] = [removed + p for p in original['probes']]
                    row['probe_truth'] = [emit(p, row['key']) for p in row['probes']]
                elif scenario == 'uniform_null':
                    row['input'] = [''.join(str(rng.randrange(10)) for _ in w) for w in row['input']]
                    row['expected'] = None
                elif scenario == 'within_group_shuffle':
                    for _ in range(100):
                        shuffled = []
                        for w in row['input']:
                            chars = list(w); rng.shuffle(chars); shuffled.append(''.join(chars))
                        if shuffled != row['input']:
                            break
                    else:
                        raise ValueError('Ineffective shuffle control')
                    row['input'] = shuffled; row['expected'] = None
                cases.append(row)
        templates = protocol['ambiguous_templates']
        for i, sentence in enumerate(f'{a} {b}' for a in templates['frames'] for b in templates['objects']):
            forms = sentence.split()
            tokens = merge_units(forms, protect={'c'})
            if tokens is None:
                raise ValueError('Ambiguous template not encodable: ' + sentence)
            key, raw = assign(tokens, rng)
            digit = next(d for d in key if key[d] == 'c')
            alternative = dict(key); alternative[digit] = 'r'
            other = [emit(w, alternative) for w in raw]
            assert all(w in lexical for w in forms + other) and forms != other
            intended = key if rng.randrange(2) else alternative
            cases.append({'id': f'{version}_ambiguous_pair_{i:02d}', 'version': version,
                          'scenario': 'ambiguous_pair', 'input': raw,
                          'expected': [emit(w, intended) for w in raw], 'key': intended,
                          'alternative_keys': [key, alternative],
                          'alternative_plaintexts': [forms, other], 'probes': [], 'probe_truth': []})
    return {'seed': protocol['fixtures']['seed'], 'source_eligibility': sources,
            'language_model_sources': protocol['language_model_sources'],
            'lexical_forms': len(lexicon), 'language_model_pairs': model_pairs,
            'qualification_is_internal_not_external_blind': True, 'cases': cases}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-only', action='store_true')
    args = parser.parse_args()
    protocol = json.loads((ROOT / 'data/round35_protocol.json').read_text())
    if args.model_only:
        lexicon = sorted(w.lower() for w in banks()[0]['grapheme1_3'].reverse)
        print('Frozen model pairs:', train_model(protocol, lexicon))
        raise SystemExit(0)
    destination = ROOT / 'data/round35_fixtures.json'
    if destination.exists():
        raise ValueError('Do not overwrite frozen fixtures')
    result = prepare(protocol)
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'cases'}, indent=2))
    print('Cases:', len(result['cases']))
