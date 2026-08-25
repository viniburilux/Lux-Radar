# Arquitetura Inicial

## 1. Princípio

O Lux Radar será organizado como uma camada de composição e inteligência sobre fontes e componentes existentes. O núcleo público deve privilegiar contratos, evidência, proveniência, seleção explicável e experimentos reproduzíveis.

```text
ECOSSISTEMA
  ├── fontes institucionais
  ├── APIs e datasets
  ├── páginas e PDFs
  ├── newsletters e eventos
  └── sinais humanos
          ↓
DISCOVERY / INGESTION
          ↓
SIGNAL RECORD
          ↓
SOURCE DISCOVERY
          ↓
EVIDENCE + PROVENANCE
          ↓
CANONICAL OPPORTUNITY
          ↓
DEDUPLICATION / STATUS
          ↓
CONTEXT / MATCHING
          ↓
DELIVERY / ACTION
```

## 2. Componentes existentes

### TraceFoundry

O TraceFoundry deve ser tratado como infraestrutura epistemológica reutilizável. Seus conceitos de adapter, registro canônico, seleção explicável, manifest, evidência, estado de investigação e Research Move são compatíveis com a passagem de sinal para oportunidade verificada.

O primeiro trabalho de integração não deve reescrever o TraceFoundry. Deve mapear o que o Lux Radar precisa para um contrato de `SignalRecord`, `EvidenceRecord` e `OpportunityRecord`, preservando os contratos existentes quando fizer sentido.

### pncp-data-pipeline

O pipeline PNCP permanece como sistema de coleta e preservação da fonte PNCP. O Lux Radar não deve copiar Parquets privados nem reproduzir a coleta. Quando o domínio exigir contratos ou compras públicas, o radar deverá consumir releases, manifestos ou recortes normalizados conforme a interface que for definida entre os repositórios.

O ponto de integração prioritário é um recorte normalizado que carregue `dataset_release`, fonte, método, chave territorial, limitações e rota de proveniência. A ausência desse contrato deve ser tratada como uma lacuna de integração, não como justificativa para iniciar outro pipeline.

### Interfaces existentes

Os repositórios `Radar-Contratos-BA`, `explorador-dados-bahia`, `monitor-gastos-pncp` e `gastos-eventos-ba` são referências de apresentação e exploração. Eles podem contribuir com componentes visuais, padrões de narrativa, filtros e formas de comunicar dados, mas não devem ser tratados como a camada canônica de ingestão.

## 3. Camadas do Lux Radar

| Camada | Responsabilidade | Estado inicial |
|---|---|---|
| Signal intake | Receber texto, link, documento ou sinal humano sanitizado | Fixture e importação manual |
| Discovery | Encontrar a fonte primária ou registrar que ela não foi encontrada | Procedimentos reproduzíveis; adapters depois |
| Evidence | Guardar URL, tipo, data, versão, hash quando possível e limitações | Contrato público |
| Canonical record | Representar a oportunidade sem duplicar manifestações | Schema e fixtures |
| Provenance | Explicar de onde veio cada campo e qual observação o sustenta | Compatível com TraceFoundry |
| Status | Distinguir aberto, encerrado, alterado, não verificado e insuficiente | Regras explícitas |
| Deduplication | Agrupar manifestações da mesma oportunidade sem apagar aliases | Primeiro heurística auditável |
| Context | Relacionar tema, território, público e perfil | Inicialmente manual ou declarativo |
| Delivery | Produzir relatório, JSON, consulta ou alerta | Saída de experimento |

## 4. Modelo de estados

O sistema não deve colapsar todos os resultados em `found` ou `not found`. Os estados iniciais sugeridos são:

```text
received_signal
candidate
source_not_found
source_found
verification_pending
verified_primary
insufficient_evidence
expired
superseded
duplicate
rejected
ready_for_action
```

`source_not_found` não significa que a oportunidade não existe. Significa que a investigação não localizou uma fonte primária suficiente dentro do escopo e do momento registrados.

## 5. Proveniência mínima

Cada registro canônico deve conseguir responder:

1. Qual foi o sinal inicial?
2. Qual fonte primária foi localizada?
3. Qual evidência sustenta cada atributo importante?
4. Quando a evidência foi observada?
5. Qual versão ou snapshot foi usado?
6. O que permanece incerto?
7. Qual foi a transformação aplicada?
8. Quais manifestações secundárias foram relacionadas?

A proveniência é por campo quando possível. Uma URL geral não deve ser apresentada como prova automática de todos os atributos do registro.

## 6. Deduplicação inicial

A primeira versão deve ser determinística e auditável. Uma possível ordem de comparação é:

1. identificador oficial ou número do edital, quando existir;
2. URL canônica e URL do documento;
3. organização promotora normalizada;
4. título normalizado;
5. prazo e janela temporal;
6. território e tipo;
7. similaridade semântica apenas como apoio à revisão.

Nenhum agrupamento automático deve apagar a manifestação original. A relação deve registrar o motivo, a confiança e a possibilidade de revisão humana.

## 7. O que fica fora do primeiro estágio

Não fazem parte do primeiro estágio: Neo4j, Kafka/NATS, bot de WhatsApp, scraping em escala, rotação de proxies, matching autônomo de alto risco, ingestão de dados privados, redistribuição automática de conteúdo protegido ou banco de dados universal de oportunidades.

Esses itens podem aparecer como decisões futuras, mas somente após um experimento demonstrar que a camada atual não resolve o caso.

## 8. Evolução prevista

A evolução deverá ocorrer por adapters e contratos isolados:

```text
adapter de fonte
  → observação bruta
  → normalização
  → evidência
  → registro canônico
  → seleção explicável
  → manifest
  → revisão
```

A arquitetura deve permanecer compatível com o TraceFoundry e com releases externos, sem acoplar o domínio de sustentabilidade a uma única fonte ou fornecedor.
