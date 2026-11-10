#!/usr/bin/env python3
"""Explore homophone-selection residue, conditional on the imported row0 model.

No symbol meanings or translations are inferred. Nulls conserve per-book,
per-symbol code counts. Overlapping windows are never treated as independent.
"""
import collections, hashlib, json, math, pathlib, random
ROOT=pathlib.Path(__file__).resolve().parents[1]
SEED=46920261110

def entropy(counts):
    n=sum(counts)
    return -sum(c/n*math.log2(c/n) for c in counts if c) if n else 0.0

def conditional_entropy(books):
    grouped=collections.defaultdict(collections.Counter)
    for b in books:
        for symbol,code in zip(b['symbols'],b['codes']):grouped[symbol][code]+=1
    total=sum(sum(c.values()) for c in grouped.values())
    return {'code_given_symbol_bits':sum(sum(c.values())/total*entropy(c.values()) for c in grouped.values()),
            'by_symbol':{s:{'positions':sum(c.values()),'observed_codes':len(c),'entropy_bits':entropy(c.values())} for s,c in sorted(grouped.items())}}

def shuffle_within_symbol(books,rng):
    out=[]
    for b in books:
        codes=list(b['codes']);groups=collections.defaultdict(list)
        for i,s in enumerate(b['symbols']):groups[s].append(i)
        for indices in groups.values():
            values=[codes[i] for i in indices];rng.shuffle(values)
            for i,v in zip(indices,values):codes[i]=v
        out.append({'id':b['id'],'symbols':b['symbols'],'codes':codes})
    return out

