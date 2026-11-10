# Como trabalhamos com IA neste projeto

O regulamento permite e recomenda o uso de IA. O que importa é a qualidade do que entregamos. Este guia vale para qualquer agente (Claude Code, Gemini CLI, Devin ou outro) e para quem usa chat.

## Princípios

1. **IA acelera, a gente responde pelo resultado.** Ninguém faz merge do que não sabe explicar.
2. **Contexto primeiro.** O agente começa lendo `AGENTS.md` e os documentos indicados lá. Em chat sem acesso ao repositório, cole o trecho relevante.
3. **Tarefa pequena, critério verificável.** Uma tarefa de `docs/BACKLOG.md` por vez, com o critério de aceite junto.
4. **Plano antes de código** quando a tarefa mexe em mais de um arquivo ou em contrato. Peça o plano, leia, corrija, só então autorize.
5. **Prove, não presuma.** Teste, lint, build e o fluxo aberto no navegador, não "deve funcionar".
6. **Segredos e dados reais ficam fora.** Nunca cole chave, `.env` ou dado pessoal em chat ou prompt.

## Como começar uma sessão com o agente

- No Claude Code (computador ou na nuvem, em claude.ai/code com o repositório conectado), cada tarefa em uma sessão e uma branch própria.
- Primeira mensagem sugerida: "Leia AGENTS.md e docs/STATUS.md. Tarefa: T-xx de docs/BACKLOG.md. Faça um plano antes de editar."
- Use as skills do projeto por nome (`/contrato-api`, `/acessibilidade`, `/pr-pronto`) ou deixe o agente escolher.
- Peça revisão a outro agente com contexto limpo: "Use o agente revisor nas mudanças desta branch" e depois "use o agente seguranca".
- Para tarefas arriscadas, comece em modo de plano (sem editar) e só depois libere edições.

## Usando Gemini CLI ou outra ferramenta

- Gemini CLI lê o `GEMINI.md` da raiz, que só importa o `AGENTS.md`. Para conferir, rode `/memory show` e veja se as regras de `AGENTS.md` aparecem. Se não aparecerem, avise o time.
- As skills e os agentes do projeto ficam em `.claude/`. Gemini CLI não lê essa pasta sozinho, então peça: "Leia `.claude/skills/pr-pronto/SKILL.md` e siga os passos". Para revisão: "Leia `.claude/agents/revisor.md` e revise o diff desta branch".
- As travas de `.claude/settings.json` só existem no Claude Code. Quem usa outra ferramenta segue as regras escritas no `AGENTS.md` por conta própria e nunca libera acesso a `.env`.
- Primeira mensagem sugerida: a mesma da seção acima, mais "Siga as regras do AGENTS.md e não edite `.claude/`".
- Nunca cole `.env`, chave ou dado pessoal em chat, em nenhuma ferramenta.

## Modelos de pedido

**Implementar**
> Tarefa T-xx (cole o critério de aceite). Leia docs/ARQUITETURA.md e docs/PRODUTO.md. Faça um plano com os arquivos que vai tocar. Não mude o contrato da API. Escreva os testes primeiro. No fim rode `pr-pronto`.

**Revisar**
> Revise o diff desta branch contra AGENTS.md. Procure: dado pessoal, segredo, chamada externa fora da lista, regra de pontuação sem teste, tela sem rótulo, número inventado. Liste achados por gravidade com arquivo e linha.

**Investigar uma fonte**
> Teste a fonte X à mão (um CNPJ da lista de demonstração) e me diga: campos retornados, tempo, limite de uso, termos. Não escreva código de produção ainda. Atualize docs/DADOS.md com data do teste.

**Preparar a demo**
> Use a skill demo-e-video. Monte a sequência de dados de exemplo para o roteiro do docs/DEMO.md e confira que cada passo funciona no ambiente publicado.

## Bons usos de IA aqui

- Rascunhar código, testes e documentação que alguém do time vai revisar.
- Gerar dados fictícios e fixtures, desde que marcados como fictícios.
- Revisar acessibilidade, segurança e consistência com o contrato da API.
- Resumir documentação de uma fonte (conferindo na fonte original).
- Acelerar a edição do vídeo e de textos da interface.

## Usos que não aceitamos

- IA decidindo pontuação, limite ou taxa. É regra em código, testada.
- Fato jurídico, financeiro ou número de mercado sem fonte conferida por uma pessoa.
- Dependência sugerida sem checar que o pacote existe, é o certo (cuidado com nomes parecidos) e tem licença compatível.
- Código copiado de projeto anterior ao evento.
- Agente com acesso a produção, chaves reais ou dados reais.

## Sinais de alerta no que a IA entrega

- Diz "pronto" sem ter rodado teste, lint ou build.
- Mexeu em teste para ele passar.
- Fez mais do que a tarefa pedia (novas telas, novas dependências, refatoração geral).
- Respondeu com números, taxas ou leis sem fonte.
- A interface funciona só com mouse ou sem rótulos.
- Resultado diferente a cada execução em algo que deveria ser determinístico (a pontuação).

## Transparência

No PR, uma linha: "IA usada em: ..., revisado por: ...". O README do projeto descreve como usamos IA. Isso ajuda os jurados a entender o processo e mostra maturidade.

## Créditos de ferramentas

Os créditos do evento (por exemplo Devin e Firecrawl) são opcionais e não dão nota. Firecrawl faz coleta de páginas web: **não** use para coletar dados de empresas ou de pessoas. As fontes do produto são as de `docs/DADOS.md`.

## Ferramentas pessoais

Cada pessoa pode ter plugins e skills próprios na sua conta. Eles não entram no repositório nem são necessários para trabalhar aqui. O que o projeto exige está em `AGENTS.md` e em `.claude/`.
