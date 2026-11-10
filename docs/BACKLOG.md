# Backlog inicial

Tarefas para começar. Cada uma vira uma Issue do GitHub, com uma pessoa responsável. Os donos são propostas: confirme com cada um. Datas seguem os marcos de `docs/PROCESSO.md`.

Legenda de tamanho: P (até meio dia), M (1 dia), G (2 dias ou mais).

## Preparação (até 09/11)

| ID | Tarefa | Dono | Tam. | Critério de aceite |
| --- | --- | --- | --- | --- |
| T-00 | Criar o repositório público novo (depois de 04/11 às 21h), com README, `AGENTS.md`, `CLAUDE.md`, `.claude/`, `docs/` no primeiro commit | Felipe | P | Repositório público, sem fork nem histórico importado, com os arquivos do pacote |
| T-01 | Proteger a `main` (PR obrigatório e uma aprovação) e convidar os 3 colegas | Felipe | P | Push direto na `main` é recusado |
| T-02 | Todos aceitam os termos e preenchem cidade e UF no painel do evento; cadastrar Kayke e Amanda no time | Todos | P | Os 4 aparecem no painel |
| T-03 | Escrever o contrato da API v1 (`docs/ARQUITETURA.md` e esqueleto do OpenAPI) | Felipe, revisão de Guilherme e Kayke | M | Os 3 aprovam o contrato; exemplos de JSON válidos |
| T-04 | Testar à mão as fontes: CNPJ (cnpja e BrasilAPI) e séries do Banco Central. Confirmar nome e escopo das séries 21083 e 20714; achar séries mensais atuais | Felipe | M | `docs/DADOS.md` atualizado com data, campos e limites; escolha entre cnpja e BrasilAPI registrada |
| T-05 | Primeira versão das regras de pontuação, do catálogo de demonstração e da fórmula do simulador de custo, com a tabela de premissas | Kayke | M | `api/scoring/config.yaml` com cada premissa comentada; o caso de referência (economia de R$ 169,80) conferido à mão; casos de teste em papel |
| T-06 | Wireframes das telas de consulta, resultado e painel; tokens de cor com contraste 4,5:1 conferido | Amanda | M | Telas aprovadas pelo time; tabela de cores com razões de contraste |
| T-07 | Decidir hospedagem (D-004) e criar projetos de web, API e banco | Felipe e Guilherme | M | URL HTTPS com uma página "olá" no ar |
| T-08 | Enviar à organização a dúvida sobre como o impacto é avaliado na trilha | Felipe | P | E-mail enviado a oi@hackbrasil.com; resposta registrada em `docs/STATUS.md` |
| T-09 | Gerar a lista de CNPJs de demonstração (empresas grandes e fictícios válidos) | Kayke | P | `fixtures/cnpjs_demo.json` com origem de cada CNPJ |

## Semana 1: fluxo principal (10 a 16/11)

| ID | Tarefa | Dono | Tam. | Critério de aceite |
| --- | --- | --- | --- | --- |
| T-10 | `POST /v1/consultas` com fixtures: valida CNPJ, devolve resultado completo | Felipe | G | RF-01, RF-03 com fixtures; testes passam |
| T-11 | Motor de pontuação v0 com testes por regra | Kayke | G | RF-04: mesmo entrada dá mesma saída; cada regra tem teste |
| T-12 | Simulador de custo, recomendação de máquina, limite e taxas (simulação) | Kayke | G | RF-05, RF-11, RF-12; o caso de teste de referência passa; aviso de simulação no retorno |
| T-13 | Tela de consulta e resultado do agente | Guilherme | G | Fluxo funciona com a API de fixtures; checklist de acessibilidade |
| T-14 | Propostas e eventos: `POST /v1/propostas`, `GET /v1/eventos` (SSE) | Felipe | G | RF-06: proposta aparece em outra aba sem recarregar |
| T-15 | Painel da matriz com lista em tempo real | Guilherme | G | RF-06, RF-07 |
| T-16 | Esqueleto de deploy automático com a `main` | Felipe | M | Merge na `main` publica em HTTPS |
| T-17 | Ditado de CNPJ por voz (v0) com conferência na tela | Guilherme | M | RF-02; alternativa digitada funciona |
| T-18 | Design visual aplicado nas duas telas, com a economia em reais em destaque | Amanda | G | Mocks entregues e tokens no código |
| T-19 | Referência de mercado do Banco Central (MDR): testar o recurso e mostrar "acima ou abaixo da média", se funcionar | Felipe | M | RF-13; se o recurso não funcionar até 16/11, cortar e registrar em `docs/STATUS.md` |

## Semana 2: integrar e congelar (17 a 23/11)

| ID | Tarefa | Dono | Tam. | Critério de aceite |
| --- | --- | --- | --- | --- |
| T-20 | Fontes reais com cache, timeout e fallback | Felipe | G | RF-10; teste derrubando a fonte |
| T-21 | Sanitização e modo demo | Felipe | M | Sócios, e-mail e telefone nunca aparecem; MEI sem nome |
| T-22 | Aprovar, recusar, pedir pendência e contrato simulado em PDF | Guilherme e Felipe | G | RF-07, RF-08, RF-09 |
| T-23 | Auditoria de acessibilidade completa (teclado, leitor de tela, axe, zoom) | Amanda | G | Checklist de `docs/ACESSIBILIDADE.md` sem pendência |
| T-24 | Calibrar as premissas e revisar as explicações dos fatores | Kayke | M | Explicações em linguagem simples; premissas documentadas |
| T-25 | Teste de ponta a ponta do fluxo principal | Guilherme | M | Playwright cobre consulta até aprovação |
| T-26 | **Congelar o escopo (23/11)** | Todos | P | Nada novo depois; o que sobrar vira "próximos passos" |
| T-28 | (Opcional) 5 a 10 conversas anônimas com comerciantes para medir intenção de troca | Amanda e Guilherme | G | Só o número agregado, sem extrato nem dado pessoal; nada disso aparece no vídeo |

## Semana 3: teste, vídeo e envio (24 a 30/11)

| ID | Tarefa | Dono | Tam. | Critério de aceite |
| --- | --- | --- | --- | --- |
| T-30 | Correção de bugs e teste em outro navegador e no celular | Todos | G | Lista de bugs vazia no fluxo principal |
| T-31 | Roteiro do vídeo (até 26/11) | Amanda | M | `docs/DEMO.md` aprovado pelo time |
| T-32 | README final para jurados | Felipe e Amanda | M | Quem nunca viu o projeto entende, roda e acha o vídeo |
| T-33 | Gravação do vídeo, com todos na tela (até 28/11) | Amanda | G | Vídeo de até 3 min, sem login, produto funcionando |
| T-34 | Conferir a lista de envio e submeter (até 29/11) | Felipe | P | Repositório público, demo no ar, vídeo, README, todos no painel |
| T-35 | Manter o repositório público e a demo no ar até 15/12 | Felipe | P | Verificação semanal |
| T-36 | Teste de deploy na Vercel com várias contas (fazer junto com T-07) | Felipe e mais uma pessoa | P | Outra pessoa abre um PR com uma linha; o Felipe faz o merge; o deploy de produção sai. Repetir com um commit de outra conta numa branch e ver se o preview sai. Se bloquear, aplicar o plano B de D-004 |

## Quando surgir tarefa nova

Abra uma Issue com: o que, por quê, critério de aceite, dono. Se aumentar o escopo do MVP, discuta antes com o time e registre em `docs/DECISOES.md`.
