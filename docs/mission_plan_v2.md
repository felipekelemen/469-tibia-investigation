# Plano de missão v2 — revisão após 23 rodadas

Revisão de 17/11/2026, baseada no commit
`d0f50399b3bcc2b77e151ac431a181ea1e881ddd` e nos sete pontos solicitados pelo usuário.
Este passa a ser o plano de execução atual. O [plano inicial](next_experiments.md)
e os protocolos/resultados anteriores permanecem como histórico.
O [balanço das 23 rodadas](rounds_01_23_review.md) identifica o que aproveitar,
o que não repetir e os limites de cada conclusão. Esta revisão **não é a
rodada 24 executada** e não contém uma nova pesquisa exaustiva da web.

## Missão e três desfechos admissíveis

O objetivo principal continua sendo obter um **algoritmo reproduzível que receba
os dígitos originais e produza texto inteligível, preferencialmente inglês,
com previsões verificáveis em conteúdo não usado para inventar a regra**.
“Fórmula” inclui um procedimento com estados, regras e chave especificados;
não exige uma única expressão algébrica. Outra língua só entra como hipótese
explícita, com os mesmos controles e com avaliação linguística adequada.

Há duas linhas de investigação e um desfecho necessário para resultados ainda
insuficientes:

| Desfecho | Evidência exigida | O que não basta |
| --- | --- | --- |
| T — tradução demonstrada no escopo declarado | Regra integral congelada, saídas literais coerentes, previsão em conteúdo distinto, validação externa e reprodução por outra implementação | Palavras isoladas, boa pontuação, anagramas, frases inventadas a partir da lore, recuperar o próprio exemplo usado para escolher a chave |
| G — origem sem texto documentada no escopo declarado | Evidência autenticada do processo autoral/gerador daquela versão e fonte, mostrando que os números foram produzidos sem mensagem textual de entrada; reprodução do mecanismo quando disponível | Fracasso de cifras, bom compressor, cópias, uma opinião comunitária ou um gerador novo que apenas memorize o corpus |
| I — inconclusivo / não identificável com os dados atuais | Registro do que foi excluído, das lacunas de fonte, ambiguidades e limites computacionais | Forçar a escolha T/G só porque já fizemos muitas rodadas |

Não podemos provar que **nenhuma função possível** converta um conjunto finito
de números em frases: uma tabela arbitrária sempre pode atribuir frases a
sequências distintas. Essa tabela não descobriria a linguagem do jogo. A meta
negativa verificável é investigar a origem e excluir classes de mecanismos
especificadas, não prometer uma impossibilidade matemática universal.

Também não confundiremos “sem texto codificado” com “sem utilidade no jogo”:
os números ainda poderiam ter função narrativa, estética, de identificação
ou de interação. E uma fala pode ter significado enquanto certos livros são
montados decorativamente. A conclusão precisa indicar fonte, época e alcance;
não presumimos um único sistema nem sistemas necessariamente diferentes.

**Estado atual: I.** Nenhuma tradução foi validada e a origem não textual
não foi demonstrada. A falta de autenticidade/independência de fontes e as
falhas de recuperação em positivos continuam obstáculos reais.

## Como os sete pedidos entram no plano

| Pedido | Entrega e decisão |
| --- | --- |
| 1. Demonstrar uma fórmula de tradução | R27 qualifica recuperação; R28 procura tradução nos alvos; R30 congela previsões e replica o resultado |
| 2. Investigar ausência de texto | R24 procura evidência autoral; R29 compara geradores com/sem mensagem; R30 distingue origem documentada de mera preferência estatística |
| 3. Absorver lore e pesquisas publicadas | R24 cria um registro rastreável de alegações/fontes e reprodução de métodos; toda rodada registra atualizações pertinentes |
| 4. Priorizar Avar Tar, Knightmare e Chayenne | Os três são os alvos de R24/R28; R25 também usa Knightmare e Avar; os livros só validam transferência quando houver um mecanismo candidato |
| 5. Confirmar ou encerrar 3478/nomes | R25 entrega decisões separadas para tradução do nome, identificador de entidade, chave e ligação histórica |
| 6. Confirmar ou encerrar matrizes | R26 entrega decisão por dimensão, procedência e mecanismo; encerra buscas redundantes e suspende as sem dados |
| 7. Compartilhar hipóteses e traduções potenciais | Relatório obrigatório por rodada, com saída literal, derivação, controles, incerteza e motivos para manter/descartar cada candidata |

