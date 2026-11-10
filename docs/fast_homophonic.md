# Solucionador homofônico incremental P02-v1

Este componente otimiza **apenas os códigos de descoberta** contra um
pontuador externo congelado. Não recebe plaintext, chave verdadeira, livros
reservados ou resultados de qualificação como entrada. A função não interpreta
sua saída como tradução. O benchmark separado mede recuperação real em
positivos; esta implementação, por si, não demonstra capacidade suficiente.

## Interface e compilação

```python
from fast_homophonic import solve
result = solve(train_sequences, table, seed=123,
               restarts=8, steps=100000)
mapping = result['mapping']  # lista de 100 inteiros, A=0,...,Z=25
```

`table` contém 26^4 log10-probabilidades de tetragramas, não treinadas no
plaintext de qualificação. A API aceita várias sequências e não pontua
transições entre suas fronteiras. Códigos inteiros 0–255 são suportados,
mas a configuração congelada usa 100 slots. Slots não observados no treino
retêm valores arbitrários e devem ter cobertura explicitamente reportada:
isso não constitui recuperação de uma chave nunca observada.

O C++ é compilado em biblioteca compartilhada por `g++ -std=c++17 -O3 -shared
-fPIC`. O cache em `/tmp` usa SHA-256 do fonte, das opções e da identificação
do compilador. O binário não é versionado. Compilador observado: `g++ (Debian
14.2.0-19) 14.2.0`. Não há `-ffast-math` nem instruções nativas específicas.
Tempos `runtime_seconds` excluem compilação e carregamento inicial.

Hashes congelados antes da qualificação:

- `src/homophonic_solver.cpp`: `0d71f35474df0e2c9f76a230ab67fb9c897440de280fabb53e782e01122132a1`.
- `scripts/fast_homophonic.py`: `a3d0cb37527f7fbec6069c193ba320a6464051b2c2a1f4f2cfbc777be68118cc`.

O protocolo externo também registra seus próprios hashes e impede alteração
dos arquivos de implementação durante a qualificação.

## Algoritmo e objetivo

Os tetragramas de códigos são agregados com suas multiplicidades. Cada código
possui uma lista dos tetragramas que ele afeta. Uma mutação reavalia somente
a união dessas listas, sem contar várias vezes um tetragrama que contém o
mesmo código em múltiplas posições. A pontuação usa a soma ponderada dos
log10-escores, evitando a temperatura excessiva em relação às minúsculas
diferenças de médias do protótipo Python anterior.

O objetivo congelado é:

```
S = soma(log10 P(tetragrama))
J = S - 2 * soma_a ((C_a - N*pi_a)^2 / (N*pi_a + 5))
```

`C_a` é a frequência decodificada da letra, `N` é o número de caracteres de
descoberta e `pi_a` é a marginal da primeira letra inferida do pontuador de
tetragramas normalizado. A penalidade desencoraja soluções degeneradas que
concentram códigos em poucas letras. É uma regularização, não um teste
estatístico de chi-quadrado. A função devolve `train_score=S/numero_de_ngrams`
e `objective=J` separadamente.

Os reinícios alternam inicialização aproximada por frequências, variantes
perturbadas, mapeamentos aleatórios e perturbação da melhor solução. Existem
três movimentos: reassociar um código (65% das escolhas), trocar os valores
de dois códigos (30%) e trocar dois grupos inteiros de letras (5%). Escolhas
que não alteram a chave são puladas; `steps` conta iterações propostas, não
somente movimentos efetivos. São quatro ciclos fixos de resfriamento e
reaquecimento por reinício, com temperatura máxima 12, fator 0,55 por ciclo,
resfriamento exponencial e piso 0,04.

Configuração congelada P02-v1: **8 reinícios × 100.000 iterações**, temperatura
12 e peso de frequência 2.0. Otimiza-se `J`, sem consultar acerto ou plaintext
para selecionar a chave dentro de um ajuste. O relatório também inclui
número de movimentos aceitos e divergência entre escore incremental e
recomputação integral da melhor solução.

