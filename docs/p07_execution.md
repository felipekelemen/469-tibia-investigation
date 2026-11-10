# P07 executado: leitura 4×4 ordenada pelas caveiras

Foi congelado o protocolo `data/protocols/matrix_walk_v1.json` antes de obter
as pontuações desta rodada. O corpus é público e já foi visto: essa precedência
local não transforma a análise em confirmação prospectiva.

A hipótese explícita é que as quantidades das caveiras ordenam posições de
blocos de16 símbolos. Empates usam uma varredura geométrica fixa, entre oito
simetrias do quadrado; direção de ordenação e leitura direta/inversa são
predefinidas. Testamos as duas matrizes e três representações: rótulos row0,
códigos módulo26 e códigos menos1 módulo26. São192 configurações, sem bônus
para BEHOLDER/BONELORD, sem ajuste de seeds e sem preencher caudas: o sufixo
incompleto permanece intacto. O estado reinicia a cada livro.

Selecionamos a configuração no grupo de68 livros e aplicamos aos dois livros
reservados conhecidos. O melhor foi a matriz posterior, geometria6, ordem
ascendente, direta, camada de símbolos: treino−6,345665 e reservado−6,595400.
Não há inglês coerente. Em39 controles por blocos de8, com a seleção inteira
repetida, **p=0,75**. Outros39 controles embaralham homofones dentro de cada
símbolo/livro: **p=1,0**. Esse segundo nulo mantém exatamente a camada de
símbolos, portanto todos os candidatos que só a utilizam ficam inalterados;
seu p não é um teste de potência para esses candidatos.

Um positivo externo cifrado com uma permutação da família foi recuperado
sem fornecer a chave ao seletor:100% de1.000 caracteres reservados. Isso
verifica uma chave plantada da família e o escore básico, não qualifica busca
de transposição arbitrária nem substitui o benchmark homofônico de P02.
Três testes automatizados verificam ordenação conhecida, oito geometrias e
roundtrip com caudas de comprimentos diferentes.

O resultado negativo cobre apenas esta família finita. Não há evidência
histórica de que as caveiras sejam ordem de leitura; a análise é uma hipótese
explícita de baixa complexidade. Não valida ligação com a renomeação. Nenhuma
saída foi promovida a tradução e nenhuma nova grade foi ajustada ao resultado.
Reprodução: `python scripts/matrix_walk_experiment.py`.
