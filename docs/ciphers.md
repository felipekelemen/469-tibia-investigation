# Primeira bateria criptanalítica: resultado negativo limitado

Nenhuma tradução verificável foi encontrada. Não há texto inglês externo pareado com estes livros. O resultado `NO_VERIFIED_TRANSLATION` descreve a bateria executada; não prova que toda cifra ou toda mensagem seja impossível.

## Protocolo reproduzível

Executar `python scripts/cipher_battery.py --nulls 19` após a auditoria. Dependência: NumPy (execução registrada: 2.3.5). Fonte inglesa independente: *Alice’s Adventures in Wonderland*, de Lewis Carroll, Project Gutenberg, conservada integralmente com licença em `data/english_reference`. SHA-256 e URL estão no resultado e em `SOURCE.json`. Removemos cabeçalhos/rodapés Gutenberg e tudo exceto A–Z. Os primeiros 80% treinam probabilidades de tetragramas com suavização aditiva 0,01; os últimos 20% são controle positivo, sem ajustar o modelo aos números de Tibia. Média de log10 de probabilidades: maior é melhor. Isso mede semelhança local com inglês literário, não tradução ou significado.

O grupo de descoberta contém 68 livros. Os livros 20 e 54, juntos um único componente de repetições, ficam reservados: 61 códigos/120 dígitos. Não têm trechos literais compartilhados de pelo menos 16 dígitos com descoberta. Compartilham conteúdo entre si; não constituem duas observações independentes. Repetições menores e transformadas continuam possíveis. O corpus já era público; trata-se de holdout computacional da seleção, não de um teste prospectivo totalmente cego. O protocolo fragmentário mais rigoroso da auditoria deixa somente 58 dígitos, insuficientes para evidência convincente.

## Implementações efetivamente executadas

A grade contém 1.092 candidatos sobre três representações: códigos de dois dígitos restaurados como inteiros; dígitos originais como inteiros; letras da camada intermediária como A=0…Z=25, com a máscara `*`=26 (reduzida a 0 nas operações módulo26). O valor lexical aparente das letras intermediárias não é presumido verdadeiro.

- Afins: `(a*x+b) mod26`, todos os 12 multiplicadores invertíveis e 26 deslocamentos, em cada representação. Isso inclui César/identidade e reversões alfabéticas.
- Vigenere: soma/subtração periódica das chaves `469`, `3478`, `BEHOLDER`, `BONELORD`, com dígitos como seus valores e letras como A=0. A fase recomeça em cada livro.
- Transposição colunar sem chave: larguras2–16, lendo colunas da esquerda à direita, linhas irregulares permitidas; direções direta/inversa.
- Rail fence: 2–8 trilhos, direções direta/inversa.
- Substituição homofônica exploratória separada: mapa arbitrário de100 códigos para26 letras; quatro reinícios de annealing,5.000 mutações por reinício, seleção somente em descoberta. Há muitos ótimos locais e essa busca curta não exclui a família. Nenhuma semântica foi atribuída a saídas.

São convenções finitas, não uma cobertura de todas as transposições, substituições ou cifras polialfabéticas. Não foram testadas todas as ordens de colunas nem buscas gerais de período Vigenere nesta rodada.

## Controles e seleção

Cada controle recebe a mesma grade inteira de1.092 candidatos; o melhor é escolhido em descoberta e apenas então pontuado no holdout. Para cada uma das três classes há19 réplicas com seed4693478: valores uniformes no alfabeto da representação; embaralhamento dos valores de cada livro (preserva frequências marginais); embaralhamento de blocos contíguos de oito valores (preserva ordem dentro dos blocos). As representações são controladas separadamente: não se trata de um modelo gerativo conjunto de dígitos/códigos/símbolos. Blocos de8 não preservam exatamente todos os bigramas. A resolução mínima de p é0,05; valores de p são descritivos desse escore, nunca probabilidade de tradução correta. A busca homofônica não recebe nulos com nova otimização: por isso não tem p nem afirmação estatística de sucesso.

## Resultados

| Medida | Escore médio |
|---|---:|
| Inglês reservado de Alice | -4,1437 |
| Mesmo inglês embaralhado | -6,4541 |
| Melhor candidato em descoberta | -6,3077 |
| Mesmo candidato no holdout | -6,3074 |
| Substituição homofônica em descoberta | -5,6169 |
| Mesmo mapa homofônico no holdout | -6,0291 |

O candidato de maior escore em descoberta foi a transposição colunar de largura15 da representação de símbolos. Os p empíricos de cauda superior no holdout foram0,25 contra uniforme,0,40 contra embaralhamento marginal e0,15 contra blocos. Não supera convincentemente os controles. As saídas completas estão em `results/cipher_battery.json`; nenhuma constitui inglês coerente. A diferença descoberta/holdout na substituição homofônica é compatível com sobreajuste; não oferece tradução validada.

A pontuação reconhece corretamente o controle positivo inglês e o distingue do seu embaralhamento por2,31 unidades log10 por tetragrama. Esse teste demonstra sensibilidade básica, não poder para todo texto, domínio ou algoritmo.

## Testes e próximo passo

`python -m unittest discover -s tests -p test_ciphers.py -v` valida o vetor Vigenere clássico ATTACKATDAWN/LEMON→LXFOPVEFRNHR, uma transposição colunar irregular com vetor conhecido, a sensibilidade do escore e a ausência de16-gramas compartilhados entre grupos. Os quatro testes passaram.

A prioridade antes de aumentar buscas é obter um par longo e externo número→inglês ou um fragmento histórico realmente novo. Para trabalho computacional adicional: nulos com preservação exata de bigramas; otimização homofônica com controles otimização-por-otimização; pontuadores independentes de domínio; e decodificação com critérios explícitos de palavras/frases e pares externos. Aumentar pontuação de ngramas sem validar a leitura não satisfaz o objetivo.
