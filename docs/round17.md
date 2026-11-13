# Rodada 17 — segmentação com vocabulário oculto

**Nenhum método passou no gate para aplicação aos livros.** Foram executados
288 ajustes de desenvolvimento e360 ajustes de qualificação, com 720 avaliações
pareadas de alvos. Vocabulário, chave, número de unidades e fronteiras não
foram fornecidos aos aprendizes. Nenhuma nova leitura do corpus foi produzida.

O resultado principal é uma falha demonstrável do critério de compressão:
nos30 controles copiados cujo código verdadeiro tem dois dígitos, o seletor
escolhe largura12 em todos. Comprimir melhor não identifica necessariamente
a unidade correta. Há também um certificado de dois dicionários diferentes,
ambos com 64 unidades, mesmo custo e mesmos dados, mas fronteiras incompatíveis.

## O que mudou em relação ao parser da rodada 16

A rodada 16 fornecia o dicionário numérico completo ao parser. Agora a API dos
aprendizes recebe apenas mensagens de dígitos e parâmetros congelados. A chave
verdadeira fica no gerador e no pontuador; o módulo de aprendizado não lê
arquivos ingleses, palavras da lore, códigos importados ou cortes verdadeiros.

Foram comparadas três famílias:

1. **Largura fixa:** escolher entre 1–12 pela entropia dos tokens mais custo de
armazenamento do dicionário/contagens, com reset por mensagem e cauda preservada.
2. **BPE:** fundir o par adjacente mais frequente, sem cruzar mensagens;
comprimento máximo12 e orçamento128/256 unidades, incluindo os dez dígitos.
3. **BPE+unigramas:** usar as unidades BPE como candidatas e fazer oito rodadas
de resegmentação Viterbi, com frequências, suavização e custo amortizado do
dicionário. Escolher o snapshot com menor objetivo comum de treino.

O objetivo é inspirado em MDL: entropia ideal mais custo das strings e das
contagens. **Não é um novo codec binário autossuficiente**, nem pontuador de
inglês. A interpretação dos números permanece desconhecida.

## Desenvolvimento, congelamento e qualificação

O desenvolvimento usou oito casos base de Baum/Barrie, já expostos no projeto,
em duas famílias de emissão e dois estilos de treino:32 conjuntos. Cada um
avalia nove configurações, totalizando288 ajustes. A grade inclui ponderação
original ou deduplicação de mensagens, além dos dois orçamentos BPE.

A seleção maximiza a média F1 de fronteiras/spans na pior célula, depois a
média geral, com desempates registrados. Foram escolhidos BPE256 e
unigramas256, ambos com mensagens deduplicadas; o seletor periódico é baseline.

Código, protocolo e fontes foram fixados por hashes antes do desenvolvimento.
Os parâmetros selecionados e o resultado de desenvolvimento foram vinculados
num segundo manifesto **antes** de abrir a qualificação. O congelamento foi
local; não o apresentamos como registro público prévio. Nenhum parâmetro foi
alterado após os resultados da qualificação.

Os autores de qualificação, **Oscar Wilde e Edith Wharton**, são novos para o
projeto e não escolheram os parâmetros. Os textos completos do Project Gutenberg
foram preservados com cabeçalhos/licença, URLs e hashes. As30 janelas base podem
se sobrepor; são dois autores, não30 fontes independentes. Cada caso/família
recebe uma chave nova. Estilos e alvos são pareados:60 chaves,120 conjuntos de
treino e360 ajustes entre os três aprendizes.

As famílias verdadeiras são:

- **Unidades de caracteres com códigos de dois dígitos:**26 códigos aleatórios
distintos, zeros preservados;70 mensagens de 80 letras.
- **Unidades de palavras com códigos de 3–8 dígitos:** chave prefix-free de 64
palavras frequentes;70 mensagens de 32 unidades. O gerador filtra outras palavras,
preservando a ordem relativa: **é um fluxo filtrado, não prosa gramatical**.

O estilo copiado seleciona16 chunks com reposição e os reutiliza até70 mensagens.
Na qualificação isso deixa12–16 mensagens distintas. O estilo sem montagem por
cópia contém 70 mensagens distintas, embora conserve repetições naturais.

Cada alvo tem oito mensagens posteriores, restritas a unidades verdadeiras
vistas no treino. Uma versão pareada permuta as unidades, preservando o
histograma e mudando a ordem. A permutação é controle positivo de fronteiras:
não se exige gramática para decodificar uma chave de emissão fixa.

Não há omissão de zeros, homofonia ou transposição nestes fixtures. Nenhuma
robustez a esses mecanismos ou a vocabulário aberto foi qualificada aqui.

## Resultados

F1 médio nos alvos posteriores; cada entrada mostra **fronteiras / spans de
unidades exatos**. Fronteiras de início/fim da mensagem são excluídas do F1
para não inflar o acerto. Os oito documentos mantêm identidades separadas.

