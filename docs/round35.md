# Rodada 35 — qualificação E2 e encerramento do ciclo v3

27/11/2026. Base: `9672fa09bed19aaff8d4909a513a455152969150`.
**Nenhuma tradução nova. O método M1 não qualificou; o resultado da missão
continua I — inconclusivo.** O [dossiê de conclusão](mission_conclusion_v3.md)
adjudica as seis etapas, incluindo as dependências que não foram acionadas.

## Hipótese e protocolo

Hipótese H127: uma busca com largura limitada, restrições de dicionário e
pontuação inglesa consegue selecionar a chave correta na família que admite
153.174.074 chaves lexicais para Knightmare. Antes de aplicar ao jogo, exigimos
recuperação em controles de texto conhecido, cuja resposta não entra no solver.

O [protocolo](../data/round35_protocol.json) fixa emissões não vazias de uma
a três letras por dígito, fronteiras de palavras fornecidas, o léxico CMU da
R23 e pontuação de unigramas/bigramas de palavras. Isso aproxima frequência
e sucessão de palavras; **não é um analisador sintático nem uma medida de
significado**. O modelo usa Alice, Frankenstein e Pride and Prejudice.

Duas configurações foram fixadas antes dos resultados: beam 64 e 256. A
segunda usa outros 30 trechos naturais; não é uma tentativa ajustada depois
de observar a primeira. Limites por ajuste: 300.000 linhas locais por grupo,
20 milhões de verificações de compatibilidade, um milhão de extensões por
profundidade, 30 segundos internos, 35 externos e 4 GiB de espaço de endereços.
Ao atingir limite, não se declara ausência de chave. A confiança usa diferença
de pontuação entre chaves retidas, sem alegar unicidade exaustiva.

Os manifestos [pré-execução](../data/round35_prerun_manifest.json) e
[de execução](../data/round35_execution_manifest.json) fixam entradas e código.
Os hashes documentam integridade; não provam cegamento externo.

## Dados e limites do benchmark

Selecionamos 60 trechos de sete palavras de Dracula e Moby Dick, 15 por autor
e configuração. São segmentos delimitados por pontuação após normalização;
não afirmamos que todos sejam orações completas. Os livros já eram conhecidos
em benchmarks anteriores, mas os trechos/cifragens desta rodada são novos e
os autores não participam do treinamento do pontuador. Nenhum dos 60 segmentos
normalizados coincide integralmente com uma sentença do treinamento.

O encoder foi fixado antes do solver: fusões de pares, até três letras por
unidade e sete a dez unidades distintas. Dos 181 segmentos examinados,
60 foram selecionados, 78 não receberam inventário pelo encoder guloso,
42 continham palavras fora do léxico e um era duplicado. Isso limita a cobertura;
não prova impossibilidade de representar os outros trechos por outro encoder.

Cada trecho gera condições pareadas: sete palavras, repetição tripla, espaços
removidos, nome sintético fora do léxico, dígito ausente, controle uniforme e
embaralhamento dentro de grupos. Há ainda 30 pares CAT/RAT ambíguos por
configuração, construídos com três moldes. **480 casos não equivalem a 480
observações independentes.** Os dez probes reservados de cada base são novas
combinações de unidades, não prosa inglesa. Medem transferência da chave;
o inglês é avaliado separadamente na recuperação do trecho de entrada.

## Resultados da qualificação

| Cenário, 30 casos por configuração | M1/64 | M1/256 | Interpretação |
| --- | ---: | ---: | --- |
| Trechos naturais de sete palavras | 0 aprovados | 0 aprovados | Exigidos 27/30; todos atingiram limites |
| Trecho repetido três vezes | 0 | 0 | Repetição não produziu recuperação neste procedimento |
| Nome fora do léxico | 0 | 0 | Não qualificado para esse cenário |
| Sem espaços | 0 | 0 | Explicitamente não suportado; nenhuma busca iniciada |
| Uniforme, aceitações falsas | 0 | 0 | Abstenção em todos os casos |
| Embaralhado, aceitações falsas | 0 | 0 | Abstenção em todos os casos |
| Ambiguidade/dígito ausente, falsas certezas | 0 | 0 | Abstenção em todos os casos |

No total: **418 ajustes limitados, 60 casos não suportados e dois casos sem
candidata no beam**. Nenhum retornou uma candidata aceita. Para cada controle
negativo, o intervalo binomial exato bilateral de 95% com 0/30 eventos é
[0; 11,57%], condicionado ao gerador do benchmark. Esse zero é vacuamente
seguro porque o método se abstém de tudo; não demonstra discriminação útil.
Também não permite concluir que o pontuador rejeitou uma tradução correta
após examinar exaustivamente as possibilidades.

As execuções consumiram 235,812 segundos de CPU dos subprocessos; a contagem
inclui positivos, negativos e falhas. [Todos os resultados](../results/round35_qualification.json).

### Incidente técnico preservado

