# Rodada 29 — comparação de geradores e limites da evidência por compressão

Executada em 23/11/2026, horário de São Paulo, sobre
`22b4d09c3fbd0e4827beed8055fe672c1194cee4`.

**A comparação não se qualificou para identificar a origem de 469.** Foram
executados 240 corpora sintéticos com processo de construção conhecido. Pelo
custo total, o modelo numérico venceu todos, inclusive inglês cifrado cuja
chave correta foi recuperada. Pela previsão reservada, houve reconhecimento
de textos e misturas da família prevista, mas falhas nos controles estruturais
e nas cifras fora dessa família. Nenhum desses resultados prova ausência de
texto no jogo. A missão permanece inconclusiva.

**Nenhuma candidata nova; tradução potencial não identificada.** Não há nova
tradução de Avar Tar, Knightmare, Chayenne ou dos livros. Não atribuímos origem
textual/não textual ao corpus usando um critério que falhou nos controles.

## O que mudou desde as rodadas 3 e 24

As comparações anteriores já mostravam que copiar módulos comprime também
inglês cifrado. Aqui, acrescentamos um modelo explicitamente treinado em inglês,
busca de chave, uma classe mista, custos de implementação e parâmetros, autores
novos, previsão reservada, controles pareados e um teste fora da família da cifra.

| Hipótese | Teste novo | Resultado |
| --- | --- | --- |
| H113: menor descrição distingue texto, números e mistura | Três classes com chave/dicionário/custos pagos, 240 corpora | Falha: todos escolhidos como N, inclusive textos e misturas conhecidos |
| H114: prever melhor os trechos reservados resolve a origem | Mesmos ajustes congelados, sem custo de modelo na pontuação reservada | Falha nos módulos embaralhados e nas permutações fora da família |
| H115: uma divisão de livros fornece avaliação independente | Componentes de trechos iguais e cobertura do reservado | Todos os 70 conectados; forte sobreposição na divisão fixa |

