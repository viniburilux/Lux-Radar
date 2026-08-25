# Relatório de execução — Lux Radar

**Data:** 25 de agosto de 2026  
**Autor:** Manus AI  
**Objetivo:** ler a interação completa, executar o prompt operacional, verificar se o posicionamento do Lux Radar precisava ser corrigido e iniciar a camada de aquisição.

## 1. Conclusão executiva

A interação completa muda, sim, o posicionamento. O Lux Radar não deve ser descrito inicialmente como um portal ou dashboard de oportunidades. A formulação mais precisa é:

> **Lux Radar é uma infraestrutura de aquisição, observação, evidência, proveniência e releases versionados que pode alimentar inteligência de oportunidades. O radar é a ponta visível; a máquina de aquisição é o ativo central.**

O prompt final foi executado em duas etapas. Primeiro, foram mapeadas 20 fontes e suas superfícies reais de publicação. Depois, foram escolhidos três perfis tecnicamente diferentes para um piloto: uma API/JSON/CSV, uma fonte HTML + PDF + errata e um programa institucional que aponta para parceiro e chamadas territoriais.

O piloto produziu um resultado útil mesmo com uma falha: FAPESB e BNDES/Floresta Viva responderam com HTTP 200 e geraram claims observáveis; Transferegov respondeu HTTP 403 e foi registrado como `blocked`. Isso confirma a decisão de que falhas e bloqueios são dados do sistema, e não algo a ser escondido ou convertido artificialmente em sucesso.

## 2. O que mudou no repositório público

