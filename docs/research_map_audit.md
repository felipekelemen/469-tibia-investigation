# Auditoria da pista de mapas históricos do Deep Research

**A fonte sugerida não permite extrair object IDs nem quantidades de caveiras.**
Inspecionamos o repositório [tibiamaps/tibia-historical-map-data](https://github.com/tibiamaps/tibia-historical-map-data)
no commit`8885f3f3fb103cd47f8944df77f06868ee025d5d`, através da API GitHub.
A raiz contém apenas versões7.3,7.4,7.5,7.7 eREADME. A pasta7.7 contém16
arquivos`floor-00-map.png`a`floor-15-map.png`: camadas de minimapa. Não há
pastas8.60–8.70, banco de objetos, item IDs ou stack counts nesse snapshot.

O [guia do formato Automap](https://tibiamaps.io/guides/map-file-format)
distingue pixels de cores, custo de percurso e marcadores; o
[guia dos PNGs modernos](https://tibiamaps.io/guides/minimap-file-format)
descreve a mesma representação de minimapa. Isso serve para geometria,
localização e topologia de áreas, não para recuperar inventário de objetos
por célula. Um sprite e sua definição no cliente também não fornecem o estado
original dos objetos colocados numa sala. Arquivos de cliente não equivalem
a um mapa autoral com posições, pilhas e quantidades.

O README atribui os PNGs7.7 a arquivos oficiais vazados, mas **a derivação não
inclui automaticamente esses arquivos-fonte**. Não adquirimos nem auditamos
esse material. O objetivo sugerido pelo Deep Research—extrair object IDs,
posições e stack counts desse repositório—deve ser corrigido antes de investir
em download ou parser. Não auditamos todos os commits/forks; esta conclusão
é sobre o snapshot examinado.

## Cronologia: fontes primárias e suas limitações

A busca recuperou texto indexado do domínio oficial para
[Content Fixes and Changes,23/08/2010](https://www.tibia.com/news/?id=1437&subtopic=newsarchive),
que anuncia Beholder→Bonelord e faz a alusão conhecida. O acesso direto
retornou403. Esse resultado fortalece a origem oficial da data antes preservada
apenas via wiki em nossa pesquisa; não demonstra mudança da matriz.

Também foi localizado texto indexado do anúncio oficial
[Major Game Update8.7,08/12/2010](https://www.tibia.com/news/?id=1557&subtopic=newsarchive).
Ele estabelece a data de lançamento, mas o corpo indexado consultado **não
menciona Hellgate ou caveiras**. A associação de Hellgate à reforma8.7 aparece
na [cronologia comunitária](https://tibia.fandom.com/wiki/Updates).
Portanto a formulação de que o anúncio primário comprova a reforma específica
da matriz é forte demais. O
[teaser oficial de11/11/2010](https://www.tibia.com/news/?id=1525&subtopic=newsarchive)
menciona residências de bonelords em Drefia e Necropolis; isso não identifica
por si só a sala, a contagem ou a data da edição das caveiras.

Entre23/08 e08/12 há**107dias**, e não simultaneidade. Mesmo esse intervalo
separa dois eventos gerais; só será intervalo da mudança da matriz se uma
fonte independente demonstrar quando a matriz mudou.

## Experimento histórico viável

Buscar captura/vídeo datável antes de23/08/2010, entre23/08 e08/12, e depois
de08/12; registrar versão, coordenadas, câmera, cobertura de cada célula,
possibilidade de objetos móveis e caveiras escondidas atrás de pilares.
Se existir extrato autorizado e autenticável de mapa **com objetos**, comparar
as células por item ID específico da versão e quantidade, documentando formato.
Minimapas permanecem auxiliares de localização, não prova das contagens.

URLs, IDs de versão, estados de acesso e limites estão em
`results/research_map_audit.json`. Esta auditoria altera o planejamento de
fontes; não executa outra cifra nem fornece tradução.
