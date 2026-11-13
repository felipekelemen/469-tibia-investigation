# Rodada 18 — contexto, fronteiras e inferência sem escolha arbitrária

**Não há tradução nova.** Foram executados750 ajustes exatos em controles
combinatórios e uma contagem de parses das falas e dos 70 livros. O avanço é
distinguir observações que reduzem ambiguidade de mais cópias dos mesmos
blocos, mantendo todas as chaves compatíveis em vez de escolher uma por custo.

Os controles usam uma **família de candidatos fornecida**. Não qualificam
aprendizado geral de vocabulário oculto, não substituem o gate que falhou na
rodada 17 e não fornecem significados ingleses para469.

## Experimento de contexto

Cada caso tem32 blocos numéricos de 10 dígitos. Cada bloco pode ser dividido
em 4|6,5|5 ou6|4, formando duas unidades. Há64 unidades por chave. Os primeiros
três dígitos dos candidatos certificam que qualquer chave fixa é prefix-free.

O treino tem70 mensagens com 16 blocos:11.200 dígitos, próximo do tamanho do
corpus estudado. Cada bloco aparece35 vezes; portanto cada unidade verdadeira
também aparece35 vezes. Como os dois membros de cada par nunca se separam,
**todas as 3³²=1.853.020.188.851.841 chaves** explicam o mesmo treino. Não foi
necessário enumerá-las uma a uma.

A família, inclusive os blocos e as três posições candidatas, é informação
lateral explícita. Ela não foi descoberta nos livros e não é atribuída a
CipSoft. Os30 casos têm famílias/chaves numéricas geradas independentemente;
não contêm inglês nem constituem30 fontes linguísticas.

Três tipos de observação foram comparados:

- Mais mensagens dos mesmos pares completos, mudando ordem e frequência.
- Mensagens raw com duas unidades em combinações novas, sem fornecer o corte.
- Mensagens válidas curtas que isolam uma unidade de um grupo ainda não observado.

O terceiro caso seleciona grupos distintos; o segundo sorteia recombinações
que podem voltar aos mesmos grupos. Seus números de mensagens não são uma
comparação universal de custo ou de eficiência ótima.

## Solver e validação

Cada mensagem raw gera um conjunto exato de caminhos, que impõem atribuições
parciais às posições de corte. Um solver de domínios finitos conjuga essas
restrições, preserva correlações, conta chaves e calcula os valores ainda
possíveis. Pode concluir zero, uma ou várias chaves, sem forçar unicidade.

O decoder considera somente caminhos de um alvo que se estendam a uma chave
compatível. Emite uma análise apenas quando todos os caminhos viáveis
concordam; caso contrário, abstém-se. A validade e as fronteiras do próprio
alvo também condicionam essa inferência local. O alvo não entra no conjunto
de adaptação nem escolhe parâmetros.

Os testes comparam o solver a enumeração exaustiva independente em famílias
pequenas e a um decoder prefix-free de chave fixa. Para os casos completos,
as contagens de pares e de unidades isoladas têm identidades analíticas:
3³² e3^(32−a), respectivamente. A chave verdadeira é conferida num verificador
separado, sem entrar no estado/cache usado para inferência.

Foram congelados protocolo e implementação antes de gerar os resultados.
Todos os 750 ajustes ficaram exatos, sem atingir os limites de 4.096 caminhos
ou100.000 nós. O máximo observado foi349 nós, incluindo consultas de suporte
e decodificação. Se algum limite fosse atingido, o resultado seria marcado
como incompleto, sem alegar chave única. Não há ajuste de hiperparâmetros por
inglês ou lore.

## Resultados dos controles

Incerteza média restante, medida como log₂ do número de chaves. A interpretação
em bits condiciona-se ao prior uniforme desta família fornecida, não estima
a entropia real de 469.

| Observações adicionais | Mais pares completos | Recombinações novas | Unidades isoladas distintas |
|---:|---:|---:|---:|
| 0 | 50,72 | 50,72 | 50,72 |
| 8 | 50,72 | 30,66 | 38,04 |
| 16 | 50,72 | 18,33 | 25,36 |
| 32 | 50,72 | 6,71 | 0 |
| 64 | 50,72 | 0,85 | — |
| 128 | 50,72 | 0 | — |

Mais pares completos não identificam nenhum corte. Com64 recombinações,
17/30 casos têm chave única; com 128,30/30. Com32 unidades isoladas, todas as
32 variáveis ficam determinadas nos30 casos, como previsto pela contagem
analítica. Isso demonstra o valor de quebrar a dependência dentro dos pares,
condicionalmente a esta família.

