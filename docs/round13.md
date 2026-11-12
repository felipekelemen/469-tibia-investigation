# Décima terceira rodada: transposição colunar exata entre textos anagramas

**Nenhuma tradução foi encontrada.** Uma transposição colunar pura, com
qualquer ordem de 2–32 colunas, linhas incompletas sem preenchimento e
reversões globais, não transforma o livro ID22 em Kharos. A rejeição é exata
para essa relação entre dois textos. Não pressupõe que um deles seja texto
claro e não exclui transposição como componente de uma cifra desconhecida.

## Por que testar essa relação

Os dois livros têm 137 dígitos e o mesmo histograma, mas a rodada anterior
excluiu a conservação dos códigos importados de ID22. A nova hipótese opera
diretamente nos dígitos, sem tokens fornecidos, omissões aprendidas, letras
arbitrárias ou escore de inglês.

Nenhuma fonte examinada fornece uma regra colunar atestada para esse par.
Testamos uma família clássica solicitada no plano, não uma intenção atribuída
à CipSoft. Os dados e a igualdade de histogramas já eram públicos/expostos;
o protocolo precedeu os novos resultados, sem torná-los confirmação cega.

A busca da primeira rodada testava ordens colunares naturais, larguras 2–16,
com representações projetadas módulo 26 e pontuação linguística. Aqui o
objetivo é igualdade raw completa e a ordem das colunas é uma permutação
arbitrária. São perguntas diferentes, e o novo teste não melhora ou substitui
uma tradução inexistente.

## Família congelada e inferência exata de chaves

Em `data/columnar_pair_protocol.json` fixamos:

- larguras de 2 a 32, com todas as permutações dos índices de colunas;
- escrita da entrada em linhas de largura fixa, sem padding;
- leitura de cada coluna de cima para baixo, em ordem dada pela chave;
- última linha incompleta, com comprimentos determinados pelo tamanho da entrada;
- operações direta e inversa e reversão global opcional da entrada/saída.

São 248 parametrizações de largura/operação/reversões; algumas podem
representar transformações equivalentes. Não são apenas 248 chaves:
cada largura permite qualquer ordem das colunas. Não adicionamos reversões
por coluna, permutações de linhas, correções locais ou exceções após a busca.

Para uma largura, cada coluna é uma string conhecida. O algoritmo testa se a
saída é uma concatenação de todas essas strings, cada uma usada uma vez.
Programação dinâmica conta as ordens de classes de colunas idênticas. A
contagem de chaves físicas multiplica o número de ordens por fatoriais das
multiplicidades das classes. Isso impede declarar uma chave única apenas
porque duas colunas são iguais no texto de ajuste.

O limite é de 100 mil estados e 256 chaves explicitamente enumeradas. Um
limite de estados retorna inconclusivo; nunca incompatível. Uma contagem
maior que 256 mantém a contagem exata, mas marca a lista de chaves incompleta.
Cada chave retida precisa reproduzir exatamente a saída. Nenhum inglês é
usado para desempatar ou escolher uma chave.

## Qualificação com segundo texto não usado no ajuste

Para cada largura foram gerados 30 pares sintéticos: entrada decimal IID de
137 dígitos e saída cifrada com uma chave aleatória. Depois geramos outra
entrada de 173 dígitos, cifrada com a mesma chave. O inferidor recebe apenas
o primeiro par e a largura verdadeira; não vê a segunda saída para escolher
chave. Portanto, esta é uma qualificação de recuperação de chave com **par
conhecido**, não uma decifração sem texto claro ou um teste de coerência inglesa.

O gate exige viabilidade completa nos 30 pares por largura e chave única
verdadeira com predição e decodificação exatas do segundo texto em pelo
menos 27/30. Todas as larguras passam:

|Larguras|Pares por largura|Chave única e segundo texto exato|
|---|---:|---:|
|2–29|30|30/30 em cada largura|
|30|30|29/30|
|31|30|29/30|
|32|30|29/30|

Todos os 930 pares são viáveis. Nos três casos restantes há duas chaves
compatíveis com o primeiro par e previsões diferentes no segundo. Não
escolhemos a chave verdadeira consultando a segunda saída. São falhas de
identificação naquela amostra, não falhas de otimização nem textos sem sentido.

