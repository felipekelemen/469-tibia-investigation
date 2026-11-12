# Rodada15 — dimensões3×3,4×4,5×5; nomes,3478 e falas

Foram executadas **1.860 configurações distintas**, em duas representações dos
70 livros, com **150 controles positivos** e **468 buscas completas sobre
corpora de controle**. Nenhuma tradução verificável foi encontrada. Os líderes
3×3,4×4 e5×5 inspecionados não produziram inglês coerente nos textos reservados.
As predições externas de Kharos e dos NPCs também não trouxeram uma leitura
plausível. Isso limita uma família finita; não elimina matrizes em geral.

## O que realmente conhecemos da matriz

| Tabela | Determinante | Invertível mod25 | mod26 | mod29 |
|---|---:|:---:|:---:|:---:|
| Bloco3×3 relatado:111/136/114 | 6 | sim | não | sim |
| Antiga4×4 fornecida | −7 | sim | sim | sim |
| Posterior4×4 fornecida | −18 | sim | não | sim |
| Física5×5 | desconhecido | ? | ? | ? |

Uma matriz pode ter dimensão3×3 e conter o valor6: a contagem de uma célula
não é uma coordenada. A não invertibilidade exclui uma chave de Hill reversível
naquele módulo, não toda transformação direta ou algoritmo com outras camadas.
Os valores completos das tabelas4×4 continuam sendo relatos, com as limitações
históricas documentadas na [rodada14](round14.md).

Não obtivemos25 contagens autenticadas para uma chave5×5. São16 células
desconhecidas se só o bloco3×3 estiver fixado, ou9 se aceitarmos uma tabela4×4.
Estender qualquer uma das duas tabelas4×4 com linha/coluna uniformes de zeros
ou de uns gera determinante zero, nas quatro posições de encaixe:16 casos.
Isso rejeita esses preenchimentos como chaves reversíveis, não a dimensão5.

Como contraponto matemático, diag(M,t),t=1 ou2, preserva a tabela4×4 e tem
determinante t·det(M). Os quatro exemplos são invertíveis mod29. Eles demonstram
que bordas não observadas mudam a chave; **não são contagens propostas para
Hellgate** e não foram ajustados para produzir inglês.

Uma leitura literal de3478 como coordenadas de quadrados3×3,4×4 ou5×5 falha
nas bases0 e1:7 e8 ficam fora do intervalo. Isso não exclui índices lineares,
valores de células ou uma etapa intermediária.

## Experimento com nomes como senhas de Hill

O [protocolo](../data/round15_protocol.json), implementação, entradas e
[catálogo](../data/round15_candidate_catalog.json) foram congelados por hashes
antes da pontuação dos livros. A regra de senha é explícita, mas conjectural:
repetir BEHOLDER ou BONELORD até preencher n² posições por linhas, com ordinais
de base0 ou1. Testaram-se também transposta, operação direta/inversa,
alfabeto normal ou chaveado por cada nome, e cinco opções para3478:
nenhuma, soma/subtração periódica antes ou depois da matriz. A fase reinicia
em cada livro, sem procurar offsets ou outras sementes.

Repetir um nome de oito letras numa matriz4×4 produz duas linhas repetidas
e determinante zero, para os dois nomes e todos os alfabetos/bases testados.
Essa construção não fornece chave reversível4×4. Algumas construções3×3 e5×5
são invertíveis mod25/29; nenhuma senha3×3/5×5 desta regra é invertível mod26.
Mod25 funde I/J; mod29 acrescenta espaço,ponto e interrogação. Isso é uma escolha
de representação do experimento, não uma propriedade descoberta da linguagem.

| Dimensão | Configurações novas | Origem |
|---|---:|---|
| 3×3 | 960 | bloco relatado e senhas; mod25/29 |
| 4×4 | 480 | tabelas antiga/posterior; mod25 |
| 5×5 | 420 | somente senhas conjecturadas; mod25/29 |

As tabelas4×4 mod26/29 já tinham sido examinadas em rodadas anteriores.
Não repetimos essa busca como evidência nova. O catálogo mantém aliases das
configurações numericamente equivalentes. Os nomes são entradas da hipótese;
um candidato usar BONELORD não demonstra que a palavra seja a chave real.

## Qualificação, dados e controles

A busca recuperou **150/150 textos reservados exatamente**, em cinco células
de dimensão/módulo,30 casos por célula. Cada caso escolhe a configuração no
trecho de treino de300 caracteres e prediz outros180 sem novo ajuste. O módulo
é conhecido nesses controles; os dois livros ingleses já eram referências
expostas do projeto. É uma qualificação operacional dentro da família.

No jogo, as duas entradas são pares fixos de dígitos desde a posição0 e os
códigos importados da pesquisa anterior. Estes últimos continuam condicionais
a um parser não demonstrado. O controle positivo conserva zeros e não valida
omissões, segmentação variável ou outra serialização real. Caudas incompletas
e dígitos ímpares ficam explicitamente sem interpretação, sem padding/reparo.

O treino usa os68 livros do split existente; IDs20 e54 não escolhem a chave.
Esses dois livros já foram expostos e compartilham trechos curtos com o treino:
**não são validação semântica cega ou independente**. Alice fornece o modelo
fixo de tetragramas. Escores de módulos diferentes não são comparados entre si.

