# Relatório — linguagem469 do Tibia

Data da execução:10/11/2026. **Nenhum algoritmo de tradução para inglês foi validado.**
Esta é uma primeira rodada executada, com corpus, fontes, código, controles,
resultados negativos e testes. Não é demonstração de que uma mensagem seja
impossível. Traduções verificadas: **0**.

## Resultados demonstrados e alcance

| Questão | Resultado verificável | Limite |
|---|---|---|
| Corpus comunitário |70 livros únicos;11.263 dígitos; cópias dos três repositórios idênticas|Proveniência compartilhada; sem captura independente do jogo nesta rodada|
| Camada intermediária |5.729 códigos/símbolos;195 zeros;99 códigos→14 rótulos;roundtrip70/70|Tokenização e mapa importados; nove alinhamentos ambíguos; significado não demonstrado|
| Vazamento |20 livros contidos em outros; compartilhamentos≥12 dígitos conectam todos70|Split livre desses compartilhamentos inviável no nível de livros|
| Holdout computacional |68 livros de descoberta+2 reservados sem trechos≥16 em comum|Apenas61 códigos; os dois reservados são correlacionados; menores repetições permanecem|
| Matriz antiga |determinante−7; inversível em10,26,27,29,256|Condição necessária, não evidência de uso|
| Matriz posterior |determinante−18; singular em10,26,27,256; inversível em29|Exclui Hill reversível no domínio completo desses módulos, não outras funções|
| Cribs dos nomes |BEHOLDER/antiga e BONELORD/posterior não geram mesmo criptograma nas convenções testadas|Relações históricas ou camadas extras continuam abertas|
| Geradores simples |Nenhum LCG nem recorrência afim de ordem2 mod100 satisfaz os códigos|Rejeição só das equações e representação especificadas|
| Honeminas |Produto escalar literal=83|Fórmula não fornece procedimento completo de decodificação|

Fontes, definições e saídas completas estão em [corpus](corpus.md),
[matrizes](matrix.md), [cifras](ciphers.md) e [estrutura](structural.md).

## Testes criptográficos e controles

A busca matricial examinou144 variantes Hill mod26 com matrizes, orientações,
sentidos, agrupamentos, bases e offsets explícitos. O escore de trigramas
favoreceu levemente o corpus contra shuffle de dígitos(p=0,025), mas essa vantagem
não se sustentou contra permutação global dos rótulos preservando todas as
repetições(p=0,275) nem shuffle de blocos16(p=0,375). Cada controle teve39
réplicas e repetiu a escolha do máximo sobre toda a família. A saída de maior
escore não é inglês coerente. Trata-se de triagem no corpus completo, sem
alegação de holdout semântico.

Outra bateria examinou1.092 transformações afins, Vigenere com chaves469,
3478,BEHOLDER,BONELORD, transposição colunar e rail fence. Um pontuador de
 tetragramas treinado em referência inglesa externa foi congelado antes da
seleção. Para cada um de três nulos foram executadas19 réplicas com a mesma
busca completa. O candidato selecionado em descoberta teve p=0,25 contra
uniforme,0,40 contra shuffle marginal e0,15 contra blocos8 no holdout. Não
produziu inglês coerente. A pontuação reconhece um controle positivo inglês,
mas isso não garante sensibilidade a todo gênero ou método.

Uma busca homofônica curta, quatro reinícios de5.000 mutações sobre mapa de
códigos para letras, melhorou o escore em descoberta mas caiu no holdout e
não produziu leitura coerente. Não houve nulo com reotimização dessa busca;
logo não atribuímos significância nem excluímos substituição homofônica.
Transposições gerais, períodos arbitrários, matrizes de permutação completas,
algoritmos gerais de difusão e todas as segmentações letra/sílaba/palavra/conceito
não foram esgotados nesta rodada. As lacunas são explícitas.

## Alegações anteriores submetidas a auditoria

