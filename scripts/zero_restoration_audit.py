#!/usr/bin/env python3
"""Audit imported zero-restoration annotations and raw mechanical ambiguity.

No language score, mapping meaning, translation or true parse is inferred.
Counts refer to segmentation/omission paths, not necessarily distinct codewords.
"""
import collections,hashlib,itertools,json,pathlib,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
ZERO_CODES=tuple(f'0{i}' for i in range(10))

def admissible_edges(raw,i,inventory):
    if i+2<=len(raw) and raw[i:i+2] in inventory:
        yield i+2,raw[i:i+2],False
    code='0'+raw[i]
    if code in inventory:yield i+1,code,True

def parse_summary(raw,inventory):
    """Exact path count and shortest/longest token witnesses using arbitrary ints."""
    n=len(raw);counts=[0]*(n+1);counts[n]=1
    shortest=[None]*(n+1);longest=[None]*(n+1);shortest[n]=longest[n]=0
    short_choice=[None]*(n+1);long_choice=[None]*(n+1)
    for i in range(n-1,-1,-1):
        for end,code,omitted in admissible_edges(raw,i,inventory):
            counts[i]+=counts[end]
            if shortest[end] is not None and (shortest[i] is None or 1+shortest[end]<shortest[i]):
                shortest[i]=1+shortest[end];short_choice[i]=(end,code,omitted)
            if longest[end] is not None and (longest[i] is None or 1+longest[end]>longest[i]):
                longest[i]=1+longest[end];long_choice[i]=(end,code,omitted)
    def witness(choices):
        if not counts[0]:return None
        codes=[];omissions=[];i=0
        while i<n:
            end,code,omitted=choices[i]
            if omitted:omissions.append(len(codes))
            codes.append(code);i=end
        serialized=''.join(c[1:] if j in set(omissions) else c for j,c in enumerate(codes))
        assert serialized==raw
        return {'codes':codes,'omitted_zero_code_indices':omissions}
    return {'segmentation_path_count':str(counts[0]),'count_bit_length':counts[0].bit_length(),
      'min_tokens':shortest[0],'max_tokens':longest[0],
      'minimum_token_witness':witness(short_choice),'maximum_token_witness':witness(long_choice)}

def code_counts(books):
    counts={c:{'occurrences':0,'omitted':0,'preserved':0,'book_ids_omitted':[],'book_ids_preserved':[]} for c in ZERO_CODES}
    for b in books:
        omit=set(b['omitted_zero_code_indices'])
        for i,c in enumerate(b['codes']):
            if not c.startswith('0'):continue
            r=counts[c];r['occurrences']+=1;r['omitted' if i in omit else 'preserved']+=1
            key='book_ids_omitted' if i in omit else 'book_ids_preserved'
            if b['id'] not in r[key]:r[key].append(b['id'])
    for r in counts.values():r['action_status']='mixed' if r['omitted'] and r['preserved'] else 'always_omitted' if r['omitted'] else 'always_preserved' if r['preserved'] else 'unobserved'
    return counts

def serialize(codes,policy):
    return ''.join(c[1:] if c.startswith('0') and policy[c] else c for c in codes)

def rule_sweep(train,hold):
    rows=[];exact_train=[];exact_all=[]
    for values in itertools.product([False,True],repeat=10):
        policy=dict(zip(ZERO_CODES,values))
        outputs=[serialize(b['codes'],policy) for b in train]
        correct=sum(s==b['digits'] for s,b in zip(outputs,train))
        length_error=sum(abs(len(s)-len(b['digits'])) for s,b in zip(outputs,train))
        row={'mask':sum((1<<i) for i,v in enumerate(values) if v),'train_exact_books':correct,'train_absolute_length_error':length_error}
        rows.append(row)
        if correct==len(train):
            hold_correct=sum(serialize(b['codes'],policy)==b['digits'] for b in hold)
            exact_train.append(dict(row,hold_exact_books=hold_correct))
            if hold_correct==len(hold):exact_all.append(row['mask'])
    best=min(rows,key=lambda r:(-r['train_exact_books'],r['train_absolute_length_error'],r['mask']))
    policy={c:bool(best['mask']&(1<<i)) for i,c in enumerate(ZERO_CODES)}
    best=dict(best,policy_omit=policy,hold_exact_books=sum(serialize(b['codes'],policy)==b['digits'] for b in hold),
      hold_predictions=[{'id':b['id'],'matches':serialize(b['codes'],policy)==b['digits'],'predicted_digits':serialize(b['codes'],policy)} for b in hold])
    return {'policies_enumerated':len(rows),'train_books':len(train),'hold_books':len(hold),'exact_train_policies':exact_train,
      'exact_all_policy_masks':exact_all,'best_train_selected_policy':best,
      'selection':'maximize exact train books, then minimize total absolute train length error, then numeric policy mask; no held scores used',
      'scope':'Only imported code streams under deterministic leading-zero action per code; not all variable-length serializations.'}

