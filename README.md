# 469-tibia-investigation — investigação reproduzível

**Estado: oito rodadas executadas; nenhuma tradução verificável encontrada.**
Não afirmamos que o corpus é indecifrável nem que qualquer solução comunitária
foi confirmada. O alvo é um algoritmo integral que generalize para textos inéditos.

Destino público: https://github.com/felipekelemen/469-tibia-investigation

**Publicado:** corpus normalizado, código, testes e resultados das oito rodadas
disponíveis neste repositório. O acesso de escrita foi confirmado após nova reconexão.

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
make test
```

`make reproduce` também obtém as fontes fixadas por commit. Os scripts não
necessitam credenciais nem acesso ao jogo. A primeira obtenção das referências
públicas exige rede; os artefatos normalizados e resultados ficam versionados.
A bateria de criptoanálise usa uma referência externa inglesa de Alice, não
Tibia, com pontuador congelado. Resultados estocásticos usam sementes fixas.
Os números de tempo de execução dependem da máquina; reserve alguns minutos.

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