## O que mudou de prioridade

A pesquisa já tem infraestrutura, corpus e 23 lotes executados. Não reiniciar
por reprodução genérica dos 5.729 símbolos, Hill, Vigenère com os nomes ou
novos períodos sem justificativa. A prioridade é **informação que discrimine
hipóteses e permita validar os três textos**, seguida da capacidade de recuperar
o mecanismo correto. Mais variações de uma chave não substituem esses requisitos.

As frentes originais permanecem, mas “lote executado” não significa objetivo
científico resolvido:

| Frente original | Situação nesta revisão | Onde continua |
| --- | --- | --- |
| P01 fontes/validação | Inventário e dependências disponíveis; falta referência semântica independente suficiente | R24, R28, R30 |
| P02 capacidade do solver | V4 qualificada só no cenário com tokens fornecidos; aprendizado bruto e solver da R23 não qualificados | R27 |
| P03 módulos/geradores | Regularidades medidas; intenção e poder de previsão fora dos motivos ajustados não estabelecidos | R29 |
| P04 busca/tradução | Buscas executadas; sucesso semântico não atingido | R28, R30 |
| P05 palavras/conceitos | Associações e fronteiras continuam hipóteses | R24, R25, R27, R28 |
| P06 história das caveiras | Evidência documental parcial; transição e contagens completas não autenticadas | R24, R26 |
| P07 algoritmos matriciais | Famílias finitas examinadas; nenhuma chave real demonstrada | R26 e, apenas se elegível, R28 |

As “quatro pendências” do quadro histórico eram entregas principais de P01,
P03, P05 e P06. Não significavam que P02/P04/P07 estavam resolvidas nem que
faltavam quatro rodadas. Agora há **sete blocos de trabalho propostos** abaixo,
com dependências e critérios de saída. Não há prazo ou número garantido de
rodadas até uma tradução. Os números R24–R30 são a sequência proposta, ainda
não executada; correções de software, por si, não justificam inflar a contagem.

## R24 — consolidar fontes, lore e alegações de solução

**Pergunta:** que evidência nova poderia distinguir os mecanismos e confirmar
uma leitura das três falas? Não basta coletar versões da mesma teoria.

Revisar os três repositórios iniciais nos commits publicados e suas mudanças,
issues/discussões, artigos de TibiaSecrets, Tibia Wiki BR e inglesa, entrevistas,
notícias oficiais, fóruns, vídeos e arquivos históricos. Buscar em português e
inglês; seguir as fontes alemãs/polonesas quando forem a origem de uma alegação.
Não substituir uma fonte primária indisponível por um resumo sem marcar a lacuna.

A coleta inicial terá até 80 consultas distintas e leitura de até 40 documentos
priorizados; é um lote de descoberta, não uma declaração de cobertura total da
internet. Consultas que só repetem espelhos serão deduplicadas. Uma segunda
passagem seguirá as referências primárias, datas e códigos citados. Novos lotes
serão motivados por lacunas ou pistas registradas, não pela repetição indefinida
dos mesmos resultados. Em cada lote, publicar cobertura, buscas infrutíferas,
fontes bloqueadas e o que ainda não foi lido.

O registro de fontes cobrirá ao menos estas classes, mesmo quando o resultado
for “não recuperado”:

1. Avar Tar: diálogo completo, gatilho, poema literal, pontuação, comentário
   inglês posterior, variantes por versão e proveniência. O comentário não é
   presumido como tradução do poema; `4378` não pode virar `3478` por conveniência.
2. Knightmare: distinguir a fala do NPC da autoria/entrevistas do desenvolvedor,
   contexto de evento e versão. Preservar os sete grupos e o zero isolado.
3. Chayenne: pergunta e resposta completas, idiomas, emoticons, transcrição
   original e espelhos. As partes de 36 e 13 dígitos já aparecem 11 e nove vezes
   nos livros; não serão reutilizadas como validação cega desses livros.
4. 3478: rótulo da criatura de nostalgia, datas e correções do nome, versus
   hipótese de palavra inglesa ou de identificador interno. A existência de um
   rótulo visível não autentica um ID de implementação.
