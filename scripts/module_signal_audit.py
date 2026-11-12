#!/usr/bin/env python3
"""Discovery-only module inventory and FIXED-key score decomposition.

This is a conditional order diagnostic, not another fitted-key null test.
Messages inside whole modules are preserved, so it is not a semantic null.
"""
import collections,hashlib,heapq,json,math,pathlib,random,time
import numpy as np
from copied_homophonic_v3 import build_model
ROOT=pathlib.Path(__file__).resolve().parents[1]
LENGTHS=(8,12,16,24,32)
SEED=60469026

def encode_codes(codes):return ''.join(chr(256+int(c)) for c in codes)
def literal_codes(s):return [ord(c)-256 for c in s]
def gamma(n):return 2*n.bit_length()-1

def fit_inventory(sequences,alphabet_size,max_entries=128):
    """Greedy uncovered gain; never obtains strings spanning book boundaries."""
    occurrences=collections.defaultdict(list);offset=0
    width=math.ceil(math.log2(alphabet_size));refwidth=math.ceil(math.log2(max_entries))
    for s in sequences:
        for n in LENGTHS:
            for i in range(len(s)-n+1):occurrences[s[i:i+n]].append(offset+i)
        offset+=len(s)+1
    covered=0;heap=[]
    def gain(m,positions):
        mask=(1<<len(m))-1;used=covered;accepted=[]
        for pos in positions:
            bits=mask<<pos
            if not used&bits:accepted.append(pos);used|=bits
        return len(accepted)*(len(m)*(1+width)-(1+refwidth))-(gamma(len(m))+len(m)*width),accepted
    for m,pos in occurrences.items():
        if len(pos)<2:continue
        value,_=gain(m,pos)
        if value>0:heapq.heappush(heap,(-value,-len(m),m))
    dictionary=[]
    while heap and len(dictionary)<max_entries:
        old,_,m=heapq.heappop(heap);value,accepted=gain(m,occurrences[m])
        if value<=0:continue
        if heap and -value>heap[0][0]:heapq.heappush(heap,(-value,-len(m),m));continue
        dictionary.append(m);mask=(1<<len(m))-1
        for pos in accepted:covered|=mask<<pos
    return dictionary

def parse(s,dictionary,alphabet_size):
    """Fixed inventory, prefix-code minimum cost, exact lossless token stream."""
    width=math.ceil(math.log2(alphabet_size));refwidth=math.ceil(math.log2(len(dictionary))) if len(dictionary)>1 else 0
    ix=collections.defaultdict(list)
    for j,m in enumerate(dictionary):ix[m[0]].append((j,m))
    costs=[float('inf')]*(len(s)+1);costs[-1]=0;choices=[None]*len(s)
    for i in range(len(s)-1,-1,-1):
        costs[i]=1+width+costs[i+1];choices[i]=('literal',s[i],None)
        for j,m in ix.get(s[i],[]):
            c=1+refwidth+costs[i+len(m)] if s.startswith(m,i) else float('inf')
            if c<costs[i]:costs[i]=c;choices[i]=('reference',m,j)
    tokens=[];i=0
    while i<len(s):
        kind,text,index=choices[i];tokens.append({'kind':kind,'text':text,'dictionary_index':index});i+=len(text)
    assert ''.join(t['text'] for t in tokens)==s
    return tokens,gamma(len(s)+1)+costs[0]

def storage_bits(dictionary,alphabet_size):
    width=math.ceil(math.log2(alphabet_size))
    return gamma(len(dictionary)+1)+sum(gamma(len(m))+len(m)*width for m in dictionary)

def choose_inventory(train,alphabet_size):
    full=fit_inventory(train,alphabet_size,128);trials=[]
    for limit in [64,128]:
        d=full[:limit]
        cost=storage_bits(d,alphabet_size)+sum(parse(s,d,alphabet_size)[1] for s in train)+1
        trials.append({'limit':limit,'entries':len(d),'dictionary_plus_discovery_bits':cost})
    chosen=min(trials,key=lambda r:(r['dictionary_plus_discovery_bits'],r['limit']))
    return full[:chosen['limit']],trials,chosen

