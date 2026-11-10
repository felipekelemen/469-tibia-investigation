#!/usr/bin/env python3
"""Frozen-dictionary copy grammar, Markov and uniform predictive coding.

Compression is a structural measurement. This script deliberately evaluates
language-with-copy positives so that copy dominance cannot be sold as proof
of a message-free origin. No supplied symbol labels are assigned semantics.
"""
import collections, hashlib, heapq, json, math, pathlib, random, re, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
SEED=304692026
LENGTHS=(4,8,12,16,24,32)
MAX_DICTIONARY=128

def gamma_bits(n):
    if n<1:raise ValueError('gamma requires positive integer')
    return 2*n.bit_length()-1

def fit_dictionary(sequences,alphabet,max_entries=MAX_DICTIONARY):
    """Greedy discovery-only motif coverage; serialize dictionary explicitly.

    Lazy heap recomputation discounts positions already covered by selected
    motifs, so128 shifts of one long phrase cannot crowd out all other modules.
    Actual achieved code length is still measured by exactDP afterwards.
    """
    occurrences=collections.defaultdict(list);offset=0
    width=math.ceil(math.log2(len(alphabet)));refwidth=math.ceil(math.log2(max_entries))
    for s in sequences:
        for n in LENGTHS:
            for i in range(len(s)-n+1):occurrences[s[i:i+n]].append(offset+i)
        offset+=len(s)+1
    covered=0;heap=[]
    def evaluate(motif,positions):
        n=len(motif);mask=(1<<n)-1;used=covered;accepted=[]
        for pos in positions:
            bits=mask<<pos
            if not bits&used:accepted.append(pos);used|=bits
        storage=gamma_bits(n)+n*width
        gain=len(accepted)*(n*(1+width)-(1+refwidth))-storage
        return gain,accepted
    for motif,positions in occurrences.items():
        if len(positions)<2:continue
        gain,_=evaluate(motif,positions)
        if gain>0:heapq.heappush(heap,(-gain,-len(motif),motif))
    dictionary=[]
    while heap and len(dictionary)<max_entries:
        old_gain,_,motif=heapq.heappop(heap)
        gain,positions=evaluate(motif,occurrences[motif])
        if gain<=0:continue
        if heap and -gain>heap[0][0]:
            heapq.heappush(heap,(-gain,-len(motif),motif));continue
        dictionary.append(motif);mask=(1<<len(motif))-1
        for pos in positions:covered|=mask<<pos
    return dictionary


def dictionary_bits(dictionary,alphabet):
    width=math.ceil(math.log2(len(alphabet)))
    return gamma_bits(len(dictionary)+1)+sum(gamma_bits(len(m))+len(m)*width for m in dictionary)

def parse_copy(s,dictionary,alphabet):
    """Minimum-cost prefix-coded token stream; no dictionary entry is learned here."""
    width=math.ceil(math.log2(len(alphabet)))
    refwidth=math.ceil(math.log2(len(dictionary))) if len(dictionary)>1 else 0
    index=collections.defaultdict(list)
    for j,m in enumerate(dictionary):index[m[0]].append((j,m))
    cost=[float('inf')]*(len(s)+1);cost[len(s)]=0;choice=[None]*len(s)
    for i in range(len(s)-1,-1,-1):
        cost[i]=1+width+cost[i+1];choice[i]=('literal',s[i])
        for j,m in index.get(s[i],[]):
            if s.startswith(m,i) and 1+refwidth+cost[i+len(m)]<cost[i]:
                cost[i]=1+refwidth+cost[i+len(m)];choice[i]=('reference',j)
    tokens=[];i=0
    while i<len(s):
        kind,v=choice[i];tokens.append((kind,v));i+=1 if kind=='literal' else len(dictionary[v])
    return {'bits':gamma_bits(len(s)+1)+cost[0],'tokens':tokens}

def decode_copy(tokens,dictionary):
    return ''.join(v if k=='literal' else dictionary[v] for k,v in tokens)

def fit_markov(sequences,alphabet):
    starts=collections.Counter();trans=collections.defaultdict(collections.Counter)
    for s in sequences:
        if s:starts[s[0]]+=1
        for a,b in zip(s,s[1:]):trans[a][b]+=1
    # Literal transition/start counts, gamma(count+1), including zero entries.
    paid=gamma_bits(len(sequences)+1)+sum(gamma_bits(starts[a]+1) for a in alphabet)
    paid+=sum(gamma_bits(trans[a][b]+1) for a in alphabet for b in alphabet)
    return {'starts':starts,'transitions':trans,'model_bits':paid,'alphabet':list(alphabet)}

