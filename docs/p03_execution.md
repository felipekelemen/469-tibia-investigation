# P03 executado — comparação gerativa e predição de variantes

**Resultado: forte compressibilidade por motivos, mas compressão por cópia não
identifica ausência de mensagem. Nenhuma tradução foi encontrada.** O teste
positivo é decisivo para a interpretação: a mesma vantagem da montagem por
cópia aparece quando os módulos contêm inglês real cifrado.

## Modelos e critérios fixos

`python scripts/generative_comparison.py` compara três modelos de codificação
nos dígitos originais e na representação row0 importada:

1. **Uniforme:** literais de largura `ceil(log2 K)` e comprimentos de livros
   codificados com Elias gamma. O alfabeto é dado e seu custo é omitido em
   todos os modelos. Dois bits identificam a família de modelo.
2. **Markov de ordem1:** contagens de início e transição aprendidas nos68livros
   de descoberta, cada contagem serializada como gamma(contagem+1), suavização
   0,5 e probabilidades congeladas. O custo dos dados é o comprimento ideal
   de codificação aritmética mais dois bits por livro, não um arquivo binário
   de tamanho fracionário realmente produzido.
3. **Gramática estática de cópia:** motivos dos comprimentos4,8,12,16,24,32,
   selecionados somente em descoberta por cobertura incremental de posições
   sem sobreposição. Até128entradas; tamanho do dicionário escolhido por custo
   de descoberta entre0,1,2,4,8,16,32,64,128, pagando quatro bits pela escolha.
   Paga-se cada motivo literal e seu comprimento, o tamanho do dicionário,
   os comprimentos de livros e cada token de literal/referência. Um parsing
   por programação dinâmica encontra o menor custo de dados no dicionário
   fixo. O teste reservado não cria entradas, atualiza frequências nem escolhe
   o tamanho do dicionário.

O dicionário é serializado como texto literal. A frequência de janelas
sobrepostas é usada apenas para propor motivos; a cobertura desconta posições
já cobertas, e a compressão final é medida pelo parsing exato, impedindo contar
o mesmo intervalo várias vezes como economia real. A emissão de tokens tem
roundtrip verificado em todas as sequências. As regras não são um algoritmo
linguístico e o mapa row0 não recebe significado por presunção.

Uma versão de desenvolvimento que apenas escolhia os128motivos de maior
frequência desperdiçava o dicionário com deslocamentos da mesma frase e falhava
até nas montagens artificiais. A heurística de cobertura foi desenvolvida para
corrigir essa deficiência nos controles sintéticos. Esta comparação permanece
exploratória, não uma análise confirmatória preregistrada. Os controles finais
usam12sementes, mas não autores independentes e suas janelas podem sobrepor.

## Resultados nos dados do jogo

| Representação | Cópia: bits totais pagos | Markov1: bits totais pagos | Uniforme |
|---|---:|---:|---:|
|Dígitos originais|21.296|35.386,45|46.084|
|row0|14.650|19.157,63|23.824|

O dicionário final possui128entradas nos dígitos e120em row0. Esses resultados
são comprimentos de descrição para três modelos finitos específicos. Não
reproduzem toda competição MDL upstream nem cobrem todas as formas de linguagem
ou modelos gerativos. Não se deve comparar os bits de raw e row0 como se ambas
representações codificassem a mesma informação: row0 colapsa a identidade dos
homofones e depende de uma tabela importada globalmente.

Nos dois livros reservados, a gramática usa16referências curtas nos dígitos,
cobrindo63,33%das120posições, e6referências em row0, cobrindo39,34%dos61símbolos.
Nos dígitos o custo condicional é372bits contra395,14bits Markov; em row0 são
253bits contra209,31. Os fragmentos curtos continuam compartilhados, pois o
split exclui apenas coincidências raw de16ou mais dígitos. Logo essa previsão
parcial não demonstra generalização a motivos inteiramente novos. O benefício
total é majoritariamente aprendido no corpus repetitivo de descoberta. Não
usamos os livros reservados para melhorar ou reajustar o dicionário.

## Positivos e negativos: teste de poder

