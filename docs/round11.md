# Décima primeira rodada: cobrar os cortes antes de inferir o mecanismo

**Nenhuma tradução foi encontrada.** Dois codecs exatos com custos explícitos
foram comparados. O critério distingue fronteiras/cortes em 119/120 alvos
sintéticos pareados, mas o livro de Kharos não favorece o formato de cortes
livres: referências a códigos completos custam 277 bits e referências a
dígitos custam 286 bits. Essa vantagem de nove bits é condicional e pequena;
não autentica a tokenização, a edição histórica ou um significado inglês.

## Pergunta e exposição prévia

A rodada anterior cobriu os 137 dígitos de Kharos com 14 fragmentos raw, sete
dos quais sem ocorrência delimitada por códigos importados. Isso poderia
sugerir cortes dentro dos códigos, mas o objetivo anterior minimizava peças,
sem cobrar endereços ou comprimentos. Uma cobertura representativa não é um
algoritmo de tradução nem uma reconstrução do trabalho do autor.

Nesta rodada, congelamos `data/copy_wire_protocol.json` antes de executar os
novos codecs. Os livros, o alvo de Kharos e os autores ingleses já eram
conhecidos; o protocolo não transforma nenhum deles em teste semântico cego.
Nenhum parâmetro foi ajustado após os resultados.

## Dois formatos de bits realmente decodificáveis

Ambos recebem a mesma biblioteca ordenada de livros raw e as anotações de
fronteiras compatíveis com seus códigos fornecidos. Esse material é
**informação lateral compartilhada**. Não contabilizamos seu custo: medimos
bits do alvo condicionados à biblioteca, não compressão autossuficiente do
corpus inteiro ou MDL completo do mecanismo.

O cabeçalho tem um bit que identifica a família e Elias gamma do comprimento
raw mais um. Cada token é um literal, com flag e quatro bits para o dígito,
ou uma referência, com flag e endereço de livro. As referências diferem:

|Formato|Endereço dentro do livro|Comprimento transmitido|
|---|---|---|
|Raw|Posição de dígito em largura fixa|Gamma do número de dígitos|
|Códigos|Alinhamento e posição de código em larguras fixas|Gamma do número de códigos|

As larguras são `ceil(log2(tamanho do espaço de endereços))`; um espaço de
tamanho um custa zero bits. O decoder conhece as larguras pela biblioteca.
O formato de códigos permite todos os 79 alinhamentos dos 70 streams fixos,
sem selecionar um deles por inglês. Nenhuma referência atravessa livros.
O máximo é 96 dígitos por referência; os comprimentos menores não têm limiar
escolhido depois do teste, pois seu custo compete diretamente com literais.

Programação dinâmica encontra o menor custo exato. Para uma mesma substring,
guardamos a testemunha com menor custo, com desempate pelo bitstream. Essa
deduplicação não elimina uma alternativa mais barata nem identifica uma
história de edição. Contagens de caminhos se referem às opções depois dessa
deduplicação, não ao total de testemunhas ou traduções.

Todos os bitstreams são decodificados e comparados aos dígitos originais.
Literais continuam sendo dígitos sem códigos semânticos atribuídos. As
referências do formato de códigos também não estabelecem uma tokenização
global do alvo através das junções e dos literais.

## Controles e gate congelado

Cada fixture contém 70 fontes de 64 códigos, gerados por uma cifra homofônica
de 99 códigos com chave aleatória e omissões IID de zeros. São 30 conteúdos
base, 15 de Baum e 15 de Barrie, em janelas não sobrepostas dentro de cada
autor. Os autores já haviam sido expostos em outras rodadas.

Para cada conteúdo há duas bibliotecas pareadas: inglês cifrado e a mesma
lista de códigos embaralhada uma vez dentro de cada fonte, antes da
serialização. Esse segundo caso preserva os histogramas dos códigos por
fonte e destrói a ordem das letras; algumas estruturas residuais podem ficar.

Cada alvo concatena quatro trechos de fontes distintas, com 32 códigos por
trecho. A condição alinhada preserva esses códigos completos. A condição
cortada remove o primeiro e o último dígito de cada trecho, ambos no interior
de códigos serializados com dois dígitos. Os spans verdadeiros são conhecidos
do experimento, mas não fornecidos ao otimizador. O alvo cortado não precisa
constituir uma mensagem inglesa coerente.

O gate exige pelo menos 27/30 preferências estritas corretas em cada célula;
empates contam como falhas. Definimos delta como bits de códigos menos bits
raw: negativo favorece códigos e positivo favorece raw.