def self_checks():
    inventory={f'{i:02d}' for i in range(100)}-{'39'}
    r=parse_summary('12345678',inventory);assert r['segmentation_path_count']=='34' and r['min_tokens']==4 and r['max_tokens']==8
    empty=parse_summary('',inventory);assert empty['segmentation_path_count']=='1' and empty['min_tokens']==0
    r2=parse_summary('001',{'00','01'});assert r2['segmentation_path_count']=='3' and r2['min_tokens']==2 and r2['max_tokens']==3
    return [{'test':'eight-digit all valid 1/2-length segmentation, Fibonacci9','raw':'12345678','paths':34,'min_tokens':4,'max_tokens':8},
      {'test':'empty stream has one empty parse','paths':1},
      {'test':'zero-run path count includes same code stream with different boundaries','raw':'001','inventory':['00','01'],'paths':3,
       'explanation':'[00,01] writes 0|01 or00|1, plus[00,00,01] writes0|0|1. Paths3, distinct code sequences2.'}]

def main():
    start=time.monotonic();bookpath=ROOT/'data/normalized_books.json';books=json.loads(bookpath.read_text());split=json.loads((ROOT/'data/normalized_splits.json').read_text())
    inventory=set(json.loads((ROOT/'data/normalized_code_map.json').read_text()))
    train=[b for b in books if b['id'] in split['discovery_book_ids']];hold=[b for b in books if b['id'] in split['holdout_book_ids']]
    tests=self_checks();rows=[]
    for b in books:
        # Annotation roundtrip verifies consistency of imported sequence, not uniqueness.
        omit=set(b['omitted_zero_code_indices'])
        assert ''.join(c[1:] if i in omit else c for i,c in enumerate(b['codes']))==b['digits']
        r=parse_summary(b['digits'],inventory);r.update(id=b['id'],raw_digits=len(b['digits']),imported_tokens=len(b['codes']),
          imported_alignment_count_capped2=b['alignment_count_capped_2'])
        assert r['min_tokens']<=r['imported_tokens']<=r['max_tokens']
        rows.append(r)
    counts=[int(r['segmentation_path_count']) for r in rows]
    out={'input_sha256':hashlib.sha256(bookpath.read_bytes()).hexdigest(),
      'map_sha256':hashlib.sha256((ROOT/'data/normalized_code_map.json').read_bytes()).hexdigest(),
      'implementation_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
      'rule':'At each position either consume two digits if its code is in imported99inventory, or consume one digit d as code0d with omitted leading0.',
      'zero_counts':code_counts(books),'zero_counts_train':code_counts(train),'zero_counts_hold':code_counts(hold),
      'code_only_rule_sweep':rule_sweep(train,hold),'raw_parse_counts':rows,
      'summary':{'books':len(books),'books_with_multiple_raw_segmentation_paths':sum(n>1 for n in counts),'smallest_count':str(min(counts)),'largest_count':str(max(counts)),
        'sum_minimum_tokens':sum(r['min_tokens'] for r in rows),'sum_imported_tokens':sum(r['imported_tokens'] for r in rows),'sum_maximum_tokens':sum(r['max_tokens'] for r in rows)},
      'self_checks':tests,'runtime_seconds':time.monotonic()-start,
      'limits':['Permissive path counts include token boundaries/omission choices. They are not counts of distinct code sequences, English translations, keys or author messages.',
       'Inventory and imported token streams were learned on the public full corpus upstream. This audit does not independently identify the true parse.',
       'Code-only rule sweep serializes the imported code sequence. Failure excludes only that policy class, not contextual, boundary, keyed or other parsing algorithms.',
       'Nine fixed-sequence omission alignments are already ambiguous; annotation-level mixed actions alone are not decisive, so exhaustive raw-string checks are included.',
       'No English score selected a parse. Min/max witnesses are mechanical alternatives only.',
       'A raw-to-English translator needs an independently specified way to choose tokens/omissions on a new raw string; imported positions alone do not provide it.'],
      'verdict':'RAW_DECODER_NOT_IDENTIFIED_NO_VERIFIED_TRANSLATION'}
    (ROOT/'results/zero_restoration_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'summary':out['summary'],'zeros':out['zero_counts'],'sweep':out['code_only_rule_sweep'],'runtime':out['runtime_seconds']},indent=2))
if __name__=='__main__':main()
