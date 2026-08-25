# Interface futura com `pncp-data-pipeline`

## Objetivo

O `pncp-data-pipeline` continua sendo a autoridade operacional para coleta, validação, releases, Parquet e integridade do domínio PNCP. O Lux Radar consome uma interface segura e versionada para transformar dados de contratos ou compras públicas em inteligência de oportunidade/contract intelligence.

```text
pncp-data-pipeline
        ↓
release / interface pública ou autorizada
        ↓
Lux Radar SourceObservation / NormalizedRecord
        ↓
OpportunityRecord ou ContractRecord
        ↓
TraceFoundry selection / investigation / review
```

## O que o pipeline consumidor precisa receber

A interface mínima deve carregar metadados de release, não exigir acesso ao armazenamento privado:

| Campo | Necessidade |
|---|---|
| `release_id` | Identificar a versão consumida. |
| `created_at` | Saber quando o release foi gerado. |
| `source_system` | Declarar PNCP e módulo correspondente. |
| `observation_window` | Saber o período observado. |
| `dataset_release` | Rastrear a release original do pipeline. |
| `schema_version` | Validar compatibilidade. |
| `record_ref` | Referenciar o registro ou artefato permitido. |
| `content_hash` | Conferir integridade sem copiar o arquivo inteiro. |
| `territory_key` | Filtrar UF, município ou órgão. |
| `limitations` | Preservar cobertura, atraso, falhas e escopo. |

## Formas possíveis de integração

A forma concreta ainda não foi decidida. A ordem de preferência é:

1. manifest seguro + recorte pequeno e autorizado;
2. exportação CSV/JSON com schema versionado;
3. API interna ou endpoint autenticado com escopo mínimo;
4. acesso a release em storage autorizado;
5. consulta a Parquet privado apenas no ambiente original, sem cópia para o Lux Radar.

O Lux Radar não deve fazer scraping do output do pipeline nem depender de caminhos locais frágeis.

## Mapeamento de domínio

| PNCP | Lux Radar | Decisão |
|---|---|---|
| Release do pipeline | `ReleaseManifest` | Reuse/adaptar metadata |
| Registro de contratação | `NormalizedRecord` ou futuro `ContractRecord` | Adaptar sem perder campos PNCP |
| Órgão/ente | `issuer`/publisher | Mapear identificador e nome |
| Objeto da contratação | Claim de registro | Preservar texto original e transformação |
| UF/município | `geography`/`territories` | Mapear chave territorial |
| Data de publicação | `publication_date` | Referenciar campo original |
| Valor | `funding` ou campo de contrato | Não confundir preço contratado com grant |
| URL PNCP | `official_url`/evidence | Preservar fonte primária |
| Hash/checkpoint | Provenance/release artifacts | Reutilizar integridade |

## Primeiro fixture seguro

O primeiro fixture público deve ser pequeno, sintético ou autorizado, contendo um manifest e poucos registros sem PII. Ele deve testar apenas a ponte de contrato:

```json
{
  "dataset_release": "pncp-example-release",
  "schema_version": "0.1.0",
  "source_system": "pncp",
  "record_ref": "example-contract-001",
  "content_hash": "sha256:example",
  "territory_key": "BA",
  "limitations": ["sanitized fixture"]
}
```

Esse fixture não autoriza publicar Parquet nacional, dados de parceiros ou material sujeito a termos incompatíveis.

## Critério de integração

A integração estará pronta quando um release permitido do `pncp-data-pipeline` puder ser lido pelo Lux Radar com `release_id`, hash, janela, schema, registros e limitações preservados, e quando a origem de cada campo relevante puder ser rastreada até o release original.
