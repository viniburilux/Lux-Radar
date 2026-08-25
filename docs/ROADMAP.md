# Roadmap Inicial

## Fase 0 — Território e direção

**Estado: concluída como investigação inicial.**

Foram analisados o ecossistema de sustentabilidade, os canais de propagação, as infraestruturas existentes, os agregadores, as analogias com funding intelligence, procurement intelligence, OSINT e research intelligence, além do encaixe com TraceFoundry e pncp-data-pipeline.

A conclusão operacional é que o núcleo do problema é transformar sinais em oportunidades verificadas, não simplesmente coletar links.

## Fase 1 — Reconstrução de casos reais

**Estado: próxima execução.**

Selecionar 10–20 oportunidades reais que cruzaram a rede e criar um registro por caso. O conjunto deve incluir variedade suficiente para revelar o contrato comum e as exceções.

Cada caso deverá registrar:

```text
signal
source_discovery
primary_source
evidence
canonical_opportunity
secondary_manifestations
status
context
match
action
```

O resultado esperado é uma coleção de casos, não um sistema automatizado.

## Fase 2 — Contratos e schemas

Depois de observar os casos, consolidar os schemas de `Signal`, `Evidence`, `Opportunity` e, se necessário, `Manifest`, `Claim` e `Action`. A regra é não criar campos abstratos sem um caso que os justifique.

O contrato deve preservar:

- identificadores e URLs;
- fonte primária e fontes secundárias;
- datas de publicação, descoberta, atualização e verificação;
- status e incerteza;
- elegibilidade, território, tema e prazo;
- relação entre sinais, evidências e oportunidade;
- método e limitações.

## Fase 3 — Adapter e validação

Mapear os contratos para o TraceFoundry sem reescrever seu núcleo. Criar uma primeira entrada manual ou adapter simples para transformar um caso em manifest verificável.

Quando o caso for de contratos ou compras públicas, avaliar a ponte com releases do `pncp-data-pipeline`. Não copiar dados privados nem criar uma nova coleta paralela.

## Fase 4 — Primeira entrega útil

Produzir uma resposta ou tela simples que, dado um sinal, mostre:

- oportunidade identificada;
- status de verificação;
- prazo e público-alvo;
- território e temas;
- motivo da relevância;
- evidências e fonte primária;
- data da última verificação;
- incertezas e limitações;
- próximo passo possível.

O objetivo é comparar essa saída com o simples encaminhamento de um link.

## Fase 5 — Medição

Medir latência de descoberta e verificação, taxa de sinais falsos, duplicidades, precisão do matching e ações geradas. O produto só deve evoluir para automação quando esses dados mostrarem uma dor recorrente e uma melhoria mensurável.

## Fase 6 — Adapters e distribuição

Adicionar fontes públicas isoladamente, começando pelas que têm valor para o domínio e contratos de acesso claros. Depois avaliar API, feed, dashboard, alertas ou distribuição via parceiros.

## Fase 7 — Expansão

Somente após validar o primeiro domínio, considerar eventos, pesquisa, inovação, turismo, cultura, clima, educação, procurement e outros segmentos. A expansão deve reutilizar o núcleo de proveniência e registro canônico, alterando apenas taxonomias, adapters e regras de contexto quando possível.

## Itens explicitamente adiados

- crawler universal;
- ingestão de WhatsApp em produção;
- grafo dedicado;
- streaming com Kafka/NATS;
- rotação de proxies;
- matching autônomo sem revisão;
- redistribuição comercial de dados de terceiros;
- banco nacional universal;
- promessas de cobertura ou precisão sem medição.