O processo pai foi pausado ao considerar uma alteração, mas a configuração
V2 pré-declarada já havia começado. A alteração **não foi feita**; o processo
foi retomado com os mesmos parâmetros. A pausa afetou `v2_name_oov7_02`,
registrado originalmente como timeout externo de 47,178 segundos.

Esse único caso foi reexecutado sem alteração: atingiu o limite de extensões
em 1,386 segundos, com 1,382 segundos de CPU. A decisão continua idêntica,
sem candidata ou aceitação. O resultado original permanece byte a byte;
o [replay técnico](../results/round35_technical_replay.json) guarda ambos.
A pausa não é escondida dos tempos, não é uma terceira configuração e não
autoriza descartar os fracassos. A reprodução limpa usa esse replay documentado
para comparar a causa do limite desse caso.

## Diagnóstico com a resposta conhecida

Como as buscas foram limitadas, não bastava atribuir o fracasso à linguagem
ou ao pontuador. Fixamos então um [diagnóstico posterior](../data/round35_oracle_protocol.json),
que recebe intencionalmente a resposta verdadeira. **Não é recuperação cega
nem qualificação de um segundo decoder.** Testa a identificabilidade sob o
mesmo modelo e pontuação, sem ajustar mensagens do jogo.

Em todos os 60 trechos, procuramos: outra segmentação que produza exatamente
o mesmo inglês, mas altere um probe; ou substituição da emissão de um único
dígito que mantenha todas as palavras no léxico, tenha pontuação igual ou
superior e altere a transferência. A busca de segmentações tinha teto de
100.000 estados por caso; nenhuma o atingiu. Ausência de testemunha nessa
vizinhança não é prova de unicidade global.

| Achado | Casos, de 60 |
| --- | ---: |
| Outra chave com mesmo inglês de entrada, mas transferência diferente | 30 |
| Alterar uma emissão gera pontuação igual ou melhor e transferência diferente | 54 |
| Pelo menos uma das duas testemunhas | 55 |
| Inglês verdadeiro abaixo do limiar de aceitação | 3 |

As categorias se sobrepõem. São **84 testemunhas**, verificadas por código
separado: emissões literais, palavras do léxico, pontuação recalculada e probe
divergente. O diagnóstico levou 2,581 segundos de CPU. Os cinco casos sem
testemunha continuam não resolvidos; não são cinco sucessos de recuperação.
Não afirmamos que toda alternativa lexical seja inglês coerente, que toda
divergência exceda 5% das letras ou que todas as alternativas fossem alcançadas
pelo beam. As testemunhas demonstram falta de identificação única por esse
critério; aumentar apenas a capacidade de busca não fornece a restrição ausente.

Um exemplo **do benchmark, não de Tibia**: em “what is it thats wrong with her”,
as emissões `0=o, 1=ng` e `0=on, 1=g`, mantendo as outras, reproduzem o mesmo
trecho. O probe `37891` recebe `riesng` ou `riesg`. São strings de teste sem
pretensão semântica, que mostram como fronteiras invisíveis impedem inferir
transferência a partir de uma frase perfeita.

[Testemunhas integrais](../results/round35_oracle.json) e
[verificação independente interna](../results/round35_audit.json).

## Decisão e reprodução

H127: M1 suspenso após duas configurações não qualificadas. H128: confirmada
a existência das ambiguidades certificadas, no modelo declarado. Nenhuma
conclusão de impossibilidade universal, tradução comunitária validada ou
geração original sem texto. Nenhuma candidata de Avar Tar, Knightmare ou
Chayenne foi produzida nesta rodada.

E3 não é acionada: M1 não qualifica, E1 não trouxe mecanismo ou âncoras
semânticas novas, e nenhum novo certificado motivou outra família. A segunda
vaga de E2 é dispensada; o plano não exige inventar uma restrição para ocupá-la.
E4 não dispõe de artefato original elegível; E5 não dispõe de candidata e
referência independente. Essas etapas recebem uma disposição explícita,
sem fingir que buscas ou validações condicionais foram executadas.

```sh
make round35       # hashes, cenários, decisões e testemunhas; offline
make round35-full  # recria fixtures/modelo, repete os 480 casos e o diagnóstico
make test
```

O modelo derivado de 2,5 MB não precisa ser versionado: é reconstruído dos
textos públicos fixados e conferido por SHA256. A auditoria E6 em cópia limpa
repete R30 (corpus e histórico), R33 (contagem principal e 100 casos pequenos),
R34 (registros de fontes), toda a R35 e a suíte de testes. O
[registro de reprodução](../results/round35_clean_replay.json) contém comandos,
tempos e hashes dos logs. Cópia limpa significa arquivos públicos sem caches,
clones ignorados ou modelo pré-gerado, na mesma máquina; não revisão externa.
**Passaram os cinco procedimentos e os 330 testes; nenhum dos 903 arquivos
do snapshot foi alterado.** Fixtures e modelo foram regenerados de forma
idêntica; todos os 480 casos e os 60 diagnósticos foram reproduzidos.
O [dossiê final](mission_conclusion_v3.md) informa o resultado efetivamente
obtido e os critérios finitos de reabertura.
