# Quarta rodada — busca homofônica robusta e aplicação controlada

**Nenhuma tradução de 469 foi validada.** A nova versão passou na qualificação
com prosa comum de autores novos e foi aplicada aos livros com 297 controles
reotimizados. A vantagem contra embaralhamento simples desapareceu diante de
controles mais estruturados. Um teste adicional demonstrou falta de potência
em parte dos cenários de prosa cifrada copiada.

## O que mudou

V1 e seus resultados ficaram intactos. V2 usa dois bancos independentes de
8 reinícios × 100.000 iterações, selecionando somente pelo objetivo de treino.
Não mudou o C++, o pontuador Alice, a regularização ou a temperatura. O custo
é aproximadamente o dobro; não se trata de uma melhoria com orçamento igual.
As quatro falhas antigas passaram a ser desenvolvimento. Três foram corrigidas
nesse desenvolvimento, e uma continuou em 0%; esse dado não foi ocultado.

Os textos da nova qualificação são de H. G. Wells e Charles Dickens,
separados dos autores usados anteriormente. São 30 excertos disjuntos e
novas chaves em cada cenário. Os mesmos excertos são reutilizados entre seis
cenários: 180 ajustes não são 180 textos independentes. Também existem
relações de estilo e frases entre excertos do mesmo autor.

## Qualificação congelada

O critério anterior foi mantido: pelo menos 95% das letras reservadas em
pelo menos 27/30 testes de cada cenário. Os hashes do algoritmo, gerador,
pontuador e textos foram congelados antes de abrir as saídas.

|Códigos|Distribuição|V2 aprovações|V2 média de letras corretas|Primeiro banco, mesmos testes|
|---|---|---:|---:|---:|
|52|equilibrada|30/30|99.10%|29/30|
|52|desigual|30/30|99.20%|29/30|
|75|equilibrada|30/30|98.52%|27/30|
|75|desigual|30/30|98.85%|28/30|
|99|equilibrada|30/30|98.27%|28/30|
|99|desigual|30/30|98.59%|29/30|

Todos os seis cenários passaram, com 180/180 aprovações. O primeiro banco
isolado passaria em 170/180 testes e também nos seis gates desta amostra nova;
isso não altera a falha histórica de V1. A comparação pareada registrou
10 melhorias, nenhuma regressão e 170 empates. Ela mede o efeito do banco
adicional no mesmo material; a comparação com os autores antigos não é pareada.

O gate é uma qualificação operacional dos cenários medidos, não uma prova de
que a taxa populacional de sucesso seja 90% com confiança estatística
especificada. Este estudo foi planejado após V1; não há controle sequencial
de alpha entre versões. Passar não demonstra que o mecanismo real de 469
seja o mesmo. Detalhes: [V2](homophonic_v2.md).

## Aplicação aos livros: 1 ajuste e 297 controles

O segundo protocolo foi congelado antes dos resultados V2. Após a aprovação,
a busca recebeu os 68 livros de descoberta; a chave selecionada foi aplicada
aos dois livros reservados antigos, com 61 códigos no total. Esses dados já
foram examinados e são correlacionados, não validação prospectiva independente.
A tokenização de dois dígitos com zeros restaurados é importada e condiciona
toda esta análise.

Para cada nulo, foram feitas 99 réplicas e a mesma otimização completa de dois
bancos. Escores são médias de log10 de tetragramas, não qualidade semântica:

|Controle|O que preserva|p de cauda superior no reservado|
|---|---|---:|
|Shuffle por livro|Comprimento e contagens dos códigos|0,02|
|Euler por livro|Também bigramas e extremidades|0,92|
|Blocos de 8 códigos|Ordem dentro dos blocos e marginais|0,78|

Os p usam (1 + nulos >= observado)/(1 + 99). São exploratórios, dependem do
modelo nulo e não são probabilidades de tradução correta. As trilhas Euler
não são amostradas uniformemente; em 16/99 réplicas os dois livros reservados
ficaram inalterados. Blocos não preservam todos os motivos nem suas fronteiras.

O treino atingiu -4,877077 e o reservado -5,835898. A saída literal foi:

```text
RTEIECEHHEWDHLINAREAIEDIGEEATHEE
HHHEWDHLINAREAIEDIGEEATHEESBY
```

Não constitui inglês coerente, não recebeu anagramas, segmentações convenientes
ou reparos manuais. A vantagem contra shuffle simples não persistiu nos outros
dois controles. Nenhuma chave ou tradução foi promovida.

## Sensibilidade a inglês cifrado e copiado

Executamos um teste exploratório separado com 12 montagens de oito motivos
ingleses de 256 letras de Frankenstein, cifrados uma vez e então copiados como
sequências numéricas. O protocolo precedeu suas saídas; ele não substitui o
gate de 30 fixtures nem muda os parâmetros. O texto já era desenvolvimento,
e o teste compartilha motivos com treino por construção.

Só 8/12 testes atingiram 95%; o pior ficou em 46,19%. Portanto qualificação em
prosa comum não demonstra potência suficiente para toda prosa cifrada com
montagem repetitiva, relevante ao caso dos livros. Uma falha em 469 não pode
excluir a família homofônica de maneira irrestrita.

Reproduzimos exatamente o pior caso para diagnóstico, sem nova semente. A
chave verdadeira pontua 3.856,40 unidades acima da chave encontrada no mesmo
objetivo de treino. Nesse caso selecionado, a falha é de busca: o algoritmo
não alcançou uma solução conhecida de maior objetivo. Isso não diagnostica
todos os outros erros, não prova a adequação universal do pontuador e não
converte o teste de desenvolvimento em qualificação independente.

## Resultado e próxima decisão

O objetivo desta etapa foi cumprido no escopo de prosa comum: há um solver
mais estável e uma comparação controlada real nos livros. O resultado continua
sendo zero traduções. A próxima melhoria deve primeiro atacar as falhas de
busca em prosa copiada, com novos positivos reservados para sua qualificação,
sem reaproveitar os 12 casos abertos como confirmação. Podem ser estudados
reinícios adaptativos ou movimentos mais amplos, cobrando seu orçamento e
mantendo o teste fora da seleção. Novos dados externos e mecanismos de
segmentação/conceitos continuam importantes; não basta aumentar o escore
nos mesmos livros.

## Reprodução e artefatos

```sh
make round4
make test
python scripts/copied_prose_stress_v2.py
python scripts/diagnose_copied_fixture_v2.py
```

`make round4` verifica resultados concluídos sem repeti-los; se não existirem,
executa qualificação e busca condicional. Para uma réplica integral, usar um
checkout separado e retirar apenas os JSONs finais de saída correspondentes,
preservando os protocolos. Nunca sobrescrever um protocolo congelado com
`--freeze`. Tempos e detalhes numéricos podem variar entre máquinas.

Fontes, parâmetros, sementes, mapas, 180 resultados e todos os controles ficam
em `data/` e `results/`. O relatório integral anterior e checkpoints temporários
não são republicados. Esta rodada exige Python, NumPy e g++ C++17.
