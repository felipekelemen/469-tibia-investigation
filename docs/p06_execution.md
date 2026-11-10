# P06 executado: datação histórica das caveiras

**Resultado parcial novo:** encontramos uma transcrição completa da matriz
antiga num post que exibe a data **26/12/2007**, anterior à renomeação. Não
obtivemos captura autenticada que fixe as quantidades da sala nas três janelas
históricas, e a data de alteração da matriz **permanece desconhecida**.

## Método e cobertura

Foram executadas 25 consultas delimitadas: nove buscas, 12 aberturas, dois
finds e duas requisições HTTP diretas. O registro contém queries, URLs,
resultados negativos e distinção entre data de captura, publicação e versão.
A cópia HTML recuperada é mantida temporariamente fora do repositório; seu
SHA-256, tamanho, URL e status constam dos metadados. Não baixamos arquivos
proprietários de servidor nem repetimos os endpoints oficiais já bloqueados
sem uma nova rota de acesso.

## Evidência nova da matriz antiga

O [tópico469 do TibiaBR, versão de impressão](https://forums.tibiabr.com/printthread.php?t=203250&pp=40)
foi obtido por HTTP200. No post número7, Jacky pumpkin, data exibida
26/12/2007 às11:21, aparecem exatamente as16 células:

```text
3 1 6 1
1 2 1 1
1 1 3 1
4 6 1 1
```

É uma atestação textual comunitária mais antiga que as reconstruções recentes.
O autor relata outro fórum e não fornece captura da sala. Respostas posteriores
repetem sua mensagem por citação; não são observações independentes. Como
obtivemos o HTML atual, e não snapshot imutável de2007, não podemos excluir
edições posteriores com base apenas no timestamp mostrado. A evidência
fortalece a existência histórica dessa descrição, mas não autentica os objetos
originais ou uma mudança em2010.

## Evidência posterior e oportunidade de inspeção visual

O [artigo de Antonio Stradivarius no TibiaSecrets](https://tibiasecrets.com/article160),
publicado em06/05/2024, lista a matriz posterior exatamente como fornecida:
`1111/1361/1141/4611`. A data do artigo não é a data de captura da ilustração,
e o trecho inspecionado não fornece uma transição de2010. Suas interpretações
com anagramas e reparos não foram aceitas como plaintext.

Encontramos também o catálogo de uma [gravação de Tetuni emHellgate](https://tibiacams.com/watch/e15cded1cdfb?t=0),
registrada pelo site como10/01/2007, cliente7.80, duração9:54. O texto acessível
mostra metadados de uma `.rec` de165KB. O player não foi inspecionado: não há
confirmação de que a câmera passe pela matriz. A gravação é um lead concreto,
não uma imagem validada das quantidades.

## Janelas e falhas registradas

| Janela | Evidência obtida | O que falta |
|---|---|---|
| Antes de23/08/2010 | Transcrição exibida num post de2007; catálogo de gravação7.80 | Captura/registro de objetos da sala autenticável |
|23/08–08/12/2010 | Nenhuma captura da sala encontrada nas consultas feitas | Evidência que discrimine edição junto ao rename ou depois |
| Depois de08/12/2010 | Transcrição posterior em artigo de2024 | Captura imediatamente após a atualização, com versão e origem |

A wiki BR retornou403 numa abertura direta; uma revisão antiga indexada
menciona `Hellgate Misterio01.jpg`. A tentativa pela API MediaWiki para esse
nome retornou página ausente. Isso não demonstra que todas as imagens estejam
ausentes: pode haver renomeação, namespace ou histórico não recuperado. A
página de discussão Fandom teve acesso restrito. A página normal do fórum
TibiaBR foi parcialmente acessível e depois403; a versão de impressão recuperou
o texto completo. Todos esses resultados foram preservados como limitações
de cobertura, não como evidência negativa sobre os eventos históricos.

## Decisão do gate

P06 avançou da dependência exclusiva de reconstruções recentes para uma
atestação textual antiga verificável hoje. **Ainda não qualifica a tese de
mudança da matriz coordenada ao nome BEHOLDER/BONELORD.** Os107 dias entre
duas notícias gerais não são datação da matriz. O plano de P07 deve permanecer
condicionado a mecanismo específico e controles, sem usar a coincidência
histórica como fato estabelecido.

O próximo passo de maior valor é inspecionar a gravação candidata ou capturas
obtidas licitamente e localizar a sala pelas coordenadas, verificando pilhas,
caveiras atrás de pilares e objetos móveis. Uma captura com muitos pixels de
lava não permite inferir quantidades ocultas. A linha temporal de recodificação
dos livros também não foi estabelecida nesta rodada.

Metadados completos: `results/p06_history.json` e `data/history_round3/`.
Nenhum algoritmo de tradução foi produzido nesta linha de trabalho.
