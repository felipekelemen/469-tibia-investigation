# Plano de conclusão v3 — após 33 rodadas

26/11/2026. Base auditada: `72b559a48ca93138d3f8e74add938dfa3dc424c2`.
Este documento substitui o plano v2 como orientação de trabalho. É uma revisão
do plano, **não uma rodada 34 executada**. Os protocolos antigos permanecem
inalterados. [Estado computável](../data/mission_plan_v3.json).

## Foi executado tudo dos planos anteriores?

**Não, se “tudo” inclui atingir os objetivos científicos e completar todas as
buscas. Sim, quanto ao lote programado de rodadas 24–30.** Foram registradas
33 rodadas; as R31–33 acrescentaram pesquisa documental e contagem exata.
Uma rodada concluída pode terminar com hipótese suspensa, busca limitada ou
método reprovado. Isso não equivale a uma entrega científica bem-sucedida.

| Frente original | Trabalho efetivamente realizado | O que continua sem solução |
| --- | --- | --- |
| P01 — fontes e validação | Corpus, procedência, auditoria de cópias; entrevistas e arquivos recuperados nas R24/31/32 | Pares numérico–inglês atestados suficientes e conteúdo independente para validar uma descoberta |
| P02 — capacidade dos algoritmos | Benchmarks, implementações verificadas e qualificação em cenários delimitados | Recuperação geral a partir dos dígitos e seleção semântica; os cenários da R27 não passaram no critério estabelecido |
| P03 — módulos e geradores | Regularidades e mecanismos de cópia medidos; comparação textual/numérica/mista na R29 | Identificar o processo original; a comparação da R29 falhou em distinguir controles de origem conhecida |
| P04 — tradução | Diversas famílias testadas, com negativos delimitados | Nenhum algoritmo produz uma tradução validada |
| P05 — letras, sílabas, palavras e conceitos | Segmentações, codebooks e unidades testados; contagem da R33 concluída | Identificar significados e escolher uma leitura com evidência externa |
| P06 — história de Hellgate | Tabelas, relatos e revisões datados, com lacunas explícitas | Contagens completas autenticadas e data da transição; coincidência com a renomeação não confirmada |
| P07 — mecanismos matriciais | Famílias finitas 3×3, 4×4 e 5×5 examinadas; condições algébricas verificadas | Nenhuma matriz demonstrada como chave; mecanismos sem dados ficam suspensos |

Referências: [plano inicial](next_experiments.md), [v2](mission_plan_v2.md),
[balanço 1–30](rounds_01_30_review.md), [R31](round31.md), [R32](round32.md),
[R33](round33.md) e [último progresso experimental](../data/plan_progress_round33.json).
Os balanços antigos descrevem seu momento; não são reescritos como se já
conhecessem resultados posteriores.

Algumas pendências computacionais foram resolvidas: os 12 casos de Chayenne
da R21 foram concluídos na R22; o caso principal de Knightmare da R23 foi
concluído na R33. Neste último existem **153.174.074 chaves lexicais** para os
nove dígitos observados, no dicionário e modelo especificados. Duas
implementações confirmam a contagem; ela não conta traduções validadas nem
necessariamente frases diferentes. Dos 51 ajustes da R33, sete controles
atingiram o limite. Outras famílias limitadas antigas não foram todas reabertas.

O corpus de 70 livros e 11.263 dígitos foi reproduzido; os 5.729 símbolos usam
segmentação/mapa importados, com ambiguidades registradas. Não são um alfabeto
decifrado. Os livros compartilham trechos e os fragmentos de Chayenne também
aparecem neles. Reservar livros já examinados não cria um teste sem exposição.

## Que conclusão pode ser definitiva?

O plano termina com uma decisão documentada, mesmo se a evidência não permitir
escolher entre tradução e origem sem texto. **Nenhum plano finito pode garantir
uma resposta binária correta a partir apenas dos números disponíveis.**
Uma tabela arbitrária pode associar qualquer sequência finita a uma frase;
encontrar ou deixar de encontrar essa tabela não identifica a intenção autoral.

| Resultado | Requisito para concluir | Alcance |
| --- | --- | --- |
| T — tradução demonstrada | Algoritmo integral congelado, previsões novas corretas, correspondência semântica autenticada e reprodução independente da implementação | Fontes, versões, unidades e domínio efetivamente validados |
| G — produção original sem mensagem textual documentada | Evidência primária autenticada sobre a criação daqueles números; auditoria do processo e reprodução quando houver material suficiente | Textos/versões identificados, sem extrapolar para toda a linguagem |
| M — resultado misto | Evidências T e G em conjuntos distintos | Cada conjunto mantém sua própria decisão; os demais podem continuar I |
| I — inconclusivo, investigação encerrada neste ciclo | Faltam evidência decisiva, identificabilidade ou capacidade demonstrada, após os limites abaixo | Não equivale a “não existe tradução” |

