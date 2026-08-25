# Arquitetura inicial

## 1. Princípio

O Lux Radar será organizado como uma camada pública de composição e inteligência sobre fontes e componentes existentes. O núcleo público deve privilegiar **catálogo de fontes, observação reproduzível, evidência, proveniência, releases versionados, seleção explicável e experimentos auditáveis**.

A coleta não é uma camada única. O sistema precisa lidar com diferentes superfícies e métodos sem fingir que elas têm a mesma estrutura.

```text
SOURCE REGISTRY
  ├── API / JSON / CSV
  ├── HTML / PDF / ERRATA
  ├── FEED / SITEMAP / NEWSLETTER
  ├── PORTAL DINÂMICO / EVENT PAGE
  └── HUMAN SIGNAL
          ↓
   SOURCE OBSERVATION
          ↓
      EVIDENCE
          ↓
  VERSIONED RELEASE
          ↓
  NORMALIZED RECORDS
          ↓
CANONICAL OPPORTUNITY
          ↓
 CONTEXT / MATCHING
          ↓
    DELIVERY / ACTION
```

Um sinal humano pode entrar no mesmo sistema por outra rota:

```text
SIGNAL
  → SOURCE RESOLUTION
  → SOURCE OBSERVATION
  → EVIDENCE
  → CANONICAL OPPORTUNITY
```

## 2. Componentes existentes

### TraceFoundry

O TraceFoundry deve ser tratado como infraestrutura epistemológica reutilizável. Seus conceitos de adapter, registro canônico, seleção explicável, manifest, evidência, estado de investigação e Research Move são compatíveis com a passagem de observação para registro verificado.

O primeiro trabalho de integração não deve reescrever o TraceFoundry. Deve mapear o que o Lux Radar precisa para contratos de `SourceObservation`, `EvidenceRecord`, `ReleaseManifest` e `OpportunityRecord`, preservando os contratos existentes quando fizer sentido.

### pncp-data-pipeline

O pipeline PNCP permanece como sistema de coleta e preservação da fonte PNCP. O Lux Radar não deve copiar Parquets privados nem reproduzir a coleta. Ele será usado como **referência operacional** de aquisição, validação, releases, integridade e checkpoints.

Quando o domínio exigir contratos ou compras públicas, o radar deverá consumir releases, manifestos ou recortes normalizados conforme a interface que for definida entre os repositórios. A ausência dessa interface é uma lacuna de integração a documentar, não uma justificativa para iniciar outro pipeline paralelo.

### Interfaces existentes

Os repositórios `Radar-Contratos-BA`, `explorador-dados-bahia`, `monitor-gastos-pncp` e `gastos-eventos-ba` são referências de apresentação e exploração. Eles podem contribuir com componentes visuais, filtros, narrativas e padrões de comunicação, mas não devem ser tratados como camada canônica de aquisição.

## 3. Camadas do Lux Radar

| Camada | Responsabilidade | Estado inicial |
|---|---|---|
| Source registry | Declarar identidade, URL, perfil, frequência, termos e estratégia de cada fonte | Inventário de 20 fontes |
| Collector | Acessar uma superfície por método declarado, sem misturar credenciais ou dados privados | Três protótipos isolados |
| Source observation | Registrar momento, método, status, conteúdo, hash, claims e limitações | Schema público |
| Evidence | Ligar uma afirmação ou atributo ao artefato observável | Contrato público |
| Release manifest | Versionar janela de observação, contagens, produtor, schemas e artefatos | Schema público |
| Normalization | Mapear observações para campos comparáveis sem apagar os originais | Adapter por fonte |
| Canonical record | Representar oportunidade sem duplicar manifestações | Schema e fixtures |
| Provenance | Explicar origem, transformação e sustentação de cada campo importante | Compatível com TraceFoundry |
| Status | Distinguir aberto, encerrado, alterado, não verificado e insuficiente | Regras explícitas |
| Deduplication | Agrupar manifestações da mesma entidade sem apagar aliases | Heurística auditável |
| Context | Relacionar tema, território, público e perfil | Inicialmente manual/declarativo |
| Delivery | Produzir relatório, JSON, consulta ou alerta | Saída de experimento |

## 4. Contratos e fluxo de dados

Cada collector deve produzir uma observação conforme `schemas/source-observation.schema.json`. Um conjunto de observações bem-sucedidas, parciais ou falhas é reunido por `schemas/release-manifest.schema.json`.

```text
collector
  → observation.json
  → evidence references
  → release manifest
  → normalized record
  → optional opportunity record
```

A oportunidade canônica não é obrigatória em toda observação. Uma fonte pode produzir apenas um sinal, uma alteração, um documento ou uma evidência insuficiente.

## 5. Modelo de estados

O sistema não deve colapsar todos os resultados em `found` ou `not found`. Os estados iniciais sugeridos são:

```text
registered_source
observation_pending
observed
partial_observation
blocked
failed
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

## 6. Proveniência mínima

Cada observação ou registro canônico deve conseguir responder:

1. Qual fonte foi observada?
2. Qual URL, endpoint ou documento foi acessado?
3. Quando e por qual método?
4. Qual foi o status da coleta?
5. Qual evidência sustenta cada atributo importante?
6. Qual versão, hash ou release foi usado?
7. Qual transformação foi aplicada?
8. O que permanece incerto ou fora do escopo?
9. Quais manifestações ou registros foram relacionados?

A proveniência é por campo quando possível. Uma URL geral não deve ser apresentada como prova automática de todos os atributos.

## 7. Deduplicação inicial

A primeira versão deve ser determinística e auditável. Uma possível ordem de comparação é:

1. identificador oficial ou número do edital, quando existir;
2. URL canônica e URL do documento;
3. organização promotora normalizada;
4. título normalizado;
5. prazo e janela temporal;
6. território e tipo;
7. similaridade semântica apenas como apoio à revisão.

Nenhum agrupamento automático deve apagar a manifestação original. A relação deve registrar o motivo, a confiança e a possibilidade de revisão humana.

## 8. O que fica fora do primeiro estágio

Não fazem parte do primeiro estágio: Neo4j, Kafka/NATS, bot de WhatsApp, scraping em escala, rotação de proxies, matching autônomo de alto risco, ingestão de dados privados, redistribuição automática de conteúdo protegido ou banco universal de oportunidades.

Também não serão armazenados no repositório público tokens, cookies, Parquets operacionais, dumps integrais de terceiros ou conversas privadas. Snapshots públicos só entram quando houver justificativa de licença, tamanho e segurança.

## 9. Evolução prevista

A evolução ocorrerá por adapters e contratos isolados:

```text
source registry
  → collector
  → raw observation metadata
  → evidence
  → release manifest
  → normalization
  → canonical opportunity
  → selection
  → review
  → delivery
```

A arquitetura deve permanecer compatível com o TraceFoundry e com releases externos, sem acoplar o domínio de sustentabilidade a uma única fonte ou fornecedor.
