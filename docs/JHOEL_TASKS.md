# Backlog de colaboração — Jhoel

## Regra de trabalho

Jhoel e seu agente podem acelerar a implementação, mas o trabalho deve acontecer em unidades pequenas, revisáveis e compatíveis com a direção do Lux Radar.

> **Construa o módulo delimitado; documente a hipótese; preserve a proveniência; abra PR; não altere a ontologia silenciosamente.**

## Tarefas prontas para execução

| ID | Tarefa | Entrada | Saída | Critério de aceite |
|---|---|---|---|---|
| JH-001 | Criar fixtures offline dos três perfis | Respostas sanitizadas de API, HTML/PDF-link e portal | Arquivos de teste sem rede | Testes reproduzem sucesso, parcial, 403/404 e parse failure. |
| JH-002 | Melhorar parser FAPESB | HTML da listagem e detalhe | Claims de título, PDF, errata e cronograma | Cada claim aponta para observation/evidence; nenhum campo é inventado. |
| JH-003 | Melhorar parser BNDES/Funbio | Página institucional e chamada | Relações programa → parceiro → chamada → território | O parser preserva URLs e conflitos de prazo/status. |
| JH-004 | Implementar diff temporal | `observation_t1`, `observation_t2` | `temporal_diff.json` | Detecta campo alterado e lista os dois IDs. |
| JH-005 | Validar contratos públicos | Release privado | Gate automático | Schema validation passa e falha com mensagem clara quando há campo inválido. |
| JH-006 | Preparar fixture de interface PNCP | Manifest/registro autorizado e sanitizado | Exemplo JSON pequeno | `dataset_release`, hash, território e limitações preservados. |
| JH-007 | Criar adapter TraceFoundry | Opportunity/normalized record | Mapeamento declarativo | Matriz de compatibilidade atualizada; nenhum core reescrito. |
| JH-008 | Propor componente visual mínimo | Release validado | Tabela ou página simples | Interface consome release; não cria coleta própria nem dashboard complexo. |
| JH-009 | Testar deduplicação | Duas manifestações seguras | Relação de alias/duplicate | Motivo, confiança e reversibilidade registrados. |
| JH-010 | Documentar fonte nova | Fonte do inventário | Ficha com método e termos | URL, superfície, frequência, limites, licença e critério de falha presentes. |

## Tarefas que não entram agora

Não iniciar crawler universal, banco central, Neo4j, Kafka/NATS, bot de WhatsApp, bypass de Cloudflare, rotação de proxy, matching autônomo sofisticado, cópia de Parquets PNCP, ingestão de dados pessoais ou dashboard completo.

## Processo de contribuição

Cada tarefa deve sair em branch própria ou PR pequeno. O PR precisa indicar o problema, a fonte, o método, a entrada, a saída, os testes, a licença/termos, as limitações e o que deliberadamente ficou fora. Alterações de schema, ontologia ou fronteira público/privado exigem decisão registrada antes do merge.
