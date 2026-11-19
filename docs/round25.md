# Rodada25 — 3478: nome, código e chave são hipóteses distintas

Executada em19/11/2026 sobre `be870129208e613cb8fe90ed948e6676834da27b`.
**Há documentação histórica mais precisa do nome3478, mas nenhuma tradução
verificada de BEHOLDER/BONELORD e nenhuma chave criptográfica identificada.**
A pista dos anagramas permanece estrutural; sua força depende do controle.
Resultado da missão: inconclusivo.

## Histórico recuperado

Três consultas públicas à API MediaWiki recuperaram metadados e14 versões
com conteúdo. Conferimos os SHA1 informados pela API contra cada texto e
registramos também SHA256 dos corpos HTTP. O
[registro completo](../results/round25_history.json) contém links para cada versão.

| Revisão | DataUTC | Campo de nome e contexto |
| --- | --- | --- |
| [52205](https://www.tibiawiki.com.br/index.php?oldid=52205) | 28/03/2012 | `3478 (Nostalgia)`; associa a criatura ao aniversário de15 anos |
| [52214](https://www.tibiawiki.com.br/index.php?oldid=52214) | 29/03/2012 | Campo simplificado para `3478` |
| [383313](https://www.tibiawiki.com.br/index.php?oldid=383313) | 18/12/2022 | Ainda `3478` |
| [386341](https://www.tibiawiki.com.br/index.php?oldid=386341) | 08/01/2023,22:12:26 | Registro da movimentação da página; conteúdo ainda conserva3478 |
| [386343](https://www.tibiawiki.com.br/index.php?oldid=386343) | 08/01/2023,22:13:45 | `Bonelord (Nostalgia)`; nota relata correção do nome no jogo |

São datas do histórico atual da wiki, **não datas autenticadas de atualização
do servidor da CipSoft**. Não há evidência de ID interno do objeto. A consulta
de2012 tinha continuação não coletada: as dez primeiras revisões localizaram a
criação registrada da página, mas não representam todo seu histórico.

Isso apoia3478 como rótulo de criatura, sem estabelecer letras, palavra comum,
nome próprio ou chave. A renomeação geral BEHOLDER→BONELORD em2010 e a correção
de um nome nostálgico relatada em2023 são eventos diferentes. Nenhum dos dois
implica por si só mudança coordenada das caveiras.

## Experimento novo: famílias de transformações e seleção de exemplos

A rodada24 confirmou3478/4378 e345/453, exemplos selecionados anteriormente
pela comunidade. Congelamos [protocolo](../data/round25_protocol.json), código
e hashes antes dos novos cálculos. Os textos já eram conhecidos; não existe
reservado semântico nesta rodada.

Usamos45 posições de grupos numéricos em oito conjuntos de procedência,
representando44 grupos distintos globalmente. Removemos repetições dentro de
cada conjunto e reunimos os gritos idênticos de duas criaturas. Chayenne mantém
seus fragmentos inteiros. São unidades operacionais, não palavras demonstradas.
Grupos menores que três dígitos e a atribuição problemática a tibia.org ficam fora.

Comparamos os28 pares de conjuntos sob sete famílias: identidade, reversão
inteira, rotação cíclica, espelhamento dentro de pares fixos, permutação dos
pares, espelhamento mais permutação dos pares e permutação de todos os dígitos.
Para famílias de pares, um zero inicial preenche grupos ímpares. O comprimento
original continua na assinatura; o preenchimento é uma hipótese explícita.

A pontuação conta assinaturas compartilhadas que admitem originais diferentes.
Cópias exatas não pontuam como transformação; identidade tem pontuação zero
por construção. Várias variantes da mesma assinatura contam uma vez. Isso não
elimina a ascendência comum dos fragmentos dos livros: os oito conjuntos não
são tratados como amostras semanticamente independentes.

| Família | Relação não idêntica encontrada entre fontes |
| --- | --- |
| Rotação cíclica | `345↔453` |
| Espelhamento dos pares, com ou sem permutação deles | `3478↔4378` |
| Permutação de todos os dígitos | Ambos os pares |
| Identidade, reversão inteira, permutação de pares sem espelhamento | Nenhuma |

Somente Avar/Knightmare apresentam relações não idênticas nessas regras.
O máximo observado é2, na família mais permissiva. Espelhamento de pares
sozinho não explica ambos; rotação cíclica também não.

Executamos9999 sorteios por controle, **29.997 ao todo**, repetindo em cada
sorteio a seleção do máximo entre todas as fontes e famílias.

| Controle | Cauda Avar/Knightmare com anagramas fixados | Cauda do máximo em28 pares×7 famílias |
| --- | ---: | ---: |
| Embaralhar dígitos de cada conjunto, preservando contagens e comprimentos | 0,0003 | 0,0014 |
| Permutação global dos rótulos dos dígitos, independente por conjunto | 0,0004 | 0,0015 |
| Redistribuir grupos inteiros entre posições de mesmo comprimento | 0,0343 | **0,0906** |

As caudas são `(acertos+1)/10000`. No último controle,905 casos têm máximo≥2.
Contagens e histogramas: [round25_structure.json](../results/round25_structure.json).
O último modelo conserva as sequências e suas relações de anagrama, testando
a concentração por fonte. Os outros alteram essas relações. Respondem a
perguntas diferentes, e nenhum deve ser escolhido isoladamente por favorecer
uma conclusão.

**Interpretação:** os pares são incomuns sob dois modelos que alteram dígitos.
A concentração por fonte é menos excepcional quando preservamos as sequências
existentes. Isso limita a interpretação semântica da pista, sem apagar a
relação observada. O máximo corrige apenas esta família finita, não toda a
exploração histórica da comunidade. Não calculamos a probabilidade de469
ter ou não significado.

As previsões estruturais de3478 alcançam apenas4378 nas famílias de
espelhamento dos pares e anagramas completos. `34334` e `486486` não pertencem
à mesma classe; nenhuma regra fornece seus significados. Esses textos também
já estavam expostos. Ordenar dígitos produz uma assinatura, não inglês.

## Decisões delimitadas

| Hipótese | Decisão | Evidência necessária para reabrir |
| --- | --- | --- |
|3478 é nome de criatura | Documentado nas revisões recuperadas; data do evento no jogo ainda não autenticada | Captura ou registro versionado do jogo |
|3478 é ID interno | Suspensa, sem evidência de campo interno | Arquivo/especificação original com procedência |
|3478 codifica BEHOLDER/BONELORD nas regras já testadas | Negativos delimitados das rodadas15/23 mantidos; não repetidos nesta rodada | Erro demonstrado ou regra nova que explique toda a fala e preveja outra mensagem |
|3478 é palavra/conceito invariável a permutações | Não identificada semanticamente | Gloss independente ou previsão semântica nova |
|3478 é senha, período, semente ou parâmetro | Famílias específicas negativas; geradores não especificados suspensos | Algoritmo fixo e previsão discriminante |
|Nomes e matrizes mudaram juntos | Suspensa, depende da rodada26 | Registros comparáveis de nomes, textos e células nas mesmas épocas |

A [rodada15](round15.md) avaliou combinações especificadas de Hill, nomes e3478,
sem tradução validada. A [rodada23](round23.md) concluiu sem chave seis ajustes
lexicais disponíveis que forçavam um nome e exigiam a fala inteira de Knightmare.
Duas avaliações fonéticas de BONELORD estavam indisponíveis por falta de
pronúncia na fonte; isso não rejeita a hipótese fonética. O ajuste livre com
blocos variáveis de letras atingiu limite, como registrado então. Não
transformamos esses resultados em rejeição de qualquer cifra possível.

Encerramos a expansão ativa dessa pista sem novo mecanismo ou fonte. É uma
suspensão operacional, não prova de irrelevância de3478. A hipótese de palavra
pode reaparecer na rodada28 mediante evidência adicional, não por preencher o
poema com lore. A história coordenada segue pendente para a rodada26.

**Candidatas: nenhuma candidata nova; tradução potencial não identificada.**
As propostas inglesas da rodada24 continuam não validadas. Nenhuma saída
inglesa foi atribuída aos anagramas ou à história do nome.

## Reprodução e continuidade

```sh
make round25
python3 -m unittest discover -s tests -v
```

O replay confere manifestos e repete29.997 simulações sem rede. Capturas
históricas ficam locais; a extração está em `scripts/round25_history_audit.py`.
O replay offline verifica seus metadados/resultados publicados sem fingir
recuperar novamente os corpos da API.

Sete testes novos verificam propriedades dos controles, contagem de cópias,
preenchimento e o máximo contra enumeração independente de pares.
**243 testes de software passaram**, sem equivalência com validação semântica.
Replay em cópia temporária sem fontes HTTP: resultados idênticos.

A rodada25 está concluída no escopo de adjudicação previsto. Permanecem cinco
rodadas planejadas,26–30. A próxima adjudica matrizes3×3,4×4 e5×5, preservando
lacunas históricas e sem inventar contagens de caveiras.
