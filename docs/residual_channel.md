# Canal residual de homofones e zeros — segunda rodada

**Resultado: dependência contextual forte; nenhuma tradução descoberta.** A
análise é condicionada à tokenização e à tabela row0 importadas. Os rótulos
simbólicos não são presumidos letras verdadeiras.

## Pergunta e unidade de análise

Perguntamos se uma mesma sequência de pelo menos oito símbolos pode aparecer
em livros distintos usando códigos numéricos diferentes. Sim: de779 contextos
simbólicos distintos de comprimento8 presentes em pelo menos dois livros,
**56 têm mais de um stream de códigos**, com máximo4 variantes. Em contextos
de24 símbolos,19 de664 apresentam duas variantes. Exemplos com representantes
reais das variantes e suas posições zero-based estão no JSON.

Essas contagens são de contextos distintos, não ocorrências. Ainda há janelas
sobrepostas e livros dependentes:56 contextos variáveis não significam56
mensagens ou eventos independentes. Não é correto inferir capacidade positiva
de mensagem a partir de variantes, nem inferir capacidade universal nula por
não ter encontrado tradução.

| Comprimento da janela | Contextos entre livros | Com múltiplos streams | Acordo exato médio dos códigos |
|---|---:|---:|---:|
|4|656|249|78,112%|
|8|779|56|96,262%|
|12|789|41|97,113%|
|16|765|33|97,650%|
|24|664|19|98,293%|

O acordo é a proporção de pares de ocorrências **de livros diferentes** com
stream numérico idêntico, calculada separadamente para cada contexto simbólico;
depois se tira a média com peso igual por contexto. Isso evita que a frequência
de uma única frase repetida domine toda a estatística, mas não torna contextos
sobrepostos independentes.

## Nulo que preserva o substrato

Em199 réplicas, cada código é embaralhado apenas entre posições do mesmo
símbolo **dentro do mesmo livro**. Assim, preservam-se exatamente comprimento,
sequência de símbolos e contagem de cada código em cada estrato livro/símbolo.
Destrói-se a associação com o contexto local e com a ocorrência específica.
A semente é46920261110. Não se usa como nulo uma distribuição uniforme de100
códigos, que alteraria a própria camada intermediária.

| Estatística | Observado | Média do nulo | p exploratório relevante |
|---|---:|---:|---:|
| Acordo exato dos códigos em contextos8 |0,962622|0,000008147|0,005, superior|
| Contextos8 com variantes distintas |56|779|0,005, inferior|
| Próximo homofone igual ao sucessor modal ajustado |0,367674|0,267580|0,005, superior|
| H(próximo código\|código anterior,símbolo),bits |2,437582|2,855109|0,005, inferior|
| Sucessor em ciclo numérico crescente |0,110426|0,116494|0,960, superior|

A primeira linha tem valor observado completo0,9626220722 no JSON; o
arredondamento na tabela não é usado nos cálculos. A previsão modal é ajustada
novamente em cada controle. A sucessão de homofones é medida entre ocorrências
consecutivas do **mesmo símbolo**, reiniciando em cada livro; não entre letras
adjacentes no texto.

A ordenação de ciclo foi predefinida como ordem numérica dos códigos de um
símbolo; sua taxa não mostra vantagem. Isso não exclui ciclos com outra ordem,
estados por palavra ou regras dependentes de contexto. A cauda inferior desse
mesmo teste é0,045, sem correção múltipla; não se interpreta como descoberta.

Os resultados fortes mostram que os códigos guardam relações contextuais
além das marginais. A reutilização de fragmentos previamente codificados é
compatível com esse resultado, assim como outros mecanismos determinísticos.
**Não discriminamos autoria por cópia, texto cifrado ou estrutura artificial
com esses testes.** Os p são de aleatorização desse modelo, não probabilidades
de mensagem. Há cinco estatísticas e duas caudas, sem correção de multiplicidade;
nenhuma conclusão semântica é promovida.

## Entropia, deduplicação e limites

H(código\|símbolo),ponderada pelas posições observadas, é2,879726bits. É
incerteza descritiva da distribuição de códigos, não capacidade de um canal
nem número de bits ocultos. Para contextos8, a entropia média da variante
numérica é0,060110bits por janela, atribuindo peso igual a cada contexto
compartilhado e usando suas frequências empíricas internas. Janelas maiores
mostram menor ambiguidade. Estas grandezas não podem ser somadas entre
janelas sobrepostas para estimar uma mensagem.

