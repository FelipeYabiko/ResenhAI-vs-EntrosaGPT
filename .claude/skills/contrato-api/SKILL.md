---
name: contrato-api
description: Use ao criar ou mudar endpoint, evento, schema ou tipo compartilhado entre /api e /web do CredFácil. Garante que o contrato muda primeiro, com exemplo, OpenAPI e tipos do front.
---

# Contrato da API

O contrato é o acordo entre `/api` (Felipe e Kayke) e `/web` (Guilherme). Ele muda **antes** do código.

## Passos

1. Leia a seção "Contrato da API" de `docs/ARQUITETURA.md` e o `api/openapi.json` atual, se existir.
2. Escreva a mudança em `docs/ARQUITETURA.md`: método, caminho, entrada, saída, erros e um exemplo de JSON. Campos em `snake_case` sem acento, datas em ISO 8601, erros no formato `{"erro": {"codigo", "mensagem"}}`, mensagens em português.
3. Se o campo mostrar limite, taxa ou aprovação, inclua o aviso de simulação.
4. Implemente os schemas no FastAPI (Pydantic) com o mesmo exemplo e gere o OpenAPI.
5. Regenere os tipos do `/web` a partir do OpenAPI. Não escreva tipos de API à mão.
6. Escreva ou atualize um teste de contrato: a resposta real bate com o schema.
7. No PR, marque "mexeu no contrato" e peça revisão de Felipe e Guilherme.

## Regras

- Mudança que quebra quem já usa (renomear ou remover campo) exige combinar com o dono do outro lado antes.
- Nunca devolva dado pessoal (sócios, e-mail, telefone) nem o corpo cru de uma fonte externa.
- Nunca ponha campo de cálculo no front. Pontuação, limite e taxa vêm da API.
- Se a mudança afetar uma pergunta em aberto, pare e pergunte (veja `docs/STATUS.md`).