def window_summary(books,k=8,examples=0):
    windows=collections.defaultdict(list)
    for b in books:
        for i in range(len(b['codes'])-k+1):
            windows[b['symbols'][i:i+k]].append((b['id'],i,tuple(b['codes'][i:i+k])))
    # Equal weight for every distinct symbolic context, instead of every reused occurrence.
    repeated={s:locs for s,locs in windows.items() if len({x[0] for x in locs})>=2}
    agreements=[];diversities=[];entropies=[];varying=[]
    for s,locs in repeated.items():
        counts=collections.Counter(c for _,_,c in locs)
        by_book=collections.defaultdict(collections.Counter)
        for book,_,c in locs:by_book[book][c]+=1
        total=len(locs);pairs=total*(total-1)//2-sum(sum(v.values())*(sum(v.values())-1)//2 for v in by_book.values())
        matches=sum(n*(n-1)//2 for n in counts.values())-sum(sum(n*(n-1)//2 for n in cs.values()) for cs in by_book.values())
        agreements.append(matches/pairs)
        diversities.append(len(counts));entropies.append(entropy(counts.values()))
        if len(counts)>1:
            varying.append({'symbol_window':s,'code_variants':len(counts),'occurrences':len(locs),
              'variant_representatives':[{'book':book,'position':i,'codes':list(c)} for c,(book,i) in {c:(book,i) for book,i,c in locs}.items()][:8]})
    return {'length_symbols':k,'unique_symbol_windows':len(windows),'unique_cross_book_repeated_windows':len(repeated),
            'windows_with_multiple_code_variants':sum(n>1 for n in diversities),
            'max_code_variants':max(diversities,default=0),
            'mean_cross_book_exact_code_agreement_equal_window_weight':sum(agreements)/len(agreements) if agreements else None,
            'mean_within_window_variant_entropy_bits_equal_window_weight':sum(entropies)/len(entropies) if entropies else None,
            'examples':varying[:examples]}

def transition_stats(books):
    vocab=collections.defaultdict(set)
    for b in books:
        for s,c in zip(b['symbols'],b['codes']):vocab[s].add(c)
    successor={s:{c:cs[(i+1)%len(cs)] for i,c in enumerate(cs)} for s,v in vocab.items() for cs in [sorted(v)] if len(cs)>1}
    counts=collections.defaultdict(collections.Counter);cyclic=total=0
    for b in books:
        previous={}
        for s,c in zip(b['symbols'],b['codes']):
            if s in previous and s in successor:
                old=previous[s];counts[(s,old)][c]+=1
                cyclic+=c==successor[s][old];total+=1
            previous[s]=c
    modal=sum(max(c.values()) for c in counts.values())
    return {'transitions':total,'numeric_sorted_cycle_hits':cyclic,'numeric_sorted_cycle_rate':cyclic/total if total else None,
      'fitted_modal_successor_rate':modal/total if total else None,
      'conditional_next_code_entropy_bits':sum(sum(c.values())/total*entropy(c.values()) for c in counts.values()) if total else None}

def null_summary(observed,values):
    return {'observed':observed,'null_mean':sum(values)/len(values),'null_min':min(values),'null_max':max(values),
            'upper_tail_p':(1+sum(x>=observed for x in values))/(1+len(values)),
            'lower_tail_p':(1+sum(x<=observed for x in values))/(1+len(values))}

def positive_controls():
    rng=random.Random(SEED);alphabet=['11','22','33','44'];n=600
    rotated=[{'id':'artificial','symbols':'A'*n,'codes':[alphabet[i%4] for i in range(n)]}]
    iid=[{'id':'artificial','symbols':'A'*n,'codes':[rng.choice(alphabet) for _ in range(n)]}]
    return {'sorted_rotation':transition_stats(rotated),'iid_homophones':transition_stats(iid)}

def main():
    path=ROOT/'data/normalized_books.json';books=json.loads(path.read_text());rng=random.Random(SEED)
    observed_trans=transition_stats(books);observed_window=window_summary(books,8,examples=3)
    metrics=['numeric_sorted_cycle_rate','fitted_modal_successor_rate','conditional_next_code_entropy_bits']
    nulls={k:[] for k in metrics};null_agreement=[];null_varying=[]
    for _ in range(199):
        null=shuffle_within_symbol(books,rng);ts=transition_stats(null);ws=window_summary(null,8)
        for k in metrics:nulls[k].append(ts[k])
        null_agreement.append(ws['mean_cross_book_exact_code_agreement_equal_window_weight'])
        null_varying.append(ws['windows_with_multiple_code_variants'])
    omissions=collections.Counter();eligible=collections.Counter();ambiguous=[]
    for b in books:
        for c in b['codes']:
            if c.startswith('0'):eligible[c]+=1
        for i in b['omitted_zero_code_indices']:omissions[b['codes'][i]]+=1
        if b['alignment_count_capped_2']>1:ambiguous.append(b['id'])
    out={'seed':SEED,'replicates':199,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'conditional_code_entropy':conditional_entropy(books),'window_summaries':[window_summary(books,k,3 if k==8 else 0) for k in [4,8,12,16,24]],
      'homophone_transitions':observed_trans,
      'null':'Independently shuffle code assignments inside each (book,symbol) stratum; exact per-stratum counts preserved; semantic window sequence fixed.',
      'comparisons':{**{k:null_summary(observed_trans[k],nulls[k]) for k in metrics},
        'window8_exact_code_agreement':null_summary(observed_window['mean_cross_book_exact_code_agreement_equal_window_weight'],null_agreement),
        'window8_multiple_variant_count':null_summary(observed_window['windows_with_multiple_code_variants'],null_varying)},
      'omissions':{'count':sum(omissions.values()),'by_code':dict(omissions),'eligible_leading_zero_codes':dict(eligible),'ambiguous_book_ids':ambiguous},
      'positive_controls':positive_controls(),
      'divergence_classification':divergent_maximal_matches(books),
      'orientation_ascii_screen':orientation_screen(books,rng),
      'limits':['All results conditional on imported row0 tokenization/map. No source authoring or plaintext attestation.',
        'Overlapping windows and books are dependent. Averaging distinct contexts reduces occurrence pseudoreplication but does not make windows independent.',
        'Entropy is descriptive uncertainty in observed code assignment, not channel capacity or message information.',
        'Numeric sorted-cycle convention predeclared; a negative result would not exclude other permutations or phase models.',
        'Fitted modal successors reselected for each null; only per-symbol global occurrence transitions measured, not a complete source model.',
        'Null destroys contextual code reuse while retaining per-book homophone marginal frequencies. Significant values show contextual dependence, not hidden language.',
        'Five statistics and both tails are exploratory with no multiplicity correction; minimum p=0.005.',
        'Zero positions are conditional alignment choices and ambiguous in9 books. They do not independently establish authorship or a message.'],
      'verdict':'STRUCTURAL_CONTEXT_DEPENDENCE_ONLY_NO_TRANSLATION'}
    (ROOT/'results/residual_channel.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'comparisons':out['comparisons'],'windows':[{k:v for k,v in r.items() if k!='examples'} for r in out['window_summaries']],'entropy':out['conditional_code_entropy']['code_given_symbol_bits']},indent=2))
def mismatch_kind(a,b):
    if a==b:return 'same'
    if {a,b}=={'19','91'}:return 'reversal_19_91'
    if a[::-1]==b:return 'other_digit_reversal'
    return 'other_homophone_pair'

def divergent_maximal_matches(books,k=8):
    index=collections.defaultdict(list)
    for bi,b in enumerate(books):
        for i in range(len(b['codes'])-k+1):index[b['symbols'][i:i+k]].append((bi,i))
    unique={};pair_kinds=collections.Counter();kinds=collections.Counter()
    for locs in index.values():
        for x,(bi,i) in enumerate(locs):
            for bj,j in locs[x+1:]:
                if bi==bj:continue
                a,b=books[bi],books[bj]
                if i and j and a['symbols'][i-1]==b['symbols'][j-1]:continue
                n=k
                while i+n<len(a['codes']) and j+n<len(b['codes']) and a['symbols'][i+n]==b['symbols'][j+n]:n+=1
                ca=tuple(a['codes'][i:i+n]);cb=tuple(b['codes'][j:j+n])
                if ca==cb:continue
                variants=sorted([ca,cb]);key=(a['symbols'][i:i+n],*variants)
                if key in unique:continue
                mismatches=[]
                for offset,(c,d) in enumerate(zip(ca,cb)):
                    if c!=d:
                        kind=mismatch_kind(c,d);kinds[kind]+=1
                        pair_kinds[(kind,*sorted((c,d)))]+=1
                        mismatches.append({'offset':offset,'symbol':a['symbols'][i+offset],'codes':[c,d],'kind':kind})
                unique[key]={'length':n,'symbols':a['symbols'][i:i+n],
                  'locations':[{'book':a['id'],'start':i,'codes':list(ca)},{'book':b['id'],'start':j,'codes':list(cb)}],
                  'mismatches':mismatches}
    records=sorted(unique.values(),key=lambda r:(-r['length'],r['symbols']))
    return {'minimum_match_symbols':k,'deduplicated_divergent_maximal_runs':len(records),
      'mismatch_counts_over_unique_maximal_runs':dict(kinds),
      'distinct_code_pair_types':len(pair_kinds),
      'code_pairs':[{'kind':key[0],'codes':list(key[1:]),'maximal_run_hits':count} for key,count in pair_kinds.most_common()],
      'examples_longest':records[:8],
      'warning':'Maximal for each occurrence pair; deduplicated by(symbols,unordered code variants). Nested and overlapping runs across different pairs remain dependent.'}

def orientation_bits(codes):
    return [int(c[0]>c[1]) for c in codes if c[0]!=c[1]]

def orientation_candidates(books):
    allowed=set(b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz \n\r\t.,!?;:\'"-')
    results=[]
    for offset in range(8):
        for invert in [False,True]:
            outputs=[]
            for b in books:
                bits=orientation_bits(b['codes'])[offset:];bs=[]
                for start in range(0,len(bits)-7,8):
                    value=0
                    for bit in bits[start:start+8]:value=(value<<1)|(bit^invert)
                    bs.append(value)
                outputs.append(bytes(bs))
            joined=b''.join(outputs);n=len(joined)
            results.append({'offset':offset,'invert':invert,'bytes':n,
              'english_ascii_fraction':sum(c in allowed for c in joined)/n if n else 0,
              'printable_ascii_fraction':sum(32<=c<=126 for c in joined)/n if n else 0,
              'preview_hex':joined[:80].hex(),'preview_latin1':joined[:80].decode('latin1')})
    return results

def orientation_screen(books,rng):
    candidates=orientation_candidates(books);best=max(candidates,key=lambda x:x['english_ascii_fraction'])
    nulls=[]
    for _ in range(99):
        altered=shuffle_within_symbol(books,rng)
        nulls.append(max(x['english_ascii_fraction'] for x in orientation_candidates(altered)))
    return {'convention':'For unequal digits only, first<second bit0 elsebit1; equal-digit codes dropped. Big-endian bytes; reset per book; offsets0..7; also bit inversion. 16 predeclared candidates.',
      'best':best,'control':'Same within(book,symbol) code shuffle; full16-candidate selection repeated in99 controls.',
      'comparison':null_summary(best['english_ascii_fraction'],nulls),
      'limits':'Exploratory whole-corpus ASCII screen, no train/holdout claim; allowed-character rate is not English prose and not translation. Palindrome-dropping is one arbitrary convention; variants elsewhere not covered.'}

if __name__=='__main__':main()
