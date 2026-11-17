#!/usr/bin/env python3
"""Pinned CMU forms; syllables are an explicit reproducible operational choice."""
from collections import defaultdict,Counter
from functools import lru_cache
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
FAMILIES=('digraph','grapheme1_3','phone1_3','syllable')


def syllabify(phones,vowels,onsets):
    nuclei=[i for i,p in enumerate(phones) if p in vowels]
    if not nuclei:return None
    cuts=[0]
    for left,right in zip(nuclei,nuclei[1:]):
        cluster=phones[left+1:right]
        lengths=[n for n in range(len(cluster)+1) if tuple(cluster[len(cluster)-n:]) in onsets]
        onset=max(lengths)
        cuts.append(right-onset)
    cuts.append(len(phones))
    return tuple(tuple(phones[a:b]) for a,b in zip(cuts,cuts[1:]))


class Bank:
    def __init__(self,family,forms,labels):
        self.family=family;self.minimum=2 if family=='digraph' else 1
        self.maximum=1 if family=='syllable' else 2 if family=='digraph' else 3
        self.labels=labels
        self.reverse={f:sorted(ws) for f,ws in sorted(forms.items())}
        self.by_length=defaultdict(list)
        for form in self.reverse:self.by_length[len(form)].append(form)
        self.lengths=sorted(self.by_length)
        self.wordforms=defaultdict(list)
        for form,ws in self.reverse.items():
            for w in ws:self.wordforms[w].append(form)

    def render(self,unit):
        if self.family.startswith('grapheme') or self.family=='digraph':return unit
        return [self.labels[c] for c in unit]


@lru_cache(maxsize=1)
def banks():
    phone_types=dict(line.split() for line in (ROOT/'data/cmudict_reference/cmudict.phones').read_text().splitlines() if line.strip())
    vowels={p for p,t in phone_types.items() if t=='vowel'}
    entries=defaultdict(set);stats=Counter()
    for line in (ROOT/'data/cmudict_reference/cmudict.dict').read_text().splitlines():
        stats['raw_lines']+=1
        tokens=line.split('#',1)[0].split()
        if not tokens:continue
        label=re.sub(r'\([0-9]+\)$','',tokens[0])
        if not re.fullmatch(r"[A-Za-z]+(?:['-][A-Za-z]+)*",label):stats['excluded_label']+=1;continue
        word=re.sub('[^A-Z]','',label.upper())
        if len(word)==1 and word not in ('A','I'):stats['excluded_single_letter']+=1;continue
        phones=tuple(re.sub('[012]$','',p) for p in tokens[1:])
        if not phones or any(p not in phone_types for p in phones):raise ValueError('unexpected phone sequence: '+line)
        entries[word].add(phones)
    onsets={()}
    for variants in entries.values():
        for ps in variants:
            first=next((i for i,p in enumerate(ps) if p in vowels),None)
            if first is not None:onsets.add(ps[:first])
    phonechars={p:chr(0x100+i) for i,p in enumerate(sorted(phone_types))}
    allsyllables=set();syll_forms=defaultdict(set)
    for word,variants in entries.items():
        for ps in variants:
            sylls=syllabify(ps,vowels,onsets)
            if sylls is not None:syll_forms[word].add(sylls);allsyllables.update(sylls)
    syllchars={s:chr(0x1000+i) for i,s in enumerate(sorted(allsyllables))}
    # Avoid embedding newline/regex-special ASCII in internal phone/syllable symbols.
    ortho=defaultdict(set);phonetic=defaultdict(set);syllabic=defaultdict(set)
    for word,variants in entries.items():
        ortho[word].add(word)
        for ps in variants:phonetic[''.join(phonechars[p] for p in ps)].add(word)
    for word,variants in syll_forms.items():
        for sylls in variants:syllabic[''.join(syllchars[s] for s in sylls)].add(word)
    added='BONELORD' not in ortho;ortho['BONELORD'].add('BONELORD')
    result={'digraph':Bank('digraph',ortho,{}),'grapheme1_3':Bank('grapheme1_3',ortho,{}),
            'phone1_3':Bank('phone1_3',phonetic,{v:k for k,v in phonechars.items()}),
            'syllable':Bank('syllable',syllabic,{v:list(k) for k,v in syllchars.items()})}
    meta={'parser_counts':dict(stats),'retained_spellings':len(entries),'retained_pronunciations':sum(len(v) for v in entries.values()),
          'phones':len(phonechars),'operational_syllable_types':len(syllchars),'attested_onsets':len(onsets),
          'hypothetical_orthographic_additions':['BONELORD'] if added else [],
          'families':{f:{'forms':len(b.reverse),'spellings':len(b.wordforms),'minimum':b.minimum,'maximum':b.maximum} for f,b in result.items()},
          'scope':'Source pronunciations/stress stripping and deterministic onset heuristic; no Tibia semantics authenticated.'}
    return result,meta
