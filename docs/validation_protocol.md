# Protocolo de validação e limites desta rodada

1. Fontes, hashes, normalização e convenções são versionados. Rótulos de camada intermediária não recebem significado por presunção.
2. O grafo de trechos compartilhados define grupos; splits aleatórios por livro não são admitidos como independência. Veja corpus.md.
3. Pontuadores externos são congelados sem treinamento nos candidatos. A seleção de chave/variante ocorre só em descoberta quando aplicável. Os testes matriciais de todo corpus são explicitamente exploratórios.
4. Repete-se a seleção de candidatos dentro de cada controle para comparar máximos, com as limitações da busca homofônica documentadas. Usa-se `(1+n_extremos)/(1+n_controles)`, nunca p=0.
5. Controles preservam progressivamente frequências, códigos, blocos ou igualdade de fragmentos; controles uniformes têm baixo poder para discriminar linguagem de repetição.
6. A reconstrução5729 já foi produzida usando todo o corpus upstream. Os splits locais não tornam essa escolha global retrospectivamente independente. O pontuador de inglês não equivale a julgamento semântico nem a tradução atestada.
7. Não há plaintext oficial dos livros à disposição. Todos os resultados desta rodada são auditorias estruturais ou triagem de hipóteses. Nenhum escore isolado satisfaz o critério de sucesso.
8. Uma promoção futura requer algoritmo integral sem reparos por item, texto inglês coerente longo em fragmento externo não utilizado, comparação com texto atestado quando disponível, falhas e exceções registradas e replicação por implementação independente.
9. Não se pode demonstrar a inexistência de qualquer mensagem oculta pela falha de uma lista finita de cifras. Também não se deve declarar solução com palavras curtas, anagramas livres ou cobertura de dicionário.

Esta rodada mantém contagem de traduções verificadas: **0**. Quantidade de
scripts, candidatos e iterações não é medida de avanço semântico.
