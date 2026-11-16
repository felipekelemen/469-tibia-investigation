# Rodada 20 — busca direta de inglês em Avar Tar, Knightmare e Chayenne

**Nenhuma tradução verificável encontrada.** Esta rodada procurou chaves de
um mecanismo integral de dígitos para inglês nos três textos prioritários.
Não dependeu da camada importada dos livros. As buscas reais terminaram sem
atingir os limites de cálculo e sem encontrar chave na família e no vocabulário
especificados abaixo.

## Família de tradução testada

Testamos sete codificações de letras: ordinais A=0 e A=1, cada qual em decimal
compacto ou com dois dígitos; ASCII maiúsculo; ASCII minúsculo compacto ou com
três dígitos. Após converter as letras, uma permutação fixa dos dez dígitos
pode trocar qualquer dígito por outro. O mesmo mapa deve explicar todos os
fragmentos usados no ajuste. São até 10! permutações por convenção, resolvidas
por restrições sem precisar percorrer cada chave.

O vocabulário contém **7.713 palavras** extraídas de *The Secret Garden* e
*My Man Jeeves*, com normalização determinística de caixa e apóstrofos. A e I
são as únicas palavras de uma letra. Não acrescentamos nomes de Tibia ou termos
escolhidos para completar uma frase. As cifras compactas podem ter mais de uma
segmentação em letras: todas permanecem possíveis. Não há alteração de letras,
correção de erros ou seleção de uma frase por parecer adequada à lore.

O resultado negativo é condicionado a esse vocabulário, aos sete codecs, à
permutação bijetiva fixa e às fronteiras assumidas. Não exclui outras cifras,
nomes ausentes, sílabas, códigos de palavras, homofonia, estado ou texto em outra
língua. Uma palavra fora do dicionário pode bastar para impedir um ajuste.

## Avar Tar e Knightmare: busca com espaços

Para Avar Tar, usamos os primeiros dez grupos para descobrir a chave e
reservamos os outros dez para transferência. Para Knightmare, usamos seus sete
grupos e planejamos aplicar a mesma chave ao poema e a Chayenne. O poema inteiro
foi examinado separadamente como diagnóstico; esse ajuste não validaria o teste
com prefixo. Os textos e suas transcrições já eram conhecidos em rodadas anteriores.

| Ajuste | Famílias examinadas | Chaves compatíveis | Busca completa |
| --- | ---: | ---: | --- |
| Primeiros dez grupos de Avar Tar | 7 | 0 | Sim |
| Sete grupos de Knightmare | 7 | 0 | Sim |
| Vinte grupos de Avar Tar, diagnóstico | 7 | 0 | Sim |

Nenhuma chave chegou à etapa de transferência. Os campos vazios nessa etapa
significam ausência de chave ajustada, não falha de uma predição independente.
Também não contamos a segunda metade de Avar Tar como confirmação independente
da rejeição baseada na primeira metade.

Em Avar Tar, certos grupos não têm sequer uma palavra compatível no dicionário
sob as convenções compactas, antes de impor uma chave comum. Em Knightmare,
cada grupo isolado tem candidatos nas duas convenções ordinais compactas;
entretanto, nenhuma chave explica todos juntos. Esse contraste mostra por que
encaixes ingleses isolados não bastam para traduzir a fala.

Foram executados **420 exemplos sintéticos**, com sete ou vinte palavras de
ajuste e sete palavras seguintes reservadas. Os textos vieram de Baum e Barrie,
autores diferentes dos dois usados para o vocabulário, mas já empregados em
rodadas anteriores. Os trechos de ajuste foram condicionados a conter palavras
do dicionário; os seguintes não foram filtrados. Trechos podem se sobrepor e
não representam 420 fontes independentes.

Todos os ajustes terminaram e preservaram a chave verdadeira. As 14 células
passaram o critério previamente registrado: pelo menos 90% das palavras
reservadas presentes no dicionário recuperadas de forma única, sem singleton
errado. Esse sucesso é lexical e condicionado à família fornecida no benchmark.
Não qualifica detecção geral de inglês ou escolha entre famílias desconhecidas.

A diferença entre decodificar letras e impor palavras é material: nas variantes
ordinais compactas, apenas 9–34 das 210 palavras por célula tinham leitura
literal única sem o dicionário, mesmo com essa boa recuperação lexical. As
ambiguidades são preservadas no resultado, não ocultadas por uma pontuação.

