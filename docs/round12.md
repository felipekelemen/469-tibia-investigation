# Décima segunda rodada: mesmos dígitos, mas não os mesmos códigos

**Nenhuma tradução foi encontrada.** Os 137 dígitos de Kharos têm exatamente
o mesmo histograma do livro de ID22 de Hellgate, também catalogado na Isle
of the Kings. Porém, não há maneira de escrever Kharos permutando exatamente
os 70 códigos importados desse livro, mesmo permitindo mudar as omissões de
zeros. Dois algoritmos independentes concordam na incompatibilidade.

## Pista, fonte e limites

A revisão de [The Hellgate's Averages](https://www.tibiasecrets.com/article166),
de Bacca Chewie, motivou conferir a relação entre os dois livros. Recalculamos
os dados originais, sem aceitar a conclusão semântica da publicação. Igualdade
de médias sozinha não demonstra igualdade de histogramas; neste par, a
igualdade mais forte de fato ocorre:

|Dígito|0|1|2|3|4|5|6|7|8|9|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|Contagem em cada livro|6|24|15|4|9|18|15|17|17|12|

Ambos têm 137 dígitos e soma 645. Entre os 70 textos, ID22 é o único com
esse histograma de Kharos. A [transcrição indexada do livro 6512889672](https://tibia.fandom.com/wiki/6512889672_%28Book%29)
coincide nos 137 dígitos e atribui localizações em Hellgate e Isle of the Kings.
Trata-se de concordância de transcrição, sem autenticar captura no cliente,
cronologia ou linhagem independente da fonte.

Isso é uma pista conhecida em literatura, agora reproduzida nesta investigação.
Não é descoberta de um texto novo ou de uma chave. A igualdade conserva
apenas as frequências dos dígitos e admite muitas permutações incompatíveis
com a camada intermediária importada.

## Hipóteses congeladas

O livro ID22 tem 70 códigos fornecidos, oito ocorrências com zero inicial e
três omissões. Seu alinhamento com os dígitos é único. Antes de executar os
novos parses, fixamos duas hipóteses em `data/conserved_code_protocol.json`:

1. **Conservação de códigos e formas escritas:** cada token da origem é
   reutilizado exatamente uma vez, com os mesmos dígitos e omissões; muda a ordem.
2. **Conservação somente dos códigos:** cada código da origem é reutilizado
   exatamente uma vez; cada código 0d pode preservar ou omitir seu zero.

Na segunda hipótese, o comprimento de 137 dígitos exige exatamente três
omissões em qualquer ordem de 70 códigos, mas suas posições não são dadas
ao parser. Não são permitidos novos códigos, trocas entre homófonos, reversões
internas, deleções ou inserções adicionais. Não supomos que o código fornecido
seja uma letra inglesa.

Todos os dados do jogo, inclusive a relação de histogramas, já estavam
expostos antes do congelamento. Kharos entra no parser somente como raw,
sem uma sequência alvo de códigos ou pontuação inglesa. O número e o
inventário dos códigos vêm da hipótese de conservação da **origem**.

## Algoritmos e verificação independente

O primeiro método usa programação dinâmica exata. Seu estado contém a
posição raw e quantas cópias de cada item da origem ainda podem ser usadas.
As transições consomem somente formas escritas permitidas que coincidem
com o próximo trecho do alvo. Todos os alinhamentos compatíveis da origem
são considerados, com deduplicação de inventários iguais.

Um milhão de estados é o limite fixado. Atingi-lo retorna **inconclusivo**,
nunca incompatível. Para saídas, guardamos até 256 streams distintos;
enumeração incompleta impede alegar unicidade. Contamos caminhos de
omissão/segmentação, que podem compartilhar a mesma sequência de códigos.

O método independente não usa essa recorrência: enumera as posições dos
tokens de um dígito entre os 70 tokens do alvo. São `C(70,3) = 54.740`
possibilidades. Cada uma determina um parse raw; comparamos seu inventário
com o da origem. A independência é de implementação do teste mecânico, não
uma validação semântica ou fonte externa de plaintext.

## Positivos: capacidade de recuperar uma conservação verdadeira

Geramos 30 permutações dos tokens de ID22, com formas escritas preservadas,
e 30 após redistribuir suas três omissões entre as oito ocorrências elegíveis.
Cada construção tem uma sequência verdadeira conhecida. São controles
mecânicos derivados de uma única origem, não 60 mensagens inglesas ou
amostras independentes do jogo.

O gate de viabilidade exige aceitar todos os positivos pertinentes, com
contagem completa. O gate separado de recuperação exige uma saída completa,
única e exata em pelo menos 27/30. Aceitar uma possibilidade não basta para
recuperar a sequência verdadeira.

|Condição positiva|Modelo|Viáveis completos|Recuperações únicas exatas|
|---|---|---:|---:|
|Permutar tokens escritos|Conservar códigos e formas|30/30|28/30|
|Permutar tokens escritos|Conservar códigos|30/30|28/30|
|Redistribuir omissões e permutar|Conservar códigos|30/30|28/30|

Os três gates pertinentes passam. Como diagnóstico, conservar formas
escritas não aceita nenhum dos 30 controles com omissões redistribuídas;
esse modelo não era obrigado a aceitá-los. Os dois casos ambíguos em cada
condição pertinente não são contados como erros semânticos ou textos sem
sentido. O gate qualifica apenas este cenário de origem/inventário fornecido.

## Kharos: rejeição das duas hipóteses

|Modelo|Resultado|Estados examinados|Contagem completa|
|---|---|---:|---|
|Conservar códigos e formas|Incompatível|2|Sim|
|Conservar códigos, omissões livres|Incompatível|177|Sim|
|Enumeração independente de omissões|0 soluções em 54.740 padrões|—|Sim|

Há uma contradição simples para o primeiro modelo: o início de Kharos é
`5159...`. A única forma escrita da origem que pode iniciar esse texto é
`51`. Depois dela, nenhuma forma escrita disponível pode iniciar `59...`.
O modelo mais permissivo precisa da busca completa; também não encontra parse.

Não houve relaxamento posterior, chave reajustada ou escolha por palavras
aparentes. O gate de exibição de uma leitura V4 fixa não foi acionado:
**não há sequência de códigos nem saída inglesa para Kharos nesta rodada**.

O resultado exclui somente a permutação exata dos **códigos importados de
ID22** sob essas regras. Não exclui permutação de dígitos, cortes em códigos,
outros códigos para o mesmo símbolo, outra tokenização, outra mensagem ou
outra cifra. Tampouco demonstra que a camada importada seja falsa.

## Controles de ordem e demais anagramas do corpus

Foram executados 99 embaralhamentos de dígitos e 99 de blocos de oito sobre
Kharos, preservando seu comprimento e histograma. Ambos os modelos rejeitam
todos. Assim, a inviabilidade do alvo não o distingue desses controles e
não é evidência de ausência de linguagem. Os testes positivos estabelecem
que o código aceita conservações verdadeiras quando fornecidas.

Entre os 70 livros existem cinco grupos de dois com histogramas raw iguais:
`2/23`, `3/4`, `11/36`, `58/59` e `60/64`. Testamos as duas direções de cada
par, sem dar a sequência alvo importada ao parser. Nenhum par tem o mesmo
histograma dos códigos importados.

Nove das dez direções são incompatíveis com ambos os modelos. Na direção
58→59, ambos encontram um stream único de **139 códigos**, enquanto a
reconstrução importada de 59 tem **138**. O stream alternativo também produz
outra sequência de rótulos da camada 14. Isso não permite decidir qual é o
stream do autor; mostra que unicidade sob uma hipótese forte não autentica
a hipótese nem transfere automaticamente a camada publicada. Não produzimos
uma leitura inglesa desse caso.

## Material externo: Your True Colour

A pesquisa de origem também identificou uma lacuna em nosso inventário:
a questão 10 do artigo oficial [Your True Colour](https://www.tibia.com/news/?fbegind=9&fbeginm=1&fbeginy=2012&fendd=8&fendm=2&fendy=2012&flist=01011111&id=1975&subtopic=newsarchive),
de 8/2/2012, contém `78567 34334 989 135 65142`. A busca no domínio oficial
retorna a questão e suas quatro alternativas; a abertura direta da página
pela ferramenta web retornou 403. A transcrição numérica também consta em
espelho indexado do Portal Tibia. Registramos essa diferença de acesso.

Nenhum trecho de cinco ou mais dígitos dessa sequência de 21 dígitos aparece
nos livros; há um 4-grama compartilhado entre suas 18 janelas. Isso não
estabelece independência transformada ou outro sistema de cifra. A sequência
já era pública e examinada upstream, portanto não é um holdout semântico cego.
As alternativas do quiz são reações possíveis; não fornecem uma tradução
explicitamente atestada para a questão.

O livro `74032 45331` permanece candidato de transcrição secundária: o índice
confirma seu título, mas a página ficou em 403 e seu corpo não foi
independentemente inspecionado. Não promovemos esse conteúdo a nova evidência
canônica ou a tradução. O registro está em `data/source_review_round12.json`.

## Decisão e reprodução

Registrar como negativo o mecanismo de conservar o inventário de códigos
de ID22 para ler Kharos. Não acrescentar trocas, deleções ou anagramas livres
até aparecer uma leitura. A igualdade de dígitos continua útil para testar
uma futura regra de transposição ou serialização explicitamente proposta;
ela não escolhe essa regra sozinha.

As prioridades semânticas continuam sendo uma equivalência externa atestada
ou uma regra independente de formação de códigos. A coleta histórica das
matrizes permanece aberta; não obtivemos nova captura nesta rodada. Nenhum
dos quatro entregáveis principais pendentes passou a concluído.

```sh
make round12
make test
```

O verificador reproduz todos os 60 positivos, os 198 controles, os dez pares
reais e a enumeração de 54.740 padrões. Também testa a implementação
independente em quatro controles positivos para impedir uma falsa rotina que
sempre devolva zero soluções. Os testes unitários incluem confronto com
enumeração exaustiva pequena, omissões ambíguas e tratamento dos limites.
Resultados completos: `results/conserved_code_experiment.json`.
