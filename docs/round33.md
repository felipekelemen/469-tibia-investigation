# Rodada 33 — contagem exata das chaves lexicais de Knightmare

26/11/2026 (UTC). Base: `d464846bb4b387c6d0122fa6fe20427dc35d88d5`.

**A pendência computacional de Knightmare na família de 1–3 letras foi
resolvida: existem exatamente 153.174.074 chaves para os nove dígitos
observados, no modelo e dicionário fixados.** Uma implementação independente
confirmou o mesmo total. Isso não equivale a 153 milhões de traduções, nem
conta necessariamente 153 milhões de frases distintas.

Nenhuma tradução candidata foi produzida. A missão permanece inconclusiva:
não há decoder validado nem processo original sem texto autenticado.

## Hipótese preservada

A mensagem é `3478 67 90871 97664 3466 0 345`. Cada dígito emite uma unidade
fixa de uma a três letras; dígitos diferentes podem ter a mesma emissão.
Cada grupo numérico deve produzir exatamente uma forma do dicionário.
Os espaços são, portanto, provisoriamente fronteiras de palavras.

Usamos as mesmas **122.368 formas ortográficas** da R23, com normalização,
CMU versionado e a adição hipotética BONELORD preservados. Há nomes próprios,
abreviações e formas pouco usuais. Não acrescentamos palavras depois de ver
os resultados, não alteramos dígitos e não impusemos significados da lore.

A R23 havia encontrado 1.769 chaves antes de atingir seu orçamento. Rechecamos
as 1.769 como testemunhas distintas e válidas. Seus registros permanecem
inalterados: a nova rodada fecha aquele caso específico por outro algoritmo,
sem reclassificar como completas todas as buscas antigas.

## Como a contagem foi concluída

O novo motor constrói uma relação de atribuições possíveis para cada grupo.
Uma linha informa as unidades emitidas pelos dígitos presentes naquele grupo.
As relações são combinadas somente quando concordam nos dígitos compartilhados.

Quando um dígito deixa de participar de restrições futuras, suas alternativas
são somadas em um peso. Isso permite contar todas as combinações sem listar
cada chave inteira. A ordem de eliminação usa o grafo de dependências e o
tamanho das relações, sem pontuar inglês ou consultar o significado esperado.
Para Knightmare, os dígitos 1 e 5 aparecem em um único grupo cada e podem ser
somados durante a construção local.

As operações são junção, multiplicação de multiplicidades e soma sobre uma
variável. Por indução, cada peso representa o número de extensões das
variáveis já eliminadas; como essas variáveis são eliminadas uma única vez,
o escalar final conta atribuições completas aos dígitos observados. O programa
usa inteiros de 128 bits com detecção explícita de estouro.

O protocolo limitou cada tabela a seis milhões de linhas, o conjunto estável
de fatores a doze milhões, as visitas a pares de junção a cem milhões, cada
processo a 3 GiB de espaço de endereçamento e cada ajuste a 150 segundos.
Qualquer limite resulta em contagem desconhecida, nunca zero.

## Verificação independente

Antes dos ajustes principais, **100 casos pequenos** foram comparados com
enumeração direta de todas as chaves possíveis de unidades A/B. Todos os
totais coincidiram. Isso verifica a aritmética em problemas controlados; não
qualifica recuperação semântica de inglês.

Depois de observar o total de Knightmare, congelamos um protocolo adicional
para um segundo programa. Ele usa partições recursivas por palavra e uma
combinação específica das sete restrições, sem importar o código, as tabelas
ou o resultado do motor principal. O total foi novamente **153.174.074**.
Dois testes adicionais conferem esse programa por enumeração direta de
comprimentos e por um caso impossível.

O segundo cálculo é uma auditoria aritmética posterior ao resultado, não
validação semântica independente. Seus 53.465 casos centrais compatíveis
representam extensões ponderadas, não 53.465 chaves ou traduções.

## Resultados dos 51 ajustes

| Conjunto | Completos | Incompletos | Resultado dos completos |
| --- | ---: | ---: | --- |
| Knightmare | 1 | 0 | 153.174.074 chaves |
| 3478 forçado a BEHOLDER/BONELORD | 2 | 0 | Zero em ambos, reproduzindo os negativos da R23 |
| Controles com chave geradora conhecida da R23 | 7 | 3 | Todos positivos; de 71.424 a 42.791.921.919.291.633 chaves |
| Embaralhamentos internos dos grupos de Knightmare | 19 | 0 | 18 positivos; máximo de 9.676.507 chaves |
| Números uniformes com os mesmos comprimentos de grupos | 15 | 4 | 12 positivos e três zeros; máximo de 241.916.343 chaves |

