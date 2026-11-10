# Primeira bateria: matrizes de Hellgate

As matrizes são as fornecidas pelo usuário. Sua data e origem histórica precisam
ser demonstradas separadamente; estes testes não autenticam as matrizes.

## Resultado matemático demonstrado

| Matriz | Determinante inteiro | mod 10 | mod 26 | mod 27 | mod 29 | mod 256 |
|---|---:|---|---|---|---|---|
| Antiga | −7 | invertível | invertível | invertível | invertível | invertível |
| Posterior | −18 | singular | singular | singular | invertível | singular |

Uma matriz inteira é invertível módulo m exatamente quando gcd(det,m)=1.
Portanto, a matriz posterior **não é uma chave reversível de Hill padrão** nos
domínios completos mod 10, 26, 27 ou 256. Isso não exclui uma função restrita a
um subconjunto, um módulo diferente ou uma composição com camadas adicionais.
A antiga satisfaz essa condição necessária, que por si só não evidencia uso
criptográfico.

Exemplo construtivo em A=0, módulo26: a posterior transforma tanto AAAA
([0,0,0,0]) quanto NNAA ([13,13,0,0]) em AAAA. Logo, pelo menos esses dois
blocos distintos são indistinguíveis sem informação externa.

## BEHOLDER, BONELORD e 3478

Foram codificados BEHOLDER com a antiga e BONELORD com a posterior, em blocos
de quatro letras, módulo 26, A=0 e A=1, vetores coluna e linha. Os vetores
numéricos completos estão em `results/matrix.json`. Os dois nomes não produzem
o mesmo criptograma na convenção de coluna para nenhuma das duas bases.
Isso rejeita somente essa equivalência específica, não uma relação histórica
ou uma equivalência sob um algoritmo diferente.

Tratando 3478 como o vetor de quatro dígitos [3,4,7,8], foram computadas as
imagens diretas em todos os cinco módulos e as inversas quando existem. Um
bloco de quatro símbolos Hill continua contendo quatro símbolos. Não pode
produzir BEHOLDER ou BONELORD, de oito letras, sem uma regra de expansão
adicional. Tratar 3478 como inteiro ou identificador de conceito exige outro
modelo e não é refutado pelo teste.

## Busca limitada no corpus

O arquivo `sources/s2ward/books.json` é identificado por SHA-256 no resultado.
Foram examinadas 144 combinações pré-definidas: matriz, orientação, direção
direta/inversa (somente se válida mod26), grupos de um ou dois dígitos, todos
os offsets de alinhamento de dígitos e de bloco, bases de entrada 0 e 1.
Saídas usam A=0, Z=25. Valores de entrada ≥26 são explicitamente reduzidos
módulo26. Não há preenchimento: sufixos incompletos são descartados e a
quantidade de dígitos aproveitados é registrada. Blocos não cruzam livros.

O escore é a fração de posições que coincidem com 26 trigramas ingleses comuns
fixados no código. Não é um detector de inglês coerente. Cada um dos 39
controles embaralha independentemente os dígitos **dentro de cada livro**,
preservando comprimento e frequência exata. Repete-se a busca inteira e usa-se
o máximo: isso controla a seleção entre as 144 variantes para esse nulo.

O máximo observado foi 0,00445355, contra máximos dos controles entre
0,00240429 e 0,00384686; p empírico = 1/40 = 0,025, a resolução mínima deste
ensaio. Isso evidencia estrutura destruída pelo embaralhamento, **não uma
tradução**. Repetições longas no corpus podem repetir os poucos trigramas
favoráveis e são uma explicação concorrente. Os controles não preservam esses
fragmentos e os livros não podem ser considerados observações independentes.

Controles adicionais mudam a interpretação desse primeiro sinal:

| Nulo (39 réplicas cada; seleção do máximo repetida) | p empírico |
|---|---:|
| Embaralhamento individual de dígitos por livro | 0,025 |
| Permutação bijetiva global dos rótulos 0–9 | 0,275 |
| Embaralhamento de blocos de 16 dígitos por livro | 0,375 |

A permutação global preserva exatamente todas as igualdades, repetições e
sobreposições do corpus, bem como o espectro das frequências; troca qual rótulo
tem cada frequência. O controle em blocos preserva contagens exatas dos dígitos
e motivos internos aos blocos; inclui na permutação eventual bloco final curto,
portanto não preserva todas as fronteiras/alinhamentos nem módulos completos.
Sementes: 3478 e 160469, respectivamente. Em ambos, a vantagem observada deixa
de ser rara. Não há evidência neste ensaio de que os valores numéricos das
matrizes/dígitos produzam inglês; o sinal contra dígitos individuais
embaralhados é compatível com a estrutura repetitiva existente.

Prévia do melhor candidato, antiga transposta/direta, um dígito, base1:

```
HVPREEIKREOSJNTIABZAEAUFYKISVACTIJPGSBSRDQFNUMWMCRAQIJWIAYDPOXDEBXHIYNAMCRTNOMVNLULQHYJJFOKYNTXTSCBPFGFRBEKUHKWKSZWSDBUGWWCBVHLJIIUOIQIIWVWNUPMS
```

Nenhuma saída foi promovida a tradução. Este ensaio explora o corpus inteiro:
**não alega validação semântica em holdout**. Uma hipótese nova ajustada a
essas saídas precisa ser construída em dados de descoberta e avaliada em
fragmentos independentes, com critérios de inglês mais exigentes e controles
que preservem a estrutura de módulos repetidos. A contagem de candidatos
executados não é evidência de progresso semântico.

## Reprodução e testes

```
python scripts/matrix_experiments.py
python -m unittest discover -s tests -p test_matrix.py -v
```

Quatro testes passaram: vetor Hill de referência ACT→POH, inversas em módulos
compostos com roundtrip, rejeição de matriz singular e ausência de padding
implícito. São testes do algoritmo e de suas convenções; não validam nenhuma
interpretação linguística. A família não inclui todas as permutações, chaves
polialfabéticas, gramáticas de tokens nem qualquer algoritmo arbitrário.
