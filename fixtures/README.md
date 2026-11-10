# Fixtures

Dados de demonstração e de teste. **Nada aqui pode ser dado pessoal real.**

Arquivos previstos:

- `cnpjs_demo.json`: lista de CNPJs que a demo aceita (`MODO_DEMO=true`). Cada item tem `cnpj`, `apelido` e `origem` (`real_empresa_grande` ou `ficticio`). CNPJs fictícios têm dígitos verificadores válidos.
- `respostas_fontes/`: respostas já sanitizadas das fontes para os CNPJs da lista, usadas em testes e como fallback.
- `faturamentos_exemplo.json`: faturamentos mensais de exemplo, marcados como exemplo.

Regras completas em `docs/DADOS.md` e na skill `fontes-e-dados`.
