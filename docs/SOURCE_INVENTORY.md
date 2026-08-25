# Inventário inicial de fontes

**Data de observação:** 25 de agosto de 2026. **Escopo:** fontes primárias ou portais oficiais relacionados a sustentabilidade, território, pesquisa, inovação, financiamento e oportunidades de parceria.

Esta lista descreve superfícies observadas nas páginas oficiais. Ela não afirma que toda fonte possui API, feed ou permissão de redistribuição. Esses pontos precisam ser confirmados pelo collector e pelos termos aplicáveis.

| # | Fonte | Domínio e papel | Superfície observada | Acesso inicial | Atualização/risco | Prioridade |
|---:|---|---|---|---|---|---|
| 1 | MMA/FNMA | Editais ambientais e apoio a municípios | Página Gov.br, PDFs, retificações e cronograma | HTML + PDF | Mudança de prazo e anexos | Alta |
| 2 | MMA/Fundo Clima | Chamadas de financiamento climático | Página Gov.br com histórico por ano e páginas filhas | HTML + PDF a confirmar | Histórico e estrutura variável | Média |
| 3 | MCTI | Pesquisa, inovação, bioeconomia e sustentabilidade | Notícias e páginas Gov.br | HTML, acesso a confirmar | Algumas páginas podem exigir acesso ou mudar de estrutura | Média |
| 4 | Finep | Financiamento competitivo e não reembolsável, P&D e inovação | Portal de oportunidades com categorias, busca e chamadas abertas | HTML/portal dinâmico | Mudança de filtros e páginas | Alta |
| 5 | BNDES/Floresta Viva | Restauração, conservação e recursos hídricos | Página BNDES, chamadas por território e links para Funbio | HTML + páginas parceiras + documentos | Relação operador/gestor/chamada | Alta |
| 6 | FAPESB | Pesquisa, inovação, bolsas e eventos na Bahia | Listagem WordPress, páginas de edital, PDFs e formulários externos | HTML + PDF + formulário externo | Erratas e múltiplos sistemas | Muito alta |
| 7 | CNPq | Pesquisa, bolsas, cooperação e impacto socioambiental | Página de chamadas abertas e páginas/PDFs de edital | HTML Gov.br + PDF | Calendário e defeso podem alterar visibilidade | Alta |
| 8 | CAPES | Bolsas, pós-graduação e redes de pesquisa | Catálogo de editais abertos e resultados | HTML Gov.br + páginas filhas | Programas com taxonomias distintas | Média-alta |
| 9 | Fundo Amazônia | Projetos territoriais, floresta, água e comunidades | Página de chamadas 2026/anteriores e páginas de programas | HTML + documentos + parceiros | Cobertura pode ser via BNDES ou parceiro | Alta |
| 10 | Embrapii | Parcerias de P&D e competências tecnológicas | Competências, unidades, projetos, painéis e comunicação | HTML dinâmico + links | Nem toda oportunidade aparece como edital | Média-alta |
| 11 | Petrobras Socioambiental | Seleções para projetos sociais e ambientais | Página dinâmica, FAQs, PDFs, status e canais sociais | HTML + PDF + canais de comunicação | Encerramento, prorrogação e documentos relacionados | Alta |
| 12 | Sebrae | Inovação, empreendedorismo e sustentabilidade | Conteúdo, PDFs e páginas de oportunidades; catálogo a investigar | HTML + PDF a confirmar | Estrutura federativa e navegação heterogênea | Média |
| 13 | RNP | P&D, bolsas, eventos, parcerias e tecnologia | Catálogo por categoria, páginas abertas/anteriores e detalhes | HTML + páginas filhas + PDF a confirmar | Mistura de chamadas atuais e históricas | Média-alta |
| 14 | Transferegov | Transferências, parcerias e instrumentos públicos | APIs documentadas e downloads CSV | API + CSV | Módulos têm cronograma de expansão | Alta como controle técnico |
| 15 | EU Funding & Tenders | Funding e procurement da Comissão Europeia | Portal central de busca de programas e oportunidades | Portal dinâmico; API a confirmar | Complexidade e autenticação por operação | Média-alta |
| 16 | CINEA/LIFE | Clima, natureza, biodiversidade, energia e economia circular | Página temática com chamadas, prazos e links para portal central | HTML + links + portal | Página temática propaga para outra plataforma | Alta |
| 17 | Simpler.Grants.gov | Grants federais dos Estados Unidos | Portal e API REST documentada | REST + X-API-Key + extracts | API em desenvolvimento, rate limit e chave | Média-alta |
| 18 | NSF | Grants, fellowships e pesquisa | Funding search, award search e RSS | HTML + busca + RSS | Taxonomia por diretorias e programas | Média-alta |
| 19 | UNESCO | Chamadas, práticas e colaboração internacional | Páginas editoriais, formulários e documentos | HTML + documento + e-mail | Chamadas podem ser temáticas e regionais | Média |
| 20 | Banco Mundial | Procurement e projetos de desenvolvimento | Catálogo paginado, filtros, Excel em lotes e alertas por e-mail | HTML dinâmico + exportação + alerta | Volume grande, filtros e termos de uso | Média-alta |

## Leitura por padrão técnico