**44 ajustes completos e sete limitados.** Os sete atingiram o limite de linhas
por tabela. Seus totais não foram estimados. Os controles conhecidos foram
verificados contra suas chaves geradoras, mas essas chaves nunca foram
fornecidas ao motor. Os sete resultados completos continuam ambíguos; o motor
de contagem não seleciona o plaintext verdadeiro entre eles.

Os 19 embaralhamentos são os mesmos, já expostos, da R23. Agora todos têm
contagem completa nesta família. Os controles uniformes têm a mesma sequência
de comprimentos, mas podem observar uma quantidade diferente de dígitos.
Não calculamos significância ou um ranking completo. Os números são
comparações descritivas entre espaços de chaves, não medidas de qualidade
linguística. Uma contagem maior pode refletir restrições mais permissivas.

O programa principal registrou cerca de 14 segundos para Knightmare, e o
segundo cerca de dois segundos. Os métodos e a carga concorrente diferem;
esses tempos são registros operacionais, não um benchmark controlado.

## O que isso permite concluir

**H123:** a busca limitada de Knightmare pode ser fechada por contagem exata.
Confirmado no espaço lexical declarado, com duas implementações concordantes.

**H124:** a existência de uma chave que produza palavras basta para reconhecer
uma tradução. Não sustentado: os controles embaralhados e uniformes também
admitem muitas chaves. Gramática, significado e transferência independente
continuam necessários. Não avaliamos semanticamente os 153 milhões de
resultados possíveis, nem concluímos que nenhum possa conter uma frase legível.

O dígito **2 continua ausente** de Knightmare e presente nas duas partes de
Chayenne. Sua emissão pode variar sem alterar qualquer restrição desta fala.
Por isso o total se refere a nove dígitos: uma contagem completa não resolve
essa falta de informação para transferir a chave a Chayenne.

Os testes com BEHOLDER e BONELORD preservam a rejeição apenas desta hipótese
de unidades fixas, dicionário e fronteiras. Não refutam 3478 como nome contextual
ou código de palavra. Não houve novo ajuste de Avar Tar ou novas medições de
Hellgate nesta rodada.

O próximo avanço metodológico útil seria qualificar um critério de seleção
gramatical em mensagens sintéticas com plaintext conhecido e reservado,
incluindo casos ambíguos e controles fora da família. Uma seleção só poderá
ser aplicada às falas do jogo dentro do alcance demonstrado. Outra alternativa
é obter uma restrição semântica atestada. A contagem completa fornece uma
base para esses testes; não determina qual chave foi usada pelo autor.

## Artefatos e reprodução

[Protocolo principal](../data/round33_protocol.json),
[fixtures](../data/round33_fixtures.json),
[qualificação aritmética](../results/round33_count_qualification.json),
[todos os ajustes](../results/round33_counts.json),
[auditoria independente](../results/round33_independent_count.json) e
[síntese computável](../results/round33_summary.json).

```bash
make round33
make round33-full
make test
```

O replay padrão confere os artefatos, as testemunhas antigas, os 100 casos
pequenos e repete a contagem principal de Knightmare. `round33-full` repete
também todos os 51 ajustes, com os mesmos limites. Tempos não entram na
comparação. O código requer Python 3.11+ e g++ C++17, sem novas dependências.

Os resultados e limites de execução constam em
[round33_verification.json](../results/round33_verification.json).

Passaram **326 testes**, incluindo nove testes novos. O replay padrão passou
em um diretório temporário com apenas 23 arquivos públicos, sem clones,
capturas privadas ou binários antigos. A repetição integral dos 51 ajustes
não foi realizada nesta consolidação: os 51 foram executados uma vez, e a
contagem principal foi repetida. As auditorias das R30–32 passaram. O aviso
não fatal já conhecido do leitor CSV congelado da R30 permanece no log.

Para repetir separadamente a contração independente, exporte o mesmo léxico:

```bash
python -c "import sys; sys.path.insert(0, 'scripts'); from unit_morphism_lexicon import banks; print('\n'.join(sorted(banks()[0]['grapheme1_3'].reverse)))" > /tmp/469-r33-lexicon.txt
g++ -O2 -std=c++17 scripts/round33_independent.cpp -o /tmp/469-r33-independent
/tmp/469-r33-independent /tmp/469-r33-lexicon.txt
```
