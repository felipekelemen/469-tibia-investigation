# Rodada 27 — recuperação de chaves e certificados de ambiguidade

Iniciada em 20/11 e consolidada em 21/11/2026, horário de São Paulo,
sobre `85aa411a24a834d83a5d0e5f73a78c031825a0be`.
Esta rodada avalia capacidade de recuperação em dados sintéticos. **Nenhuma
fala ou livro de 469 foi ajustado nesta rodada, e nenhum inglês sintético
apresentado aqui é tradução de Tibia.**

**Os 120 ajustes terminaram. Nenhum cenário atingiu a meta de 27 casos
aprovados em 30.** A rodada distingue recuperação parcial, ambiguidade
demonstrada e falta de resposta dentro do orçamento; não demonstra que 469
seja impossível de traduzir ou não contenha texto.

## Resultados

[Resultados completos](../results/round27_qualification.json), incluindo cada
consulta, testemunha, previsão, abstenção e gabarito sintético:

| Cenário | Casos aprovados | Formas reservadas certificadas | Chaves inteiras certificadas |
| --- | ---: | ---: | ---: |
| 30 grupos, unidades distintas no gerador | 17/30 | 261/300 | 7/30 |
| Sete grupos, mesmas chaves | 4/30 | 117/300 | 2/30 |
| Grupos contendo um dígito removidos | 0/30 | 104/300 | 0/30 |
| 30 grupos, dois dígitos com emissão igual | 13/30 | 268/300 | 5/30 |

Nenhuma previsão certificada estava errada. O cenário com dígito removido é
um controle deliberado de informação insuficiente: cada caso tem ao menos
uma mensagem reservada afetada. Houve abstenção nas 126 mensagens com algum
dígito ausente. Seu resultado 0/30 não deve ser interpretado como falha em
recuperar informação que estava disponível.

| Cenário | Duas chaves de treino comprovadas | Primeira chave não encontrada no orçamento |
| --- | ---: | ---: |
| 30 grupos | 22/30 | 1/30 |
| Sete grupos | 25/30 | 3/30 |
| Dígito removido | 26/30 | 2/30 |
| Dígitos homofônicos | 25/30 | 0/30 |

Uma chave inteira ambígua pode ainda dar uma leitura única para um alvo que
não usa suas partes ambíguas. Por isso os números de mensagens certificadas
e chaves inteiras não são intercambiáveis. As condições pareadas não são
amostras independentes; não usamos a soma das 1.200 previsões como tal.

Nas mensagens com nomes excluídos do léxico de treino, foram certificadas
48/54 instâncias, envolvendo 17 nomes distintos. Isso demonstra transferência
fora desse léxico nos controles, sem constituir leitura de nomes de Tibia.

O novo método certificou 20 formas a mais que o comparador no cenário curto
(117 contra 97), em quatro casos. O total de casos aprovados permaneceu em
4/30. Consumiu 184.038 estados contra 45.163, cerca de 4,07 vezes mais.
Assim, não demonstramos ganho de qualificação nem vantagem sob custo igual.

### Fronteiras e grafias

Dos 150 pares concatenados, apenas 30 tiveram divisão lexical única com a
**chave verdadeira fornecida**; os outros 120 admitiram mais de uma divisão.
Com chave inteira aprendida e certificada, somente quatro mensagens tiveram
divisão única correta. Nenhum dos 30 casos acertou os cinco pares de forma
única, tanto na condição de chave fornecida quanto na aprendida. Não há
qualificação para recuperar palavras a partir de treino sem fronteiras.

Os 30 controles fonéticos recuperaram os fonemas com chave fornecida e
preservaram grafias alternativas. Os 30 controles de vocabulário oculto
confirmaram a construção de dois dicionários que explicam os mesmos bytes.
São diagnósticos específicos de ambiguidade, não 60 traduções nem 30 provas
independentes de que um corpus real carece de significado.

### Auditoria de reaproveitamento de trechos

As formas inteiras de treino e teste são distintas, mas isso não assegura
novidade de todos os fragmentos numéricos. A
[auditoria posterior ao ajuste](../results/round27_overlap_audit.json) não
altera a meta nem escolhe novos casos:

