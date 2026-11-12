# Próximos experimentos após auditoria do Deep Research

Base: duas rodadas científicas publicadas até `1246af8`, relatório integral
recebido e [cruzamento de alegações](research_crosswalk.md). Não há tradução
nova nem plaintext oficial descoberto nesta revisão. Este plano substitui
o rascunho local provisório.

## Decisão

O relatório reforça três caminhos: capacidade do solucionador, explicação dos
módulos e evidência externa. Corrigimos suas recomendações sobre minimapas,
Chayenne, independência dos conjuntos e força da evidência histórica.
A arqueologia das caveiras continua importante, mas não deve bloquear todos
os experimentos nem alimentar uma busca ilimitada de sementes arbitrárias.

Manter três representações concorrentes: dígitos originais; row0 condicional;
row0 mais escolhas dos homofones e metadados de zeros. A etapa 99→14 perde
informação sobre a escolha do código; não presumir que essa perda seja
irrelevante. Tampouco presumir que os rótulos intermediários sejam inglês.

## Lote A — preparar discriminação antes de procurar novas leituras

### P01. Inventário por fonte e viabilidade de validação

**Pergunta:** que conteúdo realmente novo e que equivalências atestadas temos?

Expandir o inventário de livros, falas, poemas, entrevistas e enquetes. Para
cada amostra: fonte original, data da ocorrência e da captura, versão, bytes,
hash, significado explicitamente fornecido e proveniência da transcrição.
Separar modalidade de fonte: Chayenne é resposta de desenvolvedora, mas contém
fragmentos literais dos livros; não deve ser forçada a um codebook por palavra.

Executar correspondência exata, alinhamentos e cobertura por motivos em raw
e nas representações aplicáveis. Comparar também com o material já conhecido
upstream e registrar exposição histórica. Não concatenar livros para criar
falsos fragmentos que atravessem fronteiras.

- Chayenne já foi examinada: 11 e 9 ocorrências das duas partes. Serve como atestação externa, não como holdout independente dos livros.
- Knightmare e Avar Tar não aparecem integralmente e não compartilham 12-gramas raw com os livros no teste atual. Isso não prova independência transformada nem mesmo algoritmo distinto.
- Amostras posteriores no calendário não são automaticamente novas no conteúdo ou cegas para esta pesquisa.

Construir grafo de dependências de motivos, congelando previamente critérios
em dígitos e símbolos. Medir se é possível dividir por componentes. Se os
componentes conectarem tudo, emitir **INVIÁVEL**, em vez de relaxar o critério
após consultar pontuações. Partições menores podem servir a testes parciais,
mas não serão chamadas de independência semântica.

**Entrega:** corpus modal versionado, tabela de atestação e manifesto de
validação. **Gate:** qualquer claim de generalização identifica exatamente
quais dependências foram excluídas e qual conteúdo permaneceu intocado.

### P02. Benchmark e melhoria do solucionador homofônico

**Pergunta:** conseguimos recuperar um texto cuja cifra desta família sabemos
que existe? Esta é a primeira tarefa de implementação criptanalítica.

Criar positivos de inglês de múltiplos autores, separados do treino dos
pontuadores, com 52/75/99 códigos, diferentes distribuições de homofones,
sementes, comprimentos e graus de repetição. Incluir prosa montada por cópia
e caracteres/códigos raros, registrando cobertura entre treino e teste.
Calcular o limite de identificabilidade devido a códigos não vistos; não
confundir essa impossibilidade local com falha de otimização.

Melhorias candidatas: escore incremental de ngramas, reinícios, trocas e
movimentos de grupos, inicialização por frequência, beam search ou componentes
de palavras com complexidade explícita. Começar pelas melhorias clássicas
antes de introduzir um modelo neural. Usar dois pontuadores independentes;
modelo generativo de texto não pode reescrever a saída decodificada.

A restauração de zeros da serialização não demonstra que existam símbolos
nulos. Se testar deleções, inserções ou segmentação variável, especificar um
modelo gerativo, orçamento de exceções e penalidade de complexidade; não
apagar caracteres manualmente até surgir inglês. Esses cenários exigem
positivos próprios e potência medida separadamente.

Ajustar tudo apenas em positivos de desenvolvimento. Depois congelar
algoritmo, orçamento, seleção e pontuador para qualificação externa. Gate
operacional proposto, a registrar antes da execução: pelo menos 95% das
letras corretas em pelo menos 90% de 30 ou mais fixtures independentes por
cenário relevante. Relatar precisão, cobertura e falhas, inclusive quando o
gate não for alcançado. Isso qualifica o cenário, não toda a homofonia.

**Entrega:** benchmark reexecutável, chaves verdadeiras e orçamentos por
instância. **Gate:** nenhuma exclusão da família enquanto a recuperação de
positivos compatíveis for insuficiente. O resultado atual de 42,6% não passa.

### P03. Modelo gerativo dos módulos e variantes

**Pergunta:** os livros exigem linguagem para explicar suas regularidades,
ou uma montagem sem plaintext prediz os mesmos efeitos?

