#!/usr/bin/env python3
"""Calibrate an independent lexical cost on external English, then audit fixed469outputs.

No key selection, no lore bonuses, no edits except spaces. Candidate rankings
are exploratory, not translation or grammaticality proofs.
"""
import argparse,collections,datetime,hashlib,json,pathlib,random,time,math
import numpy as np
from independent_word_validator import build_model,development_letters,body,words
from copied_homophonic_v3 import build_model as char_model
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'data/word_validator_protocol.json'
LENGTHS=[32,64,128,160]
@__import__('functools').lru_cache(maxsize=1)
def transitions():
    table,_=char_model();p=10**table.reshape(26**3,26);return p/p.sum(axis=1)[:,None]

def markov_text(prefix,n,rng):
    probs=transitions();out=list(prefix[:3])
    while len(out)<n:
        a,b,c=[ord(x)-65 for x in out[-3:]];index=(a*26+b)*26+c
        out.append(chr(rng.choices(range(26),weights=probs[index],k=1)[0]+65))
    return ''.join(out)

def window(tokens,start,length):
    # Preserve sourceword identities for a word-order control. Allow cut final word.
    out=[];n=0;i=start
    while n<length:
        if i>=len(tokens):raise ValueError('source too short')
        w=tokens[i][:length-n];out.append(w);n+=len(w);i+=1
    return out,i

def controls(parts,seed):
    rng=random.Random(seed);text=''.join(parts);sh=list(text);rng.shuffle(sh)
    wo=parts[:];rng.shuffle(wo)
    if ''.join(wo)==text and len(wo)>1:wo=wo[1:]+wo[:1]
    noisy=list(text)
    for i in rng.sample(range(len(noisy)),max(1,round(.03*len(noisy)))):
        choices=[c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c!=noisy[i]];noisy[i]=rng.choice(choices)
    return {'english':text,'english_noisy3':''.join(noisy),'shuffle_letters':''.join(sh),
      'shuffle_words':''.join(wo),'quad_markov':markov_text(text[:3],len(text),rng)}

def development():
    model,meta=build_model();samples=[]
    for name in ['secret_garden','my_man_jeeves']:
        tok=words(body(ROOT/f'data/word_validator_reference/{name}.txt'));cursor=int(.8*len(tok))
        for n in LENGTHS:
            for i in range(10):
                parts,cursor=window(tok,cursor,n);samples.append({'length':n,'controls':controls(parts,61069000+n+i+(0 if name=='secret_garden' else 1000))})
    summaries=[];trials=[]
    for config in [{'unknown_cost':u,'backoff':b} for u in [2.5,3.0] for b in [20,100]]:
        rows=[]
        for s in samples:
            scores={label:model.segment(text,**config)['cost_per_letter'] for label,text in s['controls'].items()}
            rows.append({'length':s['length'],'scores':scores})
        thresholds={};quality=[]
        for n in LENGTHS:
            part=[r for r in rows if r['length']==n];pos=[r['scores'][k] for r in part for k in ['english','english_noisy3']]
            neg=[r['scores'][k] for r in part for k in ['shuffle_letters','shuffle_words','quad_markov']]
            candidates=sorted(set(pos+neg));best=max(candidates,key=lambda t:(sum(x<=t for x in pos)/len(pos)+sum(x>t for x in neg)/len(neg),-t))
            thresholds[str(n)]=best;quality.append((sum(x<=best for x in pos)/len(pos)+sum(x>best for x in neg)/len(neg))/2)
        summaries.append({'config':config,'thresholds':thresholds,'development_balanced_accuracy':sum(quality)/len(quality)})
        trials.append({'config':config,'rows':rows})
    selected=max(summaries,key=lambda s:s['development_balanced_accuracy'])
    r={'role':'development only, externalwordmodel authors last20%','model':meta,'summary':summaries,'selected':selected,'trials':trials}
    (ROOT/'results/word_validator_development.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(summaries,indent=2),flush=True)

def freeze():
    if PROTOCOL.exists():raise RuntimeError('alreadyfrozen')
    selected=json.loads((ROOT/'results/word_validator_development.json').read_text())['selected']
    source=json.loads((ROOT/'data/word_validator_reference/SOURCES.json').read_text())
    p={'version':'LEXICAL_VALIDATOR_V1','frozen_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'selected':selected,'model':build_model()[1],'lengths':LENGTHS,'qualifications_per_length':30,
      'train_authors':['FrancesHodgsonBurnett','P.G.Wodehouse'],'qualification_authors':['L.FrankBaum','J.M.Barrie'],
      'gate':'Eachlength:>=90% acceptance for pristine/noisy English separately,<=10% acceptance pernegative type. Otherwise notqualifiedasgenericcoherencejudge.',
      'negative_types':['shuffle_letters','shuffle_words','quad_markov'],'positive_types':['english','english_noisy3'],
      'candidate_policy':'Rank all fixedV4outputs only afterqualification; addspacesonly; manualgrammar/lore audit required. No lorewordprior.',
      'source_hashes':{r['name']:r['sha256'] for r in source},
      'implementation_hashes':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in ['scripts/independent_word_validator.py','scripts/word_validator_experiment.py','scripts/copied_homophonic_v3.py','scripts/homophonic_benchmark.py']},
      'key_result_sha256':hashlib.sha256((ROOT/'results/qualified_tibia_search_v4.json').read_bytes()).hexdigest(),
      'limits':['Independentmodel/wordtraintexts, notstatisticalindependence ofgamevalidation.',
        'Unknownfantasywordsandnames penalized; calibrationtests poweronunfamiliarfantasyfiction and3%errors.',
        'Perlengththresholds are notpvalues or proof ofgrammar; shortgamebooks may fall between/outsidecalibrationlengths.']}
    PROTOCOL.write_text(json.dumps(p,indent=2)+'\n');return p

