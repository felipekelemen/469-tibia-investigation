# Terceira rodada — execução do plano auditado

**Nenhuma tradução verificável foi encontrada.** Executamos inventário e
viabilidade, melhoria e qualificação do solucionador, modelos gerativos,
pesquisa histórica e uma família finita de leitura matricial. O gate da
nova busca homofônica não passou globalmente; sua aplicação confirmatória
aos livros não foi executada, respeitando o protocolo previamente definido.

| Linha | Execução e resultado |
|---|---|
|P01 fontes/validação|16amostras,15candidatas e1controle excluído; zero novos pares oficiais completos número/plaintext; zero amostras prospectivas cegas|
|P02 capacidade|Solucionador incremental C++;180ajustes,30fixtures pareados entre6cenários;5gates passam,99desigual fica em26/30 contra mínimo27|
|P03 modelos/variantes|Cópia comprime fortemente; vantagem também em inglês cifrado copiado, portanto não identifica ausência de mensagem|
|P04 busca qualificada nos livros|Bloqueada pela falha global de P02; nenhuma exceção ad hoc para ignorar o cenário difícil|
|P05 codebook por fonte|Inventário e identifiabilidade executados; sem novos glosses externos suficientes para validação semântica de frases|
|P06 arqueologia|25consultas; transcrição completa da matriz antiga em post com data exibida26/12/2007; mudança exata ainda sem data|
|P07 matriz como leitura|192variantes,39controles de blocos+39condicionais; p=0,75 e1,0,respectivamente; nenhuma leitura coerente|

Na linhaP07, o segundo nulo mantém inalterada a representação de símbolos,
limitação explícita desse controle.

## Avanço medido, sem confundir infraestrutura com tradução

A capacidade foi medida em plaintext conhecido: no cenário99equilibrado,
30/30testes atingiram95%de letras corretas, média98,03%. No99desigual,
apenas26/30passaram e a média foi86,20%. Portanto temos uma ferramenta
muito mais capaz em cenários específicos, mas ainda não uma autorização
científica para declarar negativa a família real de469. Veja
[P02](p02_execution.md) e o [gate](../results/p04_gate.json).

O inventário detectou que gritos do bibliotecário também reutilizam números
dos livros: `485611800364197` ocorre1vez e `78572611857643646724` ocorre6.
Somados à resposta Chayenne, mostram que não cabe impor NPC=wordcode e
livro=outro sistema como divisão universal. O grafo de compartilhamento de
8símbolos contém componentes68+2livros; três conjuntos são inviáveis nesse
limiar. Com12símbolos há66+2+1+1, mas conjuntos pequenos e sobreposições
menores permanecem. Não há novos textos cegos. [P01/P05](p01_p05_execution.md).

A comparação gerativa paga explicitamente o dicionário aprendido só em
descoberta e seus tokens. Cópia custa21.296bits nos dígitos, contra35.386do
Markov1; emrow0,14.650contra19.158. No controle de potência, porém, cópia
domina tanto12/12montagens sem mensagem como12/12montagens de inglês real
cifrado. Uma regra simplista de classificar toda vantagem de cópia como
não linguagem erra todos esses positivos. Isso limita **este** critério;
não refuta sozinho todas as análises upstream. Um modelo de contexto acertou
21/61códigos reservados contra6/61da marginal, avanço mecânico exploratório
em conjunto já exposto e dependente. [P03](p03_execution.md).

A arqueologia encontrou a matriz antiga inteira num post datado pelo fórum
em26/12/2007. É evidência textual nova para nossa investigação, mas obtida
num HTML atual potencialmente editável e atribuída pelo autor a outro fórum.
Não é screenshot autenticado de2007 nem data de edição do mapa. Localizamos
uma gravação catalogada deHellgate7.80/10Jan2007, ainda sem inspecionar o
trajeto e sem comprovar que mostra a sala. A janela23Ago–8Dec2010 continua
sem captura discriminante. [P06](p06_execution.md).

A leitura4×4 fixa ordena células pela quantidade de caveiras e usa oito
simetrias para desempate, sem busca livre de seeds. Seu positivo plantado
foi recuperado100%, mas os livros não produziram inglês nem vantagem sobre
os controles. Isso é resultado negativo da família finita, não prova de que
qualquer relação entre matriz e linguagem seja impossível. [P07](p07_execution.md).

## Decisões e próximos testes

1. Manter P04 bloqueado nesta versão; não retirar99desigual do gate nem reaproveitar os mesmos30plaintexts como teste cego de versão ajustada depois.
2. Em uma próxima versão do benchmark, estudar falhas de ótimos locais e incompatibilidade do pontuador nos dados agora de desenvolvimento, reservando textos e chaves de qualificação novos antes de alterar o algoritmo.
3. Para significado ou ausência dele, exigir discriminadores que também reconheçam prosa cifrada copiada; compressão isolada e ganho contextual não bastam.
4. Priorizar a inspeção da gravação histórica candidata e fontes externas realmente novas. Uma transcrição de2007 aumenta a base histórica, sem provar coordenação com o rename.

Os fontes do solucionador e protocolo de qualificação ficaram inalterados
após a abertura dos resultados. A cópia de checkpoint local pode indicar
`complete:false` mesmo após180ajustes: ela é um snapshot temporário. A saída
canônica concluída é `results/homophonic_benchmark.json`, com `complete:true`.
Nenhum de seus180ajustes usou os livros deTibia como entrada de otimização.

## Reprodução

Python3.11+, NumPy e compilador `g++` C++17. Fontes públicas fixadas podem
ser obtidas por `python scripts/bootstrap_sources.py`. Depois:

```sh
make round3
make test
```

A qualificação pode levar alguns minutos. Não há dependência deGPU. A pesquisa
histórica é preservada por metadados, URLs, hashes e registro de consultas;
reabrir páginas dinâmicas não garante obter o mesmo HTML. Resultados completos,
protocolos e código estão versionados. O total de traduções verificadas
permanece **zero**.
