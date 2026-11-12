# Oitava rodada: restrições exatas dos zeros e posição no plano

**Não foi encontrada tradução.** Foram testadas 15 famílias de regras de
formatação, sem inglês: 13 são incompatíveis com os códigos importados, e duas
tabelas locais reproduzem os livros de descoberta, mas não identificam uma
regra para os eventos reservados. Esta é uma auditoria da etapa numérica,
condicionada à tokenização pública, não uma solução raw→inglês.

A [posição no plano](plan_status.md) esclarece a contagem: sete frentes já
iniciadas, três lotes delimitados executados e quatro frentes com entregas
principais pendentes. A dependência raw→tokens e a validação semântica final
permanecem abertas; não há número garantido de novas rodadas até a solução.

## Pergunta e método

Existe alguma função determinística compartilhada que escolha omitir/preservar
o primeiro zero de cada código 00–09 e reproduza exatamente os dígitos?

Mantivemos os streams de códigos fixos. Um algoritmo forward/backward contou
**79 alinhamentos completos** nos 70 livros: 61 livros com um e nove com dois.
Dos 634 eventos de zero, 616 têm ação forçada e 18 permitem ambas. Todas as
alternativas foram consideradas, preservando a dependência entre eventos do
mesmo alinhamento; não escolhemos a anotação que favorece uma hipótese.

Para cada família, o algoritmo pergunta se existe **qualquer tabela booleana**
com as características declaradas. Assim, não depende de acertar um classificador
ou enumerar chaves. Uma contradição forçada fornece dois eventos com as mesmas
entradas e ações opostas em todos os alinhamentos possíveis. Nos demais casos,
busca exata combina os alinhamentos completos. Limites de recursos retornam
"não resolvido", nunca uma rejeição; não foram atingidos nos dados reais.

O protocolo foi congelado antes desta execução. Ajustes usam os 68 livros de
descoberta; os dois reservados antigos já são expostos e correlacionados. A
verificação reservada recebe os códigos importados e não é teste de tradução.

