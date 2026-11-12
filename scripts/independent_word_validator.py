#!/usr/bin/env python3
"""Independent word/bigram reading cost. Adds spaces only; never repairs letters.

Not a truth detector or lore translator. Unknown words are penalized, so power
must be measured on unfamiliar fantasy names and cipher-like errors.
"""
import collections,functools,hashlib,json,math,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
TRAIN_NAMES=['secret_garden','my_man_jeeves']

def body(path):
    text=path.read_text(encoding='utf-8-sig')
    if '*** START OF THE PROJECT GUTENBERG EBOOK' in text:text=text.split('*** START OF THE PROJECT GUTENBERG EBOOK',1)[1].split('***',1)[1]
    return text.split('*** END OF THE PROJECT GUTENBERG EBOOK',1)[0]

def words(text):
    return [re.sub('[^A-Z]','',w.upper()) for w in re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)*",text)]

class WordModel:
    def __init__(self,documents,min_count=2,max_word=24):
        raw=collections.Counter(w for doc in documents for w in doc)
        self.vocabulary={w for w,n in raw.items() if n>=min_count and len(w)<=max_word and (len(w)>1 or w in ['A','I'])}
        self.vocabulary.update(['A','I']);self.counts=collections.Counter();self.transitions=collections.defaultdict(collections.Counter)
        for doc in documents:
            mapped=[w if w in self.vocabulary else '<UNK>' for w in doc]
            self.counts.update(mapped)
            for a,b in zip(mapped,mapped[1:]):self.transitions[a][b]+=1
        self.total=sum(self.counts.values());self.max_word=max_word;self.trie={}
        for w in self.vocabulary:
            node=self.trie
            for c in w:node=node.setdefault(c,{})
            node['$']=w
    @functools.lru_cache(maxsize=300000)
    def transition(self,previous,following,backoff):
        # Proper word probability with unigram backoff; spelling cost added separately for unknowns.
        uni=(self.counts[following]+.1)/(self.total+.1*(len(self.vocabulary)+1))
        if previous is None:return -math.log(uni)
        row=self.transitions.get(previous,{})
        return -math.log((row.get(following,0)+backoff*uni)/(sum(row.values())+backoff))
    def segment(self,text,*,unknown_cost=2.5,backoff=20,beam=8,max_unknown=24):
        if not re.fullmatch('[A-Z]*',text):raise ValueError('uppercase A-Z input required; no cleaning or repair')
        if not text:return {'segmented':'','tokens':[],'cost_per_letter':0,'known_fraction':1}
        # node=(cost,previous_node,start,end,word,is_known), immutable backpointers.
        n=len(text);states=[{} for _ in range(n+1)];states[0][None]=(0,None,0,0,None,True)
        for i in range(n):
            current=sorted(states[i].items(),key=lambda item:item[1][0])[:beam]
            if not current:continue
            trie=self.trie
            for j in range(i,min(n,i+self.max_word)):
                trie=trie.get(text[j])
                if trie is None:break
                if '$' in trie:
                    word=trie['$'];previous,node=min(current,key=lambda item:item[1][0]+self.transition(item[0],word,backoff))
                    candidate=(node[0]+self.transition(previous,word,backoff),node,i,j+1,word,True)
                    old=states[j+1].get(word)
                    if old is None or candidate[0]<old[0]:states[j+1][word]=candidate
            previous,node=min(current,key=lambda item:item[1][0]+self.transition(item[0],'<UNK>',backoff))
            base=node[0]+self.transition(previous,'<UNK>',backoff)
            for j in range(i+1,min(n,i+max_unknown)+1):
                cost=base+unknown_cost*(j-i)+2*math.log(j-i+1)
                candidate=(cost,node,i,j,text[i:j],False);old=states[j].get('<UNK>')
                if old is None or cost<old[0]:states[j]['<UNK>']=candidate
        best=min(states[n].values(),key=lambda node:node[0]);cost=best[0];tokens=[]
        while best[1] is not None:
            tokens.append({'text':text[best[2]:best[3]],'start':best[2],'end':best[3],'known':best[5]});best=best[1]
        tokens.reverse();assert ''.join(t['text'] for t in tokens)==text
        return {'segmented':' '.join(t['text'] for t in tokens),'tokens':tokens,'cost_per_letter':cost/n,
          'known_fraction':sum(len(t['text']) for t in tokens if t['known'])/n}

@functools.lru_cache(maxsize=1)
def build_model():
    documents=[];metadata=[]
    for name in TRAIN_NAMES:
        path=ROOT/f'data/word_validator_reference/{name}.txt';tokens=words(body(path));cut=int(.8*len(tokens));documents.append(tokens[:cut])
        metadata.append({'name':name,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'training_words':cut,'development_words':len(tokens)-cut})
    model=WordModel(documents)
    return model,{'training_sources':metadata,'vocabulary':len(model.vocabulary),'token_count':model.total,
       'model_source_independence':'Wordtrain authors not used by previous charscorer; no Tibia terms or decodedbook output used for training.'}

def development_letters(name):
    tokens=words(body(ROOT/f'data/word_validator_reference/{name}.txt'));return ''.join(tokens[int(.8*len(tokens)):])
