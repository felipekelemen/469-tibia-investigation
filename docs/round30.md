# Rodada 30 — fechamento do lote e reprodução independente dos dados

Iniciada em 23/11/2026 e consolidada em 24/11/2026, horário de São Paulo.
Base: `d13c49b3d83651ab9127adbadbaddc00e26e6229`.
Protocolo e fontes do fechamento congelados no commit
`eabfc706df1b98a5b2444fcffd5517c378df035f`.

**Resultado da missão neste lote: I — inconclusivo.** Não encontramos um
algoritmo de tradução validado, nem evidência autenticada de que os textos
tenham sido produzidos originalmente sem uma mensagem. A rodada 30 conclui
o lote do plano v2; não demonstra impossibilidade universal e não encerra a
missão de decifração. Não há nova candidata promissora para compartilhar.

Esta rodada executou auditoria e reprodução. Não realizou outra busca de
cifras nem nova pesquisa de lore na internet. Os resultados anteriores não
foram reclassificados como confirmações apenas porque houve muitas rodadas.

## Resultado verificável do fechamento

- **636 referências de hash**, em **48 manifestos**, coincidem com os arquivos
  atuais. São 487 caminhos distintos; referências repetidas não são verificações
  científicas independentes. Três outros manifestos têm esquemas diferentes e
  são listados separadamente, sem alegação de cobertura pelo verificador genérico.
- Os três arquivos originais de dígitos, o fluxo importado de códigos e a tabela
  CSV foram recuperados dos commits Git registrados na rodada 1. Seus cinco
  hashes coincidem com os registros antigos. Agora estão incluídos no repositório
  público, com procedência e as licenças disponíveis.
- Uma implementação nova reproduziu **70 livros, 11.263 dígitos, 5.729 símbolos,
  99 códigos e 195 zeros iniciais omitidos**. Reproduziu também as nove
  ambiguidades de alinhamento. A checagem usa programação dinâmica para frente,
  em vez da recursão do auditor original.
- Oito procedimentos passaram em uma cópia limpa do commit congelado,
  sem clones ignorados, HTML local, caches ou binários antigos. Nenhum dos
  **759 arquivos** do snapshot foi alterado ou removido; nenhum arquivo novo
  apareceu dentro dele. Os binários foram recompilados em diretórios temporários
  novos, separados por procedimento.

Os dados e códigos da camada intermediária continuam **importados**, não
descobertos como uma chave inglesa. A concordância entre repositórios que
compartilham procedência não equivale a três capturas independentes do jogo.
As ambiguidades são nos livros 2, 10, 13, 14, 19, 27, 35, 57 e 67, com IDs
iniciando em zero. A reconstrução confirma a relação aritmética declarada;
não autentica significado ou intenção autoral.

Fontes e resultados:
[originais empacotados](../data/round30_reference/SOURCES.json),
[integridade](../results/round30_integrity.json) e
[reconstrução](../results/round30_corpus.json).

## Reprodução em cópia limpa

| Procedimento | O que foi repetido | Resultado |
| --- | --- | --- |
| Testes do snapshot | 298 testes, incluindo os cinco primeiros testes de fechamento | Passou |
| R22 | Recompilação C++ e 828 ajustes finitos, incluindo os 12 casos reais pendentes de Chayenne | Passou; nenhum caso real encontrou chave |
| R23 | Certificados locais/fixos e conferência das chaves retornadas | Passou; não é repetição integral da busca limitada |
| R24 | Auditorias numéricas e das propostas de tradução comunitárias | Passou |
| R25 | Experimento estrutural e controles, com os hashes das fontes registradas | Passou |
| R26 | Consistência matricial e controles sintéticos | Passou |
| R28 | 540 ajustes positivos, 396 conjuntos nulos e certificados das fontes reais | Passou |
| R29 | 240 corpora e 50.400 custos de documento/modelo selecionado | Passou |

A reprodução é interna, na mesma infraestrutura, com Python 3.12.14 e g++
14.2.0. Não é revisão por terceiros. Não alegamos ter recalculado integralmente
as 29 rodadas: a seleção está fixada no protocolo e os escopos estão na tabela.
Os domínios de chaves da R22 incluem poda matemática; não são bilhões de
decodificações integrais explícitas.

