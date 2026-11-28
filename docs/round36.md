# Rodada 36 — quanto vale uma tradução parcial autenticada?

28/11/2026. Base: `e53567dabd990e8a8fef919b130867b632620a0a`.
**Nenhuma tradução nova.** Esta é uma extensão finita após o encerramento do
ciclo v3, para responder uma pergunta distinta: uma única palavra inglesa
atestada identificaria o restante da fala de Knightmare no modelo da R33?
Não repetimos a busca M1 nem mudamos retrospectivamente os critérios da R35.

## Hipótese e execução

Entrada preservada: `3478 67 90871 97664 3466 0 345!`.
Modelo condicional: cada dígito observado emite uma sequência fixa de uma a
três letras; cada grupo numérico corresponde a uma palavra do léxico congelado
CMU da R23, com a adição hipotética BONELORD já declarada. Homofonia é permitida.
O dígito 2 não aparece e permanece desconhecido. Não há pontuação de inglês,
ajuste pela lore ou inferência de intenção autoral.

O [protocolo](../data/round36_protocol.json) foi fixado antes dos cálculos.
A R33 contava chaves; esta rodada particiona **todas as 153.174.074 chaves**
conforme a palavra emitida em cada posição. Em cada partição contamos as
chaves e verificamos separadamente se a mensagem inteira é única. Duas chaves
diferentes podem produzir as mesmas sete palavras; não confundimos os critérios.

O algoritmo contrai as relações lexicais e combina os ramos dos dígitos 5
e (0,1) por produtos de contagens. Para cada significado hipotético, preserva
uma chave literal e, quando há variação da mensagem, outra chave que prova
essa variação. Não precisa listar os 153 milhões de chaves completas.

## O que uma palavra conhecida resolveria

| Grupo revelado | Palavras possíveis no modelo | Menor número de chaves restantes | Maior número | Significados que deixam mensagem única |
| --- | ---: | ---: | ---: | ---: |
| `3478` | 5.507 | 3 | 1.333.521 | 0 |
| `67` | 132 | 22 | 27.311.502 | 0 |
| `90871` | 39.337 | 6 | 41.047 | 0 |
| `97664` | 1.432 | 3 | 2.325.482 | 0 |
| `3466` | 893 | 3 | 3.362.502 | 0 |
| `0` | 1.084 | 12 | 18.588.412 | 0 |
| `345` | 23.766 | 1 | 31.838 | 131 |

Os extremos consideram somente palavras com pelo menos uma chave compatível.
Uma tradução autenticada fora do conjunto correspondente **contradiria este
modelo, léxico e enquadramento**; não seria licença para alterar a chave à mão.

**Conclusão exata:** revelar apenas um dos primeiros seis grupos nunca
determina toda a fala nesse espaço. Há testemunhas de duas mensagens diferentes
para cada uma dessas possibilidades. O último grupo, `345`, identifica a chave
e a fala em 131 de suas 23.766 possibilidades lexicais. Nas demais há ambiguidade.
Logo, uma palavra autenticada pode ajudar muito, mas não há garantia de que
qualquer palavra única resolva a mensagem — nem de que este seja o modelo real.

Há dois critérios diferentes para priorizar uma pergunta ao autor:

- **Menor incerteza no pior caso:** `345` primeiro (até 31.838 chaves),
  `90871` depois (até 41.047). Isso é condicional a a resposta estar no modelo.
- **Sob pesos uniformes artificiais nas chaves:** `90871` tem maior informação
  média, 14,543 bits e 8.541,54 chaves restantes em média; `345` tem 13,725 bits
  e 13.972,53. Os pesos não são probabilidades sobre a mensagem pretendida.
  Chaves diferentes podem representar o mesmo texto e receber peso repetido.

Nenhum desses critérios autoriza escolher a palavra mais conveniente como
se ela fosse a resposta. A prioridade prática continua ser obter o texto
completo e o mecanismo, se existirem, de fonte autenticada.

## As 131 soluções condicionais não são traduções descobertas

As 131 palavras de `345` que deixam chave única agrupam-se em 12 prefixos
distintos de seis palavras. Todos foram inspecionados literalmente, sem
reparar grafia, trocar nomes ou preencher lacunas. Não encontramos uma frase
inglesa completa coerente que pudesse ser promovida a candidata do jogo.
Essa avaliação é humana/interna, não um classificador ou prova automática
de ausência de inglês em todo o espaço.