def decompose(tokens,mapping,table):
    chars=[];owner=[];reference_ids=set();covered=0
    for i,t in enumerate(tokens):
        chars.extend(mapping[c] for c in literal_codes(t['text']));owner.extend([i]*len(t['text']))
        if t['kind']=='reference':reference_ids.add(i);covered+=len(t['text'])
    categories={k:{'windows':0,'score_sum':0.0} for k in ['internal_module','module_boundary','residual']}
    for i in range(max(0,len(chars)-3)):
        ids=owner[i:i+4]
        if len(set(ids))==1 and ids[0] in reference_ids:kind='internal_module'
        elif any(x in reference_ids for x in ids):kind='module_boundary'
        else:kind='residual'
        a,b,c,d=chars[i:i+4];v=float(table[((a*26+b)*26+c)*26+d]);categories[kind]['windows']+=1;categories[kind]['score_sum']+=v
    return {'characters':len(chars),'reference_characters':covered,'reference_tokens':len(reference_ids),'tokens':len(tokens),'categories':categories}

def aggregate(books_tokens,mapping,table):
    results=[decompose(t,mapping,table) for t in books_tokens]
    out={'characters':sum(r['characters'] for r in results),'reference_characters':sum(r['reference_characters'] for r in results),
      'reference_tokens':sum(r['reference_tokens'] for r in results),'tokens':sum(r['tokens'] for r in results),'categories':{}}
    windows=total=0
    for kind in ['internal_module','module_boundary','residual']:
        n=sum(r['categories'][kind]['windows'] for r in results);s=sum(r['categories'][kind]['score_sum'] for r in results)
        out['categories'][kind]={'windows':n,'score_sum':s,'mean_score':s/n if n else None};windows+=n;total+=s
    out.update(windows=windows,score_sum=total,mean_score=total/windows if windows else None,
       reference_fraction=out['reference_characters']/out['characters'] if out['characters'] else 0,
       internal_window_fraction=out['categories']['internal_module']['windows']/windows if windows else 0)
    return out

def shuffled_tokens(books_tokens,rng):
    out=[]
    for tokens in books_tokens:
        copied=list(tokens);rng.shuffle(copied);out.append(copied)
    return out

def known_english_positive(table):
    # Source is previously opened qualification; property demonstration only.
    from homophonic_benchmark import letters
    source=ROOT/'data/benchmark_reference_v4/tom_sawyer.txt';body=letters(source)
    modules=[body[20000+512*i:20000+512*i+128] for i in range(8)]
    tokens=[{'kind':'reference','text':encode_codes([ord(c)-65 for c in modules[i%8]]),'dictionary_index':i%8} for i in range(24)]
    before=aggregate([tokens],list(range(26)),table);rng=random.Random(SEED+10000)
    after=aggregate(shuffled_tokens([tokens],rng),list(range(26)),table)
    assert before['categories']['internal_module']['windows']==after['categories']['internal_module']['windows']
    assert abs(before['categories']['internal_module']['score_sum']-after['categories']['internal_module']['score_sum'])<1e-8
    return {'role':'KNOWN_ENGLISH_PROPERTY_DEMONSTRATION_not_blind_qualification','source':str(source.relative_to(ROOT)),
      'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'known_english_modules':24,'unique_modules':8,
      'before':before,'after_one_permutation':after,
      'interpretation':'Whole English spans and every internal tetragram are preserved when their order changes. This null does not remove meaning inside modules.'}

