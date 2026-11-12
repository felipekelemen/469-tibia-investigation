# Sexta rodada: coerência literal, módulos e decodificação dos dígitos

**Nenhuma tradução verificável ou candidata longa contextualizável foi
encontrada.** Esta rodada executou auditorias sobre a chave V4 existente,
qualificou um avaliador independente e identificou uma etapa ainda ausente
para traduzir dígitos inéditos. Não houve nova otimização da chave.

## Resultados e consequências

1. **Módulos:** um inventário aprendido só nos 68 livros de descoberta cobre
   4.012/5.668 códigos (70,78%) e 59,75% dos seus tetragramas. Nenhum dos
   61 códigos reservados pertence a referências desse inventário de motivos
   com pelo menos oito códigos. Portanto, o nulo proposto de permutar módulos
   fica bloqueado no reservado: ali seria apenas embaralhar caracteres.
   Foram executadas 99 permutações diagnósticas com chave fixa, não novas
   otimizações. Seus p condicionais não substituem os controles anteriores.
   [Método, decomposição e limite](module_signal_audit.md).
2. **Coerência independente:** o modelo lexical treinado com outros autores
   foi congelado e avaliado em 600 condições pareadas externas. Nenhum dos
   quatro comprimentos passa o gate. O avaliador aceita muitas sequências
   com palavras embaralhadas e perde inglês com erros/nomes desconhecidos.
   Assim, sua falha não é evidência de ausência de linguagem nos livros.
   [Protocolo e todas as taxas](word_validator_audit.md).
3. **Leitura literal:** foram inspecionadas as 70 saídas, 5.729 letras. Há
   fragmentos curtos como `BUT I WAS`, mas nenhum trecho identificado com
   seis palavras/25 letras contínuas, gramatical e contextualizável sem
   modificar letras. Esse mínimo é uma triagem exploratória, não certificado
   de tradução. A recorrência dos fragmentos vem de motivos compartilhados.
   [Exemplos e posições nos números originais](literal_candidate_review.md).
4. **Zeros e segmentação:** nos códigos importados, 195 zeros iniciais foram
   omitidos e 439 preservados. Nenhuma das 1.024 políticas determinísticas
   por código reproduz todos os 68 livros de descoberta mantendo os streams
   importados. Sem fornecer os códigos, o modelo permissivo de passos de
   um/dois dígitos admite múltiplos caminhos em todos os 70 livros: entre
   14.930.352 e aproximadamente 2×10^61 por livro. São caminhos de fronteiras
   e omissão, não contagens de mensagens. [Contagem exata e escopo da
   exclusão](zero_restoration_audit.md).

## Um fragmento real, ainda insuficiente

Sob a chave V4 selecionada anteriormente, o fragmento numérico do livro 0
`81911800356114`, tokenizado como `81 91 18 00 35 61 14`, produz literalmente:

```text
BUTIWAS
```

Pode receber os espaços `BUT I WAS` ("mas eu era/estava"), mas seu contexto é
`ERSEALSOUTEABUTIWASEANDANDDANSTHENYME`, que não continua uma frase coerente.
Não há base para ligá-lo a um evento ou personagem da lore. São sete letras
comuns, obtidas por uma chave escolhida para favorecer inglês: não constituem
tradução de mensagem. O registro também documenta o falso candidato
`ALL THE SAND`: o literal é `ALLETHESAND`, com um E adicional que não pode ser
apagado. Não houve correção de letras nem preenchimento narrativo.

## O que permanece demonstrado e o que falta

A V4 passou o benchmark sintético específico da quinta rodada e seu escore
de tetragramas superou os nulos testados (p exploratórios 0,01/0,01/0,02).
Esta rodada não remove esse sinal estrutural nem demonstra sua origem.
Também não transforma esses p-valores em evidência semântica.

A reconstrução de 5.729 códigos tem roundtrip exato **quando a sequência
importada e as omissões são fornecidas**. Ainda não há regra validada que
escolha esses códigos a partir de uma nova sequência bruta. O inventário de
códigos também foi obtido do corpus público completo; a auditoria não cria
um teste externo independente. Um tradutor integral deve resolver a etapa
raw→tokens além de tokens→inglês, sem receber a resposta intermediária.

As exclusões desta rodada são limitadas: uma família de políticas de zeros
foi descartada para os streams fixos; um avaliador falhou; um controle modular
ficou inviável no reservado. Isso não prova que 469 seja sem significado.

## Próximos experimentos priorizados

1. **Qualificar a etapa raw→tokens.** Criar positivos externos com supressão
   de zeros conhecida, inclusive contextuais, e controles pareados; separar
   a recuperação de fronteiras da recuperação de inglês. Congelar famílias
   pequenas antes de testar 469. Não selecionar a segmentação só por palavras
   aparentes; medir quantas alternativas produzem igual pontuação nos nulos.
2. **Coletar pares externos autenticáveis.** Priorizar mensagens novas e
   traduções oficiais explícitas, com data/fonte e busca de sobreposição
   nos livros. Os antigos reservados não podem voltar a ser testes cegos.
3. **Aprimorar coerência fora do jogo.** Avaliar um novo critério com melhor
   discriminação da ordem e robustez a nomes, em autores ainda não usados,
   antes de usá-lo para selecionar chaves ou segmentações de 469.

Uma candidata que emerja desses passos deve ser publicada com o literal
exato, algoritmo completo, decisões feitas antes da validação e teste externo.
Sem isso, a lore pode sugerir perguntas, mas não fornecer letras faltantes.

## Conferir a execução

```sh
make round6
make test
```

O primeiro comando confere hashes, integridade das 70 leituras, os 600 registros
e recalcula a contagem dinâmica dos 70 livros sem ajustar chaves. Os comandos
para recalcular cada estudo estão nos relatórios especializados. O manifesto
`data/round6_evidence_manifest.json` fixa os artefatos publicados; resultados
negativos e impedimentos estão no registro de hipóteses.
