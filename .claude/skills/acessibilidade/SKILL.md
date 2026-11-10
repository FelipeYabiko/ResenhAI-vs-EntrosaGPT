---
name: acessibilidade
description: Use ao criar ou mudar qualquer tela, componente, cor ou texto de interface do CredFácil, incluindo o ditado por voz. Aplica o checklist WCAG 2.1 AA do projeto.
---

# Acessibilidade (WCAG 2.1 AA)

Leia `docs/ACESSIBILIDADE.md`. Ele tem o checklist completo. Resumo do que conferir em toda tela:

1. **Estrutura.** `lang="pt-BR"`, um `h1`, títulos em ordem, regiões (`header`, `main`).
2. **Campos.** `label` visível associado a cada campo. Placeholder não é rótulo.
3. **Teclado.** Tudo funciona sem mouse, com foco visível e ordem lógica.
4. **Contraste.** Texto 4,5:1, componentes 3:1. Use só as cores dos tokens aprovados. Informação nunca só por cor: a faixa de risco tem letra e texto.
5. **Leitor de tela.** Resultado em `aria-live="polite"`, erros em `role="alert"`, nova proposta na matriz anunciada sem roubar o foco.
6. **Voz.** O texto reconhecido aparece e é lido de volta antes de consultar. Digitar continua possível. Estado "Ouvindo" acessível.
7. **Linguagem.** Simples, sem jargão sem explicação. Aviso "Simulação. Não é oferta de crédito." em texto.
8. **Movimento.** Respeite `prefers-reduced-motion`.

## Como provar

- Percorra o fluxo só com teclado.
- Rode axe e Lighthouse na tela e corrija os erros.
- Verifique contraste das cores usadas.
- Teste com leitor de tela (NVDA ou VoiceOver) quando a tela for nova ou mudar muito.
- Zoom de 200% sem perder conteúdo.

No PR, escreva o que testou. Não escreva "acessível" sem ter feito os testes.
