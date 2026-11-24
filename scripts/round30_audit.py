#!/usr/bin/env python3
"""Offline closure audit; source agreement and imported labels are not translation."""
from collections import Counter, defaultdict
from pathlib import Path
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alignments(raw,codes):
    """Forward DP with saturated counts, independent of original recursive solver."""
    reachable={0:1}
    for code in codes:
        if len(code)!=2 or not code.isascii() or not code.isdigit():
            raise ValueError('Two ASCII digits per imported code required')
        following=defaultdict(int)
        for pos,count in reachable.items():
            if raw.startswith(code,pos):
                following[pos+2]=min(2,following[pos+2]+count)
            if code[0]=='0' and raw.startswith(code[1],pos):
                following[pos+1]=min(2,following[pos+1]+count)
        reachable=following
    return reachable.get(len(raw),0)


def integrity(root=ROOT):
    catalog=json.loads((root/'data/round30_manifest_catalog.json').read_text())
    cache={};rows=[]
    for name in catalog['checksummed_manifests']:
        manifest=json.loads((root/name).read_text())
        checks=[]
        for path,expected in manifest['sha256'].items():
            if path not in cache:cache[path]=digest(root/path) if (root/path).is_file() else None
            actual=cache[path]
            checks.append({'path':path,'expected':expected,'actual':actual,
                           'status':'match' if actual==expected else 'missing' if actual is None else 'mismatch'})
        rows.append({'manifest':name,'checks':checks})
    counts=Counter(c['status'] for row in rows for c in row['checks'])
    return {'scope':'Baseline path-to-SHA256 manifests only; no live network reauthentication',
            'manifest_count':len(rows),'reference_count':sum(counts.values()),
            'distinct_referenced_paths':len(cache),'statuses':dict(counts),
            'all_current_references_match':not(counts['missing'] or counts['mismatch']),
            'other_manifest_schemas':catalog['other_manifest_schemas'],'manifests':rows}


def corpus(root=ROOT):
    ref=root/'data/round30_reference'
    package=json.loads((ref/'SOURCES.json').read_text())
    for row in package['sources']:
        assert digest(root/row['path'])==row['sha256'],row['path']
    copies={}
    for name in ['s2ward','arturo','kimlage']:
        data=json.loads((ref/(name+'_books.json')).read_text())
        copies[name]=data if isinstance(data,list) else [data[str(i)] for i in range(len(data))]
    assert copies['s2ward']==copies['arturo']==copies['kimlage']
    raw_books=copies['s2ward']
    imported=json.loads((ref/'imported_tokens.json').read_text())['books']
    labels={}
    for row in csv.DictReader((ref/'imported_labels.csv').open()):
        codes,symbols=row['ordered_codes'].split('|'),row['ordered_labels'].split('|')
        assert len(codes)==len(symbols)
        for code,symbol in zip(codes,symbols):
            assert code not in labels or labels[code]==symbol
            labels[code]=symbol
    normalized=json.loads((root/'data/normalized_books.json').read_text())
    assert labels==json.loads((root/'data/normalized_code_map.json').read_text())
    assert len(raw_books)==len(normalized)==70
    rows=[]
    for i,(raw,record) in enumerate(zip(raw_books,normalized)):
        codes=imported[str(i)]
        assert raw and raw.isascii() and raw.isdigit()
        assert record['id']==str(i) and record['digits']==raw and record['codes']==codes
        assert ''.join(labels[c] for c in codes)==record['symbols']
        omitted=record['omitted_zero_code_indices'];selected=set(omitted)
        assert len(omitted)==len(selected) and all(0<=p<len(codes) and codes[p][0]=='0' for p in selected)
        assert ''.join(c[1:] if j in selected else c for j,c in enumerate(codes))==raw
        count=alignments(raw,codes)
        assert count>0 and count==record['alignment_count_capped_2']
        rows.append({'id':str(i),'digits':len(raw),'imported_codes':len(codes),
                     'omitted_zeros':len(omitted),'alignment_count_capped_2':count,
                     'raw_sha256':hashlib.sha256(raw.encode()).hexdigest()})
    result={'books':len(rows),'unique_digit_strings':len(set(raw_books)),
            'digits':sum(r['digits'] for r in rows),'imported_symbols':sum(r['imported_codes'] for r in rows),
            'omitted_leading_zeros':sum(r['omitted_zeros'] for r in rows),
            'observed_codes':len({c for seq in imported.values() for c in seq}),
            'label_alphabet':sorted(set(labels.values())),
            'ambiguous_alignment_book_ids':[r['id'] for r in rows if r['alignment_count_capped_2']==2],
            'three_original_digit_copies_equal':True,'normalized_records_equal':True,
            'rows':rows,'scope':'Independent byte/arithmetic reproduction from packaged original files. Imported segmentation and labels remain inputs; no live-game authenticity or English semantics implied.'}
    old=json.loads((root/'results/audit.json').read_text())
    assert result['digits']==old['digits']
    assert result['imported_symbols']==old['reconstruction']['symbol_count']
    assert result['omitted_leading_zeros']==old['reconstruction']['inserted_leading_zeros']
    assert result['ambiguous_alignment_book_ids']==old['reconstruction']['ambiguous_alignment_book_ids']
    return result


def verify_inputs(root=ROOT):
    for path,expected in json.loads((root/'data/round30_input_manifest.json').read_text())['sha256'].items():
        assert digest(root/path)==expected,path


if __name__=='__main__':
    verify_inputs()
    for name,operation in [('integrity',integrity),('corpus',corpus)]:
        target=ROOT/f'results/round30_{name}.json'
        if target.exists():raise ValueError('Refuse to overwrite closure audit')
        result=operation();target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(name,{k:v for k,v in result.items() if k not in ['manifests','rows','other_manifest_schemas']},flush=True)
