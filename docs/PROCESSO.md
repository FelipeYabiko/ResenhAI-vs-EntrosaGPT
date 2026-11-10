# Processo de trabalho

Proposta do time. Ajuste com o grupo e registre mudanças em `docs/DECISOES.md`.

## Branches

- `main` sempre funciona e é publicada. Ninguém faz push direto nela. Ative a proteção da branch no GitHub: exigir pull request e uma aprovação.
- Deploy na Vercel Hobby (D-014, proposta): só o dono da conta (Felipe) dispara deploy. Os outros trabalham em branch e PR; o Felipe faz o merge. Confira o autor do commit de merge no primeiro teste (T-36). O `git config user.email` de cada pessoa deve ser o e-mail verificado no GitHub.
- Branch por tarefa: `tipo/descricao-curta`, por exemplo `feat/consulta-cnpj`, `fix/validacao-cnpj`, `docs/arquitetura`.
- Branch viva por no máximo 2 dias. PR pequeno é revisado mais rápido.

## Commits

Conventional Commits, em inglês:

```
feat(api): add CNPJ query endpoint
fix(web): keep focus on result after lookup
docs: update data sources
test(scoring): cover inactive company gate
chore: add env example
```

Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`. Um assunto por commit. Código aberto público copiado leva a origem na mensagem.

## Pull request

- Use o modelo em `.github/pull_request_template.md`.
- Título no formato de commit. Descreva o que mudou, como testar e cole o resultado de testes, lint e build.
- Mexeu em pasta de outra pessoa? Ela revisa. Mexeu no contrato da API? Felipe e Guilherme revisam. Mexeu em `/api/scoring`? Kayke revisa.
- Mexeu em tela? Cole o resultado do checklist de acessibilidade.
- Quem abriu não faz o próprio merge sem uma aprovação.

## Definição de pronto

- [ ] O critério de aceite da tarefa passa.
- [ ] Testes, lint e build passam.
- [ ] O fluxo foi aberto e percorrido no navegador.
- [ ] Sem segredo, dado pessoal ou número inventado.
- [ ] Acessibilidade conferida (se mexeu em tela).
- [ ] Documentação atualizada (`STATUS`, `ARQUITETURA`, `DADOS`, `DECISOES`, conforme o caso).
- [ ] Alguém além de quem escreveu consegue explicar a mudança.

## Rotina

- Assíncrono durante a semana. Check-in no Discord 2 ou 3 vezes por semana: o que fiz, o que vou fazer, o que me trava.
- Call no fim de semana para alinhar e decidir.
- Tarefas em GitHub Issues e Projects, a partir de `docs/BACKLOG.md`. Uma pessoa por tarefa.
- Depois de cada call, atualizar `docs/STATUS.md` (quem conduziu) e `docs/DECISOES.md` (se houve decisão).

## Marcos

| Data | Marco |
| --- | --- |
| 09/11 | Trilha, ideia, escopo e contrato da API v1 fechados |
| 16/11 | Fluxo principal funcionando de ponta a ponta, mesmo que com fixtures |
| 23/11 | Fontes reais integradas, design aplicado, **escopo congelado** |
| 26/11 | Roteiro do vídeo pronto |
| 28/11 | Vídeo gravado |
| 29/11 | Envio (um dia antes do prazo de 30/11, 23h59) |

## Regras de ouro

- Congelou em 23/11, nada novo entra. Ideias novas vão para "próximos passos" do pitch.
- Travou por mais de 1 hora? Pede ajuda no Discord.
- Dúvida de regra do evento: oi@hackbrasil.com, não suposição.