Na R26, o replay informou corretamente que os corpos HTTP ignorados não
estão distribuídos: foram conferidos os metadados e a parte matemática, sem
nova leitura das capturas históricas. O log de testes preserva um aviso
não fatal de fechamento tardio do arquivo CSV no auditor congelado; não houve
falha de teste nem divergência de bytes ou resultados. Não alteramos esse
programa depois de congelar seus hashes.

[Registro da execução](../results/round30_clean_replay.json) e
[logs completos](../results/round30_replay) permitem conferir comandos,
saídas, tempos, compilação e limites de reprodução.

## Adjudicação das possíveis traduções

O [catálogo de evidências](../data/round30_evidence_catalog.json) reúne oito
famílias de resultados já existentes, preservando fontes e saídas. Ele não
inventa novas frases e não é um classificador automático de inglês.

| Proposta anterior | Saída literal ou situação | Por que não satisfaz T |
| --- | --- | --- |
| Tabela comunitária aplicada a Knightmare | `be a wit than be a fool` | Os próprios rótulos propostos fornecem o inglês; sem transferência ou atestação semântica independente |
| Tabela comunitária aplicada a Evil Eye | `look at you` | Leitura mecânica reproduzida; rótulos externos não confirmados |
| Tabela comunitária aplicada a Elder Bonelord | `let me see you` | Mesma limitação; retirar a fonte do ajuste impede o parse |
| Chave V4 nos livros | Fragmentos como `BUTIWAS` e `THESAND` | Os contextos completos não fornecem inglês coerente sem reparos; reutilização entre livros |
| Transferência da tabela alemã mapping_v7 | Saídas literais e 51 símbolos não mapeados registrados | Não há prosa validada ou conteúdo independente confirmando significado |
| Matrizes R15 | Catálogo de 1.860 configurações | Nenhuma leitura inglesa validada; cribs e geometria física não confirmados |
| Unidades por dígito R23 | 1.769 chaves lexicais de Knightmare | Busca incompleta; compatibilidade lexical não valida semântica |
| Inteiros em bases alfabéticas R28 | Nenhuma candidata integral | Resultado negativo na família e léxico especificados, sem generalização universal |

Os três enunciados da tabela comunitária **não são traduções descobertas nesta
rodada**. A auditoria R24 reproduziu sua aplicação e mostrou que o teste que
reutiliza os próprios rótulos é circular. Duas implementações concordarem com
uma tabela proposta não transforma seus significados em fatos do jogo.

As transcrições prioritárias permanecem preservadas, incluindo `4378` no poema
de Avar Tar e `3478` na fala de Knightmare. Não substituímos um pelo outro.
As partes de Chayenne continuam com 36 e 13 dígitos, reaparecendo 11 e nove
vezes nos livros. Essas cópias não fornecem um gabarito inglês independente.

**T não estabelecido:** falta uma candidata com regra integral, leitura coerente,
previsão independente, atestação semântica e reprodução no escopo declarado.
**G não estabelecido:** não há processo original autenticado, associado a uma
fonte e versão, demonstrando produção sem entrada textual. Os modelos numéricos
criados pela pesquisa não são o gerador original da CipSoft. A R29 mostra
contraexemplos concretos à inferência de ausência de texto por compressão menor.

O [resultado computável da adjudicação](../results/round30_adjudication.json)
é I. Os estados de evidência são julgamentos explícitos baseados nos documentos
citados; o script apenas verifica sua consistência e os requisitos, sem criar
verdade semântica a partir de hashes.

## Famílias encerradas e hipóteses preservadas

| Tema | Decisão ao final do lote |
| --- | --- |
| Sete codecs decimais, permutações fixas e extensões periódicas/com feedback | Buscas publicadas encerradas nos léxicos e enquadramentos fixados; as 12 pendências de Chayenne foram fechadas na R22 |
| Unidades fixas de dígitos para letras/sílabas/fonemas | Manter os certificados exatos onde existem; manter Knightmare/grapheme1_3 incompleto. As falhas de qualificação não refutam todas as cifras dessa classe |
| Inteiros em bases 26/27 e alfabetos afins | Família finita da R28 encerrada sem candidatos nos três alvos; outras bases ou regras não foram eliminadas |
| Transposição colunar do par Kharos/ID22 | Família de 2–32 colunas, nas regras da R13, incompatível; não é rejeição de toda transposição composta |
| 3478 como nome contextual da criatura | Documentado em revisões recuperadas da wiki; não demonstra grafia inglesa literal, ID interno ou chave criptográfica |
| 3478 → BEHOLDER/BONELORD | Negativos restritos às regras testadas; na R28, três símbolos não podem produzir oito letras. Nenhuma equivalência universal confirmada |
| Matrizes 3×3/4×4/5×5 | Encerrar as construções enumeradas; suspender ampliações sem células autenticadas e mecanismo especificado |
| Mudança das caveiras junto à renomeação | Não confirmada. Relatos anteriores à renomeação são circunstanciais; faltam versões comparáveis com contagens completas |
| Origem sem texto | Não demonstrada. Compressão, cópias e cifras fracassadas não autenticam intenção autoral |