Também geramos 30 controles com colunas repetidas, largura 16, para verificar
o tratamento da ambiguidade. Cada um tem 1.828.915.200 chaves físicas
compatíveis. As 256 chaves retidas em cada caso produzem 256 saídas distintas
na segunda entrada. O programa preserva essa ambiguidade. Um teste unitário
adicional usa uma entrada toda zero: a contagem correta é exatamente `16!`,
embora todas as chaves reproduzam a mesma entrada de ajuste.

Esses controles medem capacidade mecânica sob a geração especificada. Não
fornecem equivalência numérico/inglês para 469. A largura é fornecida na
qualificação; nos textos reais todas as larguras e orientações são testadas.

## Resultado no par ID22/Kharos

Nenhuma das 248 parametrizações admite chave. Não houve limite atingido.
Em todas, a rejeição acontece no primeiro estado: nenhuma coluna completa
pode iniciar a string de saída exigida. Trocar a ordem das demais colunas
não pode resolver essa contradição.

Após abrir esse resultado, fizemos uma verificação independente da condição
necessária. Outro script constrói a grade linha por linha, sem importar o
inferidor ou o cifrador. Para cada coluna, registra o primeiro dígito que
diverge do prefixo exigido. Foram produzidos 248 certificados, com 4.216
testemunhas de divergência. Esse é um diagnóstico determinístico posterior,
sem novo ajuste, estatística de significância ou alegação confirmatória.
Testes em pares válidos, incluindo operações/reversões, verificam que o
certificador não rejeita exemplos positivos.

Esse resultado explica somente por que a família especificada não relaciona
as duas strings. Os livros podem conter mensagens diferentes, sem que haja
uma transposição direta entre eles. Não são um par cifra/plaintext atestado.

## Alcance sobre matrizes e outros pares

A largura 16 admite qualquer permutação das colunas, incluindo as ordens que
poderiam ser construídas por ranquear os valores de uma matriz 4×4 de
caveiras. Nenhuma ordem dessa subclasse explica a relação ID22→Kharos sob
essa operação de transposição colunar integral.

Isso não testa datas, renomeação BEHOLDER/BONELORD, Hill ou outras operações
matriciais. Uma matriz pode participar de outra camada sem produzir essa
relação direta. Não inferimos inexistência de chave matricial a partir deste
resultado. As limitações históricas permanecem.

Os dez pares direcionais dos cinco grupos internos de histogramas iguais
também são incompatíveis com a família. Kharos foi ainda embaralhado em 99
permutas de dígitos e 99 de blocos de oito, preservando seu comprimento e
histograma; a busca completa foi repetida em cada controle e todos ficaram
incompatíveis. Logo, a incompatibilidade do alvo não é um sinal que o
distinga desses controles, nem evidência de presença/ausência de linguagem.

O protocolo previa aplicar qualquer chave que ajustasse o par primário,
sem alterações, aos cinco pares canônicos de IDs crescentes. Como não houve
chave primária, essa etapa não foi acionada. IDs não fornecem ordem histórica,
e os demais pares não seriam automaticamente validação semântica.

## Decisão e próxima prioridade

Registrar a rejeição dessa relação colunar sem aumentar a largura ou adicionar
padding/exceções para tentar ajustar o mesmo par. Não há chave identificada,
leitura inglesa candidata ou avanço em significado externamente confirmado.
Este é um resultado estrutural negativo, não uma solução parcial de um livro.

Na frente matricial, o próximo trabalho prioritário volta à evidência
histórica: localizar material verificável da sala e de suas pilhas, antes
de abrir mais famílias de chaves. Continuam prioritários um par externo com
significado atestado ou uma regra de serialização de origem independente.
Nenhuma das quatro entregas principais pendentes passou a concluída.

## Reprodução

```sh
make round13
make test
```

O verificador reproduz todos os positivos, controles de ambiguidade, buscas
nos embaralhamentos e pares reais, além dos certificados independentes.
Os testes incluem vetores conhecidos, comparação com enumeração exaustiva
das permutações em casos pequenos e proteção contra falsa unicidade/limites.
Resultados: `results/columnar_pair_experiment.json` e
`results/columnar_prefix_certificates.json`.
