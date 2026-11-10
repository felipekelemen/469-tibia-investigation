# Geometria da tabela de códigos — segunda rodada

Pergunta: uma função aritmética simples dos dois dígitos, incluindo operações
com as matrizes de Hellgate, explica exatamente o mapa intermediário importado?
Foram testadas53 funções predefinidas: soma, produto, XOR,AND,OR,diferença
absoluta, soma dos quadrados, produto+soma, par não ordenado, consultas4×4 por
resíduos módulo4 e formas bilineares dos vetores binários de quatro bits dos
dígitos sob as matrizes antiga/posterior e suas transpostas. As formas
bilineares usam ordens de bits baixa/alta e módulos10,14,26,29,100.

Para cada função, agrupamos os99 códigos por seu valor. Se um grupo contém
rótulos distintos, **nenhuma** tabela de substituição determinística que
receba somente esse valor consegue reproduzir o mapa inteiro. O erro mínimo
é calculado escolhendo o rótulo mais frequente de cada grupo. Não inferimos
que os nomes dos rótulos sejam letras verdadeiras.

Nenhuma das53 funções explica todos os99 códigos:

| Função | Número mínimo de códigos incompatíveis |
|---|---:|
| Par não ordenado dos dígitos |1|
| Soma de quadrados |7|
| Produto+soma |19|
| Produto |27|
| Melhor função derivada das caveiras nesta grade |59|

A estrutura de quase simetria já é visível no mapa:19→I e91→N são uma
exceção explícita;39 está ausente, portanto não podemos lhe atribuir valor
por simetria. O par não ordenado define55 valores distintos, uma tabela de
alta capacidade, e não um algoritmo curto de tradução. Ele acerta98/99
entradas ajustando toda a tabela, mas cobre somente88 entradas em teste
leave-one-code-out, das quais86 corretas. Isso não é holdout de livros,
muito menos validação de inglês.

999 permutações dos rótulos preservam suas multiplicidades e repetem a
seleção do máximo entre todas as funções. O máximo observado0,989899
supera a média dos máximos nulos0,602795 e seu máximo0,676768,p=0,001.
Isso demonstra geometria na **tabela importada**, não significado ou autoria.
As funções das caveiras falham em reproduzi-la exatamente nas convenções
declaradas; não se excluem outras representações, funções ou camadas.

Reprodução: `python scripts/map_geometry.py`. Três testes verificam colisões
incompatíveis, controle positivo de tabela determinística e valores bilineares
em vetores da base que distinguem orientação da matriz.