| Cenário | Reservados que reaparecem dentro de um grupo de treino | Certificados entre os que não reaparecem |
| --- | ---: | ---: |
| 30 grupos | 62/300 | 203/238 |
| Sete grupos | 39/300 | 102/261 |
| Dígito removido | 34/300 | 79/266 |
| Dígitos homofônicos | 65/300 | 208/235 |

O solver não recebe plaintexts de treino, mas o cenário já fornece o léxico
que inclui as formas de teste. Portanto, nem o resultado integral nem esse
subconjunto substituem validação em prosa de autores independentes, vocabulário
aberto ou fragmentos inéditos do jogo.

## Pergunta e método

A rodada 23 preservou a partição verdadeira em testes locais, mas suas 40
buscas conjuntas atingiram o orçamento. Enumerar muitas alternativas sem
esgotá-las não estabelece consenso. O novo método procura uma chave compatível
e depois uma segunda chave que contradiga a primeira:

- **SAT:** existe uma chave testemunha, publicada e conferida contra o treino.
- **UNSAT:** busca completa, sem contraprova; permite certificar unicidade
  apenas no modelo e no conjunto de dígitos especificados pela consulta.
- **UNKNOWN:** orçamento esgotado; não autoriza escolher uma leitura.

O modelo continua estrito: cada dígito emite uma unidade fixa de uma a três
letras; cada grupo de treino corresponde a uma forma do léxico. Unidades
vazias, estado dependente do contexto, pontuação, ordem de palavras e sintaxe
não entram. Dois dígitos podem emitir a mesma unidade, inclusive na análise
dos controles gerados com unidades distintas. Não fornecemos ao solver os
comprimentos nem as unidades verdadeiras.

A transferência admite strings fora do léxico. Para cada mensagem reservada,
certificamos separadamente a string concatenada e as unidades que a compõem.
Unicidade da string não implica unicidade das unidades ou das palavras.
Dígitos nunca observados permanecem desconhecidos. As soluções verdadeiras
só entram no gerador e na avaliação, nunca nas restrições de descoberta.

## Dados, congelamento e orçamento

[Protocolo](../data/round27_protocol.json), [fixtures](../data/round27_fixtures.json)
e [manifesto](../data/round27_experiment_manifest.json) foram fixados antes dos
ajustes. Reutilizamos a normalização e o CMU versionado da rodada 23. Trinta
nomes pré-declarados são removidos das restrições lexicais do treino; outros
nomes, sobrenomes e abreviações do CMU permanecem. Portanto, satisfazer o léxico
não é produzir prosa coerente.

Foram geradas 30 chaves com dez unidades distintas e outras 30 com dois
dígitos emitindo a mesma unidade. A aceitação exige pelo menos 60 formas
codificáveis, um nome reservado e cobertura dos dez dígitos nos sete grupos
escolhidos por uma regra gulosa de cobertura. Os sete são estendidos a 30;
dez formas diferentes são reservadas. Nenhum caso foi escolhido pelo sucesso
do solver. A geração precisou de 144 e 220 tentativas, respectivamente,
dentro do limite prévio de 20.000 por família.

As mesmas 30 primeiras chaves originam os cenários de 30 grupos, sete grupos
e remoção de todos os grupos contendo um dígito escolhido. São condições
pareadas, não 90 chaves independentes. As 30 chaves homofônicas são adicionais.
Os nomes compartilham esses ajustes, sem nova chave ou treino.

Cada consulta admite 2.000 estados e 20.000 atribuições locais por estado;
o conjunto de consultas de um ajuste e suas transferências admite 20.000
estados. Não houve aumento de orçamento após observar os resultados. A meta
é 27 de 30 casos com pelo menos 95% das formas reservadas recuperadas com
certificado, F1 médio dos spans de unidades de pelo menos 0,95 e nenhuma
afirmação certificada errada. Há dez formas por caso: 95% de recuperação
exige dez acertos. Abstenções recebem zero, inclusive no F1 certificado.

São listas condicionadas a um dicionário, não textos de novos autores.
Este teste não satisfaz sozinho a qualificação de prosa ou vocabulário aberto
prevista no plano. Não herdamos para fronteiras ocultas a eventual capacidade
de um modelo que recebe os grupos de treino separados.

