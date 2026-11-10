#!/usr/bin/env python3
"""Audit community digit copies; reproduce (not semantically validate) row0.

No network, database, spreadsheet dependency. Run from any directory after cloning
sources. The recorded upstream tokenization is an input, not a discovered key.
"""
from pathlib import Path
from collections import Counter, defaultdict
from functools import lru_cache
import csv
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def align_omissions(digits, codes):
    """Find all possible leading-zero omission alignments, capped at 2.

    Return one path and capped solution count. Reject deletion of nonzero digits.
    The supplied two-digit code sequence remains fixed throughout.
    """
    @lru_cache(None)
    def solve(i, j):
        if j == len(codes):
            return ((), 1) if i == len(digits) else (None, 0)
        c = codes[j]
        choices = []
        if digits.startswith(c, i):
            choices.append((i + 2, False))
        if c.startswith('0') and digits.startswith(c[1], i):
            choices.append((i + 1, True))
        path, count = None, 0
        for end, omitted in choices:
            tail, n = solve(end, j + 1)
            if n:
                if path is None:
                    path = ((j,) if omitted else ()) + tail
                count = min(2, count + n)
        return path, count
    return solve(0, 0)


def shared_components(strings, k):
    owners = defaultdict(set)
    for i, s in enumerate(strings):
        for j in range(len(s) - k + 1):
            owners[s[j:j+k]].add(i)
    parent = list(range(len(strings)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for group in owners.values():
        first = next(iter(group))
        for item in group:
            parent[find(item)] = find(first)
    groups = defaultdict(list)
    for i in range(len(strings)):
        groups[find(i)].append(i)
    return sorted(groups.values(), key=lambda a: (-len(a), a))


def novel_fragments(strings, train_ids, test_ids, k=12):
    """Mask every held-out character in a k-mer seen in discovery books.

    Maximal remaining runs >= k are eligible. This guarantees zero shared
    k-mers, but does not imply statistical/semantic independence below k.
    """
    seen = {strings[i][p:p+k] for i in train_ids
            for p in range(len(strings[i])-k+1)}
    fragments = []
    for bid in test_ids:
        s = strings[bid]
        mask = [False]*len(s)
        for p in range(len(s)-k+1):
            if s[p:p+k] in seen:
                mask[p:p+k] = [True]*k
        start = 0
        while start < len(s):
            if mask[start]:
                start += 1
                continue
            end = start
            while end < len(s) and not mask[end]:
                end += 1
            if end-start >= k:
                fragments.append({'book_id': str(bid), 'start': start,
                                  'end': end, 'digits': s[start:end]})
            start = end
    return fragments


def run():
    paths = {'s2ward': ROOT/'sources/s2ward/books.json',
             'arturo': ROOT/'sources/arturo/data/books.json',
             'kimlage': ROOT/'sources/kimlage/analysis/audit_20260609/books_digits.json'}
    copies = {}
    for name, path in paths.items():
        raw = json.loads(path.read_text())
        copies[name] = raw if isinstance(raw, list) else [raw[str(i)] for i in range(len(raw))]
    books = copies['s2ward']
    assert len(books) == 70 and all(s and s.isascii() and s.isdigit() for s in books)
    corpus_path = ROOT/'sources/kimlage/analysis/audit_20260609/hs_corpus.json'
    tokens = json.loads(corpus_path.read_text())['books']
    table_path = ROOT/'sources/kimlage/analysis/row0_origin_parallel_20260621/data/row0_pair_table_canonical.csv'
    cmap = {}
    for row in csv.DictReader(table_path.open()):
        for code, symbol in zip(row['ordered_codes'].split('|'), row['ordered_labels'].split('|')):
            assert code not in cmap or cmap[code] == symbol
            cmap[code] = symbol
    records = []
    for i, digits in enumerate(books):
        codes = tokens[str(i)]
        assert all(len(c) == 2 and c.isdigit() for c in codes)
        omitted, npaths = align_omissions(digits, codes)
        assert npaths, f'book {i}: no legal zero-only alignment'
        symbols = ''.join(cmap[c] for c in codes)
        assert ''.join(c[1:] if j in omitted else c for j,c in enumerate(codes)) == digits
        records.append({'id': str(i), 'digits': digits, 'codes': codes,
                        'symbols': symbols, 'omitted_zero_code_indices': list(omitted),
                        'alignment_count_capped_2': npaths})
    containments = [[i,j] for i,s in enumerate(books) for j,t in enumerate(books)
                    if i != j and s in t]
    components = {str(k): shared_components(books,k) for k in [8,12,16,24,32,48]}
    # Reserve components under explicit >=16-digit criterion; never randomly split books.
    groups = components['16']
    heldout = []
    for group in reversed(groups):
        if len(heldout) + len(group) <= 14:
            heldout += group
    train = [i for i in range(70) if i not in heldout]
    fragments = novel_fragments(books, list(range(56)), list(range(56,70)))
    splits = {'criterion': 'No exact shared substring of >=16 digits across book groups; shorter leakage remains possible.',
              'discovery_book_ids': list(map(str,train)), 'holdout_book_ids': list(map(str,sorted(heldout))),
              'components_at_16_digits': groups,
              'fragment_protocol': {'discovery_book_ids': list(map(str,range(56))),
                    'candidate_holdout_book_ids': list(map(str,range(56,70))),
                    'mask_shared_kmer_length':12,
                    'warning':'Exploratory fragment split excludes exact >=12-digit reuse only; no ground truth; shorter or transformed repeats possible.',
                    'eligible_fragments':fragments}}
    provenance = {}
    for name, path in paths.items():
        repo = ROOT/'sources'/name
        provenance[name] = {'url': subprocess.check_output(['git','-C',str(repo),'remote','get-url','origin'],text=True).strip(),
                'commit': subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),
                'corpus_path':str(path.relative_to(repo)), 'sha256':digest(path),
                'same_order_and_content': copies[name] == books,
                'differences_at_book_ids':[i for i in range(min(len(books),len(copies[name]))) if copies[name][i] != books[i]],
                'book_count':len(copies[name])}
    result = {'book_count':len(books), 'digits':sum(map(len,books)),
              'unique_books':len(set(books)), 'odd_length_books':sum(len(s)%2 for s in books),
              'source_copies':provenance,
              'source_independence':'Copies share lineage; agreement does not verify against live game or historical screenshots.',
              'reconstruction':{'valid_books':len(records), 'symbol_count':sum(len(r['codes']) for r in records),
                    'inserted_leading_zeros':sum(len(r['omitted_zero_code_indices']) for r in records),
                    'ambiguous_alignment_book_ids':[r['id'] for r in records if r['alignment_count_capped_2']>1],
                    'observed_codes':len(set(c for r in records for c in r['codes'])),
                    'map_codes':len(cmap),'alphabet': sorted(set(cmap.values())),
                    'symbol_counts':dict(Counter(''.join(r['symbols'] for r in records))),
                    'token_input_sha256':digest(corpus_path),'map_input_sha256':digest(table_path),
                    'limitation':'Upstream token stream and labels imported; zero omission alignment independently checked. No semantic validity implied. Workbook decodedbase not independently compared: XLSX files are Git LFS pointers.'},
              'containment_pairs':containments,'contained_book_count':len({i for i,j in containments}),
              'overlap_component_sizes':{k:list(map(len,v)) for k,v in components.items()},
              'book_holdout_count_at_16':len(heldout),
              'novel_fragment_count_at_12':len(fragments),
              'novel_fragment_digit_count':sum(len(f['digits']) for f in fragments)}
    for path, obj in [('data/normalized_books.json',records),('data/normalized_splits.json',splits),
                      ('data/normalized_code_map.json',cmap),('results/audit.json',result)]:
        target=ROOT/path; target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_copies','containment_pairs']},indent=2))
    return result

if __name__ == '__main__':
    run()
