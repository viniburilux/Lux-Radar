# Relatório de execução — linha de produção Lux Radar

**Data:** 25 de agosto de 2026  
**Autor:** Manus AI  
**Objetivo:** provar a linha `Source → Observation → Evidence → Normalization → OpportunityRecord → Versioned Release`, sem construir a plataforma inteira.

## 1. Resultado executivo

A direção aprovada foi executada. O Lux Radar agora está posicionado como uma **infraestrutura de aquisição, observação, evidência, proveniência, normalização e releases versionados que produz datasets/records de oportunidades**. O dashboard é uma camada consumidora posterior.

O release privado `2026-08-25-pilot-007` produziu:

| Contagem | Resultado |
|---|---:|
| Observações | 7 |
| Evidências | 5 |
| Registros normalizados | 2 |
| OpportunityRecords | 2 |
| Falhas explícitas | 1 |
| Drifts temporais/cross-surface | 1 |

Os dois registros foram construídos a partir de FAPESB e BNDES/Funbio. O Transferegov foi mantido como perfil API de controle e seu probe diagnóstico retornou HTTP 404 no release 007, registrado como `failed`; nenhuma proteção foi contornada.

## 2. Auditoria do estado atual

| Item | Estado atual | Decisão |
|---|---|---|
| Lux Radar público | Pronto como laboratório de contratos, schemas, documentação, fixtures e decisões | Reutilizar como camada pública e governança |
| Lux Radar Acquisition privado | Pronto como operação mínima de collectors, transformadores, release e validação | Evoluir por módulos pequenos |
| `SourceObservation` | Implementado e validado | Reuse/adaptar com TraceFoundry |
| `EvidenceRecord` | Implementado no transformador e validado | Reuse/adaptar evidência por claim |
| `NormalizedRecord` | Implementado e agora possui schema público | Adaptar como camada intermediária reversível |
| `OpportunityRecord` | Dois registros mínimos produzidos | Reutilizar schema atual, com campos adicionais de verificação e proveniência |
| `ReleaseManifest` | Produzido com artefatos, contagens e drift temporal | Reuse/adaptar como unidade de reprodução |
| Temporalidade | Detector genérico same-URL + drift cross-surface BNDES | Manter simples e auditável |
| TraceFoundry | Compatibilidade documentada; nenhuma reescrita | Integrar após estabilizar os contratos |
| `pncp-data-pipeline` | Referência operacional e interface futura documentadas | Não duplicar coleta nem copiar Parquets |
| Dashboard | Não iniciado nesta etapa | Adiar |

## 3. O que estava pronto, prototipado, faltando e duplicado

### Pronto

O repositório público já possuía tese, arquitetura, governança, inventário, schemas iniciais de sinal/evidência/oportunidade, fixtures sintéticas, experimento 001, regras de contribuição e fronteira público/privado. O braço privado já possuía três collectors mínimos, captura limitada, hashes, configuração de fontes, release de observações e validação inicial.

### Prototipado

Os collectors ainda são probes mínimos. Eles observam uma superfície e extraem claims de navegação; não são schedulers de produção, não fazem cobertura ampla e não garantem que todos os itens de uma fonte sejam capturados. A normalização atual é deliberadamente pequena e não pretende resolver deduplicação geral ou matching.

### Faltava e foi implementado neste estágio

Faltavam a passagem efetiva para evidência, a leitura do PDF oficial FAPESB, normalização reversível, dois OpportunityRecords, estrutura de release com subdiretórios, artefato de mudança temporal, validação dos novos tipos e fixtures públicas sanitizadas. Esses componentes foram implementados no privado e documentados/publicados no público sem expor o bundle operacional.

### Duplicidade evitada

O Lux Radar não reproduziu o `pncp-data-pipeline`, não reescreveu o TraceFoundry, não criou banco universal, não copiou Parquets e não criou um crawler nacional. O collector BNDES também não tenta substituir a operação do Funbio; registra a relação entre página institucional, parceiro e chamada.

