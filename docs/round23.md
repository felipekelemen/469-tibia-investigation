# Rodada 23 — dígrafos, blocos de letras/fonemas e sílabas

**Ainda não há tradução verificável.** Esta rodada testa quatro regras fixas
com um vocabulário externo mais amplo. Os resultados negativos têm alcance
lexical e algorítmico delimitado; as buscas limitadas permanecem inconclusivas.
Uma sequência composta de palavras do dicionário não é automaticamente inglês
coerente, muito menos uma tradução de Tibia.

## Fonte e regras congeladas

Usamos o CMU Pronouncing Dictionary no commit
`74790861f652b15e4ac49015a90074ad62a27690`. Os arquivos originais, licença,
URLs e hashes estão em `data/cmudict_reference/`. Não há rede durante o replay.
Após a normalização documentada, a fonte contém **122.367 grafias e 131.132
pronúncias distintas por grafia**, com 39 fonemas sem marcação de tonicidade.
Há nomes próprios, abreviações e homófonos; esta é uma fonte permissiva.

Cada dígito deve emitir a mesma unidade em toda a mensagem. Dígitos diferentes
podem emitir a mesma unidade. Não admitimos unidades vazias, correções do texto,
exceções por palavra ou mudança contextual de chave.

| Modelo | Unidade emitida por um dígito | Formas distintas no banco |
| --- | --- | ---: |
| Dígrafo | Exatamente duas letras | 122.368 |
| Bloco de letras | Uma a três letras | 122.368 |
| Bloco de fonemas | Um a três fonemas CMU | 114.787 |
| Sílaba operacional | Uma sílaba da pronúncia segmentada | 114.782 |

BONELORD é a única adição ortográfica, explicitamente hipotética. BEHOLDER está
na fonte. Não inventamos pronúncia para BONELORD: suas duas avaliações fonéticas
são **indisponíveis**, não rejeições. Pontuação de grafias é retirada e variantes
de pronúncia são mantidas. Palavras de uma letra ficam restritas a A/I.

A silabificação escolhe, entre duas vogais, o maior sufixo consonantal que aparece
como início de alguma pronúncia do banco. As consoantes restantes fecham a sílaba
anterior. Isso produz 16.742 tipos de sílaba; é uma regra operacional reproduzível,
não uma afirmação de que a silabificação inglesa tenha sido resolvida.

Os espaços numéricos de Avar Tar/Knightmare são tratados provisoriamente como
fronteiras de palavras inglesas. Chayenne entra somente na transferência de
chaves, sem fornecer espaços internos. Não testamos nesta rodada chaves aprendidas
diretamente dos fragmentos sem espaços, transposições ou unidades de vários dígitos.

## Busca e limites

O solver enumera todas as divisões de cada forma em unidades, exigindo igualdade
sempre que um dígito se repete. Expressões regulares apenas filtram formas
possíveis; sua primeira captura nunca é escolhida como segmentação verdadeira.
A busca conjunta mantém atribuições distintas e verifica a chave contra todos
os grupos fornecidos. Um dígito ausente do ajuste continua desconhecido.

O protocolo fixou 2.000 estados, 2.000 soluções e 20.000 atribuições locais como
limites. Ultrapassar qualquer um deles torna a busca **incompleta**. Encontrar
zero chaves dentro do orçamento não autoriza rejeição; encontrar várias não
autoriza consenso sobre possibilidades ainda não visitadas.

`data/round23_input_manifest.json` fixa fonte, normalização, protocolo, fixtures,
solver e execução antes dos ajustes conjuntos. Testes pequenos anteriores
compararam o algoritmo com enumeração exaustiva. Uma auditoria posterior,
`scripts/round23_certificate_audit.py`, usa vetores explícitos de comprimentos
e junções de atribuições, sem importar o solver, para conferir certificados
negativos. Essa auditoria não é uma nova validação semântica.

## Controles sintéticos e alcance

