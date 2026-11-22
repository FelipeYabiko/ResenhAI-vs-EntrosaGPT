# Status do projeto

Documento vivo. Atualize depois de cada call ou decisão.

Última atualização: 17/11/2026.

Legenda: **Decidido** = o time confirmou. **Proposto** = sugestão para confirmar. **Em aberto** = ainda sem resposta.

## Decidido

- Participar do Hack Brasil 2026 em time de 4: Felipe, Guilherme, Kayke e Amanda.
- Comunicação pelo grupo "Hack BR" no Discord.
- Trilha: **Pagamentos & finanças**.
- Ideia: **CredFácil**, aprovada pelo time (informado pelo Felipe em 08/11). Detalhes em `docs/PRODUTO.md`. O documento original (POS-Intel) é a base; este repositório detalha o MVP e marca onde nos afastamos dele.
- Hospedagem: **site no Netlify e API no Render** (Felipe, 17/11; D-020, substitui a Vercel). Passo a passo em `docs/DEPLOY.md`. Pendente: criar os dois projetos e testar o deploy por outra conta do GitHub (#26).
- Protótipo da landing feito pela Amanda no Figma (17/11). Tarefas de código abertas como issues #12 a #26.
- Login e chat do protótipo ficam: "Entrar na demonstração" (Agente ou Matriz) e ajuda com respostas prontas, sem LLM (D-015).
- Catálogo da demo com marcas fictícias (D-016). Valores da landing vêm do simulador; até ele existir, ficam os do protótipo, marcados como ilustrativos (D-017).
- Telas que faltam no Figma são feitas seguindo a estética do protótipo (D-018).
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
| Contrato da API v1 | Escrito em `docs/ARQUITETURA.md` e em `api/openapi.json` (issue #12). A consulta só exige CNPJ e faturamento; sem mix ou taxas atuais, não há economia (D-019). Aguarda aprovação de Felipe, Guilherme e Kayke |
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
- Render grátis desliga a API após 15 min sem uso (fonte: fórum do Render, não conferido na página oficial). Conferir se o despertador agendado (`.github/workflows/despertar-api.yml`) mantém a API acordada e se o limite de horas do plano grátis comporta isso (#26).
- Quem criou ou vai criar o repositório. Ele precisa ser criado do zero (sem fork nem histórico importado) depois de 04/11 às 21h.
- Licença do projeto (D-010).
- Séries do Banco Central: confirmar o que são 21083 e 20714 e achar séries mensais atuais. As séries trimestrais por estado que testei só têm dados até 2023 (T-04).
- Qual série do IBGE traz poder de compra e densidade comercial. Opcional.
- Premissas da pontuação: pesos, múltiplos de limite e taxas. Quem define: Kayke (T-05).
- Prazo para enviar o rascunho que libera os créditos do Devin e do Firecrawl. O e-mail da organização não informa. Perguntar a oi@hackbrasil.com.
- Lista de temas proibidos do FAQ do site, ainda não lida na íntegra.
- Quem é o agente: de uma credenciadora específica ou de um marketplace multi-provedor (D-012).
- Concorrentes. Há comparadores de maquininha online (por exemplo, calculadoradetaxas.com.br e simuladores do iDinheiro, vistos em resultados de busca; não abri as páginas) e ferramentas internas de credenciadoras (não pesquisadas). Olhar 3 ou 4 antes de afirmar qualquer diferencial.
- No deploy, definir `CORS_ORIGENS` no Render com o endereço do site no Netlify (o padrão só libera `localhost:3000`). Propostas em memória somem quando o Render reinicia ou desliga a API por inatividade; aceitável na demo até existir o banco (#23, #26).
- Imagens do site (17/11): as maquininhas azuis no fundo laranja e o mascote vêm do Figma da Amanda. Confirmar com ela a origem e a licença de cada imagem. Uma foto de maquininhas brancas do protótipo ficou fora por parecer produto real de marca.
- Teto do faturamento na consulta (17/11): hoje a API aceita qualquer valor acima de zero. Definir um máximo no contrato (quem define: Kayke, junto com as premissas) e repetir no formulário.
- Faixa de risco sobre empresas reais (18/11): a lista da demo tem 4 estatais com nome (BB, Caixa, Petrobras, Correios). A tela e o PDF mostrariam uma faixa de risco e um limite calculados por nós com o nome real da empresa, o que pode ser lido como avaliação de crédito de verdade. Proposta: no vídeo e no fluxo principal, usar só os 3 fictícios; as estatais servem para mostrar a consulta à fonte. Alternativas: aviso "não é avaliação desta empresa" ou não gerar proposta para elas. Decidir com o time.
- CNPJ alfanumérico: a Receita Federal anunciou CNPJ com letras para inscrições novas a partir de julho de 2026 (não conferi a norma nem a regra do dígito). A validação de hoje (#14) aceita só 14 dígitos. Conferir no site da Receita e decidir se a demo precisa aceitar. Como a demo só aceita a lista de CNPJs de demonstração, o impacto é baixo (17/11).
- Recurso "Taxas de desconto (MDR) e volumetria" do Banco Central: nome do endpoint, campos e periodicidade (T-19).
- Taxas e faixas do catálogo de demonstração e premissas do simulador: quem define é o Kayke (T-05). São ilustrativas.
- Pix na maquininha: o RFC assume taxa zero. Conferir antes de usar esse valor em qualquer cálculo.
- Programas de afiliado: quais existem e quanto pagam. Só importa se o modelo de receita entrar no pitch.
- Nome das marcas fictícias do catálogo. O time pensou em nomes parecidos com os reais (ex.: "InfinitoPay"); recomendação: nomes que não lembrem marca real (D-016, 17/11).
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
- 17/11: protótipo do Figma recebido; issues #12 a #26 criadas; decisões D-015 a D-018.
- 17/11: contrato da API v1 com schemas, OpenAPI e testes de contrato (issue #12); proposta D-019.
- 17/11: esqueleto da API com servidor local, lint e um comando de verificação (issue #13).
- 17/11: validação de CNPJ na API, antes de qualquer outra etapa (issue #14). Pergunta nova: CNPJ alfanumérico.
- 17/11: propostas e eventos ao vivo na API, com a matriz recebendo a proposta em cerca de 15 ms no teste local (issue #23). Risco novo: eventos ao vivo na Vercel (resolvido pela D-020).
- 17/11: hospedagem trocada para Netlify (site) e Render (API), por causa do deploy por várias contas e do SSE (D-020). Configuração e passo a passo prontos (#26).
- 17/11: pasta `web/` criada (combinado com o Guilherme): Next.js, cores e fonte do Figma com contraste conferido, landing e formulário ligado à API. Testes no navegador com axe sem violações.
- 18/11: parte de dados da consulta (#16): limpeza da resposta da fonte de CNPJ e dados de demonstração gerados a partir dela. Ambiente da sessão liberado para `open.cnpja.com`.
- 18/11: API das decisões da matriz (pendência, aprovação, recusa), cada uma publicada como evento em tempo real (SSE); contrato em PDF fica para o próximo passo.
- 18/11: contrato simulado em PDF para proposta aprovada (RF-09).
- 18/11: lista de CNPJs da demo (#15): 4 estatais conferidas na fonte e 3 fictícios (mercadinho, salão, loja) conferidos como inexistentes. Descoberto que o CNPJ de exemplo 11.222.333/0001-81 é de uma associação real; trocado nos testes.
- 19/11: núcleo do simulador de economia (#18), com o caso de referência do RF-11 e o exemplo da landing conferidos em teste. Catálogo, taxa do Pix e antecipação continuam com o Kayke.