|Conteúdo das fontes|Corte do alvo|Acertos|Delta médio em bits|Gate|
|---|---|---:|---:|---|
|Inglês cifrado|Fronteiras de códigos|30/30|-7,20|Passa|
|Inglês cifrado|Interior de códigos|30/30|22,27|Passa|
|Códigos embaralhados|Fronteiras de códigos|30/30|-7,17|Passa|
|Códigos embaralhados|Interior de códigos|29/30|24,10|Passa|

São 120 alvos **pareados**, não 120 textos ou autores independentes. O resultado
qualifica essa discriminação operacional, sob a geração especificada. As
distribuições de comprimentos e os códigos verdadeiros dos controles não
autenticam os códigos importados do jogo. O desempenho similar nas duas
condições de conteúdo mostra que a preferência não é um detector de inglês.

## Kharos: resultado com custo pago

Os índices foram construídos apenas com os 70 textos de Hellgate. Os 137
dígitos de Kharos não entraram no dicionário de fontes.

|Formato|Bits totais|Bits de cabeçalho|Referências|Dígitos literais|
|---|---:|---:|---:|---:|
|Raw|286|16|10|9|
|Códigos|277|16|10|13|

O formato de códigos gasta 29 bits a menos nos endereços/comprimentos das
referências e 20 bits a mais nos quatro dígitos literais adicionais. O saldo
é de nove bits. Há quatro caminhos mínimos após deduplicação no formato raw
e um no formato de códigos. Isso não é unicidade de plaintext.

Portanto, a cobertura anterior em 14 peças não basta para inferir montagem
por cortes raw. Sob estes dois formatos, a opção alinhada é um pouco mais
econômica. O resultado não prova que o autor usou uma das duas regras ou que
as unidades importadas sejam a cifra verdadeira. As famílias não são
exaustivas e há treze dígitos não explicados por referências no vencedor.

## Controles de ordem e dependência entre livros

Foram feitas 99 permutações de dígitos e 99 permutações de blocos raw de oito
dígitos, preservando comprimento e histograma exato de dígitos do alvo. Os
dois parsers foram reotimizados em cada alvo com os mesmos índices fixos.

|Controle|Delta médio em bits|Rank exploratório superior do delta observado|
|---|---:|---:|
|Dígitos embaralhados|-13,78|0,28|
|Blocos de oito embaralhados|-20,41|0,02|

Esses ranks são descritivos, em material exposto e com dois controles
diferentes. Não sustentam uma descoberta semântica ou a escolha de um p-valor
favorável. A vantagem observada em códigos é menor que a vantagem média dos
controles; compressão ou sinal estatístico não autoriza tradução.

Também repetimos a predição cruzada entre os dois componentes do grafo de
reutilização raw de 16 dígitos: 68 livros e os livros 20/54. Cada componente
foi codificado somente a partir do outro, sem aprender fragmentos nos alvos.
Os totais são 43.266/42.298 bits raw/códigos para os 68 livros e 338/320 para
os dois. O pequeno conjunto de duas fontes limita fortemente o primeiro
sentido de predição; os custos não são diretamente comparáveis aos de uma
biblioteca de 70 fontes. Sobreposições menores ou transformadas persistem.
Não é uma divisão semântica independente ou prospectiva.

## O que encerra e o que falta

O teste encerra a inferência simples de que sete cortes incompatíveis em uma
cobertura escolhida demonstram um mecanismo raw. Uma comparação que paga os
endereços não favorece esse mecanismo no alvo sob os formatos fixados.

Não há nova regra de zeros, chave inglesa, leitura candidata ou prova de
ausência de mensagem. Os próximos passos de maior valor continuam sendo uma
regra raw→tokens atestada ou um par externo com significado explícito. Não
ampliaremos formatos de compressão apenas para inverter estes nove bits.
A frente histórica das matrizes continua aberta, sem nova captura nesta rodada.

## Reprodução

```sh
make round11
python scripts/run_round11.py --full
make test
```

O primeiro comando verifica hashes, gates, oito condições positivas
selecionadas previamente por índice de autor, todos os 198 controles e os
70 alvos entre componentes. `--full` reproduz os 120 alvos sintéticos.
Todos os streams reexecutados são decodificados sem perda. Os seis novos
testes incluem comparação da programação dinâmica com enumeração exaustiva
em alvos pequenos, alinhamentos ambíguos e rejeição de streams inválidos.
Resultados completos em `results/copy_wire_experiment.json`.
