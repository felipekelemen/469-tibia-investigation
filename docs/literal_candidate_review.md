# Auditoria literal das possíveis leituras da chave V4

**Não identifiquei uma candidata substantiva de tradução em inglês.** Examinei
as70saídas completas,5.729letras, produzidas pela mesma chave V4 que foi
selecionada antes desta revisão. Nenhuma chave foi ajustada para criar palavras
da lore ou melhorar este parecer. A revisão linguística é uma inspeção
assistida dessas saídas, não um classificador automático de gramática.

## O que conta como candidata nesta triagem

Uma leitura substantiva exigiria pelo menos seis palavras e25letras contínuas,
inglês gramatical e interpretação contextual justificável sem inventar conteúdo.
Esse limiar não torna uma sequência verdadeira; apenas evita promover palavras
curtas e coincidências locais. Só é permitido acrescentar espaços/pontuação à
mesma sequência de letras. Não se permite inserir, retirar, trocar ou rearranjar
letras, mudar a chave ou escolher um anagrama a partir da lore.

Os70literais, IDs dos livros e papéis no ajuste estão em
`results/literal_candidate_audit.json`. Os IDs são zero-based. Os68livros de
descoberta informaram a chave; os dois reservados já foram examinados e têm
relação entre si. Nada aqui cria um novo teste cego.

## Fragmentos reconhecíveis, sem leitura suficiente

Há sequências curtas reais, e não seria correto escondê-las. Elas também não
são uma frase traduzida ou evidência independente de lore:

|Espaçamento possível sem mudar letras|Ocorrências|Exemplo de origem|
|---|---:|---|
|BUT I WAS|13|livro0,códigos28–34|
|I WAS|16|livro0,códigos31–34|
|WAS TO THE|15|livro0,códigos3–10|
|THE SAND|8|livro17,códigos110–116|
|IN THE|2|livro4,códigos29–33|
|THERE|5|livro4,códigos31–35|

As ocorrências reutilizam motivos entre livros e não equivalem a13ou15
mensagens independentes. Os probes foram registrados após a inspeção, como
exemplos exploratórios; não são um teste preregistrado nem oferecem p semântico.

No livro0, o trecho numérico original `81911800356114`, posições raw54–67,
separa-se exatamente em `81 91 18 00 35 61 14` e produz `BUTIWAS`. O contexto
literal é:

```text
ERSEALSOUTEABUTIWASEANDANDDANSTHENYME
```

`BUT I WAS` é legível, mas o entorno não continua como frase inglesa coerente
sem reparos. Não há um predicado completo, um evento de lore identificável ou
um par de plaintext oficial. Uma sequência de sete letras e três palavras
comuns não é a tradução de um livro.

No livro17, `58576594344215` produz `THESAND`, dentro de:

```text
IFEALAREALLETHESANDHILEANTTOEAUARRDDO
```

A leitura tentadora `ALL THE SAND` **não aparece**. O literal correspondente é
`ALLETHESAND`; para produzir aquela expressão seria necessário apagar umE.
Esse reparo é proibido e não foi usado. A palavra `SAND` não estabelece relação
com desertos do jogo por si; escolher um lugar da lore depois de ver a palavra
seria uma interpretação adicional sem evidência.

Outras expressões aparentes que merecem controle negativo — `THE NAME`,
`OF THE`, `AND THEN` e `THE OTHER` — têm zero correspondências literais sob
essa chave. Isso também não é um teste de ausência de linguagem; documenta
apenas os probes desta inspeção.

## Reservado e nomes aparentes

As duas saídas reservadas continuam:

```text
TSICASAWREYALHEATHERMABELIESTOTE
LWREYALHEATHERMABELIESTOTERES
```

Há substrings que lembram nomes ou palavras, mas não uma frase contínua
com significado verificável. Não inserimos letras para converter essas formas
em nomes de NPCs, lugares ou uma narrativa. A informação de lore deve ajudar
a verificar uma leitura que o algoritmo já produziu, não fornecer letras
faltantes ou selecionar correções ad hoc.

## Proveniência e reprodução

`scripts/literal_candidate_audit.py` aplica o mapa fixo sem fitting. Para cada
fragmento curto, registra livro, intervalo de códigos, dígitos raw originais,
intervalo raw, contexto e ambiguidade da restauração de zeros. As posições
originais são calculadas da reconstrução escolhida e têm roundtrip verificado.
Nos nove livros com múltiplos alinhamentos compatíveis, essa localização é
condicional ao alinhamento importado, não uma resolução independente.

```sh
python scripts/literal_candidate_audit.py
```

Esta conclusão impede promover **essas saídas** como traduções neste momento.
Não rejeita outras chaves, códigos por palavra/sílaba ou algoritmos ainda não
validados. Nenhuma tradução contextual foi fabricada para satisfazer a busca.
