# Tese de produto

## 1. Problema

O ecossistema de sustentabilidade, território, pesquisa e inovação publica informação em múltiplas superfícies: APIs, CSVs, páginas institucionais, PDFs, feeds, sitemaps, newsletters, redes sociais, páginas de eventos e sinais humanos. O mesmo fato pode ser publicado mais de uma vez, com alterações, prazos diferentes, documentos complementares ou pouca estrutura.

O problema inicial não é apenas localizar links ou listar editais. É **observar fontes heterogêneas de maneira reproduzível**, preservar o que foi visto, identificar mudanças e produzir releases versionados que possam alimentar registros confiáveis.

A partir desses releases, o sistema pode transformar um sinal ou uma observação em uma oportunidade canônica contextualizada e acionável.

## 2. Tese central

O Lux Radar deve começar como uma **máquina de aquisição, observação, evidência e inteligência de oportunidades**. O dashboard ou radar é uma aplicação da máquina, não a definição completa do produto.

```text
SOURCE REGISTRY
  → SOURCE OBSERVATION
  → EVIDENCE
  → VERSIONED RELEASE
  → CANONICAL OPPORTUNITY
  → CONTEXT
  → ACTION
```

A primeira prova de produto não é cobrir todas as oportunidades. É demonstrar que o mesmo pipeline consegue lidar com perfis radicalmente diferentes, declarar suas limitações e produzir uma saída auditável.

## 3. Conceitos

### Source

Uma fonte é uma superfície observável — como uma API, página, PDF, CSV, feed, sitemap, portal ou canal editorial — com identidade, URL, perfil técnico, frequência esperada, termos e estratégia de coleta registrados no catálogo de fontes.

### Observation

Uma observação é o registro timestamped do que foi acessado em uma fonte, por qual método, com qual status, tipo de conteúdo, hash quando possível e quais claims foram extraídos. A observação não é automaticamente uma oportunidade.

### Evidence

Uma evidência é um artefato observável que sustenta uma afirmação. Pode ser uma página, PDF, resposta de API, arquivo CSV, comunicado ou documento vinculado. Toda evidência deve carregar origem, data de observação e limitações conhecidas.

### Release

Um release é um conjunto versionado e reproduzível de observações e registros normalizados, identificado por uma janela temporal, produtor, schemas, contagens e referências de artefatos.

### Signal

Um sinal indica que uma oportunidade pode existir. Pode ser mensagem, áudio transcrito, print, newsletter, post, link, notícia, PDF ou indicação humana. O sinal é útil para resolução de fonte, mas não autoriza automaticamente uma ação.

### Canonical opportunity

Uma oportunidade canônica é a entidade estruturada que reúne atributos confirmados e manifestações relacionadas. Não é simplesmente um documento; é uma representação versionada sustentada por evidências.

## 4. Valor proposto

O valor do Lux Radar será testado por quatro capacidades:

| Capacidade | Pergunta respondida |
|---|---|
| Aquisição | Conseguimos observar fontes diferentes com método e limites declarados? |
| Proveniência | Conseguimos explicar o que foi visto, quando e de onde veio? |
| Normalização | Conseguimos transformar observações em registros comparáveis sem apagar incertezas? |
| Ação | Conseguimos contextualizar um registro e indicar um próximo passo útil? |

A proposta não é prometer cobertura universal. É reduzir o custo de **observar, confiar e agir** sobre informação relevante.

## 5. Laboratório inicial

O primeiro domínio considera fontes de sustentabilidade, território, pesquisa, turismo, conservação, inovação e financiamento, com atenção especial à Bahia e às redes relacionadas a Blue Bahia, Eco Global e parceiros do LUXVERSO.

O laboratório inicial tem duas unidades complementares:

1. **Experimento de aquisição:** mapear 20 fontes e implementar três collectors de perfis diferentes.
2. **Experimento de sinal para oportunidade:** reconstruir 10–20 casos reais depois que o contrato de observação e release estiver provado.

Essa ordem é deliberada. Primeiro provamos a máquina de aquisição; depois medimos o valor de transformar sinais em oportunidades.

## 6. Hipóteses a testar

| Hipótese | Como testar |
|---|---|
| Um contrato comum consegue representar API, HTML/PDF e programa com parceiro sem apagar diferenças. | Implementar três collectors e comparar os releases. |
| Observações versionadas reduzem ambiguidades de prazo, status e documento. | Recoletar fontes com retificações e comparar versões. |
| Proveniência por campo aumenta a confiança para agir. | Apresentar registros com e sem evidência a usuários reais. |
| A mesma oportunidade aparece em várias manifestações. | Reconstruir casos e contar agrupamentos canônicos. |
| Matching contextual é mais útil do que uma lista genérica. | Comparar recomendações contextualizadas com encaminhamentos simples. |
| O valor está na verificação e na ação, não no volume coletado. | Medir precisão percebida, tempo economizado e taxa de ação. |

Estimativas produzidas por modelos não devem ser tratadas como fatos ou metas sem método de medição.

## 7. Primeiro experimento de aquisição

Mapear 20 fontes primárias ou portais oficiais e selecionar três perfis diferentes:

```text
API/JSON/CSV
  + HTML/PDF/errata
  + programa institucional com parceiro e chamada territorial
```

Para cada fonte, registrar identidade, URL, perfil, mecanismo real de publicação, frequência observada ou esperada, campos, documentos, atualização, evidência, limitações, termos e estratégia de coleta.

O primeiro release deve preservar sucesso, parcialidade, bloqueio, falha e ausência de resultado. Um collector não deve esconder uma fonte porque não conseguiu obter o conteúdo completo.

## 8. Segundo experimento: sinal para oportunidade

Depois do release inicial, reconstruir de 10 a 20 oportunidades reais que cruzaram a rede. Cada caso deve registrar sinal, resolução de fonte, observações, evidências, oportunidade canônica, manifestações, status, contexto, ação e resultado.

Resultados negativos — sinal falso, fonte não encontrada, evidência insuficiente, oportunidade encerrada, duplicata ou baixa relevância — fazem parte da medição.

## 9. Métricas

Na aquisição: taxa de sucesso por fonte, cobertura observada, latência de coleta, taxa de alteração detectada, tamanho do release, proporção de falhas e estabilidade do schema.

Na inteligência: latência de descoberta, latência de verificação, taxa de falsos sinais, taxa de duplicação, precisão do matching, taxa de ação e tempo economizado.

## 10. Critérios de não construção

Não construir quando uma capacidade puder ser resolvida por uma fonte existente, um adapter do TraceFoundry, uma interface do `pncp-data-pipeline`, um release já disponível ou um componente visual existente. A construção só se justifica quando houver uma lacuna observada, com entrada, saída e critério de sucesso claros.

Não iniciar ainda crawler universal, banco de dados nacional, grafo dedicado, mensageria de produção, matching autônomo de alto risco ou redistribuição de conteúdo de terceiros.

## 11. Direção de longo prazo

O radar de sustentabilidade é a primeira aplicação. A máquina poderá atender pesquisa, inovação, turismo, cultura, educação, clima, financiamento, eventos e procurement. A expansão deve reutilizar aquisição, observação, evidência, proveniência, release e registro canônico, alterando somente adapters, taxonomias e regras de contexto quando possível.
