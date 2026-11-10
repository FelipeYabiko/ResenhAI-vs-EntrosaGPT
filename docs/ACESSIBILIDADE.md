# Acessibilidade (WCAG 2.1 nível AA)

Acessibilidade é um dos diferenciais do produto e aparece no vídeo. Vale como critério de pronto para qualquer tela. Ferramentas automáticas pegam só parte dos problemas: o teste com teclado e leitor de tela é obrigatório.

## Checklist por tela

**Estrutura**
- [ ] `lang="pt-BR"` na página. Um `h1` por tela, títulos em ordem, regiões (`header`, `main`, `nav`).
- [ ] Todo campo tem `label` visível associado. Placeholder não substitui rótulo.
- [ ] Botões são `button`, links são `a`. Nome acessível claro ("Consultar CNPJ", não "Enviar").

**Teclado e foco**
- [ ] Tudo funciona só com teclado, na ordem lógica. Sem armadilha de foco.
- [ ] Foco sempre visível, com contraste suficiente.
- [ ] Alvos de toque com pelo menos 44 por 44 px (boa prática para uso em campo, com uma mão).

**Cor e contraste**
- [ ] Texto normal: contraste mínimo 4,5:1. Texto grande e componentes de interface: 3:1.
- [ ] Informação nunca só por cor. A faixa de risco aparece com letra e texto ("Faixa B, risco moderado"), não só com verde e amarelo.
- [ ] Modo de alto contraste disponível e testado.
- [ ] Respeitar `prefers-reduced-motion`.

**Leitor de tela**
- [ ] Resultado da consulta anunciado com `aria-live="polite"`. Erros com `role="alert"`.
- [ ] No painel da matriz, nova proposta é anunciada ("Nova proposta recebida") sem roubar o foco.
- [ ] Gráficos e ícones com alternativa em texto. Decorativos com `aria-hidden`.
- [ ] Tabelas com `th` e `scope`.

**Voz**
- [ ] O botão de ditado tem nome acessível e estado ("Ouvindo").
- [ ] O texto reconhecido aparece na tela e é lido de volta ("Você disse: ...") para conferência antes de consultar.
- [ ] Digitar continua possível. Se o navegador não suportar voz, o botão some ou explica por quê.
- [ ] Números ditados são normalizados (aceitar "zero zero", pontos e barras) e validados.

**Conteúdo**
- [ ] Linguagem simples, sem jargão sem explicação (explicar "antecipação de recebíveis" na primeira vez).
- [ ] Aviso "Simulação. Não é oferta de crédito." visível, em texto, não só em imagem.

## Como testar

1. Só teclado: percorrer o fluxo completo sem mouse.
2. Leitor de tela: NVDA no Windows (gratuito) ou VoiceOver no macOS, no fluxo completo.
3. Automático: axe (extensão do navegador) e Lighthouse em cada tela. Corrigir tudo que for erro.
4. Contraste: conferir as cores do design em um verificador de contraste antes de implementar. Amanda define os tokens de cor já aprovados.
5. Zoom de 200% sem perder conteúdo nem funcionalidade.

Registre no PR o que foi testado. Para a skill de apoio, use `acessibilidade`.
