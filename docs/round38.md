# Rodada 38 — todas as chaves condicionadas por FOOL e sua transferência

**A associação `345 → FOOL` não forneceu uma tradução.** Enumeramos todas as
3.976 chaves da família fixada que aceitam essa associação na fala de Knightmare.
Elas só permitem `3466 → FORR` ou `3466 → FOSS`, e todas produzem `453 → OOLF`
no poema de Avar Tar. Esse fragmento não admite palavra nem segmentação lexical
no banco usado. A pista fica encerrada como explicação compartilhada dessas
mensagens **dentro desta família**. Código de palavras inteiras, anagramas e
outros mecanismos não são excluídos por esse resultado.

O resultado geral da missão continua **I — inconclusivo**. Não houve nova
tradução candidata, confirmação de ausência de significado, nova fonte externa
ou reabertura do método M1 reprovado na R35.

**Protocolo e qualificação.** O protocolo, 597 controles e seleção das mensagens
de transferência foram fixados antes dos novos resultados. A pergunta parte
de uma observação posterior da R37; FOOL veio de interpretação comunitária,
não de resposta conhecida fornecida pelos autores de Tibia. Esse histórico
impede tratar a comparação como teste confirmatório de significado.

Mantivemos as regras R33/R36: cada dígito observado emite sempre a mesma unidade
de uma a três letras; espaços de Knightmare delimitam palavras; homofonia entre
dígitos é permitida. Usamos as 122.368 formas do CMU fixado, incluindo a adição
hipotética anterior de BONELORD. Não adicionamos palavras para melhorar a saída.

Um novo enumerador usa uma árvore de prefixos do dicionário para evitar
percorrer repetidamente formas incompatíveis. Antes do ajuste real, suas
contagens **e conjuntos completos de chaves** concordaram com enumeração direta
independente em 70 casos pequenos. Os 60 casos binários usam unidades A/B de
comprimento 1–3; outros dez casos unários reproduzem os escopos dos sete grupos
de Knightmare. Isso qualifica a aritmética do enumerador, não um tradutor de inglês.

O alvo terminou completo com 3.976 chaves distintas, todas conferidas literalmente,
concordando com a contagem anterior feita pelos outros algoritmos. Cada chave
produz uma sequência diferente de sete palavras. O dígito `2` permanece desconhecido.

**O que sustenta as chaves.** A enumeração completa força:

```text
3 = F
4 = O
5 = OL
6 = R ou S
```

| Saída de `3466` | Chaves |
|---|---:|
| FORR | 1.919 |
| FOSS | 2.057 |

Uma segunda implementação, baseada em partições explícitas de palavras,
confirmou as duas atribuições parciais acima a partir do suporte completo de
`3466` e da hipótese FOOL. As demais emissões variam: `3478` admite 40 formas,
`90871` admite 3.012 e `97664`, 46. Nenhuma chave torna todas as sete palavras
presentes nas três obras de sensibilidade fixadas: *Alice*, *Frankenstein* e
*Pride and Prejudice*. FORR e FOSS estão ausentes desse conjunto, assim como
as 46 formas de `97664`.

Essa ausência vale apenas para os três arquivos selecionados. Eles não abrangem
todo o inglês nem classificam nomes próprios. Incluímos inclusive seus cabeçalhos
na contagem, conforme o protocolo. Não usamos frequência para escolher uma chave
nem apresentamos uma combinação lexical como frase coerente.

**Controles mais amplos.** Foram 199 sorteios em cada família, mantendo comprimentos
dos grupos e contagens de dígitos. A terceira família preserva o multiconjunto
global dos primeiros seis grupos, permitindo mover dígitos entre eles.

| Controle | Concluídos | Limitados | Positivos entre concluídos | Maior contagem concluída |
|---|---:|---:|---:|---:|
| Embaralhar cada grupo, inclusive o grupo associado a FOOL | 196 | 3 | 17 | 944 |
| Embaralhar os demais grupos, mantendo `345` | 196 | 3 | 18 | 506 |
| Redistribuir os demais dígitos, mantendo `345` | 169 | 30 | 4 | 4.268 |
| **Total** | **561** | **36** | **39** | **4.268** |