5. Wrinkled Bonelord, Elder Bonelord e Evil Eye: falas, 486486, referência a
   Tibia como 1, tabu do zero e fórmula dependente do observador. Contexto de
   entidades não fornece automaticamente uma substituição de letras.
6. Honeminas: expressão integral, vetores, variantes de transcrição e o sentido
   atribuído às variáveis. O produto escalar literal 83 já foi calculado; não
   fornece sozinho um decodificador. Não selecionar erros de transcrição por
   produzirem a resposta desejada.
7. Hellgate: objetos da sala, pilhas ocultas, dimensão e orientação, capturas,
   gravações, notícias de renomeação e possível mudança dos livros.
8. Alegações técnicas: código executável, tabelas propostas, traduções
   publicadas e testes de cada autor, incluindo limitações admitidas por ele.

Cada entrada terá URL/commit/revisão, autoria atribuída, citação/contexto,
data da publicação/captura/versão separadas, bytes/hash quando disponíveis,
linhagem entre espelhos, alegação, reprodução já feita e restrição testável.
Vídeos usarão timecodes e trechos conferidos; título ou resumo automático não
será evidência de uma cena não vista. Material alterado ou de autenticidade
incerta fica separado do corpus canônico.

Priorizar a reprodução dos métodos publicados que tenham especificação e
previsões realmente novas. Rodar o programa original e uma checagem independente;
verificar se usa o próprio codebook como “verdade” ou deixa tabelas de tradução
manuais escondidas. O registro distinguirá “reproduz o programa”, “reproduz a
alegação numérica” e “valida o significado”. Não inventar um algoritmo para um
autor que publicou apenas uma interpretação.

**Saída:** catálogo de fontes/alegações e corpus de contextos dos três alvos;
para cada hipótese, qual dado a apoiaria ou refutaria. Falta de fonte vira
pendência explícita. Esta rodada não precisa produzir uma tradução para ser útil.

## R25 — decisão sobre 3478, BEHOLDER e BONELORD

Separar quatro hipóteses que antes podiam ser confundidas:

| Hipótese | O que já sabemos | Teste/critério de encerramento |
| --- | --- | --- |
| 3478 codifica literalmente a grafia inglesa | Dígrafos da R15 e seis ajustes disponíveis da R23 não explicam Knightmare inteiro nas regras registradas | Auditar o catálogo finito já executado; testar apenas regra nova especificada por R24 e com previsões fora do exemplo |
| 3478 é rótulo de entidade | Há uso documental como nome da criatura; isso não é tradução de cada dígito | Autenticar contexto/época e prever usos independentes. Sem equivalências adicionais, registrar “rótulo, significado lexical não identificado” |
| 3478 é chave, semente ou parâmetro | Chave periódica de período quatro e combinações matriciais específicas já foram examinadas | Uma semente sem gerador definido não é hipótese executável; suspender sem expandir arbitrariamente o algoritmo |
| A troca de nome exige troca coordenada da matriz/cifra | Coincidência histórica ainda não demonstrada | Comparar nomes, objetos e textos nas mesmas épocas; depende de R26 e não pode ser assumida ao ajustar chaves |

Se surgir regra elegível, congelar antes do teste: interpretação do inteiro
ou dos dígitos, segmentação, chave, vocabulário, parâmetros e saída esperada.
Usar a fala inteira de Knightmare e verificar previsões para `4378`, `34334`,
`486486` e outros contextos, sem corrigir os números. Essas amostras já são
expostas; consistência nelas não equivale a significado externo confirmado.
Se parte da chave faltar, a saída mantém lacunas. Falta de pronúncia de BONELORD
na fonte da R23 é dado indisponível, não rejeição fonética do nome.

**Saída obrigatória:** tabela de decisões por sub-hipótese: confirmada no escopo,
refutada no escopo, inconclusiva por limite, ou suspensa por falta de evidência.
Sem mecanismo novo ou previsão apoiada, encerrar a busca ativa desta pista.
Reabrir apenas com fonte autenticada nova, erro demonstrado ou previsão distinta;
não encerrar falsamente a possibilidade abstrata de alguma relação desconhecida.

## R26 — decisão sobre matrizes de Hellgate

