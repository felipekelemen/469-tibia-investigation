# Décima quarta rodada: fontes históricas das matrizes

**Nenhuma tradução foi encontrada.** Há agora uma atestação arquivada da
tabela antiga em 2008. Relatos atribuídos a 2009 e abril de 2010 descrevem
mudança de aparência e o bloco visível da disposição posterior, antes da
renomeação de agosto de 2010. Isso enfraquece a coincidência proposta, mas
não identifica a data real da alteração ou todas as contagens históricas.

## Matriz antiga: fonte escrita preservada em 2008

O índice CDX forneceu capturas de duas páginas do mesmo tópico, ambas em
26/12/2008: [página 3](https://web.archive.org/web/20081226112707id_/http://forum.tibia.org.pl:80/showthread.php?t=265100&page=3)
e [página 47](https://web.archive.org/web/20081226112712id_/http://forum.tibia.org.pl:80/showthread.php?t=265100&page=47).
Os corpos completos foram recebidos e seus SHA-1 em base32 coincidem
exatamente com os digests CDX. A extração recupera:

```text
3 1 6 1
1 2 1 1
1 1 3 1
4 6 1 1
```

As páginas repetem o mesmo primeiro post, atribuído a 10/3/2008, que cita
uma observação comunitária anterior. **É uma única atestação escrita,
preservada em duas páginas; não são duas observações independentes do jogo.**
Ela demonstra que essa tabela circulava antes da renomeação. Não demonstra
que o estado do mapa, em determinada sessão de 2008, tivesse essas contagens.

A primeira resposta arquivada examinada, com timestamp de março de 2008,
tinha HTTP 200, mas era um aviso de login/permissões. Não foi usada como
conteúdo do tópico. A distinção entre resposta válida e evidência relevante
foi preservada; nenhum login foi efetuado.

Os bytes completos das páginas ficam locais, fora do Git. Publicamos URLs,
hashes, registros CDX e somente o excerto numérico, sem republicar os textos.

## Relatos anteriores à renomeação

Uma [mensagem atualmente datada de 9/8/2009](https://torg.pl/tibia/265100-hellgates-library-469-spoilery-46.html#post3485811)
diz que a aparência da matriz havia mudado após um update e que nem todas
as caveiras continuavam visíveis. Ela não fornece uma tabela completa nem
uma data do evento; sua atribuição atual de data não autentica um corpo de
2009. É um relato de aparência, não uma medição antiga de todas as pilhas.

Mais específico, o [post de 10/4/2010](https://torg.pl/tibia/265100-hellgates-library-469-spoilery-58.html#post4148484)
de shoq apresenta o bloco visível:

```text
1 1 1
1 3 6
1 1 4
```

Essa data atribuída antecede 23/8/2010 em **135 dias**. O texto atual também
mostra edição em abril de 2010. Não obtivemos uma cópia arquivada desse
comentário anterior à renomeação, portanto não o promovemos a captura
histórica autenticada. A data do patch continua sendo a âncora já auditada
em fontes de [Bonelord](https://tibia.fandom.com/wiki/Bonelord); não foi
recuperado um novo anúncio primário nesta rodada.

Na [discussão de 11/4/2010](https://torg.pl/tibia/265100-hellgates-library-469-spoilery-59.html),
há correção de uma contagem aparente de cinco para seis e incerteza explícita
na pilha inferior. O registro final apresentado por shoq tem a forma:

```text
1 1 1 1
1 3 6 1
1 1 4 1
4 ? 1 1     ? >= 5, segundo o participante
```

Essa é uma tabela atribuída a um participante, não uma medição nossa.
Não substituímos `?` por 6. Uma publicação posterior, datada de 2016, usa
5 nessa posição, mas seus dois anexos retornaram 404; ela não resolve a
quantidade real ou a época de uma eventual mudança.

Se os relatos de abril preservarem corretamente o estado observado, a
disposição visível já havia mudado **antes** do nome Bonelord. Isso contraria
a associação temporal simples entre as duas matrizes e os dois nomes.
Ainda pode haver ajustes de pilhas ocultas em outras datas. Não concluímos
que a tabela completa posterior, incluindo a pilha inferior de seis, já
estivesse confirmada em abril de 2010.

## Correspondência exata do bloco parcial

Comparamos os nove números transcritos de abril com cada matriz candidata,
permitindo todas as oito rotações/reflexões e os quatro recortes contíguos
3×3 dentro de 4×4. Não há escore de inglês ou reconhecimento automático de
quantidades em imagem.

|Candidata|Posicionamentos compatíveis com o bloco relatado|
|---|---:|
|Antiga fornecida|0|
|Posterior fornecida|1|
|Variante de 2016 com 5 inferior|1|

A incompatibilidade antiga é especialmente simples: qualquer recorte 3×3
de sua grade 4×4 inclui o número 2 interior, ausente do bloco relatado. Isso
também vale após rotações/reflexões. Já o bloco parcial não diferencia as
variantes posteriores com 5 ou 6 na célula inferior não observada.

## O determinante não autentica as contagens duvidosas

Reproduzimos uma observação algébrica da discussão, com código independente.
Defina as posições questionadas como:

```text
M(x,y) = 1 1 1 1
         1 3 x 1
         1 1 4 1
         4 y 1 1
```

**`det M(x,y) = −18` para quaisquer x e y.** O símbolo `x` usado pelo
participante para a pilha inferior corresponde ao nosso `y`; os nomes aqui
servem apenas para distinguir as duas posições.

Uma expansão simbólica pelas 24 permutações cancela todos os termos
variáveis, restando somente −18. A verificação numérica por cofatores,
implementada anteriormente e mantida intacta, concorda nos 121 pares de
0 a 10. A prova geral vem dos coeficientes simbólicos, não dessa amostragem.

Também se pode subtrair a primeira linha das demais e expandir pela última
coluna: o determinante passa a ser o negativo de
`det[[0,2,x−1],[0,0,3],[3,y−1,0]]`, ou seja, −18.

O total das entradas é `22+x+y`. Uma soma de 34 exige x+y=12, sem determinar
o par; se x=6 já estiver confirmado, então y=6. O determinante constante não
escolhe esses valores nem certifica a matriz completa. Não usamos essa
ambiguidade para ajustar novas chaves a inglês.

## Duas imagens inspecionadas, datas com papéis diferentes

Obtivemos e examinamos o arquivo [Hellgate Misterio02.jpg](https://www.tibiawiki.com.br/wiki/Arquivo:Hellgate_Misterio02.jpg)
e a [imagem usada por s2ward](https://user-images.githubusercontent.com/25346191/160277253-fe60dbf6-00f9-48fc-bcea-1f3bf004c9d0.png).
As duas mostram a sala com lava e barreiras de ossos. A visão parcial não
fornece contagem confiável de todas as 16 células nem mensagens de LOOK
que resolvam cada pilha; não extraímos delas uma chave completa.

|Registro|Data disponível|Papel dessa data|
|---|---|---|
|Histórico público da wiki|1/1/2014|Upload atribuído pelo servidor; uma entrada retornada|
|Mesmo JPEG, cabeçalho HTTP|12/3/2015|Last-Modified do arquivo servido|
|PNG hospedado no GitHub|27/3/2022|Last-Modified HTTP|
|Captura efetiva no jogo|Desconhecida|Não deve ser substituída por nenhuma das anteriores|

O SHA-1 do JPEG recebido coincide com o informado no histórico da wiki,
vinculando os bytes à entrada consultada. Isso não fornece versão do cliente,
data da sessão ou procedência suficiente para autenticar o estado autoral.

O tutorial encontrado com publicação em 30/4/2010 tem edição atribuída a
29/8/2010, depois da renomeação; seu mapa vinculado retornou 404. Ele não
forneceu uma captura utilizável anterior ao patch.

## O que foi estabelecido e o que permanece aberto

- **Demonstrado como história documental:** a tabela antiga consta em
  payloads arquivados de 2008 com integridade conferida no CDX.
- **Evidência circunstancial contrária à coincidência:** relatos atribuídos
  a 2009/abril de 2010 já falam em mudança e descrevem o bloco posterior.
- **Demonstrado matematicamente:** o bloco relatado é incompatível com a
  matriz antiga, e −18 não identifica as duas contagens questionadas.
- **Em aberto:** data real da mudança, todas as quantidades, eventual
  alteração dos livros na mesma época e papel criptográfico da matriz.

Não delimitamos a mudança como ocorrida entre 2008 e 2010: a fonte de 2008
é uma citação de tabela, não uma observação datada do mapa ainda antigo.
Também não encontramos um novo par número/inglês atestado ou algoritmo de
tradução. A hipótese temporal perdeu apoio; não foi substituída por outra
ligação causal sem evidência. As quatro entregas principais continuam abertas.

## Coleta e reprodução

Foram preservadas 27 coletas HTTP explícitas: 21 retornaram 200, três 404 e
três 503. Entre os 200 há um aviso de permissões, distinguido de conteúdo.
Consultas arquivísticas de escopo mais amplo ficaram em 503; listas vazias
e indisponibilidade não provam inexistência de outras capturas.

```sh
make round14
make test
# Com as capturas locais originais, verificar novamente bytes e extração:
python scripts/history_round14_build.py --check
```

O verificador offline repete a álgebra, a comparação de grades e a coerência
dos registros de fontes. Se os corpos locais estiverem presentes, também
recalcula seus hashes e extrai novamente os dados. Em clone/backup sem esses
corpos, ele informa explicitamente que não releu HTML ou imagens.

`history_source_fetch.py` permite coletas opcionais em novos lotes, com
timeout, limite de tamanho e preservação dos anteriores. Não republicamos
as páginas completas ou imagens no Git. URLs, papéis de datas, hashes e
resultados estão em `data/history_round14_sources.json`,
`data/history_round14_http_manifest.json` e `results/history_round14_analysis.json`.