| Emissão verdadeira / treino | Periódico | BPE | BPE+unigramas |
|---|---:|---:|---:|
| Dois dígitos / sem montagem | 1,000 / 1,000 | 0,667 / 0,245 | 0,740 / 0,384 |
| Dois dígitos / copiado | 0,283 / 0,000 | 0,739 / 0,384 | 0,880 / 0,697 |
| Variável / sem montagem | 0,300 / 0,000 | 0,720 / 0,524 | 0,928 / 0,825 |
| Variável / copiado | 0,119 / 0,004 | 0,653 / 0,429 | 0,761 / 0,568 |

O gate exige fronteiras F1≥.95 **e** spans F1≥.95 em pelo menos27/30 casos,
em cada combinação de emissão, treino e alvo: oito células por aprendiz.

O baseline passa30/30 nas duas células de dois dígitos sem cópias, falhando
nas demais. BPE não passa nenhum caso. Unigramas passa apenas1/30 na célula
variável, sem montagem e com alvo permutado; nas outras células,0/30.
**Nenhum pipeline é elegível para a aplicação predefinida ao jogo.**

No alvo permutado de dois dígitos com treino copiado, unigramas atinge média
de 0,958 em fronteiras, mas apenas0,881 em spans. Portanto nem um F1 de
fronteiras acima de 95% autoriza tratar as unidades como recuperadas.

Nos códigos variáveis com cópias, unigramas tem recall médio de fronteiras
de 0,959, mas precisão de 0,633: introduz muitos cortes falsos. Cerca de 79,9%
das unidades verdadeiras dos alvos aparecem sequer como strings no vocabulário
candidato. Sem cópias, essa cobertura sobe para92,1%. São diagnósticos do
aprendizado, sem significados ingleses associados às unidades.

## Por que o melhor custo pode escolher o corte errado

Os controles copiados de caracteres têm160 dígitos por mensagem:80 códigos
verdadeiros de dois dígitos. O baseline escolhe largura12 em 30/30 casos.
Todos os seus cortes internos estão em fronteiras verdadeiras, mas agrupam
seis caracteres por unidade. O recall de fronteiras fica em 13/79 e nenhum
span coincide com um código verdadeiro; a cauda de quatro dígitos é preservada.

Nos dois primeiros casos, o objetivo favorece estritamente a solução errada:

| Fonte | Objetivo com largura verdadeira2 | Objetivo escolhido com largura12 |
|---|---:|---:|
| Wilde | 23.853,50 | 19.515,24 |
| Wharton | 23.554,16 | 19.528,69 |

A largura2 é usada aqui somente como verdade conhecida do diagnóstico, não
como informação dada ao aprendiz. Mais reinícios do mesmo seletor não corrigem
essa preferência do objetivo. Isso não prova que o jogo use largura2 ou12.

## Certificado de subdeterminação, mesmo com 64 unidades observadas

Um exemplo pós-qualificação fortalece o certificado abstrato predefinido:

- DicionárioA contém `1234`, `5678`, `9012` e61 unidades compartilhadas.
- DicionárioB contém `12345`, `678`, `9012` e as mesmas61 unidades.

Ambos têm64 entradas, são prefix-free, usam apenas comprimentos3–8 e explicam
as mesmas70 mensagens, cada uma com 32 unidades. **Todas** as 64 unidades de
cada dicionário aparecem35 vezes. O objetivo de ambos é exatamente15.745.

Ainda assim, o mesmo raw `123456789012` tem os cortes:

`1234 | 5678 | 9012` ou `12345 | 678 | 9012`.

Uma combinação nova, `12349012`, é aceita porA e não porB. O certificado
completo inclui os dados e as duas análises. Não usa palavras inglesas
inventadas. Mostra que parse único **com chave conhecida** não identifica a
chave ou as fronteiras quando o vocabulário está oculto. É um contraexemplo
da classe, não uma prova de que os dados reais de 469 tenham essa origem.

## Decisão e próximos experimentos

Registrar a falha de potência e manter os modelos fora de novas buscas de
tradução em 469. A missão não ganhou um parser raw→unidades validado. Também
não houve rejeição geral de cifras por palavras, sílabas ou conceitos.

O próximo modelo precisa de restrições que distingam unidades de combinações
recorrentes: diversidade de contextos, evidência externa de fronteiras ou
significado, e representação de segmentações alternativas. Não ampliar
automaticamente merges até sair uma palavra. Uma nova versão deve ter
qualificação própria, sem reusar estes resultados como confirmação prospectiva.
As entregas P01/P03/P05/P06 continuam abertas.

## Reproduzir

`make round17` repete integralmente os 288 ajustes de desenvolvimento, verifica
a seleção sem modificar arquivos, refaz os 360 ajustes e720 avaliações da
qualificação e confere os certificados. Nenhum dado do jogo é ajustado.
`make test` inclui testes independentes de Viterbi, fronteiras entre mensagens,
caudas, métricas e equivalência dos dois dicionários.

O script de benchmark recusa reabrir a qualificação como um teste novo quando
o resultado já existe. Use o replay. O manifesto do resultado vincula código,
documentação e saídas; tempos e logs são metadados variáveis.

Artefatos: [desenvolvimento](../results/round17_development.json),
[qualificação](../results/round17_qualification.json),
[diagnósticos/certificado](../results/round17_failure_diagnostics.json),
[protocolo](../data/round17_protocol.json),
[fontes](../data/segmentation_reference/SOURCES.json).