## Fronteiras e identificabilidade

Para cada uma das 30 chaves base, concatenamos os dez grupos reservados em
cinco pares. Contamos todos os caminhos no grafo lexical, permitindo fronteiras
de palavras somente entre unidades emitidas por dígitos. Essa restrição é do
gerador, que codifica cada palavra separadamente. Há duas avaliações distintas:
chave verdadeira fornecida e chave aprendida integralmente certificada.
Não se trata de aprendizado conjunto com treino sem espaços.

Trinta controles de pronúncia fornecem a chave verdadeira e preservam todas
as grafias CMU compatíveis com os mesmos fonemas. Eles verificam a necessidade
de abstenção ortográfica; não qualificam descoberta de chaves fonéticas.

Trinta permutações novas dos dígitos verificam o seguinte contraexemplo de
vocabulário oculto, derivado da construção da rodada 17:

```text
A = {1234, 5678, 9012}
B = {12345, 678, 9012}
treino = (123456789012) repetido três vezes
mensagem discriminante = 12349012
```

Ambos os dicionários são livres de prefixos, têm três unidades, soma dos
comprimentos 12 e cada unidade aparece três vezes. Reconstruem exatamente
os mesmos bytes de treino, com fronteiras diferentes. A mensagem discriminante
é aceita somente por A. Isso demonstra não identificabilidade **desses dados
nesse modelo**, sem provar que os livros de Tibia não contenham mensagens.
Não é uma nova qualificação dos segmentadores reprovados na rodada 17.

## Comparação com o método anterior

O [suplemento](../data/round27_baseline_protocol.json) foi congelado após os
primeiros resultados do método novo estarem visíveis, antes de executar o
comparador. É uma comparação exploratória explicitamente posterior ao início
do teste principal, sem mudar sua meta ou selecionar casos pelo resultado.

O enumerador da rodada 23 permanece sem alterações. Usamos os mesmos 30
casos base, sete grupos de treino e dez grupos reservados, com limite de
2.000 estados, 2.000 soluções e 20.000 atribuições locais. A presença da chave
verdadeira na lista é apenas diagnóstico; ela não pode ser escolhida usando
o gabarito. Só uma enumeração completa pode certificar consenso. O novo método
pode gastar até 20.000 estados em várias consultas, de modo que a comparação
não demonstra superioridade sob orçamento total idêntico.

Na comparação, o método anterior concluiu a enumeração em 11/30 casos;
os outros 19 atingiram 2.000 estados. A chave verdadeira estava entre as
alternativas visitadas em 14/30, mas isso não é uma previsão. Ele certificou
97/300 formas reservadas, sem erro certificado; quatro casos recuperaram
todas as dez formas e suas unidades. Consumiu 45.163 estados no conjunto.

## Execução e equivalência

A execução foi dividida por índices em dois intervalos disjuntos, mantendo
todos os 120 ajustes. Depois de resultados parciais, introduzimos somente
um cache dos domínios lexicais por chave parcial. Um domínio filtrado depende
da interseção das restrições da chave com o domínio inicial, não da consulta
que o alcançou. Reutilizar essa interseção não altera a árvore de busca,
a ordem, as exclusões nem a contagem de estados. Não armazenamos respostas
de consultas para inferir respostas de outras.

O código original congelado permanece intacto. O
[suplemento de execução](../data/round27_execution_protocol.json) registra
a mudança posterior e o [manifesto adicional](../data/round27_execution_manifest.json)
fixa seu código antes da continuação. Comparamos 1.056 consultas pequenas,
variando exclusões e limites de estados/atribuições locais, além da transferência
em um ajuste completo. Também repetimos os ajustes base00/30grupos,
base18/7grupos e base01/7grupos: todos os resultados, testemunhas e contagens
foram idênticos, incluindo os casos de 10.687 e 20.000 estados.
[Registro](../results/round27_cache_equivalence.txt).

