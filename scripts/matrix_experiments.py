"""Bounded Hill-matrix tests. No inferred plaintext or fitted English dictionary.

Run from any directory. Inputs are pinned by the project's source manifest.
The trigram score is only a falsification screen, not a translation validator.
"""
from pathlib import Path
import hashlib
import json
import math
import random

ROOT = Path(__file__).resolve().parents[1]
MATRICES = {
    'old': [[3,1,6,1],[1,2,1,1],[1,1,3,1],[4,6,1,1]],
    'new': [[1,1,1,1],[1,3,6,1],[1,1,4,1],[4,6,1,1]],
}
TRIGRAMS = set('THE AND ING HER ERE ENT THA NTH WAS ETH FOR DTH HAT SHE ION TIO VER EST ERS ATI HIS ALL ITH HES OTH RES'.split())

def determinant(a):
    if len(a) == 1:
        return a[0][0]
    return sum((-1)**j*a[0][j]*determinant([r[:j]+r[j+1:] for r in a[1:]]) for j in range(len(a)))

def transpose(a):
    return [list(x) for x in zip(*a)]

def inverse(a, modulus):
    """Adjugate inversion works for composite moduli; returns None if singular."""
    det = determinant(a)
    if math.gcd(det, modulus) != 1:
        return None
    n = len(a)
    cofactors = [[(-1)**(i+j)*determinant([r[:j]+r[j+1:] for k,r in enumerate(a) if k != i]) for j in range(n)] for i in range(n)]
    inv_det = pow(det, -1, modulus)
    return [[x*inv_det % modulus for x in r] for r in transpose(cofactors)]

def transform(values, matrix, modulus):
    """Column-vector convention; deliberately discard an incomplete final block."""
    n = len(matrix)
    out = []
    for i in range(0, len(values)-n+1, n):
        block = values[i:i+n]
        out.extend(sum(a*b for a,b in zip(row,block)) % modulus for row in matrix)
    return out

def render(values):
    return ''.join(chr(65+x) for x in values)

def score(text):
    return sum(text[i:i+3] in TRIGRAMS for i in range(len(text)-2))/max(1,len(text)-2)

def candidates(books):
    """Explicit bounded family: digit widths 1/2, all alignments, A0/A1 input.

    No padding, no carrying blocks between books. Forward and inverse mod26,
    both row/column conventions. Values >=26 reduced modulo26 explicitly.
    """
    for name, original in MATRICES.items():
        for orientation, matrix in [('column',original),('row',transpose(original))]:
            for direction, operator in [('forward',matrix),('inverse',inverse(matrix,26))]:
                if operator is None:
                    continue
                for width in (1,2):
                    for offset in range(width):
                        for block_offset in range(4):
                            for base in (0,1):
                                decoded=[]
                                retained=0
                                for book in books:
                                    vals=[(int(book[i:i+width])-base)%26 for i in range(offset,len(book)-width+1,width)]
                                    vals=vals[block_offset:]
                                    out=transform(vals,operator,26)
                                    decoded.append(render(out))
                                    retained+=len(out)*width
                                # Separators prevent spurious cross-book trigrams.
                                text='|'.join(decoded)
                                yield {'matrix':name,'orientation':orientation,'direction':direction,'digit_width':width,'digit_offset':offset,'block_offset':block_offset,'input_base':base,'output_base':0,'retained_digits':retained,'score':score(text),'preview':text[:240]}

def block_controls(books, observed_score, replicates=39):
    rng=random.Random(160469)
    maxima=[]
    for _ in range(replicates):
        shuffled=[]
        for book in books:
            blocks=[book[i:i+16] for i in range(0,len(book),16)]
            rng.shuffle(blocks)
            shuffled.append(''.join(blocks))
        maxima.append(max(x['score'] for x in candidates(shuffled)))
    return {'seed':160469,'null':'shuffle nonoverlapping 16-digit blocks within each book, including one possible short final block; preserves named-digit counts and all within-block motifs, not inter-block boundaries or cross-book synchronization','block_digits':16,'replicates':replicates,'max_statistic_scores':maxima,'familywise_empirical_p':(1+sum(x>=observed_score for x in maxima))/(1+replicates),'interpretation':'Exploratory whole-corpus comparison; no semantic holdout. Tests against a null retaining many local motifs, not all repeated modules.'}

