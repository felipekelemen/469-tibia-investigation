# Auditoria do corpus e reprodução da camada de símbolos

A execução `python scripts/audit_corpus.py` verificou **70 livros únicos, 11.263 dígitos, 37 comprimentos ímpares**. As cópias de `s2ward/books.json`, `arturo/data/books.json` e `kimlage/analysis/audit_20260609/books_digits.json` concordam integralmente, na mesma ordem. Isso verifica consistência entre cópias de origem comunitária compartilhada; não substitui comparação independente com o jogo ou capturas históricas.

## O que foi reproduzido

Importamos os streams de códigos de `kimlage/analysis/audit_20260609/hs_corpus.json` e o mapa de `kimlage/analysis/row0_origin_parallel_20260621/data/row0_pair_table_canonical.csv`. Uma implementação independente de alinhamento por programação dinâmica confirmou que cada stream pode produzir exatamente os dígitos originais removendo **somente zeros iniciais de códigos de dois dígitos**. Há 195 remoções e 5.729 códigos/símbolos, em 70/70 livros. O mapa contém 99 códigos observados para 14 rótulos: `*ABCEFILNORSTV`. As contagens por rótulo reproduzem as contagens publicadas.

**Esse resultado é condicionado à tokenização e ao mapa importados.** Não descobrimos essa tabela de forma independente. A identidade `11263 + 195 = 2 × 5729` e o roundtrip demonstram consistência mecânica; não provam origem histórica, unicidade, letras verdadeiras, idioma ou tradução. Nos livros 2, 10, 13, 14, 19, 27, 35, 57 e 67 existem duas ou mais escolhas de posições de remoção compatíveis com o mesmo stream importado; a contagem é truncada em 2. A interpretação de que as remoções foram deliberadas pelos autores não foi demonstrada.

Os três arquivos `.xlsx` da cópia de kimlage são ponteiros Git LFS de 133 bytes. Portanto **não** comparamos independentemente os valores `decodedbase` dos workbooks. A reprodução aqui usa os artefatos JSON/CSV versionados, e essa limitação consta do resultado estruturado.

## Vazamento e divisão de validação

Há 31 relações dirigidas de contenção exata envolvendo 20 livros contidos em outros. Um grafo liga dois livros quando compartilham qualquer trecho exato de comprimento mínimo `k`; componentes conexos incluem também conexões transitivas.

| k (dígitos) | Tamanhos dos componentes |
|---|---|
| 8 | 70 |
| 12 | 70 |
| 16 | 68, 2 |
| 24 | 67, 2, 1 |
| 32 | 65, 2, 2, 1 |
| 48 | 55, 4, 2 e nove isolados |

Não existe divisão não vazia de livros que elimine todo compartilhamento de 12 dígitos. O split por componentes de 16 dígitos reserva o componente de 2 livros; garante ausência de coincidências exatas de 16 ou mais dígitos entre os lados, mas permite compartilhamentos menores e não implica independência estatística.

Um segundo protocolo exploratório reserva os candidatos 56–69 e mascara toda posição pertencente a um 12-grama presente nos livros 0–55. Restam apenas **3 fragmentos, 58 dígitos** em trechos de pelo menos 12 dígitos. Esse conjunto minúsculo mostra por que uma divisão aleatória de livros seria enganosa. Fragmentos transformados, unidades menores e relações semânticas permanecem possíveis; não chamamos esse conjunto de prova de independência total.

Os experimentos iniciais permanecem exploratórios. Nenhum dos splits dispõe de plaintext atestado, e o conjunto completo já informou a pesquisa comunitária que produziu a tokenização. Uma hipótese derivada dessa pesquisa precisa de fragmentos externos inéditos e pares cifra/plaintext oficiais para uma avaliação confirmatória convincente.

## Artefatos e testes

- `data/normalized_books.json`: dígitos originais, códigos, rótulos e posições de remoção escolhidas por livro; identificadores zero-based, preservando a ordem comunitária.
- `data/normalized_code_map.json`: mapa importado, sem promover rótulos a significados.
- `data/normalized_splits.json`: grupos e fragmentos com posições exatas de início/fim.
- `results/audit.json`: métricas, proveniência, commits, hashes e limitações.
- `tests/test_corpus.py`: seis testes verificam roundtrip de todos os livros, rejeição de deleções ilegais, identificação de ambiguidade, transitividade de componentes e ausência dos k-gramas proibidos em ambos os splits.

Os dígitos derivam de *Tibia*, de CipSoft GmbH. A cópia local preserva as fontes; os números são incluídos somente para investigação e reprodução, sem reivindicar direitos sobre conteúdo do jogo. O mapa/tokenização e sua atribuição vêm da pesquisa de Kim de Amorim Lage (2026); código e documentação upstream estão sob MIT, e os dados do jogo têm a ressalva explícita de `sources/kimlage/NOTICE`. As três cópias não são três fontes independentes de verdade.
