# P02 executado — qualificação do solucionador homofônico

**O solucionador melhorou substancialmente, mas a qualificação global falhou.**
Passou em cinco cenários; no sexto,99códigos com distribuição desigual,
26/30fixtures passaram, contra o mínimo previamente fixado de27. Não se
arredondou o resultado nem se alterou o critério depois de consultar a saída.
P04 permanece bloqueado para esta versão.

## Implementação e separação dos dados

O novo componente C++ avalia somente os tetragramas afetados por cada mudança
de código. Usa reassociação, trocas de códigos, trocas de grupos de letras,
reinícios e reaquecimento, com regularização de frequências. Seu objetivo,
desenvolvimento e auditoria numérica estão em [fast_homophonic.md](fast_homophonic.md).

Alice, primeiros80%, é a referência de ajuste do pontuador. Frankenstein
foi usado para desenvolvimento, e também como segundo pontuador **apenas na
avaliação**, nunca para selecionar a chave. A qualificação usa30excertos
contíguos e sem sobreposição,15de Austen e15de Conan Doyle. Cada trecho tem
5.668letras de treino e1.024de teste, divididas em sequências de128. As mesmas
30fontes são reutilizadas nos seis cenários:180ajustes não equivalem a180
textos independentes, e excertos contíguos do mesmo autor podem compartilhar
estilo e frases. Não são30autores independentes.

As chaves verdadeiras são aleatórias e distintas do algoritmo; os IDs de
código não revelam a letra. Todos os26caracteres têm homofones disjuntos.
Os cenários52/75/99códigos usam alocação equilibrada ou desigual. O relatório
inclui cobertura de códigos vistos no treino e posições de teste não vistas.
Essas posições não são declaradas como recuperação comprovada de chave.

O protocolo `data/homophonic_benchmark_protocol.json` foi congelado antes da
qualificação, com hashes do C++, wrapper, harness, textos e referência Alice.
Foram usados8reinícios×100.000iterações, temperatura12 e peso de frequência2,
com100slots de códigos e dois workers. O run final levou272,59segundos nesta
máquina, sem contar desenvolvimento. Implementações e fontes foram verificadas
novamente após a execução. O módulo antigo `cipher_battery.py` que cria o
pontuador permaneceu idêntico ao commit científico anterior.

## Resultado da qualificação

Um fixture passa quando recupera pelo menos95%das1.024letras reservadas.
Cada cenário exige pelo menos27/30fixtures aprovados; a versão global exige
que todos os seis cenários passem.

| Códigos | Distribuição | Fixtures aprovados | Média de letras corretas | Gate |
|---|---|---:|---:|---|
|52|equilibrada|30/30|99,07%|passa|
|52|desigual|29/30|96,03%|passa|
|75|equilibrada|29/30|95,25%|passa|
|75|desigual|30/30|98,68%|passa|
|99|equilibrada|30/30|98,03%|passa|
|99|desigual|**26/30**|86,20%|**falha**|

Há falhas catastróficas de otimização em alguns fixtures, inclusive acerto
próximo de zero; a média por cenário não deve ocultá-las. Não foi feita
comparação pareada com o antigo42,6%: aquele teste usava outro plaintext,
comprimento de reservado e orçamento. Os novos resultados medem recuperação
real de positivos sintéticos, não tradução de469.

`scripts/qualification_gate.py` recalcula a decisão a partir dos acertos
inteiros de cada tentativa; não confia no resumo agregado. Verifica conclusão,
protocolo, hashes, cenários, fixtures duplicados/ausentes e consistência entre
contagens e precisão. Sua saída é `results/p04_gate.json`, status
`BLOCKED_INSUFFICIENT_QUALIFICATION`. Três testes verificam o limiar exato,
falha fechada e rejeição de precisão falsificada.

## Limites e próxima decisão

Não aplicamos este novo solucionador aos livros nem produzimos mais tentativas
sobre os mesmos testes para transformar26em27. O gate falhou: isso não exclui
homofonia ou significado nos livros, e os cenários sintéticos não são uma
réplica completa da distribuição real desconhecida.

Uma versão futura pode testar mais reinícios, melhor seleção de ótimos locais
ou pontuador externo mais abrangente, mas deve ter protocolo novo e dados de
qualificação distintos. Os30excertos abertos agora passam a ser desenvolvimento;
não poderão reaparecer como confirmação cega de uma versão ajustada a suas
falhas. O teste de desenvolvimento já mostrou que uma chave errada pode ter
escore de tetragramas melhor que a verdade, portanto melhorar somente escore
não é critério suficiente.

## Reprodução

Requer Python, NumPy e `g++` com suporte a C++17. O binário é compilado em
`/tmp`, com cache por hash e identificação do compilador; não é versionado.
Os textos e suas licenças estão em `data/benchmark_reference/`.
São snapshots byte a byte, com CRLF e espaços originais preservados;
`.gitattributes` impede normalização desses arquivos congelados.

```sh
python scripts/homophonic_benchmark.py --run
python scripts/qualification_gate.py
```

Não executar `--freeze` sobre o protocolo já congelado. Reexecuções estocásticas
usam as sementes registradas; tempos e detalhes numéricos podem variar entre
máquinas. Saídas completas: `results/homophonic_benchmark.json`.
