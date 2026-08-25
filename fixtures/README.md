# Fixtures públicas

As fixtures do Lux Radar devem ser pequenas, sanitizadas e suficientes para reproduzir um comportamento. Elas não são um espelho do acervo privado.

## Regras

Uma fixture pública pode conter:

- dados sintéticos;
- URLs públicas;
- textos já publicados em fontes públicas, quando o uso for compatível com os termos aplicáveis;
- exemplos anonimizados ou reescritos;
- timestamps e identificadores artificiais;
- evidências mínimas necessárias para um teste.

Uma fixture pública não deve conter:

- nomes, telefones ou mensagens privadas sem autorização;
- conteúdo de grupos de WhatsApp ou Telegram;
- tokens, cookies, credenciais ou URLs assinadas;
- Parquets, dumps, caches ou bases privadas;
- dados pessoais desnecessários;
- documentos de parceiros sem autorização de publicação.

## Identificadores

Use IDs artificiais e estáveis, por exemplo `sig-exp001-001`, `ev-exp001-001` e `opp-exp001-001`. Não use números de telefone, hashes de arquivos privados ou identificadores que revelem sistemas internos.

## Proveniência

Toda fixture baseada em uma fonte pública deve registrar a URL, a data de observação, o tipo de fonte e as limitações conhecidas. Uma fixture reescrita ou sintética deve declarar isso explicitamente.
