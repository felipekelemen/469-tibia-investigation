# Avaliação lexical independente — rodada 6

**O avaliador não passou a qualificação como juiz geral de coerência.** Seus
custos servem para ordenar leituras exploratórias; não permitem confirmar
tradução nem rejeitar inglês em 469. Nenhuma chave foi ajustada nesta rodada.

## Modelo e protocolo

O modelo usa palavras e transições entre palavras de *The Secret Garden* e
*My Man Jeeves*: primeiros 80% dos tokens para treino, últimos 20% para
desenvolvimento. São 106.204 tokens de treino e 3.833 palavras no vocabulário.
Esses autores não integram o pontuador de tetragramas V4. As fontes completas,
incluindo cabeçalhos e licenças, estão em `data/word_validator_reference/`,
com URLs e SHA-256 em `SOURCES.json`.

Um trie e uma busca de segmentação com beam 8 inserem somente espaços. Há
backoff unigramal nas transições e custo explícito de palavras desconhecidas;
nomes da lore não recebem bônus. Quatro configurações foram comparadas no
desenvolvimento. A escolhida usa custo desconhecido 2,5 e backoff 20, com
limiares separados por comprimento. O protocolo foi congelado antes de abrir
a qualificação, junto com hashes de implementação, fontes e chave existente.

Qualificação: *The Wonderful Wizard of Oz* e *Peter Pan*, 15 trechos por autor
e comprimento, em 32/64/128/160 letras. Cada trecho gera cinco condições:
inglês original, inglês com cerca de 3% de letras trocadas, letras embaralhadas,
palavras embaralhadas e sequência Markov de ordem 3 amostrada do pontuador
caracteral existente. São **600 avaliações**, não 600 textos independentes:
os cinco casos de cada trecho são pareados. Não há novas buscas de chaves.
As janelas começam em fronteiras de palavras e terminam no comprimento exato,
podendo cortar a última palavra ou uma frase. São fragmentos de prosa inglesa,
não necessariamente sentenças completas; isso também limita a interpretação
do gate como avaliação de gramática.

O gate operacional exige, em cada comprimento, aceitar pelo menos 90% de cada
condição positiva e no máximo 10% de cada controle. Texto com palavras
embaralhadas pode conservar frases válidas por acaso; o teste mede capacidade
de distinguir ordem, não certifica que todo controle seja sem significado.
O texto com erros também não é necessariamente gramatical: mede robustez ao
tipo de saída imperfeita que motivou o avaliador.

## Resultado executado

Taxas de aceitação (30 observações por célula):

|Letras|Inglês|Inglês com erros|Letras embaralhadas|Palavras embaralhadas|Markov|
|---|---:|---:|---:|---:|---:|
|32|66,7%|50,0%|0%|50,0%|10,0%|
|64|50,0%|13,3%|0%|10,0%|0%|
|128|96,7%|86,7%|0%|70,0%|0%|
|160|80,0%|23,3%|0%|16,7%|0%|

Nenhum comprimento passa todos os requisitos. O modelo separa bem letras
aleatórias, mas falha com nomes/erros e aceita muitas permutações de palavras.
Não ajustamos novos limiares olhando essa qualificação. Esses textos agora
estão expostos e só podem servir como desenvolvimento numa próxima versão.

## Aplicação exploratória à chave V4 fixa

Depois da qualificação, aplicamos o modelo sem alterações às 70 saídas V4.
Todos os literais foram preservados; os tokens concatenados reproduzem as
5.729 letras. Os dois livros reservados antigos já foram vistos e se sobrepõem.
Há livros mais curtos que o menor comprimento calibrado; não extrapolamos
limiares nem produzimos p-valores por livro.

A melhor pontuação lexical é do livro 4, mas o literal espaçado continua:

```text
SHE M AND EASTEANCIESTRATHINEAME IN THE RENHBERYA THE FOOT HHEDINATSIDGNEDCONT TH
```

Isso ilustra por que uma classificação por custo não é tradução: palavras
comuns coexistem com sequências desconhecidas e não formam uma mensagem.
A [revisão literal](literal_candidate_review.md) também não encontrou uma
leitura longa e gramatical nas saídas fixas. Ela é inspeção linguística,
não um teste estatístico cego, e não exclui outras chaves ou mecanismos.

## Reprodução

```sh
python scripts/word_validator_experiment.py --run
python -m unittest discover -s tests -p test_independent_word_validator.py -v
```

`--run` recalcula os 600 casos e as 70 leituras, substituindo o JSON e seu
tempo de execução. Para conferir a execução publicada sem substituir
artefatos, use `make round6`. Desenvolvimento e congelamento são comandos
separados; não descongelar o protocolo existente para melhorar retrospectivamente
esse resultado. Uma versão nova requer nova qualificação.
