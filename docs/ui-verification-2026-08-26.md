# Verificação local da interface — 26/08/2026

A página estática carregou em `http://127.0.0.1:4173/` com o release `weekly-local-20260825`, exibindo 11 fontes observadas e 204 oportunidades visíveis. Os filtros de pesquisa, domínio, território, tipo, status e prazo aparecem no viewport. O filtro de domínio foi populado com valores observados como biodiversity, climate, conservation, education, energy, financing, forest, innovation, nature, research, sustainability e water.

A abertura de um card exibiu o modal de detalhe com título, organização, tipo, domínios, território, prazo, financiamento, elegibilidade, última atualização, fonte, confiança, evidências e link para a fonte oficial. A primeira versão local está funcional; os candidatos genéricos aparecem como `UNKNOWN`/desconhecidos e com prazo não observado, de acordo com a limitação declarada do collector genérico. Isso é uma limitação de verificação de detalhe, não um erro de carregamento.

## URL temporária pública

A interface também carregou corretamente na URL temporária `https://4173-i4lmjgl63e7hjld9d17es-b251dc2e.us3.manus.computer/`, exibindo 11 fontes observadas, 226 oportunidades no release gerado pelo workflow manual e cards com filtros/detalhe. O GitHub Pages não pôde ser habilitado automaticamente porque o token da integração não possui a permissão administrativa necessária; as etapas de coleta, validação e commit do workflow passaram, mas `Configure Pages` falhou com `Resource not accessible by integration`.
