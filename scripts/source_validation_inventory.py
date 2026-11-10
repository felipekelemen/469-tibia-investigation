#!/usr/bin/env python3
"""P01/P05: source inventory, content dependence and semantic identifiability.

No proposed gloss is used to label a book or to construct a translation.
Row0 projections are only inherited, boundary-aligned occurrences in books
whose recorded zero-omission alignment is unique; they are not new decodes.
"""
from collections import Counter, defaultdict
import hashlib, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def occurrences(text,needle):
    start=0
    while needle:
        i=text.find(needle,start)
        if i<0:return
        yield i
        start=i+1

def components(records,field,k):
    parent={r['id']:r['id'] for r in records};index={}
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for r in records:
        text=r[field]
        for gram in {text[i:i+k] for i in range(max(0,len(text)-k+1))}:
            if gram in index:
                a,b=find(r['id']),find(index[gram]);parent[a]=b
            else:index[gram]=r['id']
    groups=defaultdict(list)
    for r in records:groups[find(r['id'])].append(r['id'])
    return sorted(groups.values(),key=lambda g:(-len(g),g))

def coverage(sample,books,k):
    known={b['digits'][i:i+k] for b in books for i in range(max(0,len(b['digits'])-k+1))}
    covered=set()
    for i in range(max(0,len(sample)-k+1)):
        if sample[i:i+k] in known:covered.update(range(i,i+k))
    return len(covered)

def raw_boundaries(book):
    """Map original digit boundaries to inherited token boundaries."""
    omitted=set(book['omitted_zero_code_indices']);positions={0:0};cursor=0
    for i,c in enumerate(book['codes']):
        cursor+=1 if i in omitted else 2;positions[cursor]=i+1
    if cursor!=len(book['digits']):raise ValueError('invalid reconstructed length')
    return positions

def inherited_projections(sample,books,matches):
    out=[];lookup={b['id']:b for b in books}
    for m in matches:
        book=lookup[m['book_id']]
        if book['alignment_count_capped_2']!=1:continue
        bounds=raw_boundaries(book);a=m['raw_start'];z=a+len(sample)
        if a in bounds and z in bounds:
            i,j=bounds[a],bounds[z]
            out.append({'book_id':book['id'],'raw_start':a,'code_start':i,'code_end_exclusive':j,
                        'codes':book['codes'][i:j],'symbols':book['symbols'][i:j]})
    return out

def provenance(entry):
    p=ROOT/entry['local_source'];text=p.read_text()
    needle=entry['source_literal'];lines=text.splitlines()
    hits=[i+1 for i,line in enumerate(lines) if needle in line]
    if not hits:raise ValueError(f"source literal not found: {entry['id']}")
    return {'local_source':entry['local_source'],'source_sha256':digest(p),'matching_lines_1based':hits,
            'original_url':entry['original_url'],'source_check':'literal verified in pinned local source; original page not newly fetched',
            'claimed_event_date':entry['claimed_event_date'],'source_capture_date':None,
            'claimed_game_version':entry.get('claimed_game_version'),'date_caveat':entry['date_caveat']}

