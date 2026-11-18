# Fixtures

Dados de demonstração e de teste. **Nada aqui pode ser dado pessoal real.**

Arquivos previstos:

- `cnpjs_demo.json`: lista de CNPJs que a demo aceita (`MODO_DEMO=true`). Cada item tem `cnpj`, `apelido` e `origem` (`real_empresa_grande` ou `ficticio`). CNPJs fictícios têm dígitos verificadores válidos.
- `respostas_fontes/<cnpj>.json`: dados de empresa já sanitizados (só os campos do contrato), gerados com `scripts/gerar_fixture_empresa.py`. Usados em testes e como dado da demo. Hoje: `00000000000191` (empresa grande, permitido por `docs/DADOS.md`).
- `faturamentos_exemplo.json`: faturamentos mensais de exemplo, marcados como exemplo.

Regras completas em `docs/DADOS.md` e na skill `fontes-e-dados`.
