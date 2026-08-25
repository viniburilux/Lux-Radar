# Lux Radar

**Opportunity Intelligence Infrastructure for signals, evidence, provenance and actionable opportunities.**

O **Lux Radar** é a camada de inteligência de oportunidades do ecossistema LUXVERSO. Seu objetivo inicial é transformar sinais dispersos — mensagens, links, PDFs, newsletters, eventos, chamadas públicas e fontes institucionais — em oportunidades verificáveis, rastreáveis e acionáveis.

> O produto não precisa descobrir tudo. Ele precisa transformar sinais dispersos em oportunidades confiáveis e acionáveis.

## O que estamos construindo

O Lux Radar não é apenas um portal de editais, um crawler universal ou uma lista de links. Ele é uma infraestrutura que representa o caminho entre:

```text
SIGNAL
  → SOURCE DISCOVERY
  → PRIMARY SOURCE
  → EVIDENCE
  → CANONICAL OPPORTUNITY
  → CONTEXT
  → MATCH
  → ACTION
```

Uma mesma oportunidade pode aparecer em um site oficial, em um PDF, em uma newsletter, no LinkedIn e em uma mensagem de WhatsApp. O sistema deve tratá-los como manifestações e evidências relacionadas de uma entidade canônica, e não como cinco oportunidades independentes.

## Primeiro domínio

O primeiro laboratório será o ecossistema de **sustentabilidade, território, pesquisa, turismo, conservação, inovação e financiamento**, com atenção especial à Bahia e às redes relacionadas a **Blue Bahia**, **Eco Global** e parceiros do LUXVERSO.

Esse domínio foi escolhido porque já existem sinais reais, fontes reais, pessoas reais, oportunidades acontecendo agora e possíveis usuários para validar se o sistema entrega mais valor do que simplesmente encaminhar um link.

## O que já existe e será reaproveitado

O Lux Radar não começa do zero. A arquitetura deve compor ativos já existentes:

| Ativo | Papel no Lux Radar | Decisão |
|---|---|---|
| [TraceFoundry](https://github.com/viniburilux/TraceFoundry) | Proveniência, evidência, seleção explicável, manifestos e estados de investigação | Reutilizar e adaptar |
| [pncp-data-pipeline](https://github.com/viniburilux/pncp-data-pipeline) | Coleta, validação, Parquet, releases e integridade de dados PNCP | Consumir como fonte; não duplicar |
| [Radar-Contratos-BA](https://github.com/viniburilux/Radar-Contratos-BA) | Referência visual para dashboards e narrativas públicas | Reaproveitar componentes e padrões |
| Releases e manifestos existentes | Versionamento, cobertura, hashes e rota de proveniência | Reutilizar diretamente |
| Sinais humanos reais | Casos para testar descoberta, verificação e matching | Usar como fixtures sanitizadas |

O código privado, os segredos operacionais, os Parquets nacionais, caches e dados não autorizados permanecem nos seus repositórios e ambientes de origem. Este repositório público deve conter contratos, documentação, testes, fixtures sanitizadas e componentes que possam ser compartilhados com segurança.

## O que não vamos fazer agora

Não vamos começar construindo um crawler universal, um grafo Neo4j, uma arquitetura Kafka/NATS, um bot de WhatsApp, um banco nacional do zero ou um portal genérico de oportunidades. Essas decisões só serão tomadas quando um experimento real demonstrar necessidade concreta.

Também não vamos transformar estimativas dos outputs das IAs em fatos. Percentuais como cobertura esperada, participação de sinais informais ou precisão de deduplicação serão tratados como hipóteses até serem medidos com casos reais.

## Primeiro experimento

Vamos reconstruir de 10 a 20 oportunidades reais que já cruzaram nossa rede. Para cada caso, registraremos:

1. o sinal original;
2. a descoberta da fonte primária;
3. as evidências encontradas;
4. o registro canônico da oportunidade;
5. as manifestações secundárias;
6. o status e a última verificação;
7. o contexto de relevância;
8. a ação possível ou realizada.

O primeiro sucesso não será medido pelo número de links coletados. As métricas iniciais serão **latência de descoberta**, **latência de verificação**, **taxa de falsos sinais**, **taxa de duplicação**, **precisão do matching** e **taxa de ação**.

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
│   └── decisions/
├── schemas/
│   ├── signal.schema.json
│   ├── evidence.schema.json
│   └── opportunity.schema.json
├── fixtures/
│   ├── signals/
│   ├── evidence/
│   └── opportunities/
├── experiments/
│   └── 001-signal-to-opportunity/
├── src/
│   └── lux_radar/
├── tests/
└── .github/
    ├── ISSUE_TEMPLATE/
    └── pull_request_template.md
```

## Regra de arquitetura

Antes de criar uma integração ou feature, perguntar:

> O conector, schema, release, manifest ou composição já existe?

Se existe, devemos compor e adaptar. Se não existe, adicionamos um módulo isolado com fonte, método, limite, licença e proveniência declarados.

## Estado atual

Este repositório começa como **laboratório público de contratos, evidência e experimentação**. O próximo marco é materializar o primeiro conjunto de oportunidades reais, sem exposição de informações pessoais ou conteúdo privado, e comparar o modelo proposto com o que o TraceFoundry e o pipeline PNCP já suportam.

## Licença e dados externos

O código novo deste repositório será publicado sob licença MIT, salvo indicação diferente em um arquivo específico. Dados, documentos, APIs, marcas, textos de editais e fontes externas permanecem sujeitos aos seus próprios termos. A licença do código não concede licença sobre dados de terceiros.

## Governança

Vinícius Buri Lux mantém a direção do produto, a ontologia central, os limites público/privado e as decisões de arquitetura. Colaboradores podem propor e implementar módulos delimitados por pull request, sempre preservando proveniência, evidência, segurança e reprodutibilidade. Consulte [CONTRIBUTING.md](CONTRIBUTING.md) e [docs/GOVERNANCE.md](docs/GOVERNANCE.md) antes de contribuir.