def markov_bits(s,model):
    alphabet=model['alphabet'];k=len(alphabet);alpha=.5
    if not s:return gamma_bits(1)
    starts=model['starts'];trans=model['transitions']
    bits=gamma_bits(len(s)+1)+2-math.log2((starts[s[0]]+alpha)/(sum(starts.values())+alpha*k))
    for a,b in zip(s,s[1:]):
        row=trans.get(a,{})
        bits-=math.log2((row.get(b,0)+alpha)/(sum(row.values())+alpha*k))
    return bits

def compare(train,hold,alphabet):
    alphabet=sorted(alphabet);width=math.ceil(math.log2(len(alphabet)))
    candidates=fit_dictionary(train,alphabet);markov=fit_markov(train,alphabet)
    grid=(0,1,2,4,8,16,32,64,128)
    # Choose dictionary size only on discovery; pay four-bit size selector.
    ranked=[]
    for size in grid:
        candidate=candidates[:size]
        bits=dictionary_bits(candidate,alphabet)+sum(parse_copy(s,candidate,alphabet)['bits'] for s in train)
        ranked.append((bits,size,candidate))
    selected_cost,selected_size,dictionary=min(ranked,key=lambda r:(r[0],r[1]))
    def evaluate(group):
        copy=uniform=markov_cost=0;references=0;reference_symbols=0;length=0
        for s in group:
            parsed=parse_copy(s,dictionary,alphabet)
            assert decode_copy(parsed['tokens'],dictionary)==s
            copy+=parsed['bits'];uniform+=gamma_bits(len(s)+1)+len(s)*width
            markov_cost+=markov_bits(s,markov);length+=len(s)
            references+=sum(k=='reference' for k,_ in parsed['tokens'])
            reference_symbols+=sum(len(dictionary[v]) for k,v in parsed['tokens'] if k=='reference')
        return {'symbols':length,'copy_data_bits':copy,'uniform_data_bits':uniform,'markov_data_bits':markov_cost,
                'reference_tokens':references,'reference_symbol_fraction':reference_symbols/length if length else 0}
    tr=evaluate(train);ho=evaluate(hold);dict_cost=dictionary_bits(dictionary,alphabet)
    # Two bits identify one of the three predeclared model families.
    totals={'copy':2+4+dict_cost+tr['copy_data_bits']+ho['copy_data_bits'],
            'markov1':2+markov['model_bits']+tr['markov_data_bits']+ho['markov_data_bits'],
            'uniform':2+tr['uniform_data_bits']+ho['uniform_data_bits']}
    return {'alphabet_size':len(alphabet),'dictionary_entries':len(dictionary),'dictionary_bits':dict_cost+4,'dictionary_size_selected':selected_size,'discovery_dictionary_size_trials':[{'max_entries':n,'dictionary_plus_discovery_bits':bits} for bits,n,_ in ranked],
            'dictionary':dictionary,'markov_model_bits':markov['model_bits'],'discovery':tr,'reserved':ho,
            'total_two_part_bits':totals,'copy_minus_markov_bits_per_symbol':(totals['copy']-totals['markov1'])/(tr['symbols']+ho['symbols'])}

def english_reserved():
    text=(ROOT/'data/english_reference/alice.txt').read_text(encoding='utf-8-sig')
    if '*** START OF THE PROJECT GUTENBERG EBOOK' in text:
        text=text.split('*** START OF THE PROJECT GUTENBERG EBOOK',1)[1].split('***',1)[1]
    text=text.split('*** END OF THE PROJECT GUTENBERG EBOOK',1)[0]
    text=re.sub('[^A-Z]','',text.upper())
    return text[int(.8*len(text)):]

