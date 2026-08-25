# Governança do Lux Radar

## 1. Natureza do repositório

O Lux Radar começa como um **laboratório público de infraestrutura e produto**. O fato de o código ser público não significa que todos os dados, decisões privadas, credenciais, pipelines operacionais ou materiais de parceiros devam ser publicados.

O repositório deve permanecer aberto à colaboração, mas com fronteiras claras entre:

| Área | Regra |
|---|---|
| Código e schemas públicos | Podem ser discutidos, testados e melhorados por pull request. |
| Ontologia e contratos centrais | Mudanças exigem decisão registrada e revisão do mantenedor. |
| Dados privados ou sensíveis | Não entram no repositório público. |
| Credenciais, tokens e cookies | Nunca entram no Git. |
| Parquets, caches e dumps de fontes | Não entram sem autorização, licença e necessidade demonstrada. |
| Outputs de IA | Entram apenas após revisão, síntese e atribuição de status epistemológico. |
| Integrações externas | Devem declarar método, limite, licença, custo e proveniência. |

## 2. Papéis

### Direção do produto e arquitetura

**Vinícius Buri Lux** mantém a direção do produto, a tese central, os limites de publicação, a ontologia de sinais/evidências/oportunidades, a relação com TraceFoundry e as decisões que alterem o núcleo conceitual ou a estratégia de distribuição.

### Colaboradores de implementação

Colaboradores, incluindo Jhoel, podem atuar como construtores de módulos delimitados: adapters, schemas, fixtures sanitizadas, testes, documentação, protótipos de interface, scripts de validação e experimentos reproduzíveis.

A colaboração deve ocorrer por branch e pull request. Uma contribuição pode ser tecnicamente excelente e ainda assim precisar de ajuste de escopo, nomenclatura, segurança, proveniência ou compatibilidade com o núcleo.

### Revisão

Toda alteração relevante deve declarar:

- problema que resolve;
- evidência que motivou a alteração;
- arquivos afetados;
- dependências novas;
- riscos de segurança, licença e privacidade;
- forma de teste;
- o que deliberadamente não foi construído.

## 3. Diretriz para o Jhoel

A diretriz de trabalho para o Jhoel é:

> Construa rápido dentro de um problema delimitado, mas não defina sozinho a ontologia, a arquitetura global ou a direção do produto. Primeiro leia a tese, a arquitetura e as decisões registradas; depois proponha uma implementação pequena, testável e reversível.

As primeiras tarefas adequadas para colaboração são:

1. criar fixtures sanitizadas de sinais e evidências;
2. implementar validação dos schemas;
3. construir um parser de entrada manual sem chamadas externas;
4. criar um relatório de reconstrução de uma oportunidade real;
5. adicionar testes de deduplicação determinística;
6. adaptar uma interface visual sem misturar dados privados;
7. documentar um adapter de fonte pública com limites explícitos.

As primeiras tarefas inadequadas são: alterar o contrato canônico sem decisão, criar um banco ou grafo definitivo, conectar WhatsApp, inserir credenciais, copiar dados privados, raspar centenas de páginas ou adicionar dependências complexas sem um experimento que as justifique.

## 4. Processo de decisão

Decisões pequenas podem ser tomadas no próprio pull request. Decisões que alterem o modelo de dados, o limite público/privado, a estratégia de proveniência, a licença, a dependência do TraceFoundry ou a integração com dados privados devem gerar um registro em `docs/decisions/`.

A classificação usada nas decisões é:

- **REUSE:** consumir ou reaproveitar diretamente;
- **ADAPT:** criar uma ponte compatível;
- **BUILD:** construir uma capacidade que o experimento demonstrou faltar;
- **BUY:** avaliar serviço externo quando o custo e os termos forem aceitáveis;
- **AVOID:** não adotar por custo, risco, duplicação ou inadequação.

## 5. Regra de evidência

O repositório diferencia:

| Categoria | Significado |
|---|---|
| Observado | Está presente em um arquivo, execução, fonte ou documentação verificável. |
| Inferido | É uma interpretação razoável, mas ainda não foi demonstrada diretamente. |
| Hipótese | Precisa ser testada com dados ou usuários. |
| Decisão | Escolha operacional adotada pelo projeto. |
| Bloqueio | Algo que não pôde ser confirmado por falta de acesso, fonte ou condição. |

Nenhum output de IA deve ser tratado como fonte primária apenas porque parece consistente com outros outputs.

## 6. Regras de segurança

Antes de publicar, verificar se o material contém credenciais, dados pessoais, conteúdo de grupos privados, documentos de parceiros, informações contratuais, dados sujeitos a licença, URLs com tokens ou arquivos grandes que possam carregar conteúdo não autorizado.

Em caso de dúvida, manter o material fora do repositório público e registrar apenas um resumo sanitizado, a origem e o motivo da não publicação.
