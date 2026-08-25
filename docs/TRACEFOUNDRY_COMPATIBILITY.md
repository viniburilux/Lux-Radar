# Compatibilidade Lux Radar × TraceFoundry

## Princípio

O Lux Radar não deve criar uma segunda epistemologia. Ele deve produzir observações, evidências, registros normalizados e oportunidades de domínio; o TraceFoundry fornece conceitos reutilizáveis para descoberta, seleção explicável, manifestos, estados de investigação e movimentos de pesquisa.

| Conceito Lux Radar | Conceito TraceFoundry | Decisão | Justificativa |
|---|---|---|---|
| Source | `Source adapter`, `DatasetRecord`, `AssetRecord` | **ADAPT** | O TraceFoundry descreve fontes e assets de pesquisa/dados; o Lux Radar precisa declarar superfícies de oportunidade como API, HTML, PDF, portal, feed e sinal humano. Reutilizar identidade, URL, versão, acesso, licença e warnings. |
| Source Registry | `DiscoveryQuery.source`, catálogo/adapters | **ADAPT** | O Lux Radar precisa de um catálogo operacional com frequência, termos, método e risco por fonte. A intenção de consulta do TraceFoundry é reutilizável; o registro de operação é específico do radar. |
| Observation | `Source response` / observação de discovery | **ADAPT** | Reutilizar timestamp, fonte, resposta, warnings e metadata-only. Adaptar para status HTTP, perfil de superfície, claims, hash e falhas de collector. |
| Evidence | `Evidence evaluation`, public evidence references | **REUSE + ADAPT** | Reutilizar a ideia de evidência pública ligada a claims e limitações. Adaptar `evidence_type` para página oficial, PDF, API response, comunicado e documento de chamada. |
| Manifest | `Versioned manifest` | **REUSE + ADAPT** | Reutilizar o manifest como unidade de reprodução. Adaptar contagens de observação/evidência/normalização/oportunidade e janela de coleta; preservar query/método quando houver. |
| Normalized Record | `Canonical DatasetRecord / AssetRecord` | **ADAPT** | O padrão de record canônico e campos de origem é reutilizável. Os campos de oportunidade, elegibilidade, deadline, status e tema são específicos do domínio. |
| OpportunityRecord | Registro canônico de domínio | **ADAPT** | Não criar uma entidade paralela de evidência. Mapear oportunidade para record canônico com `opportunity_id`, `issuer`, `official_url`, `observation_ids`, `evidence_ids` e `field_provenance`. |
| Provenance | Provenance em records e manifest | **REUSE** | Reutilizar origem, versão, método, limitações, warnings e manifest. O Lux Radar adiciona proveniência por campo para deadline, elegibilidade, financiamento e status. |
| Selection | `Explainable selection` | **REUSE** | Matching e priorização devem ser determinísticos, explicáveis e reversíveis. Uma seleção produz candidato operacional, não promessa de relevância absoluta. |
| Research Move | `Research Move` | **REUSE + ADAPT** | Usar para registrar próximo passo — buscar PDF, resolver bloqueio, verificar errata, comparar versão — com razão, observação esperada e critério de parada. |
| Investigation State | `Investigation State` | **REUSE + ADAPT** | Usar para casos incompletos, `insufficient_evidence`, `dependency_blocked`, `skipped`, revisão e decisão. O estado de oportunidade não substitui o estado de investigação. |
| Controlled acquisition | `Controlled acquisition` | **REUSE** | A aquisição operacional permanece no braço privado, com gates e sem expor segredo. O TraceFoundry recebe artefatos seguros ou manifests revisáveis. |

## Onde o Lux Radar termina

O Lux Radar é responsável por:

- registrar e classificar fontes de oportunidades;
- executar ou orquestrar collectors de domínio;
- produzir `SourceObservation`;
- preservar claims, evidências, hashes e limitações;
- produzir releases versionados;
- normalizar observações em registros de oportunidade;
- adaptar registros para contexto territorial, temático e de público;
- entregar dados ou relatórios de oportunidade.

## Onde o TraceFoundry começa

O TraceFoundry deve ser usado quando a pergunta exigir:

- uma `DiscoveryQuery` declarada;
- adapter para uma fonte ou dataset já conhecido;
- seleção determinística e explicável;
- avaliação de evidência;
- manifest de reprodução;
- `InvestigationState` com lacunas e warnings;
- `ResearchMove` com próximo passo e critério de parada;
- revisão humana sobre um resultado candidato.

A fronteira não é um corte rígido por arquivo. É uma separação de responsabilidade: Lux Radar conhece o domínio de oportunidades; TraceFoundry conhece a disciplina de discovery, seleção, evidência e investigação.

## Mapeamento do primeiro release

```text
Lux Radar Acquisition
  SourceObservation
       ↓
  EvidenceRecord
       ↓
  NormalizedRecord
       ↓
  OpportunityRecord
       ↓
TraceFoundry
  Versioned manifest
  Explainable selection
  Investigation State
  Research Move
  Human review
```

## Decisões de não duplicação

Não criar no Lux Radar uma segunda camada de `DatasetRecord` genérica para substituir o TraceFoundry. Não reimplementar seleção explicável do TraceFoundry sem uma lacuna demonstrada. Não mover o `pncp-data-pipeline` para o Lux Radar. Não gravar memória privada ou estado proprietário automaticamente no core público.