A deduplicação se limita ao agrupamento por sequência simbólica distinta e
à exclusão de pares do mesmo livro. Não há amostra de origem independente,
plaintext atestado nem modelo completo de geração. O valor99 códigos→14
rótulos já foi construído a partir do corpus inteiro upstream.

## Zeros omitidos

São contabilizadas195 remoções de zeros iniciais, por código, com totais de
códigos elegíveis no resultado. Nove livros têm alinhamentos compatíveis
ambíguos. As posições são uma solução de alinhamento condicionada aos streams
importados, não observações diretas do processo autoral. Não foi encontrado
algoritmo que traduza essa máscara em inglês, nem se promove a máscara a
canal independente. Comparações sem tratar a ambiguidade seriam frágeis.

## Controles positivos e reprodução

```
python scripts/residual_channel.py
python -m unittest discover -s tests -p test_residual_channel.py -v
```

Cinco testes passaram. Confirmam conservação exata das marginais condicionais,
detecção de variantes em contextos artificiais, exclusão de repetições de um
único livro, valores de entropia conhecidos e sensibilidade de ciclo/entropia.
No controle com rotação conhecida de quatro homofones, a taxa de sucessor é1
e a entropia condicional é0. No controle iid com o mesmo alfabeto a taxa fica
perto de1/4 e a entropia perto de2bits. Esses controles validam a mensuração,
não a decifração.

## Classificação das variantes em contextos maximais

Expandimos cada par de ocorrências simbólicas iguais à esquerda e à direita
até seus limites de igualdade. Depois deduplicamos pela sequência simbólica
e pelo par não ordenado de streams numéricos. Permanecem106 trechos maximais
com divergência. Esse agrupamento elimina shifts de janela do mesmo par,
mas trechos de pares diferentes ainda podem ser aninhados ou sobrepostos.

Nas181 posições divergentes contabilizadas nesses106 registros:

-51 são reversões dos dois dígitos,como34↔43;
-130 são outros pares de homofones,como06↔65;
-0 são19↔91.

Há52 tipos distintos de pares de códigos divergentes. Essas181 posições não
são181 eventos independentes. Na tabela importada,19→I e91→N: a reversão19↔91
não é invisível na sequência simbólica e, portanto, não pode ocorrer como
homofonia dentro dos mesmos contextos desta análise. Não pressupomos uma
regra universal de reversão dos dígitos.

Um exemplo de105 símbolos compartilhados ocorre no livro46 a partir do
código20 e no livro51 a partir do código25 (índices zero-based). Os primeiros
102 códigos são idênticos; os três finais são06/51/59 contra65/15/95. Isso
é uma divergência concreta em contexto longo, mas localizada na fronteira
de uma sequência compartilhada; não é evidência de mensagem escondida.
Os oito exemplos mais longos constam no JSON com coordenadas e códigos
integrais para reprodução.

## Orientação dos dígitos como bits

Testamos uma hipótese limitada: código de dígitos diferentes com primeiro
menor→0,primeiro maior→1; códigos palindrômicos são omitidos. Bits são
agrupados em bytes big-endian, reiniciando por livro. Enumeramos offsets0–7
e inversão0↔1,total16 candidatos. O escore é a proporção de bytes que são
letras inglesas, espaços, whitespace ou pontuação comum; a proporção ASCII
imprimível é relatada separadamente. Não é um pontuador de prosa.

O melhor candidato(offset5,sem inversão) tem581 bytes,29,776% no conjunto de
caracteres definido e39,071% ASCII imprimível. Em99 controles com shuffle
de códigos dentro de cada estrato livro/símbolo, escolhendo novamente o
máximo entre os16 candidatos, p de cauda superior=**0,28**. Nenhuma sequência
foi promovida a inglês. Prévia hexadecimal e literal escapada estão no JSON.
Esse teste é exploratório no corpus inteiro; não alega holdout ou exclui
outras convenções de bits, palíndromos, ordem de bytes ou cifra adicional.

O teste positivo constrói os bits de `HELLO WORLD`,converte0→12 e1→21 e
recupera exatamente seus bytes. A classificação de reversões e a deduplicação
de contextos maximais têm testes próprios. Total atualizado: **8 testes passam**.
