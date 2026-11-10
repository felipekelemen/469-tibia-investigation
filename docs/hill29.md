# Segunda rodada: matrizes de Hellgate módulo29

Esta experiência aborda um domínio em que **ambas** as matrizes fornecidas são
invertíveis. O módulo29 não foi deduzido da lore: é uma hipótese concreta,
pré-especificada antes de observar as saídas desta rodada. O alfabeto fixado é
`ABCDEFGHIJKLMNOPQRSTUVWXYZ .?`, com índices0–28.

## Modelo e grade

O escore não apaga pontuação para aproximar a saída de palavras inglesas.
Treinamos tetragramas sobre os29 símbolos no primeiro80% de *Alice*, referência
externa congelada. Transformamos caracteres que não pertencem ao alfabeto em
espaço, colapsamos espaços consecutivos, preservamos pontos e interrogações.
Usamos suavização aditiva0,01. Assim sequências de pontuação inadequadas são
penalizadas pela própria probabilidade externa; não ganham pontuação por serem
omitidas. Os20% finais são controle positivo, não treino do modelo.

A grade fixa tem **320 candidatos**:

- matrizes antiga e posterior;
- convenção de vetor coluna ou linha;
- operação direta ou inversa módulo29;
- cinco camadas: dígitos individuais; pares de dígitos brutos com offsets0/1;
  códigos restaurados de dois dígitos; símbolos intermediários;
- bases de entrada0/1, subtraídas antes da redução modular;
- offsets de0–3 símbolos por livro.

Os rótulos intermediários são convertidos por A=0…Z=25 e a máscara `*`=28;
essa convenção não transforma os rótulos em letras verdadeiras. Valores de
código maiores que28 são reduzidos explicitamente módulo29. Cada livro começa
nova fase; não há blocos cruzando livros. Caudas incompletas são descartadas
na triagem, sem inserir padding. O escore é média dos log10 de tetragramas,
ponderada por número de janelas, sem janelas entre livros.

## Seleção e controles

Somente os68 livros de descoberta escolhem o candidato. O selecionado é
pontuado nos livros20 e54, o componente reservado de61 códigos. Não há
compartilhamento literal de16 dígitos com descoberta, mas repetições menores e
transformadas podem permanecer. Os dois livros reservados são correlacionados,
e a camada intermediária foi importada de pesquisa que já viu o corpus inteiro.
Não existe aqui um teste prospectivo semanticamente independente.

Cada uma de39 réplicas embaralha blocos de oito valores **por livro e por
camada**, preservando ordem interna, comprimentos e frequências. A mesma grade
completa é otimizada novamente em descoberta; compara-se então o escore
reservado com o escore reservado dessa seleção. As camadas são controladas
separadamente, não são uma simulação gerativa conjunta de dígitos e códigos.
O nulo preserva muitos motivos locais, mas não todos os fragmentos longos nem
contagens exatas de bigramas. A resolução mínima do p empírico é0,025.

## Implementação e controles positivos

A inversão usa o adjunto e inverso do determinante módulo29. Um trecho de257
caracteres do inglês reservado é cifrado e decifrado com as duas matrizes nas
duas orientações. Caudas de1–3 caracteres podem ser preservadas explicitamente
sem cifra no helper de roundtrip; isso é uma convenção de teste declarada,
não uma chave ou regra descoberta para os livros. O rastreio no resultado
registra quantos blocos foram cifrados e quantos caracteres não foram.

Quatro testes verificam recuperação exata com pontuação e comprimentos
irregulares, ausência de padding implícito na triagem, sensibilidade do escore
a inglês externo e enumeração da grade/normalização. O resultado estruturado
contém todas as39 réplicas, candidatos vencedores e saídas reservadas completas.

```
python scripts/hill29_experiments.py --nulls 39
python -m unittest discover -s tests -p test_hill29.py -v
```

Nenhum escore ou p desta triagem constitui tradução atestada. A falha da grade
não exclui todas as cifras mod29, outras ordens de alfabetos, camadas extras ou
qualquer algoritmo arbitrário.

## Resultado executado

A seleção escolheu a matriz posterior, row, operação forward, camada `digits1`, base0 e offset1. Escore em descoberta **-7.002258**, no holdout **-7.015629**. O p empírico é **0.475**: nenhuma vantagem convincente sobre o controle de blocos. O controle inglês reservado tem escore **-3.671481**, contra **-6.679836** embaralhado. Todos os quatro roundtrips positivos foram exatos; quatro testes automatizados passaram.

Saídas reservadas do candidato selecionado:

```
20: HEHSC KTDTUUNKUSJZOR.MBPJESXOFYTUDTRJEGXNPFKKBPY.GEPXOKUU LL
54: NKUSJZOR.MBPJESXOFYTUDTRJEGXNPFKKBPY.GEPXOKUU LLPIDXNXKK
```

Nenhuma dessas saídas é inglês coerente. Resultado **NO_VERIFIED_TRANSLATION**, limitado à grade e ao pontuador declarados.
