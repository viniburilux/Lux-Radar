# Lux Radar

**Opportunity Intelligence Infrastructure for source observation, evidence, provenance and actionable opportunities.**

O **Lux Radar** é a camada pública de contratos, experimentos e composição do ecossistema LUXVERSO. Ele está sendo construído para observar fontes heterogêneas, adquirir sinais de forma declarada, preservar evidências e produzir releases versionados que possam alimentar oportunidades contextualizadas e acionáveis.

> O radar é a ponta visível. O ativo central é a máquina de aquisição, observação, evidência e inteligência que existe por baixo.

## O que estamos construindo

O Lux Radar não é apenas um portal de editais, um crawler universal ou uma lista de links. A unidade operacional começa antes da oportunidade canônica:

```text
SOURCE REGISTRY
  → SOURCE OBSERVATION
  → EVIDENCE
  → VERSIONED RELEASE
  → CANONICAL OPPORTUNITY
  → CONTEXT
  → MATCH
  → ACTION
```

Uma mesma oportunidade pode aparecer em uma API, em uma página institucional, em um PDF, em uma newsletter, no LinkedIn e em uma mensagem de WhatsApp. O sistema deve preservar essas manifestações e explicar como cada atributo foi observado, transformado e relacionado.

A arquitetura também precisa aceitar sinais que ainda não são oportunidades verificadas:

```text
SIGNAL
  → SOURCE RESOLUTION
  → OBSERVATION
  → EVIDENCE
  → CANONICAL OPPORTUNITY
```

## Primeiro domínio

O primeiro laboratório observa fontes de **sustentabilidade, território, pesquisa, turismo, conservação, inovação e financiamento**, com atenção especial à Bahia e às redes relacionadas a **Blue Bahia**, **Eco Global** e parceiros do LUXVERSO.

Esse domínio foi escolhido porque já existem fontes reais, sinais reais, pessoas reais e possíveis usuários para validar se a infraestrutura entrega mais valor do que simplesmente encaminhar um link.

## Primeiro experimento de aquisição

O prompt operacional desta etapa é:

> Mapear 20 fontes primárias de sustentabilidade e selecionar três fontes estruturalmente diferentes para implementar os primeiros collectors, usando como referência operacional o `pncp-data-pipeline`. O objetivo não é construir o sistema final, mas provar a capacidade de transformar fontes heterogêneas em releases observáveis e versionados que possam alimentar os schemas do Lux Radar.

O inventário inicial está em [docs/SOURCE_INVENTORY.md](docs/SOURCE_INVENTORY.md). A pesquisa com evidências e URLs está em [docs/research-2026-08-25.md](docs/research-2026-08-25.md).

Os três perfis selecionados para o piloto são:

| Perfil | Fonte piloto | Motivo |
|---|---|---|
| API/JSON/CSV | Transferegov | Controle estruturado, filtros documentados e possibilidade de paginação/release. |
| HTML + PDF + errata | FAPESB | Recorte prioritário da Bahia, múltiplas páginas, documentos, retificações e submissão externa. |
| Programa institucional + parceiro + chamada territorial | BNDES/Floresta Viva | Cadeia distribuída entre BNDES, Funbio, chamada, bioma, bacia e território. |

## O que já existe e será reaproveitado

O Lux Radar não começa do zero. A arquitetura compõe ativos já existentes:

