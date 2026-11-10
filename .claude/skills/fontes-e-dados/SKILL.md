---
name: fontes-e-dados
description: Use ao mexer em chamadas a CNPJ ou Banco Central, cache, sanitização, fixtures, lista de CNPJs de demonstração ou dados fictícios do CredFácil. Aplica as regras de privacidade e de limites de uso.
---

# Fontes e dados

Leia `docs/DADOS.md` antes de começar. Ele tem as fontes aprovadas, os limites e a data dos testes.

## Regras

1. **Hosts fixos.** Só os de `docs/DADOS.md`. Nada de URL vinda da entrada do usuário.
2. **Valide antes de chamar.** CNPJ com formato e dígitos verificadores. Em `MODO_DEMO=true`, só CNPJs de `fixtures/cnpjs_demo.json`.
3. **Sanitize na entrada.** Descarte `members`, e-mails, telefones e endereço detalhado antes de guardar, logar ou devolver. Para MEI e empresário individual, oculte o nome.
4. **Respeite o limite.** A fonte de CNPJ aceita 5 consultas por minuto por IP. Use cache (TTL em `.env.example`) e não faça laço de consultas.
5. **Timeout e falha.** Timeout de 1,2 s. Se falhar, use o último dado em cache marcado "dado de DD/MM" ou devolva `502` claro. Nunca dado inventado.
6. **Não faça scraping.** Nada de coletar páginas de sites, nem contornar captcha ou limite.
7. **Não chame a API da Receita no Conecta gov.br.** É para órgãos públicos.
8. **Séries do Banco Central.** Confira nome, periodicidade e data do último ponto antes de usar. Não chame de "inadimplência" o que não foi confirmado.
9. **Taxas de maquininha.** O catálogo da demo é fictício e marcado como ilustrativo. Taxa real de provedor só com URL da fonte e data de coleta no próprio dado. Nunca preencha taxa de memória nem assuma Pix com taxa zero. O MDR do Banco Central é referência agregada e defasada, nunca taxa de provedor.

## Dados fictícios

- CNPJ fictício precisa ter dígitos verificadores válidos. Gere por script em `scripts/` e registre em `docs/DADOS.md`.
- Marque cada item de `fixtures/` com a origem (`real_empresa_grande` ou `ficticio`).
- Nomes, faturamentos e propostas de exemplo são inventados e marcados como exemplo.

## Antes de terminar

- Teste derrubando a fonte (timeout, erro) e confira o fallback.
- Confira nos logs e nas respostas que nenhum dado pessoal aparece.
- Atualize `docs/DADOS.md` se descobriu algo sobre uma fonte, com a data do teste.
