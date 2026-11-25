# Rodada 31 — entrevistas, atribuições e aquisição de evidência

Pesquisa iniciada em 24/11/2026; publicação consolidada em 25/11/2026 (UTC).
Base: `3196a8d3507ea35f04efca09ebb7cdbe26659603`.

**Resultado: inconclusivo. Nenhuma tradução candidata nova.** Esta rodada
seguiu a prioridade de obter evidência semântica ou de autoria. Resolveu uma
lacuna de fontes, mas não encontrou um novo par de números e inglês nem um
processo original de geração. Não executou outra busca de cifras: a condição
de obter uma resposta numérica nova não ocorreu.

O lote das rodadas 24–30 continua concluído. Esta investigação adicional não
renumera aquele plano e não pressupõe outra sequência fixa de rodadas.

## Achados e seus limites

| Fonte | Resultado | Consequência para a missão |
| --- | --- | --- |
| Teyrata, entrevista de 2014 | A pergunta sobre a linguagem recebe uma resposta em inglês, sem números | Fecha a suspeita de uma resposta numérica omitida do inventário; não fornece tradução |
| Knightmare, entrevista TibiaEvents de 2014 | A tradução portuguesa publicada evita confirmar ou eliminar teorias | Não confirma algoritmo, aleatoriedade ou origem sem texto |
| Chayenne, entrevista de 2009 | Os dois grupos existentes, de 36 e 13 dígitos, foram reconferidos | Mesmos dados já testados; nenhuma equivalência inglesa nova |
| Três repositórios iniciais | Os últimos commits listados pela integração coincidem com os registrados na R24 | Nenhuma mudança de código identificada por essa consulta |