Usamos os últimos20%de *Alice's Adventures in Wonderland*, preservados na
referência externa do projeto. Uma substituição monoalfabética aleatória cria
ciphertexts com plaintext conhecido. Os comprimentos e a separação dos livros
são os mesmos da row0(5.729símbolos totais,5.668descoberta e61reservados).
São12réplicas sintéticas por cenário:

- **Prosa contínua cifrada:** segmentos sucessivos de inglês real.
- **Prosa cifrada copiada:**16módulos com fragmentos ingleses de24–96letras,
  montados repetidamente nos livros. Há significado nos fragmentos; a ordem
  aleatória não promete ensaios coerentes de livro inteiro.
- **Montagem sem plaintext fornecido:** mesma escolha de módulos, comprimentos
  e montagem do cenário anterior, mas as letras de cada módulo são embaralhadas
  uma vez antes de copiá-lo. Isso preserva as marginais dos módulos e sua
  reutilização. O rótulo descreve o gerador, não prova ausência de qualquer
  interpretação matemática possível.

| Cenário | Média(cópia−Markov),bits/símbolo | Réplicas em que cópia vence |
|---|---:|---:|
|Prosa contínua cifrada|+0,471|0/12|
|Prosa cifrada copiada|−1,902|12/12|
|Montagem de módulos embaralhados|−2,468|12/12|

Se alguém usasse a regra **“cópia vence Markov ⇒ dados não linguísticos”**,
classificaria corretamente12/12montagens negativas, mas também classificaria
incorretamente12/12positivos de prosa copiada: **100%de falsos positivos nesse
cenário**. Isso não refuta toda análise estatística upstream; refuta a suficiência
dessa regra para promover uma conclusão semântica. Não há novo teste capaz de
dizer que a língua469 não significa nada.

## Predição dos homofones fora do ajuste

Três preditores condicionados ao símbolo row0 foram ajustados nos68livros:
frequência marginal por símbolo; transição a partir do homofone anterior do
mesmo símbolo; e dois símbolos anteriores como contexto. As distribuições de
contexto são interpoladas com a marginal, com peso `n/(n+5)` e suavização0,5,
sem ajustar esses valores ao reservado. O código atual é o alvo, não a entrada
do preditor. Estados de ocorrência reiniciam em cada livro.

| Preditor | Acertos nos61códigos reservados | Bits/código |
|---|---:|---:|
|Marginal por símbolo|6/61(9,84%)|3,3482|
|Homofone anterior do mesmo símbolo|17/61(27,87%)|3,3471|
|Dois símbolos anteriores|21/61(34,43%)|2,6250|

O contexto fornece ganho mecânico no recorte, mas o conjunto já foi examinado
historicamente e seus61códigos pertencem a um componente correlacionado. A
lista de códigos permitidos por símbolo vem de todo o corpus público, como
condição do mapa importado; não alegamos inferência independente dessa lista.
Não atribuímos p confirmatório nem tradução a esses acertos.

O grafo de compartilhamento exato de8símbolos tem apenas dois componentes,
68e2livros. Calculamos também as duas direções leave-component-out; uma treina
em apenas2livros para prever os outros68, com acertos próximos de20%para todos
os modelos. Esse desequilíbrio limita a validade comparativa. Não há três
partições independentes nesse limiar, e dependências menores/transformadas
continuam possíveis. As9ambiguidades de alinhamento dos zeros não são resolvidas
por este experimento, que é condicional aos streams importados e não usa os
zeros como um canal preditivo.

## Testes, saídas e próximos passos

Seis testes passaram em `tests/test_generative_comparison.py`: custo calculado
à mão e roundtrip; dicionário congelado durante teste; ausência de motivos e
transições cruzando livros; contagens Markov congeladas mesmo diante de estado
novo; modelo de variantes congelado; e compressão/roundtrip em montagem positiva
conhecida. O JSON contém sementes, hipóteses, contagens, custos, dicionários e
saídas dos controles. A execução usa apenas a biblioteca padrão Python.

O passo seguinte para P03 é aumentar os controles com autores e geradores
independentes e avaliar variantes em conteúdo externo realmente novo. Uma
competição mais rica pode discriminar cenários particulares, mas deve primeiro
mostrar poder para separar prosa cifrada copiada de montagem sem plaintext.
Não tratar compressibilidade, dependência contextual ou ganho de previsão de
códigos como prova de uma tradução ou de ausência universal de mensagem.
