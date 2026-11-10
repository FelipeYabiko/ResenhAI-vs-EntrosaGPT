# Status do projeto

Documento vivo. Atualize depois de cada call ou decisão.

Última atualização: 10/11/2026.

Legenda: **Decidido** = o time confirmou. **Proposto** = sugestão para confirmar. **Em aberto** = ainda sem resposta.

## Decidido

- Participar do Hack Brasil 2026 em time de 4: Felipe, Guilherme, Kayke e Amanda.
- Comunicação pelo grupo "Hack BR" no Discord.
- Trilha: **Pagamentos & finanças**.
- Ideia: **CredFácil**, aprovada pelo time (informado pelo Felipe em 08/11). Detalhes em `docs/PRODUTO.md`. O documento original (POS-Intel) é a base; este repositório detalha o MVP e marca onde nos afastamos dele.
- Hospedagem: **Vercel** (informado pelo Felipe em 09/11). Pendente: teste de deploy com várias contas do GitHub (T-36, D-014) e confirmar API em Python, SSE e banco na Vercel.
- Haverá integrantes usando Gemini CLI. `GEMINI.md` importa o `AGENTS.md`; ver `docs/IA.md`.

## Propostas para confirmar

Ver `docs/DECISOES.md` para o motivo de cada uma.

| Tema | Proposta |
| --- | --- |
| Escopo do MVP | Fluxo de consulta, resultado, proposta e painel da matriz em tempo real, como em `docs/PRODUTO.md`. Nada novo depois de 23/11 |
| Fontes de dados | API pública de CNPJ (cnpja ou BrasilAPI, a testar) e referências do Banco Central (séries e MDR). API da Receita no Conecta gov.br fora (é para órgãos públicos). IBGE fora do MVP |
| Pontuação | Regras explicáveis, sem ML e sem LLM (D-003) |
| Simulador de economia | Do RFC "Comparador de Maquininhas": custo atual contra custo com a oferta, economia em reais por mês e por ano, custo de saída e referência do Banco Central. Afiliados e comparação por marca ficam fora (D-011, D-013) |
| Privacidade | Modo demo com lista de CNPJs e sanitização (D-005) |
| Stack | Next.js + TypeScript, FastAPI, Postgres, Server-Sent Events (ver `docs/ARQUITETURA.md`) |
| Pastas | Monorepo com `/web` e `/api`. Sem `/ml` |
| Papéis | Felipe: API, fontes, integrações e deploy. Kayke: pontuação, dados fictícios. Guilherme: web (agente e matriz). Amanda: UX, acessibilidade, vídeo e README |
| Organização do código | Contrato da API definido primeiro, `main` sempre funcionando com deploy automático, PR com revisão (ver `docs/PROCESSO.md`) |
| Modo de trabalho | Assíncrono na semana, check-in 2 ou 3 vezes no Discord, call no fim de semana, tarefas em GitHub Issues e Projects |
| Uso de IA | Livre, com `AGENTS.md`, skills e agentes de `.claude/` (ver `docs/IA.md`) |
| Cronograma | 09/11 fechar escopo e contrato. 10 a 16/11 fluxo principal. 17 a 23/11 integrar e congelar. 24 a 30/11 testes e vídeo (roteiro 26/11, gravação 28/11, envio 29/11) |
| Vídeo | Amanda responsável. Até 3 min, em inglês, produto funcionando (ver `docs/DEMO.md`) |
| Idioma | Código e commits em inglês, documentos e interface em português, vídeo em inglês |

## Em aberto

