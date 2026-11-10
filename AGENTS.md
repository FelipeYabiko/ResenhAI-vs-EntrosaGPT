# Regras para agentes neste repositório

Projeto **CredFácil** no Hack Brasil 2026. Este repositório é **público** e o código é avaliado por jurados.

## Leia antes de começar

1. `docs/STATUS.md`: o que está decidido, o que é só proposta e o que está em aberto.
2. `docs/PRODUTO.md`: o que o produto faz, o escopo do MVP e o que fica de fora.
3. `docs/ARQUITETURA.md`: módulos, contrato da API, pastas e modelo de dados.
4. `docs/DADOS.md`: fontes de dados, limites e regras de privacidade.

Consulte só quando a tarefa precisar: `docs/ACESSIBILIDADE.md`, `docs/PROCESSO.md`, `docs/IA.md`, `docs/DECISOES.md`, `docs/BACKLOG.md`, `docs/CONTEXT.md` (regras do evento) e `docs/RESEARCH.md` (pesquisa de mercado).

Se a tarefa depender de algo marcado como **em aberto** no `docs/STATUS.md`, pare e pergunte. Não decida sozinho.

## Prioridades

1. A demo funciona de ponta a ponta. Um fluxo principal completo vale mais que várias funcionalidades pela metade.
2. O código é lido por jurados: simples, legível, com README que funciona para quem nunca viu o projeto.
3. Nada de funcionalidade fora do escopo do MVP definido em `docs/PRODUTO.md`.
4. Acessibilidade (WCAG 2.1 AA) faz parte de pronto, não é enfeite no fim.
5. Use IA para ganhar velocidade, mas revise, teste e entenda o que foi gerado.

## O que o agente NÃO deve fazer

- Não use dados reais de pessoas. Nunca busque, guarde, mostre ou registre em log CPF, sócios, e-mails ou telefones de terceiros.
- Não chame a API CNPJ oficial da Receita (Conecta gov.br). Ela é para órgãos públicos. Use só as fontes listadas em `docs/DADOS.md`.
- Não faça scraping de sites, nem contorne captcha ou limites de uso. Respeite o limite de cada fonte.
- Não apresente nada como crédito real. Todo limite, taxa e "pré-aprovação" é **simulação** e deve aparecer assim na interface, na API e no vídeo.
- Não invente números, estatísticas, taxas oficiais, regras legais ou nomes de bibliotecas. Se não sabe, diga que não sabe e aponte como conferir.
- Não coloque taxas reais de maquininha sem URL da fonte e data de coleta. O catálogo da demo é fictício e marcado como ilustrativo, sem marcas reais. Nunca preencha taxa de memória, nem assuma Pix com taxa zero.
- Não apresente a economia simulada como resultado real. São dados de exemplo e estimativas do comerciante.
- Não prometa precisão do modelo. A pontuação é por regras explicáveis. Não há dados reais de inadimplência para validar acerto.
- Não use LLM para calcular pontuação, limite, taxa ou economia. Cálculo é código determinístico e testado.
- Não esconda falha com dado falso. Se uma fonte cair, devolva o último dado em cache marcado como tal, ou um erro claro. Nunca dado inventado fingindo ser real.
- Não faça commit de `.env`, chaves, tokens ou dados pessoais. Não leia esses arquivos.
- Não altere nem apague testes para fazer o build passar.
- Não reorganize pastas, renomeie módulos públicos nem mude o contrato da API sem pedir. Contrato muda primeiro em `docs/ARQUITETURA.md` e no OpenAPI.
- Não adicione dependência sem justificar no PR.
- Não faça push na `main`, não use `--force` e não apague branches que não criou.
- Não copie código de repositórios anteriores ao evento. Código aberto público só com licença compatível e menção da origem no commit.
- Não deixe a interface sem rótulos, foco visível ou contraste mínimo. Veja `docs/ACESSIBILIDADE.md`.

## Segurança e dados

