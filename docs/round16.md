# Rodada 16 — grupos numéricos como palavras ou outras unidades

**Nenhuma tradução foi encontrada.** A rodada verificou um dicionário finito
de 45 grupos numéricos observados, testou sua transferência aos70 livros e
produziu certificados dos cortes nas cópias de falas. O resultado novo mais
útil é uma restrição de serialização: o grito de 20 dígitos do bibliotecário
termina dentro de um código importado nas seis ocorrências nos livros.
Isso impede usá-lo diretamente como um bloco completo desse stream.

## Uma cópia raw não fornece automaticamente os mesmos códigos

O grito `78572611857643646724` ocorre nos IDs 12,21,24,26,30 e56.
Foram examinados todos os alinhamentos compatíveis dos livros, sem selecionar
o que produziria palavras. Os seis livros relevantes têm um alinhamento cada.

| IDs | Início do grito | Fim do grito | Contexto fora do grito, no livro |
|---|---|---|---|
| 12,21,24,30 | dentro do código27 | dentro do código43 | dígito2 antes e3 depois |
| 26,56 | fronteira de código78 | dentro do código43 | dígito3 depois |

Nos quatro primeiros, o menor trecho circundante delimitado por códigos é:

`27 85 72 61 18 57 64 36 46 72 43`

Nos outros dois, é:

`78 57 26 11 08 57 64 36 46 72 43`

Nestes dois últimos o zero de 08 está omitido na serialização importada.
As duas listas diferentes contêm o mesmo trecho raw do NPC, com os cortes
mostrados. O outro grito, `485611800364197`, ocorre uma vez no ID 30 e tem
ambos os extremos alinhados: `48 56 11 80 03 64 01 97`, com omissão em 01.

Os dígitos vizinhos são **contexto observado nos livros**, não correções da
fala. Não acrescentamos2 ou3 à transcrição do NPC e não atribuímos letras
inglesas a essas listas. A constatação é condicional aos códigos importados:
eles ainda não são uma tokenização demonstrada da linguagem real.

Há7 certificados explícitos, verificados também por reconstrução dos livros
a partir de cada código e de sua emissão raw. As seis cópias não são seis
observações independentes de significado. A evidência restringe a hipótese
de transferência de blocos completos; não prova que NPCs e livros tenham
cifras diferentes ou que a transcrição do NPC esteja errada.

Um contraponto concreto: a fala isolada também admite os pares fixos
`78 57 26 11 85 76 43 64 67 24`, todos presentes no inventário importado.
Isso não escolhe uma leitura verdadeira; demonstra por que não podemos
rejeitar outra segmentação ou outro enquadramento da fala a partir dos cortes
nos livros. Nenhuma dessas listas recebe gloss inglês.

## O dicionário observado é consistente, mas incompleto

O inventário inclui 13 registros fora da entrevista de Chayenne, com 49 grupos
numéricos e45 valores distintos. São grupos observados entre espaços ou
pontuação, não palavras inglesas comprovadas. Chayenne ficou fora deste teste
de grupos; isso não presume que ela use outro algoritmo.

O teste exato de Sardinas–Patterson encontrou **decodificabilidade única** para
os 45 valores. Apesar de haver relações de prefixo, como67/677, nenhuma
sequência finita de unidades desse dicionário colide com outra. O algoritmo
explora estados residuais sem limite artificial;12 estados bastam no caso
completo. Uma implementação independente por conjuntos verifica o método em
testes de codebooks pequenos, incluindo ciclos e colisões construídas.

Ao retirar espaços, os 13 registros voltam a ser segmentados exatamente com
o dicionário completo. É consistência no próprio inventário fornecido ao
parser, **não previsão de palavras inéditas ou tradução**. Um vocabulário maior
pode alterar a propriedade de decodificabilidade única.

Nenhum dos 70 livros admite segmentação completa usando apenas esses45 grupos.
Isso rejeita a completude desse vocabulário para os livros, não a hipótese
geral de códigos de palavras, sílabas, morfemas ou conceitos.

## Cobertura, custo e controle das cópias

Foram congeladas quatro variantes antes das novas estatísticas. A programação
dinâmica mede a menor quantidade de dígitos sem unidade conhecida. Um codec
separado escolhe referências ou dígitos literais pelo menor custo em bits.
As duas medidas têm objetivos diferentes: cobertura não significa compressão.

| Dicionário | Unidades | Maior cobertura por concatenação | Economia condicional nos livros | Saldo pagando dicionário |
|---|---:|---:|---:|---:|
| Todos os grupos | 45 | 31,73% | 41 bits | −1.213 bits |
| Comprimento≥3 | 42 | 6,50% | 38 bits | −1.191 bits |
| Sem os dois gritos copiados | 43 | 30,84% | 0 | −1.096 bits |
| Comprimento≥3, sem gritos | 40 | 5,46% | 0 | −1.071 bits |

A cobertura alta do primeiro modelo vem sobretudo de unidades curtas como0,
1 e67. Não as lemos como inglês. As pequenas economias de 41/38 bits ocorrem
apenas nos IDs 24 e30 e desaparecem ao remover os dois gritos predefinidos.
Nos IDs 20/54 do reservado exposto não há economia em nenhuma variante.

