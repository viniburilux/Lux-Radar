# Lux Radar — Environmental Signal Engine v1

## Objetivo

O Environmental Signal Engine é uma view derivada do pipeline existente. Ele observa cinco capacidades comprovadas — INPE Queimadas, GBIF Occurrence API, NASA EONET, IBGE Localidades e Open-Meteo — sem promover seus dados a oportunidades. A arquitetura permanece `Source Registry → SourceObservation → Evidence → NormalizedRecord → Signal → Opportunity View`.

## Capacidades e sinais

| Fonte | Tipo inicial | Identidade | Tratamento |
|---|---|---|---|
| INPE Queimadas | `FIRE_ACTIVITY` | `id` UUID do foco | CSV diário mais recente, agrupamento por município/UF/bioma, contagem e FRP observados |
| GBIF | `BIODIVERSITY_OCCURRENCE` | `key`/`gbifID` | Página limitada, taxonomia, localização, data, licença e proveniência preservadas |
| NASA EONET | `NATURAL_EVENT` | `id` EONET | Status aberto/encerrado, categorias, geometria, datas e fontes originais preservados |
| IBGE Localidades | `TERRITORIAL_CONTEXT` | `municipio-id` | Índice territorial com município, UF e regiões; correspondência só quando segura |
| Open-Meteo | `CLIMATE_CONDITION` | coordenada + timestamp | Janela horária limitada; enriquecimento espacial/temporal, nunca causalidade |

## Diffs

Quando existe uma identidade estável, cada snapshot é comparado por entidade e pode produzir `ADDED`, `REMOVED`, `CHANGED` ou `UNCHANGED`. Quando a coleta falha, o sistema publica `SOURCE_UNAVAILABLE` com `SOURCE_LEVEL_CHANGE_ONLY`; nunca infere remoções a partir de indisponibilidade.

Os snapshots preservam todas as entidades observadas e suas contagens. Para evitar releases excessivamente pesados, o manifest registra a contagem exata e o sinal-fonte mantém uma amostra detalhada; sinais individuais de mudança são limitados a 600 por fonte e por release.

## Composição

As composições são determinísticas e descritivas. O release publica até três demonstrações: atividade de fogo com território e contexto climático; concentração de fogo agrupada por território; e ocorrência de biodiversidade com território. Uma composição não afirma causalidade, risco, anomalia ou oportunidade.

## Interface

A seção ambiental exibe `AGORA`, `NOVOS`, `ALTERADOS`, `ENCERRADOS / REMOVIDOS`, `INALTERADOS`, `CONTEXTO` e as demonstrações compostas. A experiência de oportunidades continua separada, preservando a regra `UNKNOWN != ACTIVE`.

## Limitações conhecidas

O INPE observa focos de satélite, que não equivalem automaticamente a incêndios distintos. O GBIF usa uma página limitada e não baixa o universo reportado. O EONET depende do snapshot da API; ausência em uma coleta não prova ausência do fenômeno. O IBGE fornece hierarquia territorial, não coordenadas municipais. O Open-Meteo entrega previsão contextual e requer revisão de termos comerciais antes de adoção definitiva. MapBiomas, ANA e OpenAQ não fazem parte deste protótipo.
