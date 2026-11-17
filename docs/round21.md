# Rodada 21 — chave periódica e dependência do dígito anterior

**Nenhuma tradução inglesa verificável foi encontrada.** Avar Tar e Knightmare
não admitiram chave nas configurações examinadas. Em Chayenne, parte da busca
atingiu o limite predefinido e permanece inconclusiva. Os resultados são
condicionados ao vocabulário, aos códigos e às fronteiras descritos abaixo.

## Algoritmo testado

Convertemos letras em números decimais compactos, por três convenções:
A=0, A=1 e ASCII minúsculo. Uma chave periódica desconhecida, de comprimento
1–8, altera os dígitos. Opcionalmente, o dígito cifrado anterior também
participa da emissão:

```
c[i] = (d[i] + chave[i mod período] + feedback * c[i-1]) mod 10
```

`feedback` vale zero ou um; o estado anterior inicial é zero. Testamos reinício
da chave/estado por palavra e continuidade pela mensagem. Espaços e emoticons
não consomem posições. O mesmo mecanismo e a mesma chave devem explicar todos
os grupos usados no ajuste. Essa é uma dependência específica de posição e
estado, sem afirmar que represente a matemática da lore.

São **96 configurações nominais**: três codecs × oito períodos × dois modos de
reinício × duas opções de feedback. Chaves de período menor podem reaparecer
em modelos de período maior; pares modelo/chave não são evidências independentes.
A chave decimal `3478` está incluída na busca de período quatro. Não atribuímos
significado inglês a esse número ou usamos BEHOLDER/BONELORD como texto claro.

O vocabulário continua sendo o conjunto congelado de **7.713 palavras** de
Burnett/Wodehouse. Não acrescentamos palavras após consultar os resultados.
As outras quatro convenções da rodada 20 têm largura fixa de dois ou três
algarismos; os comprimentos de pelo menos um grupo de cada alvo impedem seu
uso sob as fronteiras testadas. A soma modular não altera esse comprimento.
Isso é uma restrição aritmética desses codecs, não uma exclusão de todas as
representações por letras.

## Validação do mecanismo

Geramos 108 fixtures novas, distribuídas entre os três codecs, períodos 2/4/8,
os dois reinícios e as duas opções de feedback. O solver recebe sete palavras
cifradas e procura entre **todos os 96 modelos**, sem receber o modelo gerador.
As sete palavras seguintes ficam reservadas, com a continuidade de fase e
estado corretamente preservada.

Todos os 108 ajustes e suas expansões de chaves terminaram; a chave verdadeira
foi mantida em todos. Das 756 palavras reservadas, 692 pertenciam ao vocabulário.
O consenso estrito recuperou **678/692 (97,98%)**, sem previsão única errada.
Uma previsão só é única quando todas as chaves sobreviventes concordam; uma
chave que não encontra palavra no dicionário bloqueia a afirmação de consenso.

Os textos vêm de Baum e Barrie, já usados no projeto. As janelas podem se
sobrepor; são duas fontes, não 108 autores ou observações semânticas
independentes. As palavras de ajuste foram condicionadas ao vocabulário,
enquanto as reservadas não foram filtradas. Esse benchmark qualifica uma
recuperação lexical restrita, não um detector universal de inglês.

Há ainda 12 fixtures de parsing sem espaços internos, uma por codec/reinício/
feedback com período quatro. Nelas, somente o modelo gerador é fornecido e o
objetivo é preservar a chave verdadeira. As 12 buscas terminaram e mantiveram
a chave verdadeira. Não confundimos esse teste mecânico
com a busca entre todos os modelos do benchmark anterior.

## Os três textos prioritários

| Ajuste real | Configurações completas | Configurações limitadas | Chaves encontradas |
| --- | ---: | ---: | ---: |
| Primeiros dez grupos de Avar Tar | 96 | 0 | 0 |
| Sete grupos de Knightmare | 96 | 0 | 0 |
| Vinte grupos de Avar Tar, diagnóstico | 96 | 0 | 0 |
| Duas partes de Chayenne, espaços internos ocultos | 84 | 12 | 0 |

Os 12 casos limitados são os codecs A=0/A=1, períodos 6/7/8, modo contínuo,
com e sem feedback. Os modelos com reinício por palavra terminaram.
O limite é de 20.000 estados e 2.000 chaves parciais por modelo. Não encontrar
chave nos 12 casos limitados de Chayenne **não os refuta**. As buscas completas
excluem somente o encaixe exato no léxico e no mecanismo especificados.