O codec transmite a lista ordenada de grupos uma vez, cobrando comprimentos
e quatro bits por dígito. Cada livro recebe comprimento gamma e um bit para
escolher raw ou referências. Uma referência custa flag+índice de largura fixa;
um literal custa flag+quatro bits. Todos os bitstreams foram decodificados e
comparados aos números originais. É comparação entre esses formatos, sem
alegação de compressão ótima ou de MDL de toda a linguagem.

Como baseline, dicionários de substrings escolhidas por frequência nos68 livros
de descoberta, com exatamente o mesmo número e comprimentos de entradas,
economizam2.194–2.733 bits líquidos. Não recebem significados ingleses. A
vantagem mostra que este codec aproveita repetições sem identificar semântica;
o baseline não é uma prova de ausência de mensagem.

Nota de nomenclatura: o campo JSON `minimum_covered_fraction` contém
1−mínimo_de_dígitos_sem_cobertura/total, portanto é a **maior cobertura possível**
nesse problema. A nota de escopo explicita esse nome; não é uma estimativa de
percentual traduzido.

## Nulos e transferência entre fontes

Foram gerados99 controles de cada família,297 dicionários ao todo:

- Bijeção global dos dígitos apenas no dicionário.
- Embaralhamento dos dígitos dentro de cada grupo distinto, preservando seus histogramas.
- Substrings distintas dos livros de descoberta, amostradas com comprimentos iguais aos grupos.

Os livros ficam intactos, com todas as cópias e dependências, em cada controle.
Cada dicionário passa pelas mesmas quatro ablações e pelo mesmo parser exato:
1.188 avaliações de modelos. Colisões de entradas são reamostradas conforme
o protocolo para preservar cardinalidade e comprimentos.

A estatística primária é o maior saldo líquido entre os quatro modelos;
p=1,00 nas três famílias. Esse objetivo prefere o menor dicionário, que não
economiza bits nos livros. Individualmente, os modelos com os gritos dão
p=.01 contra as duas randomizações de dígitos e p=.64/.68 contra substrings dos
próprios livros. Os dois modelos sem os gritos dão p=1,00. O piso é .01 com 99
réplicas. O sinal de correspondência específica é compatível com as cópias já
conhecidas, não com uma tradução descoberta.

Deixando cada grupo de fonte inteiro de fora, apenas3/13 registros são
completamente segmentados: o mesmo grito reproduzido por Evil Eye/Elder,
contado duas vezes, e o 0 já visto em Knightmare. Nenhuma frase nova não trivial
foi reconstruída. O grupo 67538 é compartilhado por Avar Tar e pela enquete,
sem gloss; essa reutilização também não fornece significado.

O diagnóstico de fronteiras encontra205 ocorrências raw dos grupos de
comprimento≥3, reduzidas a 73 assinaturas de contexto.22 têm ambos os extremos
alinhados em todos os parses fornecidos;183 não têm nenhum parse com ambos
alinhados. Por exemplo,3478 tem18 ocorrências alinhadas e6 não alinhadas.
Uma coincidência curta não garante que a ocorrência seja uma unidade lexical.
As assinaturas não são novas observações independentes.

## O que foi qualificado

São 30 passagens base de dois autores já expostos, em duas formas pareadas:
120 palavras contíguas e montagem por cópia. Para cada passagem foram criados
três dicionários numéricos: livre de prefixos, com prefixos mas unicamente
decodificável, e com ambiguidade plantada.

O parser recupera exatamente as unidades em 120/120 casos decodificáveis e
detecta ambiguidade em 60/60 casos plantados. Todas as 180 serializações voltam
aos números originais. Os seis gates de 30 casos passam. **O dicionário é
fornecido ao parser:** isso qualifica segmentação e detecção de ambiguidade,
não inferência de vocabulário desconhecido, chave ou inglês.

O [protocolo](../data/round16_protocol.json), código e entradas foram congelados
por hashes antes das novas estatísticas. Os certificados de contexto são uma
explicação posterior do diagnóstico predefinido, sem ajustar parâmetros ou
reabrir a busca. O corpus e as fontes já estavam expostos; não há novo par
inglês/números nem validação semântica independente.

## Próxima decisão e reprodução

P05 ganhou consistência formal de um inventário e uma restrição concreta de
fronteiras. Ainda precisa de inferência com unidades desconhecidas e/ou par
semântico independente. Não usar as seis cópias do grito como crib de um
mesmo vetor importado, nem completar o dicionário com palavras da lore até
aparecer uma frase. A próxima qualificação de segmentação deve esconder o
vocabulário, medir fronteiras e controlar compartilhamento de trechos.

`make round16` regenera a análise inteira, incluindo os 297 controles,180 alvos
de qualificação e7 certificados, e compara os artefatos publicados.
`python scripts/wordcode_transfer_experiment.py --run` regenera os resultados
principais; `python scripts/wordcode_boundary_certificates.py` regenera as
explicações. Não trocar o protocolo publicado via `--freeze`.

Artefatos: [transferência e codecs](../results/round16_wordcode_transfer.json),
[decodificabilidade](../results/round16_decodability.json),
[fronteiras](../results/round16_boundaries.json),
[certificados](../results/round16_boundary_certificates.json),
[qualificação](../results/round16_qualification.json).
