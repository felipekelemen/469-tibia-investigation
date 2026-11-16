# Rodada 19: foto numérica e fronteira de Chayenne

**Nenhuma tradução inglesa verificável foi encontrada.** Executamos duas
investigações numéricas ligadas a fontes do jogo, sem atribuir letras ou palavras.
Os protocolos e seus hashes foram gravados antes das comparações desta rodada.
As pistas e a fala já eram públicas: esta não é uma validação semântica cega.

## A tabela pública não explica a foto por projeção direta

Uma [discussão comunitária de 2020](https://www.reddit.com/r/TibiaMMO/comments/gmgkux/a_note_regarding_mysteries_leaked_data/)
associa o papel numérico da foto a uma tabela técnica chamada `conversion.lst`.
Obtivemos a [tabela pública indicada](https://pastebin.com/Mn5FspPT): 4.294 linhas
com três inteiros cada. Duas extrações, texto bruto e HTML, concordam; são duas
representações do mesmo paste, não fontes históricas independentes. A função
das colunas, a versão e a procedência atribuída ao arquivo não foram autenticadas.

A transcrição conservadora da foto, conferida nas imagens espelhadas indicadas
pelo repositório s2ward, mantém dígitos ocultos como `?`. O par 737→469 foi
reservado para calibrar as seis projeções dirigidas possíveis entre as três
colunas. Outros 14 pares totalmente visíveis seriam validação numérica; não
escolheriam a projeção.

**Nenhuma das seis projeções aceita sequer 737→469.** Na tabela, 737 aparece
na terceira coluna com 14 e 120 nas outras duas; 469 aparece com 12 e 68.
Logo, nenhuma projeção fica elegível para prever os 14 pares. O resultado rejeita
somente essa correspondência direta nesta tabela. Não exclui outra versão,
composição de colunas, outro arquivo ou outras operações. Não demonstramos que
o papel seja uma cifra nem que a identificação comunitária esteja correta.

Os controles aleatórios da foto são **não aplicáveis**: o conjunto de modelos
calibrados ficou vazio. O runner congelado registra 1.998 posições de loop e
máximos vazios iguais a zero; não houve comparações efetivas de tabelas
randomizadas. Os campos `p=1` são placeholders sem interpretação estatística.
Essa limitação está explícita em `data/round19_scope_notes.json`; não usamos
esses campos como evidência e não ampliamos a família após observar a falha.

O acesso à URL atribuída à publicação original do Facebook devolveu uma página
genérica. As imagens consultadas representam a mesma foto, não duas observações.
Não autenticamos a data alegada nem completamos dígitos pela tabela candidata.

## Uma fronteira numérica recuperável, sem significado inglês

Reproduzimos uma afirmação já exposta no
[estudo de kimlage](https://github.com/kimlage/tibia-469-cipher-casestudy/blob/main/docs/wiki/README.md):
a resposta numérica atribuída a Chayenne pode ser dividida em dois trechos
encontrados nos livros. Concatenamos as duas partes canônicas do inventário:

```
114514519485611451908304576512282177 | 6612527570584
```

O algoritmo recebeu somente a sequência concatenada e os 68 livros de
descoberta. Enumerou os 48 cortes possíveis, exigindo que cada lado completo
ocorresse dentro de um livro. Não recebeu a posição de separação publicada.
Há um único corte válido: **36 + 13 dígitos**, coincidente com a separação da
entrevista. O resultado é igual usando todos os 70 livros.

O trecho de 36 dígitos tem 11 endereços nos livros; o de 13 tem nove. Os 99 pares
de endereços não são 99 confirmações independentes. A resposta inteira não ocorre
em um único livro. Invertendo a ordem dos dois trechos, o método também recupera
a fronteira 13 + 36, mostrando que o critério não decide qual ordem faz sentido.

| Controle | Réplicas | Alguma cobertura por dois trechos | Corte gerador único |
| --- | ---: | ---: | ---: |
| Bijeção global dos dígitos da resposta | 999 | 0 | 0 |
| Embaralhamento dos dígitos da resposta | 999 | 0 | 0 |
| Novos pares de fragmentos dos livros, comprimentos 36 e 13 | 999 | 999 | 802 |

Os controles de cópia preservam a característica relevante: conteúdo retirado
do próprio corpus, incluindo sua repetição. Todos contêm o corte gerador por
construção; em 802/999 ele é único. A unicidade observada é compatível com
simples compartilhamento de fragmentos. Não permite inferir tradução, gramática
ou intencionalidade semântica. Os dois primeiros controles apenas distinguem
essa relação de duas perturbações numéricas específicas; não fornecem um valor
de significância para uma hipótese de língua.

Também verificamos os extremos das ocorrências em todos os alinhamentos
compatíveis com os códigos importados e a omissão opcional de zero. Somente uma
ocorrência do trecho esquerdo (livro 31, intervalo bruto [143,179)) tem os dois
extremos em fronteiras de códigos no mesmo alinhamento. Nenhuma das nove
ocorrências direitas tem ambos os extremos alinhados. Portanto não herdamos
uma sequência completa de códigos para a resposta. Isso limita esse uso dos
códigos importados, sem demonstrar quais seriam as unidades reais de 469.

As cópias são do corpus atual e da entrevista transcrita. Não autenticamos aqui
uma captura dos livros anterior a 2009; a direção histórica da cópia permanece
indeterminada. A pergunta em inglês, comentários e emoticons da entrevista não
foram usados como texto claro.

## Fontes, reprodução e próximos testes

A revisão de capturas arquivadas de 2008, já preservadas na rodada 14, não
encontrou sequências contínuas de pelo menos 20 dígitos no texto visível extraído.
Isso não cobre imagens ou prova ausência de livros na época. O corpo atual do
tópico de 2007 contém variantes de teorias; a data do tópico não autentica a
data de seu conteúdo atual. Não obtivemos novas contagens históricas das
matrizes ou um novo par número/inglês.

Reprodução offline, sem rede:

```
make test
make round19
```

São 189 testes automatizados no projeto. O replay confere hashes e reexecuta
as seis projeções, os cortes e os 2.997 controles de cópia. Quando disponíveis
localmente, também confere as capturas completas e reextrai os inteiros; um
checkout público usa os fatos numéricos normalizados e não reautentica páginas
ou imagens ausentes. Capturas completas não são redistribuídas nesta rodada.

Prioridades seguintes:

1. Encontrar captura datada do texto de livros anterior à entrevista e à
   renomeação; separar história editorial de estrutura criptográfica.
2. Procurar recombinações atestadas dos mesmos fragmentos em contextos novos,
   com teste de fronteiras e controles de cópia previamente definidos. Não
   tratar os 99 endereços como dados independentes ou promover códigos importados
   a unidades demonstradas.
3. Exigir documentação independente da tabela técnica antes de testar novas
   composições de colunas. Não ajustar aritmética aos pares visíveis da foto.
4. Continuar buscando âncoras semânticas independentes. Matrizes 3×3, 4×4 e 5×5,
   BEHOLDER/BONELORD e 3478 permanecem documentados nas rodadas anteriores;
   esta rodada não oferece nova evidência a favor dessas chaves.

P01, P03, P05 e P06 continuam abertos. Nenhum experimento desta rodada satisfaz
o critério de generalizar de 469 para inglês em conteúdo semanticamente inédito.
