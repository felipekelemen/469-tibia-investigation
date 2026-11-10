# Geradores, fórmula e controles de ocorrências

`structural_experiments.py` enumera todos os parâmetros para duas famílias
concretas, sobre os códigos reconstruídos inteiros 0–99, com reset por livro:

- `x[t+1] = (a*x[t]+c) mod100`;
- `x[t+2] = (a*x[t+1]+b*x[t]+c) mod100`.

Nenhum parâmetro satisfaz os textos completos em nenhuma família. A enumeração
poda candidatos assim que uma transição contradiz a equação; isso é exato e
não depende de pontuação de inglês. Controles positivos gerados pelas duas
recorrências são recuperados nos testes. Essa rejeição não cobre geradores
com estado oculto, transformações de rótulos, combinações por blocos ou não lineares.

Na leitura literal da fórmula de Honeminas, o produto escalar dos vetores
(4,3,1,5,3) e (3,4,7,8,4) é **83**. As demais variáveis não vêm acompanhadas de
valores ou de procedimento para interpretar livros; a expressão sozinha não
especifica algoritmo de tradução.

Sete fragmentos escolhidos antes da contagem são confrontados com 999 controles
por tipo, semente4693478: embaralhamento de dígitos por livro, embaralhamento dos
códigos reconstruídos por livro e permutação de blocos de16 dígitos. O controle
de códigos usa a representação preenchida com zeros (11.458 dígitos), portanto
é somente sensibilidade, não comparação calibrada do mesmo comprimento.

`3478` aparece24 vezes, contra média0,604 no shuffle de dígitos,1,280 no de
códigos e19,102 no de blocos. Sua recorrência é estruturalmente real; a enorme
mudança de baseline ilustra a importância de preservar motivos. Não se obtém
significado lexical desses números. Os testes são exploratórios, duas caudas
sem correção de múltiplas comparações e com livros dependentes. Nem ausência
de códigos de NPC nem significância contra shuffle prova a existência ou
inexistência de um idioma comum.

# Auditoria da alegação de solução alemã

Reproduzimos `arturo/scripts/validate_solution.py` com semente469. Os cinco
testes originais passam (log integral em results). **Não endossamos a conclusão
do programa.** Dois testes são tautológicos: decodificam a mesma substring com
o mesmo mapa dos dois lados da comparação. Repetimos esses testes com100
mapas aleatórios: ambos passam100/100. Frequência e índice de coincidência
mostram estrutura e composição, sem identificar idioma. O teste de permutação
compara mapa ajustado a mapas não ajustados, nos mesmos livros usados para
investigação; não calibra a seleção histórica de mapas e reparos.

O teste adicional `audit_claimed_translation.py` aplica v7 literalmente à
**tokenização de kimlage**, sem anagramas, deleções de letras ou inserções
narrativas. É um teste de transferência entre representações, não reprodução
da pontuação94,6% do pipeline CADST de Arturo. Há51 posições sem código no mapa;
sete das oito expressões destacadas no README não aparecem exatamente, e
`DEN EN DE REDER KOENIG` aparece4 vezes. Esse resultado não basta para refutar
qualquer versão possível do método; mostra que uma transformação determinística
completa e generalizável ainda precisa ser especificada e validada.