Não houve uma nova busca de lore nesta rodada. Reutilizamos as transcrições
prioritárias já auditadas. As únicas fontes novas são os controles literários:
[*Silas Marner*, George Eliot](https://github.com/GITenberg/Silas-Marner_550/tree/a4c56c3b0a355f69ceba3fb73adf25579ad3ddd9)
e [*North and South*, Elizabeth Gaskell](https://github.com/GITenberg/North-and-South_4276/tree/aeffaffe76f31ee5bf6e9608e825e3b38947c025).
Os arquivos integrais, avisos Gutenberg, commits, datas e hashes estão em
[round29_reference](../data/round29_reference/SOURCES.json). O modelo de inglês
usa outros autores: Lewis Carroll e Jane Austen, em fontes já preservadas.

## Protocolo e modelos

[Protocolo](../data/round29_protocol.json),
[fixtures](../data/round29_fixtures.json) e
[manifesto de 20 insumos](../data/round29_experiment_manifest.json) foram
congelados antes dos ajustes de qualificação. Testes pequenos de software
foram executados antes do congelamento; não foram usados para calibrar o gate.

- **T:** pares decimais 00–25 representam letras sob uma chave afim módulo 26.
  Enumeramos as 312 chaves. Um modelo de bigramas ingleses fornece probabilidades;
  pares 26–99 são exceções pagas, com massa total 1/16. Dígito final ímpar é pago
  separadamente. Não são testadas todas as substituições, bases ou homofonias.
- **N:** dígitos uniformes, frequências IID ou Markov de primeira ordem,
  com contagens aprendidas apenas no treino. São códigos estatísticos;
  sua capacidade de representar um texto não indica como ele foi criado.
- **M:** um componente T e um N, com um bit por documento escolhendo qual usar.
  O bit é transmitido; não alegamos prever a origem antes de ler o documento.

T e N podem usar o **mesmo recurso de cópia**: até 64 módulos, aprendidos
exclusivamente no treino, em comprimentos predefinidos. O dicionário é pago;
cada referência ou literal é pago; o caminho de menor custo é calculado
exatamente. M paga o dicionário compartilhado uma única vez quando necessário.
Referências atualizam o contexto pelos dígitos recuperados. Nenhum módulo
novo é aprendido no reservado.

Por corpus, comparamos 624 configurações T, seis N e 3.744 M. Todas as chaves,
bases e opções de cópia são selecionadas pelo custo de parâmetros mais dados
de **treino**. Depois calculamos duas regras distintas, previamente fixadas:
menor custo total e menor custo dos dados reservados. Não ajustamos as escolhas
com o reservado. Foram 240 buscas finitas completas, sem truncamento.

### Custos explicitamente cobrados

- Chave afim: nove bits; seletores de classe, base e cópia: campos fixos.
- Modelo inglês: 26 contagens marginais e 676 de transição, codificadas por
  gamma, totalizando **7.998 bits**. Os textos-fonte não precisam ser transmitidos
  além das estatísticas que o decodificador efetivamente usa.
- Modelos numéricos: contagens IID ou Markov serializadas; uniforme sem contagens.
- Dicionário: quantidade, comprimentos e conteúdo de cada módulo; sete bits por
  par decimal. Caminhos, referências e exceções não são gratuitos.
- Comprimento de cada documento e dois bits de terminação aritmética; quantidade
  de documentos em cada conjunto; um bit de rota por documento em M.
- Programa comum: **210.184 bits**, medidos nos bytes das duas implementações
  de decodificação, mais 20 bits comuns para as quantidades de documentos.
  Esse custo é idêntico entre T/N/M e não muda o vencedor.

Python, NumPy e a linguagem de descrição são condições compartilhadas. Nenhum
modelo ajustado usa uma semente para reconstruir os dados: custo de semente
zero, declarado; as sementes dos controles não são chaves gratuitas do codec.
Os custos são comprimentos ideais de códigos prefixados/aritméticos com
sobrecarga explícita, não arquivos comprimidos medidos nem mínimos universais
de complexidade. Outra linguagem de descrição ou um modelo inglês já
compartilhado mudaria os custos relativos; não testamos essa mudança após ver
os resultados.

## Controles e avaliação

São 30 janelas de posições não sobrepostas, 15 de cada autor novo, emparelhadas
entre oito perfis: **240 corpora, não 240 fontes independentes**. Cada corpus
contém 70 documentos, com comprimentos derivados dos livros reais e arredondados
para baixo ao par de dígitos. O corpus real não foi modificado. São 11.226
dígitos sintéticos: 7.746 nos primeiros 50 documentos de treino e 3.480 nos
últimos 20 reservados.

Nos perfis com cópia, 16 módulos de 32 letras estão disponíveis no treino;
o reservado pode usar esses módulos e oito adicionais. O controle embaralhado
mantém os mesmos sorteios e histogramas por módulo, permutando a ordem de suas
letras uma única vez. Na mistura, documentos inteiros alternam prosa cifrada
e Markov numérico. As permutações de desafio não pertencem às 312 chaves afins.
Nenhum caso foi selecionado pelo resultado do buscador.

| Processo do controle | Rótulo operacional esperado | Acertos por custo total | Acertos por previsão reservada |
| --- | --- | ---: | ---: |
| Prosa inglesa, cifra afim | T | 0/30 | 30/30 |
| Fragmentos ingleses copiados, cifra afim | T | 0/30 | 30/30 |
| Dígitos uniformes | N | 30/30 | 30/30 |
| Markov numérico | N | 30/30 | 30/30 |
| Módulos embaralhados, mesma estrutura de cópia | N | 30/30 | 2/30 |
| Mistura de prosa cifrada e Markov | M | 0/30 | 30/30 |
| Prosa, substituição não afim | T | 0/30 | 0/30 |
| Fragmentos copiados, substituição não afim | T | 0/30 | 8/30 |

O limiar predefinido era 27/30 por perfil. Nenhuma regra passou, mesmo
considerando apenas os seis perfis dentro das famílias declaradas. Os 28
controles embaralhados que falharam na regra reservada foram escolhidos como T;
nas cópias com permutação não afim, houve oito T, vinte N e dois M.

O rótulo N dos módulos embaralhados designa um **controle estrutural**. Sua
composição vem de inglês e sua procedência é preservada; não prova inexistência
de qualquer informação textual recuperável. A falha diz que o critério não
discrimina os processos operacionais especificados. Os contraexemplos de prosa
inglesa escolhida como N pelo custo total independem dessa ressalva.

O protocolo fixa 30 casos por perfil, mas também contém a expressão ambígua
"no pooling ... authors". A execução tem 15 casos por autor e aplica o limiar
ao perfil de 30; não há qualificação separada de 30 casos por autor. Publicamos
as contagens por autor no [resumo](../results/round29_summary.json). Não
alegamos qualificação por autor; as falhas de discriminação aparecem em ambos,
portanto essa ambiguidade não autoriza aplicar o método a 469.

### Por que o vencedor numérico não demonstra ausência de texto

Nos 60 controles T de cifra afim, o componente textual recuperou a **chave
verdadeira em todos**. Ainda assim, N venceu pelo custo total. Para prosa
comum, T economizou em média 1.545,8 bits nos dados reservados, mas seu custo
total ficou 2.372,1 bits acima de N. Para fragmentos copiados, as diferenças
foram −1.345,8 bits no reservado e +6.063,4 no total. O cabeçalho do modelo
inglês não foi amortizado nessas amostras.

Além disso, a chave de relabeling afim foi recuperada nos 30 controles de
módulos embaralhados. Recuperar frequências ou uma transformação de símbolos
não reconstitui automaticamente a ordem original ou valida sentido inglês.

Esses são contraexemplos concretos à inferência "modelo numérico menor implica
origem sem texto", dentro desta comparação. Não são um teorema contra toda
comparação estatística de geradores, nem uma identificação da cifra de Tibia.

## Dependência e aplicação ao jogo

As duas regras falharam antes de qualquer pontuação de origem no jogo. Conforme
o protocolo, **não executamos a classificação T/N/M do corpus real**. Executamos
a auditoria de dependência, sem escolher nova divisão para melhorar métricas.

Todos os 70 livros pertencem a um único componente quando uma igualdade de
12 dígitos cria uma ligação. Nos últimos 20 livros da divisão fixa:

| Critério | Janelas iguais ao treino | Dígitos reservados cobertos |
| --- | ---: | ---: |
| 12 dígitos | 2.968/3.269 | 3.394/3.489 = 97,3% |
| 24 dígitos | 2.510/3.029 | 3.304/3.489 = 94,7% |

Igualdade não identifica por si só a causa da repetição. Nos próprios controles
de prosa sem cópia intencional, janelas de 12 dígitos cobrem em média 31,5% do
reservado; com 24 dígitos, 1,9%. Portanto, não tratamos toda janela curta igual
como prova de colagem autoral. As dependências reais continuam inadequadas
para alegar validação semântica independente entre livros.

As partes de Chayenne de 36 e 13 dígitos continuam aparecendo 11 e nove vezes
nos livros. O levantamento por grupo de comprimento pelo menos 12 não inclui
os grupos curtos de Avar/Knightmare; não é alegação de ausência de outras
dependências. As três falas continuam prioritárias, mas nenhuma recebe novo
plaintext. `3478`/nomes e matrizes de Hellgate não tiveram nova evidência nem
nova busca: permanecem as decisões delimitadas das rodadas 25, 26 e 28.

## Verificação, reprodução e decisão

A implementação independente usa probabilidades escalares e programação
dinâmica no sentido oposto ao código principal. Conferiu **50.400 custos de
documento/modelo**, além dos cabeçalhos, com diferença máxima de
1,82×10⁻¹² bit. Verifica os modelos selecionados; não reivindica uma auditoria
independente de toda a seleção nem revisão por terceiros.

Passaram **293 testes automatizados**. Os registros de reprodução estão em
[round29_verification.json](../results/round29_verification.json).
O replay completo também terminou: os 240 corpora foram reajustados e todos
os resultados coincidiram com os arquivos originais.

```bash
make test
make round29
make round29-full
```

O replay curto confere hashes, regenera fixtures e estatísticas inglesas,
refaz auditorias, certificados e agregações e reajusta os oito primeiros
corpora. O completo repete os 240 ajustes. Não precisa acessar a rede.
Os scripts recusam sobrescrever resultados experimentais já produzidos.

Encerramos R29 como **comparação executada, discriminação não qualificada**.
Nenhum gerador original de Tibia foi autenticado; nenhuma ausência de texto
foi demonstrada. R30 é a única etapa restante deste lote: consolidar os
certificados e limitações das 29 rodadas, verificar a reprodução e adjudicar
T/G/I no escopo das evidências. Uma nova tentativa de classificação exigiria
modelo e critérios fixados com novos controles, não reajuste destas amostras
já expostas até obter uma conclusão desejada.
