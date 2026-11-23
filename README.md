# CredFácil

Consulta de crédito e recomendação de maquininha para vendedores de campo, com dados públicos, regras explicáveis e interface acessível.

Projeto do time ResenhaAI vs EntrosaGPT no Hack Brasil 2026, trilha **Pagamentos & finanças**.

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
- Site no Netlify e API no Render, com deploy automático da `main` (ver [`docs/DEPLOY.md`](docs/DEPLOY.md)).
- Acessibilidade WCAG 2.1 AA: rótulos, leitor de tela, alto contraste e entrada por voz com conferência.

Detalhes em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) e [`docs/PRODUTO.md`](docs/PRODUTO.md).

## Dados e privacidade

- Fontes públicas de dados de empresas (CNPJ) e séries do Banco Central. Lista e limites em [`docs/DADOS.md`](docs/DADOS.md).
- Nenhum dado pessoal real. A demo usa uma lista de CNPJs de demonstração, e dados de sócios, e-mails e telefones são descartados.

## Como rodar

O projeto tem duas partes: a API (Python, pasta `api/`) e o site (Next.js, pasta `web/`).

### API

Precisa de Python 3.12 ou mais novo. Da raiz do repositório:

```powershell
# Windows (PowerShell). Se "python" não for reconhecido, troque por "py".
python -m venv .venv
# Só na primeira vez, se o PowerShell disser que a execução de scripts está desabilitada:
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.venv\Scripts\Activate.ps1
pip install -r api/requirements-dev.txt
```

```bash
# macOS e Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements-dev.txt
```

Com o ambiente ativado, sempre a partir da raiz do repositório:

| Para quê | Comando |
| --- | --- |
| Subir a API em http://localhost:8000 | `cd api; python -m uvicorn app.main:app --reload` |
| Ver e testar as rotas no navegador | abrir http://localhost:8000/docs |
| Rodar lint, formatação e testes de uma vez | `python scripts/verificar.py` |
| Regenerar `api/openapi.json` depois de mudar o contrato | `python scripts/exportar_openapi.py` |

Hoje só `/v1/saude` responde de verdade. As outras rotas do contrato respondem "em construção" (`501`).

Configuração: por enquanto a API só usa `MODO_DEMO` (padrão `true`) e lê do ambiente, não do arquivo `.env`. Para mudar, defina antes de subir a API: `$env:MODO_DEMO="false"` no PowerShell ou `export MODO_DEMO=false` no macOS e Linux. As outras variáveis de `.env.example` entram quando as fontes e o banco forem ligados.

### Site

Precisa de Node.js 22. Em outro terminal, a partir da raiz:

```bash
cd web
npm install
npm run dev
```

Abra http://localhost:3000. O site chama a API em `http://localhost:8000`; para outro endereço, copie `web/.env.example` para `web/.env.local` e ajuste `NEXT_PUBLIC_API_URL`.

| Para quê | Comando (dentro de `web/`) |
| --- | --- |
| Conferir o código (lint, inclui regras de acessibilidade) | `npm run lint` |
| Gerar a versão de produção | `npm run build` |
| Testes no navegador, com axe (rode o build antes) | `npm run e2e` |
| Atualizar os tipos da API depois de mudar o contrato | `npm run tipos` |

Os testes no navegador usam o Playwright. Na primeira vez, instale o navegador com `npx playwright install chromium`.

## Como usamos IA

Usamos agentes de código com regras explícitas, skills e agentes de revisão do projeto, todos em [`AGENTS.md`](AGENTS.md), [`.claude/`](.claude) e [`docs/IA.md`](docs/IA.md). Toda mudança passa por revisão humana.

## Equipe

Felipe, Guilherme, Kayke e Amanda.

## Licença

A definir.

---

**English summary.** CredFácil helps field sales agents who distribute card terminals check a small merchant from a tax ID (CNPJ) typed or dictated by voice. It pulls public company data, computes an explainable rule-based risk band, recommends a terminal model and a *simulated* credit limit and fees, and sends the proposal to a back-office dashboard in real time. All credit figures are simulations. The UI follows WCAG 2.1 AA.