O prefixo de Avar Tar deveria descobrir a chave para sua segunda metade. A
chave de Knightmare deveria ser aplicada ao poema, à entrevista de Chayenne e
à enquete numérica, sem reajuste. Como nenhuma chave foi encontrada, essas
transferências não produziram previsões e não constituem validações negativas
independentes. O ajuste do poema inteiro é diagnóstico, não teste reservado.

Chayenne foi examinada diretamente, inferindo espaços internos. O reinício por
palavra, quando escolhido, ocorre nos cortes inferidos; o modo contínuo mantém
fase e dígito anterior entre as duas partes. A fronteira indicada pelos emoticons
é assumida como separação de palavras. Os fragmentos continuam reutilizados
nos livros e não representam conteúdo semanticamente independente deles.

## Controles e limites

Foram executados 114 conjuntos negativos, cada um pesquisado nos 96
modelos. Para Avar Tar e Knightmare, há 19 embaralhamentos globais com reposição
dos comprimentos e 19 embaralhamentos de cada grupo distinto, preservando suas
repetições. Para Chayenne, há 19 embaralhamentos dentro das partes e 19 pares
retirados dos livros de descoberta, com os comprimentos 36 e 13.

Os 76 controles de Avar Tar/Knightmare terminaram em todos os modelos, sem
chaves. Nos 38 controles de Chayenne não foi encontrada chave, mas cada um
também tem 12 buscas limitadas: 456 buscas inconclusivas ao todo. Portanto a
ausência de chaves nesses controles não é uma prova de rejeição completa.
As contagens finais ficam em `data/round21_summary.json`. Qualquer busca limitada permanece
inconclusiva; não calculamos significância a partir dela ou de conjuntos vazios.
Encontrar palavras isoladas em um controle também não demonstra gramática.

Nenhuma transcrição nova ou par número/inglês autenticado entrou nesta rodada.
Usamos o inventário canônico e as fontes já atribuídas. O texto fora do
vocabulário — incluindo nomes próprios do jogo — continua sendo uma limitação
importante. Os resultados não excluem sílabas, palavras, morfemas, outros
estados, outras línguas ou outros modos de serializar números.

## Reprodução

```
make test
make round21
```

Os **213 testes automatizados** passaram. A implementação de referência e
seu manifesto permanecem preservados.
Uma implementação equivalente da segmentação evita decifrar o mesmo prefixo
numérico para cada aresta da programação dinâmica; outra filtra em lote, com
NumPy, as atribuições de chave incompatíveis. A ordem dos candidatos permanece
igual à referência. Os testes comparam contagens,
saídas e ambiguidades entre as duas versões em todas as 96 configurações,
incluindo dados perturbados e continuação de estado. As hipóteses, a ordem de
busca e os limites são os mesmos. O replay usa essa versão mais rápida.

O protocolo foi registrado localmente antes dos resultados; não houve registro
público prospectivo. Os dois lotes iniciais de referência/otimização parcial
foram interrompidos antes de produzir o JSON final;
o log registra o ponto efetivo. O manifesto da otimização contém uma correção
explícita de sua descrição inicial desse ponto. O lote otimizado recomeça todo
o experimento; suas contagens não são somadas às tentativas anteriores.

A auditoria também separa chaves parciais de suas completações: com cortes de
palavras desconhecidos, duas chaves parciais podem representar conjuntos que
se sobrepõem. O resumo calcula a união exata dentro de cada modelo real, em
vez de somar essas contagens brutas. Os controles usam existência de alguma
chave, que não depende dessa multiplicidade.

A pendência computacional é concluir os 12 modelos contínuos de Chayenne já
registrados, com melhor poda ou processamento, mantendo o tratamento dos
controles. Isso não exige ampliar a família de chaves. Em paralelo, o próximo
caminho de modelagem é examinar códigos de unidades maiores com um
vocabulário externo de pronúncias/morfemas definido antes dos alvos, incluindo
controle de termos ausentes. A escolha de unidades deverá passar por nova
qualificação; o aprendiz da rodada 17 não será tratado como validado. Não há
justificativa nesta rodada para ampliar períodos indefinidamente até aparecer
uma frase. P01/P03/P05/P06 permanecem abertos.