- Chaves entram só por variável de ambiente. Mantenha `.env.example` sem valores reais.
- Nenhum segredo no front-end. Variáveis `NEXT_PUBLIC_*` são públicas.
- Toda query SQL usa parâmetros. Nunca f-string nem concatenação.
- Valide todo CNPJ de entrada (formato e dígitos verificadores) antes de qualquer chamada externa.
- Chamadas externas só para os hosts fixos de `docs/DADOS.md`, com timeout e tratamento de erro.
- Só dados sintéticos, de fixtures ou de empresas (CNPJ) na lista de demonstração. Pagamentos e crédito só como simulação.
- Agente sem acesso a produção. Credenciais de teste, com o menor privilégio possível.

## Código

- Código e commits em inglês, documentos e textos da interface em português do Brasil (proposta; ver `docs/DECISOES.md`).
- Commits no padrão Conventional Commits. Veja `docs/PROCESSO.md`.
- A pontuação mora em `api/scoring/`, é função pura (sem rede, sem banco) e tem testes para cada regra.
- Respeite a estrutura de pastas de `docs/ARQUITETURA.md`.
- Todo código é novo. Biblioteca, framework e starter kit públicos são permitidos, respeitando a licença.

## Skills e agentes do projeto

Em `.claude/skills/` (chame por `/nome` ou deixe o agente escolher pela descrição):

| Skill | Use quando |
| --- | --- |
| `contrato-api` | Criar ou mudar endpoint, evento ou tipo compartilhado entre `/api` e `/web` |
| `fontes-e-dados` | Mexer em chamadas a CNPJ ou Banco Central, cache, fixtures ou dados fictícios |
| `acessibilidade` | Criar ou mudar qualquer tela, componente ou texto da interface |
| `pr-pronto` | Antes de dizer que terminou ou de abrir PR |
| `demo-e-video` | Preparar dados de demo, roteiro ou gravação do vídeo |

Em `.claude/agents/`: `revisor` (revisão de código contra as regras do projeto) e `seguranca` (segredos, dados pessoais, entrada e chamadas externas). Peça: "use o agente revisor nas mudanças desta branch".

### Se você não é o Claude Code (Gemini CLI, Codex, Cursor, Copilot, chat)

- `GEMINI.md` e `CLAUDE.md` só importam este arquivo (`@AGENTS.md`). As regras daqui valem para qualquer ferramenta.
- Skills e agentes são arquivos de texto comuns. Quando a tarefa casar com a coluna "Use quando", abra `.claude/skills/<nome>/SKILL.md` e siga as instruções. Para revisar, leia `.claude/agents/revisor.md` (depois `seguranca.md`) e aplique ao diff da branch, sem editar nada.
- As travas de `.claude/settings.json` (não ler `.env`, não dar push forçado) só funcionam no Claude Code. Nas outras ferramentas, vale o que está escrito aqui: não leia `.env`, não use `--force`, não faça push na `main`. A proteção da `main` no GitHub vale para todos.

## Autonomia proporcional ao impacto

| Nível | O que o agente faz | Controle |
| --- | --- | --- |
| Sugerir | Autocomplete e rascunhos | Livre |
| Executar | Rodar código em sandbox | Revisar o resultado |
| Integrar | Trabalhar em branch própria e abrir PR | Aprovação humana. Agente nunca faz push direto na main |
| Produção | Nada | Bloqueado por padrão |

## Antes de dizer que terminou

Prove, não presuma. Use a skill `pr-pronto`.

- Rode testes, lint e build e cole o resultado no PR.
- Abra o app e percorra o fluxo que você mexeu.
- Confira o critério de aceite da tarefa em `docs/BACKLOG.md`. Se não houver um verificável, peça antes de começar.
- Segredos e dados pessoais ficaram fora do código, dos logs e do contexto?
- Dependências, permissões e licenças foram revisadas?
- Se mexeu em tela: passou pelo checklist de acessibilidade?
- Alguém do time consegue explicar o que mudou? Se ninguém consegue, não faz merge.

## Memória do projeto

Se a sua tarefa mudar uma decisão, resolver uma pergunta em aberto ou criar uma nova, inclua a atualização de `docs/STATUS.md` (e de `docs/DECISOES.md`, se for decisão) no mesmo PR.