Uma incompatibilidade matemática pode encerrar definitivamente **uma família
especificada**. Fracasso heurístico ou limite de memória não pode. “Sem mensagem
textual” também não significa “sem utilidade no jogo”: números podem cumprir
funções narrativas, estéticas ou de identificação.

## Seis etapas de execução restantes neste novo ciclo

Os identificadores E1–E6 representam entregas, não uma promessa de seis novas
rodadas até a tradução. Cada entrega termina em realizada, refutada no escopo,
suspensa por falta de evidência ou não acionada por dependência reprovada.
Uma descoberta forte antecipa E5/E6. E4 depende de E1, não de terminar E2/E3.

### E1 — buscar a evidência que pode decidir a questão

**Prioridade:** Avar Tar, Knightmare e Chayenne, seguidos pela procedência de
3478 e das matrizes. Reutilizar o inventário existente; procurar lacunas
específicas, não repetir uma varredura genérica de teorias.

Buscar, nesta ordem:

1. Um par completo numérico–inglês atribuído ao autor, instruções do sistema,
   notas de criação ou implementação original publicamente disponível.
2. Evidência de como cada fala/livro foi produzido: texto codificado, cópia de
   números existentes, geração numérica ou mistura. Uma cópia pode herdar uma
   mensagem anterior; investigar também sua origem.
3. Mudanças nos três repositórios iniciais, alegações novas com algoritmo
   executável e fontes primárias ainda não recuperadas. As entrevistas já
   recuperadas nas R31/32 não passam a ser evidência nova.
4. Capturas/mapas com procedência e contagens verificáveis de Hellgate;
   versões pareadas de livros e documentação das renomeações.

**Limite:** até 30 consultas distintas e 60 documentos/capturas únicos,
distribuídos em no máximo duas passagens pelo inventário. Uma repetição de
acesso por falha transitória; registrar bloqueios. Identificar antes da leitura
os alvos e por que poderiam preencher uma lacuna. Contar espelhos como cópias,
não como testemunhos independentes. Não prometer esgotar a internet.

Entregar `e1_sources`, registro de exposição e decisões separadas para:

- **3478:** nome contextual documentado; grafia BEHOLDER/BONELORD, ID interno
  e chave continuam hipóteses distintas. Preservar `4378` em Avar Tar.
- **Hellgate:** distinguir bloco parcial 3×3, tabelas 4×4 e uma chave física
  5×5 ainda não observada por completo. Não completar células por conveniência.
- **Cronologia:** datas de captura, postagem e atualização do jogo separadas.
  Intervalos compatíveis com a renomeação não provam coincidência exata nem
  vínculo causal. Distinguir a renomeação geral de 2010 do caso nostálgico
  documentado na wiki em 2012/2023.

Sem nova evidência, manter negativos delimitados e retirar essas hipóteses da
fila ativa. Uma lacuna histórica termina como **não demonstrada**, não falsa.

Contato direto com autores/CipSoft seria uma via de evidência especialmente
útil, mas não é uma ação autorizada neste plano. Podemos preparar uma consulta
com os textos exatos, perguntas sobre origem e pedido de exemplo independente;
nenhuma mensagem será enviada sem instrução do usuário. A falta de contato ou
resposta não impede o encerramento do ciclo em I.

### E2 — demonstrar que um método consegue reconhecer a resposta correta

A contagem da R33 fornece um espaço de soluções lexicais. O próximo problema
é selecionar significado; não basta contar mais palavras de dicionário.

Qualificar no máximo **dois métodos de seleção**, com até **duas versões por
método**. A primeira opção é busca com restrições gramaticais e pontuação de
inglês congeladas, preservando literalmente as emissões do algoritmo. Um
segundo método deve acrescentar uma restrição diferente e motivada, não apenas
outra senha ou outro modelo de linguagem. Versões não aprovadas ficam registradas.

Antes do ajuste ao jogo, congelar corpora, partições por origem, cenários,
parâmetros, critérios de abstenção e orçamento. Usar pelo menos 30 casos novos
por cenário relevante: sete grupos curtos, texto sem espaços, nomes fora do
vocabulário, repetições, ambiguidade e símbolo não observado. A qualificação
com contexto longo não habilita automaticamente o caso curto de Knightmare.

Nos cenários identificáveis, manter o critério anterior: **27/30 casos com
pelo menos 95% das letras reservadas corretas**, relatando também recuperação
integral, erros e cobertura. Nos casos ambíguos ou fora da família, exigir
alternativas/abstenção e medir falsas certezas; não pontuar como acerto a
invenção de uma emissão para o dígito ausente. Exigir zero aceitações falsas
nos 30 controles negativos de qualificação do cenário; divulgar o intervalo
binomial, pois zero observado não garante risco zero.

