# Tese de Produto

## 1. Problema

O ecossistema de sustentabilidade produz e compartilha oportunidades em múltiplos formatos e canais. Uma oportunidade pode nascer em uma fonte institucional, circular por newsletter, rede social, comunidade, evento, mensagem ou indicação pessoal e chegar ao interessado com informação incompleta, duplicada, atrasada ou sem a fonte primária.

O problema central não é apenas localizar links. É transformar um **sinal de oportunidade** em um **registro de oportunidade verificado**, preservando a relação entre a fonte, as evidências, as versões, os atributos extraídos e a decisão de relevância.

## 2. Distinção central

### Signal

Um sinal é uma observação que indica que uma oportunidade pode existir. Pode ser uma mensagem, um áudio transcrito, um print, uma newsletter, um post, um link, uma notícia, um PDF ou uma indicação humana. O sinal é útil para descoberta, mas não autoriza automaticamente uma ação.

### Evidence

Uma evidência é um artefato observável que sustenta uma afirmação sobre a oportunidade. Pode ser uma página oficial, um PDF, um registro de API, um comunicado institucional ou outra fonte identificável. Toda evidência deve carregar origem, data de observação e limitações conhecidas.

### Canonical opportunity

Uma oportunidade canônica é a entidade estruturada que reúne atributos confirmados e manifestações relacionadas. Ela não é simplesmente um documento. É uma representação versionada sustentada por evidências.

```text
SIGNAL → CANDIDATE → SOURCE DISCOVERY → VERIFICATION → EVIDENCE → CANONICAL OPPORTUNITY
```

## 3. Valor proposto

O valor do Lux Radar será testado por quatro capacidades:

| Capacidade | Pergunta respondida |
|---|---|
| Descoberta | O que pode existir e onde devemos verificar? |
| Verificação | Qual é a fonte primária e o que ela realmente confirma? |
| Contexto | Para quem, onde e em que condições isso é relevante? |
| Ação | Qual é o próximo passo possível e qual é o prazo? |

A proposta não é prometer cobertura universal. É reduzir o custo de confiar e agir sobre oportunidades relevantes.

## 4. Usuários iniciais

O primeiro laboratório considera pessoas e organizações que atuam em sustentabilidade, território, turismo, conservação, pesquisa, inovação, cultura, financiamento e políticas públicas. O recorte inicial será conectado a sinais e oportunidades reais da rede do LUXVERSO, incluindo contextos relacionados a Bahia, Blue Bahia e Eco Global.

## 5. Hipóteses a testar

As hipóteses abaixo não são fatos. Devem ser testadas com casos reais e registradas com método:

| Hipótese | Como testar |
|---|---|
| Um sinal humano pode acelerar a descoberta de uma oportunidade relevante. | Comparar data do sinal com data da descoberta em fontes oficiais. |
| A mesma oportunidade aparece em várias manifestações. | Reconstruir 10–20 casos e contar agrupamentos canônicos. |
| Proveniência explícita aumenta a confiança para agir. | Entrevistar ou observar usuários antes e depois da apresentação de evidências. |
| Matching contextual é mais útil que uma lista genérica. | Comparar recomendações filtradas com encaminhamentos sem contexto. |
| O valor está na verificação e na ação, não no volume coletado. | Medir taxa de ação, precisão percebida e tempo economizado. |

Não usar percentuais estimados por modelos como metas ou evidências sem uma medição definida.

## 6. Métricas iniciais

O primeiro experimento deve medir, quando possível:

- **Discovery latency:** tempo entre a publicação e a descoberta pelo sistema ou pela rede.
- **Verification latency:** tempo entre o recebimento do sinal e a confirmação da fonte primária.
- **False signal rate:** proporção de sinais que não se convertem em oportunidade verificável.
- **Duplicate rate:** proporção de observações agrupadas como a mesma oportunidade.
- **Match precision:** proporção de recomendações consideradas relevantes pelo destinatário.
- **Action rate:** proporção de oportunidades que geram inscrição, contato, parceria, participação ou outra ação definida.

## 7. Primeiro experimento

Reconstruir de 10 a 20 oportunidades reais já recebidas pela rede. O conjunto deve conter casos variados, como editais, chamadas, eventos, bolsas, oportunidades de pesquisa, parcerias e financiamento. Cada caso deve percorrer o mesmo roteiro:

```text
sinal original
  → busca da fonte primária
  → captura das evidências
  → extração dos atributos
  → registro canônico
  → agrupamento das manifestações
  → classificação de status
  → avaliação de relevância
  → ação observada
```

O experimento deve aceitar resultados negativos: sinal falso, fonte não encontrada, evidência insuficiente, oportunidade encerrada, duplicata ou baixa relevância. Esses resultados são parte do produto e não devem ser apagados.

## 8. Critérios de não construção

Não construir ainda uma solução quando o problema puder ser resolvido diretamente por uma fonte existente, um adapter do TraceFoundry, um release do pipeline PNCP, uma consulta simples ou um componente visual já disponível. A construção só é justificada quando houver uma lacuna observada no experimento, com entrada, saída e critério de sucesso claros.

## 9. Direção de longo prazo

O radar de sustentabilidade é a primeira aplicação. A infraestrutura poderá futuramente atender pesquisa, inovação, turismo, cultura, educação, clima, financiamento, eventos e procurement. Essa expansão só deve ocorrer depois de validar o núcleo comum: sinal, evidência, proveniência, registro canônico, atualização, matching e ação.
