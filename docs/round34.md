# Rodada 34 — E1 do plano de conclusão

26/11/2026. Base: `fcc6bcce77a26cc36b584db3b148563a1808d9f8`.
**E1 foi executada: nenhuma tradução candidata, par numérico–inglês atestado
ou processo original de geração foi encontrado nesta busca delimitada.**
O resultado continua I. O [plano v3](mission_plan_v3.md) foi publicado antes
desta execução; não reclassificamos os testes anteriores como tradução.

## Escopo e execução

Congelamos protocolo e seis hashes antes das novas consultas. A busca teve
duas passagens, voltadas às lacunas dos três alvos, à atribuição de dicionário,
à origem dos números, às fontes históricas das matrizes e a mudanças upstream.

| Operação | Executado |
| --- | ---: |
| Consultas distintas | 20 |
| Aberturas de página pelo leitor web | 11 |
| Localizações de trecho nas páginas | 4 |
| Leituras de branch pela API GitHub | 4 |
| GETs diretos de páginas públicas | 8 |

São **27 operações de leitura/captura**, cobradas conservadoramente no teto
de 60 mesmo quando repetem uma página ou falham. Não são 27 testemunhos
independentes. Dos GETs, seis retornaram 200 e dois 403. As duas respostas
Reddit com 200 continham apenas a página mínima, sem os posts; o contexto foi
obtido pelo leitor web e assim identificado. HTTP200 não comprova acesso ao texto.

Os três branches consultados continuam nos commits fixados nas R24/31.
A consulta ao antigo branch `master` de s2ward retornou redirecionamento para
`main`, seguido explicitamente. Não foi feita uma varredura de todos os branches,
issues ou discussões. As pesquisas indexadas reencontraram alegações já auditadas;
elas não foram promovidas a novas soluções nem reexecutadas sem mudança de insumo.

## O que mudou na evidência

