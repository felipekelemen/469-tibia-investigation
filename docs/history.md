# Auditoria histórica e de lore — primeira rodada (2026-11-10)

## Conclusão

A matriz posterior fornecida pelo usuário é reproduzida literalmente por uma fonte comunitária externa consultada nesta rodada. A renomeação Beholder → Bonelord é datada pela Tibia Wiki BR no patch 8.61, em **23 de agosto de 2010**. **Não foi encontrada uma data verificável para a alteração da matriz**, portanto a coincidência histórica com a renomeação permanece não demonstrada. Nenhuma fonte consultada fornece uma tradução autorizada de livro 469 para inglês.

## Método e preservação

Consultas HTTP foram feitas sem executar código das páginas. Respostas originais e metadados (URL solicitada, URL final, status, horário UTC, SHA-256, bytes) estão em `data/historical_sources/`; arquivos `.txt` são extrações auxiliares sem scripts/styles. O HTTP 200 não é tratado automaticamente como conteúdo pertinente: algumas rotas de TibiaSecrets devolvem a homepage e `tibiawiki.com` redireciona para venda de domínio. Arquivos brutos devem permanecer locais; os metadados e este relatório bastam para publicação sem republicar páginas completas de terceiros. Não solicitamos nem redistribuímos arquivos proprietários de servidor Tibia.

## Evidências e força

