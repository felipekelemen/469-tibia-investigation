# 469-tibia-investigation — investigação reproduzível

**Estado: dezoito rodadas executadas; nenhuma tradução verificável encontrada.**
Não afirmamos que o corpus é indecifrável nem que qualquer solução comunitária
foi confirmada. O alvo é um algoritmo integral que generalize para textos inéditos.

Destino público: https://github.com/felipekelemen/469-tibia-investigation

**Publicado:** corpus normalizado, código, testes e resultados das dezoito rodadas
disponíveis neste repositório. O acesso de escrita foi confirmado após nova reconexão.

A [décima oitava rodada](docs/round18.md) executou 750 inferências exatas em
uma família de candidatos fornecida: novas combinações e molduras válidas
reduzem a ambiguidade; mais cópias dos mesmos pares não reduzem. Esse resultado
restrito não autoriza um decoder de 469. Nas falas reais, o modelo mecânico
testado ainda permite 9.600 parses para Knightmare com os espaços preservados,
sem identificar significados ingleses. A busca limitada de fontes não trouxe
um novo par semântico aceito.

A [décima sétima rodada](docs/round17.md) testou a aprendizagem de unidades com
vocabulário oculto, com seleção em desenvolvimento e qualificação em dois
autores novos. Nenhum dos três métodos passou nos controles com cópias;
a aplicação ao jogo ficou bloqueada pelo gate. Um contraexemplo com duas
chaves de 64 unidades mostra fronteiras diferentes com os mesmos dados,
cardinalidade, frequências e custo de descrição. Não é prova sobre a origem
de 469 nem ausência de significado.

A [décima sexta rodada](docs/round16.md) verificou 45 grupos numéricos como
unidades de um dicionário: são unicamente decodificáveis, mas não segmentam
nenhum livro inteiro. Os pequenos ganhos do codec desaparecem ao retirar os
gritos já copiados. Certificados mostram que o grito de 20 dígitos termina
dentro de um código importado nas seis cópias, com dois streams circundantes
diferentes. Nenhum significado inglês foi inferido.

A [décima quinta rodada](docs/round15.md) executou 1.860 configurações para
matrizes 3×3, 4×4 e 5×5, com BEHOLDER/BONELORD e a sequência periódica 3478.
Recuperou exatamente os 150 controles ingleses, mas não produziu tradução
dos livros ou falas. Chaves 5×5 foram senhas explicitamente conjecturadas:
não há 25 contagens autenticadas da sala. Uma leitura de 3478 por dígrafos
também foi testada, sem evidência independente de significado.

A [décima quarta rodada](docs/round14.md) recuperou a tabela antiga em páginas
arquivadas de 2008, com payloads conferidos no CDX. Relatos atribuídos a abril
de 2010 já descrevem o bloco visível posterior, enfraquecendo a coincidência
com a renomeação de agosto. A data real e a contagem inferior permanecem
incertas; o determinante −18 não resolve as posições questionadas.

A [décima terceira rodada](docs/round13.md) testou a relação ID22/Kharos por
transposição colunar exata com qualquer ordem de 2–32 colunas. Nenhuma chave
ajusta o par; uma implementação independente confirma a contradição já na
primeira coluna. O método passou nos controles de pares conhecidos, mas isso
não identifica nenhum texto como plaintext nem exclui outras cifras.

A [décima segunda rodada](docs/round12.md) confirmou que Kharos e o livro ID22
têm exatamente o mesmo histograma de 137 dígitos, mas não os mesmos códigos
permutados: dois métodos independentes rejeitam essa conservação, mesmo
liberando as omissões de zeros. A enumeração verificou 54.740 padrões.
A sequência oficial Your True Colour foi acrescentada ao inventário, sem gloss.

A [décima primeira rodada](docs/round11.md) comparou dois formatos de cópia
com custos de endereços e comprimentos pagos e decodificação exata. O critério
distingue cortes/fronteiras em 119/120 alvos sintéticos pareados. Em Kharos,
referências a códigos custam 277 bits contra 286 de referências raw, mas
13 dígitos ficam literais. Isso não identifica a cifra ou produz inglês.

A [décima rodada](docs/round10.md) revisou fontes por modalidade e examinou um
texto externo de Kharos. Um parser de cópia recupera todos os positivos, mas
deixa 81/137 dígitos do alvo sem reconstrução no limiar principal. Uma cobertura
por 14 fragmentos raw não transfere automaticamente fronteiras dos códigos.
Não houve novo plaintext longo atestado nem saída inglesa para esse livro.

A [nona rodada](docs/round9.md) excluiu 18 famílias adicionais de estado e
comprimento para os zeros importados e auditou os metadados: `book_positions`
contém offsets de texto, apesar de ser descrito como posição física. Duas
transcrições da wiki coincidem com o corpus; uma gravação histórica exigiu
verificação humana e não forneceu quadros. A expansão de tabelas foi encerrada
até uma pista de serialização independente.

