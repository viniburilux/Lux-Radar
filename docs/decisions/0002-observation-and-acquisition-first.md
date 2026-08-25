# ADR 0002 — Observação e aquisição antes da oportunidade

- **Status:** aceito
- **Data:** 2026-08-25
- **Decisores:** Vinícius Buri Lux / direção do LUXVERSO

## Contexto

A interação que originou o Lux Radar revelou que o problema não começa no dashboard nem no registro de oportunidade. As fontes são heterogêneas: APIs, HTML, PDFs, erratas, portais, parceiros e sinais humanos. O sistema precisa demonstrar primeiro que consegue observar e versionar essas superfícies.

A primeira execução do piloto implementou três perfis:

| Perfil | Fonte | Resultado observado |
|---|---|---|
| API | Transferegov | O endpoint foi documentado, mas respondeu HTTP 403 no ambiente do piloto. Isso é uma observação de bloqueio, não um registro de oportunidade. |
| HTML + PDF | FAPESB | HTTP 200 e extração de metadados, links, headings e referências documentais. |
| Institucional + parceiro | BNDES/Floresta Viva | HTTP 200 e extração de referências a chamadas, Funbio, biomas e territórios. |

## Decisão

O primeiro produto do Lux Radar será validado como **infraestrutura de aquisição, observação, evidência e releases versionados**. A oportunidade canônica, o matching e a interface pública entram depois da prova de aquisição.

Cada collector deve produzir uma observação mesmo quando houver bloqueio, falha, resposta parcial ou conteúdo fora do formato esperado. O pipeline não pode converter `403`, timeout ou ausência de JSON em `success`.

## Consequências

### Positivas

- O sistema preserva incerteza e falhas de acesso como informação útil.
- Três superfícies diferentes testam o contrato comum sem exigir arquitetura pesada.
- O repositório público pode manter contratos e documentação, enquanto o privado mantém execução e artefatos operacionais.
- A integração com TraceFoundry ocorre depois que há observações e releases reais para mapear.

### Negativas

- Um release inicial pode conter zero oportunidades canônicas e ainda ser considerado válido.
- Uma fonte importante pode exigir browser, credencial ou mudança de endpoint antes de entrar em recorrência.
- O contrato de oportunidade continuará incompleto até que os casos de normalização revelem os campos necessários.

## Fora do escopo desta decisão

Esta ADR não define frequência de produção, contrato jurídico de redistribuição, mecanismo de bypass para bloqueios, armazenamento de snapshots integrais, matching autônomo ou infraestrutura de mensageria.
