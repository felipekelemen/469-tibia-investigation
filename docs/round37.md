# Rodada 37 — origem e teste das associações de Knightmare

**Resultado: inconclusivo. Nenhuma nova tradução validada.** Esta rodada segue
os alvos `345` e `90871` identificados na R36, sem reabrir a busca M1 reprovada
na R35. Foram rastreadas três associações publicadas e executadas verificações
exatas, mantendo separadas as regras de dígitos e de pares numéricos.

O texto analisado permanece `3478 67 90871 97664 3466 0 345!`.
Nenhuma palavra foi aceita como resposta correta fornecida pelos autores do jogo.

**Fontes e atribuição.** A busca limitada usou 12 consultas, 13 operações de
página e nove tentativas HTTP. As consultas não repetem literalmente as 83
inventariadas nas R24, R26, R31, R32 e R34. Isso evita repetição de consultas,
não torna as fontes independentes nem demonstra exaustão da internet.
Dos nove HTTPs, quatro falharam por conexão, quatro retornaram 403 e um, 200.
Algumas páginas foram legíveis pelo conector de busca apesar do bloqueio HTTP.

- Um [comentário de TibiaBR](https://forums.tibiabr.com/threads/444776-Misterios-de-Knightmare/page4),
  com data exibida de 22/01/2012, associa `345` a **knowledge**, citando uma
  imagem de exemplo de outro participante. Somente o trecho indexado foi
  recuperado; a página completa, a imagem e sua procedência continuam ausentes.
  Vários URLs de resultados apontam para a mesma discussão. Não são confirmações
  independentes, e a data exibida não equivale a uma captura arquivada em 2012.
- **Wit** e **fool** aparecem na leitura ajustada do
  [artigo comunitário de Antonio Stradivarius](https://www.tibiasecrets.com/article160),
  com data exibida de 06/05/2024. A proposta já foi auditada na R24. A R37
  explicita suas escolhas de transformação; não a apresenta como descoberta nova.
  O link do artigo para o fórum de Tibia retornou 403. Estar em um fórum no
  domínio oficial tampouco transforma uma postagem comunitária em tradução autoral.
- O [relatório final de kimlage](https://github.com/kimlage/tibia-469-cipher-casestudy/blob/4d726a8de7af1f2216bd48d9b86165e0c50616b6/docs/469_final_report.md)
  identifica as sete entradas de Knightmare como reconstrução documental e
  reconhece que seus testes de significado comparavam a proposta consigo mesma.
  Não fornece confirmação independente de CipSoft. Não adotamos sua conclusão
  universal de inexistência de tradução dos livros.
- O [inventário comunitário no Reddit](https://www.reddit.com/r/TibiaMMO/comments/g3b9g8/469_bonelord_language_vocabulary/)
  lista `345` e `90871` sem significados. A página de linguagem do WordPress
  e outra discussão de Mathemagics não forneceram a correspondência procurada.

Os URLs, níveis de acesso e classificações estão em
[round37_sources.json](../data/round37_sources.json). Capturas integrais ficam
fora da publicação; seus hashes e parâmetros estão no
[registro de descoberta](../data/round37_discovery_log.json). Hashes verificam
integridade, não autoria nem veracidade. Não houve contato com terceiros.

**Teste por dígito.** Mantivemos a família R33/R36: cada dígito observado emite
sempre a mesma unidade de uma a três letras; cada grupo precisa formar uma
palavra do léxico CMU fixado, com a adição hipotética de BONELORD. Há 122.368
formas. O dígito `2` não aparece e continua sem emissão determinada.

| Associação hipotética | Chaves para a fala inteira | Conclusão nesta família |
|---|---:|---|
| `345 → KNOWLEDGE` | 0 | Incompatível com o conjunto lexical fixado |
| `345 → FOOL` | 3.976 | Compatível e ainda ambígua |
| `90871 → WIT` | 0 | Cinco emissões não vazias não produzem três letras |

Três execuções novas do contador da R33 concordaram com as marginais da R36.
Para KNOWLEDGE, a única divisão possível é `3=KNO`, `4=WLE`, `5=DGE`.
Assim, `3466` precisaria produzir `KNOWLE` seguido de duas cópias da mesma
unidade de uma a três letras; nenhuma forma do léxico atende à condição.
Esse resultado depende da regra e do léxico. Não proíbe que um código de
palavra inteira, ou outro mecanismo, associe `345` a knowledge.

Também consultamos as contagens exatas dos cinco embaralhamentos internos de
palavras previamente fixados na R36. As três associações deixam zero chaves
nesses controles, enquanto FOOL deixa 3.976 na fala real. Essa diferença é
descritiva: os controles já estavam expostos, a palavra veio de interpretação
posterior à observação do texto e são apenas cinco casos. Não calculamos
p-valor nem alegamos descoberta de significado. O protocolo desse diagnóstico
foi fixado depois do resultado real e antes de consultar as contagens condicionadas.

**Teste por pares.** Extraímos a tabela e as expansões da representação do
artigo fornecida pelo conector e conferimos os valores usados no código.
A regra acrescenta um zero à esquerda dos grupos de comprimento ímpar.
A aplicação literal produz:

```text
BE A TIV TAN BE * VF
```

A leitura ajustada proposta no artigo é:

```text
BE A WIT THAN BE A FOOL
```

Enumeramos todas as expansões relevantes, mantendo os limites entre palavras:

| Operações permitidas | Sequências distintas | Contém a leitura ajustada? |
|---|---:|---|
| Ordem preservada, expansões por ocorrência | 22.464 | Não |
| Permutação dos símbolos de cada palavra, depois expansões por ocorrência | 6.469.632 | Sim |

Na segunda regra, `TIV` é reordenado como `VIT`, usando `V=W`, e `VF` passa
a `FV`, usando `V=OOL`. Para THAN, `T=TH`; para WIT, `T=T`. O curinga recebe A.
Essas escolhas dependem da ocorrência; não constituem uma emissão global fixa.
As contagens são produtos de conjuntos de palavras possíveis em cada posição,
com espaços fixos. Não contam frases gramaticais, probabilidades de significado
ou chaves criptográficas uniformemente distribuídas.

O artigo permite explicitamente anagramas. Portanto, a falha da versão que
preserva a ordem **não refuta toda a proposta**. A versão relaxada reproduz
a frase escolhida entre muitas saídas, sem uma regra de seleção previamente
fixada ou transferência demonstrada para mensagens de significado reservado.
Permutamos os símbolos antes de expandir, mantendo os blocos expandidos intactos;
outras definições de anagrama podem permitir ainda mais saídas.

As associações WIT e FOOL continuam sendo uma conjectura comunitária conhecida,
não uma nova candidata obtida por esta rodada. A hipótese de código de palavras
inteiras não foi refutada pela falha do modelo de dígitos.

**Reprodução e limites.** `make round37` verifica hashes, refaz a enumeração
de expansões e consulta os seis censos fixados. `make round37-full` também
recompila o contador e repete as três contagens condicionadas. Os testes novos
cobrem zeros à esquerda, limites de palavras, ordem versus anagrama, saídas
duplicadas, curinga explícito e comparação das partições com enumeração
independente de chaves pequenas. Os resultados detalhados estão em
[round37_claim_checks.json](../results/round37_claim_checks.json) e
[round37_controls.json](../results/round37_controls.json).

O replay em cópia pública, sem fontes privadas nem rede, é registrado em
[round37_clean_replay.json](../results/round37_clean_replay.json).
As três contagens novas foram repetidas; os 337 testes passaram e nenhum dos
977 arquivos do snapshot foi alterado. As auditorias do encerramento v3 e
da publicação R36 também passaram. Isso confere reprodução no mesmo ambiente,
não revisão por uma instituição externa.

O ciclo v3 permanece encerrado com resultado **I**. Esta busca complementar não
encontrou evidência suficiente para T (tradução) ou G (processo original sem
texto). Avar Tar, Chayenne, 3478 e as matrizes não receberam evidência nova nesta
rodada. O próximo avanço útil depende de recuperar a imagem e sua procedência,
obter um par autoral verificável ou especificar um mecanismo novo que passe por
qualificação antes de ser ajustado às mensagens. Repetir a frase conjecturada
como verdade de treinamento não atende a esse requisito.