A [oitava rodada](docs/round8.md) verificou 15 famílias de regras de zeros
considerando todos os alinhamentos dos códigos importados. Treze têm
contradições forçadas; duas tabelas cabem no treino, mas não identificam as
decisões novas. Um ciclo fixo 4×4 de formatação também falha. A [posição no
plano](docs/plan_status.md) distingue sete frentes e quatro pendências principais.

A [sétima rodada](docs/round7.md) testa a recuperação de fronteiras/zeros a
partir dos dígitos brutos em duas versões e novos autores. O parser usa chave
correta fornecida; não é busca de chave nem tradução de 469. Há 480 condições
positivas e 960 controles de ordem pareados, com protocolos congelados e
diagnóstico exato das falhas. [Método](docs/raw_parser.md).

A [sexta rodada](docs/round6.md) revisou literalmente as 70 saídas V4, executou
600 avaliações externas de um critério lexical e auditou a segmentação dos
dígitos. Nenhuma candidata longa foi identificada; o avaliador não qualificou
e o controle modular ficou bloqueado no reservado. A reconstrução intermediária
ainda depende de códigos/zeros importados, sem regra raw→tokens validada.

A [quinta rodada](docs/round5.md) melhorou a busca em prosa cifrada copiada,
qualificou uma nova versão em90testes e executou297controles nos livros.
Há sinal de tetragramas nos três nulos testados, mas nenhuma saída validada
como inglês coerente. A origem desse sinal permanece em investigação.

A [quarta rodada](docs/round4.md) qualificou V2 em 180 testes de autores novos
e executou a busca homofônica nos livros com 297 controles reotimizados.
A saída não é inglês coerente; a vantagem não persistiu nos controles de
bigramas e blocos. Prosa cifrada copiada ainda revelou falhas do solucionador.

A [terceira rodada](docs/round3.md) executa o plano auditado: qualificação
homofônica em180ajustes, modelos gerativos, fontes e leitura matricial.
Nessa versão V1, o solucionador passou5de6cenários e o gate permaneceu fechado;
a quarta rodada usa protocolo novo e qualificação distinta.

A [segunda rodada](docs/round2.md) testa Hill módulo29, homofonia com nulos de
bigramas, o canal residual e a geometria do mapa.

A [auditoria do Deep Research](docs/research_crosswalk.md) corrige as pistas de
mapas e validação externa. O [plano atualizado](docs/next_experiments.md) define
os próximos experimentos e seus critérios de avanço.

O [relatório da primeira rodada](docs/report.md) distingue resultados demonstrados, indícios e
hipóteses. [Protocolo de validação](docs/validation_protocol.md).

## Reproduzir

Python3.11+ e NumPy2.3.5; a terceira rodada também requer `g++` C++17.
Os testes de corpus/matrizes/estrutura usam stdlib.

```sh
python -m pip install -r requirements.txt
python scripts/bootstrap_sources.py
make experiments
make round2
make round3
make round4
make round5
make round6
make round7
make round8
make round9
make round10
make round11
make round12
make round13
make round14
make round15
make round16
make round17
make round18
make test
```

`make reproduce` também obtém as fontes fixadas por commit. Os scripts não
necessitam credenciais nem acesso ao jogo. A primeira obtenção das referências
públicas exige rede; os artefatos normalizados e resultados ficam versionados.
A bateria de criptoanálise usa uma referência externa inglesa de Alice, não
Tibia, com pontuador congelado. Resultados estocásticos usam sementes fixas.
Os números de tempo de execução dependem da máquina; reserve alguns minutos.
`make round15-full` repete também as 468 buscas completas dos controles da
rodada15; `make round15` confere os vencedores registrados e refaz os positivos
e as buscas observadas. O relatório explica o alcance de cada reprodução.

## Material

| Caminho | Conteúdo |
|---|---|
| `sources/manifest.json` | Três repositórios de origem, commits e hashes dos arquivos |
| `data/normalized_books.json` | Corpus original de dígitos + reconstrução de códigos e símbolos |
| `data/normalized_splits.json` | Divisões e máscaras de reutilização |
| `data/historical_sources/` | Metadados, URLs, respostas HTTP e hashes da pesquisa histórica |
| `scripts/` | Auditoria, reconstrução, cifras, geradores e controles |
| `tests/` | Controles positivos e verificações automatizadas |
| `results/` | Saídas JSON e logs reais das execuções |
| `docs/hypotheses.json` | Registro de hipóteses, resultados negativos e limites |
| `docs/` | Relatórios especializados e síntese |

Clones upstream completos e capturas HTML/TXT ficam na cópia local, ignorados
pelo Git; fontes podem ser recuperadas dos commits e URLs registrados. A ausência
de XLSX materializado via Git LFS é explicitada na auditoria; usamos JSON/CSV
versionados, não fingimos ter reexecutado a planilha operacional.

Código original sob MIT. Texto de Tibia ©CipSoft GmbH; dados, mapas e pesquisas
upstream preservam atribuição e termos próprios. Projeto independente, sem
vínculo com CipSoft. Consulte [atribuições](docs/attribution.md).
