# Roadmap

## Fase 0 — Território, direção e acervo existente

**Estado: concluída como investigação inicial.**

Foram analisados o ecossistema de sustentabilidade, os canais de propagação, as infraestruturas existentes, os agregadores, as analogias com funding intelligence, procurement intelligence, OSINT e research intelligence, além do encaixe com TraceFoundry e `pncp-data-pipeline`.

A conclusão operacional foi refinada: o Lux Radar é inicialmente uma **máquina de aquisição, observação, evidência e releases versionados**. A oportunidade canônica e o radar visual são camadas que dependem dessa base.

## Fase 1 — Mapa de 20 fontes

**Estado: concluída como levantamento inicial; precisa de validação por collector.**

O inventário em [SOURCE_INVENTORY.md](SOURCE_INVENTORY.md) reúne 20 fontes e classifica superfície, acesso, risco de atualização, relação com parceiros e prioridade. O mapa diferencia API, CSV, HTML, PDF, feed, sitemap, portal dinâmico, parceiro, comunicação editorial e sinal humano.

O inventário não presume API, licença ou estabilidade. Cada fonte precisa ganhar uma ficha de fonte antes de entrar em observação recorrente.

## Fase 2 — Escolha de três perfis e fichas de fonte

**Estado: seleção inicial realizada.**

O piloto usará três perfis radicalmente diferentes:

| Perfil | Fonte | Prova que precisamos obter |
|---|---|---|
| API/JSON/CSV | Transferegov | Paginação, filtros, resposta estruturada, limites e release reproduzível. |
| HTML + PDF + errata | FAPESB | Listagem, detalhe, documento, retificação, mudança de prazo e limitação. |
| Programa + parceiro + chamada territorial | BNDES/Floresta Viva | Relação entre programa, Funbio, chamada, território, bioma, prazo e fonte final. |

Antes do código definitivo, criar uma ficha para cada uma com URL, método, frequência, termos, campos, falhas esperadas, estratégia de snapshot e critério de sucesso.

## Fase 3 — Collectors mínimos

**Estado: concluída como prova inicial; operação recorrente ainda não iniciada.**

Implementar três collectors isolados, um por perfil. Cada collector deve:

1. observar apenas conteúdo público e permitido;
2. registrar início, fim, status, método e erro;
3. preservar URL, content type, hash quando possível e timestamp;
4. produzir observações compatíveis com `source-observation.schema.json`;
5. não produzir oportunidades canônicas prematuras;
6. tornar falhas, bloqueios e observações parciais visíveis;
7. ter fixture ou mock mínimo para teste sem rede.

O código operacional deve viver no repositório privado de aquisição. O repositório público mantém contratos, fixtures sanitizadas, documentação, exemplos e testes sem segredo.

## Fase 4 — Primeiro release

**Estado: concluída como release privado de prova (`2026-08-25-pilot-007`).**

Gerar um release pequeno e versionado com `release-manifest.schema.json`, contendo:

- três `source_ids`;
- janela de observação;
- contagem de observações, evidências, oportunidades e falhas;
- produtor e versão dos collectors;
- referências de artefatos;
- hashes e limitações quando disponíveis;
- versão dos schemas usados.

O release `2026-08-25-pilot-007` produziu 7 observações, 5 evidências, 2 registros normalizados, 2 oportunidades e 1 falha explícita, além de um diff temporal cross-surface. Ele é reproduzível a partir do commit, da configuração e das entradas permitidas; dados brutos grandes ou sensíveis não entram no Git público.

## Fase 5 — Normalização e ponte para o TraceFoundry

Mapear observações para registros comparáveis e, quando houver evidência suficiente, para `OpportunityRecord`. A ponte deve preservar o original, a transformação, o `release_id`, o `source_id` e a evidência de cada campo importante.

Não reescrever o TraceFoundry. Não duplicar a coleta do `pncp-data-pipeline`. Definir interfaces entre repositórios quando a necessidade aparecer no experimento.

## Fase 6 — Experimento de sinal para oportunidade

Depois de provar a aquisição, reconstruir 10–20 oportunidades reais que cruzaram a rede. Cada caso deverá registrar sinal, resolução de fonte, observações, evidências, oportunidade canônica, manifestações, status, contexto, ação e resultado.

O conjunto deve aceitar sinal falso, fonte não encontrada, evidência insuficiente, oportunidade encerrada, duplicata e baixa relevância.

## Fase 7 — Primeira entrega útil

Produzir uma resposta ou tela simples que mostre, para uma observação ou sinal:

- registro ou oportunidade identificada;
- status de verificação;
- prazo e público-alvo;
- território e temas;
- motivo da relevância;
- evidências e fonte primária;
- data da última verificação;
- incertezas e limitações;
- próximo passo possível.

## Fase 8 — Medição e expansão

Medir sucesso por fonte, cobertura observada, latência de coleta, mudanças detectadas, falhas, estabilidade do schema, taxa de duplicação, precisão do matching, taxa de ação e tempo economizado.

Somente depois considerar novas fontes, eventos, pesquisa, inovação, turismo, cultura, clima, educação, procurement, alertas e distribuição via parceiros.

## Itens explicitamente adiados

- crawler universal;
- ingestão de WhatsApp em produção;
- grafo dedicado;
- streaming com Kafka/NATS;
- rotação de proxies;
- matching autônomo sem revisão;
- redistribuição comercial de dados de terceiros;
- banco nacional universal;
- promessas de cobertura ou precisão sem medição;
- interface pública sofisticada antes de provar releases confiáveis.