O repositório [Lux Radar](https://github.com/viniburilux/Lux-Radar) continua público, mas sua tese e arquitetura foram atualizadas no commit `27c6bbc`.

Foram adicionados ou atualizados:

| Artefato | Função |
|---|---|
| `schemas/source-observation.schema.json` | Contrato para registrar fonte, URL, momento, perfil, método, status, conteúdo, claims e limitações. |
| `schemas/release-manifest.schema.json` | Contrato para registrar janela, fontes, contagens, produtor, schemas, artefatos e limitações de um release. |
| `docs/SOURCE_INVENTORY.md` | Inventário inicial das 20 fontes e classificação técnica. |
| `docs/research-2026-08-25.md` | Log de pesquisa com evidências, URLs e cautelas epistemológicas. |
| `docs/decisions/0002-observation-and-acquisition-first.md` | ADR formalizando aquisição e observação antes da oportunidade canônica. |
| `docs/ARCHITECTURE.md` | Arquitetura revisada com `Source Registry → Observation → Evidence → Release → Opportunity`. |
| `docs/PRODUCT_THESIS.md` | Tese revisada, com aquisição como capacidade primária e sinal→oportunidade como segunda etapa. |
| `docs/ROADMAP.md` | Roadmap executável em ordem mapear → escolher → coletar → observar → ajustar → integrar → inteligência. |
| `experiments/001-signal-to-opportunity/README.md` | Experimento 001 convertido em piloto de aquisição e release. |

O código público continua separado da operação. Ele contém contratos, documentação, testes e fixtures seguras, mas não contém tokens, cookies, Parquets privados, caches ou documentos integrais de terceiros.

## 3. Braço privado de aquisição

Foi criado o repositório privado [Lux Radar Acquisition](https://github.com/viniburilux/Lux-Radar-Acquisition), com os commits `0d100a5` e `cf27bac`.

Ele contém:

- catálogo configurável das fontes-piloto;
- núcleo comum de captura pública com timeout, limite de tamanho, hash e status;
- collector de Transferegov;
- collector de FAPESB;
- collector de BNDES/Floresta Viva;
- geração de observações e manifest de release;
- testes unitários sem rede;
- validação contra os schemas públicos;
- `.gitignore` para impedir vazamento de ambiente, dados brutos e releases locais.

A primeira validação foi concluída com três testes unitários e validação dos três JSONs de observação mais o manifest contra os contratos públicos.

## 4. Inventário e evidências observadas

O inventário completo está em [docs/SOURCE_INVENTORY.md](SOURCE_INVENTORY.md). A síntese abaixo mostra por que as fontes não podem ser tratadas como uma única categoria.

| Padrão | Fontes | Evidência operacional |
|---|---|---|
| API/documentação/CSV | Transferegov, PNCP como referência do acervo existente | O Transferegov documenta APIs públicas e CSVs, mas o endpoint testado respondeu 403 no ambiente; o PNCP permanece referência operacional existente. [1] [2] |
| HTML + PDF + retificação | MMA/FNMA, FAPESB, CNPq, CAPES | Há páginas de listagem, documentos, erratas, calendários e páginas filhas. [3] [4] [5] [6] |
| Portal dinâmico com busca | Finep, EU Funding & Tenders, NSF, Banco Mundial | Há filtros, catálogos, busca, paginação, exportação ou feeds; API não deve ser presumida sem documentação. [7] [8] [9] [10] |
| Programa + parceiro + território | BNDES/Floresta Viva, Fundo Amazônia, CINEA/LIFE | A página principal pode descrever o programa e encaminhar para parceiro ou portal de chamada. [11] [12] [13] |
| Seleção empresarial com documentos | Petrobras Socioambiental | A página combina seleção, status, prazos, FAQs, PDFs e canais adicionais. [14] |
| Fonte editorial ou de parceria | UNESCO, MCTI, Sebrae, Embrapii, RNP | Comunicação institucional pode apontar oportunidade, mas precisa ser diferenciada de chamada formal. [15] [16] [17] [18] |

A página do Fundo Nacional do Meio Ambiente, por exemplo, mostra que um edital pode ter publicação, retificação, prorrogação, datas por etapa e anexos distintos. [3] A FAPESB combina listagem de editais, texto descritivo, PDFs, erratas e sistemas externos de submissão. [6] A Petrobras também combina status de inscrição, período, resultado e documentos complementares. [14]

O Transferegov é particularmente importante como controle técnico porque seu portal oficial anuncia APIs públicas, documentação, CSV e módulos com disponibilização progressiva. [1] A documentação do módulo de Transferências Especiais descreve modelos e operadores de filtragem. [2] O fato de o primeiro endpoint ter respondido 403 não invalida a documentação; apenas impede classificar o acesso daquele caminho como operacional no ambiente atual.

Internacionalmente, o Funding & Tenders Portal se apresenta como entrada única para programas de financiamento e procurement da Comissão Europeia. [8] A CINEA publica a página temática LIFE com subprogramas, prazos e encaminhamento para o portal central. [9] Simpler.Grants.gov documenta API REST com chave, busca, paginação, extracts e rate limits, mas informa que a API está em desenvolvimento. [19] O Banco Mundial expõe procurement notices com filtros, paginação, exportação em lotes e alertas. [10]

## 5. Escolha dos três perfis

A seleção não foi feita pelas fontes mais fáceis. Foi feita para testar se um contrato comum consegue lidar com superfícies diferentes.

| Perfil | Fonte | Collector | Estado |
|---|---|---|---|
| API/JSON/CSV | Transferegov | `transferegov` | Implementado; bloqueio HTTP 403 preservado. |
| HTML + PDF + errata | FAPESB | `fapesb` | Implementado; HTTP 200 e 8 claims. |
| Programa institucional + parceiro + chamada territorial | BNDES/Floresta Viva | `bndes_floresta_viva` | Implementado; HTTP 200 e 9 claims. |

O terceiro perfil é importante porque a página oficial do BNDES descreve o Floresta Viva, seus territórios e editais, e encaminha a organização das chamadas para o Funbio. [11] O Fundo Amazônia apresenta padrão semelhante de chamadas próprias e chamadas realizadas por instituições parceiras. [12]

## 6. Resultado do primeiro release local

O release local produziu três observações e zero oportunidades canônicas, o que é esperado nesta etapa.

| Fonte | HTTP | Status | Claims |
|---|---:|---|---:|
| BNDES/Floresta Viva | 200 | `success` | 9 |
| FAPESB | 200 | `success` | 8 |
| Transferegov | 403 | `blocked` | 0 |

O manifest registrou `observations=3`, `opportunities=0` e `failed=1`, porque `blocked` entra como resultado operacional falho para fins de contagem, sem apagar a observação.

A ausência de oportunidades canônicas é correta. O objetivo do primeiro release é provar aquisição, observação e versionamento; normalização em oportunidade entra depois que o contrato de observação estiver demonstrado.

## 7. Decisão de arquitetura

A sequência oficial passa a ser:

```text
SOURCE REGISTRY
  → COLLECTOR
  → SOURCE OBSERVATION
  → EVIDENCE
  → VERSIONED RELEASE
  → NORMALIZED RECORD
  → CANONICAL OPPORTUNITY
  → CONTEXT / MATCH
  → ACTION
```

O [TraceFoundry](https://github.com/viniburilux/TraceFoundry) entra como infraestrutura epistemológica de proveniência, evidência, seleção explicável, manifestos e estados de investigação. O [pncp-data-pipeline](https://github.com/viniburilux/pncp-data-pipeline) permanece como referência de aquisição, validação, Parquet, releases e integridade do domínio PNCP. O Lux Radar não deve duplicar esses sistemas.

O próximo trabalho de integração deve ser mapear `SourceObservation`, `EvidenceRecord` e `ReleaseManifest` para os contratos existentes, sem reescrever o TraceFoundry e sem copiar dados privados do pipeline PNCP.

## 8. Diretriz para Jhoel e outros agentes

A colaboração é bem-vinda, mas deve ocorrer dentro da moldura definida por nós. A diretriz prática é:

> **Construa módulos delimitados; não redefina a ontologia do produto sem decisão registrada. Toda contribuição deve declarar fonte, método, frequência, campos observados, limitações, termos, testes e critério de sucesso.**

Jhoel pode começar por testes, parsers, adapters, validação de schemas, documentação de fonte e componentes visuais. Não deve começar por crawler universal, banco central, mensageria de produção, matching autônomo, ingestão de WhatsApp ou mudança silenciosa dos limites público/privado.

A direção do produto, o modelo conceitual e os limites de publicação permanecem com Vinícius Buri Lux. A implementação pode ser distribuída; a ontologia e a governança precisam ser coerentes.

## 9. Próximos passos

A sequência recomendada agora é:

1. Resolver o status do collector Transferegov por investigação permitida de endpoint, documentação e alternativa de exportação; não fazer bypass de proteção.
2. Adicionar fixtures de respostas HTML, PDF-link listing, JSON e bloqueio para que os collectors sejam reproduzíveis sem rede.
3. Produzir o primeiro release revisado com artefatos e hashes somente quando a política de armazenamento estiver definida.
4. Implementar normalização mínima de claims para `OpportunityRecord`, começando por FAPESB e Floresta Viva.
5. Mapear a ponte com TraceFoundry e a interface de consumo de releases do `pncp-data-pipeline`.
6. Só depois reconstruir 10–20 casos reais de sinal para oportunidade e medir latência, duplicação, verificação, matching e ação.

## 10. Referências

[1]: https://www.gov.br/transferegov/pt-br/ferramentas-gestao/api-de-dados-abertos-transferegov.br "Transferegov — API de Dados Abertos"
[2]: https://docs.api.transferegov.gestao.gov.br/transferenciasespeciais/ "Transferegov — documentação da API"
[3]: https://www.gov.br/mma/pt-br/composicao/secex/dfre/fundo-nacional-do-meio-ambiente/editais-e-termos-de-referencia-1 "MMA/FNMA — Editais e Termos de Referência"
[4]: https://www.gov.br/mma/pt-br/composicao/secex/dfre/fundo-nacional-sobre-mudanca-do-clima/chamadas-editais-1 "MMA/Fundo Clima — Chamadas e Editais"
[5]: https://www.gov.br/cnpq/pt-br/assuntos/defeso-eleitoral/copy_of_veja-as-chamadas-com-inscricoes-abertas-no-cnpq "CNPq — Chamadas com prazo aberto"
[6]: https://www.fapesb.ba.gov.br/category/edital/ "FAPESB — Editais"
[7]: https://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta "Finep — Chamadas Públicas Abertas"
[8]: https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/programmes/horizon "EU Funding & Tenders Portal"
[9]: https://cinea.ec.europa.eu/life-calls-proposals-2026_en "CINEA — LIFE Calls 2026"
[10]: https://projects.worldbank.org/en/projects-operations/procurement "World Bank — Procurement Notices"
[11]: http://www.bndes.gov.br/wps/portal/site/home/desenvolvimento-sustentavel/parcerias/floresta-viva "BNDES — Floresta Viva"
[12]: https://www.fundoamazonia.gov.br/pt/como-apresentar-projetos/chamadas-publicas/ "Fundo Amazônia — Chamadas Públicas"
[13]: https://www.unesco.org/en/articles/call-2026-good-practices-world-heritage-contribution-sustainable-development-goals "UNESCO — Call for 2026 Good Practices"
[14]: https://petrobras.com.br/sustentabilidade/selecoes-publicas "Petrobras — Seleções públicas socioambientais"
[15]: https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/2026/04/mobilidade-sustentavel-ganha-r-120-milhoes-em-apoio-a-projetos-inovadores "MCTI — Mobilidade sustentável"
[16]: https://sebrae.com.br/sites/PortalSebrae/ufs/df/sebraeaz/editais,e6bc1b1b0e26d710VgnVCM100000d701210aRCRD "Sebrae — Editais"
[17]: https://embrapii.org.br/ "Embrapii — Inovação e Pesquisa"
[18]: https://www.rnp.br/28101-2/chamadas-publicas/ "RNP — Chamadas Públicas"
[19]: https://wiki.simpler.grants.gov/product/api "Simpler.Grants.gov — API"
[20]: https://www.nsf.gov/funding "NSF — Funding"