Arturo declara solução alemã; kimlage declara texto não linguístico. Nenhum
veredicto foi tomado como premissa. Reproduzimos o validator público de Arturo:
5/5 testes passam. Contudo, dois testes de consistência comparam a mesma
substring com o mesmo mapa; ambos passam100/100 mapas aleatórios. Não são
validação semântica. Frequência e IC não identificam idioma; um mapa ajustado
comparado a mapas aleatórios não ajustados nos mesmos dados não mede
capacidade de generalização.

Aplicar v7 literalmente à reconstrução de kimlage deixa51 posições não mapeadas
 e não reproduz literalmente sete de oito expressões destacadas. É um teste
de transferência, **não** reprodução do pipeline CADST nem refutação de toda
versão possível do método. Anagramas e reparos precisam de regras determinísticas
independentes para serem avaliados como algoritmo. A alegação ampla de que
não possa haver mensagem também não foi demonstrada por nossos testes finitos.

## História e pistas externas

A pesquisa consultou22 URLs, com catálogo de acessos, hashes e falhas HTTP.
A Tibia Wiki BR atribui Beholder→Bonelord ao patch8.61,de23/08/2010; é fonte
secundária. Confirma-se a matriz posterior na wiki, mas não foi obtida data
verificável da sua mudança. Uma afirmação posterior de simultaneidade remete
a uma passagem de s2ward que não fornece essa data: não a promovemos a fato.

`3478` é nome/identificador de criatura de nostalgia em fonte secundária e
ocorre24 vezes nos livros. A repetição é real, mas não constitui tradução
lexical. As médias dos controles mudam de0,604(dígitos) para19,102(blocos16),
mostrando quanto a estrutura compartilhada importa. Ausências de códigos
curtos de NPC também não provam separação absoluta de sistemas.

O poema de Avar Tar e falas de NPC são catalogados como amostras distintas,
sem pressupor cifra comum. O comentário inglês após o poema não é uma tradução
paralela. Uma equivalência número→palavra comunitária não recebe status de
CipSoft-confirmada. Veja [história e fontes](history.md).

## Próximos experimentos priorizados

1. **Ampliar evidência externa:** obter fragmentos históricos realmente inéditos e, idealmente, par longo cifra/plaintext atestado. Reservá-los antes de qualquer ajuste. Cotejar corpus com captura independente do jogo; as três cópias atuais não são independentes.
2. **Datar as caveiras:** comparar capturas verificáveis de clientes/mapas antes e depois de23/08/2010, registrando origem, versão, coordenadas e imagem; distinguir data de publicação e data da cena. A associação nominal só deve guiar chaves após esse teste.
3. **Matrizes em outros domínios:** testar mod29 com convenções de alfabeto e expansão fixadas, e matrizes como permutação/índice, contra controles que preservem os motivos. Não escolher convenções olhando o holdout.
4. **Homofonia e segmentação:** otimização com orçamentos iguais em dados e controles, nulos exatos de bigramas e homofones, hipótese de sílabas/palavras com penalidade de complexidade; pontuadores de inglês de domínio distinto e verificação por texto atestado.
5. **Camada dos homofones e difusão:** investigar informação residual na escolha dos códigos, posições de zeros e encadeamento entre módulos com modelos nulos de cópia; prever ocorrências externas. Ganho estatístico sem leitura permanece resultado estrutural.

O [registro de hipóteses](hypotheses.json) identifica o modelo exato rejeitado
e sua limitação, evitando a repetição de variantes já negativas. O
[protocolo](validation_protocol.md) define condições de promoção. Nenhum
resultado desta rodada satisfaz o critério principal do projeto.

## Entrega e publicação

Repositório local organizado, fontes fixadas, scripts, testes e resultados
executados. A conta GitHub felipekelemen foi reconhecida. A criação pública
foi tentada por GraphQL e REST e recusada por permissão da integração
(CreateRepository/HTTP403). Não há repositório remoto criado ou publicação
comprovada. A publicação depende de um repositório vazio acessível ou de
credencial com a permissão necessária, configurada fora do chat.
