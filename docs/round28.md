# Rodada 28 — inteiros em bases alfabéticas nas três falas prioritárias

Iniciada em 21/11/2026, horário de São Paulo, sobre
`5ab9a832b0614f4c2ec48dde57924d3ca7331a8e`.
Consolidação concluída em 22/11/2026, no mesmo fuso.

**Nenhuma candidata nova de tradução foi encontrada.** As 1.872 combinações
de codec, enquadramento e alfabeto examinadas não explicam uma fonte inteira
de Avar Tar, Knightmare ou Chayenne no léxico declarado. As buscas são
completas nessa família finita; não atingiram limites de estados. Isso não
rejeita outras cifras, palavras ausentes do léxico ou significado não textual.

O buscador recuperou a chave e todas as letras reservadas em 532/540 controles
sintéticos. Esse resultado verifica capacidade dentro da família fornecida;
não torna o detector lexical um tradutor geral de 469.

## Hipótese nova e regras

As rodadas 20–23 trataram dígitos como códigos de letras ou unidades locais.
Aqui, um quadro decimal inteiro representa **um número**, expandido em uma
base alfabética. Assim, repetir um dígito decimal não exige repetir uma letra.
A família é distinta das anteriores e evita pressupor que `3222011` represente
unidades repetidas `XYYYZWW`.

| Codec | Representação | Tratamento do inteiro zero |
| --- | --- | --- |
| Base 26 bijetiva | A=1…Z=26, como numeração alfabética de colunas | Inválido |
| Base 26 canônica | Dígitos 0…25 em representação posicional mínima | Um símbolo 0 |
| Base 27 com espaço | 0 é espaço; 1…26 são letras | Um espaço literal |

Depois dessa expansão, cada símbolo de letra recebe a mesma transformação:

```text
letra = (a × símbolo + b) mod 26
gcd(a,26) = 1; 0 ≤ a,b < 26
```

São 312 alfabetos afins bijetivos. Não incluem todas as 26! permutações do
alfabeto, multiplicação do inteiro, transposições ou chaves contextuais.

Dois enquadramentos foram fixados:

- **Por grupo numérico:** cada grupo é um inteiro independente; suas bordas
  são fronteiras lexicais. Nas bases 26, pode haver palavras internas sem espaços.
- **Por fonte inteira:** os grupos são concatenados e lidos como um único
  inteiro; sua separação original é tratada como formatação.

Isso dá 3 codecs × 2 enquadramentos × 312 chaves = **1.872 combinações por
entrada**. A pontuação e o texto original permanecem no artefato de fontes;
não reivindicamos que indiquem pontuação do plaintext. Zeros decimais iniciais
são padding numérico declarado, sem apagar outros dígitos. Na base 27, os
espaços decodificados são preservados, incluindo o grupo `0`; uma fonte
formada apenas por espaços não é aceita como texto.

O léxico mantém as 122.368 formas da base ortográfica da rodada 23: CMU
normalizado e a adição hipotética, já declarada, de BONELORD. Inclui nomes e
abreviações. Não acrescentamos palavras da lore após examinar as saídas.
Nas bases 26, um grafo exato conta todas as divisões em palavras; na base 27,
somente os espaços efetivamente decodificados estabelecem essas divisões.

[Protocolo](../data/round28_protocol.json) e
[manifesto de insumos](../data/round28_experiment_manifest.json) foram fixados
antes dos ajustes. Começamos por Knightmare porque seus sete grupos e o zero
isolado discriminam as regras aritméticas, independentemente de uma leitura desejada.

## Controles com inglês conhecido

Usamos *The Scarlet Letter*, de Nathaniel Hawthorne, e *Little Women*, de
Louisa May Alcott, autores novos nos controles do projeto. O Gutenberg
principal retornou HTTP 503; os espelhos públicos GITenberg foram fixados por
commit e SHA256. Os textos completos e seus avisos foram preservados em
[round28_reference](../data/round28_reference/SOURCES.json).

Selecionamos 90 janelas sem sobreposição de posições, 15 por autor em cada
perfil. A seleção considera apenas comprimento e presença das palavras de
treino no léxico; as palavras reservadas não são filtradas pelo léxico.
Os perfis aproximam os comprimentos dos alvos, sem reproduzir exatamente
todas as extensões decimais: sete palavras curtas para Knightmare, dez para
Avar e duas partes de cinco e duas palavras para Chayenne.

