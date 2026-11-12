# Recuperar fronteiras e zeros sem receber a tokenização

Esta rodada testa um componente necessário para um possível tradutor de 469:
interpretar uma string bruta quando zeros iniciais podem ser omitidos.
**As chaves corretas e as distribuições de emissão são fornecidas nos testes.**
Isso torna o problema muito mais fácil que decifrar 469. Nenhum resultado deste
benchmark valida uma chave, tokenização ou tradução comunitária dos livros.

## Modelo probabilístico e busca exata

O encoder possui 99 códigos de dois dígitos, todos exceto 39, repartidos entre
as 26 letras. A repartição e os homofones são aleatórios, com frequências
desiguais. O decoder recebe o mapa verdadeiro e `P(código|letra)`, normalizado
por letra; não recebe o comprimento original, fronteiras ou posições dos zeros.

Em cada posição raw, uma aresta pode consumir dois dígitos como código inteiro
ou um dígito `d` como `0d` com zero omitido. Sua probabilidade é o produto de:

- probabilidade da letra no modelo de caracteres;
- probabilidade do código dada a letra;
- probabilidade de preservar/omitir o zero, quando o código começa com zero;
- probabilidade de continuar a mensagem, `127/128`.

Há um fator final de parada `1/128`, correspondente ao prior geométrico
`P(N=n)=(1/128)(127/128)^n`, para `n>=0`. Assim o objetivo não usa a soma
ingênua de log-frequências conjuntas de tetragramas para comparar comprimentos
diferentes. As transições linguísticas são normalizadas. A distribuição de
comprimentos e o modelo de língua continuam aproximações aos textos reais.

Programação dinâmica guarda a soma forward e o melhor caminho Viterbi por
posição, últimas letras e código anterior módulo 3. Esse estado é suficiente
para os modelos testados. Não há beam nem amostragem no parser: todos os caminhos
admissíveis são considerados, mesclando estados equivalentes. Todo resultado
possível reproduz exatamente seus dígitos brutos ao serializar códigos/omissões.

Testes independentes enumeram caminhos pequenos e conferem a probabilidade
total, o máximo e o posterior. Também conferem o contexto de quarta ordem,
normalização, ausência de limpeza silenciosa, regras e preservação dos controles.

## Regras e desenho experimental

Quatro leis geram as mensagens:

1. preservar todos os zeros;
2. omitir o primeiro zero de todo código 00–09;
3. omitir independentemente com probabilidade 0,3;
4. omitir se o código anterior tiver resto 1 módulo 3; no início, preservar.

No modo **oracle**, o decoder recebe a regra verdadeira. No modo **selected**,
escolhe entre oito modelos usando somente a probabilidade marginal de uma
mensagem separada de calibração com 512 letras: as duas regras determinísticas,
cinco taxas IID (0,1/0,3/0,5/0,7/0,9) e a contextual. A escolha fica fixa na
mensagem de avaliação e nos seus controles. A regra contextual é um controle
sintético predefinido, não uma pista da lore nem hipótese demonstrada para Tibia.

Cada versão tem 30 casos por comprimento/regra: 64/128 letras × quatro regras
= **240 condições positivas**, oriundas de 60 trechos/chaves. Os quatro regimes
são pareados, não 240 plaintexts independentes. Fontes e implementações foram
congeladas antes de cada qualificação. Janelas podem cortar palavras/frases.

O gate exige simultaneamente F1 de fronteiras internas >=0,95, F1 de spans
de código >=0,95 e acurácia por distância de edição das letras >=0,95, em
pelo menos 27/30 casos de cada célula. O F1 não conta os endpoints obrigatórios.
Spans e letras são medidas distintas: fronteiras podem divergir mesmo quando
a mesma sequência de letras é recuperada por homofones.

Para cada caso há dois controles: embaralhar códigos ou permutar blocos de
oito códigos, mantendo seu multiconjunto. Nas regras sem contexto, movem-se
também as flags de omissão, preservando exatamente o comprimento raw. Na
contextual é necessário reserializar segundo a mesma lei, podendo mudar o
comprimento. Ambos continuam cifras válidas com resposta estrutural conhecida,
mas ordem alterada. Não se afirma que todo controle seja sem significado.

## V1: qualificação e diagnóstico