Foram preservados 24 ajustes completos anteriores à otimização; trabalho
inacabado foi refeito sob os mesmos limites, sem ser classificado como falha.
Os tempos do registro não são um benchmark comparável de desempenho: a carga
de processos concorrentes era diferente. Essa mudança não amplia a capacidade
estatística atribuída ao método.

## Limites lógicos da interpretação

Um certificado é condicional ao modelo, ao léxico e às fronteiras declaradas.
Mesmo uma leitura única nesse espaço não prova o plaintext original de um
jogo que talvez use outro mecanismo. Zero erros certificados em controles
gerados pelo próprio modelo não mede a taxa de falsas traduções fora dele.

Se um dígito não aparece no treino, trocar apenas sua emissão de `A` para `B`
preserva todas as restrições de treino. No modelo sem restrição de injetividade,
há 26 + 26² + 26³ = 18.278 strings possíveis de uma a três letras para ele.
Nenhuma busca mais longa resolve essa ausência de informação. Isso explica a
abstenção necessária nos alvos que usam o dígito retirado; não explica, por si,
as falhas nos dígitos observados nem qualquer propriedade da 469.

A cobertura dos dez dígitos no treino não garante unicidade da chave.
Os 30 casos base misturam instâncias identificáveis e ambíguas; não foram
filtrados pelo sucesso do solver. Portanto, a taxa de aprovação não estima
isoladamente a recuperação em 30 instâncias previamente provadas identificáveis.
Não obtivemos essa qualificação mais forte nesta rodada.

Um exemplo **exclusivamente sintético** é `base_00`: para o reservado `36`,
as testemunhas permitem `BAN` e `DAN`, enquanto o gabarito é `FAN`. Cada chave
testemunha satisfaz todos os 30 grupos de treino no léxico. Escolher a palavra
mais conveniente não seria decifração. A mesma rodada contém casos de chave
única recuperada; não confundimos esses dois resultados.

## Candidatas, decisão e próximo passo

**Candidatas de tradução de 469 nesta rodada: nenhuma.** Nenhum novo algoritmo
recebe qualificação para as falas de Avar Tar, Knightmare ou Chayenne. Os
resultados também não autenticam um gerador original sem texto. A missão
permanece inconclusiva.

As decisões anteriores sobre 3478/nomes e matrizes permanecem: nome contextual
documentado, sem equivalência criptográfica demonstrada; expansão das matrizes
suspensa até novos dados ou mecanismo com previsão independente. Esta rodada
não reabre essas buscas nem produz nova evidência histórica.

A próxima etapa é R28, com as três falas prioritárias: usar somente métodos
qualificados no seu escopo e testes exatos de hipóteses finitas explicitadas.
Uma incompatibilidade completa pode excluir aquele modelo; uma busca limitada
não pode excluir a família geral. Nenhuma palavra será completada pela lore
ou escolhida apenas por plausibilidade. Restam as rodadas 28–30 do plano
revisado; sua conclusão não garante a descoberta de uma tradução.

## Verificação e reprodução

Passaram **265 testes automatizados**, e `make round27` passou.
O [registro de verificação](../results/round27_verification.json) distingue
a execução original dos 120 ajustes de uma segunda execução integral:
esta última não foi realizada na consolidação. Testes de software não são
casos de tradução nem substituem a meta de recuperação.

Foram executados os 120 ajustes principais, os 30 ajustes do comparador,
os 60 diagnósticos de ambiguidade e as verificações de equivalência descritas.
O resultado não depende de rede. O corpus CMU e sua licença constam dos
insumos versionados da [rodada 23](round23.md).

```bash
make test
make round27
make round27-full
```

`make round27` confere hashes, agregações, todas as testemunhas SAT, os 60
diagnósticos e repete o primeiro ajuste com a implementação original.
`make round27-full` repete os 120 ajustes com o cache equivalente, em diretório
temporário, e compara o resultado integral. A referência sem cache permanece
disponível por `python3 scripts/run_round27.py --full`.

O comparador é `scripts/round27_baseline.py`; para repeti-lo, use uma cópia
temporária sem `results/round27_baseline.json`, preservando o resultado original
para comparação. O programa recusa sobrescrevê-lo. A auditoria descritiva pode
ser refeita com `python3 scripts/round27_result_audit.py`.
