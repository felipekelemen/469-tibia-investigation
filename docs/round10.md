# Décima rodada: fontes por modalidade e o livro externo de Kharos

**Nenhuma tradução foi encontrada.** Um parser baseado em fragmentos recuperou
exatamente os códigos de todos os controles positivos, mas não reconstruiu o
livro externo de Kharos. O contraste entre cópia de dígitos e cópia de unidades
importadas expõe uma limitação concreta da transferência da tokenização.
Foram revisadas fontes de falas, nomes, entrevista e poema, sem obter novo
par longo número/inglês explicitamente atestado.

## Texto externo e proveniência

O livro [5159564611](https://www.tibiawiki.com.br/wiki/5159564611_%28Book%29)
tem **137 dígitos** e é associado pela wiki a Kharos/Ferumbras Citadel. A
visualização textual, revisão indicada 403186, coincide integralmente com a
entrada adicional em `s2ward/data/books_sorted_unique_with_kharos.json`.
Ele não é nenhum dos 70 textos normalizados de Hellgate nem uma substring
integral de qualquer deles.

Esse é um texto adicional para este experimento, **já público e conhecido
upstream**, não uma descoberta nova no jogo ou um teste cego. Partes dos seus
dígitos ocorrem nos livros de treino. A wiki não fornece inglês paralelo, e
seus metadados de local/versão não foram autenticados diretamente no cliente.
Fonte, commit e hashes estão em `data/external_book_round10.json`.

## Parser de cópia com fronteiras de códigos

Construímos um dicionário usando apenas os 70 livros e seus códigos importados.
Todos os 79 alinhamentos compatíveis foram considerados. Cada fragmento:

- fica integralmente dentro de um livro de origem;
- começa e termina em fronteiras de códigos naquele alinhamento;
- contém 8–96 dígitos brutos;
- preserva todas as sequências de códigos distintas que produzem o mesmo raw.

O dicionário tem 89.665 strings e 89.887 variantes de códigos. O parser recebe
somente os dígitos do alvo; não recebe sua tokenização, número de símbolos ou
posições de zeros. Minimiza primeiro dígitos sem cobertura e depois número de
fragmentos. Esse é um critério estrutural fixo, não MDL completo ou escore
linguístico. Resíduos ficam sem interpretação; letras não são inseridas.
Todas as alternativas ótimas são preservadas até o limite de 512 streams;
atingir o limite impede alegar unicidade. Nenhum limite foi atingido no alvo.

O limiar primário de 16 dígitos e as sensibilidades 8/12 foram congelados antes
dos resultados. Apenas uma reconstrução integral, única e com o gate positivo
passado poderia receber a chave V4 fixa como exibição literal exploratória.
Não foi ajustada nova chave nem escolhido um caminho por parecer inglês.

## Controles positivos e limites

Cada um dos 30 fixtures usa oito motivos ingleses de 64 letras, cifra
homofônica aleatória de 99 códigos e omissão IID de zeros. O alvo reorganiza
quatro motivos raw completos, com fronteiras ocultas ao parser. Os autores
Baum/Barrie já haviam sido abertos em estudos anteriores: são controles de
capacidade do parser, não qualificação nova de coerência inglesa.

O parser recupera **30/30 streams exatos e únicos em cada limiar**. São 30
conteúdos pareados em três limiares, não 90 textos independentes. O gate
27/30 passa para essa condição de cópia exata. Isso não qualifica decifração
de chave desconhecida ou textos que não preservem essas unidades.

Também foram executadas três condições por fixture/limiar:

|Controle|Fração média de dígitos sem cobertura, limiar 16|
|---|---:|
|Embaralhamento de dígitos|100%|
|Embaralhamento de blocos de 8 dígitos|98,53%|
|Outra ordem dos motivos completos|0%|

Esses 270 controles preservam comprimento e frequências de dígitos. A última
condição continua reconstruível porque conserva os motivos; isso mostra por
que cobertura de cópia não avalia a coerência da ordem ou o significado de
uma mensagem. Motivos podem conter prosa verdadeira mesmo reorganizados.

## Resultado no livro de Kharos

|Mínimo de dígitos por fragmento|Dígitos sem reconstrução|Fragmentos copiados|
|---|---:|---:|
|8|27/137|8|
|12|28/137|7|
|16 — primário|81/137|3|

O método passou os positivos delimitados e falhou em obter reconstrução
integral do alvo. **Não foi produzida uma sequência inglesa para esse livro.**
Completar os resíduos com letras ou escolher outra segmentação pelo inglês
violaria o gate definido. O resultado não prova cifra distinta: pode haver
cortes, junções, alterações ou fronteiras diferentes da reconstrução importada.

Há conteúdo externo, mas também vazamento substancial. Entre suas janelas raw,
67/130 de comprimento 8 e 15/122 de comprimento 16 já aparecem em Hellgate.
Para comprimento 24, uma das 114 janelas aparece. Isso não torna as janelas
restantes observações independentes ou plaintext novo atestado.

## Diagnóstico posterior: copiar dígitos sem fronteiras

Depois de abrir o resultado, registramos um diagnóstico separado, identificado
como exploratório: permitir fragmentos em qualquer posição dos textos, sem
herdar códigos. Com o mesmo máximo 96:

|Mínimo raw|Resíduo com fronteiras de códigos|Resíduo sem fronteiras|
|---|---:|---:|
|8|27|24|
|12|28|24|
|16|81|64|

Permitindo fragmentos de um dígito, todo texto pode trivialmente ser coberto.
A informação útil é o mínimo de peças: **14 fragmentos** cobrem os 137 dígitos.
Contra 99 embaralhamentos de dígitos e 99 de blocos de oito, as médias foram
50,30 e 24,61 peças; os ranks exploratórios de cauda inferior foram 0,01 nos
dois controles. Isso mede reaproveitamento/ordem de dígitos, não semântica.
Não é validação confirmatória: o diagnóstico veio depois da abertura do alvo.

Na cobertura representativa de 14 peças, **sete não possuem nenhuma ocorrência
que comece e termine em fronteiras de códigos**, considerando todos os livros
e todos os alinhamentos. O próprio prefixo de 16 dígitos do alvo é um exemplo.
Não se infere que essa seja a edição histórica feita pelo autor: muitas
ocorrências podem servir como testemunhas do mesmo trecho.

Esse contraste exige distinguir cópia de raw e transferência dos códigos
importados. Não rejeita universalmente a tabela, nem prova que o texto seja
sem significado. Textos cifrados podem ser cortados dentro de unidades, e
outra tokenização ou contexto de fragmentos pode resolver parte da diferença.

## Revisão de significados por modalidade

O inventário de `data/source_review_round10.json` registra 11 entradas de
fontes, com acesso e alcance separados. Resultados principais:

- A [entrevista de Chayenne](https://forum.portaltibia.com.br/topic/11420-entrevista-com-chayenne/)
  foi relida: a resposta contém os números e emoticons, sem uma tradução inglesa
  junto da resposta. Os fragmentos continuam reutilizados nos livros.
- A transcrição de [A Wrinkled Bonelord](https://www.tibiawiki.com.br/wiki/A_Wrinkled_Bonelord)
  associa `1` a Tibia e dá `486486` como nome próprio. São âncoras de referência,
  não licença para traduzir cada dígito 1 interno aos livros ou converter o
  nome numérico no título inglês do NPC. A reação a `0` é contexto de tabu.
- O catálogo [Bonelord/Nostalgia](https://www.tibiawiki.com.br/wiki/Bonelord_%28Nostalgia%29)
  associa `3478` à criatura. A nota sobre correção do nome em 2023 é uma
  alegação da wiki; não obtivemos anúncio primário na busca oficial delimitada.
  A referência à criatura não determina uma tradução lexical geral de `3478`.
- [Elder Bonelord](https://www.tibiawiki.com.br/wiki/Elder_Bonelord) tem sons
  ingleses e numéricos listados, sem emparelhamento explícito. A presença dos
  dois tipos não autentica a leitura comunitária de cada número.
- Na transcrição de [Avar Tar](https://www.tibiawiki.com.br/wiki/Avar_Tar),
  o comentário inglês segue o poema, mas não é apresentado como sua tradução.
  A reputação do personagem também não prova que os números sejam falsos.
- Na [entrevista atribuída a Knightmare](https://forums.tibiabr.com/threads/378403-TibiaBR-entrevista-Knightmare),
  o trecho indexado discute o idioma orc e depois conta uma história ficcional
  sobre um beholder escrevendo textos. Ele não fornece um decoder nem prova
  ausência de significado em 469. A abertura direta ficou em 403.
- A opção numérica da enquete de 2020 continua sem tradução atestada nas
  fontes examinadas; as outras alternativas não fornecem seu plaintext.
  Um GET HTTPS direto ao endereço oficial retornou 403, além da indisponibilidade
  da ferramenta web. O status e o hash da resposta estão em
  `results/official_poll_http_round10.json`; essa falha de acesso não prova
  ausência de uma tradução em material não acessado.

Essas consultas não tornam as transcrições capturas autenticadas do jogo.
Páginas indisponíveis são limites de cobertura. **Nenhum novo par longo
número/inglês explicitamente atestado foi encontrado neste conjunto**, sem
afirmar inexistência em todas as fontes possíveis.

## Relações entre palavras numéricas, sem atribuir significados

Uma [discussão comunitária indexada](https://www.reddit.com/r/TibiaMMO/comments/1u1i3ag/avar_tars_469_poem_seems_to_contain_scrambled/)
motivou um teste separado das palavras de Knightmare e do poema. O critério
conta palavras inteiras de pelo menos três dígitos com o mesmo multiconjunto:

|Knightmare|Avar Tar|Relação demonstrada|
|---|---|---|
|3478|4378|Mesmos dígitos, outra ordem|
|345|453|Mesmos dígitos, outra ordem|

Nenhum par é reversão literal: a reversão de `3478` é `8743`, e a de `345`
é `543`. Chamar essas relações de reversão seria testar um algoritmo diferente
do que os dados mostram. O token inteiro `67538` também é compartilhado entre
o poema e a opção numérica da enquete; não inferimos sua tradução pelo tema.

Foram executadas 999 renomeações globais dos dígitos não zero, mantendo zero,
comprimentos, repetições e padrão de multiplicidades. O rank superior
exploratório foi 0,001. Em outras 999 permutações dentro de cada palavra,
preservando exatamente seus dígitos, a estatística é invariável e o rank é
1,0. O primeiro controle mostra associação com os rótulos específicos; o
segundo deixa claro que o critério não distingue regras de ordenação entre
anagramas. As correspondências foram selecionadas pela comunidade antes do
teste, sem correção por todas as relações previamente procuradas.

Isso registra uma relação numérica local, não igualdade de significados,
compartilhamento de algoritmo ou tradução. Nenhuma palavra inglesa foi
atribuída aos pares. Resultado e plano exploratório estão em
`results/npc_digit_relation_audit.json` e `data/npc_digit_relation_plan.json`.

## Histórico e próxima decisão

As buscas históricas encontraram referências indexadas a uma discussão de
2008 e a uma observação posterior sobre uma pilha parecer ter cinco caveiras
e revelar seis ao inspecionar. As rotas da discussão antiga não ficaram
acessíveis; a página posterior teve leitura parcial e depois 403 nas buscas
focadas. Não autenticamos imagem da sala, contagem ou transição em 2010.
P06 continua aberto; não se repetiu a tentativa de resolver a verificação humana
do player da rodada anterior.

A prioridade passa a uma amostra com plaintext explicitamente atestado ou
uma regra de serialização que possa ser verificada fora dos trechos copiados.
O parser de cópia fica disponível como componente limitado. Inglês plausível
em fragmentos reutilizados, sozinho, não satisfaz a missão.

```sh
make round10
make test
```

108 testes passaram. A verificação é offline e preserva os artefatos congelados.
Resultados completos: `results/copy_parser_experiment.json`,
`results/kharos_copy_diagnosis.json` e `results/kharos_boundary_audit.json`.