### Adiado

Continuam adiados crawler universal, Neo4j, Kafka/NATS, bot de WhatsApp, matching autônomo sofisticado, proxies, dashboard complexo, banco universal, ingestão de dados pessoais e redistribuição automática de conteúdo de terceiros.

## 4. Release real produzido

O bundle operacional está no repositório privado e segue esta estrutura:

```text
releases/local/2026-08-25-pilot-006/
├── manifest.json
├── observations/
├── evidence/
├── normalized/
├── opportunities/
└── changes/
    └── temporal.json
```

O manifest declara as fontes, a janela, contagens, referências de artefatos, hashes, versões dos schemas, produtor, limitações e `temporal_changes`. Os artefatos de observação incluem a URL, o momento, o método, status HTTP, tipo de conteúdo, hash e claims.

A validação automatizada cobre `SourceObservation`, `Evidence`, `NormalizedRecord`, `OpportunityRecord` e `ReleaseManifest`. O release 007 passou pelos testes unitários e pelo gate de contratos.

## 5. FAPESB: linha completa

A fonte FAPESB foi observada como listagem HTML, página de detalhe e PDF de diretrizes. O PDF oficial foi lido para claims e não foi persistido no bundle. A chamada RAMP 2026-2027 foi normalizada com:

| Campo | Valor | Estado |
|---|---|---|
| Título | 1ª Chamada da Parceria de Matérias-Primas para a Transição Verde e Digital | Observado |
| Publicador | FAPESB | Observado |
| Estado | Bahia | Observado |
| Data das diretrizes | 20/07/2026 | Observado no PDF |
| Deadline de proposta completa | 15/02/2027 | Observado no PDF |
| Valor máximo por proposta | €50.000 | Observado no PDF |
| Valor global | €150.000 | Observado no PDF |
| Elegibilidade | Pesquisadores doutores vinculados a ICTs públicas ou privadas sem fins lucrativos na Bahia | Observado no PDF |
| Exigências adicionais | Requisitos completos da chamada conjunta | `unknown`/limitação |

O registro carrega três observações e três evidências, incluindo a página de detalhe e o PDF, com proveniência por campo.

## 6. BNDES/Funbio: linha completa e incerteza

A página institucional do BNDES apresenta o Floresta Viva e referencia chamadas territoriais geridas pelo Funbio. A página operacional do Funbio identifica a chamada da Bacia do Rio Parnaíba, seu objetivo, território, valor e elegibilidade. O registro foi normalizado como encerrado, com valor total de R$70.500.000 e território ligado ao Piauí, Bacia do Rio Parnaíba e UHE Boa Esperança.

A página contém duas datas de prazo em trechos distintos: 15 e 29 de junho de 2026. O sistema não escolhe uma delas. Elas aparecem no diff temporal como `cross_surface_drift_detected`, e o campo canônico `deadline` permanece sem valor normalizado. Essa é a propriedade desejada: **o sistema preserva a divergência em vez de fabricar certeza**.

## 7. Falha explícita

O probe do Transferegov foi executado sem credencial, sem CAPTCHA, sem proxy e sem rotação de IP. No release 007, a resposta observada foi HTTP 404 na base pública alternativa. O resultado foi:

```text
fetch.status = failed
fetch.http_status = 404
```

Isso não significa “oportunidade inexistente”. Significa que aquele caminho não entregou o recurso esperado naquele momento e ambiente. O release preserva a observação, a URL, o hash do corpo limitado e a limitação operacional.

## 8. Temporalidade

O detector implementado oferece duas formas simples:

1. `compare_same_source(before, after)` compara claims de duas observações da mesma URL e emite o campo alterado com `observation_ids` de `observation_t1` e `observation_t2`.
2. `detect_changes(...)` também registra drift entre uma página institucional e uma página operacional relacionada, como no caso BNDES/Funbio.

