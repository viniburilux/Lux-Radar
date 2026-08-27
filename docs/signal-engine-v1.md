# Sustainability Signal Engine v1

## Decisão

O comando recebido foi considerado o melhor caminho **com escopo reduzido**. O Lux Radar não ganhou uma segunda arquitetura nem passou a tratar todo sinal como oportunidade. A cadeia existente foi preservada: `Source Registry → SourceObservation → Evidence → NormalizedRecord → OpportunityRecord`. A nova saída é uma **view derivada** que torna observações de fonte, registros normalizados e mudanças visíveis antes da promoção para oportunidade.

O contrato anterior de `Signal` para sinais brutos de canais humanos foi preservado. Para a saída derivada, foi criado um contrato explícito em `schemas/derived-signal.schema.json`, evitando misturar uma eventual mensagem de WhatsApp com um snapshot de API ou página pública.

## Experimento heterogêneo

O laboratório foi executado com sete fontes já justificadas pela matriz de capacidades: FUNBIO, Fundação Grupo Boticário, Prosas, CNPq, PNCP, IBGE Localidades e MapBiomas. O objetivo foi testar funding, notícia, descoberta, pesquisa, procurement, dado territorial e dado ambiental no mesmo fluxo, sem adicionar OpenAQ ou endpoints não comprovados.

| Capacidade | Fonte | Tipo de sinal | Evidência observada |
|---|---|---|---:|
| Financiamento/chamadas | FUNBIO | `funding_opportunity` | 8 links candidatos |
| Notícias e chamadas | Fundação Grupo Boticário | `news_signal` | 44 links candidatos |
| Descoberta | Prosas | `discovery_signal` | snapshot observado, sem itens candidatos nessa execução |
| Pesquisa/financiamento | CNPq | `research_funding` | 34 links candidatos |
| Procurement | PNCP | `procurement` | fonte respondendo em uma execução e indisponível em outra |
| Território estruturado | IBGE Localidades | `territorial_data` | 5.571 itens JSON observados; preview limitado preservado |
| Dados ambientais | MapBiomas | `environmental_data` | snapshot/hash da plataforma; nenhum item candidato HTML extraído |

No primeiro run do laboratório, as sete fontes responderam e foram gerados sete snapshots de fonte. Na repetição, a mesma fonte PNCP apresentou timeout; o motor classificou isso como `SOURCE_UNAVAILABLE`, sem inferir ausência de dados. FUNBIO e Boticário demonstraram alteração de conteúdo entre execuções; IBGE e MapBiomas mantiveram o mesmo hash na repetição. Esse resultado prova a necessidade do mapa de saúde e de mudança, mas também mostra que uma página HTML dinâmica de MapBiomas ainda não equivale a uma captura estruturada de indicadores ambientais.

## Release global de validação

O build global foi executado sobre as 34 fontes do registry, sem bypass de bloqueio ou autenticação. O resultado local `signal-engine-v1-global-final` produziu:

| Métrica | Resultado |
|---|---:|
| Observações | 223 |
| Perfis `html` / `pdf` / `portal` / `api` | 197 / 22 / 2 / 2 |
| Evidências | 217 |
| Registros normalizados | 813 |
| Registros canônicos | 581 |
| Oportunidades atuais | 15 |
| Sinais derivados totais | 615 |
| Sinais de fonte raiz | 34 |
| Mudanças temporais | 21 |
| Fontes com sucesso | 29 |
| Fontes indisponíveis | 5 |
| `UNKNOWN` na visão atual | 0 |

Os cinco canais indisponíveis foram preservados no manifest: Transferegov, GIFE, MinC CultBR, PNCP e IBGE nessa execução específica. Isso representa **saúde operacional**, não prova de inexistência de informação. O release mantém `UNKNOWN`, `CANDIDATE` e `INSUFFICIENT_EVIDENCE` fora da visão atual.

## Alterações implementadas

O collector genérico agora registra respostas JSON como claims estruturadas, incluindo tipo de resposta, quantidade de itens, chaves, identificadores e um preview limitado. O builder deriva snapshots de fonte apenas a partir da observação raiz; detalhes enriquecidos carregam `parent_observation_id` e não são contados como novas fontes. O perfil de observação passou a respeitar o enum formal (`api`, `html`, `pdf`, `portal` e `unknown`) também nos adapters Wave 2.

O manifest ganhou `signal_counts` e `temporal_changes`, e o release publica `data/signals.json`. A interface ganhou uma seção experimental “O que apareceu e o que mudou”, com métricas, tipo de sinal, estado da fonte, quantidade observada, limitações e link original. A view de oportunidades permanece intacta e continua sendo a única camada que promove registros para ação.

## O que o experimento provou e o que não provou

O experimento provou que o Lux Radar consegue observar fontes heterogêneas no mesmo fluxo, registrar API estruturada sem convertê-la em oportunidade, detectar diferença entre conteúdo alterado e fonte indisponível, e expor a proveniência na interface. Também provou que o primeiro ganho real está em **observabilidade da coleta**, não em multiplicar fontes.

Ele não provou ainda que MapBiomas ou qualquer página dinâmica forneça indicadores ambientais estruturados no collector atual. Também não provou que todo item observado de uma fonte deve virar card individual; por enquanto, o snapshot de fonte e os registros normalizados coexistem apenas como views derivadas, com limitação explícita para evitar interpretação prematura.

## Próxima etapa recomendada

A próxima construção deve ser um **painel de saúde e mudança por fonte**, com histórico de resposta, hash, quantidade observada, tipo de conteúdo, itens adicionados/removidos/alterados e taxa de falha. Só depois desse painel devemos escolher quais capacidades ambientais merecem adapters estruturados — por exemplo, indicadores territoriais, clima, biodiversidade ou qualidade ambiental — e quais tipos de sinal merecem experiências próprias.

Não devem ser adicionados agora: ML, recomendação, matching, alertas personalizados, dezenas de APIs do catálogo `public-apis`, bypass de fontes bloqueadas ou novas regras para transformar ausência de prazo em oportunidade. O princípio continua sendo: **observar primeiro, interpretar depois e promover apenas quando a evidência permitir**.

## Referências

[1]: https://servicodados.ibge.gov.br/ "IBGE — Serviços de Dados"

[2]: https://plataforma.mapbiomas.org/projects/mapbiomas/brazil "MapBiomas — Plataforma Brasil"

[3]: https://github.com/public-apis/public-apis "public-apis — catálogo comunitário de APIs"