- Como o impacto é avaliado na trilha Pagamentos & finanças. O regulamento diz "conforme o que cada trilha define", mas não achei a definição. Perguntar a oi@hackbrasil.com (T-08).
- Vercel Hobby aceita deploy de commits de outras contas do GitHub? A documentação diz que só o dono dispara deploy. Testar (T-36). Plano B em D-004.
- Quem criou ou vai criar o repositório. Ele precisa ser criado do zero (sem fork nem histórico importado) depois de 04/11 às 21h.
- Licença do projeto (D-010).
- Séries do Banco Central: confirmar o que são 21083 e 20714 e achar séries mensais atuais. As séries trimestrais por estado que testei só têm dados até 2023 (T-04).
- Qual série do IBGE traz poder de compra e densidade comercial. Opcional.
- Premissas da pontuação: pesos, múltiplos de limite e taxas. Quem define: Kayke (T-05).
- Prazo para enviar o rascunho que libera os créditos do Devin e do Firecrawl. O e-mail da organização não informa. Perguntar a oi@hackbrasil.com.
- Lista de temas proibidos do FAQ do site, ainda não lida na íntegra.
- Quem é o agente: de uma credenciadora específica ou de um marketplace multi-provedor (D-012).
- Concorrentes. Há comparadores de maquininha online (por exemplo, calculadoradetaxas.com.br e simuladores do iDinheiro, vistos em resultados de busca; não abri as páginas) e ferramentas internas de credenciadoras (não pesquisadas). Olhar 3 ou 4 antes de afirmar qualquer diferencial.
- Recurso "Taxas de desconto (MDR) e volumetria" do Banco Central: nome do endpoint, campos e periodicidade (T-19).
- Taxas e faixas do catálogo de demonstração e premissas do simulador: quem define é o Kayke (T-05). São ilustrativas.
- Pix na maquininha: o RFC assume taxa zero. Conferir antes de usar esse valor em qualquer cálculo.
- Programas de afiliado: quais existem e quanto pagam. Só importa se o modelo de receita entrar no pitch.
- Vídeo, marcas: o catálogo da demo é fictício e sem marcas reais (AGENTS.md), mas a issue nº 8 e o `docs/roteiro.md` do Kayke usam Cielo, InfinitePay e Ton com taxas reais. Decidir: manter o catálogo fictício ou mostrar marcas reais com fonte e data na tela, em cada taxa (10/11, ver `docs/roteiro-unico-proposta.md`).
- Vídeo, quantidade: o roteiro do Kayke fala em "passar de fase" e créditos para abrir a empresa, e a seção "Próximos passos" fala em um rascunho de 3 minutos para liberar créditos. É um vídeo só ou dois (pitch para os créditos e entrega final do evento)? (10/11)
- Vídeo, idioma: inglês (preferido pelo evento) ou português (aceito). O roteiro do Kayke está em português e `docs/roteiro-video.md` em inglês, com tradução (10/11).

## Próximos passos

- [ ] T-00 a T-09 de `docs/BACKLOG.md`
- [ ] Todos aceitam os termos e preenchem cidade e UF em "Meus dados" no painel
- [ ] Criar o repositório público com README, `AGENTS.md`, `CLAUDE.md`, `.claude/` e `docs/`
- [ ] Publicar uma página simples em HTTPS
- [ ] No fim da call, gravar um vídeo de cerca de 3 minutos com todos aparecendo (rascunho para os créditos)
- [ ] Enviar o rascunho e liberar os créditos

## Como manter este arquivo

- Depois de cada call, quem conduziu atualiza "Decidido", move itens de "Proposto" ou "Em aberto" e registra no "Log".
- Pergunta nova entra em "Em aberto" com a data. Resolvida, sai de lá e vira "Decidido".
- Sugestão: cole as anotações da call no agente e peça para atualizar este arquivo. Revise o diff antes de fazer commit.

## Log

- 04/11: abertura do evento. Time montado pelo Discord com Guilherme, Kayke e Amanda.
- 05/11: aprendizados do evento presencial sobre uso de IA, incorporados ao `AGENTS.md`.
- 06/11: pacote de contexto criado (`AGENTS.md`, `CLAUDE.md`, `docs/`).
- 08/11: CredFácil aprovada pelo time. Fontes de dados testadas. Documentação de produto, arquitetura, dados, acessibilidade, processo, IA e backlog criada. Skills e agentes do projeto criados em `.claude/`.
- 08/11: RFC "Comparador de Maquininhas (Pós-Cred)" considerado. Proposta: absorver o simulador de custo, a métrica de economia e a referência do Banco Central no CredFácil; afiliados e comparação por marca ficam fora do MVP (D-011 a D-013). Documentos de produto, arquitetura, dados e backlog atualizados.
- 09/11: time decidiu hospedar na Vercel. Pesquisa: o plano grátis (Hobby) só permite deploy pelo dono da conta; plano B e teste em D-004, D-014 e T-36.
- 10/11: suporte a Gemini CLI (`GEMINI.md`, seção em `docs/IA.md`).
- 10/11: roteiro de fala do vídeo (`docs/roteiro-video.md`) e proposta de roteiro único junto com o do Kayke (`docs/roteiro-unico-proposta.md`). Três perguntas novas em "Em aberto": marcas, quantidade de vídeos e idioma.
