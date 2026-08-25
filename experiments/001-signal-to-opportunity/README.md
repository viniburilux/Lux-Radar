# Experimento 001 — Source acquisition to versioned release

## Objetivo

Provar que o Lux Radar consegue observar três perfis de fontes públicas estruturalmente diferentes e produzir observações e um release versionado compatíveis com os contratos públicos.

A reconstrução manual de oportunidades continua como experimento posterior. Nesta etapa, o foco é a máquina que antecede o registro canônico.

## Unidade de análise

A unidade primária é uma **observação de fonte**. Cada observação deve conter:

```text
observation_id
source_id
source_url
observed_at
source_profile
fetch.status
fetch.method
content metadata
claims
limitations
collector version
```

O release agrega as observações e registra:

```text
release_id
observation window
source_ids
record counts
producer
schema versions
artifacts
limitations
```

## Fontes do piloto

| Fonte | Perfil | Pergunta |
|---|---|---|
| Transferegov | API/JSON/CSV | O contrato registra resposta estruturada, paginação e bloqueio sem inventar sucesso? |
| FAPESB | HTML + PDF + errata | O contrato preserva listagem, documentos, links, mudança e limitações? |
| BNDES/Floresta Viva | Programa + parceiro + chamada territorial | O contrato preserva relações entre programa, parceiro, chamada, bioma e território? |

## Procedimento

1. Ler a configuração declarativa da fonte.
2. Fazer uma requisição pública sem credencial.
3. Registrar status HTTP, tipo de conteúdo, timestamp, hash e tamanho limitado.
4. Extrair somente claims mínimos e auditáveis.
5. Preservar limitações e falhas.
6. Escrever a observação local.
7. Agregar as observações em um manifest de release.
8. Validar JSON e testes sem rede.
9. Revisar dados e termos antes de qualquer publicação.

## Critérios de sucesso

O experimento será considerado tecnicamente bem-sucedido se:

- os três collectors produzirem uma observação válida;
- pelo menos dois perfis HTML/portal retornarem claims observáveis;
- um bloqueio ou falha for representado explicitamente;
- o manifest registrar contagens, janela e produtor;
- nenhum token, cookie, dado pessoal ou documento integral entrar no Git;
- o mesmo núcleo puder ser testado com fixtures sem rede.

A ausência de uma oportunidade canônica não é falha desta etapa. O release pode conter zero oportunidades e ainda provar a camada de aquisição.

## Resultado inicial

Na primeira execução local de 25 de agosto de 2026:

| Fonte | Status | Claims |
|---|---:|---:|
| BNDES/Floresta Viva | HTTP 200 / success | 9 |
| FAPESB | HTTP 200 / success | 8 |
| Transferegov | HTTP 403 / blocked | 0 |

O bloqueio do Transferegov é preservado como observação operacional. Ele exige investigação posterior de acesso, endpoint, política de borda ou alternativa de release; não autoriza bypass nem classificação da fonte como inexistente.

## Saídas

- observações locais em `Lux-Radar-Acquisition/releases/local/`;
- manifest local de release;
- schemas públicos em `Lux-Radar/schemas/`;
- documentação de fonte em `Lux-Radar/docs/SOURCE_INVENTORY.md`;
- integração futura com TraceFoundry depois de estabilizar o contrato.
