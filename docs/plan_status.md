# Quanto falta do plano

**Restam quatro frentes com entregas principais pendentes, dentro das sete
frentes P01–P07. Todas as sete já foram iniciadas.** Três lotes experimentais
delimitados foram executados; isso não significa três frentes integralmente
resolvidas nem que quatro novas rodadas garantam uma tradução.

Esta contagem usa o [plano formal registrado após o Deep Research](next_experiments.md).
A solicitação inicial também incluía tarefas permanentes — repositório público,
corpus, scripts, testes, métricas, registro de hipóteses e relatórios — que já
estão implantadas. Rodadas numeradas são execuções; P01–P07 são linhas de pesquisa.

|Frente|O que já foi feito|O que permanece|
|---|---|---|
|P01 — fontes e validação|16 amostras, proveniência e grafos de reutilização|Conteúdo externo autenticado/novos glosses e validação independente viável|
|P02 — capacidade do solver|V4 qualificada nos cenários de homofonia com tokens fornecidos|Qualificação da segmentação bruta e da busca conjunta com chave escondida|
|P03 — módulos e variantes|Comparações gerativas, positivos, predição de variantes e auditoria modular|Mecanismo que generalize fora dos motivos ajustados; controle modular informativo|
|P04 — busca nos livros|V4 aplicada com 297 controles reotimizados; sem tradução validada|Uma candidata longa e coerente, com algoritmo congelado e evidência externa|
|P05 — palavras/conceitos|Triagem por fonte e subdeterminação semântica documentada|Significados externos atestados e previsões em outra fonte|
|P06 — história das caveiras|Transcrição antiga e cronologia geral recuperadas|Capturas autenticadas dos objetos da sala e data da alteração da matriz|
|P07 — algoritmos matriciais|Famílias finitas Hill, funções aritméticas e leitura 4×4 executadas|Qualquer mecanismo diferente exige regra específica e teste próprio|

As quatro pendências principais são **P01, P03, P05 e P06**. Os lotes de P02,
P04 e P07 têm resultados executados e delimitados, incluindo negativos; seus
gates e extensões não são automaticamente satisfeitos. Em particular, o gate
semântico de P04 continua aberto.

Surgiu uma dependência transversal importante: os 5.729 códigos importados
ainda não vêm de um decodificador raw→tokens validado para mensagens inéditas.
As rodadas 6–8 medem esse problema. Depois de uma candidata, ainda faltará a
validação semântica final e a replicação independente. A contagem de rodadas
até a solução não pode ser prevista com os dados disponíveis.

O estado também está em `data/plan_status.json`, distinguindo lote executado,
entrega pendente e critério de sucesso ainda não atendido. A missão continua
sendo tradução reproduzível, sem letras corrigidas ou significado inventado.
