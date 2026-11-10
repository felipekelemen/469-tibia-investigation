#!/usr/bin/env python3
"""Exploratory power/scope check for repeated encrypted real English motifs."""
import json,pathlib,random,hashlib,time
from homophonic_benchmark import letters,encode,segments
from cipher_battery import english_model
from robust_homophonic import solve
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    prot=ROOT/'data/protocols/copied_prose_stress_v2.json';p=json.loads(prot.read_text())
    source=ROOT/'data/benchmark_reference/frankenstein.txt';plain=letters(source)
    table,_=english_model(ROOT/'data/english_reference/alice.txt');rows=[];started=time.monotonic()
    for i in range(p['fixtures']):
        seed=p['base_seed']+i;rng=random.Random(seed)
        motifs=[plain[x:x+p['letters_per_motif']] for x in [rng.randrange(20000,len(plain)-1000) for _ in range(p['motifs'])]]
        encoded,key,_=encode(''.join(motifs),99,'skewed',seed)
        pools=[encoded[j*256:(j+1)*256] for j in range(8)]
        schedule=[rng.randrange(8) for _ in range(30)];text=''.join(motifs[j] for j in schedule);codes=[c for j in schedule for c in pools[j]]
        train=codes[:5668];hold=codes[5668:6692];truth=text[5668:6692]
        out=solve(segments(train),table,seed=seed+900000,banks=2)
        pred=''.join(chr(out['mapping'][c]+65) for c in hold)
        row={'fixture':i,'seed':seed,'character_accuracy':sum(a==b for a,b in zip(pred,truth))/len(truth),
          'test_characters':len(truth),'unseen_positions':sum(c not in set(train) for c in hold),
          'selected_bank':out['selected_bank'],'train_score':out['train_score'],'known_key_exact':''.join(chr(key[c]+65) for c in hold)==truth,
          'preview':pred[:100],'truth_preview':truth[:100]}
        rows.append(row);print(json.dumps(row),flush=True)
    r={'protocol':p,'protocol_sha256':hashlib.sha256(prot.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
       'trials':rows,'at_least95_percent':sum(t['character_accuracy']>=.95 for t in rows),'runtime_seconds':time.monotonic()-started,
       'limits':['Development-source sensitivity check, not blinded qualification.','Copied motifs and tests overlap by construction, unlike a claim of prospective semantic validation.',
       'Any failure limits rejection of a copied-prose mechanism; no parameter tuning or relaxation of originalV2gate follows this test.']}
    (ROOT/'results/copied_prose_stress_v2.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
