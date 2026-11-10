# Auditoria do Deep Research: Chayenne, NPCs, enquetes e fragmento hexadecimal

**Resultado:** o relatório oferece uma organização útil, mas sua proposta de
usar Chayenne como holdout temporal precisa de correção. As duas partes
numéricas da entrevista já são fragmentos exatos dos livros. Tampouco existe
plaintext oficial disponível para as supostas palavras do pequeno codebook
comunitário consultado.

## Chayenne: fonte externa, conteúdo numérico reutilizado

A [entrevista publicada pelo Portal Tibia em15/05/2009](https://forum.portaltibia.com.br/topic/11420-entrevista-com-chayenne/)
foi lida nesta auditoria. A seção inglesa contém a resposta numérica atribuída
à desenvolvedora e os emoticons; não oferece tradução da resposta. Trata-se de
fonte contemporânea da entrevista, não de confirmação de toda interpretação
posterior da linguagem.

Contagem direta em `data/normalized_books.json`, sobre dígitos originais, sem
padding e sem cruzar fronteiras dos livros:

| Fragmento | Ocorrências | Livros zero-based |
|---|---:|---|
|114514519485611451908304576512282177|11|1,8,10,19,27,31,35,37,41,63,66|
|6612527570584|9|2,5,9,22,28,46,48,51,53|
|Concatenação direta das duas partes|0|nenhum|

Os offsets exatos constam de `results/research_npc_audit.json`. A ausência da
concatenação não torna as partes inéditas: cada uma já ocorre integralmente
na descoberta. A entrevista pode atestar o uso público desses números por uma
desenvolvedora; não é avaliação independente de conteúdo novo para um decoder
que já viu os70 livros. Nem permite presumir que cada bloco separado por
espaço corresponda a uma única palavra.

## Knightmare, falas e enquetes

A frase concatenada de Knightmare não ocorre no corpus. Seus tokens têm
comportamentos distintos:3478 aparece24 vezes,67 aparece189,345 aparece40;
90871,97664 e3466 não aparecem. Essas contagens não demonstram equivalências
léxicas, nem provam por si só um sistema diferente. Tokens curtos podem
coincidir com partes dos códigos dos livros.

O [relatório de kimlage, seção3.2](https://github.com/kimlage/tibia-469-cipher-casestudy/blob/main/docs/469_final_report.md)
explicita que os significados de seu codebook são análises comunitárias e não
CipSoft-confirmados. Distingue entradas armazenadas em sua base de reconstruções
documentais; os testes internos citados comparam saídas de seu próprio decoder.
Armazenar uma atribuição em uma tabela chamada ground truth não a transforma
em referência semântica externa. Essas atribuições podem orientar hipóteses,
mas não servir simultaneamente para construí-las e validá-las.

A [enquete oficial de2020](https://www.tibia.com/community/?subtopic=polls&page=show&questionaireid=1009)
não pôde ser aberta pela ferramenta web nesta auditoria. A transcrição local
fixada de s2ward contém a opçãoC e mantém seu significado como desconhecido.
As explicações das outras alternativas não são a tradução da alternativa469.
Não há novo par número/inglês oficial derivado dessa consulta.

## Fragmento hexadecimal: o demonstrado e o atribuído

`bytes.fromhex('62792068657272657261').decode('ascii')` produz exatamente
`by herrera`. O fragmento não ocorre nos70 livros. A
[discussão histórica do Reddit](https://www.reddit.com/r/TibiaMMO/comments/qh0nvd/469_language/)
foi lida: o post original foi excluído, mas comentários preservam a comparação
com o poema de Avar Tar e a interpretação hexadecimal. Um comentário posterior
infere intervenção de terceiro; não é, sozinho, prova de um mecanismo específico
de comprometimento de DNS.

A [compilação de s2ward](https://github.com/s2ward/469/blob/main/00-timeline.md)
relata confirmação por Herrera e aponta uma captura. Essa captura e a identidade
do interlocutor não foram autenticadas nesta auditoria. Portanto registramos:
decodificação ASCII **demonstrada**; autoria/história do incidente **atribuída à
fonte comunitária**, não independentemente comprovada. Para a investigação469,
o fragmento alterado deve ficar fora dos cribs canônicos; não é necessário
resolver toda a história do domínio para evitar usá-lo como pista oficial.

## Mudanças recomendadas no plano

1. Separar **fonte externa de atestação** de **texto externo inédito para teste**.
   Reutilização exata, montagem por motivos e exposição prévia precisam ser
   auditadas antes de chamar qualquer amostra de holdout.
2. Organizar por modalidade, fonte e época, sem assumir automaticamente que
   todos os números de NPC/desenvolvedor usem código por palavra, nem que
   todos pertençam a um único sistema distinto dos livros.
3. Manter glosses comunitários como hipóteses com proveniência e alternativas.
   Deixar uma fonte inteira fora do ajuste e procurar previsões externas;
   frases já usadas para inventar a tabela não validam essa mesma tabela.
4. Não selecionar uma tradução da enquete a partir do contexto temático nem
   usar os emoticons de Chayenne como plaintext. Contexto restringe hipóteses,
   mas não resolve a ambiguidade por si só.

Esta foi uma auditoria de fontes e reutilização, não uma nova tentativa de
tradução. Nenhum código recebeu significado novo. Os metadados, contagens,
fontes e limitações estão no JSON associado.