| Proposição | Fonte efetivamente consultada | Resultado | Limite |
|---|---|---|---|
| Beholder foi renomeado Bonelord no 8.61 | [Bonelord](https://www.tibiawiki.com.br/wiki/Bonelord), revisão 441181 | Confirmado como afirmação da wiki | Fonte secundária, não anúncio oficial |
| Patch 8.61 lançado em 23/08/2010 | [Patches/8.61](https://www.tibiawiki.com.br/wiki/Patches/8.61), revisão 354750 | Texto explícito; lista rename | Anúncio oficial vinculado [id 1437](https://www.tibia.com/news/?subtopic=newsarchive&id=1437) retornou HTTP 403 |
| Matriz posterior é `1111/1361/1141/4611` | [469](https://www.tibiawiki.com.br/wiki/469), seção Mistério no Hellgate; s2ward README | Reprodução textual exata | Wiki observa caveiras ocultas atrás de pilares; contagem visual superficial pode ser errada |
| Matriz antiga fornecida é anterior ao rename | Fontes iniciais e busca histórica | **Não demonstrado** | Não foi localizado snapshot datado com contagem exata antiga |
| Mudança das matrizes coincide com rename | idem | **Em aberto** | Falta data da mudança; correlação não testável atualmente |
| 3478 é nome de criatura em evento de nostalgia | [3478](https://www.tibiawiki.com.br/wiki/3478) | Wiki data adição 9.44 em 13/01/2012 e informa nome corrigido para Bonelord em 2023 | Uso como identificador não estabelece equivalência léxica nem decoder |
| Knightmare diz `3478 67 90871 97664 3466 0 345!` | Wiki 469, seção NPC Knightmare | Sequência transcrita | Sem gloss; os tokens não são pares texto→tradução |
| Avar Tar recita poema numérico | Wiki 469, seção Avar Tar | Sequência transcrita, contém **4378**, não 3478 | Não corrigir silenciosamente para caber em hipótese |
| Fórmula Honeminas usa vetores `(4,3,1,5,3).(3,4,7,8,4)` | s2ward README, transcrição completa; arturo e kimlage | Concordância entre pesquisas sobre essa expressão | Página BR do livro foi obtida, mas fórmulas estão ausentes do HTML: não é confirmação primária independente |
| NPCs e livros compartilham mesmo algoritmo | Nenhuma fonte com gloss comum | **Não demonstrado** | Estilo de espaçamento e agrupamento difere; só teste externo pode decidir |

## Risco de propagação de afirmação não comprovada

`kimlage/analysis/lore_audit_20260618/source_report_pt.md`, §13, afirma que s2ward registra uma matriz antiga pré-2010 e alterada pós-rename. O README de s2ward consultado apenas diz que Cip alterou a quantidade de caveiras algum tempo após especulações dos jogadores. **Não fornece essa data nem liga explicitamente a mudança à renomeação.** Portanto não usamos a frase de kimlage como confirmação histórica independente.

As fontes iniciais discordam fortemente no plano semântico: arturo anuncia solução alemã, enquanto kimlage classifica o substrato como não linguístico. Nenhum desses veredictos substitui os controles independentes deste projeto. Em especial, a confirmação de números em arquivo de servidor, reportada em `arturo/docs/investigation/primary-source-7.7.md`, valida no máximo a transcrição se o arquivo for auditado; não autentica a tradução proposta.

## Honeminas: consequência matemática limitada

Se o ponto significa produto escalar ordinário, a expressão vale `4×3+3×4+1×7+5×8+3×4 = 83`. Isso é aritmética verificável, mas não demonstra que o mesmo operador codifica livros. `g` é explicado como gate, e `e` como energia mágica na transcrição; faltam definições suficientes para um sistema físico ou decoder único. O README de s2ward também menciona abreviações `43151 34783` que não coincidem com os vetores transcritos: tratar variantes como erros de extração candidatos, sem selecionar a que dê resultado mais atraente.

## Poema e falas: âncoras sem significado atribuído

Avar Tar na wiki:

> 29639 46781! 9063376290 3222011 677 80322429 67538 14805394, 6880326 677 63378129 337011 72683 149630 4378! 453 639 578300 986372 2953639!

A fala inglesa subsequente ("I know it's rather short, but still, this poem I like best") comenta o poema; **não é sua tradução**. Usá-la como plaintext seria fabricar um crib.

O relatório de arturo informa que o poema não existe no material de servidor 7.7 e que gritos `653768764` aparecem em Elder Beholder/Evil Eye. Isso é uma afirmação secundária auditável futuramente, não foi verificada contra servidor nesta rodada. Ausência de leitura sob uma chave comunitária não prova dois sistemas distintos, pois a chave pode estar errada.

## TibiaSecrets e arquivos

- [Bonelord Tome](https://tibiasecrets.com/bonelord_tome) foi consultado com sucesso. A página descreve a criação conceitual do item por fusão dos tomos e linguagem 469. Não oferece um algoritmo nem gloss validado.
- As rotas `/articles`, `/sitemap.xml` e `/?s=469` devolveram o mesmo hash da homepage; não contam como buscas completas no arquivo de artigos.
- O fórum oficial [thread 4141645](https://www.tibia.com/forum/?action=thread&threadid=4141645&pagenumber=1), apontado pela wiki, foi consultado: contém especulação comunitária datada de dezembro de 2013. Não autentica uma alteração da matriz em 2010.
- Wayback CDX retornou registros da página Hellgate em tibia.wikia.com de 2008, 2009, 2011 etc. O índice é preservado. As tentativas de obter snapshots de 2009 e 2011 retornaram HTTP 429; não foram interpretadas como ausência de evidência na época.
- Fandom retornou HTTP 402 para Bonelord, Hellgate, 469 e Honeminas. Isso limita a cobertura desta rodada.

## Próximos experimentos históricos priorizados

1. Obter screenshots ou mapa legalmente disponibilizado com versão/data e contagem exata de cada célula, anterior e posterior a 23/08/2010. Exigir também estado dos objetos móveis e caveiras ocultas; imagem isolada não fixa estado autoral.
2. Verificar anúncio oficial 1437 por snapshot arquivado e notas do patch: procurar menção explícita à formação Hellgate, além do rename já relatado na wiki.
3. Recuperar a expressão completa de Honeminas de fonte ingame com versão/data; congelar bytes antes de testar variantes matemáticas.
4. Recolher frases numéricas de NPCs acompanhadas de gloss oficial independente, caso exista. Identificadores como 3478 e 486486 devem ser registrados como nomes até surgir evidência de equivalência semântica.
