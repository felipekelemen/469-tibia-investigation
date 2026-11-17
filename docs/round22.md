# Rodada 22 — conclusão exaustiva dos 12 casos de Chayenne

**Os 12 casos que ficaram limitados na rodada 21 foram concluídos, sem chave
compatível e sem tradução verificável.** Não mudamos o vocabulário, os codecs,
a família de chaves ou as fronteiras presumidas. Com os 84 casos já completos,
as 96 configurações dessa família estão agora resolvidas para Chayenne, dentro
dessas premissas. Isso não exclui outras formas de codificar 469.

## Como a busca foi concluída

Os casos pendentes eram A=0/A=1 em decimal compacto, chave contínua de período
6/7/8 e feedback zero/um. A chave e o estado atravessam a separação entre as duas
partes da resposta. Os espaços internos são desconhecidos; o limite indicado
pelos emoticons é tratado como fronteira de palavra, como na rodada anterior.

A busca anterior explorava divisões em palavras a partir dos 36 dígitos iniciais.
A nova começa pelo fragmento de **13 dígitos**, cuja posição no fluxo e dígito
cifrado anterior são conhecidos. O feedback é removido na ordem original da
mensagem antes de alterar a ordem de verificação. A chave não reinicia no trecho
mais curto.

Construímos um autômato que reconhece concatenações dos códigos decimais das
7.713 palavras do vocabulário congelado. Ele mantém simultaneamente as divisões
possíveis, reunindo caminhos equivalentes. Para um período `p`, cada chave tem
exatamente um prefixo numérico decifrado de comprimento `p` no trecho escolhido:
essas posições visitam todos os elementos da chave uma vez.

Enumeramos esses prefixos e descartamos apenas os que não podem começar uma
concatenação de palavras do dicionário. Ao completar uma chave, verificamos o
restante do trecho curto e o trecho maior. A implementação não tem limite de
estados, duração ou número de soluções. A identidade

```
chaves verificadas + chaves descartadas por prefixo impossível = 10^p
```

é conferida em cada execução. Não são testes estatísticos nem estimativas de
cobertura. Um erro de execução ou registro ausente impede marcar o caso como
concluído. O código C++17 e o verificador Python são publicados; o executável é
compilado localmente e não integra o repositório.

## Resultados nos dois fragmentos

| Codec | Período | Feedback | Chaves que explicam o trecho de 13 dígitos | Chaves que explicam ambas as partes |
| --- | ---: | ---: | ---: | ---: |
| A=0 | 6 | 0 | 475 | 0 |
| A=0 | 6 | 1 | 270 | 0 |
| A=0 | 7 | 0 | 3.157 | 0 |
| A=0 | 7 | 1 | 3.730 | 0 |
| A=0 | 8 | 0 | 34.935 | 0 |
| A=0 | 8 | 1 | 59.769 | 0 |
| A=1 | 6 | 0 | 306 | 0 |
| A=1 | 6 | 1 | 292 | 0 |
| A=1 | 7 | 0 | 1.563 | 0 |
| A=1 | 7 | 1 | 1.966 | 0 |
| A=1 | 8 | 0 | 19.365 | 0 |
| A=1 | 8 | 1 | 47.694 | 0 |

“Explicar” nessa tabela significa admitir segmentação exata no dicionário,
sem afirmar gramática ou significado. Um trecho curto pode admitir dezenas de
milhares de chaves; nenhuma dessas chaves explica a resposta inteira nesta
família. A parte maior funciona como restrição adicional. Os dois fragmentos
já eram conhecidos e copiados nos livros; não constituem validação semântica cega.

Para a resposta real, a cobertura soma **444.000.000 combinações chave/modelo**:
9.854.522 chaves completas foram verificadas e 434.145.478 foram eliminadas por
prefixos impossíveis. Não afirmamos ter decifrado explicitamente 444 milhões
de mensagens. Chaves equivalentes em períodos diferentes também não são
observações independentes.

