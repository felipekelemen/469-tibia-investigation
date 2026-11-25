# Rodada 32 — recuperação das entrevistas originais de Knightmare

25/11/2026 (UTC). Base: `9f59d7e6eac3955c951bff26534fd14af856b78c`.

**Duas lacunas de procedência foram resolvidas. A missão continua inconclusiva.**
Recuperamos o texto original publicado das entrevistas BomDiaTibia e
TibiaEvents em capturas históricas. A atribuição sobre um dicionário permanece
sem fonte original localizada. Nenhuma dessas recuperações fornece uma
tradução de números 469 ou um algoritmo executável.

Esta é uma rodada de aquisição e verificação de fontes, prevista como
prioridade na R31. As condições do protocolo para iniciar outra busca de
cifras não ocorreram; não executamos cifras repetidas para preencher a rodada.

## O que agora tem fonte recuperada

| Alegação | Evidência nova nesta investigação | Decisão |
| --- | --- | --- |
| Knightmare mencionou um tradutor com mais olhos | Entrevista original BomDiaTibia, capturas de 04/05/2018 e 22/07/2019 | Atribuição confirmada no material arquivado; operação criptográfica não especificada |
| Knightmare imaginou uma civilização futura achando a linguagem óbvia | Mesmo artigo e mesmas duas capturas | Contexto recuperado; não é uma observação independente nem prova de decifrabilidade |
| A resposta TibiaEvents de 2014 evita escolher entre as teorias | Texto inglês original, capturas de 01/04/2016 e 02/03/2019 | Confirma o contexto da tradução portuguesa examinada na R31 |
| Knightmare disse que basta um dicionário | Nenhum original recuperado na busca delimitada | Atribuição pendente; não usar como regra confirmada nem declará-la falsa |

