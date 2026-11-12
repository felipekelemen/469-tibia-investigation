# Sétima rodada: parser exato de dígitos, dois benchmarks e limites do formato

**Nenhuma tradução de 469 foi encontrada.** Executamos duas versões de um
parser de fronteiras/zeros em cifras externas com respostas conhecidas. A
segunda melhora a recuperação, mas ambas falham na qualificação global, mesmo
recebendo chave correta e probabilidades verdadeiras dos homofones. Não houve
busca de chave nem nova leitura dos livros de Tibia nesta rodada.

## Resultado independente V2

V2 foi escolhida em desenvolvimento e congelada antes de abrir autores novos:
Lucy Maud Montgomery e Joseph Conrad. O baseline V1 usa exatamente as mesmas
novas cifras, chaves, emissões e regras. O decoder não recebe fronteiras,
omissões ou o número verdadeiro de letras da mensagem de avaliação.

Cada célula tem 30 casos. Passar exige simultaneamente >=95% de F1 de
fronteiras, F1 de spans de códigos e acurácia de letras por distância de edição.
O gate exige pelo menos 27/30 em **todas** as células.

|Letras|Regra de zeros|V1 pareada, regra conhecida|V2 regra conhecida|V2 regra selecionada|
|---|---|---:|---:|---:|
|64|Preservar todos|30/30|30/30|30/30|
|64|Omitir sempre|20/30|22/30|22/30|
|64|IID 0,3|25/30|27/30|27/30|
|64|Contextual|30/30|28/30|28/30|
|128|Preservar todos|30/30|30/30|30/30|
|128|Omitir sempre|19/30|24/30|24/30|
|128|IID 0,3|27/30|29/30|29/30|
|128|Contextual|30/30|30/30|30/30|

A melhora pareada é **211→220 casos aprovados em 240** na condição com regra
conhecida. A acurácia média de letras chega a 99,12%, mas apenas **185/240
plaintexts são integralmente exatos**; a baseline tem 165/240. Esses números
não devem ser confundidos com 99% de mensagens traduzidas corretamente.
No modo de regra selecionada, 183/240 plaintexts são exatos. Nem o gate oracle
nem o gate selected passa globalmente; os dois cenários de omissão total
permanecem abaixo do mínimo. Não reajustamos o modelo usando esses resultados.

Os cenários IID e contextual passam as células predefinidas de V2. Isso
qualifica somente esses casos favoráveis com chave/emissões fornecidas, nas
duas extensões testadas. Não estabelece a lei de zeros real nem recupera a
chave de 469; não se promove uma qualificação parcial a solução do problema.

## O que foi executado antes de V2

V1 teve 240 condições positivas de Stevenson/London e 480 controles de ordem
pareados. O modelo linguístico melhora bastante o baseline de letras uniformes,
mas passa só 214/240 condições oracle e falha em três das oito células.

A busca é exata para seu modelo probabilístico. Em todos os 26 casos que
falham, o caminho errado tem maior objetivo que o verdadeiro, com vantagens
entre 0,4872 e 20,8001 em log-probabilidade. Logo mais tentativas da mesma
busca não resolveriam essas falhas. A solução exige outra informação ou modelo,
não apenas mais orçamento de otimização.

Depois de abrir V1, quatro configurações de contexto/backoff foram comparadas
nesses mesmos dados: 219, 231, 220 e 229 passes em 240. Foi selecionada ordem
4/backoff 10, mantendo os mesmos segmentos de treino externos. **231/240 é
desenvolvimento**, distinto da qualificação independente V2. V1 inclui um caso
com índice em números romanos; ele não foi removido retrospectivamente.

## Controles e ambiguidade construtiva

As duas versões somam **480 condições positivas e 960 controles pareados**;
os cenários compartilham 120 trechos/chaves, de quatro autores. Não são 1.440
plaintexts independentes. Os controles conservam os códigos e suas frequências,
embaralhando unidades ou blocos de oito. Flags de omissão são preservadas nos
casos sem contexto; na lei contextual, a reserialização pode alterar o tamanho.

Em V2, houve um plaintext errado com posterior de caminho >95% nos controles
de códigos embaralhados e dois nos controles de blocos. A confiança é
condicional ao modelo; não é certificado de gramática ou tradução. Alguns
blocos podem conservar palavras/frases verdadeiras, por isso esses controles
não são declarados universalmente sem significado.

Há também uma ambiguidade demonstrável **antes** de usar inglês. Se todos os
zeros iniciais forem omitidos, o mesmo raw `10` representa:

```text
[10]       → 10
[01, 00]   → 1 | 0
```

Se a omissão for opcional IID, `00` pode vir de `[00]` preservado ou de
`[00,00]` com ambos os zeros iniciais omitidos. As testemunhas foram construídas
e verificadas no inventário importado. Assim, essas classes de serialização
não são injetivas sem restrições adicionais: não garantem recuperação exata de
qualquer sequência de códigos. Isso não demonstra duas frases inglesas válidas,
não prova que 469 use essas regras e não exclui delimitadores, estado, contexto,
checksums ou redundância linguística que resolvam ambiguidades particulares.

## Consequência e próxima prioridade

O componente de segmentação agora tem implementação reproduzível, medidas
separadas de fronteiras/códigos/letras, controles e limites medidos. Ainda não
é um decifrador: fornecer a chave e as emissões verdadeiras foi uma vantagem
forte, indisponível nos livros reais. O mapa V4 e o fragmento `BUT I WAS` da
rodada anterior não ganham nova confirmação com estes experimentos externos.

Priorizar uma regra adicional de fronteiras/zeros, que possa ser verificada
sem escolher palavras aparentes, e modelos externos com palavras/contexto
mais forte, incluindo nomes e colisões conhecidas. Qualquer nova família deve
ser congelada e qualificada em dados novos, mantendo a estrutura de cópia nos
controles. Uma distribuição de omissões por código/estado também deve ser
comparada com IID sem tratar ocorrências copiadas como independentes.
Busca conjunta de chave e segmentação precisa de seu próprio benchmark com
chave escondida; este gate condicional não a substitui.

## Reproduzir e conferir

```sh
make round7
make test
```

93 testes passaram. `make round7` verifica hashes, totais e 32 parses exatos
representativos, de ambos os autores/comprimentos/regras de cada versão.
Os protocolos completos, dados sintéticos, controles e métricas estão em
`data/raw_parser_v{1,2}_protocol.json` e `results/raw_parser_v{1,2}.json`.
O [relatório de método](raw_parser.md) explica as probabilidades, o desenho e
a reexecução integral. `results/raw_parser_summary.json` distingue recuperação
aproximada, plaintext exato, caminho exato e confiança nos controles.
