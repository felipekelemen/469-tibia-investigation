# Decomposição modular do sinal V4 — auditoria executada

**O inventário aprendido em descoberta cobre 70,78% dos códigos de descoberta,
mas nenhum dos 61 códigos reservados.** Portanto, um controle que apenas
permuta esses módulos não preserva módulos no reservado: ali vira um
embaralhamento de literais. Esse controle não pode ser apresentado como
validação de montagem modular no conjunto de teste.

Não foi descoberta tradução, nem executada nova otimização de chave.
A análise usa a chave V4 já ajustada e o pontuador amplo congelado; é um
diagnóstico condicionado a uma chave selecionada anteriormente nos livros.

## Inventário e fronteiras

Cada código de dois dígitos é representado por um único caractere injetivo
`chr(256+int(code))`; isso não atribui letras ou significados. Motivos
candidatos têm 8,12,16,24 ou32 códigos, com pelo menos duas ocorrências nos
68livros de descoberta. Nunca se extraem janelas cruzando livros.

A heurística escolhe ganho de cobertura incremental sem sobreposições, pagando
motivos e comprimentos. Gera no máximo128entradas. Compara os prefixos64/128
pelo custo de dicionário+tokens de descoberta, com um bit pela escolha. O
parsing final de cada livro usa programação dinâmica com literais e referências
prefixadas, sem alterar o inventário no teste. É uma decomposição finita,
heurística; não afirmamos ter recuperado os módulos verdadeiros dos autores.

Foram selecionadas64entradas. Todo livro tem roundtrip exato. Para cada
janela de quatro caracteres decodificados, distinguimos:

- **Interna:** os quatro caracteres pertencem à mesma referência de módulo.
- **Fronteira de módulo:** toca alguma referência, mas não fica integralmente numa só.
- **Residual:** todos os caracteres pertencem a literais.

As janelas nunca cruzam fronteiras de livros. A soma das três categorias
reproduz exatamente, salvo arredondamento numérico, os escores V4 originais.

|Grupo|Códigos|Códigos em referências|Janelas internas|Fronteira|Residual|
|---|---:|---:|---:|---:|---:|
|Descoberta|5.668|4.012 (70,78%)|3.265|1.108|1.091|
|Reservado|61|0|0|0|55|

Na descoberta, as janelas internas representam59,75% de todas as janelas.
Seus escores médios foram−4,548867, contra−4,681965nas fronteiras e
−5,238240nos resíduos. Essas frações e médias não são proporções de
significado ou explicação causal: a chave foi escolhida na própria descoberta.

O reservado tem escore médio−4,552778, mas nenhuma referência exata de8ou
mais códigos do inventário. Logo seu sinal não se explica por referências
literais a **esses** motivos aprendidos em descoberta. Fragmentos menores,
relações transformadas, homofones, estatísticas de ordem superior e a
reutilização entre os próprios dois livros reservados continuam possíveis.
Não houve restauração de independência ou demonstração de semântica.

## Permutação da ordem: o que foi realmente medido

Em99réplicas, permutamos os tokens completos dentro de cada livro, mantendo
cada referência indivisível e cada literal. Isso preserva comprimento,
contagens dos códigos, inventário e multiplicidade dos tokens. Todas as
janelas internas dos módulos e sua soma de escores ficam invariantes por
construção. As diferenças de pontuação vêm somente de fronteiras e resíduos.
Não se reparseia o texto permutado para inventar novos módulos.

A chave e o pontuador permanecem fixos. Os p condicionais descritivos foram
0,01na descoberta e0,01no reservado. **Não são os p dos experimentos anteriores
com chave reotimizada em cada nulo.** A seleção anterior da chave na ordem
original não é recalibrada, e a análise de descoberta é pós-seleção. No
reservado sem referências, a permutação é apenas shuffle de códigos individuais.

Por isso, o status operacional é `BLOCKED_NO_HELD_MODULE_COVERAGE` e o número
de novos nulos com chave reotimizada foi **zero**. Um p baixo desse diagnóstico
não responde à hipótese de ordem entre módulos no reservado.

## Controle positivo e limite semântico

Uma demonstração com oito trechos ingleses conhecidos de TomSawyer, cada um
com128letras, usados em24tokens ao todo (três de cada), confirmou que permutar a ordem
preserva integralmente todos os tetragramas internos. O exemplo usa texto
já aberto e não pretende ser qualificação independente.

Esse fato matemático também é um limite interpretativo: módulos podem conter
prosa verdadeira. Mudar sua montagem pode manter significado dentro deles,
ainda que destrua relações entre frases. Portanto esse controle não pode ser
chamado automaticamente de gerador sem mensagem.

## Reprodução e verificações

```sh
python scripts/module_signal_audit.py
python -m unittest discover -s tests -p test_module_signal_audit.py -v
```

Quatro testes passaram: parsing lossless com referências/literais; ausência
de aprendizagem e pontuação entre livros; inventário imutável diante de teste
inédito; invariância exata do escore interno e mudança possível nas fronteiras.
Protocolos, lista de motivos, categorias, todas as99réplicas, hashes e limites
estão em `results/module_signal_audit.json`.