def main():
    raw=ROOT/'sources/s2ward/books.json'
    books=json.loads(raw.read_text())
    results={'scope':'Exploratory whole-corpus screen; no semantic holdout claim',
             'input_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
             'book_count':len(books),'matrices':{},'crib_tests':[]}
    for name,matrix in MATRICES.items():
        det=determinant(matrix)
        results['matrices'][name]={'values':matrix,'determinant':det,
            'moduli':{str(m):{'gcd':math.gcd(det,m),'invertible':inverse(matrix,m) is not None} for m in (10,26,27,29,256)}}
    results['matrices']['new']['mod26_collision_witness']={'input1':[0,0,0,0],'input2':[13,13,0,0],'output1':transform([0,0,0,0],MATRICES['new'],26),'output2':transform([13,13,0,0],MATRICES['new'],26),'A0_plaintexts':['AAAA','NNAA']}
    for base in (0,1):
        encoded={}
        for name,crib in [('old','BEHOLDER'),('new','BONELORD')]:
            vals=[ord(x)-65+base for x in crib]
            encoded[name]=transform(vals,MATRICES[name],26)
            results['crib_tests'].append({'matrix':name,'plaintext':crib,'alphabet_base':base,'modulus':26,'column_vector_cipher':encoded[name],'row_vector_cipher':transform(vals,transpose(MATRICES[name]),26)})
        results['crib_tests'].append({'alphabet_base':base,'old_BEHOLDER_equals_new_BONELORD_column_cipher':encoded['old']==encoded['new']})
    results['crib_3478']={'assumption':'Treat 3478 as exactly one digit vector, rather than variable-length identifier',
        'transforms':{name:{str(m):{'forward':transform([3,4,7,8],matrix,m),'inverse':None if inverse(matrix,m) is None else transform([3,4,7,8],inverse(matrix,m),m)} for m in (10,26,27,29,256)} for name,matrix in MATRICES.items()},
        'limitation':'One 4-symbol Hill block cannot decode to an 8-letter name without an extra expansion layer. A numeral 3478 or variable-length code is a separate hypothesis.'}
    observed=sorted(candidates(books),key=lambda r:r['score'],reverse=True)
    results['hill_screen']={'candidate_count':len(observed),'score':f'fraction of positions matching {len(TRIGRAMS)} fixed common English trigrams; weak screening statistic only','best':observed[:8]}
    rng=random.Random(469)
    control_max=[]
    # Each randomization preserves each book's exact digit frequencies/length.
    for trial in range(39):
        shuffled=[]
        for book in books:
            chars=list(book);rng.shuffle(chars);shuffled.append(''.join(chars))
        control_max.append(max(x['score'] for x in candidates(shuffled)))
    p=(1+sum(x>=observed[0]['score'] for x in control_max))/(1+len(control_max))
    results['hill_screen']['controls']={'seed':469,'null':'independent within-book digit permutations, preserving counts and lengths','replicates':len(control_max),'max_statistic_scores':control_max,'familywise_empirical_p':p,'interpretation':'Small p establishes structure relative to this null only, never English or a translation. Shared book fragments invalidate naive independent-book inference.'}
    label_rng=random.Random(3478)
    label_max=[]
    for trial in range(39):
        labels=list('0123456789');label_rng.shuffle(labels)
        mapping=str.maketrans('0123456789',''.join(labels))
        relabeled=[book.translate(mapping) for book in books]
        label_max.append(max(x['score'] for x in candidates(relabeled)))
    label_p=(1+sum(x>=observed[0]['score'] for x in label_max))/(1+len(label_max))
    results['hill_screen']['label_controls']={'seed':3478,'null':'one global bijective digit relabeling, preserving all exact repeat/overlap/equality patterns and frequency spectrum (not named-digit counts)','replicates':len(label_max),'max_statistic_scores':label_max,'familywise_empirical_p':label_p,'interpretation':'Tests whether the specific digit values outperform relabelings while corpus duplication remains intact. No semantic holdout or English validation.'}
    results['hill_screen']['block_controls']=block_controls(books, observed[0]['score'])
    results['status']='No independently verified translation produced; bounded family only. Not a proof against all matrix or multi-layer ciphers.'
    path=ROOT/'results/matrix.json';path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'determinants':{k:v['determinant'] for k,v in results['matrices'].items()},'candidate_count':len(observed),'best_score':observed[0]['score'],'familywise_empirical_p':p,'label_control_p':label_p,'status':results['status']},indent=2))

if __name__=='__main__':
    main()