As mesmas janelas foram emparelhadas entre seis configurações, produzindo
540 ajustes com chaves escondidas. São **90 trechos, não 540 fontes independentes**.
Na base 26 canônica, condicionamos a escolha da chave para evitar um símbolo
zero inicial que perderia informação. A qualificação desse codec vale nesse
domínio; não resolve a recuperação de letras iniciais omitidas.

Cada ajuste enumera todas as 312 chaves, preservando as compatíveis com o
treino. Uma letra reservada só recebe certificado se todas elas concordarem.
A meta é ao menos 27/30 casos com 95% de letras certificadas corretamente e
nenhuma letra certificada errada, em cada célula separadamente.

| Codec / enquadramento | Perfil Knightmare | Perfil Avar | Perfil Chayenne |
| --- | ---: | ---: | ---: |
| Bijetiva 26 / grupos | 30/30 | 30/30 | 30/30 |
| Bijetiva 26 / fonte inteira | 29/30 | 30/30 | 27/30 |
| Canônica 26 / grupos | 30/30 | 30/30 | 30/30 |
| Canônica 26 / fonte inteira | 29/30 | 30/30 | 27/30 |
| Base 27 / grupos | 30/30 | 30/30 | 30/30 |
| Base 27 / fonte inteira | 30/30 | 30/30 | 30/30 |

As 18 células passaram o critério de **letras com codec/enquadramento conhecidos**.
A chave verdadeira permaneceu entre as soluções em 540/540 ajustes; em 532
ela foi única e recuperou a string reservada inteira. Os outros oito são
ambiguidades preservadas, sem letras certificadas erradas.

A recuperação de palavras é outra medida: apenas **216/540** sequências de
palavras foram determinadas de forma única e correta. A base 27, que transmite
espaços, acertou as 180; as duas bases 26 acertaram 36/360. Nenhuma célula de
base 26 qualifica recuperação automática de fronteiras. Também não houve
qualificação de seleção entre famílias desconhecidas ou de reconhecimento geral
de inglês. [Resultados por caso](../results/round28_qualification.json).

A auditoria confirmou as posições diretamente nos textos fixados. Nenhuma
sequência reservada reaparece inteira no treino do próprio caso. Um par curto
de palavras do perfil Chayenne aparece no treino de outro caso, com chave
independente. O [resumo auditável](../results/round28_summary.json) registra
essa repetição; não alegamos ausência de frases comuns entre autores ou casos.

## Resultados nas falas

As transcrições são as versões já conferidas nas rodadas anteriores, fixadas
por hash. Não obtivemos um novo par oficial número/inglês nesta rodada.

| Fonte | Compatíveis por grupos, três codecs | Compatíveis por fonte inteira, três codecs |
| --- | ---: | ---: |
| Knightmare, sete grupos | 0 | 0 |
| Avar Tar, vinte grupos | 0 | 0 |
| Chayenne, 36+13 dígitos | 0 | 0 |

Também terminaram sem chave os ajustes de descoberta dos primeiros dez grupos
de Avar e dos primeiros 36 dígitos de Chayenne, nos três codecs por grupos.
Portanto, não houve chave para prever suas partes reservadas. Isso é ausência
de candidato ajustado, não uma tradução prevista e posteriormente refutada.

No enquadramento por fonte inteira, não cortamos o inteiro decimal em prefixo
e sufixo para simular uma reserva: converter um número de base não preserva
tais cortes. Esse enquadramento usa a fonte inteira como diagnóstico e só
poderia prever outras fontes. Nenhuma chave sobreviveu nem individualmente;
as hipóteses de chave compartilhada e de chaves separadas não obtiveram ajuste.

O código contabiliza 12 bits para o campo de configuração/chave compartilhado
ou 36 para três configurações separadas. É apenas contagem de parâmetros;
exclui programa, léxico e dados, e **não** é uma comparação MDL de autoria.

As 18 buscas completas e seis buscas de prefixo totalizam **7.488 casos de
chave**. Cada chave rejeitada tem sua primeira contradição registrada em
[round28_targets.json](../results/round28_targets.json). Uma segunda implementação
usa intervalos de comprimento e somas de potências, em vez das divisões do
decodificador, além de programação dinâmica inversa em vez do trie lexical.
Ela confirmou os 7.488 casos, inclusive todas as rejeições:
[certificados](../results/round28_certificates.json). É verificação interna
independente de implementação, não revisão por terceiros.