| Ativo | Papel no Lux Radar | Decisão |
|---|---|---|
| [TraceFoundry](https://github.com/viniburilux/TraceFoundry) | Proveniência, evidência, seleção explicável, manifestos e estados de investigação | Reutilizar e adaptar |
| [pncp-data-pipeline](https://github.com/viniburilux/pncp-data-pipeline) | Referência de coleta, validação, Parquet, releases e integridade PNCP | Usar como referência e consumir interfaces; não duplicar |
| [Radar-Contratos-BA](https://github.com/viniburilux/Radar-Contratos-BA) | Referência visual para dashboards e narrativas públicas | Reaproveitar padrões, sem tratá-lo como backend |
| Releases e manifestos existentes | Versionamento, cobertura, hashes e rota de proveniência | Reutilizar diretamente quando a interface for definida |
| Sinais humanos reais | Casos para testar resolução de fonte e ação | Usar apenas como fixtures sanitizadas |

O código privado, os segredos operacionais, os Parquets nacionais, caches e dados não autorizados permanecem nos repositórios e ambientes de origem. Este repositório público deve conter contratos, documentação, testes, fixtures sanitizadas e componentes que possam ser compartilhados com segurança.

## Contratos públicos

Os contratos iniciais estão em `schemas/`:

| Schema | Responsabilidade |
|---|---|
| `source-observation.schema.json` | Registrar uma observação timestamped de uma fonte, método, status, conteúdo, claims e limitações. |
| `release-manifest.schema.json` | Registrar a identidade, janela, contagens, artefatos, produtor e limitações de um release. |
| `normalized-record.schema.json` | Preservar claims e referências no estágio entre observação e oportunidade canônica. |
| `signal.schema.json` | Representar um sinal de oportunidade antes da verificação. |
| `evidence.schema.json` | Ligar afirmações e atributos a artefatos observáveis. |
| `opportunity.schema.json` | Representar a oportunidade canônica sustentada por evidências. |

## Documentos de execução

- [Inventário de fontes](docs/SOURCE_INVENTORY.md)
- [Matriz TraceFoundry](docs/TRACEFOUNDRY_COMPATIBILITY.md)
- [Interface futura com PNCP](docs/PNCP_INTERFACE.md)
- [Tarefas para colaboradores](docs/JHOEL_TASKS.md)
- [Experimento 001](experiments/001-signal-to-opportunity/README.md)

## O que não vamos fazer agora

Não vamos começar construindo um crawler universal, um grafo Neo4j, uma arquitetura Kafka/NATS, um bot de WhatsApp, um banco nacional do zero ou um portal genérico de oportunidades. Também não vamos tratar uma página institucional como API sem documentação, nem supor que conteúdo público tenha licença de redistribuição.

Não vamos transformar estimativas dos outputs das IAs em fatos. Percentuais de cobertura, sinais informais ou precisão de deduplicação serão tratados como hipóteses até serem medidos.

## Primeiro sucesso

O primeiro sucesso é um release pequeno e reproduzível contendo observações de três perfis técnicos diferentes, com:

- fonte, URL, momento e método declarados;
- status de acesso e limitações registradas;
- evidências e hashes quando possível;
- contagem e janela de observação;
- transformação rastreável para os schemas públicos;
- falhas e casos não verificáveis preservados;
- nenhum segredo, dado pessoal ou material privado publicado.

## Estrutura inicial

```text
Lux-Radar/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── docs/
│   ├── PRODUCT_THESIS.md
│   ├── ARCHITECTURE.md
│   ├── GOVERNANCE.md
│   ├── ROADMAP.md
│   ├── SOURCE_INVENTORY.md
│   ├── research-2026-08-25.md
│   ├── TRACEFOUNDRY_COMPATIBILITY.md
│   ├── PNCP_INTERFACE.md
│   ├── JHOEL_TASKS.md
│   └── decisions/
├── schemas/
│   ├── source-observation.schema.json
│   ├── release-manifest.schema.json
│   ├── normalized-record.schema.json
│   ├── signal.schema.json
│   ├── evidence.schema.json
│   └── opportunity.schema.json
├── fixtures/
├── experiments/
├── src/lux_radar/
└── tests/
```

## Regra de arquitetura

Antes de criar uma integração ou feature, perguntar:

> O conector, schema, release, manifest ou composição já existe?

Se existe, devemos compor e adaptar. Se não existe, adicionamos um módulo isolado com fonte, método, limite, licença e proveniência declarados.

## Licença e dados externos

O código novo deste repositório será publicado sob licença MIT, salvo indicação diferente em um arquivo específico. Dados, documentos, APIs, marcas, textos de editais e fontes externas permanecem sujeitos aos seus próprios termos. A licença do código não concede licença sobre dados de terceiros.

## Governança

Vinícius Buri Lux mantém a direção do produto, a ontologia central, os limites público/privado e as decisões de arquitetura. Colaboradores podem propor e implementar collectors, adapters, testes e documentação delimitados por pull request, sempre preservando proveniência, evidência, segurança e reprodutibilidade. Consulte [CONTRIBUTING.md](CONTRIBUTING.md) e [docs/GOVERNANCE.md](docs/GOVERNANCE.md) antes de contribuir.
