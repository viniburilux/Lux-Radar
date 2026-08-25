# Contribuindo com o Lux Radar

## Antes de começar

Leia, nesta ordem:

1. [README.md](README.md);
2. [docs/PRODUCT_THESIS.md](docs/PRODUCT_THESIS.md);
3. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md);
4. [docs/GOVERNANCE.md](docs/GOVERNANCE.md);
5. as decisões em [docs/decisions](docs/decisions).

O objetivo é entender o problema antes de escolher a tecnologia.

## Como trabalhar

Crie uma branch curta e específica a partir de `main`:

```text
feat/signal-fixture
feat/opportunity-schema
fix/deduplication-rule
docs/reconstruction-001
```

Cada pull request deve resolver um problema pequeno e demonstrável. Evite misturar refatoração ampla, interface, ingestão, mudança de schema e integração externa no mesmo PR.

## Formato do pull request

Descreva:

- **Problema:** qual situação motivou a mudança?
- **Solução:** o que foi implementado?
- **Evidência:** qual caso, fonte ou experimento sustenta a decisão?
- **Escopo:** o que ficou deliberadamente fora?
- **Testes:** como a mudança foi verificada?
- **Riscos:** há impacto em licença, privacidade, segurança, custo ou proveniência?

## Critérios de aceite

Uma contribuição é considerada pronta quando:

- possui documentação suficiente para ser compreendida por outra pessoa;
- não inclui segredo, dado privado ou conteúdo sem autorização;
- preserva a proveniência da fonte usada;
- diferencia observado, inferido e hipotético;
- possui teste, fixture ou procedimento de validação adequado;
- não duplica uma capacidade já presente no TraceFoundry ou no pipeline PNCP sem justificativa;
- não transforma um protótipo em decisão arquitetural permanente sem registro;
- mantém compatibilidade com os schemas e contratos vigentes, ou inclui uma decisão de migração.

## Novas dependências

Antes de adicionar uma dependência, explique no PR:

1. qual problema ela resolve;
2. por que a biblioteca padrão ou um componente existente não basta;
3. licença e manutenção observáveis;
4. impacto de instalação e execução;
5. alternativa considerada.

Dependências que exigem credenciais, infraestrutura paga, proxy, dados privados ou serviços externos devem começar como proposta documentada, não como integração automática.

## Dados e fixtures

Fixtures devem ser pequenas, sanitizadas e reproduzíveis. Prefira URLs públicas, dados sintéticos ou exemplos mínimos. Não copie conversas privadas, nomes pessoais, telefones, tokens, documentos internos, Parquets ou dumps de bases sem autorização explícita.

Quando um caso real for importante para o experimento, publique apenas uma versão sanitizada e mantenha o material original fora deste repositório.

## Mudanças de contrato

Alterações em `schemas/` podem afetar todos os consumidores. O PR deve incluir:

- motivo da alteração;
- exemplo antes/depois;
- compatibilidade retroativa;
- estratégia de migração;
- atualização da documentação;
- decisão em `docs/decisions/`, quando a alteração for estrutural.

## Regra de ouro

> Construa o menor componente que testa a hipótese. Não transforme uma hipótese em infraestrutura definitiva antes de observar o caso real.