A pesquisa de Kim Lage já apresenta associações locais dos zeros em
[regras compactas](https://github.com/kimlage/tibia-469-cipher-casestudy/blob/4d726a8de7af1f2216bd48d9b86165e0c50616b6/analysis/generator_search_20260618/zero_compact_rule_report.md).
A auditoria atual acrescenta todos os alinhamentos e a verificação de existência
de qualquer tabela nas famílias declaradas. Caminhos, commit e hashes dos três
relatórios anteriores ficam em `data/zero_rule_prior_sources.json`. Seus
resultados não foram usados como glosses ou como confirmação de tradução.

## Famílias executadas

|Entrada permitida da função de zeros|Resultado em descoberta|
|---|---|
|Código atual|Incompatível — baseline já excluída na rodada 6|
|Código atual e 1/2/3/4/8 códigos anteriores|Todas incompatíveis|
|Código atual e próximo código|Incompatível|
|Janela de um código de cada lado|Incompatível|
|Janela de três códigos de cada lado|Tabela possível: 262 entradas|
|Janela de oito códigos de cada lado|Tabela possível: 359 entradas|
|Código atual e posição em ciclos de 2/4/8/16|Todas incompatíveis|
|Código atual, anterior e posição no ciclo de 16|Incompatível|

São famílias de formatadores condicionados, não 15 algoritmos completos de
decifração. Uma entrada de tabela pode ser uma regra memorizada para um
contexto; a compatibilidade não fornece idioma ou significado.

## Duas contradições úteis

**Início do livro:** os livros 30 e 64 começam com o mesmo código importado
`09`. No 30, o zero é obrigatoriamente preservado; no 64, é obrigatoriamente
omitido. Ambos têm alinhamento único. Sob um estado inicial comum e acesso só
ao código atual/passado, qualquer formatador determinístico teria a mesma
decisão inicial. Logo essa classe causal precisa de informação adicional:
estado inicial variável, comprimento, metadados, lookahead, aleatoriedade ou
outra tokenização são alternativas ainda possíveis. O argumento não depende
de limitar a memória a oito códigos.

**Ciclo 4×4:** no mesmo livro 6, os índices zero-based 61 e 77 contêm o código
`01`, ambos precedidos por `16`. Ambos ocupam a posição 13 módulo 16. Em um
o zero é forçosamente omitido; no outro é preservado. O conflito persiste sob
qualquer fase constante ou permutação fixa das células desse livro.

Isso exclui a função de zeros baseada apenas em código atual, anterior e célula
de um ciclo fixo de 16 códigos. Inclui usar a quantidade de caveiras dessa
célula como única informação adicional. **Não exclui as matrizes como componente
de outros algoritmos**, estado que muda entre blocos, mistura, lookahead ou
tokenizações diferentes. Não data a alteração das caveiras nem valida a
relação BEHOLDER/BONELORD.

Certificados com livros, índices, entradas, posições raw e ações forçadas
estão em `results/zero_rule_constraints.json`; a extensão lógica está em
`results/zero_rule_identifiability.json`.

## Duas tabelas que cabem, sem previsão identificada

As janelas maiores permitem tabelas que reproduzem os 68 livros. Porém os
**sete eventos de zero dos dois reservados têm características não vistas no
treino**, nas duas famílias. O default congelado de preservar zeros erra os
dois livros. Isso não rejeita todas as extensões possíveis da família:

- Na janela de três códigos de cada lado, há seis novas entradas: **64
  extensões booleanas** igualmente compatíveis com o treino.
- Na janela de oito, há sete novas entradas: **128 extensões**.

Essas são contagens de tabelas, não mensagens ou traduções. Construímos duas
extensões de cada tabela que preservam todos os acertos de descoberta e
produzem dígitos diferentes nos reservados. Também mostramos uma extensão que
acerta os dois reservados **depois de receber suas respostas**: ela é ajuste
retrospectivo explícito, nunca previsão. Esse exemplo registra como vazamento
poderia produzir um falso relato de sucesso.

## Controles e alcance

- **15 positivos plantados:** um formatador conhecido por família; todos foram
  reconhecidos como compatíveis.
- **39 embaralhamentos dentro de código/livro:** preservam os streams, contagens
  de omissão por código/livro e comprimentos raw por livro. Alteram de 18 a
  29 livros por réplica. Nenhuma família explica todos os livros de descoberta
  nessas réplicas.
- **9 controles de contexto copiado:** uma decisão mecânica compartilhada por
  janela de sete códigos; as famílias de janelas 3 e 8 aceitam todas as
  réplicas. Preservam códigos e consistência entre contextos copiados, mas não
  todas as contagens/comprimentos raw observados.

O teste principal é lógico, sem p-valores. Cópias repetidas não transformam uma
contradição em observações independentes. Os controles medem a capacidade do
teste e alternativas de formatação; não demonstram ausência ou presença de
significado nos códigos. O sinal contextual também não identifica qual
processo original gerou a escrita.

## Consequência prática e próxima prioridade

Uma regra simples dependente apenas de passado ou de ciclo fixo 4×4 não resolve
os zeros dessa reconstrução. Tabelas mais largas conseguem memorizar a camada,
mas ainda não geram previsões novas. Antes de ampliar novamente o pontuador de
inglês, priorizar a verificação da proveniência da tokenização e das fronteiras,
com registros independentes dos dígitos e contexto de cada livro. Estado
inicial, lookahead ou informação de comprimento devem entrar como hipóteses
explícitas, pagando sua complexidade, sem ajustes diferentes por livro.

As exclusões mantêm os códigos importados fixos; outra tokenização pode escapar
delas. As três cópias comunitárias dos dígitos compartilham linhagem, portanto
a concordância entre elas não substitui observação independente do jogo.
Nenhum nome de NPC, palavra da lore ou fragmento inglês pontuou estes testes.

## Reprodução

```sh
make round8
make test
```

98 testes passaram. A verificação repete os alinhamentos, as 15 decisões
principais e os certificados, sem trocar os artefatos publicados. Os comandos
completos são `python scripts/zero_rule_experiment.py --run` e
`python scripts/zero_rule_identifiability.py`; o primeiro recusa substituir
um resultado existente. Fontes, limites e decisões estão no protocolo congelado.
