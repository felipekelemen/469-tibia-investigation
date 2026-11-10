# Segunda rodada: substituição homofônica com controles de otimização

**Resultado: nenhuma tradução verificada.** A vantagem de pontuação em treino
contra sequências com códigos embaralhados diminui quando os controles
preservam exatamente os bigramas. O conjunto reservado não mostra vantagem
convincente. Além disso, o orçamento não recupera prosa nem sequer no controle
positivo sintético: não temos poder para excluir a família homofônica.

## Modelo, seleção e orçamento

`python scripts/homophonic_controls.py` reutiliza o pontuador de tetragramas de
`cipher_battery.py`, treinado nos primeiros 80% de *Alice's Adventures in
Wonderland*. O corpus numérico não ajusta o pontuador. Um mapa arbitrário de
100 códigos para 26 letras é ajustado só nos 68 livros de descoberta; os livros
20 e 54 ficam reservados, com 61 códigos no total. Blocos de tetragramas não
cruzam livros. O mapa que maximiza o treino é aplicado ao conjunto reservado,
sem alteração posterior.

O algoritmo de annealing é exatamente o usado na primeira rodada. Cada ajuste
recebe dois reinícios de 5.000 mutações, tanto nos dados quanto nos nulos e no
controle positivo. As sementes são distintas e registradas pelo código a partir
da semente principal 23469478. Foram executados 40 ajustes: observação, 19 nulos
de embaralhamento marginal, 19 nulos de bigramas e um positivo. Tempo registrado:
25,3 segundos nesta máquina; NumPy 2.3.5. Esse orçamento é curto e não pretende
aproximar o ótimo global.

## Nulos e o que preservam

1. **Shuffle por livro:** permuta os códigos completos; preserva comprimento e
   contagem de cada código. Não preserva bigramas, os zeros originais omitidos
   nem a repetição de motivos entre livros.
2. **Euler por livro:** cada transição de código é uma aresta dirigida de um
   multigrafo. As listas de arestas de saída são embaralhadas e Hierholzer
   constrói uma trilha euleriana iniciada no primeiro código original. São
   preservados exatamente comprimento, primeiro/último códigos, unigramas e
   bigramas dirigidos. A função verifica essas igualdades em cada amostra.
   A distribuição resultante **não é uniforme** sobre todas as sequências
   compatíveis; preserva menos informação que módulos longos ou motivos
   compartilhados entre livros.

Nos controles de bigramas, 66–68 dos 68 livros de treino mudaram. A sequência
reservada é curta e tem poucas alternativas: nenhuma das duas amostras mudou
em 5 das 19 réplicas; uma mudou em 9 e ambas mudaram em 5. Esse fato limita a
variabilidade do nulo. Ambos os livros reservados apresentaram sequências diferentes
em cada controle marginal. Cada réplica recebe sua própria otimização em treino;
portanto não se compara mapa ajustado nos dados a mapas aleatórios não ajustados.

## Resultados reais

Escores são médias de log10 da probabilidade dos tetragramas, maior é melhor.
`p` de cauda superior usa `(1 + controles >= observado)/(1 + 19)`; resolução
mínima 0,05. Há múltiplas métricas exploratórias, sem correção de comparações.
Nenhum desses valores é probabilidade de uma tradução estar correta.

| Medida | Observado | Média shuffle | Média bigramas |
|---|---:|---:|---:|
| Treino | -5,6439 | -6,1399 | -5,8103 |
| Reservado | -5,9035 | -6,2045 | -5,9089 |
| p do escore de treino | — | 0,05 | 0,10 |
| p do escore reservado | — | 0,20 | 0,45 |

O ganho treino menos reservado do observado é 0,2596. Os p desse ganho são
0,30 contra shuffle e 0,20 contra bigramas; essa métrica descreve sobreajuste,
não evidência semântica. A saída reservada literal é:

```
livro20: EANOOUOTENTTELTORENEOTHTSLLGHLAL
livro54: ETENTTELTORENEOTHTSLLGHLALSDT
```

Essas sequências não constituem uma tradução e não receberam reparos,
segmentações ou interpretações narrativas.

## Controle positivo e poder do método

Reservamos os últimos 20% de Alice, que não ajustaram o modelo de inglês.
Cada letra recebe dois homofones disjuntos: A→00/01, B→02/03, ..., Z→50/51.
A escolha do homofone é aleatória por ocorrência. O positivo usa os mesmos
comprimentos de livros, separação de treino e reservado e orçamento de busca.
Assim, a chave verdadeira existe e é conhecida, mas não é fornecida ao ajuste.

- Decodificação pela chave verdadeira: recuperação exata em todos os trechos.
- Busca sem chave: 26/61 letras reservadas corretas, **42,6%**.
- Escore reservado pela chave verdadeira: -4,1545.
- Escore reservado pela chave estimada: -5,2310.
- A saída estimada não recupera prosa coerente.

Isso demonstra alguma recuperação parcial e, sobretudo, insuficiência para o
critério exigente de tradução. O positivo tem só 52 códigos possíveis, menos
que os 99 do corpus. Mesmo esse caso mais simples não foi resolvido pelo
orçamento. Logo a falha nos livros não permite rejeitar substituição
homofônica. A próxima melhoria algorítmica deve primeiro resolver positivos
externos com diferentes sementes, homofones e textos, antes de retornar aos
livros com orçamento e seleção congelados.

## Reprodutibilidade e limites

As saídas completas, mapas e réplicas estão em
`results/homophonic_controls.json`. Os quatro testes em
`tests/test_homophonic_controls.py` verificam:

- contagens e extremidades da trilha Euler em casos ramificados, degenerados,
  unitários e vazios;
- capacidade de produzir trilhas diferentes quando há liberdade;
- geração e decodificação exata do positivo com uma chave conhecida;
- preservação do objeto original e das contagens pela transformação nula.

O holdout contém um único componente de livros correlacionados. Permanecem
repetições menores que 16 dígitos, possíveis relações transformadas, uso global
do corpus na tokenização upstream e ausência de plaintext oficial. Os controles
são testes de um modelo específico e de um algoritmo curto, não teste completo
de linguagem, de homofonia ou de qualquer mensagem oculta.