def controls(books,train_ids,hold_ids,replicates=12):
    ref=english_reserved();needed=sum(len(b['symbols']) for b in books)
    if len(ref)<needed+100:raise ValueError('insufficient external positive reference')
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ';rows=[]
    def split_and_compare(sequences):
        tr=[s for b,s in zip(books,sequences) if b['id'] in train_ids]
        ho=[s for b,s in zip(books,sequences) if b['id'] in hold_ids]
        return compare(tr,ho,alphabet)
    for seed in range(replicates):
        rng=random.Random(SEED+seed);perm=list(alphabet);rng.shuffle(perm);key=dict(zip(alphabet,perm))
        offset=rng.randrange(len(ref)-needed);source=ref[offset:offset+needed];cursor=0;prose=[]
        for b in books:
            n=len(b['symbols']);piece=source[cursor:cursor+n];cursor+=n
            prose.append(''.join(key[c] for c in piece))
        # Random assembly of ciphertext blocks that each preserve a real prose span.
        # A matched negative shuffles letters ONCE within each block, then copies it.
        modules=[]
        for _ in range(16):
            n=rng.choice([24,32,48,64,96]);i=rng.randrange(len(ref)-n)
            modules.append(''.join(key[c] for c in ref[i:i+n]))
        shuffled_modules=[]
        for m in modules:
            chars=list(m);rng.shuffle(chars);shuffled_modules.append(''.join(chars))
        copied=[];no_message=[]
        for b in books:
            n=len(b['symbols']);pos=0;parts=[];negative_parts=[]
            while pos<n:
                idx=rng.randrange(len(modules));take=min(n-pos,len(modules[idx]))
                parts.append(modules[idx][:take]);negative_parts.append(shuffled_modules[idx][:take]);pos+=take
            copied.append(''.join(parts));no_message.append(''.join(negative_parts))
        row={'seed':SEED+seed,'prose_ciphertext':split_and_compare(prose),'copied_prose_ciphertext':split_and_compare(copied),
             'shuffled_module_assembly':split_and_compare(no_message)}
        rows.append(row)
    summary={}
    for label in ['prose_ciphertext','copied_prose_ciphertext','shuffled_module_assembly']:
        deltas=[r[label]['copy_minus_markov_bits_per_symbol'] for r in rows]
        summary[label]={'replicates':replicates,'mean_copy_minus_markov_bits_per_symbol':sum(deltas)/replicates,
                        'min':min(deltas),'max':max(deltas),'copy_beats_markov_count':sum(d<0 for d in deltas)}
    # Explicit attempted discriminator: copy wins => non-linguistic assembly.
    # Its false positives on copied REAL prose establish whether this rule is usable.
    summary['proposed_copy_dominance_discriminator']={
       'rule':'Predict non-linguistic assembly if total copy code beats Markov1',
       'false_positive_rate_on_copied_prose':summary['copied_prose_ciphertext']['copy_beats_markov_count']/replicates,
       'true_positive_rate_on_shuffled_modules':summary['shuffled_module_assembly']['copy_beats_markov_count']/replicates,
       'warning':'This is a structural, predeclared illustrative rule, not a learned semantic classifier.'}
    # Dictionary text itself is a development artifact, not Tibia plaintext.
    slim=[]
    for r in rows:
        slim.append({k:({a:b for a,b in v.items() if a!='dictionary'} if isinstance(v,dict) else v) for k,v in r.items()})
    return {'reference':'Last20% of Alice; no Tibia-derived plaintext','replicates':rows.__len__(),
            'summary':summary,'trials':slim,'limit':'Different random windows overlap across seeds; fixtures are synthetic replicates, not independent source authors.'}

def fit_variant_models(books):
    marginal=collections.defaultdict(collections.Counter);previous=collections.defaultdict(collections.Counter)
    contexts=collections.defaultdict(collections.Counter)
    for b in books:
        last={}
        for i,(s,c) in enumerate(zip(b['symbols'],b['codes'])):
            marginal[s][c]+=1
            if s in last:previous[(s,last[s])][c]+=1
            contexts[(s,b['symbols'][max(0,i-2):i])][c]+=1
            last[s]=c
    return {'marginal':marginal,'previous':previous,'contexts':contexts}

def evaluate_variants(books,fit,allowed):
    results={name:{'bits':0,'correct':0,'positions':0} for name in ['symbol_marginal','previous_homophone','previous2_symbols']}
    for b in books:
        last={}
        for i,(s,c) in enumerate(zip(b['symbols'],b['codes'])):
            vocabulary=sorted(allowed[s]);counts=fit['marginal'].get(s,{});total=sum(counts.values());k=len(vocabulary)
            base={x:(counts.get(x,0)+.5)/(total+.5*k) for x in vocabulary}
            for name,out in results.items():
                if name=='symbol_marginal':dist=base
                else:
                    cs=fit['previous'].get((s,last.get(s)),{}) if name=='previous_homophone' else fit['contexts'].get((s,b['symbols'][max(0,i-2):i]),{})
                    n=sum(cs.values());weight=n/(n+5)
                    dist={x:weight*((cs.get(x,0)+.5)/(n+.5*k))+(1-weight)*base[x] for x in vocabulary}
                out['bits']-=math.log2(dist[c]);out['correct']+=max(dist,key=lambda x:(dist[x],x))==c;out['positions']+=1
            last[s]=c
    for out in results.values():out['bits_per_code']=out['bits']/out['positions'];out['accuracy']=out['correct']/out['positions']
    return results