def main():
    start=time.monotonic();bookpath=ROOT/'data/normalized_books.json';books=json.loads(bookpath.read_text());split=json.loads((ROOT/'data/normalized_splits.json').read_text())
    mapping=json.loads((ROOT/'results/qualified_tibia_search_v4.json').read_text())['observed']['mapping'];table,model=build_model()
    discovery=[b for b in books if b['id'] in split['discovery_book_ids']];held=[b for b in books if b['id'] in split['holdout_book_ids']]
    train=[encode_codes(b['codes']) for b in discovery];test=[encode_codes(b['codes']) for b in held]
    alphabet_size=len({c for s in train for c in s});dictionary,trials,chosen=choose_inventory(train,alphabet_size)
    group_tokens={'discovery':[parse(s,dictionary,alphabet_size)[0] for s in train],
                  'heldout':[parse(s,dictionary,alphabet_size)[0] for s in test]}
    observed={name:aggregate(t,mapping,table) for name,t in group_tokens.items()}
    original=json.loads((ROOT/'results/qualified_tibia_search_v4.json').read_text())['observed']
    assert abs(observed['discovery']['mean_score']-original['train_score'])<1e-10
    assert abs(observed['heldout']['mean_score']-original['holdout_score'])<1e-10
    nulls={name:[] for name in group_tokens}
    for i in range(99):
        rng=random.Random(SEED+i)
        for name,tokens in group_tokens.items():
            trial=aggregate(shuffled_tokens(tokens,rng),mapping,table)
            assert abs(trial['categories']['internal_module']['score_sum']-observed[name]['categories']['internal_module']['score_sum'])<1e-8
            nulls[name].append({'mean_score':trial['mean_score'],'internal_score_sum':trial['categories']['internal_module']['score_sum'],
              'boundary_score_sum':trial['categories']['module_boundary']['score_sum'],'residual_score_sum':trial['categories']['residual']['score_sum']})
    summaries={}
    for name,values in nulls.items():
        scores=[v['mean_score'] for v in values]
        summaries[name]={'trials':values,'replicates':99,'mean_permuted_score':sum(scores)/99,
          'conditional_fixed_key_upper_tail_p':(1+sum(s>=observed[name]['mean_score'] for s in scores))/100,
          'calibration':'FIXED_V4_KEY: key selection not repeated, discovery key fitted on original order, descriptive diagnostic only'}
    status='BLOCKED_NO_HELD_MODULE_COVERAGE' if observed['heldout']['reference_characters']==0 else 'PARTIAL_COVERAGE_ONLY_NOT_SEMANTIC_VALIDATION'
    out={'protocol':{'lengths_codes':LENGTHS,'max_dictionary':128,'size_grid':[64,128],'size_selection':'dictionary+discovery data prefix-code bits; no held input',
       'encoding':'chr(256+integercode), injective and no semantics','mapping':'frozen V4 observed.mapping','seed':SEED,'permutations':99},
       'books_sha256':hashlib.sha256(bookpath.read_bytes()).hexdigest(),'model_sha256':model['model_sha256'],
       'fitted_result_sha256':hashlib.sha256((ROOT/'results/qualified_tibia_search_v4.json').read_bytes()).hexdigest(),
       'split_sha256':hashlib.sha256((ROOT/'data/normalized_splits.json').read_bytes()).hexdigest(),
       'implementation_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
       'discovery_ids':[b['id'] for b in discovery],'heldout_ids':[b['id'] for b in held],
       'dictionary_selection_trials':trials,'selected':chosen,'dictionary':[literal_codes(m) for m in dictionary],
       'observed':observed,'permutations':summaries,'module_null_feasibility':status,
       'fully_refitted_game_nulls_run':0,'positive_control':known_english_positive(table),'runtime_seconds':time.monotonic()-start,
       'limits':['All data and V4 key were already exposed; no prospective language validation.',
        'Inventory uses discovery only; minimum8codes may leave heldout completely uncovered. If so permutation is literal shuffle there, not module-preserving control.',
        'Chosen64/128 inventory is one finite decomposition; not evidence of true author modules.',
        'Internal sums are invariant by construction. The order diagnostic can only measure cross-token/residual contributions.',
        'Fixed-key p is NOT comparable to earlier fully reoptimized null p; discovery key selection is not recalibrated.',
        'Permuting whole modules may preserve a real message inside modules. No semantic null or universal absence claim.'],
       'verdict':'NO_VERIFIED_TRANSLATION'}
    (ROOT/'results/module_signal_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'selected':chosen,'observed':observed,'feasibility':status,'p':{n:r['conditional_fixed_key_upper_tail_p'] for n,r in summaries.items()},'runtime':out['runtime_seconds']},indent=2))
if __name__=='__main__':main()
