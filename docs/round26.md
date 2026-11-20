# Rodada 26 — adjudicação das matrizes de Hellgate

Executada em 20/11/2026 sobre `f25c01f870830889a60e9a8dd438908a71125186`.
**Nenhuma tradução nova foi encontrada. A função criptográfica das caveiras
continua sem demonstração.** A expansão livre de matrizes fica suspensa até
uma contagem autenticada ou uma regra com previsão verificável. Isso não é
prova de que qualquer relação com 469 seja impossível.

Consolidamos as famílias anteriores e executamos um teste novo de consistência
entre duas chaves de Hill. A missão permanece inconclusiva; faltam as quatro
rodadas planejadas 27–30.

## História e contagens

Foram feitas sete consultas distintas, 14 GETs diretos e uma nova abertura do
player em Chromium. O [diário](../data/round26_discovery_log.json), os metadados
HTTP e a [extração](../results/round26_sources.json) distinguem consultas,
conteúdo recebido, datas e indisponibilidade. Corpos completos ficam locais.

| Fonte | Resultado | Alcance |
| --- | --- | --- |
| Históricos MediaWiki de 469/Hellgate | Primeiras versões retornadas: 20/02/2011 e 06/03/2011; conteúdo/SHA1 conferidos, sem menção às caveiras | Não fornecem estado de 2008–2010 |
| Hellgate Misterio02.jpg | Uma versão atribuída a 01/01/2014, mesmo SHA1 da rodada 14 | Upload, não data de sessão do jogo |
| CDX específico das páginas 58/59 do tópico antigo em 2010 | Nenhuma captura retornada | Apenas aquelas consultas; não ausência de todo arquivo possível |
| Relato de LOOK no TibiaBR | Post original de 08/05/2017; imagem não recuperada | Seis caveiras na pilha central, sem contagem completa |
| Gravação de Tetuni | Reprodução 403 e janela de verificação humana | Nenhum quadro da gravação examinado |
| Notícias oficiais 1437/3777 | GET 403; links/referências indexados | Sem novo corpo primário autenticado sobre a transição |

