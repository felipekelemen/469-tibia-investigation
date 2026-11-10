# Auditoria do Deep Research recebido

O relatório integral enviado pelo usuário foi lido. Seu SHA-256 e limites de
proveniência estão em `data/research_report_manifest.json`; a cópia integral é
mantida localmente, fora do Git público. O texto contém marcadores internos de
citação, mas não a bibliografia resolvida. Não conseguimos abrir esses IDs como
URLs: fontes decisivas foram procuradas novamente e as demais alegações
permanecem explicitamente atribuídas ao relatório, não confirmadas.

A auditoria usa os resultados científicos de H01–H17. **O relatório não trouxe
plaintext atestado nem algoritmo novo validado.** Ele organiza pistas úteis,
mas não elimina os limites de identificação e vazamento que já medimos.

## Correções que alteram a prioridade

| Proposta/alegação | O que verificamos | Decisão |
|---|---|---|
| Extrair caveiras de tibiamaps histórico | Snapshot8885f3f3 contém minimapas7.3–7.7; não objetos, pilhas ou8.6–8.7 | Não baixar o repositório inteiro nem desenvolver parser de objetos para essesPNGs |
| Chayenne comoholdoutposterior independente | Partes36/13dígitos presentes11/9vezes nos livros | Usar como atestação de conteúdo, nunca como teste de generalização desses livros |
| Todos os textos deNPC/desenvolvedor são wordcodes separados | Chayenne reutiliza strings dos livros | Modelos por fonte/modalidade; testar transferência em vez de impor dois sistemas |
| Notícias oficiais datam edição deHellgate/matriz | Renameid1437 e updateid1557 achados por textoindexado; corpo consultadoid1557 não citaHellgate | Data da matriz permanece em aberto;107dias separam eventos gerais |
| Hexadecimal comprova domínio sequestrado | Hex→`by herrera` confirmado; autoria/incidente exigem outra evidência | Excluir de cribs canônicos enquanto não autenticado, sem afirmar incidente comprovado |
| Camada5729 é chave linguística já estabelecida | Reconstrução é condicional à tabela e segmentação importadas | Comparar raw,row0 e row0+resíduo; não fixar letras como verdade |
| Três partições independentes de módulos estão disponíveis | Grafo exato em8/12dígitos conecta os70livros | Medir viabilidade; não prometer independência nem relaxar limiar olhando o resultado |
| FracassoHill torna PRNG/semântica da matriz provável | Não há implicação probabilística sem modelo e evidência adicionais | Exigir mecanismo finito e previsões antes de expandir famílias |

As [auditorias de mapas](research_map_audit.md) e
[amostras deNPC/desenvolvedores](research_npc_audit.md) apresentam URLs,
versões, acesso e limites. A checagem literal foi também implementada em
`scripts/audit_external_samples.py`, com saída `results/external_samples_screen.json`.

## O que a pesquisa reforça

- Qualificar a busca homofônica em positivos antes de transformar um resultado negativo em exclusão de família. Nosso positivo só recuperou42,6%das letras.
- Separar evidência histórica, código visível no jogo e interpretação comunitária.3478 é pista de entidade, nãoIDinterno ou gloss provado.
- Reproduzir a seleção inteira dentro dos nulos e controlar sobreposição. O corpus não oferece70observações independentes.
- Testar modelos de cópia e recombinação como competidores, incluindo positivos reais com repetição para não confundir montagem de prosa com ausência de mensagem.
- Testar a matriz como mecanismo específico, não como fonte ilimitada de sementes e convenções escolhidas depois de olhar o inglês.

## Cobertura e novidade

H01–H04,H08–H12,H14–H17 já cobrem grande parte das recomendações numéricas.
Não se deve repetir reprodução de5729,Hill26/29,Vigenere com nomes ou ASCII por
orientação apenas porque reaparecem no relatório. São abertos: busca
homofônica com potência demonstrada; predição de variantes fora de famílias;
codebook/modalidades com fontes e segmentação auditadas; competição gerativa
sem pressupor semântica; e hipóteses matriciais com mecanismo não arbitrário.

A matriz completa de21alegações, estados e links de evidência está em
`data/research_claims.jsonl`. As alegações não auditadas por completo, incluindo
exaustividade de busca em vídeos e incidente histórico de domínio, não ganham
status de fatos nesta incorporação.

O [plano revisado](next_experiments.md) substitui o plano provisório anterior.
Esta entrega executa auditoria de fontes e checagem de sobreposição, não uma
terceira rodada de decifração. Traduções verificadas permanecem**zero**.
