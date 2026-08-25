# Experimento 001 — Signal to Opportunity

## Objetivo

Testar se o Lux Radar consegue transformar sinais reais em oportunidades verificadas e acionáveis com menos ambiguidade do que o simples encaminhamento de links.

## Amostra

Selecionar de 10 a 20 casos reais recebidos pela rede. A amostra deve ser sanitizada antes de entrar no repositório público e pode incluir editais, chamadas públicas, grants, eventos, pesquisa, parcerias, financiamento e oportunidades de sustentabilidade.

## Unidade de análise

Cada caso deve conter, quando possível:

```text
case_id
signal
source_discovery
primary_source
evidence
canonical_opportunity
secondary_manifestations
status
context
match
next_action
outcome
```

## Procedimento

1. Registrar o sinal original em versão pública e sanitizada.
2. Identificar o que o sinal afirma e o que ele não informa.
3. Procurar a fonte primária sem assumir que o link inicial é suficiente.
4. Registrar páginas, PDFs ou respostas de API que sustentem os atributos.
5. Criar o registro canônico da oportunidade.
6. Relacionar manifestações secundárias sem apagar suas diferenças.
7. Classificar status, incertezas e limitações.
8. Registrar por que a oportunidade pode ser relevante para um perfil ou território.
9. Registrar a ação possível e, quando disponível, o resultado observado.

## Saída esperada

O experimento deve produzir:

- fixtures sanitizadas de sinais, evidências e oportunidades;
- um relatório de reconstrução por caso;
- uma tabela de campos recorrentes e exceções;
- uma lista de decisões de schema;
- uma medição inicial de latência, duplicação, verificação e ação;
- uma conclusão sobre o menor componente que vale automatizar.

## Resultados negativos

Registrar também quando:

- a fonte primária não for encontrada;
- o sinal estiver errado ou incompleto;
- a oportunidade estiver encerrada;
- houver evidência insuficiente;
- várias manifestações forem a mesma oportunidade;
- o matching não gerar interesse;
- nenhuma ação ocorrer.

## Critério de sucesso

O experimento será considerado útil se produzir uma representação mais confiável e acionável do que o sinal original e se revelar quais etapas exigem automação, revisão humana ou apenas documentação.