Separar **objeto histórico**, **dimensão** e **função criptográfica**. Testar
3×3, 4×4 e 5×5 não significa possuir três chaves físicas autenticadas.

- 3×3: o bloco relatado `111/136/114` tem determinante 6; é evidência parcial
  da disposição, não confirmação de que a chave inteira tenha essa dimensão.
- 4×4: as duas tabelas fornecidas têm determinantes −7 e −18. A segunda não
  é chave Hill reversível no domínio completo módulo 26; módulo 29 já foi
  testado. O determinante −18 não resolve as pilhas duvidosas.
- 5×5: não há 25 contagens autenticadas. Matrizes construídas a partir de nomes
  já foram ensaiadas, mas não são medições de Hellgate. Não preencher as bordas
  desconhecidas escolhendo números que melhorem o inglês.

Fechar primeiro a cronologia com fontes de objetos/capturas e versões, quando
recuperáveis: a tabela antiga foi arquivada em 2008; relatos atribuídos a 2009
ou abril de 2010 descrevem alteração antes da renomeação de agosto de 2010,
mas não autenticam integralmente a mudança. Distinguir data do post, upload,
captura, edição e patch. A notícia geral de atualização de dezembro não data
as caveiras. Minimapas e sprites não fornecem por si os objetos colocados.

O lote histórico buscará as lacunas já identificadas, incluindo a gravação
candidata, versões de imagens e relatos com quantidades observáveis. Se o acesso
ou a contagem continuarem impossíveis, concluir “dados insuficientes” e suspender
esta tarefa até surgir material verificável. Não chamar ausência de captura
de refutação da matriz.

Na parte matemática, consolidar o catálogo de Hill, leituras/permutação,
funções aritméticas e senhas já testadas nas R1–3/R15. Só admitir uma nova
família se especificar entrada, módulo, orientação, estado, tratamento da cauda
e relação prevista entre as duas tabelas antes de ver sua saída em inglês.
Honeminas ou “observador” só justificam uma família quando fornecem restrições
operacionais, não qualquer função que possamos inventar.

Cada família nova precisa de positivos compatíveis e matrizes-controle que
preservem dimensão e propriedades pertinentes. Se alegar que a mudança da
matriz corresponde à troca do nome, prever conjuntamente o efeito sobre o nome
e sobre outros textos/épocas; apenas acertar BEHOLDER/BONELORD não basta.
Comparar também versão sem matriz: uma camada sem poder preditivo adicional
não ganha crédito por usar as caveiras.

**Saída obrigatória:** decisão separada para história, cada grade observada e
cada mecanismo. Encerrar as famílias enumeradas negativas; suspender 5×5 física
ou outras variantes sem dados. Não prolongar a busca por offsets, bordas e
sementes não motivados. Uma conclusão global “a sala não é uma chave” exige
mais evidência que a rejeição dessas famílias.

## R27 — qualificar recuperação e distinguir ambiguidade de falta de cálculo

A R23 preservou a partição verdadeira em 120 testes locais, mas suas 40 buscas
com chave escondida atingiram o limite de 2.000 estados sem recuperar a chave
verdadeira. As 1.769 chaves lexicais de Knightmare não são um tradutor qualificado.
A primeira melhoria deve ser medida em controles, antes de novo ajuste ao jogo.

Construir um benchmark que separe:

- Forma/segmentação fornecida: verifica o enumerador, sem reivindicar descoberta.
- Chave escondida e inventário conhecido: variar quantidade de contextos,
  unidades observadas, homófonos, nomes e comprimentos próximos das três falas.
- Fronteiras e/ou vocabulário escondidos: qualificação própria; não herdar o
  sucesso de uma condição mais fácil nem reativar o método reprovado da R17.

Incluir casos deliberadamente ambíguos, dígitos não vistos e palavras fora do
léxico; exigir abstenção e alternativas explícitas. Nos controles identificáveis,
observar todos os dígitos no ajuste e criar combinações distintas no teste.
Isso será uma condição de benchmark, não uma alteração das falas reais.
Separar textos/autores de desenvolvimento e qualificação; listas condicionadas
a um dicionário não substituem prosa nem validação de vocabulário aberto.