Sem chave sobrevivente, não houve previsão nova para Avar Tar, Knightmare ou
a enquete. Seus resultados anteriores permanecem os da rodada 21; não contamos
uma transferência vazia como novo teste independente.

## Controles e ambiguidade

Executamos **828 ajustes completos**:

- 360 fixtures sintéticas: 30 por configuração, usando seis palavras consecutivas
  de Baum/Barrie com espaços internos ocultos. O modelo gerador é fornecido,
  mas a chave não; isso testa a conclusão exaustiva, não seleção geral de modelos.
- 12 ajustes da resposta de Chayenne.
- 456 ajustes dos mesmos 38 controles da rodada 21, sob os 12 modelos: 19
  embaralhamentos internos e 19 pares copiados dos livros de descoberta.

Todos os 360 positivos mantiveram a chave verdadeira. **270 tiveram chave única,
mas somente 35 tiveram também um único caminho de palavras nas duas partes.**
O máximo foi 127 chaves em uma fixture. A retenção da chave verdadeira não deve
ser apresentada como tradução única de todas as fixtures.

Todos os **1.253 candidatos** produzidos na qualificação foram conferidos por
programação dinâmica em Python, independente do autômato C++. Quando ambas as
partes tiveram leitura lexical única, essa leitura foi recodificada e comparada
byte a byte com os números. Os 456 ajustes negativos terminaram sem chaves;
não restam os 456 casos limitados correspondentes da rodada anterior.

A preparação dos positivos condiciona as seis palavras ao léxico e garante
comprimento suficiente para cobrir a chave. São dois autores já usados no
projeto, com possíveis sobreposições de janelas. Não são 360 fontes novas,
frases de Tibia ou testes de vocabulário irrestrito.

Uma auditoria posterior explicita uma causa de ambiguidade dos codecs:

| Codec sintético | Duas palavras do vocabulário | Mesmo código decimal |
| --- | --- | --- |
| A=0 compacto | BY / ME | 124 |
| A=1 compacto | AHEAD / READ | 18514 |

Esses são certificados aritméticos do algoritmo testado, sem atribuição de
significado a números de 469. Entradas decimais idênticas continuam idênticas
após a mesma chave e feedback. Portanto conhecer a chave pode deixar leituras
lexicais distintas; gramática e evidência externa continuam necessárias.

## Verificação e reprodução

```
make test
make round22
```

O replay exige **Python, NumPy e um compilador C++17 disponível como `g++`**.
O ambiente usado tem g++ 14.2.0; versão e opções ficam em
`results/round22_compiler.json`. Compilação e execução são offline.

Os **218 testes automatizados** passaram. Os testes novos comparam todos os
resultados do algoritmo nativo com enumeração independente em períodos pequenos
e com a busca Python congelada em dicionários menores. Incluem feedback entre
fragmentos, fase correta ao começar pelo segundo trecho, zeros iniciais, múltiplas
segmentações e a diferença entre prefixo válido e palavra completa.

O protocolo, os dados das fixtures e o código foram registrados localmente por
hashes antes da nova busca. Não houve registro público prospectivo. A fonte dos
controles permanece o resultado congelado da rodada 21, sem nova amostragem
selecionada pelos resultados. A identidade de cobertura é verificada em todos
os 828 casos, com os candidatos revisados separadamente.

## Alcance e próximo caminho

O resultado rejeita o encaixe exato desses modelos no léxico e nas fronteiras
assumidos. Não rejeita nomes ausentes do dicionário, unidades maiores, outros
estados, outras línguas ou outros algoritmos. Não autenticamos novo texto
paralelo inglês nesta rodada.

A pendência de completar os 12 casos está encerrada. O próximo caminho
prioritário é testar unidades maiores — fonemas, sílabas ou morfemas — com um
vocabulário externo fixado antes dos alvos e qualificação de vocabulário oculto.
As relações numéricas com 639, 67538 e 3478 podem restringir modelos, mas não
recebem significados por tema. Os aprendizes que falharam na rodada 17 não são
promovidos por este resultado. P01/P03/P05/P06 continuam abertos.
