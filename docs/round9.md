# Nona rodada: estados dos zeros, metadados e tentativa de evidência histórica

**Nenhuma tradução foi encontrada.** Testamos 18 famílias adicionais de
regras de zeros, com comprimentos e estados que mudam ao longo do livro.
Todas são incompatíveis com os códigos importados. A auditoria também
identificou um campo comunitário descrito incorretamente como posição física.
Uma gravação histórica foi aberta no navegador, mas o conteúdo ficou atrás
de verificação humana; nenhum quadro da sala das caveiras foi examinado.

## Metadados auditados antes de testar sementes

O README de Arturo descreve `book_positions.json` como posição física no jogo.
O código que o produz usa `master.find(books[i])` e grava índice do livro,
offset de string e comprimento. **É posição em uma reconstrução textual,
não coordenada geográfica.** Das 70 entradas, 56 têm offset -1. Nenhuma
das 70 coincide com a busca no `master_text.txt` atualmente versionado,
mostrando também uma inconsistência entre esses artefatos. Isso não valida
a narrativa reconstruída ou indica coordenadas ocultas.

Esse arquivo foi excluído como semente de localização. As evidências vêm
do [gerador de offsets](https://github.com/arturoornelasb/tibia-bonelord-469-cipher/blob/007dcf1707acc9b991642e68bcac08214a5bb38c/scripts/experimental/master_text.py)
e do [README dos dados](https://github.com/arturoornelasb/tibia-bonelord-469-cipher/blob/007dcf1707acc9b991642e68bcac08214a5bb38c/data/README.md),
no commit fixado. Pequenos snapshots, licença MIT e hashes foram preservados
em `data/metadata_reference/` para reprodução offline.

O arquivo distinto `bookcase_mapping.json` foi conferido com um parser
independente da listagem textual: **71 ocorrências, 70 textos únicos e 40
estantes**, com correspondência integral dos dígitos. O mesmo texto, livro 61,
ocorre nas estantes listadas como 19 e 26. Mantivemos ambas as ocorrências,
sem escolher uma localização conveniente ou separar cópias entre treino/teste.

Os números das estantes são categorias ordenadas de uma listagem comunitária,
sem autenticação de x/y/z por livro. Números TIBN de outra wiki podem usar um
esquema diferente; não os tratamos como a mesma escala ou como contradição
de posição. Rótulos numéricos dos livros também não foram aceitos como
plaintext ou metadados independentes da própria escrita.

## Corroboração externa limitada

A transcrição acessível de [0943435084](https://www.tibiawiki.com.br/wiki/0943435084_%28Book%29),
revisão indicada 403238, coincide nos 150 dígitos com o livro 30. A de
[9521991184](https://www.tibiawiki.com.br/wiki/9521991184_%28Book%29), revisão
403321, coincide nos 151 dígitos com o livro 64. Isso corrobora a diferença
de escrita inicial discutida na rodada 8, sem confirmar os códigos latentes.

A primeira veio do trecho indexado, pois a abertura direta retornou 403;
a segunda, de uma visualização textual indexada da página. Esses mecanismos
não são captura bruta autenticada do jogo. Wikis e repositórios podem compartilhar
transcrições, portanto não surgiram novos testes semânticos cegos ou glosses.
URLs, método, revisões indicadas e comparações exatas estão em
`data/metadata_web_evidence.json`.

## Estado e comprimento: teste congelado

Em cada família perguntamos se existe **qualquer tabela booleana** que,
recebendo o código atual e o estado declarado, escolha os zeros de forma a
produzir os dígitos. Não foi usado inglês, nome de criatura ou escore da lore.

O estado é calculado antes da decisão atual. Nos contadores de dígitos escritos,
ele muda conforme o alinhamento; cada caminho completo foi considerado com
seus próprios estados. Não se congelou uma das nove restaurações ambíguas.
O teste mantém dependências entre decisões e pode excluir uma família por
contradição no mesmo livro ou entre todas as opções compatíveis de livros.

|Família|Quantidade|Resultado|
|---|---:|---|
|Código + comprimento em códigos/bruto módulo 2/4/16|6|Incompatíveis|
|Contador em códigos módulo 32, iniciado pelo comprimento em códigos|1|Incompatível|
|Contadores de dígitos escritos módulo 16/32, iniciados por comprimento|3|Incompatíveis|
|Soma dos códigos anteriores módulo 16, iniciada por comprimento|2|Incompatíveis|
|XOR dos códigos anteriores módulo 16, iniciado por comprimento|2|Incompatíveis|
|Paridade do comprimento + célula 16 + paridade do bloco|1|Incompatível|
|Ordinal da estante módulo 16, com estado constante/soma/contador raw|3|Incompatíveis|

Foram 16 contradições forçadas entre opções de livros e duas famílias sem
nenhum alinhamento internamente compatível de um livro. Nenhum limite de
alinhamento ou busca foi atingido. Os certificados e entradas exatas estão
em `results/zero_state_constraints.json`.

Os comprimentos exigem cuidado:

- **Comprimento bruto:** observável nos dígitos. Usá-lo como semente final
  define uma restrição possivelmente não causal; um encoder precisaria
  resolver a consistência do comprimento que ele próprio produz.
- **Comprimento em códigos:** deriva da tokenização importada. É informação
  extra em um teste raw→texto, não uma fronteira já recuperada pelo algoritmo.
- **Ordinal de estante:** metadado comunitário condicional, não posição física
  autenticada. Os modelos usam 69 ocorrências de descoberta, incluindo a cópia
  do livro 61, mas continuam apenas 68 conteúdos de descoberta.

Cada modelo recebe somente as informações declaradas. Foram congelados dois
defaults para entradas novas — preservar zero e maioria por código com média
sobre alinhamentos de treino. Como nenhuma família ajusta descoberta, nenhum
default foi promovido a previsão nos reservados.

## Controles e decisão de parada

**18 corpora positivos**, com oito mensagens sintéticas cada, foram gerados
por uma regra compartilhada conhecida: todos foram reconhecidos como
compatíveis. Nas famílias condicionadas ao comprimento bruto, o gerador
buscou um ponto fixo e repetiu a amostragem quando não existia um; foram 20
tentativas descartadas no total. Isso testa o solucionador de restrições,
sem qualificar essas regras como encoders universais.

**39 corpora embaralhados** preservam comprimento por livro e contagem de
omissões por código/livro. Só depois do embaralhamento dos 70 textos se
reproduz a ocorrência duplicada da listagem, preservando sua identidade.
As 702 combinações de corpus/família foram incompatíveis.

**39 permutações dos ordinais das estantes**, mantendo membros de cada
estante, foram testadas nas três famílias de localização. As 117 combinações
também foram incompatíveis. Não se interpreta essa falha compartilhada como
evidência de que o número real da estante seja uma chave.

O critério de parada foi fixado antes da execução: encerrar esta grade de
18 famílias e exigir nova evidência de serialização antes de aumentar estados
ou tabelas para absorver exceções. Esse critério foi seguido. As exclusões são
condicionadas aos códigos importados; estados diferentes, tokenizações
alternativas, lookahead e outros mecanismos não foram universalmente excluídos.

## Gravação histórica: reprodução bloqueada

O catálogo da [gravação de Tetuni em Hellgate](https://tibiacams.com/watch/e15cded1cdfb?t=0)
indica 10/01/2007, cliente 7.80, duração 9:54 e arquivo `.rec`. A página foi
aberta em Chromium/Playwright, com uma sessão nova e sem envio de formulários.
O player carregou os recursos do cliente, mas a requisição de reprodução
retornou **403**, acompanhada de uma janela de verificação humana do Cloudflare.
A captura de tela foi inspecionada e ficou local, com hash registrado.

**Zero quadros da gravação foram examinados.** Não se confirmou que a câmera
visite a matriz nem se contou qualquer caveira. A data do catálogo continua
uma atribuição do site; os recursos carregados não são prova de reprodução.
O registro sanitizado não inclui cookies, estados do navegador ou URLs de
desafio. Resultado: `results/historical_cam_probe_round9.json`.

A [página de licença](https://tibiacams.com/licence) informa que o renderer é
tibiarc/AGPL-3 e que as gravações vêm de coleções de jogadores. Não distribuímos
assets do cliente, renderer ou a gravação. O probe opcional fica em
`scripts/historical_cam_probe.py`; o teste offline não depende de navegador.

P06 continua aberto. A próxima coleta histórica deve buscar outra gravação
ou captura acessível com origem e versão, especialmente na janela de 2010,
antes de relacionar a alteração das caveiras ao nome da criatura. A frente de
formatadores ampliados fica suspensa até uma pista de serialização verificável;
P01 e P05 seguem prioritários para fontes e significados atestados.

## Reprodução

```sh
make round9
make test
```

102 testes passaram. `make round9` confere snapshots, relações da listagem,
corroborações textuais e repete os 18 testes principais e positivos, sem rede
ou alteração dos artefatos. A execução integral de estados está em
`python scripts/zero_state_experiment.py --run`, que recusa substituir um
resultado existente. O probe histórico é opcional, exige Playwright/Chromium
e acesso à rede, e não resolve verificações humanas.