Exemplo estritamente condicional: **se** `345` fosse `ACHE`, o modelo retornaria
`ACHMED OM STEEDMAN SMOOCH ACHOO TE ACHE`. Não temos evidência de que `345`
signifique `ACHE`, e a saída não é uma tradução plausível. Unicidade obtida
depois de introduzir uma hipótese de significado não autentica essa hipótese.

Os 12 prefixos e todas as palavras condicionantes estão em
[unique_frames.json](../results/round36/unique_frames.json). Nenhuma candidata
semântica nova foi registrada. Os dois cribs `3478→BEHOLDER/BONELORD` continuam
com contagem zero na família congelada, rechecados pelo contador independente.
Isso não refuta nome contextual, código de palavra inteira ou outra cifra.

## Controles e validação aritmética

O código foi comparado com enumeração direta de **913.050 chaves inteiras**
em 60 casos pequenos: alfabetos unário e binário, emissões variáveis, léxicos
com solução plantada e léxicos amostrados. Contagens por palavra e unicidade
da mensagem coincidiram em todos. Isso verifica o algoritmo exato; não é
qualificação para recuperar inglês natural ou tradução de 469.

Também foram recalculados os cinco primeiros embaralhamentos dentro de grupos
já fixados na R33. Preservam os comprimentos e os dígitos por grupo. Os seis
totais, incluindo Knightmare, concordam com a R33. **Todos os cinco controles
também apresentam palavras condicionantes que produzem mensagem única**:
respectivamente 1.519, 868, 93, 95 e 507 células grupo/palavra, contra 131 em
Knightmare. Essas células não são amostras independentes, e não há teste de
significância. Os controles foram expostos anteriormente; os controles uniformes
da R33 não foram reexecutados pelo motor específico desta topologia.

O resultado mostra por que uma chave lexical única, sob uma palavra escolhida,
não é prova de texto intencional: também ocorre em controles embaralhados.
Não afirma que os controles não admitam nenhuma interpretação possível.

Foram conferidas **267.017 testemunhas de chave** nos seis censos, incluindo
144.171 em Knightmare. Cada uma reconstrói literalmente todas as palavras no
léxico e mantém a âncora; os pares divergem na mensagem completa. Por fim,
**22 contagens condicionais** foram refeitas com o contador original da R33,
sem alterações, incluindo extremos/primeira palavra por grupo e os dois nomes.
Todas terminaram e concordaram. A escolha dessas verificações foi pré-declarada.

Artefatos: [resumo](../results/round36/summary.json),
[conferências independentes](../results/round36/independent_checks.json),
[auditoria](../results/round36_audit.json). Os histogramas completos e as
testemunhas estão em JSON comprimido em `results/round36/*.json.gz`; gzip
é apenas armazenamento e não participa do experimento.

## Reprodução e decisão

```sh
make round36       # integridade, fixtures, contagens e testemunhas
make round36-full  # repete os 60 casos, seis censos e 22 contagens independentes
make test
```

A execução original levou 133,27 segundos de parede, incluindo qualificação
e verificações. Os seis censos consumiram 14,946 segundos de CPU; as 22
conferências, 102,694. Compilação e avaliação Python não estão incluídas nesses
dois subtotais. A reprodução em cópia pública limpa e a suíte completa têm
registro separado em [round36_clean_replay.json](../results/round36_clean_replay.json).
Não houve revisão por terceiro nem contato com autores.

Na cópia limpa, os três procedimentos passaram, incluindo **333 testes**;
todos os 60 casos, seis censos e 22 contagens condicionais foram reproduzidos.
Nenhum arquivo do snapshot foi alterado. O invólucro de reprodução copiado da
R35 emitiu inicialmente o número de rodada 35 no metadado do relatório; apenas
esse campo foi corrigido para 36, junto com a constante do invólucro. Cálculos
e logs ficaram intactos. Os hashes anterior/posterior e a reconstrução da
versão anterior estão na [correção editorial](../data/round36_replay_metadata_correction.json).

H130: **a suficiência de uma única palavra depende da posição e do seu
significado**, com os limites exatos da tabela. H131: **unicidade condicional
lexical não valida significado**, como demonstram os controles. O resultado
da missão continua I. Avar Tar e Chayenne não receberam novas traduções nem
novos ajustes nesta rodada; a lacuna de correspondência semântica permanece.
As decisões sobre matrizes, 3478 e cronologia não foram ampliadas sem fonte nova.

Esta pergunta finita está encerrada. O [roteiro de evidência](evidence_request_round36.md)
transforma o resultado em perguntas específicas para uma eventual fonte
autorizada. Não propomos outro aumento arbitrário da busca ou do dicionário.