Comparar montagem por cópia, Markov e linguagem cifrada com reutilização de
motivos. Penalizar modelo, dicionário, seleção, exceções e dados residuais em
custo de descrição; medir também log-loss fora da família de motivos usada
para aprender o modelo. Não extrair o dicionário no teste.

Em paralelo, modelar os 106 trechos maximais divergentes e os 56 contextos
variáveis sem contar janelas sobrepostas como observações independentes.
Testar escolha de homofone por contexto, posição, fronteira de módulo e
estado por símbolo. Comparar com baseline que apenas copia fragmentos.
Enumerar alinhamentos de zeros compatíveis em análises de sensibilidade;
não selecionar o alinhamento que produz a palavra mais atraente.

Nulos preservam símbolos, marginais e motivos conforme o modelo testado.
Positivos obrigatórios incluem prosa real cifrada e prosa cifrada copiada:
a cópia é compatível com significado. Avaliar ambos antes de aplicar o
critério aos livros.

**Entrega:** preditores de módulos/variantes, competição MDL e positivos.
**Gate:** ganho fora das famílias de ajuste, demonstrado em controles. Uma
explicação gerativa sem mensagem mostra suficiência, não ausência universal
de mensagem. Prever código novo é avanço mecânico, não tradução.

## Lote B — buscas condicionadas aos gates

### P04. Aplicar a busca homofônica qualificada aos livros

Depende de P01 e P02. Tratar os conjuntos reservados locais já examinados
como triagem/desenvolvimento, não reabrir o mesmo conjunto como confirmação
prospectiva. Selecionar parâmetros em descoberta e repetir a busca inteira
em cada nulo, com o mesmo orçamento e distribuição de reinícios.

Usar nulos por códigos, bigramas e módulos; confirmar que realmente variam
o conjunto reservado. O Euler atual pode deixar livros curtos inalterados;
isso deve constar da potência efetiva. Fazer 99 réplicas na exploração e
999 na confirmação de candidato congelado, se houver sinal justificável.
Controlar a seleção entre famílias e pontuadores por estatística do máximo
ou procedimento previamente definido, sem parar cedo quando p ficar baixo.

**Gate:** leitura literal longa e coerente, desempenho além dos controles,
sem reparos por livro, e previsões externas com algoritmo congelado. Um p
pequeno ou maior escore de inglês não é tradução. Um fracasso delimita apenas
a família, parametrização, fontes e potência efetivamente testadas.

### P05. Codebook e segmentação por fonte/modalidade

Depende de P01. Manter inicialmente a resposta Chayenne na rota compatível
com os livros; estudar Knightmare, gritos e enquetes com hipóteses de
palavra/morfema sem impor que pertençam todos ao mesmo mecanismo. Não há
novo gloss oficial aceito na auditoria. Códigos comunitários serão candidatos
com origem e grau de atestação por entrada, nunca verdades de treinamento.

Comparar modelos segmentados e de grupos inteiros, custos de dicionário e
alternativas semânticas. O contexto de uma entrevista pode sugerir uma
hipótese, mas não fornecer uma tradução inexistente. Não usar o comentário
inglês de Avar Tar como plaintext do poema. Fazer validação deixando fontes
inteiras de fora e controlando substrings compartilhadas entre elas.

**Gate:** previsões de palavras/frases não utilizadas no ajuste com evidência
externa; codebooks igualmente compatíveis impedem alegação de identificação.
Solucionar uma frase não significa solucionar os 70 livros. Testar transferência
para os livros apenas depois, como hipótese separada.

## Linha histórica e matricial em paralelo

### P06. Datar caveiras, nomes e livros separadamente

O repositório `tibiamaps/tibia-historical-map-data`, no snapshot examinado,
não serve para extrair caveiras: contém minimapas, não inventário de objetos,
e não cobre versões 8.6–8.7. Arquivos de sprites/definições de cliente também
não fornecem, por si, os objetos colocados na sala.

Buscar capturas, vídeos ou extratos autenticáveis de mapa com objetos em
três janelas: antes de 23/08/2010, entre 23/08 e 08/12, e depois de 08/12.
Registrar versão, coordenadas, origem, data de captura versus publicação,
pilhas visíveis/ocultas e possibilidade de mover objetos. Cruzar testemunhos
independentes e localizar a sala por geometria, sem atribuir objetos a pixels
de minimapa. Comparar também os próprios números dos livros nas épocas,
se existirem transcrições autenticáveis: mudança da criatura, mudança da
matriz e recodificação dos livros são três eventos distintos.

As datas gerais encontradas distam 107 dias. Isso não comprova a época da
edição da matriz nem sua ligação criptográfica ao nome. O acesso aos anúncios
oficiais foi por texto indexado; os limites estão no registro de fontes.

**Entrega:** tabela célula/quantidade/fonte/intervalo de data e corpus por época.
**Gate:** só afirmar coordenação histórica quando a evidência a discriminar
estiver disponível. Indisponibilidade de arquivos é um resultado de fontes,
não rejeição da hipótese criptográfica.