def run():
    ip=ROOT/'data/source_validation_inventory.json';entries=json.loads(ip.read_text())
    bp=ROOT/'data/normalized_books.json';books=json.loads(bp.read_text());records=[]
    for e in entries:
        digits=re.sub('[^0-9]','',e['text']);matches=[]
        for b in books:
            matches.extend({'book_id':b['id'],'raw_start':i} for i in occurrences(b['digits'],digits))
        projs=inherited_projections(digits,books,matches)
        texts=sorted({p['symbols'] for p in projs})
        records.append({'id':e['id'],'source_group':e['source_group'],'modality':e['modality'],
          'text':e['text'],'digits':digits,'digit_count':len(digits),'utf8_bytes':len(e['text'].encode()),
          'sample_sha256':hashlib.sha256(e['text'].encode()).hexdigest(),'provenance':provenance(e),
          'previously_exposed':True,'gloss_status':e['gloss_status'],'asserted_meaning':e.get('asserted_meaning'),
          'full_phrase_plaintext_attested':False,'canonical_candidate':e.get('canonical_candidate',True),
          'raw_exact_matches':matches,'raw_exact_match_count':len(matches),
          'raw_coverage_positions':{str(k):coverage(digits,books,k) for k in [8,12,16,24]},
          'inherited_unique_alignment_projections':projs,'inherited_symbol_variants':texts,
          'projection_caveat':'Inherited map only, unique recorded omission alignment and whole token boundaries; no new tokenization or semantics inferred.',
          'content_status':'REUSED_BOOK_CONTENT' if matches else 'NO_WHOLE_RAW_MATCH_NOT_PROOF_OF_INDEPENDENCE'})
    bygroup=defaultdict(list)
    for r in records:
        if r['canonical_candidate']:bygroup[r['source_group']].append(r)
    source_holdouts=[]
    for group,held in bygroup.items():
        others=[r for g,rs in bygroup.items() if g!=group for r in rs]
        all_train_tokens={t for r in others for t in re.findall(r'\d+',r['text'])}
        held_tokens=[t for r in held for t in re.findall(r'\d+',r['text'])]
        raw_reused=[r['id'] for r in held if r['raw_exact_match_count']]
        source_holdouts.append({'held_source_group':group,'sample_ids':[r['id'] for r in held],
            'numeric_groups':len(held_tokens),'distinct_numeric_groups':len(set(held_tokens)),
            'groups_seen_in_other_sources':len([t for t in held_tokens if t in all_train_tokens]),
            'whole_samples_reused_in_books':raw_reused,'attested_full_phrase_plaintexts':0,
            'semantic_validation_status':'NOT_IDENTIFIABLE_WITH_AVAILABLE_ATTESTATION',
            'reason':'No official/canonical full numeric-phrase plaintext pair is available. Structural repetition and community word assignments cannot serve as independent labels.'})
    graphs={}
    for field,thresholds in [('digits',[8,12,16,24]),('symbols',[8,12,16,24])]:
        graphs[field]={}
        for k in thresholds:
            cs=components(books,field,k)
            graphs[field][str(k)]={'unit':'raw digits' if field=='digits' else 'imported row0 symbols',
                'components':cs,'component_sizes':[len(c) for c in cs],
                'three_nonempty_component_partitions_feasible':len(cs)>=3,
                'feasibility':'FEASIBLE_FOR_THIS_EXACT_OVERLAP_THRESHOLD_ONLY' if len(cs)>=3 else 'INFEASIBLE',
                'component_code_counts':[sum(len(b['codes']) for b in books if b['id'] in c) for c in cs],
                'semantic_independence_proven':False,
                'limitation':'No shared exact kgram across components. Shorter/transformed dependencies and globally imported tokenization remain.'}
    out={'input_sha256':digest(ip),'books_sha256':digest(bp),'samples':records,
      'sample_count':len(records),'canonical_candidates':sum(r['canonical_candidate'] for r in records),
      'attested_full_phrase_plaintext_pairs':0,'novel_prospective_blind_samples':0,
      'book_overlap_graphs':graphs,'leave_source_out':source_holdouts,
      'p05_wordcode_identifiability':{'status':'BLOCKED_SEMANTIC_IDENTIFICATION',
          'observed_spaced_groups':sum(len(re.findall(r'\d+',r['text'])) for r in records if r['canonical_candidate']),
          'accepted_official_word_glosses':0,
          'named_entity_and_taboo_anchors':[r['id'] for r in records if r['gloss_status']=='in_game_name_or_taboo_transcription'],
          'community_hypotheses_not_training_truth':{'knightmare':'be a wit than be a fool',
             'evil_eye':'look at you','elder_bonelord':'let me see you'},
          'invariance':'Renaming every latent word/concept consistently leaves all numeric group repetition constraints unchanged; without external labels the meanings are underidentified.',
          'not_attempted':'No English dictionary completion or community codebook score was promoted to a translation.'},
      'limits':['Local archival transcriptions are verified byte-for-byte against pinned source files, not newly authenticated ingame captures.',
        'Event/capture/version metadata remain null where unknown; guessed dates are not manufactured.',
        'Repeated source groups may share historical provenance; leave-source-out is descriptive, not a proof of independence.',
        'Direct raw match absence does not establish a separate cipher, novel semantic content or prospective blind validation.',
        'Short anchors 1/0 produce many trivial raw matches; these are not lexical or informational evidence. Coverage k exceeds their length and is therefore uninformative.',
        'The full corpus and imported map have been exposed upstream. Threshold feasibility is reported for every predeclared threshold without selecting by language scores.']}
    (ROOT/'results/source_validation_inventory.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'samples':len(records),'raw_reused':{r['id']:r['raw_exact_match_count'] for r in records},
        'symbol_graph_components':{k:v['component_sizes'] for k,v in graphs['symbols'].items()},
        'p05':out['p05_wordcode_identifiability']['status']},indent=2))
    return out
if __name__=='__main__':run()