## Controles e seleção de modelo

Executamos 99 réplicas conjuntas de cada um dos quatro controles, sempre
repetindo as 1.872 combinações em cada uma das três fontes. Todos preservam
comprimentos dos grupos; os demais invariantes variam conforme o gerador.
Todos os 99 resultados por fonte foram distintos e alteraram os dados originais.

| Controle | Propriedades adicionais | Réplicas com algum ajuste lexical completo |
| --- | --- | ---: |
| Dígitos uniformes | Apenas layout/comprimentos | 33/99 |
| Embaralhamento global | Histograma total de dígitos | 27/99 |
| Embaralhamento de cada grupo distinto | Histogramas por grupo e grupos repetidos | 24/99 |
| Trechos dos livros | Substrings reais de mesmo comprimento; repetições reutilizam a mesma amostra | 22/99 |

No último controle, sorteamos um livro elegível entre os 70 e depois uma posição.
Esses livros estão expostos e relacionados por cópias; não são reservas semânticas.

A estatística fixada maximiza, entre todas as configurações, quantas das três
fontes são completamente segmentáveis no léxico com a mesma configuração.
O valor real foi zero; os controles tiveram zero ou um, nunca dois ou três.
A cauda superior com correção +1 foi **1,0 em todos os quatro controles**.
Isso não é probabilidade de significado, inglês ou ausência de significado.

Os 106 encaixes lexicais entre 396 réplicas demonstram oportunidades de encaixe
sob esses geradores. Não os chamamos de traduções nem promovemos uma pontuação
lexical a validação semântica. A seleção completa está nos
[resultados dos controles](../results/round28_nulls.json).

## Cópias, nomes e decisão

Reconfirmamos 11 ocorrências da primeira parte de Chayenne e nove da segunda
nos livros. Essas cópias não fornecem plaintexts independentes. Como não houve
configuração sobrevivente de fonte inteira, nenhuma foi encaminhada para
decodificação dos 70 livros como teste de transferência.

Nesta família, `3478` produz no máximo três símbolos antes do alfabeto afim;
BEHOLDER e BONELORD têm oito letras. Logo, nenhuma dessas configurações pode
traduzir literalmente esse quadro isolado em um dos nomes. A conclusão vale
para essa conversão e não rejeita um identificador, código de palavra ou
referência contextual à criatura. As decisões históricas das rodadas 25–26
e a suspensão da expansão de matrizes permanecem.

**Catálogo de novas candidatas semânticas: vazio.** As propostas comunitárias
auditadas na rodada 24 não foram tomadas como gabarito e não receberam validação
nova. Não corrigimos saídas, inserimos palavras da lore nem escolhemos anagramas.

Encerramos a família finita nos enquadramentos e no léxico declarados. Não
excluímos vocabulário fora do CMU, outras bases, alfabetos arbitrários ou outros
mecanismos. A missão segue **inconclusiva**. Restam R29, comparação com geradores
textuais/não textuais/mistos, e R30, adjudicação e replicação. Uma explicação
sem texto ainda exigirá procedência do processo original para ser confirmada.

## Reprodução

```bash
make test
make round28
make round28-full
```

O replay curto confere hashes, repete todos os ajustes reais e a auditoria
independente, verifica o primeiro controle positivo e os invariantes/agregações
de todas as réplicas. O completo repete também os 540 positivos e os 396
conjuntos de controles. As fontes necessárias estão versionadas; não é preciso
acessar a rede. `round28_summary.py` refaz a agregação e a auditoria de cópias
entre os trechos sintéticos, sem alterar critérios ou ajustar chaves.

Passaram **279 testes automatizados** e `make round28`. Os 540 ajustes positivos
e os 396 conjuntos de controles foram executados para produzir os resultados;
não repetimos essa bateria inteira durante a consolidação. O replay curto
reexecutou todos os casos reais e seus certificados independentes. Detalhes em
[round28_verification.json](../results/round28_verification.json).

As decisões estão em [round28_decisions.json](../data/round28_decisions.json),
com H110–H112 no registro de hipóteses. O
[progresso atualizado](../data/plan_progress_round28.json) mantém duas etapas
planejadas: R29 e R30, sem promessa de solução nessas duas etapas.