Para cada uma das quatro ramificações,39 réplicas de cada nulo refazem a busca
completa. Os p abaixo são do máximo de treino, corrigidos pela busca de chaves
dentro da ramificação, sem transformar correlação em evidência de significado.

| Entrada/módulo | Valores embaralhados | Blocos60 | Rótulos dos dígitos |
|---|---:|---:|---:|
| Pares raw/25 | .025 | .200 | .025 |
| Pares raw/29 | .100 | .400 | .725 |
| Códigos importados/25 | .025 | .075 | .100 |
| Códigos importados/29 | .025 | .725 | .900 |

O controle de rótulos aplica uma bijeção global0–9 aos códigos de dois dígitos,
preservando igualdade e repetições nessa representação. O controle de blocos
permuta blocos de60 valores, **incluindo a eventual cauda curta**; preserva
histogramas e motivos internos, mas não toda fase/alinhamento. Nenhum desses
nulos remove a dependência entre livros. Com39 réplicas, .025 é o piso de
resolução. A correção adicional pelas quatro ramificações dá p mínimo .10.
Não há destaque consistente contra os controles estruturados nem inglês
coerente que justifique ampliar livremente os parâmetros.

Como exemplo literal da liderança5×5 sobre códigos importados/mod29, o ID20
resulta em `?PEWWDE.AREQOCWDWP.ARQN KZ BLX`. A liderança global raw/mod25,
4×4 antiga, produz `PZTVNHKWBFRLBDBQOPQXHWFTATUT`. Não fizemos anagramas,
remoção de letras ou correções guiadas pela lore para transformar essas saídas.
As280 saídas dos líderes globais e as700 dos líderes por dimensão estão
preservadas nos resultados. A separação por dimensão é um diagnóstico
descritivo posterior, sem novos parâmetros nem p específicos.

## Hipótese distinta:3478 representa quatro dígrafos

Condicionalmente a3478→BEHOLDER, obtemos3=BE,4=HO,7=LD,8=ER. Para BONELORD,
3=BO,4=NE,7=LO,8=RD. Isso **ajusta o próprio exemplo**, sem evidência de tradução.
Só35,49% dos dígitos dos livros ficam cobertos; os outros mapeamentos permanecem
`??`, sem preenchimentos escolhidos para formar palavras.

Predições independentes do exemplo ajustado:

| Texto numérico | Hipótese BEHOLDER | Hipótese BONELORD |
|---|---|---|
| 4378, no poema | HOBELDER | NEBOLORD |
| 486486, nome do NPC | HOER??HOER?? | NERD??NERD?? |
| 34334, outra amostra | BEHOBEBEHO | BONEBOBONE |

O fragmento `NERD` é consequência automática da suposição4=NE e8=RD, não uma
tradução descoberta ou uma referência confirmada ao NPC. Repetições de3478
também não são validação. Não apareceu um novo par com significado atestado.
A referência isolada1 a Tibia sugere a possibilidade de códigos de entidades,
mas não dá licença para substituir cada dígito1 pela palavra TIBIA.

Uma ligação muito simples com as caveiras foi falsificada: ler cada dígito de
3478 como índice linear1-based por linhas, e emitir um dígrafo dependente
**somente da contagem da célula**. Os quatro dígrafos dos nomes são distintos,
mas as células selecionadas têm no máximo três contagens distintas em todas
as oito simetrias de cada tabela3×3/4×4:0/24 casos compatíveis. Leitura dependente
da posição, outra indexação ou uma chave física5×5 ainda são outras hipóteses.

## Falas e próximos passos

As chaves globais raw foram aplicadas sem ajuste a Kharos, falas, poema e nome
do NPC. Foram preservados tanto o enquadramento da fala inteira quanto a
reinicialização por palavra numérica. Palavras curtas frequentemente não
completam um bloco: a saída vazia é marcada com os resíduos, não traduzida como
silêncio. Não há parser importado definido para essas fontes externas.

A fórmula dependente do observador, os nomes e3478 continuam pistas de lore,
não especificações do algoritmo. A coincidência histórica entre matriz e
renomeação continua sem demonstração, conforme rodada14.

Prioridade seguinte: testar uma especificação finita que trate códigos como
sílabas/palavras/entidades e compare a estrutura das falas com a dos livros,
preservando incerteza de segmentação e controles de cópia. Não expandir bordas,
sementes e matrizes arbitrárias sem nova evidência. Para a matriz física,
permanece necessário obter contagens verificáveis e versão/data de captura.
P01,P03,P05 eP06 ainda têm entregas abertas; esta rodada não fecha a missão.

## Reproduzir

`make round15` revalida hashes, regenera os150 controles, refaz as buscas
observadas, redecodifica literais e confere os468 vencedores dos nulos e seus
p. `make round15-full` também repete a busca integral de cada nulo.
`python scripts/dimension_name_experiments.py --run` regenera os resultados
principais a partir do protocolo congelado; a duração é metadado variável.
`python scripts/round15_dimension_leaders.py` regenera o diagnóstico por dimensão.
Não usar `--freeze` para trocar silenciosamente o protocolo já publicado.

Artefatos principais: [álgebra/dígrafos](../results/round15_dimension_analysis.json),
[busca e literais](../results/round15_matrix_search.json),
[líderes por dimensão](../results/round15_dimension_leaders.json),
[qualificação](../results/round15_qualification.json),
[fontes e limites](../data/round15_source_notes.json).
