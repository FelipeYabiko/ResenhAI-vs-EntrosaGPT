# CredFácil

Consulta de crédito e recomendação de maquininha para vendedores de campo, com dados públicos, regras explicáveis e interface acessível.

Projeto do time [nome do time] no Hack Brasil 2026, trilha **Pagamentos & finanças**.

> Status: em construção. Este README será atualizado antes do envio (30/11/2026).

**Links** (preencher antes do envio): demo `[URL]` · vídeo `[URL]`

## O problema

Vendedores de campo que oferecem maquininhas e crédito a pequenos comerciantes enfrentam três gargalos: demora para avaliar o cliente, comunicação fragmentada com a mesa de análise e interfaces sem acessibilidade. O comerciante é quem espera pela resposta.

## O que o CredFácil faz

1. O vendedor digita ou dita o CNPJ do comerciante e informa o faturamento mensal estimado.
2. O sistema consulta fontes públicas e calcula uma faixa de risco por regras, mostrando por que chegou nela.
3. Compara o custo atual do comerciante com a oferta e mostra a economia em reais por mês (**estimativa**). Recomenda o modelo de máquina, um limite de crédito **simulado** e as taxas de antecipação **simuladas**.
4. O vendedor envia a proposta e a matriz a recebe em tempo real, podendo aprovar, recusar ou pedir pendência.

> Tudo que envolve limite, taxa e aprovação é **simulação**. Não é oferta de crédito.

## Como funciona por dentro

- API em FastAPI e web em Next.js. Banco Postgres.
- A pontuação é função pura, sem rede e sem LLM, com testes para cada regra. As premissas são do time e não têm validação estatística.
- Eventos em tempo real por Server-Sent Events.
- Acessibilidade WCAG 2.1 AA: rótulos, leitor de tela, alto contraste e entrada por voz com conferência.

Detalhes em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) e [`docs/PRODUTO.md`](docs/PRODUTO.md).

## Dados e privacidade

- Fontes públicas de dados de empresas (CNPJ) e séries do Banco Central. Lista e limites em [`docs/DADOS.md`](docs/DADOS.md).
- Nenhum dado pessoal real. A demo usa uma lista de CNPJs de demonstração, e dados de sócios, e-mails e telefones são descartados.

## Como rodar

Em construção. As instruções de instalação, variáveis de ambiente (`.env.example`) e testes entram aqui assim que o primeiro fluxo funcionar.

## Como usamos IA

Usamos agentes de código com regras explícitas, skills e agentes de revisão do projeto, todos em [`AGENTS.md`](AGENTS.md), [`.claude/`](.claude) e [`docs/IA.md`](docs/IA.md). Toda mudança passa por revisão humana.

## Equipe

Felipe, Guilherme, Kayke e Amanda.

## Licença

A definir.

---

**English summary.** CredFácil helps field sales agents who distribute card terminals check a small merchant from a tax ID (CNPJ) typed or dictated by voice. It pulls public company data, computes an explainable rule-based risk band, recommends a terminal model and a *simulated* credit limit and fees, and sends the proposal to a back-office dashboard in real time. All credit figures are simulations. The UI follows WCAG 2.1 AA.
