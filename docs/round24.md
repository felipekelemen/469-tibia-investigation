# Rodada 24 — fontes, alegações publicadas e controles independentes

Execução em 19 de novembro de 2026, sobre `2d8aa534765bb38cfb65f433754ed0ae9ff3ff67`.
Primeira rodada executada do [plano revisado](mission_plan_v2.md).
**Resultado da missão: inconclusivo. Nenhuma tradução validada e nenhum gerador
original sem texto autenticado.** A contribuição mais promissora é estrutural:
os pares de anagramas de Avar Tar/Knightmare merecem um teste ampliado.

## Escopo e fontes

Foram feitas **16 consultas distintas**, 14 operações de abertura pela ferramenta
web e 10 GETs diretos. O catálogo possui 28 entradas, das quais 20 tiveram
conteúdo relevante revisado nesta rodada; inclui leitura parcial, texto indexado
e arquivos de repositório, explicitamente diferenciados. Não são 20 testemunhos
independentes. Os limites de 80 consultas/40 documentos eram tetos, não cobertura
prometida. A busca foi encerrada após reproduzir as alegações selecionadas.

Os três repositórios iniciais continuam nos mesmos commits já auditados:

| Fonte | Commit conferido no remoto |
| --- | --- |
| arturoornelasb/tibia-bonelord-469-cipher | `007dcf1707acc9b991642e68bcac08214a5bb38c` |
| s2ward/469 | `4b1c4d3d2b07ed373f4cca44ac1270638614cef5` |
| kimlage/tibia-469-cipher-casestudy | `4d726a8de7af1f2216bd48d9b86165e0c50616b6` |

Reproduzir agora um teste antigo não o torna uma publicação nova. O
[catálogo](../data/round24_sources.json) registra URLs, dependências e limitações;
o [diário de consultas](../data/round24_discovery_log.json) registra buscas e
hashes dos retornos locais da ferramenta. Esses hashes não são hashes das páginas.
Metadados HTTP separados registram os hashes dos corpos realmente recebidos.
Corpos completos e clones ficam locais/ignorados; o código reutilizado tem licença MIT preservada.

Achados de procedência:

- A [entrevista de Chayenne](https://forum.portaltibia.com.br/topic/11420-entrevista-com-chayenne/),
  com data exibida de 15/05/2009, conserva as duas sequências de 36 e 13 dígitos.
  As três ocorrências de cada parte na página são versões/citações da mesma
  resposta, não três mensagens novas. Não há inglês paralelo atestado.
- A [transcrição de Avar Tar](https://tibiasecrets.com/Avar-Tar) conserva os 20
  grupos, incluindo `4378`. Seu comentário sobre o poema não é sua tradução.
- A [página 469 da wiki](https://www.tibiawiki.com.br/wiki/469) contém a fala
  numérica de Knightmare. A página específica do NPC, nesta captura, contém
  o contexto de Excalibug/bonelords, mas **não** a fala numérica. São papéis distintos.
- A [wiki da criatura nostálgica](https://www.tibiawiki.com.br/wiki/Bonelord_(Nostalgia))
  descreve `3478` como nome exibido, registra a versão 9.44/2012 e relata correção
  do nome em 2023. Isso não demonstra um ID interno nem uma equivalência lexical
  universal. A cronologia ainda requer fontes versionadas.
- A [entrevista de Knightmare no Rookie](https://rookie.com.pl/blogs/890/interview-with-knightmare)
  foi lida no texto indexado: o GET direto recebeu somente a estrutura JavaScript.
  O criador discute ambiguidade deliberada e mistérios que ganharam interpretações
  posteriores. A resposta à pergunta que cita 469 não fornece algoritmo nem
  afirma especificamente que 469 seja desprovido de texto. A notícia oficial
  que divulga a entrevista ficou acessível somente como resultado indexado.
- A [fórmula de Honeminas](https://www.tibiawiki.com.br/Honeminas_Formula) confirma
  `(4,3,1,5,3).(3,4,7,8,4)`. O produto escalar convencional é **83**. Isso corrige
  o uso de variantes em resumos secundários, mas não define um decoder. O título
  inicialmente tentado, `Mathemagics_(Book)`, era uma URL presumida e retornou404;
  isso não foi interpretado como inexistência do livro.
- Reimpressões de entrevistas, uma citação sobre solvabilidade/primos e vídeos
  permanecem com lacunas de procedência. Vídeos encontrados não foram assistidos
  nem tiveram transcrição recuperada. A busca não acrescentou um novo registro
  histórico autenticado de todas as células de Hellgate; permanece a auditoria
  qualificada da [rodada14](round14.md).

## H97 — anagramas entre Avar Tar e Knightmare

Uma [postagem comunitária](https://www.reddit.com/r/TibiaMMO/comments/1u1i3ag/avar_tars_469_poem_seems_to_contain_scrambled/)
aponta `3478↔4378` e `345↔453`, e relata simulação aproximadamente1em10000.
Não foram disponibilizados no texto lido código, semente e definição suficiente
para reproduzir exatamente essa probabilidade. Executamos um teste próprio.

O [protocolo](../data/round24_anagram_protocol.json) e o
[manifesto](../data/round24_anagram_manifest.json) foram congelados **depois de
conhecer os exemplos publicados e antes dos cálculos novos**. Portanto, não é
descoberta cega nem teste confirmatório previamente registrado em relação aos dados.

Confirmamos os dois pares em grupos inteiros. Em Avar Tar, `4378` e `453` são
os grupos15 e16 e estão adjacentes através da pontuação. A estatística ampliada
conta todas as assinaturas distintas dos grupos de Knightmare com pelo menos
três dígitos, não apenas os dois pares destacados. Não usamos interpretação inglesa.

Cada controle teve 99.999 sorteios, sementes fixas e as mesmas estatísticas:

| Controle | Cauda: ambos os pares nomeados, em qualquer posição | Cauda: pelo menos2 assinaturas Knightmare | Cauda: pares nomeados adjacentes |
| --- | ---: | ---: | ---: |
| Embaralhar dígitos de Avar, conservando comprimentos e contagens totais | 5/100000 | 31/100000 | 1/100000 |
| Embaralhar vocabulário distinto e recolocar as palavras repetidas | 6/100000 | 15/100000 | 2/100000 |
| Permutar globalmente os rótulos dos dígitos de Avar | 7/100000 | 9/100000 | 7/100000 |

As frações usam correção Monte Carlo `(acertos+1)/(sorteios+1)`; não são as
contagens brutas. Os acertos brutos estão no [resultado completo](../results/round24_anagram.json).
O segundo controle conserva repetições e frequências do vocabulário distinto,
mas não necessariamente as frequências ponderadas por ocorrência. O terceiro
conserva toda a estrutura de igualdade e repetição, mas troca as frequências
atribuídas aos dígitos específicos. Nenhum é um modelo completo da autoria de469.

Sob o primeiro modelo, há somente uma posição adjacente de comprimentos4/3.
O cálculo hipergeométrico exato dá `0,0000082248085` para os dois multiconjuntos
nomeados nessa posição. Uma enumeração independente de pequenos exemplos
valida a fórmula. Não multiplicamos probabilidades de posições como se fossem independentes.

Embaralhar apenas dentro de cada palavra preserva essas estatísticas por
definição: cauda1. Trinta verificações confirmam a invariância. Esse controle
não discrimina intenção semântica.

**Decisão:** sinal estrutural retrospectivo que merece acompanhamento.
Não estimamos a chance global de achar *alguma* coincidência entre todas as
teorias, operações, textos e posições já examinados pela comunidade. Seleção
prévia, possível cópia e escolha da família de testes impedem interpretar esses
números como probabilidade de a linguagem ter significado. Também não demonstram
que os pares sejam a mesma palavra. Não há inglês produzido por este teste.

## H98 — tabela comunitária de frases

Reimplementamos literalmente a tabela de13 entradas do
[relatório de kimlage](https://github.com/kimlage/tibia-469-cipher-casestudy/blob/4d726a8de7af1f2216bd48d9b86165e0c50616b6/docs/469_final_report.md).
O próprio relatório qualifica os significados como propostas comunitárias,
não confirmadas pela CipSoft. Sete entradas são reconstruções documentais
associadas à frase de Knightmare. O banco SQLite original não foi executado.

| Entrada canônica | Saída literal da tabela publicada | Após retirar todas as atribuições da própria fonte |
| --- | --- | --- |
| `653768764!` | `look at you` | nenhum parse completo |
| `659978 54764!` | `let me see you` | nenhum parse completo |
| `3478 67 90871 97664 3466 0 345!` | `be a wit than be a fool` | nenhum parse completo |

Cada entrada tem um único parse com a tabela completa e os espaços preservados.
Somente `764` tem um significado proposto compartilhado por duas fontes; as
outras atribuições necessárias não transferem. Não corrigimos silenciosamente
a frase de Knightmare para uma máxima inglesa mais natural.

Em999 permutações dos rótulos ingleses entre os13 códigos, **2997/2997**
avaliações continuam segmentáveis e iguais à sua própria saída. Trata-se de
uma demonstração independente da circularidade desse critério, **não** de
execução do gate SQL original nem de uma medida de fluência dos controles.
O inglês embaralhado não passa em uma avaliação semântica; justamente essa
avaliação independente está faltando.

Essas três saídas foram escolhidas por serem as três alegações do código
publicado, não por maximização de pontuação. A chave completa está em
[phrase_claims.json](../data/round24_reference/phrase_claims.json), o parser em
[round24_claim_audit.py](../scripts/round24_claim_audit.py), e a reprodução em
`make round24`. Elas continuam **saídas de uma tabela proposta, sem validação de tradução**.
Para promoção, seria necessário fixar a regra e prever um significado atestado
em outra mensagem que não forneceu suas próprias atribuições. Nenhum teste
desta rodada encontrou esse par.

A [discussão2 do repositório arturo](https://github.com/arturoornelasb/tibia-bonelord-469-cipher/discussions/2)
também propõe um hino de Avar com sentidos inferidos para raízes e afixos.
A leitura inicial alegada é `Behold the greatness!`. Não a reproduzimos como
saída de algoritmo: nos trechos revisados faltam regra completa, escolha
unívoca de unidades e texto reservado com tradução independente. A alegação
permanece externa; a proximidade com a lore não valida suas palavras.

**Nenhuma candidata nova a tradução foi gerada nesta rodada.**

## H99 — compressão e a hipótese de origem sem texto

Inspecionamos o script público `c2_generative_mdl.py` e executamos somente
suas funções `tile`, `gamma_bits` e `two_part_module_code`, extraídas sem
modificação pela AST. Não executamos suas consultas SQL, comparações restantes
ou o banco de cerca de1GB. O snapshot e sua licença estão em
[round24_reference](../data/round24_reference/).

Com os70 livros canônicos em ordem numérica, reproduzimos:

- **62 módulos**, inventário com4464 dígitos;
- cobertura de9180/11263 dígitos por cópias e2083 dígitos literais;
- **24.627,84616864669 bits** pelo custo idealizado publicado;
- reconstrução exata de70/70 livros, conferida por serializer/decoder próprios;
- o custo recalculado independentemente coincide com o original.

O tamanho é estimativa em bits, com referências de custo fracionário; não é
um arquivo comprimido empacotado de exatamente esse tamanho. O inventário e
os literais foram extraídos dos próprios alvos. Reconstrução não é previsão
de texto novo nem recuperação da ferramenta usada pelos autores do jogo.

O [protocolo complementar](../data/round24_claim_protocol.json) foi congelado
antes da execução. Aplicamos o mesmo procedimento a controles:

| Conjunto | Dígitos | Módulos | Bits estimados | Reconstrução |
| --- | ---: | ---: | ---: | ---: |
| Livros reais | 11263 | 62 | 24627,85 | 70/70 |
| Mensagens inglesas conhecidas, ASCII decimal de3 dígitos | 15225 | 8 | 6410,15 | 70/70 e inglês exato |
| As mesmas mensagens, dígitos embaralhados dentro de cada mensagem | 15225 | 0 | 51920,36 | 70/70 |
| Dígitos uniformes nos comprimentos dos livros reais | 11263 | 0 | 38736,88 | 70/70 |

O controle positivo usa oito frases sintéticas originais combinadas numa regra
fixa e repetidas para formar70 mensagens; não pretende imitar estatisticamente
os70 livros distintos. É um contraexemplo deliberadamente simples à inferência
de que *ser reconstruível por cópias/literais* implica *não conter inglês*.
A ausência de módulos nos controles embaralhados diz respeito ao limiar20,
não à inexistência de qualquer repetição curta.

Relatórios posteriores do próprio upstream também distinguem compressão de
explicação de origem. O experimento de remoção de fonte permanece não promovido;
o programa exato de fita externa conserva sementes, literais e informações
de cópia. A revisão registrou essas ressalvas, evitando resumir o repositório
inteiro pela alegação mais forte de um relatório anterior.

**Decisão:** compressão reproduzida; inferência de ausência universal de texto
rejeitada. A hipótese de produção não textual permanece aberta e exige evidência
de origem ou um modelo com previsões discriminantes, como previsto na rodada29.

## Decisões e continuidade

| Frente | Estado após esta rodada | Próximo teste |
| --- | --- | --- |
| Avar/Knightmare | Anagramas confirmados, sentidos desconhecidos | Congelar operações e comparar todas as famílias elegíveis, contabilizando seleção e cópia |
| Chayenne | Transcrição36+13 reconferida, nenhum gloss | Manter partes e dependências dos livros; não usar os espelhos como reservado |
| 3478/BEHOLDER/BONELORD | Nome contextual corroborado por wiki; chave e equivalência lexical não demonstradas | Rodada25 separará nome, código de palavra e chave; buscar fontes versionadas |
| Matrizes3×3/4×4/5×5 | Nenhuma nova chave física autenticada nesta rodada | Rodada26 conserva as restrições históricas e os resultados negativos anteriores |
| Solvabilidade/não textual | Sem decisão global | Buscar previsões novas; não converter compressão, citações indiretas ou lore em prova |

Há **seis rodadas previstas restantes,25–30**. Isso é uma sequência de trabalho,
não uma promessa de que seis rodadas resolvam o mistério. Uma candidata que
produza previsões verificáveis antecipa a validação independente.

## Reprodução e verificação

```sh
make round24
python3 -m unittest discover -s tests -v
```

O replay é offline: confere os manifestos, repete299.997 sorteios, reproduz
as quatro condições de compressão, os testes de frases e compara os resultados
salvos. Não baixa páginas nem executa código de rede do upstream. A conferência
opcional dos corpos HTTP locais usa `python3 scripts/round24_context_audit.py`;
esses corpos não são distribuídos. Novas capturas precisam de outro nome de
batch e não sobrescrevem as originais.

**236 testes de software passaram**, incluindo7 novos: probabilidades comparadas
com enumeração completa de exemplos pequenos, fronteiras de anagramas e parsing,
reconstrução independente, custo com zero módulos e exclusão de scriptsHTML.
Isso verifica implementação, não qualifica um decifrador. Replay offline em
cópia temporária sem os clones/fontes HTTP: concluído com resultados idênticos.

Os protocolos e resultados anteriores, inclusive o estado congelado da rodada8,
foram preservados. O estado atual fica em
[plan_progress_round24.json](../data/plan_progress_round24.json) e as hipóteses
H97–H100 em [hypotheses.json](hypotheses.json). O commit desta rodada e sua
publicação são identificáveis pelo histórico Git; não há alegação de solução.