Há dois conjuntos de 32 alvos por ajuste: os pares deliberadamente ambíguos
e recombinações novas, distintas das usadas na adaptação. Nos pares, a cobertura
do decoder sai de 0% e sobe conforme os cortes são identificados. Nas
recombinações, já começa em 98,4%: a família fornecida e as fronteiras do próprio
alvo excluem quase todos os outros caminhos locais. **Essa cobertura alta não
significa que a chave global foi aprendida**, nem é desempenho em 469.

Não houve predição única errada quando família e observações eram válidas.
Esse resultado é condicional: um controle com uma fronteira falsa força um
corte incorreto, mantendo3³¹ chaves aparentemente consistentes e excluindo a
verdadeira. Ao acrescentar a fronteira correta conflitante, o solver retorna
zero. Consistência interna não autentica uma pista externa.

## Falas reais: quanto os espaços realmente restringem?

Um segundo protocolo, congelado antes das novas contagens, examinou as
transcrições existentes. O modelo é **hipotético**: cada código de dois dígitos
emite seus dois dígitos ou, se começa por 0, pode omitir esse zero. Não foram
permitidos reparos de dígitos não zero. Os códigos numéricos não recebem letras.

Foram comparados o inventário observado de 99 códigos e a versão de 100,
incluindo39, para não tratar ausência no corpus como proibição da linguagem.
A comparação entre fala unida e grupos separados assume, condicionalmente,
que cada grupo numérico seja uma moldura completa de códigos. **Não assume
que seja uma palavra ou unidade atômica.**

| Amostra | Parses unindo os números | Parses com as molduras observadas |
|---|---:|---:|
| Knightmare, inventário99 | 75.025 | 9.600 |
| Poema de Avar Tar, inventário99 | ≈1,85×10²³ | ≈3,03×10²⁰ |
| Grito de 20 dígitos do bibliotecário | 10.946 | 10.946 |
| Nome 486486 | 13 | 13 |
| Referência1, ou número0 isolado | 1 | 1 |

Cada parse inclui códigos **e escolhas de emissão/omissão**, não apenas uma
sequência distinta de IDs. Por exemplo, `000` tem três parses mas duas
sequências de IDs: `00+0` e `0+00` usam os mesmos dois códigos00 com máscaras
diferentes. A [nota de contagem](../data/round18_framing_scope_notes.json)
explicita essa distinção sem alterar os números ou o algoritmo congelado.

Esses números **não contam traduções ou significados possíveis em inglês**.
O modelo opcional permite qualquer dígito isolado como0d, portanto
aceitar uma string não valida a cifra. Para o inventário100, a quantidade é
exatamente Fibonacci(n+1), dependendo apenas do comprimento. Qualquer troca
de rótulos ou embaralhamento dos dígitos preserva essa contagem: não é detector
de linguagem.

O número 3478 admite cinco streams nesse modelo, como `34|78` ou
`03|04|07|08`. São representações hipotéticas com zeros omitidos, sem tradução
associada. A unicidade numérica de 1 sob essa hipótese também não autoriza
substituir cada dígito1 pela palavra Tibia.

Todos os 70 livros continuam com muitas análises possíveis: as contagens do
inventário99 têm8–62 algarismos decimais por livro. Esses números não são os
79 alinhamentos estudados anteriormente: aqueles fixavam os streams
importados; aqui muitos streams diferentes estão permitidos. Nenhum deles
foi escolhido por produzir uma palavra atraente.

## Fontes e decisão

A [revisão limitada de fontes](../data/source_review_round18.json) encontrou
transcrições já conhecidas, páginas inacessíveis diretamente e a história
artística do [Bonelord Tome](https://www.tibiasecrets.com/bonelord_tome).
Não foi aceito um novo par numérico/inglês ou uma especificação criptográfica.
Isso não é uma busca exaustiva nem prova de que tal evidência inexista.

O solver novo permite quantificar ambiguidades de uma família especificada;
**não há uma família equivalente ancorada independentemente para469**. Não
aplicar esse sucesso restrito aos livros nem reaproveitar os aprendizes que
falharam na rodada 17. A contagem das falas também não valida seu modelo de
serialização. Nenhuma leitura inglesa foi inventada.

Priorizar contextos que separem unidades antes sempre juntas, fronteiras de
origem independente e significado atestado. Novas cópias da mesma composição
podem acrescentar frequência sem resolver a ambiguidade. P01/P03/P05/P06
continuam abertos; permanece necessária validação inglesa independente.

## Reproduzir

`make round18` repete os 30 casos e750 ajustes, as consultas por consenso,
os controles de inconsistência e a contagem exata das falas e dos livros.
`make test` verifica enumeração independente, correlações de variáveis,
limites, efeitos de pistas falsas e a identidade de Fibonacci.

Artefatos: [contextos](../results/round18_context_evidence.json),
[contagens das falas](../results/round18_npc_framing.json),
[protocolo principal](../data/round18_protocol.json),
[protocolo de molduras](../data/round18_framing_protocol.json).