Autores novos: Robert Louis Stevenson, *Treasure Island*, e Jack London,
*The Call of the Wild*. Modelo: transições normalizadas de ordem 3 derivadas
do pontuador amplo anterior. Baseline: letras uniformes, com a mesma chave,
emissões e regra verdadeiras.

Casos que passam os três critérios:

|Letras|Regra|Oracle V1|Regra selecionada V1|Baseline uniforme|
|---|---|---:|---:|---:|
|64|Preservar|30/30|30/30|30/30|
|64|Omitir sempre|20/30|20/30|2/30|
|64|IID 0,3|26/30|25/30|12/30|
|64|Contextual|28/30|28/30|13/30|
|128|Preservar|30/30|30/30|30/30|
|128|Omitir sempre|25/30|25/30|0/30|
|128|IID 0,3|27/30|27/30|6/30|
|128|Contextual|28/30|28/30|13/30|

Os dois gates globais falham. A versão oracle passa 214/240 casos, mas não é
correto usar essa soma para ignorar células fracas. Preservar todos os zeros
é um baseline estrutural trivial de pares, não evidência de criptoanálise.

Nos 26 casos oracle que falham, o caminho errado pontua estritamente acima do
verdadeiro: vantagens de 0,4872 a 20,8001 em log-probabilidade. Como a busca é
exata para esse modelo, aumentar tentativas não recupera a verdade usando o
mesmo objetivo. A explicação é uma limitação do modelo/informação fornecida,
não insuficiência de busca. Isso não exclui modelos mais fortes.

Nos 240 controles de códigos embaralhados, só 60 caminhos são exatos e a
acurácia média de letras é 73,13%. Nos blocos, são 109/240 e 95,89%. Houve
respectivamente 1 e 5 caminhos errados com posterior acima de 95%: esse
posterior mede confiança **dentro do modelo**, não correção real ou semântica.

Limitação de qualidade registrada depois da abertura: o caso 0 de 64 letras
de Stevenson contém índice com números romanos. Os resultados e o gate V1
permanecem intactos; não removemos o caso retrospectivamente. Não se descreve
todo esse benchmark como frases gramaticais contínuas.

## Desenvolvimento depois da falha

Todos os 240 casos V1 agora são desenvolvimento. Quatro modelos interpolados
foram comparados, com ordens 4/6 e backoff 1/10. Usam exatamente os mesmos
segmentos de treino externos do pontuador anterior, sem atravessar fontes.

|Ordem|Backoff|Passam no desenvolvimento|Menor contagem em uma célula|
|---|---:|---:|---:|
|4|1|219/240|24/30|
|4|10|231/240|26/30|
|6|1|220/240|22/30|
|6|10|229/240|25/30|

A seleção maximiza a pior célula, depois o total de passes e a menor acurácia,
com desempate pela menor ordem/backoff. Foi escolhida ordem 4/backoff 10.
**231/240 não é qualificação independente.** O desenvolvimento fornece chave,
emissões e regra verdadeiras; a seleção de regra não foi reavaliada nessa grade.
Contexto e suavização mudam juntos; não se atribui isoladamente o ganho à ordem.

## V2 e artefatos

A versão selecionada foi congelada antes de qualificação em *Anne of Green
Gables*, Lucy Maud Montgomery, e *The Secret Agent*, Joseph Conrad. As janelas
começam ao menos 10.000 letras dentro dos livros, para reduzir o problema de
front matter identificado em V1. O baseline V1 é executado nas mesmas novas
cifras, evitando confundir troca de autores/chaves com ganho do modelo.

Os resultados V2 e a decisão operacional estão na [síntese da rodada](round7.md).
Fontes completas, cabeçalhos/licenças, URLs e hashes ficam nos diretórios
`data/raw_parser_reference/` e `data/raw_parser_reference_v2/`. Nenhum dado de
469 ou palavra da lore foi usado nessas qualificações.

```sh
python scripts/raw_parser_benchmark.py --run
python scripts/raw_parser_benchmark_v2.py --run
make round7
make test
```

Os comandos `--run` recusam substituir uma qualificação existente. Para
reexecutar integralmente, mova o JSON existente para uma cópia preservada e
rode sob o mesmo protocolo; o tempo de execução alterará o hash do resultado.
`make round7` confere os artefatos publicados e repete 32 parses representativos
sem reabrir seleção de modelos nem buscar chaves. O desenvolvimento também
tem artefato próprio, `results/raw_parser_v1_diagnosis.json`.
