# Fontes e atribuições

- Arturo Ornelas: https://github.com/arturoornelasb/tibia-bonelord-469-cipher — MIT; corpus, mapa v7, alegação de solução e validator reproduzido.
- s2ward e colaboradores: https://github.com/s2ward/469 — corpus, alinhamentos e coleta de pistas; não atribuímos licença MIT a conteúdo upstream sem licença específica.
- Kim de Amorim Lage: https://github.com/kimlage/tibia-469-cipher-casestudy — MIT com NOTICE para materiais de terceiros; streams tokenizados e tabela row0 empregados com atribuição.
- Tibia e seus livros/diálogos: CipSoft GmbH. Reprodução de pequenas fontes textuais para pesquisa, sem reivindicação de autoria ou afiliação.
- Tibia Wiki BR, TibiaSecrets, arquivos históricos: links, hashes, datas de coleta e condições HTTP em data/historical_sources/manifest.json. Ver docs/history.md para o alcance real das fontes acessíveis.
- Referência inglesa: Lewis Carroll, Alice's Adventures in Wonderland, Project Gutenberg; texto e metadados em data/english_reference. Material auxiliar de pontuação, não par cifra/plaintext.
- Avaliação lexical da sexta rodada: Frances Hodgson Burnett, *The Secret Garden*; P.G. Wodehouse, *My Man Jeeves*; L. Frank Baum, *The Wonderful Wizard of Oz*; J.M. Barrie, *Peter Pan*. Fontes Project Gutenberg completas, com termos/cabeçalhos preservados, URLs e hashes em `data/word_validator_reference/SOURCES.json`. Treino e qualificação têm papéis separados; não são traduções de Tibia.
- Qualificações de segmentação da sétima rodada: Robert Louis Stevenson, *Treasure Island*, e Jack London, *The Call of the Wild* (V1); Lucy Maud Montgomery, *Anne of Green Gables*, e Joseph Conrad, *The Secret Agent* (V2). Project Gutenberg, fontes e termos completos preservados. URLs, papéis e hashes em `data/raw_parser_reference/SOURCES.json` e `data/raw_parser_reference_v2/SOURCES.json`. Usados para cifras sintéticas com respostas conhecidas, sem pares de tradução de 469.
- Auditoria de metadados da nona rodada: snapshots pequenos de Arturo, no commit fixado em `sources/manifest.json`, preservados em `data/metadata_reference/arturo/` com licença MIT. Dígitos de livros continuam material de Tibia/CipSoft. Tibia Wiki BR forneceu corroboração textual indexada; TibiaCams forneceu metadados e uma tentativa bloqueada de playback. Fontes, método e limites em `docs/round9.md`; nenhum asset do cliente ou renderer foi redistribuído.

Os commits exatos e hashes dos três repositórios estão em sources/manifest.json.
Capturas completas de páginas de terceiros são mantidas apenas localmente;
metadados suficientes para localizar e auditar as referências são versionados.
