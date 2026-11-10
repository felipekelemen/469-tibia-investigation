# P01 e P05 — inventário de fontes e viabilidade de validação

**Execução concluída: inventário ampliado e dependências medidas; nenhum novo
plaintext atestado e nenhuma tradução promovida.** A análise usa transcrições
locais fixadas de s2ward, a auditoria prévia de fontes e os livros normalizados.
Não representa nova captura independente do cliente nem nova autenticação de
todas as páginas originais. URLs, linhas, hashes e limites estão nos JSONs.

## Inventário efetivamente examinado

`data/source_validation_inventory.json` contém 16 amostras: 15 candidatas de
conteúdo do jogo/desenvolvedores e um controle hexadecimal excluído. As novas
entradas incluem gritos de Evil Eye e Elder Bonelord, dois gritos do bibliotecário,
a pergunta de Your True Colour de 2012, números da Secret Library de 2018,
opção C da enquete de 2020 e três âncoras nominais/de tabu. A enquete não recebe
tradução com base nas respostas das outras alternativas.

A data da ocorrência é mantida conforme a atribuição da transcrição. Datas de
captura e versões não verificadas ficam `null`; não se infere uma versão do
jogo apenas pelo ano. Todas as amostras já eram públicas e conhecidas upstream:
**zero testes prospectivos cegos novos** foram obtidos por este inventário.

| Amostra | Dígitos | Ocorrências integrais nos livros |
|---|---:|---:|
| Chayenne, parte 1 |36|11|
| Chayenne, parte 2 |13|9|
| Knightmare |24|0|
| Avar Tar |115|0|
| Evil Eye / mesmo grito de Elder Bonelord |9|0|
| Outro grito de Elder Bonelord |11|0|
| Bibliotecário, `485611800364197` |15|1|
| Bibliotecário, `78572611857643646724` |20|6|
| Your True Colour 2012 |21|0|
| Secret Library 2018 |10|0|
| Enquete 2020, opção C |26|0|

São correspondências exatas em dígitos originais, sem cruzar fronteiras de
livros. Cobertura por trechos de 8, 12, 16 e 24 dígitos também foi registrada.
Os tokens curtos `1` e `0` aparecem trivialmente muitas vezes; isso não é
informação léxica. Ausência da string completa não implica ausência de
reutilização transformada, cifra distinta ou independência semântica.

A descoberta adicional relevante é que os dois gritos do bibliotecário também
reutilizam os livros. Portanto a categoria “NPC” não pode ser tomada como
sinônimo de um sistema de palavras separado dos livros. A relação precisa ser
modelada por fonte e por amostra.

## Projeções para a camada intermediária

Uma projeção foi aceita somente quando uma ocorrência integral coincidiu com
fronteiras dos tokens registrados em um livro cujo alinhamento de zeros é
único (`alignment_count_capped_2 == 1`). Isso evita inventar uma nova
segmentação para fazer uma frase caber na tabela.

A primeira parte de Chayenne possui uma projeção admissível nesse critério;
o primeiro grito do bibliotecário também. As demais ocorrências não satisfazem
as condições conjuntas de alinhamento único e fronteira integral. Isso não é
falha de uma cifra: apenas impede apresentar uma projeção condicionada como
se fosse inequívoca. As sequências herdadas são rótulos arbitrários, não
traduções. A análise não modifica a tabela nem escolhe alinhamento por inglês.

## É possível dividir os livros em três partes sem vazamento exato?

Componentes são formados transitivamente: se A compartilha um k-grama com B
e B com C, os três permanecem juntos, mesmo que A e C não coincidam diretamente.
Não se escolheu um limiar depois de observar pontuações de idioma.

| Limiar em símbolos row0 | Tamanhos dos componentes | Códigos nos componentes | Três partes não vazias? |
|---|---|---|---|
|8|68, 2|5668, 61|**Inviável**|
|12|66, 2, 1, 1|5553, 61, 60, 55|Viável apenas para esse limiar exato|
|16|65, 2, 1, 1, 1|5462, 61, 60, 91, 55|Viável apenas para esse limiar exato|
|24|53, 3, 2 e 12 isolados|Maior componente: 4601|Viável apenas para esse limiar exato|

O relatório também conserva componentes por limiares em dígitos originais.
Com 8 e 12 dígitos, os 70 livros continuam conectados; a separação por esse
critério é inviável. Na camada simbólica, permitir coincidências menores que
12 símbolos já produz componentes pequenos, mas não demonstra independência:
a maioria do corpus ainda está no componente gigante, os conjuntos de teste
ficariam minúsculos e a própria representação row0 foi aprendida upstream
com o corpus inteiro. **Não foi criado um novo holdout confirmatório.**

## P05: código por palavra e identifiabilidade

Foi feita a triagem leave-source-out do inventário, registrando grupos numéricos
repetidos em outras fontes e amostras que reutilizam livros. Nenhuma divisão
conta com um par longo número/plaintext oficial para avaliar o significado.

As interpretações comunitárias “look at you”, “let me see you” e “be a wit
than be a fool” estão registradas somente como hipóteses. Não foram usadas
como rótulos de treinamento nem como verdade para pontuar a mesma tabela.
As referências a `486486`, `1` e ao tabu de `0` são âncoras de nome, entidade
ou contexto na transcrição, não dicionário oficial de frases em inglês.

Resultado da porta semântica: **BLOCKED_SEMANTIC_IDENTIFICATION**. Pode-se
renomear consistentemente cada palavra/conceito latente e preservar todas as
repetições numéricas; sem rótulos externos, estrutura não identifica os
significados. Isso não impede propor um codebook, mas impede validá-lo contra
sua própria saída ou afirmar tradução única. Nenhuma frase recebeu reparos,
anagramas ou gloss novo nesta execução.

## Reprodução e próximos passos autorizados

```sh
python scripts/source_validation_inventory.py
python -m unittest discover -s tests -p test_source_validation_inventory.py -v
```

Quatro testes passaram: transitividade que impede uma divisão em três partes,
prevenção de junções artificiais entre livros, exigência de fronteiras e
alinhamento único para projeção e regressão da reutilização de Chayenne.

O próximo lote de fontes deve buscar transcrições/capturas realmente
independentes e glosses atestados, conservando a separação entre atestação
externa de números conhecidos e conteúdo novo. Sem isso, o trabalho P05
continua uma busca estrutural com múltiplas interpretações possíveis, não um
teste confirmatório de tradução. P02 pode avançar em positivos externos sem
depender desse bloqueio de fontes.