| Padrão | Fontes representativas | O que precisa ser provado |
|---|---|---|
| API/documentação/CSV | Transferegov, PNCP como referência externa do acervo existente | Paginação, filtros, limites, versionamento e contrato de campos |
| Listagem HTML + PDF + retificação | MMA/FNMA, FAPESB, CNPq, CAPES | Identidade de chamada, links documentais, atualização e alteração de prazo |
| Portal dinâmico com busca | Finep, EU Funding & Tenders, NSF, Banco Mundial | Estado da página, consultas reproduzíveis, paginação e estabilidade |
| Página temática + parceiro | BNDES/Floresta Viva, Fundo Amazônia, CINEA/LIFE | Relação entre operador, programa, parceiro e chamada individual |
| Empresa com seleção e documentação | Petrobras Socioambiental | Status, FAQs, documentos, seleção anterior e encerramento |
| Fonte com sinal editorial | UNESCO, MCTI, Sebrae, Embrapii | Distinguir notícia ou comunicação de oportunidade formal verificável |
| Feed ou alertas | NSF RSS, Banco Mundial e-mail | Cobertura, atraso, duplicação e ausência de histórico completo |

## Três fontes para os primeiros collectors

### 1. Transferegov — API/JSON/CSV

Serve como controle estruturado. A documentação oficial confirma APIs públicas para módulos de Gestão de Parcerias e Transferências Especiais e uma área de dados CSV. O primeiro probe tentou um recurso documentado com `limit=1` e recebeu HTTP 403 no ambiente do piloto. Portanto, a fonte continua selecionada como perfil API, mas seu collector deve permanecer em estado `blocked` até que endpoint, política de acesso ou alternativa de exportação sejam confirmados. Não deve haver bypass de proteção.

### 2. FAPESB — HTML + PDF + submissão externa

É uma fonte prioritária para o recorte Bahia e representa um caso em que a listagem, o texto, os documentos, as erratas e o sistema de submissão vivem em superfícies diferentes. O collector deve observar apenas conteúdo público, preservar URLs e não tentar submeter nada.

### 3. BNDES/Floresta Viva — página institucional + parceiro + chamada territorial

Representa uma cadeia distribuída. A página BNDES descreve a iniciativa e direciona para chamadas do Funbio, que organiza seleções específicas. O collector deve registrar relações entre programa, parceiro gestor, chamada, território, bioma, edital e prazo, sem pressupor que a página principal contém todos os atributos.

## Critério de seleção

A seleção não busca as três fontes mais fáceis. Busca três superfícies diferentes que permitam testar a generalidade do núcleo. O resultado inicial mostrou que diversidade técnica também inclui falha de acesso e precisa ser preservada no release:

```text
API estruturada
  + HTML/PDF/errata
  + programa institucional com parceiro e chamadas territoriais
```

Se os três perfis puderem produzir observações e releases versionados usando contratos comuns, haverá evidência inicial de que o Lux Radar é uma infraestrutura de aquisição e evidência, não apenas um dashboard.

## Próxima validação

Antes de implementar código definitivo, cada collector deve ter uma ficha de fonte com URL, mecanismo, frequência de observação, limites, status de acesso, estratégia de captura, campos esperados, política de snapshot, licença/termos e critério de falha.

## Referências

[1]: https://www.gov.br/mma/pt-br/composicao/secex/dfre/fundo-nacional-do-meio-ambiente/editais-e-termos-de-referencia-1 "MMA/FNMA"
[2]: https://www.gov.br/mma/pt-br/composicao/secex/dfre/fundo-nacional-sobre-mudanca-do-clima/chamadas-editais-1 "MMA/Fundo Clima"
[3]: https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/2026/04/mobilidade-sustentavel-ganha-r-120-milhoes-em-apoio-a-projetos-inovadores "MCTI"
[4]: https://www.finep.gov.br/chamadas-publicas/chamadaspublicas?situacao=aberta "Finep"
[5]: http://www.bndes.gov.br/wps/portal/site/home/desenvolvimento-sustentavel/parcerias/floresta-viva "BNDES/Floresta Viva"
[6]: https://www.fapesb.ba.gov.br/category/edital/ "FAPESB"
[7]: https://www.gov.br/cnpq/pt-br/assuntos/defeso-eleitoral/copy_of_veja-as-chamadas-com-inscricoes-abertas-no-cnpq "CNPq"
[8]: https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados-capes "CAPES"
[9]: https://www.fundoamazonia.gov.br/pt/como-apresentar-projetos/chamadas-publicas/ "Fundo Amazônia"
[10]: https://embrapii.org.br/ "Embrapii"
[11]: https://petrobras.com.br/sustentabilidade/selecoes-publicas "Petrobras Socioambiental"
[12]: https://sebrae.com.br/sites/PortalSebrae/ufs/df/sebraeaz/editais,e6bc1b1b0e26d710VgnVCM100000d701210aRCRD "Sebrae"
[13]: https://www.rnp.br/28101-2/chamadas-publicas/ "RNP"
[14]: https://www.gov.br/transferegov/pt-br/ferramentas-gestao/api-de-dados-abertos-transferegov.br "Transferegov"
[15]: https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/programmes/horizon "EU Funding & Tenders"
[16]: https://cinea.ec.europa.eu/life-calls-proposals-2026_en "CINEA/LIFE"
[17]: https://wiki.simpler.grants.gov/product/api "Simpler.Grants.gov"
[18]: https://www.nsf.gov/funding "NSF"
[19]: https://www.unesco.org/en/articles/call-2026-good-practices-world-heritage-contribution-sustainable-development-goals "UNESCO"
[20]: https://projects.worldbank.org/en/projects-operations/procurement "Banco Mundial"
