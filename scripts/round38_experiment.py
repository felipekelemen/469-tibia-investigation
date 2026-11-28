#!/usr/bin/env python3
"""Complete conditional key census, fixed controls, and unranked transfer diagnostics."""
import argparse
from collections import Counter
import gzip
import itertools
import json
from pathlib import Path
import random
import re
import resource
import subprocess
import tempfile
import time

from round36_experiment import ROOT, decode_key, emit, load, verify
from unit_morphism_lexicon import banks


def save(path, value):
    path = Path(path)
    data = (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix == '.gz':
        data = gzip.compress(data,mtime=0)
    with path.open('xb') as f:
        f.write(data)


def prepare_qualification():
    protocol = load('data/round38_protocol.json')['qualification']
    rng = random.Random(protocol['seed'])
    units = [''.join(s) for n in range(1,4) for s in itertools.product('AB',repeat=n)]
    pool = [''.join(s) for n in range(1,7) for s in itertools.product('AB',repeat=n)]
    cases = []
    for i in range(protocol['small_cases']):
        groups = list(dict.fromkeys(''.join(rng.choice('012') for _ in range(rng.randint(1,4))) for _ in range(rng.randint(2,5))))
        key = {d:rng.choice(units) for d in sorted(set(''.join(groups)))}
        lex = set(rng.sample(pool,15))
        anchor = emit(groups[0],key) if i%2 == 0 else rng.choice(pool)
        if i%2 == 0:
            lex.update(emit(g,key) for g in groups)
        else:
            lex.add(anchor)
        cases.append({'id':f'tiny_{i:02d}','groups':groups,'anchor_index':0,'anchor_word':anchor,
                      'lexicon':sorted(lex),'true_key':key if i%2 == 0 else None})
    groups = load('data/round38_fixtures.json')['real']['groups']
    for i in range(protocol['topology_cases']):
        key = {d:'A'*rng.randint(1,3) for d in sorted(set(''.join(groups)))}
        lex = {'A'*n for n in range(1,16) if rng.random()<.6}
        lex.update(emit(g,key) for g in groups)
        cases.append({'id':f'topology_{i:02d}','groups':groups,'anchor_index':6,
                      'anchor_word':emit(groups[6],key),'lexicon':sorted(lex),'true_key':key})
    return cases


def canonical(key):
    return tuple(sorted(key.items()))


def brute(case):
    lex = set(case['lexicon'])
    alphabet = sorted(set(''.join(lex)))
    units = [''.join(s) for n in range(1,4) for s in itertools.product(alphabet,repeat=n)]
    digits = sorted(set(''.join(case['groups'])))
    answer = set()
    for values in itertools.product(units,repeat=len(digits)):
        key = dict(zip(digits,values))
        if emit(case['groups'][case['anchor_index']],key) != case['anchor_word']:
            continue
        if all(emit(g,key) in lex for g in case['groups']):
            answer.add(canonical(key))
    return answer


def invoke(binary, lexpath, case, directory, with_keys):
    protocol = load('data/round38_protocol.json')['budgets']
    path = directory/'input.txt'
    path.write_text(f"{len(case['groups'])} {case['anchor_index']} {case['anchor_word']}\n"+'\n'.join(case['groups'])+'\n')
    def cap():
        resource.setrlimit(resource.RLIMIT_AS,(protocol['address_space_bytes'],protocol['address_space_bytes']))
    started = time.monotonic()
    try:
        p = subprocess.run([str(binary),str(lexpath),str(path),str(int(with_keys))],
                           capture_output=True,text=True,timeout=protocol['per_fit_wall_seconds'],preexec_fn=cap)
        result = json.loads(p.stdout) if p.returncode == 0 else {'complete':False,'count':None,'reason':'process_failure'}
    except subprocess.TimeoutExpired:
        result = {'complete':False,'count':None,'reason':'wall_limit'}
    return result, time.monotonic()-started


def segment_count(form, lexicon, lengths=None):
    if lengths is None:
        lengths = sorted({len(w) for w in lexicon})
    ways = [0]*(len(form)+1)
    ways[0] = 1
    for end in range(1,len(form)+1):
        for n in lengths:
            if n>end:break
            if ways[end-n] and form[end-n:end] in lexicon:
                ways[end] += ways[end-n]
    return ways[-1]


def inspect_keys(codes, fixtures, lexicon):
    keys = [decode_key(k) for k in codes]
    words = fixtures['real']['groups']
    assert len(keys) == len({canonical(k) for k in keys}) == 3976
    for key in keys:
        assert set(key) == set(''.join(words))
        assert emit('345',key) == 'FOOL'
        assert all(emit(g,key) in lexicon for g in words)
    frequencies = Counter()
    for source in load('data/round38_protocol.json')['word_attestation_sensitivity']['sources']:
        frequencies.update(re.findall('[A-Za-z]+',(ROOT/source).read_text().upper()))
    training = [tuple(emit(g,k) for g in words) for k in keys]
    hist = [Counter(row[i] for row in training) for i in range(len(words))]
    group_records = [{'raw':g,'word_forms':len(h),'forms':dict(sorted(h.items())),
                      'forms_attested_in_reference':{w:frequencies[w] for w in sorted(h) if frequencies[w]}} for g,h in zip(words,hist)]
    records, segment_cache = [], {}
    lengths = sorted({len(w) for w in lexicon})
    def paths(form):
        if form not in segment_cache:segment_cache[form]=segment_count(form,lexicon,lengths)
        return segment_cache[form]
    for target in fixtures['transfer']:
        missing = sorted(set(''.join(target['groups']))-set(keys[0]))
        group_rows = []
        for raw in target['groups']:
            absent = sorted(set(raw)-set(keys[0]))
            if absent:
                group_rows.append({'raw':raw,'status':'unknown_digits','missing':absent})
                continue
            predictions = Counter(emit(raw,k) for k in keys)
            lexical = {w:n for w,n in predictions.items() if w in lexicon}
            segmented = {w:n for w,n in predictions.items() if paths(w)>0}
            group_rows.append({'raw':raw,'status':'computed','distinct_literal_outputs':len(predictions),
                               'lexical_keys':sum(lexical.values()),'lexical_forms':dict(sorted(lexical.items())),
                               'segmentable_keys':sum(segmented.values()),
                               'unanimous_literal':next(iter(predictions)) if len(predictions)==1 else None})
        exact = relaxed = None
        if not missing:
            exact = sum(all(emit(g,k) in lexicon for g in target['groups']) for k in keys)
            relaxed = sum(all(paths(emit(g,k))>0 for g in target['groups']) for k in keys)
        records.append({'id':target['id'],'source_group':target['source_group'],'text':target['text'],
                        'unknown_digits':missing,'whole_message_word_lexical_keys':exact,
                        'whole_message_segmentable_keys':relaxed,'groups':group_rows})
    duplicate_groups = {}
    for target in fixtures['transfer']:
        duplicate_groups.setdefault(tuple(target['groups']),[]).append(target['id'])
    return {'complete_keys_checked':len(keys),'distinct_training_strings':len(set(training)),
            'training_group_marginals':group_records,
            'keys_with_all_training_words_attested_in_reference':sum(all(frequencies[w]>0 for w in row) for row in training),
            'training_frames_first_six':sorted(set(row[:-1] for row in training)),
            'transfer':records,'duplicate_transfer_inputs':[v for v in duplicate_groups.values() if len(v)>1],
            'scope':'No English ground truth on transfer. Segmentation uses dictionary words, not grammar. Unknown digits are unavailable; one-group numbers/names are not automatically ordinary words.'}


def control_summary(rows, real):
    out = {}
    for family in load('data/round38_protocol.json')['controls']['families']:
        cases = [r for r in rows if r['family']==family]
        complete = [r['result']['count'] for r in cases if r['result']['complete']]
        out[family] = {'cases':len(cases),'complete':len(complete),'limited':len(cases)-len(complete),
                       'positive_complete':sum(n>0 for n in complete),
                       'at_least_real_count_complete':sum(n>=real for n in complete),
                       'maximum_complete_count':max(complete,default=None),
                       'distinct_numeric_inputs':len({tuple(r['groups']) for r in cases})}
    return out


def execute(directory):
    verify('data/round38_input_manifest.json')
    verify('data/round38_execution_manifest.json')
    directory.mkdir(parents=True,exist_ok=False)
    fixtures = load('data/round38_fixtures.json')
    qualification = load('data/round38_qualification_fixtures.json')
    with tempfile.TemporaryDirectory(prefix='469-r38-') as name:
        temp = Path(name);binary = temp/'enumerate';lexpath = temp/'lexicon.txt'
        subprocess.run(['g++','-O2','-std=c++17','-Wall','-Wextra',str(ROOT/'scripts/round38_enumerate.cpp'),'-o',str(binary)],check=True)
        qresults = []
        for case in qualification:
            lexpath.write_text('\n'.join(case['lexicon'])+'\n')
            expected = brute(case)
            result,_ = invoke(binary,lexpath,case,temp,True)
            assert result['complete'] and result['count']==len(expected), (case['id'],result,len(expected))
            actual = {canonical(decode_key(k)) for k in result['keys']}
            assert actual==expected
            if case['true_key']:assert canonical(case['true_key']) in actual
            qresults.append({'id':case['id'],'count':len(expected),'complete_keys_match_independent_brute':True})
        save(directory/'qualification.json',qresults)
        print('70 independent arithmetic cases passed',flush=True)
        lexicon = set(banks()[0]['grapheme1_3'].reverse)
        lexpath.write_text('\n'.join(sorted(lexicon))+'\n')
        real,elapsed = invoke(binary,lexpath,fixtures['real'],temp,True)
        assert real['complete'] and real['count']==3976,real
        save(directory/'real_keys.json.gz',real)
        print('Real exact count:',real['count'],'seconds:',elapsed,flush=True)
        report = inspect_keys(real['keys'],fixtures,lexicon)
        save(directory/'inspection.json',report)
        rows = [];total = 0.0
        for i,case in enumerate(fixtures['controls']):
            if total>=load('data/round38_protocol.json')['budgets']['total_fit_wall_seconds']:
                result,seconds = {'complete':False,'count':None,'reason':'total_budget_not_executed'},0.0
            else:
                result,seconds = invoke(binary,lexpath,case,temp,False)
            total+=seconds
            rows.append(dict(case,result=result,wall_seconds=seconds))
            if (i+1)%25==0:print('Controls',i+1,'/',len(fixtures['controls']),'seconds:',round(total,2),flush=True)
        save(directory/'controls.json',rows)
        summary = {'round':38,'qualification_cases':len(qresults),'real_keys':real['count'],
                   'distinct_training_strings':report['distinct_training_strings'],
                   'all_words_reference_attested_keys':report['keys_with_all_training_words_attested_in_reference'],
                   'controls':control_summary(rows,real['count']),
                   'control_fit_wall_seconds':total,'new_candidate_translation':None,'mission_outcome':'I_inconclusive'}
        save(directory/'summary.json',summary)
        print(json.dumps(summary,indent=2),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.prepare:
        save(ROOT/'data/round38_qualification_fixtures.json',prepare_qualification())
    else:
        assert args.output is not None
        execute(args.output)