O [anúncio do BomDiaTibia](https://www.bomdiatibia.com/entrevista-knightmare-o-mito-por-tras-das-criacoes-tibianas/),
datado de 10/01/2018, contém o endereço exato do fórum, hoje com erro 404.
O índice do Internet Archive levou à
[captura de 2018 da entrevista original](https://web.archive.org/web/20180504032226/https://www.bomdiatibia.com/forum/entrevistas/membros-da-cipsoft-knightmare-o-mito-por-tras-das-historias-tibianas/).
A resposta inglesa completa à pergunta sobre seres de dois olhos é:

> You only need a translator with way more eyes :p

Isso é uma fala em inglês **sobre** 469, não a tradução de uma sequência.
Não determina quantos olhos, qual entidade, uma dimensão de matriz ou uma
operação. Na mesma entrevista, o comentário sobre uma civilização futura
aparece numa resposta sobre continuar criando conteúdo. Ele admite uma leitura
de que exista algo compreensível, mas não demonstra uma cifra inglesa ou um
mesmo mecanismo para todas as fontes. As duas passagens pertencem à mesma
entrevista e não são validações independentes.

Para o TibiaEvents, um [artigo do TibiaSecrets](https://tibiasecrets.com/article87)
forneceu o endereço perdido `/knightmare`; o índice arquivado da wiki também
o relaciona à entrevista. Recuperamos o
[texto inglês em uma captura de 2016](https://web.archive.org/web/20160401184506/https://www.tibiaevents.com/knightmare)
e o conferimos com uma de 2019. A resposta é a mesma: diante de uma pergunta
composta sobre aleatoriedade, solução, quest e dica, Knightmare evita eliminar
ou reconhecer especulações. Não é confirmação de números aleatórios nem de
um decoder. A data atribuída de 2014 vem da publicação contemporânea já
registrada na R31; a captura recuperada mais antiga nesta consulta é de 2016.

## A pista do dicionário

A [atribuição comunitária de 2026](https://www.reddit.com/r/TibiaMMO/comments/1rgakrg/solving_469_part_13/)
continua sem declaração original recuperada. Seu corpo HTTP atual retornou
200, mas continha apenas uma página vazia com o título Reddit. O conteúdo do
índice de busca permanece uma pista, não uma captura do post autenticada pelo
status HTTP.

Além das entrevistas acima, recuperamos versões públicas de quatro entrevistas
históricas ligadas pelo índice arquivado: Rookie 2016, TibiaBR 2010 e duas
TibiaNews, de 2004/2005. A varredura literal das formas de “dictionary”,
“dicionário” e “Wörterbuch” não encontrou correspondências nas oito
representações examinadas. **Esse resultado não cobre sinônimos, imagens,
áudio, entrevistas não localizadas ou declarações nunca publicadas.** Não
prova que a frase jamais tenha sido dita.

Na [entrevista TibiaBR de 2010](https://forums.tibiabr.com/showthread.php?p=5353142#post5353142),
o comentário sobre criação da língua orc é separado de uma história fictícia
sobre um bonelord trabalhando na empresa. Não tratamos a história como
documentação técnica da geração dos números nem transferimos as afirmações
sobre orc para 469.

## Verificação executada

- **16 consultas**, nove operações de página e **21 GETs** direcionados,
  dentro dos limites registrados antes da nova busca.
- Dezoito respostas HTTP 200, uma 402 e duas 404. O 200 sem conteúdo do Reddit
  foi explicitamente separado das entrevistas recuperadas.
- Quatro capturas primárias conferidas contra as URLs originais, o índice CDX,
  a data no endereço de replay e o cabeçalho `Memento-Datetime`.
- Igualdade exata, após extração e normalização de espaços, da resposta
  relevante em cada par de capturas. O contexto adicional do BomDiaTibia também
  coincide. São **duas entrevistas**, não quatro fontes independentes.
- Zero respostas numéricas novas, zero pares semânticos novos e nenhuma
  operação criptográfica determinada pelas fontes.

A extração foi escolhida após inspecionar as páginas; não alegamos avaliação
cega. Os testes conferem datas, URLs aninhadas, codificação ISO-8859-1,
separação de texto visível e respostas. Os julgamentos sobre o sentido das
falas continuam explícitos e analíticos. Hashes não comprovam intenção autoral.

[Protocolo](../data/round32_protocol.json),
[consultas](../data/round32_discovery_log.json),
[metadados HTTP](../data/round32_http.json),
[índices do arquivo](../data/round32_archive_index.json),
[cadeias de procedência](../data/round32_source_trace.json),
[fontes e limites](../data/round32_sources.json) e
[resultado](../results/round32_source_audit.json) permitem conferir o escopo.
Os corpos completos ficam ignorados em `data/private/round32/`; a publicação
inclui trechos breves e metadados. O replay público não precisa desses corpos.

## Consequência para o plano

**H120:** a atribuição de “mais olhos” foi confirmada na entrevista arquivada,
sem confirmar uma interpretação matricial ou um método.

**H121:** o original inglês TibiaEvents foi recuperado e concorda com a
interpretação contextual da R31. A lacuna de aquisição está fechada; a
questão sobre o mecanismo continua aberta.

**H122:** a atribuição de um dicionário permanece não verificada nesta busca.
Não a classificamos como inventada por falta de recuperação.

Não há nova candidata inglesa de Avar Tar, Chayenne ou do NPC Knightmare.
**3478 e Hellgate mantêm as conclusões restritas da R30.** Os comentários
recuperados não fornecem motivo suficiente para repetir rotações ou acrescentar
células a uma matriz. T e G continuam não estabelecidos.

As entrevistas BomDiaTibia e TibiaEvents não precisam mais ser procuradas sem
endereço. A próxima evidência discriminante continua sendo uma equivalência
numérica/textual atestada ou um processo autoral ligado a uma mensagem e
versão. Para uma nova rodada computacional, é necessário especificar uma
restrição adicional ou qualificar um método de recuperação; a frase sobre
olhos, sozinha, não oferece essa restrição. A busca limitada da R23 permanece
incompleta, sem promoção das suas 1.769 chaves lexicais a traduções.

## Reprodução

```bash
make round32
python -m unittest discover -s tests -p 'test_round32_archive.py' -v
```

Conferência adicional, onde as capturas privadas originais existem:

```bash
python scripts/round32_inspect_captures.py
```

Para uma nova captura de um lote registrado, com rede e nome de lote novo:

```bash
python scripts/round32_fetch_sources.py --targets data/round32_targets_confirm.json --batch nova_confirmacao
```

O coletor não substitui capturas anteriores e impõe o orçamento de GETs.
Resultados das verificações e logs: [round32_verification.json](../results/round32_verification.json).

Passaram **317 testes**, incluindo nove novos testes das ferramentas de arquivo.
O replay R32 passou em um diretório temporário com apenas 21 arquivos públicos.
As auditorias das R30/R31 também passaram. O aviso não fatal do leitor CSV
congelado da R30 permanece no log, sem falha de teste ou divergência de dados.