A [entrevista de Teyrata na wiki](https://www.tibiawiki.com.br/wiki/Tibia_Wiki:Interview_with_Teyrata)
e sua [republicação no Portal Tibia](https://portaltibia.com.br/pt/interview-with-teyrata/)
concordam na resposta relevante. A revisão recuperada **150650** mostra edição
em 20/04/2015; a republicação apresenta 06/05/2014. São datas de natureza
diferente. Não confundimos a revisão com uma captura do dia da entrevista.
O comentário sobre ausência de significado pertence à pergunta sobre o nome
da entrevistada, não à linguagem 469. Uma
[retomada posterior](https://www.tibialife.com.br/nostalgia-tibiana-hellgate/)
agrupa Teyrata com Chayenne ao discutir respostas numéricas; consultar o
intercâmbio original impede importar uma sequência que ele não contém.

Na [tradução da entrevista de Knightmare](https://portaltibia.com.br/pt/tibiaevents-entrevista-com-knightmare/),
a pergunta reúne várias alternativas: números aleatórios, possibilidade de
solução, relação com quest e pedido de dica. A resposta evita adjudicá-las.
Não extraímos uma confirmação de decifrabilidade da primeira frase isolada.
O texto é uma tradução autorizada pelo publicador da entrevista, segundo a
própria página; não o rotulamos como declaração publicada pela CipSoft.
O [aviso contemporâneo](https://forum.portaltibia.com.br/topic/29686-tibiaevents-entrevista-knightmare/)
leva ao domínio TibiaEvents, cujo início e índice atual não recuperaram a
entrevista inglesa. Esse original permanece pendente.

A [entrevista de Chayenne](https://forum.portaltibia.com.br/topic/11420-entrevista-com-chayenne/)
contém a resposta conhecida na seção inglesa. O HTML bruto repete cada grupo
nove vezes, incluindo representações duplicadas da página; isso não significa
nove mensagens. A relação com cópias nos livros já foi medida em rodadas
anteriores e não foi apresentada aqui como experimento novo.

## Busca e verificação executadas

O [protocolo](../data/round31_protocol.json) limitou a investigação. Foram
**24 consultas de busca**, dez aberturas, três cliques e três localizações
internas. Contando estes dois últimos como acesso a página, foram 16 operações
dentro do limite de 20. Uma chamada rejeitada por parâmetro inválido não gerou
acesso e foi excluída dos totais. A primeira busca está registrada sem captura
bruta preservada; não atribuímos a ela um hash inexistente.

Oito GETs adicionais capturaram sete respostas HTTP 200 e uma 403. O aviso
oficial da entrevista de Teyrata foi encontrado apenas no índice de busca;
o corpo oficial permaneceu inacessível. A wiki apresentou falha pela ferramenta
web, mas a obtenção HTTP direta posterior funcionou. Os dois estados estão
registrados, sem transformar a falha anterior em ausência de fonte.

O programa de extração conferiu as três representações de Teyrata, os limites
da pergunta/resposta de Knightmare e a presença dos grupos de Chayenne. Exige
delimitadores únicos e preserva os grupos de dígitos; não concatena datas,
scripts ou respostas vizinhas para produzir uma suposta mensagem. O conteúdo
lexical de Teyrata coincide nas três capturas, com diferença apenas na forma
do emoticon. **É uma entrevista reproduzida, não três observações independentes.**

Os julgamentos de contexto e procedência são humanos/analíticos explícitos.
Hashes e testes verificam a preservação e a consistência dos registros; não
autenticam intenção autoral nem demonstram significado. Os limites de extração
foram escolhidos após inspecionar as páginas. O manifesto de insumos é uma
fixação posterior à descoberta, não uma alegação de avaliação cega.

- [Registro das consultas](../data/round31_discovery_log.json)
- [Fontes e graus de acesso](../data/round31_sources.json)
- [Metadados HTTP](../data/round31_http.json)
- [Extração e hashes](../data/round31_capture_inspection.json)
- [Decisões e lacunas](../data/round31_source_decisions.json)
- [Resultado reproduzível](../results/round31_source_audit.json)

Os corpos completos ficam ignorados em `data/private/round31/`. Publicamos
metadados, hashes e trechos breves. Uma consulta futura pode encontrar páginas
alteradas; seu hash não precisa coincidir com o da captura atual. O replay
público confere registros preservados, não refaz uma pesquisa na internet.

## Hipóteses e próximo passo

**H118:** a entrevista de Teyrata teria uma mensagem numérica adicional.
O intercâmbio recuperado não contém essa mensagem. Essa hipótese de aquisição
foi encerrada para a fonte examinada, sem concluir nada sobre outros textos.

**H119:** a entrevista de Knightmare de 2014 permitiria decidir entre texto
cifrado e números sem texto. A resposta publicada não decide isso. Nenhuma
das duas origens foi confirmada.

Permanecem abertas as atribuições comunitárias sobre um dicionário e sobre
um tradutor com mais olhos. Não recuperamos as declarações originais nesta
busca limitada. Elas não autorizam impor um dicionário, quantidade de olhos
ou dimensão matricial ao decoder. A conclusão sobre **3478** e **Hellgate**
permanece a da R30; esta rodada não acrescenta medições históricas.

O próximo passo de aquisição com maior valor é recuperar os endereços e
versões históricas exatos das entrevistas TibiaEvents/BomDiaTibia, em vez de
repetir consultas genéricas. Um par semântico atestado ou material de autoria
ligado a uma mensagem concreta permitiria um teste discriminante. Outra cópia
de números sem significado atestado não basta. A busca limitada de Knightmare
na R23 permanece incompleta, com 1.769 chaves lexicais; só deve ser reaberta
com uma restrição nova ou um método que demonstre recuperação nos controles.

**T e G continuam não estabelecidos.** O resultado desta rodada não prova
que 469 seja indecifrável ou que seja decoração sem mensagem.

## Reprodução

```bash
make round31
python -m unittest discover -s tests -p 'test_round31_extract.py' -v
```

Na máquina que possui as capturas originais, a conferência adicional é:

```bash
python scripts/round31_inspect_captures.py
```

Para uma nova obtenção das oito URLs, com rede, use um nome de lote novo:

```bash
python scripts/round31_fetch_sources.py --batch nova_captura
```

O comando preserva os arquivos antigos e não substitui os resultados
publicados. A validação da árvore completa e seus logs constam em
[round31_verification.json](../results/round31_verification.json).

Passaram **308 testes**, incluindo sete novos testes dos limites de extração.
A auditoria R31 passou também em um diretório temporário com somente 18
arquivos públicos, sem capturas HTML ou clones. `make round30` reconferiu os
artefatos anteriores, sem repetir as buscas de cifras. O log preserva o aviso
não fatal já conhecido de fechamento tardio do CSV no auditor congelado da R30.
