#!/usr/bin/env python3
"""Round16 finite numeric-group dictionaries. No English meanings inferred.

--freeze binds protocol/code/data before new corpus statistics. --check
regenerates every result, including all randomized dictionaries.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import random
import re
import time

from numeric_word_codec import (complete_parse, decode_dictionary, decode_wire,
    dictionary_wire, parse_and_encode, unique_decodability)
from zero_rule_constraints import alignments

ROOT = Path(__file__).resolve().parents[1]
SEED = 16486486
MODELS = ('all_groups', 'length_at_least3', 'without_two_copied_wrinkled_shouts',
          'length_at_least3_without_two_copied_wrinkled_shouts')
KINDS = ('global_digit_bijection_of_dictionary_only', 'shuffle_digits_inside_each_distinct_group',
         'uniform_distinct_training_book_substrings_matched_by_length')
ABLATE = ('wrinkled_shout_1', 'wrinkled_shout_2')


def load(path):
    return json.loads((ROOT / path).read_text())


def dump(path, obj):
    (ROOT / path).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def inventory():
    entries = [r for r in load('data/source_validation_inventory.json')
               if r['canonical_candidate'] and r['modality'] != 'developer_interview']
    provenance = collections.defaultdict(list)
    for entry in entries:
        for i, word in enumerate(re.findall(r'\d+', entry['text'])):
            provenance[word].append({'id': entry['id'], 'source_group': entry['source_group'], 'group_index': i})
    return entries, [{'wire': w, 'provenance': provenance[w]} for w in sorted(provenance)]


def dictionaries(groups, mapping=None):
    mapping = mapping or {r['wire']: r['wire'] for r in groups}
    ablated = {r['wire'] for r in groups if any(p['id'] in ABLATE for p in r['provenance'])}
    return {name: sorted(mapping[r['wire']] for r in groups
                         if ('length_at_least3' not in name or len(r['wire']) >= 3)
                         and ('without_' not in name or r['wire'] not in ablated)) for name in MODELS}


def evaluate(books, words, split, keep=False):
    wordbits = dictionary_wire(words)
    if keep:
        assert decode_dictionary(wordbits) == sorted(words)
    records = []
    for b in books:
        row = parse_and_encode(b['digits'], words, keep_wire=keep)
        row['id'] = b['id']
        if keep:
            assert decode_wire(row['wire'], words) == b['digits']
            row['complete_word_only_parse_count'] = complete_parse(b['digits'], words)['count']
        records.append(row)
    baseline = sum(r['raw_bits'] for r in records)
    coded = sum(r['coded_bits'] for r in records)
    uncovered = sum(r['minimum_uncovered_digits'] for r in records)
    summary = {'dictionary_units': len(words), 'dictionary_bits': len(wordbits),
               'baseline_bits': baseline, 'conditional_book_bits': coded,
               'standalone_bits': coded+len(wordbits), 'net_saved_bits': baseline-coded-len(wordbits),
               'conditional_saved_bits': baseline-coded, 'minimum_uncovered_digits': uncovered,
               'minimum_covered_fraction': 1-uncovered/sum(len(b['digits']) for b in books),
               'complete_word_only_books': sum(r['minimum_uncovered_digits'] == 0 for r in records),
               'books_using_reference_codec': sum(r['uses_references'] for r in records)}
    for label in ('discovery', 'holdout'):
        subset = [r for r in records if r['id'] in split[label+'_book_ids']]
        summary[label+'_exposed_conditional_saved_bits'] = sum(r['raw_bits']-r['coded_bits'] for r in subset)
        summary[label+'_minimum_uncovered_digits'] = sum(r['minimum_uncovered_digits'] for r in subset)
    return {'summary': summary, 'dictionary': sorted(words), 'dictionary_wire': wordbits,
            'books': records} if keep else summary


def substring_pools(books, lengths):
    pools = {}
    for length in lengths:
        counter = collections.Counter(b['digits'][i:i+length] for b in books
                                      for i in range(len(b['digits'])-length+1))
        pools[length] = counter
    return pools


def frequency_dictionary(words, pools):
    out = []
    for length, count in sorted(collections.Counter(map(len, words)).items()):
        ordered = sorted(pools[length], key=lambda w: (-pools[length][w], w))
        if len(ordered) < count:
            raise ValueError('not enough training substrings')
        out.extend(ordered[:count])
    return sorted(out)


def control_mapping(groups, kind, pools, rng):
    words = [r['wire'] for r in groups]
    if kind == KINDS[0]:
        labels = list('0123456789'); rng.shuffle(labels)
        table = str.maketrans('0123456789', ''.join(labels))
        return {w: w.translate(table) for w in words}
    if kind == KINDS[2]:
        result = {}
        for length in sorted(set(map(len, words))):
            source = [w for w in words if len(w) == length]
            drawn = rng.sample(sorted(pools[length]), len(source))
            result.update(zip(source, drawn))
        return result
    result, used = {}, set()
    for word in words:
        for _ in range(100000):
            digits = list(word); rng.shuffle(digits)
            candidate = ''.join(digits)
            if candidate not in used:
                result[word] = candidate; used.add(candidate); break
        else:
            raise ValueError('control resampling budget exhausted')
    return result


def source_transfer(entries, groups):
    all_words = [r['wire'] for r in groups]
    full = []
    for r in entries:
        true = re.findall(r'\d+', r['text'])
        parse = complete_parse(''.join(true), all_words)
        if parse['count'] == 1:
            assert parse['unique_path'] == true
        full.append({'id': r['id'], 'observed_numeric_groups': true, 'unspaced_parse_count': parse['count'],
                     'unique_matches_recorded_spaces': parse['unique_path'] == true})
    leaveout = []
    for source in sorted({r['source_group'] for r in entries}):
        train = {w for r in entries if r['source_group'] != source for w in re.findall(r'\d+', r['text'])}
        train_raw = {''.join(re.findall(r'\d+', r['text'])) for r in entries if r['source_group'] != source}
        for r in entries:
            if r['source_group'] != source:
                continue
            true = re.findall(r'\d+', r['text']); raw = ''.join(true)
            partial = parse_and_encode(raw, train, keep_wire=False)
            leaveout.append({'held_source_group': source, 'id': r['id'],
                             'whole_utterance_reused_elsewhere': raw in train_raw,
                             'seen_numeric_groups': [w for w in true if w in train],
                             'unseen_numeric_groups': [w for w in true if w not in train],
                             'minimum_uncovered_digits': partial['minimum_uncovered_digits'],
                             'complete_unspaced_parse_count': complete_parse(raw, train)['count']})
    return {'same_inventory_consistency': full, 'leave_entire_source_out': leaveout,
            'scope': 'Already exposed groups; exact repeated words are flagged. No held English labels, semantics or new independent validation.'}


def boundary_diagnostic(books, groups):
    boundaries = {}
    for b in books:
        alignment = alignments(b)
        if not alignment['enumeration_complete']:
            raise ValueError('incomplete imported alignment enumeration')
        arrays = []
        for omitted in alignment['paths']:
            omit = set(omitted); offsets = [0]
            for i in range(len(b['codes'])):
                offsets.append(offsets[-1]+(1 if i in omit else 2))
            arrays.append(set(offsets))
        boundaries[b['id']] = arrays
    rows, contexts = [], {}
    for group in groups:
        word = group['wire']
        if len(word) < 3:
            continue
        for b in books:
            start = b['digits'].find(word)
            while start >= 0:
                end = start+len(word)
                yes = sum(start in offsets and end in offsets for offsets in boundaries[b['id']])
                total = len(boundaries[b['id']])
                label = 'all_alignments' if yes == total else 'some_alignments' if yes else 'no_alignment'
                row = {'word': word, 'book_id': b['id'], 'start': start, 'end': end,
                       'supporting_alignments': yes, 'total_alignments': total, 'endpoint_class': label,
                       'left8': b['digits'][max(0, start-8):start], 'right8': b['digits'][end:end+8]}
                rows.append(row)
                key = (word, row['left8'], row['right8'])
                state = contexts.setdefault(key, {'word': word, 'left8': row['left8'], 'right8': row['right8'],
                                                  'book_ids': set(), 'classes': set(), 'occurrences': 0})
                state['book_ids'].add(b['id']); state['classes'].add(label); state['occurrences'] += 1
                start = b['digits'].find(word, start+1)
    unique = [{**v, 'book_ids': sorted(v['book_ids']), 'classes': sorted(v['classes'])} for _, v in sorted(contexts.items())]
    return {'occurrences': rows, 'distinct_contexts': unique,
            'alignment_total': sum(map(len, boundaries.values())),
            'occurrence_endpoint_classes': dict(collections.Counter(r['endpoint_class'] for r in rows)),
            'word_occurrence_counts': dict(collections.Counter(r['word'] for r in rows)),
            'scope': 'Conditional imported-code endpoint compatibility, not proof a matching substring is a real word occurrence. Context deduplication is descriptive, not independence.'}


def prefix_key(labels, rng, first_digits='0123456789'):
    out = {}
    for label in labels:
        for _ in range(100000):
            length = rng.randrange(3, 11)
            word = rng.choice(first_digits)+''.join(rng.choice('0123456789') for _ in range(length-1))
            if all(not word.startswith(old) and not old.startswith(word) for old in out.values()):
                out[label] = word; break
        else:
            raise ValueError('positive key generation exhausted')
    return out


def qualification():
    rng = random.Random(SEED)
    references = {name: re.findall('[a-z]+', (ROOT / 'data/word_validator_reference' / name).read_text(encoding='utf-8-sig').lower())
                  for name in ('wizard_oz.txt', 'peter_pan.txt')}
    cases = []
    for trial in range(30):
        author = list(references)[trial % 2]
        start = 1000+(trial//2)*240
        plain = references[author][start:start+120]
        if len(plain) != 120:
            raise ValueError('short qualification reference')
        copied = plain[:60]*2
        labels = sorted(set(plain))
        for kind in ('prefix_free', 'nonprefix_uniquely_decodable', 'planted_ambiguity'):
            if kind == 'prefix_free':
                key = prefix_key(labels, rng)
            elif kind == 'nonprefix_uniquely_decodable':
                key = {labels[0]: '0', labels[1]: '01', **prefix_key(labels[2:], rng, '23456789')}
            else:
                key = {labels[0]: '2', labels[1]: '3', labels[2]: '23', **prefix_key(labels[3:], rng, '456789')}
            ud = unique_decodability(key.values())
            assert ud['uniquely_decodable'] == (kind != 'planted_ambiguity')
            for style, text in (('contiguous_English_words', plain), ('copied_English_word_chunks', copied)):
                text = [labels[2]]+text[1:] if kind == 'planted_ambiguity' else text
                units = [key[w] for w in text]
                raw = ''.join(units)
                parsed = complete_parse(raw, key.values())
                packed = parse_and_encode(raw, key.values())
                roundtrip = decode_wire(packed['wire'], key.values()) == raw
                success = parsed['count'] > 1 if kind == 'planted_ambiguity' else parsed['unique_path'] == units
                cases.append({'case': trial, 'reference': author, 'word_start': start, 'kind': kind, 'style': style,
                              'dictionary_units': len(key), 'parse_count': parsed['count'],
                              'success': success, 'wire_roundtrip': roundtrip,
                              'raw_sha256': hashlib.sha256(raw.encode()).hexdigest()})
    summary = []
    for kind in ('prefix_free', 'nonprefix_uniquely_decodable', 'planted_ambiguity'):
        for style in ('contiguous_English_words', 'copied_English_word_chunks'):
            rows = [r for r in cases if (r['kind'], r['style']) == (kind, style)]
            passed = sum(r['success'] for r in rows)
            summary.append({'kind': kind, 'style': style, 'cases': len(rows), 'successes': passed,
                            'gate_passed': passed >= 27 and all(r['wire_roundtrip'] for r in rows)})
    return {'summary': summary, 'cases': cases,
            'scope': '30 paired base passages x3 supplied codebooks x2 word-stream styles. Qualifies exact numeric-unit parsing and ambiguity detection with known dictionary only. No key/dictionary/English-meaning inference.'}


def build():
    qual = qualification()
    if not all(r['gate_passed'] for r in qual['summary']):
        raise ValueError('supplied-dictionary parser qualification gate failed')
    print('Qualification passed: 180 supplied-dictionary targets; no meaning inference.', flush=True)
    entries, groups = inventory()
    books, split = load('data/normalized_books.json'), load('data/normalized_splits.json')
    dicts = dictionaries(groups)
    train = [b for b in books if b['id'] in split['discovery_book_ids']]
    pools = substring_pools(train, sorted({len(g['wire']) for g in groups}))
    observed = {name: evaluate(books, words, split, True) for name, words in dicts.items()}
    baseline = {name: evaluate(books, frequency_dictionary(words, pools), split, True) for name, words in dicts.items()}
    controls = []
    observed_max = max(r['summary']['net_saved_bits'] for r in observed.values())
    for ki, kind in enumerate(KINDS):
        rng = random.Random(SEED+ki)
        trials = []
        for trial in range(99):
            mapping = control_mapping(groups, kind, pools, rng)
            null_dicts = dictionaries(groups, mapping)
            assert len(set(mapping.values())) == len(groups)
            stats = {name: evaluate(books, words, split) for name, words in null_dicts.items()}
            trials.append({'trial': trial, 'dictionaries_sha256': hashlib.sha256(json.dumps(mapping, sort_keys=True).encode()).hexdigest(),
                           'models': stats, 'max_net_saved_bits': max(r['net_saved_bits'] for r in stats.values())})
        p = (1+sum(t['max_net_saved_bits'] >= observed_max for t in trials))/100
        controls.append({'kind': kind, 'trials': trials, 'max_family_empirical_p': p,
                         'individual_p': {name: (1+sum(t['models'][name]['net_saved_bits'] >= row['summary']['net_saved_bits'] for t in trials))/100
                                          for name, row in observed.items()}})
        print(kind+' complete', flush=True)
    return {'results/round16_wordcode_transfer.json': {
                'observed': observed, 'training_substring_frequency_baselines': baseline,
                'nulls': controls, 'max_observed_net_saved_bits': observed_max,
                'scope': 'Finite incomplete numeric dictionary only; whole-corpus exploratory max, all70 books exposed and copied. Never a detector of English or proof against a larger word codebook.'},
            'results/round16_decodability.json': {'dictionaries': {name: unique_decodability(words) for name, words in dicts.items()},
                                                 'source_transfer': source_transfer(entries, groups)},
            'results/round16_boundaries.json': boundary_diagnostic(books, groups),
            'results/round16_qualification.json': qual}


def freeze():
    _, groups = inventory()
    dump('data/round16_numeric_groups.json', groups)
    files = ['data/round16_protocol.json', 'data/round16_numeric_groups.json',
             'scripts/numeric_word_codec.py', 'scripts/wordcode_transfer_experiment.py',
             'scripts/zero_rule_constraints.py', 'data/normalized_books.json', 'data/normalized_splits.json',
             'data/source_validation_inventory.json', 'data/word_validator_reference/wizard_oz.txt',
             'data/word_validator_reference/peter_pan.txt']
    dump('data/round16_evidence_manifest.json', {'stage': 'Frozen before new game statistics',
                                              'sha256': {p: sha(p) for p in files}})
    print('Frozen numeric groups:' + str(len(groups)), flush=True)


def main(check=False):
    for path, expected in load('data/round16_evidence_manifest.json')['sha256'].items():
        if sha(path) != expected:
            raise ValueError('frozen artifact changed: '+path)
    if check:
        for path, expected in load('data/round16_result_manifest.json')['sha256'].items():
            if sha(path) != expected:
                raise ValueError('published result changed: '+path)
    started = time.monotonic()
    artifacts = build()
    for path, obj in artifacts.items():
        if check:
            if load(path) != obj:
                raise ValueError('full replay changed: '+path)
        else:
            dump(path, obj)
    if not check:
        dump('results/round16_execution.json', {'duration_seconds': round(time.monotonic()-started, 3),
             'frozen_manifest_sha256': sha('data/round16_evidence_manifest.json'),
             'numeric_groups': len(inventory()[1]), 'qualification_targets': 180,
             'randomized_dictionaries': 297, 'randomized_model_evaluations': 1188,
             'verified_translations': 0})
    print('Round16 '+('full replay matched.' if check else 'completed. No English meaning inferred.'), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.freeze:
        freeze()
    elif args.run or args.check:
        main(args.check)
    else:
        parser.error('use --freeze, --run or --check')
