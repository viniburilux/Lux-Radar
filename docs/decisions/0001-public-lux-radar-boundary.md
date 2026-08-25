# ADR 0001 — Limite público do Lux Radar

- **Status:** aceito
- **Data:** 2026-08-25
- **Decisores:** Vinícius Buri Lux

## Contexto

O projeto precisa de um espaço compartilhado para experimentar Opportunity Intelligence com colaboradores, incluindo Jhoel, sem misturar código público, dados privados, segredos operacionais e decisões de produto distribuídas em vários repositórios.

Já existem ativos relevantes em `TraceFoundry`, `pncp-data-pipeline` e nos radares visuais de contratos. O pipeline PNCP contém coleta e preservação operacional; o TraceFoundry contém contratos e mecanismos de descoberta baseada em evidência; os radares existentes contêm referências de apresentação.

## Decisão

Criar o repositório público `viniburilux/Lux-Radar` como laboratório de contratos, schemas, documentação, fixtures sanitizadas, experimentos e integrações leves.

O Lux Radar será responsável por:

- definir e testar a passagem de sinal para oportunidade verificada;
- representar evidência, proveniência, status e relações entre manifestações;
- adaptar componentes existentes sem duplicar seus sistemas de origem;
- documentar hipóteses e métricas;
- produzir protótipos e saídas públicas seguras.

O Lux Radar não será responsável, no primeiro estágio, por:

- armazenar Parquets privados ou caches operacionais;
- guardar credenciais ou conteúdo de grupos privados;
- substituir o `pncp-data-pipeline`;
- reescrever o TraceFoundry;
- publicar dados externos sem verificar licença e termos;
- definir sozinho a arquitetura final de distribuição.

## Consequências

A colaboração fica mais simples porque o Jhoel pode trabalhar em um repositório público e reproduzível. A direção do produto permanece centralizada nos contratos e decisões registradas. A separação exige interfaces claras entre repositórios, especialmente para releases, manifestos, schemas e recortes normalizados.

A abertura pública também cria uma obrigação: todos os commits devem ser revisados quanto a privacidade, licença, segurança e proveniência antes do merge.

## Alternativas rejeitadas

### Criar um repositório privado imediatamente

Foi rejeitado para o primeiro estágio porque a colaboração com Jhoel e a construção compartilhada são objetivos explícitos. A proteção será feita pela separação de dados e segredos, não pelo ocultamento do código público.

### Colocar tudo no TraceFoundry

Foi rejeitado porque o TraceFoundry possui uma responsabilidade própria de infraestrutura de evidência e descoberta científica/tecnológica. O Lux Radar é uma aplicação de domínio e laboratório de integração que pode consumir e adaptar seus contratos.

### Criar um monorepo com todos os projetos

Foi rejeitado para evitar acoplamento, exposição de dados privados e perda de ownership entre pipelines, infraestrutura epistemológica e interfaces de apresentação.
