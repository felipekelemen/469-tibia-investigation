#!/usr/bin/env python3
"""Complete finite search of whole-integer codecs on priority sources and nulls."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import random
import re
from round28_radix import CODECS, FRAMINGS, KEYS, Lexicon, fit, literal_output, predict, values

ROOT = Path(__file__).resolve().parents[1]


def verify_inputs():
    manifest = json.loads((ROOT/'data/round28_experiment_manifest.json').read_text())
    for path, sha in manifest['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != sha:
            raise ValueError('Changed frozen input: '+path)


def source_inputs():
    inventory = {r['id']: r for r in json.loads((ROOT/'data/source_validation_inventory.json').read_text())}
    result = {}
    for name in ('knightmare_2012', 'avar_tar_poem'):
        result[name] = {'raw_text': inventory[name]['text'],
                        'groups': re.findall(r'[0-9]+', inventory[name]['text'])}
    first, second = (inventory['chayenne_2009_part'+str(i)]['text'] for i in (1, 2))
    result['chayenne_2009'] = {'raw_text': first+' :) '+second+' xD', 'groups': [first, second]}
    return result


def identifier(codec, framing, key):
    return f'{codec}/{framing}/{key[0]}/{key[1]}'


def full_scan(sources, lexicon, details):
    rows, config_sources = {}, Counter()
    for name, source in sources.items():
        rows[name] = []
        for codec in CODECS:
            for framing in FRAMINGS:
                solved = fit(source['groups'], codec, framing, lexicon)
                for key in solved['keys']:
                    config_sources[identifier(codec, framing, key)] += 1
                if not details:
                    solved.pop('first_failure_per_key')
                rows[name].append(solved)
    return {'sources': rows,
            'maximum_fully_lexical_sources_one_config': max(config_sources.values(), default=0),
            'shared_configs_all_sources': sorted(k for k, n in config_sources.items() if n == len(sources)),
            'source_counts_per_surviving_config': dict(sorted(config_sources.items()))}


def copies(books, groups):
    out = []
    for raw in groups:
        hits = []
        for book in books:
            start = book['digits'].find(raw)
            while start >= 0:
                hits.append({'book_id': book['id'], 'raw_start': start})
                start = book['digits'].find(raw, start+1)
        out.append({'raw': raw, 'length': len(raw), 'occurrences': hits})
    return out


def real_search(protocol, sources, books, lexicon):
    full = full_scan(sources, lexicon, details=True)
    discoveries, candidates = [], []
    for name in protocol['real_order']:
        groups = sources[name]['groups']
        for solved in full['sources'][name]:
            codec, framing = solved['codec'], solved['framing']
            cut = 10 if name == 'avar_tar_poem' else 1 if name == 'chayenne_2009' else len(groups)
            split = framing == 'runs' and cut < len(groups)
            train, held = (groups[:cut], groups[cut:]) if split else (groups, [])
            discovery = fit(train, codec, framing, lexicon) if split else solved
            predictions = {other: predict(source['groups'], codec, framing, discovery['keys'], lexicon)
                           for other, source in sources.items() if other != name}
            discoveries.append({'source': name, 'codec': codec, 'framing': framing,
                'training_groups': train, 'held_groups': held,
                'discovery_same_as_full': not split,
                'discovery': discovery if split else None,
                'discovery_keys': discovery['keys'],
                'own_held_prediction': predict(held, codec, framing, discovery['keys'], lexicon) if held else None,
                'cross_source_predictions': predictions})
            for key in solved['keys']:
                candidates.append({'source': name, 'codec': codec, 'framing': framing,
                    'key': key, 'config_id': identifier(codec, framing, key),
                    'literal_output': literal_output(groups, codec, framing, key, lexicon),
                    'status': 'conditional_lexical_witness_not_validated_translation'})
    by_config = {c['config_id']: c for c in candidates}
    book_transfer = []
    for config, candidate in sorted(by_config.items()):
        book_transfer.append({'config_id': config, 'role': 'Exposed dependent corpus; not semantic validation',
            'books': [{'id': book['id'], **literal_output([book['digits']], candidate['codec'],
                       candidate['framing'], candidate['key'], lexicon)} for book in books]})
    name_lengths = {codec: {'3478_symbols': len(values('3478', codec)),
                           'BEHOLDER_letters': 8, 'BONELORD_letters': 8,
                           'affine_keys_preserve_length': True} for codec in CODECS}
    return {'round': 28, 'translation_validated': False, 'raw_sources': sources,
        'full_source_search': full, 'discoveries': discoveries,
        'lexical_candidates': candidates, 'book_transfer': book_transfer,
        'book_transfer_status': 'performed_for_all_full_source_configs' if candidates else 'not_performed_no_full_source_config',
        'chayenne_copy_audit': copies(books, sources['chayenne_2009']['groups']),
        'name_length_certificate': name_lengths,
        'parameter_accounting': {'shared_fixed_code_bits':12, 'independent_source_code_bits':36,
            'coding':'codec2bits + framing1bit + a-index4bits + b5bits. Unused bit patterns rejected.',
            'scope':'Parameter field only; excludes program, dictionary, data and framing costs. Not MDL evidence for original authorship.'}}


def alter(groups, family, rng, books):
    if family == 'uniform':
        return [''.join(rng.choice('0123456789') for _ in group) for group in groups]
    if family == 'global_shuffle':
        digits = list(''.join(groups))
        rng.shuffle(digits)
        out, offset = [], 0
        for group in groups:
            out.append(''.join(digits[offset:offset+len(group)]))
            offset += len(group)
        return out
    mapping = {}
    for group in dict.fromkeys(groups):
        if family == 'distinct_group_shuffle':
            digits = list(group)
            rng.shuffle(digits)
            mapping[group] = ''.join(digits)
        elif family == 'book_substrings':
            eligible = [book['digits'] for book in books if len(book['digits']) >= len(group)]
            source = rng.choice(eligible)
            start = rng.randrange(len(source)-len(group)+1)
            mapping[group] = source[start:start+len(group)]
        else:
            raise ValueError('Undeclared null family')
    return [mapping[group] for group in groups]


def null_search(protocol, sources, books, lexicon, real_stat):
    rng = random.Random(protocol['nulls']['seed'])
    results = {}
    for family in protocol['nulls']['families']:
        rows = []
        for index in range(protocol['nulls']['replicates_each']):
            modified = {name: {'groups': alter(source['groups'], family, rng, books)}
                        for name, source in sources.items()}
            scan = full_scan(modified, lexicon, details=False)
            rows.append({'replicate': index, 'groups': {k: v['groups'] for k, v in modified.items()},
                'changed': {k: v['groups'] != sources[k]['groups'] for k, v in modified.items()},
                'scan': scan})
            if (index+1)%10 == 0:
                print('null', family, index+1, flush=True)
        statistics = [r['scan']['maximum_fully_lexical_sources_one_config'] for r in rows]
        results[family] = {'replicates': len(rows), 'maximum_statistic_histogram': dict(Counter(statistics)),
            'plus_one_upper_tail': (1+sum(v >= real_stat for v in statistics))/(len(rows)+1),
            'changed_sources': {k: sum(r['changed'][k] for r in rows) for k in sources},
            'distinct_outputs': {k: len({tuple(r['groups'][k]) for r in rows}) for k in sources}, 'rows': rows}
    return {'statistic': 'Max number of fully lexically compatible sources under one of all1872configurations; not English/meaning likelihood',
            'real_statistic': real_stat, 'families': results}


if __name__ == '__main__':
    verify_inputs()
    protocol = json.loads((ROOT/'data/round28_protocol.json').read_text())
    # Qualification completed before examining target outputs, even though exact
    # finite-model incompatibility does not inherit a semantic qualification.
    qualification = json.loads((ROOT/'results/round28_qualification.json').read_text())
    assert len(qualification['cases']) == 540
    lexicon = Lexicon()
    sources = source_inputs()
    books = json.loads((ROOT/'data/normalized_books.json').read_text())
    target_path, null_path = ROOT/'results/round28_targets.json', ROOT/'results/round28_nulls.json'
    if target_path.exists() or null_path.exists():
        raise ValueError('Refusing to replace results')
    real = real_search(protocol, sources, books, lexicon)
    target_path.write_text(json.dumps(real, ensure_ascii=False, indent=2)+'\n')
    print('Full-source lexical witnesses:', len(real['lexical_candidates']), flush=True)
    nulls = null_search(protocol, sources, books, lexicon,
                       real['full_source_search']['maximum_fully_lexical_sources_one_config'])
    null_path.write_text(json.dumps(nulls, ensure_ascii=False, indent=2)+'\n')
    print('Finished complete finite real/null search', flush=True)