As 120 fixtures locais — 30 por família — verificam a recuperação de partições
quando a forma inglesa é fornecida. Todas mantiveram a atribuição verdadeira.
Esse resultado testa o enumerador, não a descoberta de tradução desconhecida.

As 40 fixtures conjuntas — dez por família — escondem a chave e usam o banco
inteiro. Cada chave geradora tem dez unidades distintas; a família pesquisada
permite também homofonia. Selecionamos unidades frequentes antes dos ajustes,
exigindo pelo menos vinte formas codificáveis e uso dos dez dígitos no conjunto
disponível. Sete formas servem ao ajuste e outras sete à transferência.
O ajuste não necessariamente observa todos os dez dígitos.

**Todas as 40 buscas atingiram o limite de estados; nenhuma chave verdadeira
entrou na porção enumerada.** Foram retornadas 65.673 chaves alternativas
compatíveis, em 39 fixtures. Esses números revelam a ambiguidade e a limitação
do orçamento; não demonstram que as chaves verdadeiras sejam irrecuperáveis.
Não há qualificação de
recuperação de chaves nem previsões únicas certificadas das 280 formas reservadas.
As amostras são listas de palavras condicionadas pelo vocabulário, não prosa
gramatical nem autores independentes. Os negativos exatos do jogo abaixo são
diagnósticos de compatibilidade, não aplicação de um tradutor qualificado.

## Resultados no jogo

| Modelo | Avar: primeiros 10 grupos | Avar: 20 grupos | Knightmare: 7 grupos |
| --- | --- | --- | --- |
| Dígrafo | Completo, zero chaves | Completo, zero chaves | Completo, zero chaves |
| 1–3 letras | Completo, zero chaves | Completo, zero chaves | Incompleto, 1.769 chaves encontradas |
| 1–3 fonemas | Completo, zero chaves | Completo, zero chaves | Completo, zero chaves |
| Sílaba | Completo, zero chaves | Completo, zero chaves | Completo, zero chaves |

São 12 ajustes principais: **11 completos sem chave e um limitado**. O ajuste
integral de Avar sobrepõe o prefixo: não são amostras independentes. Como não
há chave no prefixo, os dez grupos restantes não geram uma validação de tradução.

Um certificado simples de Avar é `3222011`. Qualquer chave desta família o
transforma em `X Y Y Y Z W W`, sem espaços entre as unidades. Nenhuma forma do
banco satisfaz esse padrão nas quatro regras. A auditoria independente percorreu
explicitamente os 81 vetores de comprimento nas regras variáveis e o vetor
único nas duas fixas. Também conferiu certificados de `337011` e as junções
completas de Knightmare nas regras de dígrafo e sílaba. A busca de fonemas de
Knightmare terminou após 1.611 estados; essa busca conjunta variável não foi
reimplementada pela auditoria de junções fixas.

As 1.769 chaves parciais de Knightmare produzem palavras do banco, mas não
traduções demonstradas. Por exemplo, uma saída literal é
`ADRA ER GAARDER GREED ADEE A ADA`: nomes próprios e uma palavra reconhecível
não bastam para formar uma mensagem. O conjunto enumerado só associa o primeiro
grupo a ADRA, ADSS, BAAB ou BAAR; isso descreve apenas a porção visitada, não
exclui outras saídas além do limite. Não corrigimos letras ou escolhemos nomes
pela lore.

Todas essas chaves desconhecem o dígito **2**, ausente de Knightmare e presente
nas duas partes de Chayenne. As 1.769 transferências para cada parte ficam
marcadas `unknown_digits`; não são 1.769 refutações nem traduções da entrevista.
As transferências por grupo para os demais textos também preservam lacunas e
palavras fora do banco. Não houve transferência semântica independente validada.

### Hipóteses BEHOLDER/BONELORD

Forçamos separadamente `3478` a cada nome e exigimos que a mesma chave explique
os sete grupos de Knightmare. Isso é análise de sensibilidade a uma hipótese.