Preservar como regra operacional o alvo do plano inicial: ao menos 30 casos
por cenário relevante, com pelo menos 27 alcançando 95% de recuperação do texto
reservado. Congelar a unidade de avaliação, métricas de fronteira, cobertura,
critério de consenso/abstenção e orçamento antes de abrir os novos casos.
Relatar também a recuperação exata e leituras erradas. Um acerto médio não
compensa fracasso no cenário que será usado na mensagem real.

O benchmark não obriga uma única tecnologia. Comparar um método melhorado com
o anterior sob orçamento declarado; usar certificados exatos em instâncias
pequenas para separar múltiplas soluções legítimas de falha de busca. Um escore
de modelo de linguagem pode ordenar saídas se for congelado e controlado, mas
não pode reescrever o texto decodificado ou fabricar palavras faltantes.

**Saída:** método elegível por cenário, ou falha documentada. Se não qualificar,
R28 só recebe métodos já qualificados em seu próprio escopo. Demonstrações
algébricas e certificados completos de incompatibilidade continuam admissíveis
como tais; buscas heurísticas negativas não fecham famílias desconhecidas.

## R28 — tradução das três falas, com regras fixadas

Avar Tar, Knightmare e Chayenne têm prioridade conjunta; começar pela instância
em que R24/R27 trouxerem maior capacidade de discriminação, registrando a razão.
Não escolher a ordem porque já vimos uma palavra que gostaríamos de obter.

| Alvo | Estratégia permitida | Condição contra autoengano |
| --- | --- | --- |
| Avar Tar | Confrontar o poema inteiro e fragmentos separados; testar enquadramentos motivados e estrutura poética como hipótese auxiliar | Preservar `4378`, repetições, pontuação e lacunas; a fala inglesa posterior não é plaintext atestado. Rima sozinha não valida |
| Knightmare | Regra única para os sete grupos; comparar hipóteses de palavra, morfema, letra e fronteiras apenas nas famílias elegíveis | Zero pode ter papel especial somente em modelo explícito. Dígito 2 ausente deve continuar desconhecido; não completar a chave pela lore |
| Chayenne | Explicar os 36+13 dígitos e o contexto da entrevista com um mecanismo consistente; controlar alternativas de fronteira registradas | Os fragmentos já estão nos livros. Recuperar sua cópia ou acertar emoticons não é tradução independente |

Comparar mecanismos compartilhados e por fonte como hipóteses separadas, com
custo dos parâmetros adicionais. Não treinar uma chave diferente para cada
frase e depois apresentar o conjunto como algoritmo universal. Letras, sílabas,
blocos de vários dígitos, palavras ou entidades só entram com uma especificação
finita e critérios de identificação. Novo léxico da lore será versionado e
congelado antes do ajuste; nomes acrescentados depois de ver a saída serão
registrados como ajuste posterior, nunca validação.

Nulos devem repetir **toda** a seleção de modelo/chave com o mesmo orçamento:
embaralhamento simples, contagens por grupo e controles de repetições/blocos
conforme o alvo. Confirmar que o nulo altera efetivamente os dados testados.
Relatar todas as famílias examinadas e corrigir a seleção múltipla antes de
alegar destaque. Um p pequeno não substitui leitura e evidência externa.

Uma candidata deve produzir a saída literal de toda a região a que se aplica,
com lacunas e alternativas preservadas, e fazer previsões congeladas fora do
ajuste. Livros, enquetes e outras falas servem à transferência somente após
auditar dependências. Se não houver validação independente disponível,
classificar como candidata e especificar exatamente qual evidência falta.

**Saída:** catálogo de candidatas ou resultado negativo delimitado. Se houver
uma candidata forte, antecipar R30 imediatamente; não esperar terminar os outros
blocos para compartilhar a saída e testar a previsão.

## R29 — competir com explicações sem mensagem textual

Comparar três classes: língua cifrada, montagem numérica sem plaintext e mistura
por fonte/época. Não pressupor que livros, NPCs e entrevista tenham a mesma origem.
Geradores possíveis incluem cópia/recombinação de motivos, modelos de transição
ou regras de formatação, desde que aprendidos no ajuste e totalmente especificados.
Não extrair o dicionário de motivos no conjunto de avaliação.