def symbol_components(books,k=8):
    parent=list(range(len(books)));owner={}
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for i,b in enumerate(books):
        windows={b['symbols'][j:j+k] for j in range(len(b['symbols'])-k+1)}
        for w in windows:
            if w in owner:parent[find(i)]=find(owner[w])
            else:owner[w]=i
    groups=collections.defaultdict(list)
    for i,b in enumerate(books):groups[find(i)].append(b['id'])
    return sorted(groups.values(),key=lambda g:(-len(g),g))

def run():
    start=time.monotonic();path=ROOT/'data/normalized_books.json';books=json.loads(path.read_text());split=json.loads((ROOT/'data/normalized_splits.json').read_text())
    train_ids=set(split['discovery_book_ids']);hold_ids=set(split['holdout_book_ids'])
    tr=[b for b in books if b['id'] in train_ids];ho=[b for b in books if b['id'] in hold_ids]
    comparisons={}
    for field,alphabet in [('digits','0123456789'),('symbols',sorted(set(''.join(b['symbols'] for b in books))))]:
        comparisons[field]=compare([b[field] for b in tr],[b[field] for b in ho],alphabet)
    allowed=collections.defaultdict(set)
    for b in books:
        for s,c in zip(b['symbols'],b['codes']):allowed[s].add(c)
    comps=symbol_components(books,8);variant_fit=fit_variant_models(tr)
    variant={'fixed_discovery_split':evaluate_variants(ho,variant_fit,allowed),'components_symbol8':comps,
             'note':'Fixed split was already exposed. Imported row0 and allowed code lists use entire public corpus. No fresh semantic holdout.'}
    if len(comps)==1:
        variant['leave_component_out']={'status':'INFEASIBLE','reason':'All books connected by an8-symbol overlap; no nonempty independent family holdout at this criterion.'}
    else:
        folds=[]
        for group in comps:
            ids=set(group);fold_train=[b for b in books if b['id'] not in ids];fold_hold=[b for b in books if b['id'] in ids]
            if not fold_train:continue
            folds.append({'held_ids':group,'result':evaluate_variants(fold_hold,fit_variant_models(fold_train),allowed)})
        variant['leave_component_out']={'status':'COMPUTED_CONDITIONAL','folds':folds,'limit':'Only exact8-symbol edges removed; shorter/transformed dependencies persist.'}
    positive=controls(books,train_ids,hold_ids,replicates=12)
    out={'seed':SEED,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'model_conventions':{
      'copy':'Dictionary fit on discovery only; candidates repeated>=2 at lengths4,8,12,16,24,32; greedy nonoverlap coverage max128; dictionarysize selected in0,1,2,4,8,16,32,64,128 by discovery totalbits only;4bit selector charged; exactDP parsing; flag+fixedwidth tokens; gamma lengths; dictionary charged.',
      'markov1':'Discovery start/transition counts serialized with gamma(count+1), alpha=.5 predictive probabilities; ideal arithmetic length+2bits perbook; counts frozen forholdout.',
      'uniform':'Fixedwidthceil(log2K) literals+gamma booklength; alphabet description common/omitted;2bit family selector.',
      'bit_measurement':'Explicit ideal two-part description estimates, not measured gzip bytes. Fixedwidth copy tokens have exact integer lengths; Markov arithmetic contribution is fractional with stated overhead.'},
      'split':{'train_ids':split['discovery_book_ids'],'reserved_ids':split['holdout_book_ids'],'prior_exposure':True},
      'comparisons':comparisons,'positive_negative_controls':positive,'variant_prediction':variant,
      'runtime_seconds':time.monotonic()-start,'verdict':'STRUCTURAL_COMPARISON_ONLY_NO_TRANSLATION',
      'limitations':['No test here establishes authorial origin, message absence or plaintext. A short generator can describe encrypted language as well as nonsemantic motifs.',
       'No prospective external Tibia plaintext pair; tiny reserved component and shorter/transformed reuse remain.',
       'row0 is imported and inferred on the full public corpus; label alphabet and permissible codes are global conditions, not independently learned truth.',
       'Control positives use one author and overlapping windows; copied prose contains real English fragments, not necessarily coherent whole-book essays.',
       'Dictionary candidate frequency uses overlapping windows as a heuristic; exactDP and paid dictionary prevent counting those overlaps as achieved savings.',
       'Comparisons cover three fixed finite coding models, not all linguistic tokenizations or every generative model.']}
    (ROOT/'results/generative_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'runtime':out['runtime_seconds'],'comparisons':{k:{a:b for a,b in v.items() if a!='dictionary'} for k,v in comparisons.items()},'controls':positive['summary'],'variant':variant},indent=2))
    return out
if __name__=='__main__':run()