Os 36 casos limitados atingiram cinco milhões de visitas locais. **Nenhum foi
convertido em zero.** Seis deles já tinham chaves encontradas; portanto, ao menos
45 dos 597 controles admitem uma chave. Considerando os casos ainda desconhecidos,
o número de controles positivos está entre 45 e 75. Esses limites descrevem o
lote finito, não intervalos de confiança sobre a origem de 469.

O controle `pooled_other_digits_anchor_fixed_91`,
`7466 16 94307 96477 6830 8 345`, tem exatamente 4.268 chaves. Logo, um texto
obtido por redistribuição dos dígitos também pode exceder a contagem real de
3.976. Nos dois grupos de controles internos nenhuma contagem concluída atingiu
a real, mas seus casos limitados não permitem um ranking completo.
Não calculamos p-valor: a âncora foi selecionada após olhar o texto, o experimento
é diagnóstico e há buscas incompletas.

**Transferência sem selecionar chaves.** Aplicamos todas as chaves, sem alterações,
aos 14 registros canônicos restantes do inventário. Esses textos já eram públicos
e estavam expostos em rodadas anteriores; não possuem respostas inglesas reservadas.
O grito repetido por Evil Eye e Elder Bonelord foi marcado como duplicata, não
como duas confirmações. O grupo `0`, reutilizado do próprio ajuste, também não
constitui validação independente. Nomes e números isolados não são automaticamente
palavras comuns que precisem seguir a mesma regra.

Foram examinadas duas condições: cada grupo numérico deve formar uma palavra,
ou cada grupo pode conter uma sequência segmentável de palavras do mesmo léxico.
Na segunda condição, os espaços fornecidos continuam sendo fronteiras. Isso
mede apenas compatibilidade lexical e não gramática ou sentido.

| Fonte e fragmento | Saída unânime nas 3.976 chaves | Resultado lexical |
|---|---|---|
| Avar Tar: `453` | `OOLF` | Nem palavra nem sequência segmentável |
| Your True Colour: `34334` | `FOFFO` | Nem palavra nem sequência segmentável |

Esses impedimentos não dependem de `2`: nenhuma futura atribuição a esse dígito
os corrige. São consequências verificáveis do conjunto completo de chaves,
nunca correções de texto ou novas traduções. O poema de Avar completo já falhava
na família lexical da R23; esta rodada dá uma razão particular para o subconjunto
condicionado por FOOL, não uma segunda descoberta independente da mesma rejeição.

As duas falas de Chayenne continuam indisponíveis para decodificação completa,
pois contêm `2`. Nos textos sem esse dígito, houve segmentações lexicais para
2.269 chaves no grito compartilhado e 71 no primeiro grito de Wrinkled Bonelord.
Não são traduções: existem múltiplas chaves, não há significado reservado para
comparar e nenhuma seleção por coerência foi executada. A frase de duas partes
de Elder Bonelord não admite sequer segmentação completa com qualquer dessas chaves.

**Reprodução e registro de falhas.** `make round38` verifica integridade, todos
os testemunhos reais, as regras de geração dos controles e as deduções.
`make round38-full` repete os 70 oráculos, a enumeração real e os 597 ajustes.
Os resultados preservam contagens, limites e tempos por ajuste. A primeira
auditoria detectou uma diferença de representação entre tuplas Python e listas
JSON; a comparação foi normalizada sem alterar experimento ou resultado.
O manifesto anterior e a correção estão preservados em
[round38_audit_correction.json](../data/round38_audit_correction.json).

Artefatos centrais: [protocolo](../data/round38_protocol.json),
[resultados](../results/round38/summary.json),
[deduções e impedimentos](../results/round38/deductions.json),
[inspeção das chaves e transferência](../results/round38/inspection.json) e
[replay em cópia pública](../results/round38_clean_replay.json).

**Verificação concluída:** 341 testes passaram. A cópia pública repetiu os 70
casos aritméticos, as 3.976 chaves e os 597 controles, incluindo os mesmos
36 resultados limitados. Os 1007 arquivos do snapshot permaneceram intactos.
As auditorias do ciclo v3 e da publicação R37 também passaram. É reprodução
no mesmo ambiente, não revisão externa independente.

O próximo avanço exige evidência ou mecanismo que não dependa de escolher uma
palavra e reajustar as regras para acomodá-la. A imagem histórica de KNOWLEDGE
continua sem procedência recuperada; as matrizes de Hellgate e a associação de
3478 aos nomes da criatura não receberam evidência nova nesta rodada.