## Desenvolvimento executado antes da qualificação

O pontuador primário continua sendo Alice, primeiros 80%, produzido por
`cipher_battery.english_model`. O texto de desenvolvimento é Frankenstein,
SHA-256 `2b97b7f8aad508649481d8dd4f6b54f9b965ddb3ba634e9151c815f537b49e42`.
Após remover o cabeçalho/rodapé Gutenberg e manter A–Z, usamos o intervalo
iniciado no offset 5000: 5668 letras de treino e 1024 posteriores para avaliar
a recuperação de desenvolvimento. Esses dados foram usados para escolher
hiperparâmetros e **não** são qualificação independente.

Uma série inicial, dois homofones disjuntos por letra com IDs permutados e
escolha uniforme (seed de cifra 469, seed de busca 123), revelou:

| Busca de desenvolvimento | Peso frequência | Tempo aproximado | Acerto posterior |
|---|---:|---:|---:|
| 4 × 20.000, temperatura 12 | 0,1 | 0,34 s | 75,78% |
| 4 × 100.000, temperatura 12 | 0,1 | 1,67 s | 86,13% |
| 8 × 100.000, temperatura 12 | 0,5 | 3,23 s | 92,87% |
| 8 × 100.000, temperatura 12 | 1,0 | 3,51 s | 95,21% |
| 8 × 100.000, temperatura 12 | 2,0 | 3,53 s | 97,27% |

Outras configurações de temperatura 25/40, peso 0/0,05/0,3 e 4–12 reinícios
foram exploradas nesse mesmo desenvolvimento. Foram ajustes de
hiperparâmetros, não testes independentes nem comparação causal com o antigo
resultado de 42,6%, que usou outro fixture e orçamento.

**Limitação do pontuador demonstrada:** o plaintext verdadeiro desse treino
tem escore Alice médio -4,65844. Uma solução incorreta atingiu aproximadamente
-4,59146, acima da verdade. Portanto otimização do escore de tetragramas não
equivale a recuperação correta; aumentar somente o orçamento pode aprofundar
esse erro. A regularização foi escolhida no desenvolvimento para reduzir
esse efeito, sem substituir os testes independentes de recuperação.

Antes de congelar, repetimos seis cenários usando `encode` e `segments` do
harness: mesmo texto de desenvolvimento, seed de cifra 469, seed de busca
123, blocos de 128 códigos e a configuração final:

| Códigos | Distribuição | Acerto posterior | Tempo observado |
|---|---|---:|---:|
| 52 | balanced | 98,14% | 3,73 s |
| 52 | skewed | 99,22% | 3,78 s |
| 75 | balanced | 98,63% | 3,30 s |
| 75 | skewed | **5,66%** | 3,10 s |
| 99 | balanced | 96,29% | 2,77 s |
| 99 | skewed | 98,83% | 2,43 s |

A falha explícita em 75/skewed impede alegar recuperação garantida, mesmo
no desenvolvimento. Não ajustamos uma exceção ao cenário para apagá-la.
A próxima etapa é a qualificação separada com parâmetros congelados;
se ela falhar, a aplicação confirmatória aos livros permanece bloqueada.

## Verificação do algoritmo

Quatro testes em `tests/test_fast_homophonic.py` passaram:

1. Deltas incrementais versus recomputação Python independente em entradas
   aleatórias, códigos repetidos e várias fronteiras de sequência.
2. Contagem correta dos tetragramas e auditoria do escore integral da chave
   final, sem pontuar transições entre livros.
3. Determinismo de chave/escore sob a mesma semente e preservação de slots
   de códigos não vistos.
4. Rejeição de entradas sem tetragramas, códigos negativos, fracionários
   ou fora do domínio suportado.

Não foi lido nem otimizado o corpus Tibia neste desenvolvimento. Nenhum
resultado desta implementação constitui tradução de 469.