| Regra | BEHOLDER: partições isoladas de 3478 / chaves para toda a fala | BONELORD |
| --- | --- | --- |
| Dígrafo | 1 / 0 | 1 / 0 |
| 1–3 letras | 19 / 0 | 19 / 0 |
| 1–3 fonemas | 16 / 0 | Pronúncia indisponível |
| Sílaba | 0 / 0 | Pronúncia indisponível |

Os **seis ajustes disponíveis terminaram completos, sem chave**. As partições
isoladas não são traduções: precisam sobreviver ao restante da mensagem.
A restrição de dígrafos retoma uma hipótese já examinada na rodada15, agora
conferindo compatibilidade lexical da fala inteira; não a apresentamos como
ideia nova. As regras variáveis e fonéticas ampliam o teste de forma explícita.

### Controles embaralhados

Foram 152 ajustes: 19 embaralhamentos para cada um de dois textos, sob quatro
regras. Cada palavra é embaralhada internamente e repetições recebem a mesma
versão, preservando comprimentos, contagens de dígitos e repetição dos grupos.

| Regra | Controles completos / 38 | Controles com alguma chave encontrada |
| --- | ---: | ---: |
| Dígrafo | 38 | 0 |
| 1–3 letras | 20 | 18 |
| 1–3 fonemas | 32 | 6 |
| Sílaba | 38 | 0 |

Os 76 ajustes de controles de Avar terminaram sem chave. Entre os controles de
Knightmare, 18/19 admitem combinações de letras e 6/19 admitem combinações de
fonemas na porção visitada. Os 24 controles não concluídos têm chaves encontradas;
não estimamos o total de chaves nem calculamos significância com buscas truncadas.
O fato de dados embaralhados também admitirem palavras reforça a necessidade
de gramática, contexto e transferência externa antes de alegar tradução.

No total: **210 ajustes conjuntos** — 40 sintéticos, 12 principais, 152 nulos
e seis com nomes — além dos 120 testes locais. Há 65 ajustes limitados
(40 sintéticos, um principal e 24 nulos), explicitamente preservados como tais.

## Interpretação e próximo experimento

Nenhum significado de 3478 foi confirmado. Uma associação da criatura a esse
número não prova que ele codifique sua grafia inglesa. As hipóteses com nomes
não são textos paralelos atestados e não contam como validação independente.
Cópias da fala de Chayenne nos livros também não fornecem confirmação semântica.

O próximo passo metodológico é testar a recuperação de unidades com controles
mais informativos: todos os dígitos observados no ajuste, mais contextos distintos
e separação explícita entre grafias comuns, nomes próprios e homófonos. Esses
critérios precisam ser fixados antes de novos resultados. A comparação entre
espaços preservados e espaços não lexicais exige outro protocolo e controles
com fronteiras ocultas. Não escolhemos chaves pelo quanto combinam com a lore.

P01/P03/P05/P06 continuam com entregas principais pendentes. Esta rodada não
prova que 469 seja aleatório ou sem significado, e não fecha a missão.

## Reproduzir

```sh
make round23
python3 -m unittest discover -s tests -v
```

Python 3.11+ basta para esta rodada. O replay repete os 120 casos locais,
os ajustes conjuntos, reais e embaralhados, e a auditoria independente,
comparando os resultados com os artefatos publicados. Os testes gerais do
repositório mantêm os requisitos das rodadas anteriores.

Artefatos principais: `data/round23_protocol.json`, `data/round23_fixtures.json`,
`data/round23_summary.json`, `results/round23_qualification.json`,
`results/round23_targets.json` e `results/round23_certificate_audit.json`.


Validação da entrega: **229 testes automatizados passaram**. Uma cópia limpa
do índice Git reproduziu offline todos os ajustes e certificados sem divergência.
Os arquivos congelados dessa cópia foram comparados por hash aos arquivos finais;
registro em `data/round23_verification.json` e log em
`results/round23_offline_replay.log`. Aprovação dos testes de software não
significa qualificação semântica: as 40 buscas sintéticas continuam limitadas.