Esses estados não equivalem a encerrar todas as possibilidades sob um mesmo
rótulo. O [balanço das 30 rodadas](rounds_01_30_review.md) preserva a sequência,
incluindo resultados condicionais, falhas de potência e buscas incompletas.

## Os sete pedidos da revisão do plano

| Pedido | Estado alcançado |
| --- | --- |
| Demonstrar uma fórmula que traduza | Não alcançado; nenhuma tradução validada |
| Demonstrar origem sem texto | Não alcançado; também não cabe provar inexistência de qualquer função possível em dados finitos |
| Absorver lore e pesquisas publicadas | Fontes, versões, alegações e limites de acesso registrados; não alegamos cobertura completa da internet |
| Priorizar Avar Tar, Knightmare e Chayenne | Alvos testados e catálogos literais preservados; sem reparos orientados pela lore |
| Confirmar ou encerrar 3478/nomes | Separação entre nome contextual, grafia literal, ID, chave e história; decisões delimitadas |
| Confirmar ou encerrar matrizes | Decisões por dimensão, mecanismo e evidência histórica; lacunas preservadas |
| Compartilhar achados e traduções potenciais | Relatórios e artefatos publicados; nenhuma candidata nova neste fechamento |

## Próximos experimentos com maior valor informativo

1. **Obter pares semânticos atestados e independentes.** Priorizar material
   primário dos três alvos: transcrição integral, versão, contexto e uma
   equivalência inglesa explicitamente confirmada. Separar aquisição, descoberta
   e validação; congelar o decoder antes de revelar a parte de validação.
   Uma paráfrase da lore ou outra cópia dos mesmos números não substitui isso.
2. **Investigar o processo autoral original por fonte.** Código de geração,
   material de autoria ou declaração inequívoca e atribuível, ligado aos textos
   e versões, permitiria testar T, G ou uma origem mista. Não inferir que um
   livro decorativo resolveria todas as falas. Não é necessário contatar pessoas
   para manter o registro; nenhum contato foi realizado.
3. **Reabrir Hellgate somente com medições discriminantes.** Precisamos de
   todas as contagens da dimensão proposta em uma mesma versão, e de registros
   comparáveis antes/depois, com nomes e livros pareados. Uma borda 5×5 inventada
   ou outra rotação das mesmas células não acrescenta essa informação.
4. **Reabrir buscas limitadas com método ou restrição novos.** O caso de
   Knightmare permanece disponível, mas uma ampliação deve preservar o léxico,
   declarar a cobertura e demonstrar recuperação em controles correspondentes.
   Não transformar novas palavras acrescentadas após o ajuste em validação.

Não programamos mais uma sequência arbitrária de dezenas de rodadas. Uma
nova evidência ou método discriminante justificará o próximo lote. A conclusão
atual é a melhor sustentada pelos dados disponíveis, não uma garantia de que
469 seja decifrável ou indecifrável.

## Reprodução e publicação

```bash
make test
make round30
```

Para repetir os oito procedimentos, crie uma cópia separada do commit de
insumos, em um diretório novo:

```bash
git worktree add --detach ../469-round30-replay eabfc706df1b98a5b2444fcffd5517c378df035f
cd ../469-round30-replay
python3 scripts/round30_clean_replay.py --commit HEAD
```

Essa cópia ainda não contém os resultados de R30; o script recusa substituir
um registro concluído. Preserve a cópia principal com os resultados publicados.
`make round30` verifica os artefatos atuais, reconstrói os dados e confere os
logs; não finge repetir novamente todas as buscas.

Passaram **301 testes na árvore final**, incluindo os três testes de adjudicação
adicionados depois do snapshot de 298 testes. O registro final de testes e versões está em
[round30_verification.json](../results/round30_verification.json).
Os protocolos e resultados históricos permanecem inalterados.
