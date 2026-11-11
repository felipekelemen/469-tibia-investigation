# V3/V4 — pontuador mais amplo e reaquecimento da busca

Este estudo preserva V1/V2 e suas fontes congeladas. Não ajusta uma tradução
nos livros a partir de palavras da lore. Usa positivos sintéticos conhecidos
para qualificar o método antes de uma aplicação exploratória em 469.

## Desenvolvimento de V3

O pontuador anterior usava apenas o trecho de treino de Alice. V3 agrega
586.447 tetragramas de seis fontes já abertas: Alice, Frankenstein, Austen,
Conan Doyle, Wells e Dickens. Há 41.988 tetragramas distintos observados.
Alice continua limitada aos primeiros80%; os demais textos usam os primeiros
100.000 caracteres A–Z. Esse material já é treinamento/desenvolvimento, não
qualificação independente. Stoker, Melville, Twain e Charlotte Brontë não
entram no novo pontuador.

Mantivemos C++, dois bancos,8reinícios×100.000iterações por banco e temperatura12.
Comparamos pesos de regularização2/0,5 e dois/quatro bancos, em grade fixa,
nos12casos de prosa copiada já abertos. O peso2com dois bancos foi escolhido:
12/12atingiram95%, média99,26%, mínimo97,75%. O resultado anterior nesses
casos era8/12. Essa é melhoria em desenvolvimento, não validação nova.

A alteração muda os escores de tetragramas e as marginais usadas pela
regularização/inicialização. A comparação não isola cada componente desse
pontuador; mantém o orçamento nominal de busca.

## Qualificação V3

O protocolo foi congelado antes das saídas. Usamos30fixtures por modo,
15deDracula e15deMobyDick: autores não empregados no pontuador nem nos ajustes
anteriores. Cada fixture tem5.668letras de treino e1.024de teste,99códigos e
alocação desigual de homofones. Três modos:

1. Oito motivos de256letras cifrados uma vez e copiados como sequências numéricas.
2. Texto montado a partir dos mesmos motivos, com novos homofones por ocorrência.
3. Prosa comum, sem montagem por motivos.

As janelas de origem de fixtures distintos não se sobrepõem; o modo de prosa
comum fica em outras janelas. Os dois modos copiados compartilham os motivos
subjacentes, mas usam chaves e ordens diferentes: não são60conteúdos
independentes, nem um experimento causal que isole somente a renovação dos
homofones. Também há apenas dois autores e dependências de estilo.

|Modo|V3 aprovados em30|Média|BaselineV2 nos mesmos dados|
|---|---:|---:|---:|
|Sequências numéricas copiadas|24|86,16%|13|
|Texto copiado, homofones novos|30|99,35%|não executado|
|Prosa comum|30|99,42%|não executado|

Cada aprovação exige95%das letras. O gate exige27/30em todos os modos;
portanto **V3 falhou globalmente** e não foi aplicado aos livros. A comparação
pareada no primeiro modo tem28melhorias,2regressões; não apagamos nenhuma.
O ganho13→24é real nesse conjunto e orçamento, mas ainda insuficiente.

## Diagnóstico sem ajustar novamente as chaves

Comparamos as chaves retornadas das seis falhas com as chaves verdadeiras,
recomputando o mesmo objetivo de treino. Nenhuma busca adicional foi feita.
Em todos os seis casos a verdade tinha objetivo superior, com diferenças
entre1.336,57e6.281,19. Cinco tinham zero códigos não vistos no teste, e um
tinha apenas duas posições não vistas. A ausência de cobertura não explica
os grandes erros desses casos.

Isso fornece testemunhas concretas de insuficiência da busca finita; não
prova que a chave verdadeira seja o ótimo global nem que o objetivo nunca
prefira uma solução errada em outros dados. A análise é posterior à abertura
da qualificação, e esses casos agora são desenvolvimento.

## Desenvolvimento V4: mais exploração, mesmo número de passos

Testamos temperaturas máximas40,80,120 em grade fixada antes das saídas desse
novo desenvolvimento, nas seis falhas abertas e três guardas. As aprovações
foram6/9,7/9,9/9. Temperatura120obteve média98,08%, mínimo95,12%, e foi
congelada. C++, pontuador amplo, regularização2, bancos e número de iterações
permaneceram iguais. O custo nominal é igual; a trajetória e quantidade de
movimentos aceitos mudam, então não prometemos tempo de CPU idêntico.

Nenhum resultado V3 foi reescrito. V4 foi qualificado com novas fontes:
TomSawyer eJaneEyre, autores não usados no pontuador ou no ajuste. Os mesmos
três modos e gate foram mantidos, com novas janelas e chaves.

|Modo|V4 aprovados em30|Média|Mínimo|
|---|---:|---:|---:|
|Sequências numéricas copiadas|30|98,63%|96,29%|
|Texto copiado, homofones novos|30|99,35%|97,17%|
|Prosa comum|30|99,52%|98,44%|

V4 passou no gate operacional. No baseline pareado com o mesmo pontuador e
temperatura12,29/30passaram no primeiro modo, média95,48%. V4teve duas
melhorias e28empates. Essa diferença pareada não é a comparação24→30:
essa outra comparação mudaram autores e chaves. Não atribuímos toda diferença
entre estudos à temperatura, nem reinterpretamos a falha24/30como aprovação.

Os testes de qualificação ficam encerrados: não mudamos parâmetros olhando
os resultados novos. Os gates são operacionais, em estudos sequenciais;
não implicam taxa populacional garantida,30autores independentes ou prova
de que469use o mesmo mecanismo.

## Aplicação condicionada aos livros

O protocolo de busca V3 foi preparado, mas seu gate falhou: zero ajustes novos
nos livros nessa versão. O protocolo V4 foi congelado antes de suas saídas e
só liberou o ajuste após o gate90/90. Usa a representação de códigos importada,
o conjunto reservado antigo de61códigos e99réplicas por nulo, sempre com a
mesma otimização completa. Esse teste é exploratório e condicionado à
tokenização; os dados não se tornaram prospectivos por mudar o pontuador.

O [relatório da quinta rodada](round5.md) apresenta os resultados completos
dos controles e a interpretação. Qualificação positiva não será usada como
tradução automática ou rejeição de qualquer algoritmo possível de469.

## Reprodução

```sh
make round5
make test
```

O target verifica resultados finais presentes sem repeti-los. Para réplica
integral, usar checkout separado e retirar apenas os JSONs finais de saída,
preservando protocolos e arquivos-fonte. Os comandos `--freeze` recusam
sobrescrever protocolos já existentes. Texto e licenças originais permanecem
em `data/benchmark_reference_v3/` e `_v4/`, com hashes e bytes preservados.
