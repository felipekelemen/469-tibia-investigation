# Solucionador homofônico V2 — estudo com novos autores

V1 e sua qualificação permanecem intactos:99códigos desiguais falhou em26/30
contra o mínimo27. Não removemos esse cenário nem alteramos seu resultado.
Os fixtures já abertos passaram a ser explicitamente desenvolvimento.

## Alteração escolhida no desenvolvimento

V2 executa dois bancos independentes da busca V1, cada um com8reinícios de
100.000iterações. A semente do segundo banco é a do primeiro mais1.000.003.
Escolhe-se exclusivamente o maior objetivo regularizado **de treino**;
empates favorecem o primeiro banco. O objetivo, C++, pontuador Alice,
temperatura12 e peso de frequência2.0 não foram alterados. O custo de busca
é aproximadamente o dobro; a melhoria não é gratuita nem comparação com
orçamento idêntico. O primeiro banco fornece um baseline pareado no novo teste.

Em desenvolvimento, o segundo banco recuperou três das quatro falhas graves
abertas de V1 com acerto superior a98%. A quarta continuou falhando(0%).
Três casos adicionais anteriormente bons continuaram superiores a95%.
Esses sete casos foram escolhidos com conhecimento do resultado e **não**
constituem nova qualificação. Em um caso adicional o segundo banco foi
péssimo, mas perdeu no objetivo de treino; a seleção não consultou o acerto.
Saída completa: `results/homophonic_v2_development.json`.

## Nova qualificação

Antes de abrir os resultados, congelamos `data/homophonic_benchmark_v2_protocol.json`.
Usa30excertos disjuntos de dois autores novos:15deH.G.Wells e15deCharlesDickens.
Nenhum desses autores foi usado no desenvolvimento ou na qualificaçãoV1.
O treino tem5.668letras e o teste1.024; os30plaintexts são reutilizados nos
seis cenários52/75/99×equilibrado/desigual, portanto não são180textos
independentes. Também não são30autores: continuam existindo dependências de
estilo e frases. Chaves e sementes são novas e registradas.

O gate permanece95%de letras corretas em pelo menos27/30fixtures por cenário,
exigindo todos os seis cenários. Hashes abrangem também a implementação do
pontuador, além de wrappers, C++, gerador e textos. Os arquivos Gutenberg são
preservados byte a byte, com licenças originais; `.gitattributes` impede sua
normalização. O solver não recebe plaintext, chave verdadeira nem códigos de
teste. O resultado contém a avaliação do primeiro banco e a seleção V2,
permitindo comparar o ganho e as perdas sem retreinar.

Este é um segundo estudo planejado após a falha de V1, não uma prova com
controle sequencial de erro estatístico. O gate é uma condição operacional
necessária para esta pipeline. Mesmo se passar, não prova que469seja uma
cifra homofônica ou que uma saída inglesa esteja semanticamente correta.
Não serão ajustados parâmetros olhando essa qualificação. Uma nova versão
exigirá novamente dados de teste não usados para ajustá-la.

## Resultado da qualificação V2

Todos os seis cenários passaram:30/30fixtures em cada um atingiram pelo menos
95%de letras corretas. No cenário99desigual, a média foi98,59%. A duração foi
553,74segundos nesta máquina. O primeiro banco isolado também passaria nos
seis cenários desta amostra nova(29,29,27,28,28,29fixtures), sem alterar a falha
histórica deV1. A comparação pareada é180/180paraV2contra170/180no primeiro
banco:10melhorias,nenhuma regressão e170empates. O custo é aproximadamente
o dobro. Essa comparação distingue o benefício do banco adicional da mudança
de autores entre as qualificações, sem atribuir todo ganho apenas ao algoritmo.

### Sensibilidade adicional à prosa copiada

Um protocolo exploratório separado, congelado antes das saídas desse teste,
montou oito motivos de256letras de Frankenstein, cifrados uma vez e copiados
como sequências numéricas. Foram12fixtures, não um novo gate de30. Somente
8/12atingiram95%de acerto; o pior ficou em46,19%. Esse teste usa dados de
 desenvolvimento e mostra que a qualificação em prosa comum não garante poder
para todo cenário de cópia. Não alterou os parâmetros nem o gate formal.

Repetimos exatamente o pior caso para diagnóstico, sem nova semente. A chave
verdadeira teve objetivo−25.681,78, contra−29.538,18da chave encontrada:
uma diferença de3.856,40a favor da verdade. Isso identifica insuficiência de
busca nesse caso selecionado, não incompatibilidade do objetivo nesse caso.
Não é diagnóstico universal nem nova qualificação. Cópias cifradas e outros
mecanismos permanecem possíveis; uma falha de leitura nos livros não poderá
ser promovida a rejeição irrestrita de homofonia.

## Aplicação condicional aos livros

O protocolo `data/protocols/qualified_search_v2.json` também foi congelado
antes dos novos resultados. Se V2 não passar globalmente, o script encerra
antes de ler/ajustar os livros. Se passar, executa uma busca exploratória,
com os mesmos dois bancos, sobre os códigos reconstruídos importados e
99réplicas por nulo: shuffle por livro, bigramas Euler e blocos8.
Cada réplica recebe ajuste completo com orçamento idêntico. O reservado
antigo de61códigos já foi exposto e pertence a um componente correlacionado:
jamais será chamado de validação prospectiva independente. Nulos Euler podem
não alterar livros curtos e sua distribuição não é uniforme sobre trilhas.
Não aceitar tradução por escore ou p pequeno e não reparar as saídas à mão.

## Reprodução

```sh
python scripts/homophonic_benchmark_v2.py --run
python scripts/qualification_gate_v2.py
python scripts/qualified_tibia_search.py --run
```

Os comandos de run recusam sobrescrever silenciosamente resultados existentes;
para uma réplica, usar checkout separado e retirar apenas os JSONs de saída
correspondentes, preservando os protocolos. Não executar `--freeze` sobre
estudos já congelados. Os testes verificam seleção por objetivo de treino,
baseline pareado, fontes novas, intervalos sem sobreposição, chave conhecida,
cobertura de códigos e preservação de frequências/bigramas nos controles.