**Dicionário.** O [post comunitário de 2026](https://www.reddit.com/r/TibiaMMO/comments/1rgakrg/solving_469_part_13/)
pôde ser lido com seu contexto. Ele atribui a interpretação a uma conversa com
outro participante, sem fornecer a declaração original, data ou entrevista de
Knightmare. A busca em português, alemão e polonês não recuperou esse original.
Um [tópico polonês de 2016](https://torg.pl/tibia/472386-tibia-quot-niszczymy-quot-mity-legendy-14.html)
também discute um possível dicionário, mas explicitamente como suposição.
A atribuição permanece não confirmada; isso não prova que a frase nunca existiu.

**Matriz antiga.** O [post3169247](https://torg.pl/tibia/308246-kompendium-tibijskich-mitow-sekretow.html#post3169247)
contém exatamente:

```text
3 1 6 1
1 2 1 1
1 1 3 1
4 6 1 1
```

A página atual atribui o post a Popek, exibe 25/01/2009 19:03 e edição em
26/01/2009 20:55; o fuso não foi estabelecido. É uma referência documental
adicional, posterior à referência de 2008 já registrada na R14. Não recuperamos
uma captura arquivada em 2009 deste post, nem a observação de pilhas no cliente.
O texto compila ideias existentes; não demonstramos uma medição independente.
Portanto, não há nova matriz, data autenticada de transição ou vínculo confirmado
com a renomeação. Os corpos de duas páginas históricas adicionais ficaram
inacessíveis; seus trechos indexados não foram tratados como contagens observadas.

**3478 e origem sem texto.** Um [tópico de dezembro de 2012](https://forum.portaltibia.com.br/topic/25048-desvendando-a-linguagem-dos-bonelords/)
relata o nome nostálgico e contém opiniões sobre inexistência de tradução.
Essas opiniões são de participantes. A história do funcionário bonelord é uma
repetição da entrevista de 2010 já recuperada na R32, não outra declaração
técnica independente. Mantemos 3478 como rótulo contextual documentado, sem
inferir sua grafia inglesa, ID interno ou função de chave.

**Avar Tar.** O [debate no TibiaQA](https://www.tibiaqa.com/25041/is-avar-tar-lying-about-his-stories)
e os [comentários sobre tibia.org](https://www.reddit.com/r/TibiaMMO/comments/qh0nvd/469_language/)
reconstituem a alegação de uma versão modificada do poema. O post original
do Reddit foi apagado; os comentários distinguem `63378129` da substituição
`62792068657272657261`. Esta última dá `by herrera` em ASCII hexadecimal.
Isso confirma uma operação sobre aquela sequência, não uma tradução do poema
autêntico nem a causa da alteração do site. O problema de procedência já era
conhecido; preservamos o alvo original e seu `4378`.

**Outras pistas.** Um [post polonês exibido como de julho de 2012](https://forum.tibia.pl/showthread.php?p=2834707)
sugere inspiração em Eye of the Beholder por relato indireto, sem operação
reproduzível ou fonte autoral. Uma [compilação recente](https://tibia.gg/en/articles/unsolved-mysteries)
afirma haver 75 livros numéricos, mas não entrega a derivação item a item dessa
contagem nem significados. Não reproduzimos esse inventário nesta rodada e não
substituímos o corpus auditado de 70 livros. Também não afirmamos que os 70
sejam todos os livros numéricos existentes no jogo.

## Alegações mecânicas e hipóteses

Verificamos duas operações curtas para delimitar o que as fontes realmente
permitem dizer. Além do hexadecimal acima, os sete totais de cadáveres
informados no Reddit, `[41,36,12,17,25,22,19]`, somados a32 e lidos em ASCII
produzem `ID,1963`. Não autenticamos essas contagens, a motivação do deslocamento,
a seleção de itens ou a intenção do autor do mapa. A operação não recebe um
livro ou uma das falas prioritárias como entrada. **Nenhuma das duas saídas
é candidata a tradução de 469.** Não lhes atribuímos significância estatística.

- **H125:** esta aquisição direcionada encontra evidência suficiente para
  validar um significado ou uma origem original sem texto. Não estabelecido
  no lote; não refutação de toda fonte possível.
- **H126:** a tabela adicional permite confirmar a mudança física ou sua
  coincidência com BEHOLDER→BONELORD. Não estabelecido. Confirmada apenas a
  presença literal da tabela antiga na página recuperada.

Não houve novas contagens de chaves, ajuste de cifras ou avaliação semântica
dos 153 milhões de resultados lexicais da R33. E1 não acionou os requisitos
de um mecanismo novo, de uma chave matricial nova ou de uma referência semântica.

## Decisão e próximo trabalho

E1 está concluída como busca delimitada. Não consumimos as consultas restantes
com repetições genéricas. Dicionário, significados de3478 e cronologia física
de Hellgate permanecem suspensos onde faltam dados; os negativos matemáticos
anteriores mantêm seus escopos.

E4 não foi acionada, por ausência de material original elegível. E5 continua
condicional a uma candidata e evidência independente. **O próximo trabalho é
E2:** congelar a qualificação de seleção gramatical e abstenção em inglês
conhecido, com ambiguidades e controles negativos, antes de selecionar frases
do jogo. E2, E3, E5 e E6 ainda precisam de decisão; E4 tem a suspensão explícita.

O estado científico permanece **I — inconclusivo**, sem tradução potencial
nova. Esgotar essa busca não demonstra inexistência de texto.

## Auditoria reproduzível

```bash
make round34
```

O comando confere os manifestos, orçamentos, alvos HTTP, pins upstream,
consistência dos registros e as duas operações condicionais. Julgamentos de
contexto e autenticidade não são certificados pelo programa. Os corpos e
respostas integrais ficam privados; links, resumos, hashes e limites são públicos.

A auditoria com os arquivos privados também passou: 22 hashes conferidos e
presença da tabela verificada no contêiner do post, sem usar a duplicata JSON-LD.
Uma cópia temporária com apenas os arquivos públicos necessários reproduziu
exatamente a auditoria padrão. Nenhum novo teste de cifra foi criado ou executado;
os 326 testes relatados na R33 não são apresentados como uma nova execução aqui.

[Protocolo](../data/round34_protocol.json),
[diário](../data/round34_discovery_log.json),
[fontes e classificações](../data/round34_sources.json),
[observações](../data/round34_observations.json),
[auditoria](../results/round34_source_audit.json) e
[progresso](../data/plan_progress_round34.json).