Medir custo de descrição incluindo código, chave, sementes, dicionário, cortes
e exceções, além de previsão de novas variantes/combinações. Verificar a potência
em controles de inglês cifrado comum **e copiado**, geradores sem texto e dados
mistos. Só usar a comparação para interpretar 469 se ela distinguir esses
controles; caso contrário, registrar não identificação.

Todo bloco reservado passa por auditoria de cópias. Os 70 livros não se tornam
independentes por serem sorteados em treino/teste. Quando uma divisão informativa
não for viável, declarar a limitação e procurar nova fonte; não reduzir o critério
até obter significância. Conteúdo público já examinado é avaliação exposta.

**Saída:** comparação quantitativa e previsões testáveis; preferência por um
gerador não textual será chamada de evidência favorável àquela classe, não
prova de ausência de significado. Para o desfecho G, ainda é necessária evidência
autenticada do processo original: material autoral/declaração inequívoca ligada
aos textos e versões, ou gerador original com procedência e escopo demonstrados.
Um depoimento genérico sobre “mistério” não resolve todas as fontes.

## R30 — decisão e replicação

Para uma candidata T: congelar algoritmo, chave, vocabulário e previsões; verificar
outra implementação sem correções orientadas pela saída; testar conteúdo novo
cuja dependência de motivos foi auditada e confrontar contexto/atestações externas.
Dois programas reproduzindo uma tabela escolhida a mão não validam significado.
Replicação por terceiro, quando existir, terá origem registrada; não afirmaremos
que uma checagem interna seja revisão externa. Não é necessário contatar ninguém
para executar o plano; qualquer contato externo exige autorização separada.

Para uma candidata G: autenticar autoria, versão e abrangência da evidência de
geração; reproduzir quando possível e separar eventual material cifrado misto.
Não extrapolar “esta fala foi inventada” para “todos os livros não significam nada”.

Sem evidência suficiente: concluir I para o lote, com famílias encerradas,
hipóteses suspensas e dado específico que permitiria reabertura. O fechamento
do lote não encerra artificialmente a missão nem autoriza repetir as mesmas
buscas sem mudança substantiva.

## Estados, regras de parada e comunicação em toda rodada

Usar estados explícitos: **planejada; em execução; confirmada no escopo; refutada
no escopo; inconclusiva por orçamento/ambiguidade; suspensa por falta de evidência**.
“Encerrada operacionalmente” significa sair da fila de cálculo; pode corresponder
a refutação delimitada ou suspensão. Não é sinônimo de prova universal de falsidade.

Antes de cada execução, registrar hipótese, dados expostos, parâmetros, custo,
positivos, nulos e condição de parada. Depois, publicar resultados negativos e
falhas. Manter as versões antigas: protocolos congelados nunca serão reescritos
para acomodar uma descoberta posterior. Uma ampliação vira versão/experimento novo.

O [modelo de relatório](round_report_template_v2.md) exige, em toda rodada:

- Hipóteses investigadas e o que mudou desde a rodada anterior.
- Evidência nova de lore/fontes e sua independência, distinguindo fato,
  relato, hipótese e especulação.
- Execução real, controles, cobertura, falhas, limites e próximos critérios.
- **Traduções potenciais literais**, quando houver: sequência original,
  saída inglesa sem reparos, chave/regra, alternativas, contexto que poderia
  explicar e previsão verificável que ainda falta. Uma paráfrase da lore não
  será apresentada como saída do algoritmo.
- Decisão de manter, refutar ou suspender cada hipótese e seu escopo.

Candidatas podem ser compartilhadas antes de confirmação, mas serão rotuladas
como alegação externa não reproduzida, saída mecânica, candidata contextual
não validada ou tradução validada. Só chamar uma possibilidade de promissora
quando houver consistência de mensagem, evidência além do ajuste e controles
compatíveis; mostrar também suas falhas. Se nada cumprir isso, declarar
**“nenhuma candidata nova; tradução potencial não identificada”**, sem inventar
uma frase para preencher o relatório.

O primeiro trabalho após esta revisão é R24. R25/R26 têm prazo lógico de decisão,
não permissão para buscas ilimitadas. R27 pode avançar sem esperar por arquivos
históricos; R28 depende de métodos/fontes elegíveis, e R30 é antecipada se surgir
uma candidata forte. Essa independência é de tarefas, não exigência de agentes
paralelos. O registro estruturado está em `data/mission_plan_v2.json`.