def verify(p):
    for f,h in p['implementation_hashes'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h:raise ValueError('sourcechanged:'+f)
    for name,h in p['source_hashes'].items():
        if hashlib.sha256((ROOT/f'data/word_validator_reference/{name}.txt').read_bytes()).hexdigest()!=h:raise ValueError('referencechanged')

def run():
    p=json.loads(PROTOCOL.read_text());verify(p);model,_=build_model();config=p['selected']['config'];started=time.monotonic();rows=[];summaries=[]
    for name in ['wizard_oz','peter_pan']:
        tok=words(body(ROOT/f'data/word_validator_reference/{name}.txt'));cursor=200
        for n in LENGTHS:
            for i in range(15):
                parts,cursor=window(tok,cursor,n)
                for label,text in controls(parts,62069000+n+i+(0 if name=='wizard_oz' else 1000)).items():
                    s=model.segment(text,**config);rows.append({'source':name,'length':n,'fixture':i,'label':label,
                       'cost_per_letter':s['cost_per_letter'],'known_fraction':s['known_fraction'],
                       'accepted':s['cost_per_letter']<=p['selected']['thresholds'][str(n)]})
    for n in LENGTHS:
        part=[r for r in rows if r['length']==n];rates={label:sum(r['accepted'] for r in part if r['label']==label)/30 for label in ['english','english_noisy3','shuffle_letters','shuffle_words','quad_markov']}
        passed=rates['english']>=.9 and rates['english_noisy3']>=.9 and all(rates[k]<=.1 for k in p['negative_types'])
        summaries.append({'length':n,'acceptance_rates':rates,'passes_gate':passed})
    # Fixed key only. Wordmodel may add spaces, never refit/rewrite plaintext.
    result=ROOT/'results/qualified_tibia_search_v4.json'
    if hashlib.sha256(result.read_bytes()).hexdigest()!=p['key_result_sha256']:raise ValueError('keychanged')
    mapping=json.loads(result.read_text())['observed']['mapping'];books=json.loads((ROOT/'data/normalized_books.json').read_text());split=json.loads((ROOT/'data/normalized_splits.json').read_text());candidates=[]
    for b in books:
        literal=''.join(chr(mapping[int(c)]+65) for c in b['codes']);s=model.segment(literal,**config)
        assert ''.join(t['text'] for t in s['tokens'])==literal
        candidates.append({'book_id':b['id'],'length':len(literal),'source_split':'discovery' if b['id'] in split['discovery_book_ids'] else 'old_exposed_holdout',
           'literal':literal,**s,'decision':'ranking only; no automatic semantic acceptance'})
    out={'protocol':p,'protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'qualification':summaries,'qualification_trials':rows,
       'global_gate_passes':all(r['passes_gate'] for r in summaries),'all_books':candidates,
       'top10_lowest_cost_book_ids':[r['book_id'] for r in sorted(candidates,key=lambda r:r['cost_per_letter'])[:10]],
       'runtime_seconds':time.monotonic()-started,'verified_translations':0,'limits':p['limits']}
    (ROOT/'results/word_validator_audit.json').write_text(json.dumps(out,indent=2)+'\n');verify(p)
    print(json.dumps(summaries,indent=2),flush=True)
    print(json.dumps([{k:r[k] for k in ['book_id','literal','segmented','cost_per_letter','known_fraction']} for r in sorted(candidates,key=lambda r:r['cost_per_letter'])[:5]],indent=2),flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--development',action='store_true');a.add_argument('--freeze',action='store_true');a.add_argument('--run',action='store_true');args=a.parse_args()
    if args.development:development()
    if args.freeze:print(json.dumps(freeze(),indent=2))
    if args.run:run()