O [post6999332](https://forums.tibiabr.com/threads/511342-Linguagem-469-Isso-%C3%A9-um-padr%C3%A3o/page14#post6999332)
corrige o bloco central para `111/136/114`. Outro post o cita no dia seguinte;
não são duas observações independentes. A data de 2009 encontrada perto desse
texto é o cadastro do usuário que o cita, não a observação. O parser usa o
cabeçalho do post e tem teste específico contra essa confusão.

A imagem vinculada retornou 403 com indisponibilidade de endereço upstream
aprovado. Seu índice arquivístico exato também veio vazio. Não afirmamos que
a imagem nunca existiu nem que uma pilha oculta tenha cinco ou seis caveiras.

A [gravação](https://tibiacams.com/watch/e15cded1cdfb?t=0) segue sem reprodução.
Inspecionamos a captura: verificação humana e player sem quadros. Não houve
interação com a verificação. Cliente 7.80/data 2007 são atribuições do catálogo,
sem autenticar contagens ou passagem pela sala. [Registro](../results/round26_cam_probe.json).

Permanece a evidência da [rodada 14](round14.md): a tabela antiga aparece em
citação arquivada de 2008; relatos atualmente datados de 2009/abril de 2010 indicam
aparência posterior antes da renomeação de agosto. São indícios contrários à
coincidência simples, não uma transição do mapa autenticada. Não recuperamos
pares históricos dos mesmos livros antes/depois da mudança.

## Dimensões e catálogo anterior

| Objeto | Evidência | Consequência delimitada |
| --- | --- | --- |
| Bloco 3×3 `111/136/114` | Parte visível relatada; não estabelece dimensão da chave completa | Determinante 6; invertível mod 25/29, não mod 26 |
| Antiga 4×4 | Tabela fornecida e citação arquivada; não sessão do mapa autenticada | Determinante −7; invertível mod 25/26/29 |
| Posterior 4×4 fornecida | Disposição parcial apoiada; contagens ocultas incertas | Determinante −18; invertível mod 25/29, não mod 26 |
| Física 5×5 | Sem 25 contagens autenticadas | Não há chave física 5×5 disponível |

Uma contagem 6 cabe numa matriz 3×3; valor não é coordenada. Singularidade mod 26
impede Hill bijetivo no domínio inteiro, sem excluir subconjuntos ou outras
camadas. Bordas 5×5 e senhas da rodada 15 eram construções, não medições.

O [catálogo](../data/round26_prior_catalog.json) registra hashes e limites dos
ensaios anteriores, sem apresentá-los como execuções novas:

| Rodada | Família dentro do respectivo escopo | Estado |
| --- | --- | --- |
|1|144 convenções Hill mod 26|Nenhuma tradução validada|
|2|320 convenções Hill mod 29|Nenhuma tradução validada|
|2|53 funções aritméticas, lookup e formas bilineares|Falham como projeções univalentes dos 99 códigos para rótulos importados|
|3|192 leituras por ordenação de contagens|Sem tradução ou vantagem convincente nos controles estruturados|
|14|Simetrias/recortes e determinante com células incertas|Bloco parcial incompatível com a antiga; determinante não escolhe pilhas|
|15|1860 configurações distintas por dimensão/nomes, duas representações|150 controles exatos; nenhuma tradução real validada|

Não somamos essas contagens como experimentos independentes. Há sobreposição
de alvos, representações condicionais e limites de validação. Consistência de
rótulos importados não equivale a inglês.

## Teste novo de consistência entre chaves

[Protocolo](../data/round26_protocol.json) e
[manifesto](../data/round26_experiment_manifest.json) congelados antes dos resultados.
O modelo é estrito: mesmo plaintext P, alfabeto, enquadramento e módulo, sem IV,
camada extra, omissões ou compensação periódica. Para as matrizes antiga A e posterior B:

```text
C_antigo = A P
C_posterior = B P = B A^(-1) C_antigo
```

A é invertível mod 25/26/29. B não precisa ser invertível para prever sua saída.
Testamos vetores coluna e a convenção transposta de vetores linha.
Se o criptograma também permanecer igual, `(A−B)P=0`.

```text
B(x,y) = 1 1 1 1        A−B(x,y) = 2  0  5    0
         1 3 x 1                   0 −1  1−x  0
         1 1 4 1                   0  0 −1    0
         4 y 1 1                   0 6−y 0    0
```

Na convenção coluna, as equações forçam P3=0, P2=0 e 2P1=0; P4 é livre.
O núcleo tem `m·gcd(2,m)` vetores, independentemente de x,y.
Na convenção transposta:

```text
P1=s, 2s=0
P2=(6−y)t
P3=5s+(1−x)(6−y)t
P4=t
```

O tamanho é igual, mas a direção do núcleo pode depender das contagens incertas.
Não usamos essa liberdade para ajustar a matriz aos livros.

| Módulo | Vetores compatíveis com criptograma inalterado | Domínio |
| --- | ---: | ---: |
|25|25|390625|
|26|52|456976|
|29|29|707281|

São proporções de um domínio uniforme abstrato, não p-valores dos livros.
Na convenção coluna, mod 25/29, os criptogramas compatíveis têm quatro valores
iguais. Mod26 há outra classe decorrente de P1=13. A variante por linhas tem
outras relações, explicitadas no resultado.

Aplicamos o critério aos 70 livros atuais em duas representações: pares brutos
desde o início e códigos importados. Cada uma reinicia por livro, usa base 0,
redução modular e blocos completos de quatro valores. Caudas são registradas,
sem interpretação ou preenchimento.

- Pares brutos: 1378 blocos completos por condição.
- Códigos importados: 1403 blocos completos por condição.
- Nas 12 condições — três módulos×duas orientações×duas representações —
  **zero blocos** satisfazem a condição de permanecerem iguais sob essa troca.

O [resultado](../results/round26_matrix_consistency.json) inclui por livro a
primeira contradição, a sequência numérica prevista após a troca e as caudas.
Conferimos cada classificação pela imagem do núcleo e, independentemente,
pela aplicação do operador `B A^(-1)` ao criptograma.

**É incompatibilidade condicional, não refutação histórica de Hill em 469.**
Não sabemos se os livros permaneceram iguais, se seus plaintexts mudaram,
se as matrizes eram chaves ou se a representação adotada é correta. O teste
fornece uma previsão para versões históricas pareadas. Não deduz o significado
de 3478 nem a substituição de uma palavra inglesa por outra.

## Controles e verificação

Conferimos o núcleo por 48 enumerações completas, totalizando 37400 vetores nos
módulos 2–7, duas orientações e quatro pares de x,y. A derivação sustenta a
afirmação geral; a enumeração verifica a implementação.

Em 90 casos sintéticos com entrada inglesa conhecida, permutamos entradas das
matrizes preservando seus histogramas e dimensão. Exigimos A invertível, com
orçamento de 10000 tentativas por caso. As 90 previsões de criptograma após a
troca foram exatas; as 90 saídas alteradas em uma posição foram rejeitadas.
As matrizes canônicas passaram também nas 180 verificações de orientação.
O inglês é da referência já exposta Alice. Isso testa álgebra com chaves
fornecidas, não descoberta de chave, tradução de 469 ou qualificação em novos
autores. Não calculamos significância com esses controles de implementação.

**249 testes de software passaram**, incluindo seis novos: determinantes por
métodos diferentes, inversas, células incertas, solução extra mod 26, caudas e
distinção entre data do post e cadastro do autor. Replay numa cópia temporária
sem fontes HTTP reproduziu os resultados.

## Decisões e continuidade

As [decisões por hipótese](../data/round26_decisions.json) encerram o lote:

- História: data da mudança e contagens completas suspensas por falta de dados;
  não afirmar coincidência com a renomeação.
- Dimensão: distinguir bloco visível 3×3, tabelas relatadas 4×4 e extensão 5×5
  sem medições; não tratá-los como três chaves físicas igualmente confirmadas.
- Algoritmos anteriores: conservar negativos dentro de seus escopos e não
  repetir buscas amplas por pequenas variações sem pista independente.
- Novo teste: consequência exata de uma hipótese delimitada, aguardando dados
  históricos pareados para decidir sua aplicação real.

**Nenhuma candidata nova; tradução potencial não identificada.** Não houve
saída inglesa dos livros, Avar Tar, Chayenne ou Knightmare nesta rodada.
Matrizes não especificadas e camadas arbitrárias saem da fila ativa até uma
fonte nova, erro demonstrado ou previsão independente justificar reabertura.

A rodada 27 qualifica recuperação de chave e segmentação em casos identificáveis
e ambíguos. As rodadas 28–30 mantêm tradução verificável, comparação de geradores
e adjudicação independente como objetivos.

```sh
make round26
python3 -m unittest discover -s tests -v
```

Replay offline. Conferir capturas HTTP exige os corpos locais, não redistribuídos.
Manifestos e resultados anteriores foram preservados.
[Progresso atual](../data/plan_progress_round26.json).