Nos **396 controles negativos** — 99 por texto e por tipo — também não houve
chaves. Um tipo embaralha todos os dígitos e repõe os comprimentos originais;
o outro embaralha cada grupo distinto, preservando suas contagens e repetições.
A renomeação global dos dígitos preservou as contagens de chaves, como esperado
por construção. Esses controles não indicam que os textos reais sejam aleatórios.

## Chayenne: ataque direto sem espaços internos

Após o resultado anterior, registramos um segundo protocolo para Chayenne.
Mantivemos o vocabulário e as sete famílias, permitindo qualquer divisão em
palavras dentro de cada parte numérica. A separação marcada por emoticons foi
tratada como fronteira possível entre palavras; essa é uma hipótese explícita.
A chave é compartilhada entre as duas partes. O algoritmo procura divisões e
chave simultaneamente, sem fornecer a frase inglesa.

| Convenção | Estados visitados | Chaves compatíveis | Busca completa |
| --- | ---: | ---: | --- |
| A=0 compacto | 3.184 | 0 | Sim |
| A=0 com dois dígitos | 9 | 0 | Sim |
| A=1 compacto | 2.441 | 0 | Sim |
| A=1 com dois dígitos | 2 | 0 | Sim |
| ASCII maiúsculo | 9 | 0 | Sim |
| ASCII minúsculo compacto | 1 | 0 | Sim |
| ASCII minúsculo com três dígitos | 1 | 0 | Sim |

O limite era 10.000 estados e 1.000 mapas por família. Nenhuma busca real foi
truncada. Nas convenções de largura fixa, os comprimentos dos fragmentos já
restringem fortemente a possibilidade de codificação.

Os **70 exemplos sintéticos**, dez por família, ocultaram os espaços internos
de dois fragmentos de três palavras cada. Todos terminaram com a chave verdadeira
entre as soluções. Isso verifica retenção, sem afirmar chave ou frase única;
os seis termos eram condicionados ao dicionário. Não são poemas de significado
independente nem qualificam todos os comprimentos possíveis.

Também executamos **38 controles negativos**: 19 embaralhamentos dentro das
partes e 19 pares de fragmentos retirados dos 68 livros de descoberta, com os
mesmos comprimentos 36 e 13. Todos terminaram, sem chave. Os controles copiados
incluem a estrutura repetitiva do corpus. Nenhuma estatística de tradução foi
atribuída a esses resultados.

## Revisão das fontes e implicação

As transcrições consultadas na Tibia Wiki e em TibiaSecrets preservam os números
do poema. O comentário de Avar Tar descreve o trecho como poema; não fornece
sua tradução. A entrevista de Chayenne e a fala de Knightmare continuam sem
texto inglês paralelo autenticado nas fontes utilizadas.

A busca também localizou reconstruções temáticas do poema e um codebook
comunitário que atribui palavras à fala de Knightmare. Não os usamos como
plaintext verdadeiro: falta uma derivação independente que prediga novas
mensagens. A repetição de uma atribuição em repositórios não a autentica.
URLs e alcance da revisão constam em `data/source_review_round20.json`.

## Reprodução e próximos passos

```
make test
make round20
```

O projeto tem **198 testes automatizados**. Os scripts verificam os manifests,
reexecutam 490 fixtures sintéticas, os ajustes reais e os 434 conjuntos de
controle negativo. Os protocolos primário e secundário foram congelados em
momentos distintos, ambos antes de seus respectivos resultados. Nenhuma
captura nova ou corpo integral de página é necessário para o replay offline.

A prioridade passa a mecanismos capazes de representar unidades maiores ou
variar por contexto. Para os próximos testes:

1. Avar Tar: testar uma família explícita de códigos de sílabas/morfemas que
   explique simultaneamente grupos repetidos e as terminações com 639. Exigir
   qualificação sintética com vocabulário oculto antes de atribuir inglês;
   usar a ocorrência externa de 67538 na enquete como restrição de transferência,
   sem presumir significado.
2. Knightmare: testar códigos variáveis ou contextuais com uma única regra para
   os sete grupos, reservando outras falas para transferência. Qualquer leitura
   proposta deve explicar por que funciona fora da frase usada para ajustá-la.
3. Chayenne: manter os dois fragmentos como teste de transferência e identificar
   todos os trechos dos livros que precisam receber a mesma saída literal sob
   uma chave proposta. Suas cópias conhecidas não criam validação independente.

As quatro entregas maiores P01/P03/P05/P06 permanecem abertas. O avanço desta
rodada é uma busca integral executada e limitada com precisão, não uma nova
tradução nem prova de ausência de significado.
