# Segunda rodada — investigação469

**Resultado: nenhuma tradução verificável; zero livros com plaintext validado.**
Os experimentos abaixo foram implementados e executados, com controles positivos
e negativos. Os resultados não excluem famílias completas de cifras.

## Hill módulo29

A matriz posterior, singular em26, é invertível em29. Testamos320 convenções
explícitas com ambas as matrizes, orientações, sentidos, cinco representações,
bases e offsets. O alfabeto foi fixado como A–Z, espaço, ponto e interrogação.
O pontuador externo preserva esses caracteres; a escolha ocorre só nos68 livros
de descoberta. Os dois livros reservados contêm apenas61 códigos e pertencem
a um único componente correlacionado, limitação herdada da primeira rodada.

O melhor candidato teve escore−7,002258 em descoberta e−7,015629 no reservado.
39 controles de blocos, repetindo a seleção inteira, deram **p=0,475**. O
controle positivo inglês recebeu−3,671481 contra−6,679836 embaralhado.
Roundtrips artificiais com as chaves verdadeiras recuperaram o texto exatamente,
incluindo pontuação e tratamento explícito das caudas. Nenhum candidato
produziu inglês coerente. [Detalhes e convenções](hill29.md).

## Homofonia com controle de bigramas

Executamos busca com orçamento idêntico em dados e controles: dois reinícios,
5.000 mutações cada,19 shuffles e19 controles de trilhas Euler preservando
exatamente comprimento, contagens dos códigos, bigramas e extremidades. O
amostrador Euler não é uniforme sobre todas as trilhas possíveis. Nos livros
reservados curtos, alguns controles não conseguem alterar a sequência.

Os p no reservado foram **0,20** contra shuffle e **0,45** contra bigramas.
A melhoria em descoberta não se tornou tradução validada. Mais importante:
um positivo independente, inglês cifrado com dois homofones por letra,
recuperou apenas **26/61 letras(42,6%)** sem a chave. Com a chave verdadeira,
o fixture é recuperado integralmente. A busca não tem poder demonstrado para
rejeitar homofonia: melhorar a recuperação de positivos passa a ser condição
antes de alegar exclusão. [Método e resultados](homophonic_controls.md).

## Canal residual e variações entre trechos

Nos779 contextos simbólicos distintos de comprimento8 compartilhados entre
livros,56 usam mais de um stream de códigos, até quatro variantes. Portanto,
não cabe afirmar que a escolha de homofones seja invariavelmente fixa por
contexto. Ao mesmo tempo, o acordo numérico médio entre ocorrências de livros
distintos é96,262%, muito acima de199 nulos que preservam a sequência simbólica
e as contagens de cada código por símbolo/livro. Há dependência contextual
forte, compatível com reutilização e outros mecanismos determinísticos;
ela não identifica uma mensagem.

A expansão e deduplicação das divergências deixou106 trechos maximais.
As181 diferenças contadas nesses trechos incluem51 reversões dos dígitos e
130 outros homofones; continuam dependentes, não181 eventos independentes.
O par19/91 não conta como reversão homofônica porque tem rótulos diferentes
na tabela importada. Um exemplo possui105 símbolos, dos quais102 códigos
iniciais idênticos e três finais divergentes.

A hipótese de orientação dos pares como bits foi testada em16 convenções
(offsets0–7 e inversão), com99 nulos estratificados e seleção do máximo.
**p=0,28**, sem leitura inglesa. Essa busca de ASCII no corpus completo é
exploratória, não teste semântico em holdout. [Canal residual](residual_channel.md).

## Geometria do mapa e caveiras

Testamos53 funções dos dois dígitos: operações aritméticas/bitwise e funções
das matrizes de caveiras como lookup ou forma bilinear dos vetores de bits.
Nenhuma permite reproduzir exatamente os99 rótulos com uma tabela univalente
do resultado. A melhor função derivada das caveiras ainda exige pelo menos59
códigos incompatíveis. Isso rejeita esses modelos específicos de uma camada.

A quase simetria dos dígitos do mapa importado é real: a identificação por par
não ordenado ajusta98/99 entradas, mas possui55 valores distintos e ainda
falha em19/91. Não é tradução, nem explicação compacta suficiente. Os999
controles e leave-one-code-out da tabela estão documentados separadamente;
eles não tornam os livros nem a tabela aprendida previamente independentes.
[Geometria e limites](map_geometry.md).

## Validação, reprodução e prioridade seguinte

A suíte completa contém **36 testes aprovados**. Todas as sementes, saídas
literais, pontuações e controles são versionáveis em results. Execute:

```sh
python -m pip install -r requirements.txt
python scripts/bootstrap_sources.py
make round2
make test
```

A prioridade algorítmica agora é um solucionador homofônico que primeiro
recupere prosa em positivos externos com várias sementes e número de homofones.
Depois, congelar o orçamento e executar nulos com reotimização equivalente.
Para o canal residual, o passo seguinte é modelar as variantes dos trechos
longos e prever ocorrências externas, em vez de procurar palavras curtas.
Novos fragmentos e pares número/inglês atestados continuam sendo a melhor
forma de reduzir a ambiguidade e obter validação verdadeiramente independente.

## Publicação: bloqueio verificado após reconexão

O destino informado pelo usuário é
https://github.com/felipekelemen/469-tibia-investigation . O commit inicial
remoto foi obtido e incorporado localmente sem sobrescrever seu histórico.
Após o usuário reconectar o GitHub, git push, criação de árvore e escrita pelo
endpoint Contents continuaram retornando HTTP403, “Resource not accessible by
integration”. Nenhum desses testes publicou arquivo ou atualizou main remoto.
A consulta das instalações acessíveis devolveu lista vazia. As permissões admin
exibidas para o usuário não demonstram que a credencial da integração possa
escrever. Não foi identificada instalação gerenciável que possamos corrigir
por ferramenta nesta sessão, e não solicitamos segredos em chat.

O bundle Git entregue contém o histórico local e o commit inicial remoto.
Como alternativa que usa a autenticação GitHub da sua própria máquina:

```sh
git clone tibia-469-research.bundle 469-tibia-investigation
cd 469-tibia-investigation
git remote set-url origin https://github.com/felipekelemen/469-tibia-investigation.git
git push -u origin main
```

O push é normal, sem force. Se o remoto tiver novos commits, preserve-os por
fetch/merge antes de publicar. O histórico científico e os resultados não
dependem dessa publicação para serem reproduzidos.