As regras que definem um caso identificável serão fixadas antes da avaliação;
não remover retroativamente os fracassos. Inglês natural deve ser separado de
listas de palavras geradas para caber no dicionário. Se uma família não conseguir
representar a prosa selecionada, registrar sua cobertura e essa limitação;
não alterar o teste até caber. Uma seleção top-k precisa de k e cobertura
congelados; conter a resposta em milhões de alternativas não é recuperação.

**Saída:** `e2_qualification`, com métodos elegíveis por cenário. Após duas
versões reprovadas, suspender o método neste ciclo. Certificados algébricos
exatos continuam úteis sem exigir um seletor heurístico qualificado.

### E3 — testar os três alvos com poucas hipóteses discriminantes

Entram no máximo **três famílias**, cada uma com protocolo finito, derivação
motivada e previsão que possa falhar. Uma vaga não preenchida é dispensada;
não inventar hipóteses para consumir orçamento.

1. Seleção gramatical sobre a família da R33, somente se E2 a qualificar no
   cenário correspondente. Contar soluções não exige listá-las; escolher a
   melhor sob uma pontuação diferente exige justificar a nova busca. Busca
   aproximada nunca vira certificado de ausência de inglês.
2. Mecanismo fornecido por nova evidência de E1: por exemplo, regra matricial,
   unidades ou estados especificados. Nenhuma expansão livre de bordas,
   módulos, períodos ou senhas. Matriz só entra com dados ou mecanismo novos.
3. Codebook de palavras/conceitos apenas se houver âncoras semânticas
   independentes que permitam uma previsão adicional. Ajustar uma tabela aos
   três alvos e lê-los de volta não é teste.

Em cada família elegível, aplicar a regra aos alvos relevantes completos:
poema de Avar Tar, sete grupos de Knightmare e ambas as partes de Chayenne.
Regras compartilhadas e específicas por fonte são modelos separados, com
todos os parâmetros contados. O dígito 2 ausente de Knightmare permanece
indeterminado até surgir informação independente.

Repetir a busca e seleção completas em controles uniformes, embaralhados e
com estrutura/repetições preservadas. A R33 mostra por que um encaixe lexical
sozinho não discrimina: 18/19 embaralhamentos também admitem chaves. Para uma
alegação estatística nova, prever pelo menos 999 réplicas por tipo de nulo
declarado, corrigir o máximo das famílias/alvos selecionados neste ciclo e
relatar o erro de Monte Carlo. Isso não corrige toda a exploração histórica.
Se houver censura por orçamento, não fabricar uma distribuição completa nem
um p-valor; resultados permanecem descritivos. Significância não valida semântica.

Entregar `e3_candidates`: entrada exata, regra/chave, saída inglesa literal,
alternativas, pontuação, controles, compatibilidade com a lore e previsão
externa ainda necessária. Compartilhar imediatamente uma candidata coerente,
rotulada como não validada. Nunca reparar letras ou completar frases pela lore.
Se nenhuma passar, registrar isso sem publicar fragmentos casuais como tradução.

### E4 — verificar a hipótese de produção original sem texto

Esta é a via para uma conclusão negativa substantiva; E3 fracassar não a prova.
Examinar no máximo **dois conjuntos de artefatos originais elegíveis** encontrados
em E1, com autoria, versão e cadeia de procedência verificáveis. Material cuja
origem não pode ser autenticada fica como alegação, sem análise infinita.

Se houver código ou notas de geração, rastrear entradas, sementes, constantes,
tabelas, fragmentos copiados e edições manuais. Um programa sem argumento de
texto pode conter texto cifrado nas constantes ou copiar uma fonte que o contém.
Portanto, ausência de uma variável chamada “texto” não basta para concluir G.

Reproduzir os números e suas variantes usando os artefatos originais, quando
disponíveis; confrontar erros e versões, além de verificar eventual seleção
manual de saídas. Um gerador criado agora para memorizar os livros não conta
como origem. Um depoimento inequívoco autenticado pode sustentar origem
documentada, com escopo e dependência testemunhal explícitos; não será descrito
como código executado ou reprodução técnica se não houver esse material.

**Saída:** `e4_origin`, distinguindo processo reproduzido, declaração autoral
atestada, alegação sem confirmação e ausência de evidência. Sem material elegível,
encerrar como não acionada por falta de fonte. Não repetir a comparação da
R29 como prova: ela preferiu um modelo numérico até em controles de inglês.

### E5 — testar previsões que não ajudaram a construir a solução

Acionar quando houver uma candidata T ou evidência G. Congelar executável,
especificação, chave, vocabulário, entradas elegíveis e saída prevista **antes
de revelar os significados reservados**. Hashes provam integridade, não ausência
de exposição prévia. Materiais públicos já examinados não são cegos.

