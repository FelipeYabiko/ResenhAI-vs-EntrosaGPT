# Deploy

Decisão D-020: **site no Netlify** e **API no Render**. Os dois publicam sozinhos a cada merge na `main`, e qualquer pessoa do time pode fazer o merge.

Os nomes dos botões podem mudar um pouco nos sites do Render e do Netlify. Se algo não bater, procure a opção mais parecida e anote aqui o nome certo.

## Ordem

1. API no Render (dá para fazer agora, depois do merge dos PRs da API).
2. Despertador da API no GitHub.
3. Site no Netlify (quando a pasta `/web` existir, issue #6).
4. Ligar um ao outro (`CORS_ORIGENS` e `NEXT_PUBLIC_API_URL`).
5. Teste com outra conta do GitHub (T-36, issue #26).

## 1. API no Render

A configuração está em `render.yaml`, na raiz do repositório. Faça o merge dos PRs da API antes, para o deploy sair da `main`.

1. Entre em https://render.com e clique em **Sign in with GitHub**.
2. Clique em **New** e depois em **Blueprint**.
3. Autorize o Render a ver o repositório `ResenhAI-vs-EntrosaGPT` e escolha esse repositório.
4. O Render mostra o serviço `credfacil-api`, lido do `render.yaml`. Ele pede o valor de `CORS_ORIGENS`:
   - se o site ainda não existe, escreva `http://localhost:3000` por enquanto;
   - depois do passo 4, troque pelo endereço do site.
5. Clique em **Apply** (ou **Deploy Blueprint**) e espere o primeiro deploy terminar. Leva alguns minutos.
6. Copie o endereço que o Render deu à API, algo como `https://credfacil-api.onrender.com`.
7. Confira no navegador:
   - `<endereço>/v1/saude` deve mostrar `{"status":"ok","modo_demo":true}`;
   - `<endereço>/docs` abre a página onde dá para testar as rotas.

O plano grátis desliga a API depois de uns 15 minutos sem uso. O primeiro acesso depois disso demora de 30 a 50 segundos. O passo 2 evita isso.

## 2. Despertador da API

O arquivo `.github/workflows/despertar-api.yml` chama a API a cada 10 minutos, de graça, pelo GitHub Actions.

1. No GitHub, abra o repositório e vá em **Settings**, depois **Secrets and variables**, depois **Actions**.
2. Na aba **Variables**, clique em **New repository variable**.
3. Nome: `API_URL`. Valor: o endereço do passo 1.6, sem `/` no fim.
4. Para testar: aba **Actions**, workflow **Despertar API**, botão **Run workflow**. Deve terminar com o ícone verde.

Cuidados:

- O agendamento só roda depois que o arquivo estiver na `main`.
- O plano grátis do Render tem um limite de horas por mês. Pelo que lembramos, cerca de 750 horas, o que uma API acordada o mês todo quase esgota (não conferido). **Não crie outro serviço grátis na mesma conta do Render.**
- O GitHub não garante o horário exato dos agendamentos, então ainda pode haver um atraso de vez em quando. **Antes de gravar o vídeo e antes da avaliação, abra `<endereço>/v1/saude` e espere responder.**

## 3. Site no Netlify

Só quando a pasta `/web` existir (issue #6).

1. Entre em https://app.netlify.com com a conta do GitHub.
2. Clique em **Add new site** (ou **Add new project**) e depois em **Import an existing project**.
3. Escolha **GitHub** e o repositório `ResenhAI-vs-EntrosaGPT`.
4. Em **Base directory**, escreva `web`. O Netlify reconhece o Next.js e preenche o resto.
5. Em **Environment variables**, crie `NEXT_PUBLIC_API_URL` com o endereço da API do passo 1.6.
6. Clique em **Deploy** e espere terminar.
7. Copie o endereço do site, algo como `https://credfacil.netlify.app`.

O repositório precisa continuar **público**. Pelo que pesquisamos, é isso que deixa qualquer pessoa do time disparar deploy no plano grátis do Netlify.

## 4. Ligar o site à API

1. No Render, abra o serviço `credfacil-api`, vá em **Environment** e troque `CORS_ORIGENS` pelo endereço do site do passo 3.7. Para liberar mais de um endereço, separe com vírgula.
2. Salve. O Render reinicia a API sozinho.
3. Abra o site e faça uma consulta. Se o navegador mostrar erro de CORS, confira se o endereço está igual, com `https://` e sem `/` no fim.

## 5. Teste com outra conta (T-36)

1. Outra pessoa do time abre um PR que muda uma linha (por exemplo, no README) e alguém aprova.
2. Quem não é dono da conta do Netlify nem do Render faz o merge.
3. Confira que o Render e o Netlify publicaram sozinhos (aba **Events** no Render, **Deploys** no Netlify).
4. Anote o resultado em `docs/STATUS.md`.

## O que ainda não está aqui

- Banco de dados: ainda não existe. Hoje as propostas ficam na memória da API e somem quando o Render a reinicia ou a desliga por inatividade.
- Domínio próprio: não precisa para o evento.
