# Auditoria dos zeros restaurados e da ambiguidade dos dígitos originais

**A camada importada é mecanicamente consistente, mas ainda não especifica um
decodificador autossuficiente de uma sequência bruta inédita.** A pipeline
experimental recebe os códigos já tokenizados e restaurados. Nesta auditoria
não usamos inglês para escolher uma segmentação, nem produzimos tradução.

## Duas perguntas diferentes

1. **Com a sequência de códigos importada fixa**, em quais ocorrências seu
   zero inicial foi omitido? A auditoria anterior encontrara nove livros com
   duas ou mais posições de omissão possíveis para o mesmo stream.
2. **Sem fixar os códigos**, quantos caminhos de segmentação são compatíveis
   com os dígitos brutos e a regra permissiva de zeros? Aqui os70livros têm
   múltiplos caminhos. Isso não contradiz o resultado de nove livros: é um
   espaço de modelos maior.

Os códigos e as posições fornecidas reproduzem exatamente os70textos
originais. Isso verifica o roundtrip condicionado à entrada importada; não
identifica qual regra original ou qual segmentação deve ser aplicada a um
novo texto que só contenha dígitos.

## Omissões por código

Nos streams importados há634ocorrências de códigos00–09:195zeros omitidos e
439preservados. As contagens abaixo usam uma escolha de alinhamento registrada
em `normalized_books.json`; nos nove casos ambíguos não atribuímos autoria a
essa escolha.

|Código|Ocorrências|Zero omitido|Zero preservado|Ação observada|
|---|---:|---:|---:|---|
|00|120|4|116|mista|
|01|86|21|65|mista|
|02|8|0|8|sempre preservado|
|03|65|23|42|mista|
|04|93|20|73|mista|
|05|53|12|41|mista|
|06|58|37|21|mista|
|07|50|50|0|sempre omitido|
|08|58|20|38|mista|
|09|43|8|35|mista|

Somente02e07têm uma ação determinística nessa transcrição; isso não prova uma
regra universal em dados novos. A variedade de ações nos outros códigos pode
vir de contexto, fronteiras, outra tokenização ou alinhamento importado.
Não declaramos que os195zeros tenham sido deliberadamente removidos pelos
criadores com uma finalidade criptográfica.

## Enumeração de todas as regras que dependem somente do código

Uma política nessa classe decide, para cada um dos dez códigos00–09, omitir
sempre ou preservar sempre seu primeiro zero. São2^10=1.024políticas. Para
evitarmos interpretar uma anotação ambígua como fato, verificamos diretamente
a string serializada contra os dígitos brutos, sem consultar posições de
omissão anotadas.

Mantivemos os68livros de descoberta e os dois reservados fora do ajuste.
Nenhuma política reproduz todos os68streams de descoberta; portanto nenhuma
reproduz todos os70com esses mesmos códigos importados.

Como baseline aproximado, escolhemos a política que maximiza o número de
livros exatos em descoberta, desempata pelo menor erro absoluto dos
comprimentos e depois pela máscara numérica. Ela omite06/07/08, acerta10/68
livros de descoberta e1/2reservados. Não é um serializador validado e não
explica os streams restantes. Não escolhemos política olhando o reservado.

**Escopo essencial:** essa exclusão mantém a sequência de5.729códigos fixa.
Se ela puder mudar livremente, a política de omitir o zero de todo código0d
representa trivialmente qualquer string de dígitos por tokens individuais0d.
Ela produz outro stream, não demonstra a reconstrução publicada nem uma
tradução. A enumeração não exclui serializadores contextuais, regras de
fronteira, chaves ou algoritmos adicionais.

## Contagem dinâmica sem códigos fornecidos

Para cada posição, o modelo permissivo permite:

- consumir dois dígitos quando o par está no inventário importado de99códigos;
- consumir um dígito `d` como código `0d`, removendo seu zero inicial.

Programação dinâmica conta todos os caminhos com inteiros arbitrários, sem
amostrar, ajustar inglês ou impor5.729tokens. Também obtém testemunhas com o
mínimo e máximo de tokens e verifica seus roundtrips. Não cruzamos fronteiras
de livros.

Todos os70textos têm mais de um caminho. O menor número por livro é
**14.930.352**; o maior é aproximadamente **2,00387×10^61**, registrado
integralmente no JSON. Somando os livros, os menores caminhos têm5.652tokens;
a sequência importada tem5.729; os maiores têm11.263, um token0dpor dígito.
Isso ilustra a flexibilidade do modelo, não identifica a segmentação verdadeira.

Contamos **caminhos de fronteiras/omissão**, não necessariamente sequências de
códigos distintas. Por exemplo, raw`001` com inventário`00,01` admite:

```text
[00,01]     escrito como 0|01
[00,01]     escrito como 00|1
[00,00,01]  escrito como 0|0|1
```

São três caminhos e duas sequências de códigos. Tampouco são contagens de
plaintexts ingleses, mensagens ou chaves. O resultado não prova ausência de
mensagem: um algoritmo contextual/linguístico correto poderia reduzir o
espaço de interpretações. Esse algoritmo ainda precisa ser especificado e
validado em dígitos novos sem fornecer a resposta intermediária correta.

## Verificação e consequência para a missão

Três verificações positivas estão incorporadas ao script: raw`12345678` tem
34segmentações de passos1/2com pares válidos (Fibonacci9), mínimo4e máximo8
tokens; entrada vazia tem um caminho vazio; o caso`001` distingue caminhos de
sequências. Cada testemunha de todos os livros tem roundtrip exato. Todos
os códigos importados têm comprimento entre os mínimos e máximos calculados.

Reprodução:

```sh
python scripts/zero_restoration_audit.py
```

`results/zero_restoration_audit.json` contém hashes, contagens por código,
divisão68/2, políticas, previsões brutas dos reservados e contagens/testemunhas
por livro. A auditoria é estrutural, sem nova busca de chave ou tradução.
O status é `RAW_DECODER_NOT_IDENTIFIED_NO_VERIFIED_TRANSLATION`: qualificar
substituição com tokens verdadeiros fornecidos é uma etapa útil, mas não
satisfaz por si o objetivo de traduzir sequências brutas inéditas de469.