Para a alegação de tradução generalizável deste ciclo, estabelecer como mínimo
operacional **três mensagens/unidades completas independentes, somando pelo
menos 100 letras inglesas**, com todas as letras previstas corretamente após
a normalização fixada. Declarar quais símbolos e contextos novos foram
efetivamente cobertos. Esses limites são regras de decisão, não uma prova
universal nem autorização para escolher apenas mensagens favoráveis.

A referência deve vir de plaintext autenticado ou validação autoral específica
da correspondência; “soa inglês e combina com a lore” não é referência. Uma
glosa aproximada pode apoiar a interpretação, mas não comprova recuperação
literal. O conjunto elegível será fixado antes das previsões e todos os itens
serão relatados. Um custodiante independente pode guardar as respostas, se
houver participação disponível e autorizada; sem isso, não alegar teste cego.

Para afirmar transferência entre fontes, incluir ao menos duas procedências
independentes. Se a evidência só cobrir uma procedência, restringir a conclusão
a ela. Um par atestado isolado pode confirmar o significado daquela mensagem,
mas não satisfaz sozinho a missão de generalização. Cópias de Chayenne nos
livros não contam como novos acertos; auditar também combinações e dependências
de motivos, não apenas igualdade da mensagem inteira.

Para G, verificar se a procedência e o método cobrem precisamente os textos
alegados, distinguindo cada fala e os livros. Não exigir que fontes diferentes
tenham a mesma origem. A ausência de material para essa checagem mantém I.

Uma tentativa de validação por candidata congelada neste ciclo. Correções
depois de revelar a resposta passam a ser desenvolvimento e exigem novos
dados; não reutilizar o mesmo teste como confirmação. Uma falha técnica que
invalide o procedimento deve ser documentada antes de qualquer repetição.

### E6 — reproduzir, adjudicar e encerrar o ciclo

Reexecutar os resultados determinantes em ambiente limpo e conferir os
certificados com outra implementação. Reprodutibilidade interna e revisão por
terceiro são coisas distintas; registrar quem realmente fez cada uma. Não
afirmar revisão externa sem um revisor externo.

Publicar um dossiê por fonte: resultado T/G/I, mecanismo, versão, evidência,
falhas e limites. Usar M na síntese se houver T e G em conjuntos diferentes.
Apresentar as traduções integrais demonstradas, quando existirem, e uma lista
finita de famílias refutadas, buscas limitadas e hipóteses suspensas.

**Encerrar o trabalho ativo deste ciclo em E6, mesmo com resultado I.** Uma
sequência de “continue” não justificará repetir buscas equivalentes sem apontar
o que mudou. Reabertura requer fonte primária nova, erro demonstrado que altere
uma conclusão, método recém-qualificado no cenário necessário ou mecanismo
novo com previsão independente verificável. Uma semelhança curta não basta.

## Orçamento e comunicação

- Até 30 consultas e 60 documentos/capturas em E1; até dois conjuntos originais
  elegíveis em E4. Fontes indisponíveis são registradas, não aguardadas sem prazo.
- Até dois métodos, duas versões por método e três famílias de E3. Uma melhoria
  conta como versão mesmo que seu nome não mude.
- Teto de **48 horas de CPU em um núcleo equivalente** para os cálculos deste
  ciclo, reservando oito para validação/reprodução. Contar positivos, nulos,
  buscas fracassadas e tentativas adicionais. É teto, não estimativa nem promessa
  de uso integral; sem necessidade, parar antes.
- Até 4 GiB por processo, 8 GiB agregados e 20 GiB temporários, reduzidos se o
  ambiente tiver menos recursos. Sem contratação de GPU ou serviço pago.
- Ao atingir qualquer limite, registrar desconhecido/incompleto; não transformar
  em zero. As sete buscas secundárias limitadas da R33 não serão retomadas apenas
  para completar uma tabela: primeiro demonstrar que mudariam uma decisão.
- Não esperar indefinidamente por dados ou resposta externa. Etapas condicionais
  sem insumos serão suspensas e o ciclo seguirá para E6.
- A cada execução: hipótese, fontes novas, números realmente calculados,
  candidatas literais, controles, decisão e saldo de etapas/orçamento. Protocolos
  de execução serão congelados antes dos resultados; este plano não substitui
  especificações ainda inexistentes de métodos novos.

O trabalho já realizado nesta revisão é a auditoria do estado e a redação deste
plano. **As seis etapas E1–E6 ainda não foram executadas.** O próximo trabalho
é E1, seguido da qualificação E2; a reprodução dos 70 livros e a contagem
principal de Knightmare não precisam ser reiniciadas.