### P07. Matriz como mecanismo adicional, sem sementes arbitrárias

Depende de mecanismo específico e de P01; a força da ligação por época
depende de P06. Não repetir Hill 26/29, Vigenere com os nomes ou as 53 funções
já negativas. Não enumerar livremente LFSRs, transdutores e PRNGs até aparecer
uma palavra: o número de escolhas pode ajustar ruído ou motivos repetidos.

Uma primeira família pequena possível é leitura em blocos 4×4: ordem fixa
obtida dos valores da matriz, regra de desempate documentada, orientações
geométricas enumeradas e tratamento declarado das caudas. Outra família
só deve entrar se um modelo de P03 predizer seleção de homofones por estado.
Em qualquer caso, congelar integralmente estados, seeds, bancos de saída,
reset, direções, alfabeto e limites antes de abrir validação; cobrar sua
complexidade e usar matrizes-controle comparáveis.

Manter BEHOLDER/BONELORD fora do ajuste e do pontuador. Um único par suposto
3478→nome é subdeterminado e pode ser atendido por uma simples tabela manual.
Exigir previsões em outros itens e textos independentes. Se o número dos
livros não mudou quando a matriz mudou, o mecanismo precisa explicar por
que o restante da leitura permanece consistente, em vez de ser ajustado
apenas para trocar um nome.

**Gate:** ganho fora dos motivos ajustados e previsões literais independentes,
com parâmetros fixos e réplicas sobre nulos igualmente otimizados. Mudança de
matriz não é, por si, prova de que ela funcione como chave.

## Ordem prática e decisões

1. P01 e P02 primeiro; iniciar P03 e a pesquisa de P06 em paralelo.
2. Se P02 passar, executar P04 com orçamento congelado; se falhar, melhorar nos positivos, sem anunciar exclusão de homofonia.
3. P05 depende da qualidade e quantidade das amostras, não da crença em dois sistemas universais.
4. P07 é uma busca pequena condicionada a mecanismo, não o centro obrigatório de toda a próxima rodada.
5. Cada lote registra hipótese exata, dados vistos, dependências, parâmetros, controles, custo, falhas e critério de parada antes de rodar.

O critério principal permanece um algoritmo reproduzível que gere inglês
coerente em conteúdo independente, sem anagramas livres ou reparos por item,
com previsões externas verificáveis e replicação por outra implementação.
Um resultado em idioma diferente exige o mesmo rigor. A alternativa científica
não é provar que uma sequência não significa nada sob qualquer chave possível:
é excluir classes explícitas com poder medido e comparar explicações gerativas.
Nenhuma evidência desta revisão satisfaz ainda o critério de tradução.


Atualização de execução: a [quarta rodada](round4.md) qualificou V2 em novos
autores e aplicou a busca aos livros com controles completos. Prosa copiada
ainda revelou falhas; a prioridade algorítmica passa a essa condição, mantendo
novos dados de teste separados. Não houve tradução validada.


Atualização após a [quinta rodada](round5.md): a nova qualificação em cenários
copiados passou, e a estatística dos livros superou os três nulos locais.
Ainda não há prosa legível validada. Priorizar separação do sinal por módulos,
critério de coerência independente dos tetragramas e dados externos inéditos;
não transformar pontuação alta no mesmo reservado exposto em tradução.

Atualização após a [sexta rodada](round6.md): o inventário modular não cobre
o reservado com motivos de oito ou mais códigos; esse controle não identifica
a origem do sinal. O critério lexical independente falhou na qualificação
externa e as 70 leituras fixas não renderam candidata longa. A auditoria dos
zeros revelou que a pipeline depende da tokenização importada. Priorizar agora
qualificação de raw→tokens em positivos com regras de zeros conhecidas,
fronteiras avaliadas separadamente de plaintext e nulos com o mesmo orçamento.
Depois, testar famílias contextuais pequenas congeladas, sem escolher parses
por palavras isoladas. Continuar a coleta de pares externos autenticados e
qualificar uma nova medida de coerência antes de selecionar novas chaves.

Atualização após a [sétima rodada](round7.md): duas versões de parsing exato
foram avaliadas em qualificação com chave/emissões fornecidas, em autores
novos. V1 e V2 falham no gate global; V2 melhora a baseline pareada 211→220/240,
mas só 185 plaintexts são exatos. Não confundir qualificação parcial de cenários
com recuperação de chave ou validação de 469. As falhas V1 têm objetivo errado
estritamente maior que a verdade; mais tentativas do mesmo parser não resolvem.

Priorizar restrições de fronteira/zeros verificáveis e um modelo externo mais
forte, com nomes, omissões e colisões explícitas. Comparar taxas de omissão por
código/estado sem contar módulos copiados como observações independentes. Para
buscar chave e segmentação juntas, construir qualificação própria com a chave
escondida e um objetivo comum, antes de aplicar a novos livros. Manter os
modelos e resultados atuais congelados, inclusive os resultados negativos.
