# Quinta rodada — prosa copiada, pontuador amplo e nova busca controlada

**Nenhuma tradução verificável foi encontrada.** O solucionador ficou mais
capaz nos controles positivos, e a busca nos livros apresentou um sinal de
tetragramas superior aos três nulos testados. A saída literal, porém, continua
sem prosa inglesa compreensível. Pontuação e significância não foram
promovidas a tradução.

Nesta rodada, V3 e V4 são versões do solucionador, não números de rodadas.
A falha da primeira versão testada nesta etapa foi preservada. O estudo
seguinte usou outros autores e chaves, sem reutilizar a qualificação aberta.

## Duas alterações, duas qualificações

V3 ampliou o pontuador para seis autores já abertos, com586.447tetragramas,
sem mudar o orçamento nominal de dois bancos de8reinícios×100.000iterações.
Os12casos antigos de desenvolvimento passaram todos; isso não era validação.
Em qualificação nova com Stoker/Melville, o cenário de sequências numéricas
copiadas passou em24/30contra mínimo27, enquanto os outros dois modos
passaram em30/30. V3foi bloqueado: zero novos ajustes deTibia nessa versão.

No baseline pareado, V2passou em13/30dos mesmos casos copiados; V3teve
28melhorias e2regressões. O novo pontuador e as marginais dele derivadas
melhoraram esse conjunto, sem demonstrar qualificação global.

Sem ajustar mais chaves, recomputamos o objetivo verdadeiro e o das seis
falhas. Em todas, a chave verdadeira tinha pontuação maior, com diferenças
de1.336,57a6.281,19. Cinco tinham zero códigos não vistos no teste e uma
apenas duas posições não vistas. Portanto há testemunhas de insuficiência
dessa busca; não é uma prova de que o objetivo jamais prefira uma chave errada.

Essas seis falhas e três guardas passaram a desenvolvimento. Temperaturas
máximas40/80/120aprovaram6/9,7/9,9/9. Escolhemos120antes da próxima qualificação,
congelando novamente código, dados e configuração. O pontuador amplo, C++,
bancos e número de propostas ficaram iguais. Mais movimentos aceitos podem
alterar o tempo real; igualdade nominal não é promessa de CPU idêntica.

A qualificaçãoV4 usou MarkTwain eCharlotteBrontë, não presentes no pontuador,
com30fixtures por modo e o mesmo critério95%de letras em pelo menos27/30:

|Modo|Aprovações|Média de letras corretas|
|---|---:|---:|
|Sequências numéricas copiadas|30/30|98,63%|
|Texto copiado, homofones novos por ocorrência|30/30|99,35%|
|Prosa comum|30/30|99,52%|

O baseline de temperatura12passaria em29/30dos mesmos casos copiados novos;
V4teve duas melhorias e28empates. Não é correto atribuir a comparação24→30
somente à temperatura, pois essa comparação troca autores e chaves. A diferença
pareada é29→30. O gate é operacional em estudos sequenciais, não uma garantia
populacional universal de sucesso.

Os modos copiados compartilham motivos, mas usam ordens e chaves diferentes:
seus resultados não isolam causalmente apenas a renovação de homofones. As
janelas de origem de fixtures diferentes são disjuntas, mas há dois autores
por estudo, estilo compartilhado e conteúdos pareados entre modos. Não são
90autores nem90plaintexts independentes. Os cenários têm oito motivos de256
letras e99códigos desiguais; não cobrem todas as distribuições/reutilizações
possíveis dos livros. [Detalhes e reprodução](copied_solver_v3_v4.md).

## Aplicação V4 aos livros

O protocolo foi congelado antes da qualificação nova, condicionado à sua
aprovação. SomenteV4 liberou o ajuste. Selecionamos pelo objetivo de treino
nos68livros de descoberta e aplicamos aos dois livros reservados antigos,
com61códigos correlacionados. Esse recorte já foi exposto em várias rodadas e
não se tornou prospectivo. O mapa/stream de códigos com zeros restaurados
continua sendo uma representação importada, informada por todo o corpus.

Executamos1ajuste real e297nulos reotimizados com o mesmo orçamento. A
estatística é o escore de tetragramas do reservado, não acerto de tradução:

|Nulo|Réplicas|p superior|Réplicas sem mudança nos dois livros reservados|
|---|---:|---:|---:|
|shuffle|99|0,01|0|
|bigrams|99|0,01|15|
|blocks8|99|0,02|1|

p=(1+nulos>=observado)/(1+99). O valor0,01é a resolução mínima, não p<0,01.
São valores exploratórios do protocolo local, sem correção pela sequência
histórica de estudos. A busca é refeita em cada nulo, mas nenhum desses
controles preserva integralmente todos os motivos longos e sua montagem.
Euler não amostra uniformemente todas as trilhas compatíveis. Essas
limitações impedem converter os p em probabilidade de texto correto.

O sinal é mais forte que na rodada anterior. Não o descartamos como se
fosse inexistente: registramos enriquecimento da estatística, compatível com
estrutura de ordem superior ou módulos que os nulos destroem. Isso ainda
não distingue esses mecanismos de uma mensagem semântica. A prosa cifrada
copiada também contém módulos; controle de cópia não significa automaticamente
controle sem linguagem.

A saída literal do reservado é:

```text
TSICASAWREYALHEATHERMABELIESTOTE
LWREYALHEATHERMABELIESTOTERES
```

Não inserimos/deletamos letras, anagramas ou reparos para transformá-la numa
narrativa. Fragmentos reconhecíveis não satisfazem a exigência de inglês
coerente em conteúdo independente. Não há plaintext oficial pareado nem
previsão verificada de uma nova amostra469.

Os escores brutos não devem ser comparados diretamente aos antigos, pois
mudou o pontuador. O resultado relevante é a comparação com nulos sob a mesma
configuração e a ausência atual de uma leitura validada. Também não rejeitamos
toda homofonia ou a possibilidade de outros níveis de codificação.

## Decisão e próximo passo

O gargalo específico de potência em cenários copiados foi reduzido no escopo
medido; o projeto agora tem um método que recupera esses positivos e um sinal
estatístico mais forte nos livros. O objetivo da missão continua aberto.

O próximo experimento prioritário deve localizar de onde vem esse sinal:

1. Separar contribuição interna dos módulos de sua ordem de montagem, aprendendo inventários só na descoberta. Permutar módulos inteiros testa ordem além dos módulos; não refuta significado dentro deles.
2. Avaliar coerência com critério independente dos tetragramas que selecionaram as chaves, qualificado antes em prosa cifrada copiada e pseudoinglês com estatísticas locais semelhantes. Qualquer segmentação só pode adicionar fronteiras, nunca reparar letras; cobertura de dicionário isolada não valida texto.
3. Reservar conteúdo469realmente novo e atestado antes de testar candidatos. Os61códigos atuais não permitem demonstração forte de generalização, mesmo se surgir pontuação excelente.

Continuar aumentando o mesmo escore nos mesmos dados não basta. Nenhuma
dessas decisões é prova universal de ausência de mensagem. Traduções
verificadas nesta rodada e no projeto: **zero**.

## Reprodução

```sh
make round5
make test
```

O target verifica resultados já concluídos sem refazer ajustes. Para réplica,
usar checkout separado e retirar apenas os JSONs finais correspondentes,
preservando protocolos e hashes. As qualificações e controles levam alguns
minutos. Dados, licenças originais, mapas, sementes e todas as réplicas estão
versionados; o compilador é g++C++17, com Python eNumPy. Os fontes deV1/V2,
seus testes congelados e resultados anteriores ficaram intactos.
