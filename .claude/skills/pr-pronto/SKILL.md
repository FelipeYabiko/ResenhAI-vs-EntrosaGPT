---
name: pr-pronto
description: Use antes de dizer que uma tarefa terminou ou de abrir um pull request no CredFácil. Roda a verificação de pronto do projeto e só declara sucesso com evidência.
---

# PR pronto

Não diga "pronto" sem evidência. Faça, nesta ordem:

1. **Critério de aceite.** Releia o da tarefa em `docs/BACKLOG.md` ou na Issue. Diga, item a item, como foi verificado.
2. **Testes.** Rode os testes das pastas que mudou e cole o resultado. Falhou? Corrija o código, não o teste.
3. **Lint e build.** Rode e cole o resultado.
4. **Fluxo real.** Abra o app e percorra o fluxo que mexeu. Se não puder abrir o navegador, diga isso claramente em vez de supor.
5. **Segredos e dados.** Procure no diff por chaves, `.env`, CPF, sócios, e-mail, telefone. Nada disso entra.
6. **Simulação.** Todo limite, taxa e aprovação mostrados dizem "Simulação".
7. **Acessibilidade.** Mexeu em tela? Siga a skill `acessibilidade` e registre o que testou.
8. **Dependências.** Nova? Justifique: existe, é a certa, licença compatível.
9. **Contrato.** Mexeu? Siga a skill `contrato-api`.
10. **Documentos.** Atualize `docs/STATUS.md` e `docs/DECISOES.md` se mudou decisão ou pergunta em aberto.
11. **Revisão.** Peça o agente `revisor` e, se tocou entrada de dados ou chamadas externas, o agente `seguranca`.

## Resposta final

Entregue: o que mudou, como foi verificado (com os resultados), o que ficou de fora e o que depende de outra pessoa. Se algo falhou ou não foi testado, diga primeiro.