O primeiro release operacional demonstrou drift cross-surface. O teste unitário demonstra a forma same-URL com `observation_t1 → observation_t2 → field_changed`. A próxima coleta recorrente deve produzir dois snapshots reais da mesma fonte para medir mudanças reais sem fixture.

## 9. Matriz Lux Radar × TraceFoundry

A matriz completa está em [TRACEFOUNDRY_COMPATIBILITY.md](TRACEFOUNDRY_COMPATIBILITY.md). A decisão é:

| Lux Radar | TraceFoundry | Decisão |
|---|---|---|
| Source Registry | `DiscoveryQuery.source`, adapters | Adaptar |
| Source Observation | Source response/observation | Adaptar |
| Evidence | Evidence evaluation | Reutilizar/adaptar |
| Release | Versioned manifest | Reutilizar/adaptar |
| Normalized Record | Canonical DatasetRecord/AssetRecord | Adaptar |
| OpportunityRecord | Canonical domain record | Adaptar |
| Provenance | Provenance em record/manifest | Reutilizar |
| Selection | Explainable selection | Reutilizar |
| Research Move | Research Move | Reutilizar/adaptar |
| Investigation State | Investigation State | Reutilizar/adaptar |

O Lux Radar termina na aquisição, normalização e domínio de oportunidades. O TraceFoundry começa na disciplina de discovery, seleção, evidência, manifest, investigação e revisão.

## 10. Interface PNCP

A interface futura está em [PNCP_INTERFACE.md](PNCP_INTERFACE.md). O consumidor deve receber `release_id`, `dataset_release`, `schema_version`, `record_ref`, `content_hash`, janela de observação, chave territorial e limitações. O contrato deve ser seguro, versionado e independente de caminhos locais.

A primeira opção é manifest + recorte autorizado; depois CSV/JSON ou endpoint interno com escopo mínimo. Parquet privado não deve ser copiado para o Lux Radar.

## 11. Jhoel

O backlog delimitado está em [JHOEL_TASKS.md](JHOEL_TASKS.md). As primeiras tarefas recomendadas são fixtures offline, melhoria de parser FAPESB, melhoria de parser BNDES/Funbio, diff temporal, validação de contratos e fixture de interface PNCP.

A regra de governança é: **Jhoel pode acelerar a implementação, mas não altera ontologia, contratos públicos, fronteira público/privado ou arquitetura global sem proposta e decisão registrada.**

## 12. Próximos três passos

1. Criar fixtures offline completas dos três perfis e garantir que os collectors não dependam da rede para os testes.
2. Fazer uma segunda observação real da FAPESB e do Funbio, gerar `observation_t2` e comparar mudanças de conteúdo, prazo, status e documentos.
3. Mapear o primeiro release autorizado do `pncp-data-pipeline` para `NormalizedRecord`/`ContractRecord` e iniciar a integração mínima com TraceFoundry.

## Referências

[1]: https://www.fapesb.ba.gov.br/diretrizes-especificas-da-fapesb-1a-chamada-da-parceria-de-materias-primas-para-a-transicao-verde-e-digital-ramp-2026-2027/ "FAPESB — RAMP 2026-2027"
[2]: https://www.fapesb.ba.gov.br/wp-content/uploads/2019/08/DIRETRIZES_COOPINTER_RAMP_2026.pdf "FAPESB — Diretrizes específicas RAMP"
[3]: https://chamadas.funbio.org.br/floresta-viva-piaui "FUNBIO — Floresta Viva Bacia do Rio Parnaíba"
[4]: http://www.bndes.gov.br/wps/portal/site/home/desenvolvimento-sustentavel/parcerias/floresta-viva "BNDES — Floresta Viva"
[5]: https://docs.api.transferegov.gestao.gov.br/transferenciasespeciais/ "Transferegov — Documentação da API"
[6]: https://github.com/viniburilux/TraceFoundry "TraceFoundry"
[7]: https://github.com/viniburilux/pncp-data-pipeline "PNCP Data Pipeline"
