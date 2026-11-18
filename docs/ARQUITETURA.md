# Arquitetura

Proposta técnica para o MVP descrito em `docs/PRODUTO.md`. Pontos marcados como **proposta** ainda precisam da confirmação do time (ver `docs/DECISOES.md`).

## Visão geral

```
 Agente (web)            Matriz (web)
     |                        ^
     | HTTPS                  | SSE (eventos em tempo real)
     v                        |
 +-------------------- API (FastAPI) --------------------+
 |  rotas /v1  ->  ConsultaService                       |
 |                    |-> fontes/  (CNPJ público, BCB)   |   cache no Postgres,
 |                    |            timeout + fallback    |   hosts fixos
 |                    |-> scoring/ (regras, função pura) |
 |                    |-> recomendacao/ (simulador de   |
 |                    |    custo, máquina, limite, taxas)|
 |  propostas  ->  eventos  -> SSE  +  webhook opcional  |
 +----------------------+--------------------------------+
                        |
                    Postgres
```

Decisão-chave: **a pontuação não tem rede, banco nem LLM**. Ela recebe os dados já coletados e devolve resultado e explicação. Isso a torna testável, determinística e fácil de explicar aos jurados.

## Pastas

```
/web                 Next.js + TypeScript (rotas /agente e /matriz)
/api
  /app               rotas, schemas, serviços
  /fontes            clientes de CNPJ e Banco Central, cache, sanitização
  /scoring           regras de risco (puro) + config.yaml com pesos
  /recomendacao      simulador de custo (puro), catálogo de demonstração, limite e taxas (simulação)
  /tests
/fixtures            dados fictícios e lista de CNPJs de demonstração
/scripts             utilitários (ex.: gerar CNPJ fictício válido)
/docs
/.claude             skills e agentes do projeto
/.github             templates de PR e issue
```

Donos (proposta): `/api/fontes` e `/api/app` Felipe; `/api/scoring` e `/api/recomendacao` Kayke; `/web` Guilherme; design, acessibilidade e textos Amanda. Quem mexe na pasta de outra pessoa abre PR e pede revisão do dono.

## Stack (proposta)

| Camada | Escolha | Por quê |
| --- | --- | --- |
| Web | Next.js + TypeScript | Dois perfis (agente e matriz) em um app, bom suporte a acessibilidade |
| API | FastAPI (Python) | Contrato OpenAPI automático, Felipe e Kayke já trabalham em Python |
| Banco | Postgres | Cache das fontes, propostas, eventos |
| Tempo real | Server-Sent Events | Mais simples que WebSocket para "matriz recebe a proposta" |
| Voz | Web Speech API (`SpeechRecognition`) | Sem custo, no navegador. Funciona em navegadores baseados em Chromium. Precisa de alternativa digitada |
| Testes | pytest (API), Vitest e Playwright (web) | Fluxo principal coberto por teste de ponta a ponta |
| Hospedagem | Site no Netlify, API no Render (D-020; a Vercel foi descartada) | HTTPS e deploy automático da `main` pelo time todo. O Netlify não roda Python, por isso a API fica no Render, como um processo contínuo (bom para SSE e para a memória da API). O Render grátis desliga após 15 min sem uso: despertador agendado e aquecer antes de gravar |

## Contrato da API (v1)

Fonte da verdade: o OpenAPI gerado pelo FastAPI a partir de `api/app/schemas.py` e salvo em `api/openapi.json` (`python scripts/exportar_openapi.py`). O `/web` gera os tipos a partir dele. Mudou o contrato? Use a skill `contrato-api`. Os exemplos desta seção são os mesmos dos schemas e são conferidos por teste (`api/tests/test_contrato.py`).

Convenções: JSON, campos em `snake_case` sem acento, datas em ISO 8601, mensagens em português. Valores em reais com duas casas; percentuais como número (40 é 40%; 1,99 é 1,99%).

Toda resposta que mostra limite, taxa, economia ou aprovação traz `"aviso": "Simulação. Não é oferta de crédito."`.

### Erros

Todo erro usa o mesmo formato, inclusive os de validação:

```json
{ "erro": { "codigo": "cnpj_invalido", "mensagem": "CNPJ inválido. Confira os 14 dígitos." } }
```

| Status | `codigo` | Quando |
| --- | --- | --- |
| `404` | `nao_encontrado` | Consulta ou proposta não existe |
| `409` | `transicao_invalida` | Mudança de status não permitida, ou contrato pedido antes da aprovação |
| `422` | `entrada_invalida` | Campo faltando ou fora do formato |
| `422` | `cnpj_invalido` | Dígitos verificadores errados |
| `422` | `cnpj_fora_da_demo` | `MODO_DEMO=true` e o CNPJ não está em `fixtures/cnpjs_demo.json` |
| `429` | `limite_de_uso` | Limite de uso da API ou de uma fonte |
| `501` | `nao_implementado` | Rota prevista no contrato e ainda não implementada |
| `502` | `fonte_indisponivel` | Fonte fora do ar e sem dado em cache |
| `503` | `muitas_conexoes` | Já há muitos painéis ouvindo `GET /v1/eventos` (limite da demo: 50) |

### `POST /v1/consultas`

O CNPJ vai só com os 14 dígitos (o front tira pontos, barra e traço). Só `cnpj` e `perfil_vendas.faturamento_mensal` são obrigatórios: é o que o formulário da landing pede (protótipo do Figma). O resto do perfil e a `situacao_atual` são opcionais e, quando vierem, são estimativas do comerciante.

Entrada (completa):

```json
{
  "cnpj": "00000000000191",
  "perfil_vendas": {
    "faturamento_mensal": 15000.00,
    "mix": { "debito": 40, "credito_a_vista": 40, "credito_parcelado": 0, "pix": 20 },
    "parcelas_medias": 1,
    "ticket_medio": 60.00,
    "prazo_recebimento": "D+1"
  },
  "situacao_atual": {
    "taxas": { "debito": 1.99, "credito_a_vista": 4.98, "credito_parcelado": null, "pix": 0.0 },
    "custo_maquina_mensal": 0.0,
    "custo_saida": 0.0
  }
}
```

Entrada mínima (formulário da landing):

```json
{ "cnpj": "00000000000191", "perfil_vendas": { "faturamento_mensal": 10000.00 } }
```

Regras de entrada: o mix soma 100. `prazo_recebimento` é `D+0`, `D+1`, `D+2`, `D+14` ou `D+30`. Taxa `null` quer dizer "não informada" e nunca é tratada como zero. No exemplo, `"pix": 0.0` é a taxa que o comerciante informou, não um valor assumido pela API.

Saída `200`:

```json
{
  "consulta_id": "c_01",
  "empresa": {
    "cnpj": "00000000000191",
    "nome": "NOME DA EMPRESA",
    "situacao": "ATIVA",
    "cnae_principal": "0000-0/00",
    "porte": "DEMAIS",
    "abertura": "1966-08-01",
    "capital_social": 0,
    "municipio_uf": "Cidade/UF"
  },
  "fontes": [
    { "nome": "cnpj_publico", "status": "ok", "atualizado_em": "2026-11-08", "em_cache": true },
    { "nome": "bcb_inadimplencia_pj", "status": "ok", "atualizado_em": "2026-09-01", "em_cache": true }
  ],
  "pontuacao": {
    "faixa": "B",
    "pontos": 72,
    "fatores": [
      { "regra": "tempo_de_atividade", "contribuicao": 15, "explicacao": "Mais de 10 anos de atividade" }
    ]
  },
  "recomendacao": {
    "maquina": { "modelo": "Plus", "motivo": "Perfil de vendas na faixa do modelo" },
    "limite_credito_simulado": 50000.00,
    "taxas_antecipacao_simuladas": { "mensal_percentual": 0.0 }
  },
  "economia": {
    "custo_mensal_atual": 418.20,
    "custo_mensal_oferta": 248.40,
    "economia_mensal": 169.80,
    "economia_anual": 2037.60,
    "meses_para_compensar_saida": 0,
    "estimado": true
  },
  "benchmark_mercado": {
    "disponivel": false,
    "referencia": "Banco Central, taxas de desconto (MDR)",
    "data_referencia": null
  },
  "tempo_ms": 840,
  "aviso": "Simulação. Não é oferta de crédito."
}
```

Os números do exemplo são ilustrativos. `economia` vem `null` quando faltam o mix ou as taxas atuais: sem eles não há o que comparar, e a API não inventa um perfil padrão. Nesse caso a tela convida a completar o perfil. `fontes[].status` é `ok`, `cache` (fonte fora do ar, devolvido o último dado guardado, com a data dele) ou `indisponivel`. `pontuacao.faixa` vai de `A` a `E`. Erros: `422`, `429`, `501` (enquanto não implementada) e `502`.

### Propostas

| Método e caminho | Para quê | Resposta |
| --- | --- | --- |
| `POST /v1/propostas` | Agente envia a proposta | `201` com a proposta e `status: "enviada"` |
| `GET /v1/propostas?status=enviada` | Matriz lista propostas (filtro opcional por `status`) | `200` com `{"propostas": [...]}` |
| `GET /v1/propostas/{proposta_id}` | Detalhe | `200` com a proposta |
| `PATCH /v1/propostas/{proposta_id}` | Matriz muda o status | `200` com a proposta |
| `GET /v1/propostas/{proposta_id}/contrato` | PDF simulado, com marca d'água "SIMULAÇÃO" | `200` `application/pdf`; `409` se não estiver aprovada |
| `GET /v1/eventos` | Fluxo SSE de eventos | `text/event-stream`; `503` se já houver painéis demais |
| `GET /v1/saude` | Verificação de saúde | `200` |

`agente` é o identificador do perfil de demonstração escolhido em "Entrar na demonstração" (D-015), só letras minúsculas, números e `_`. Não há login nem nome de pessoa real. `observacoes` e `pendencias[].descricao` são texto livre e aparecem para qualquer visitante da demo. A tela avisa para não escrever dado pessoal, e a API recusa com `422` o texto que tem e-mail ou 8 dígitos ou mais seguidos (CPF, telefone). `consulta_id` usa só letras minúsculas, números e `_`.

Entrada de `POST /v1/propostas`:

```json
{ "consulta_id": "c_01", "agente": "agente_demo", "observacoes": "Comerciante prefere receber em D+1." }
```

Proposta (resposta de `POST`, `GET` e `PATCH`):

```json
{
  "proposta_id": "p_01",
  "consulta_id": "c_01",
  "agente": "agente_demo",
  "status": "pendente",
  "observacoes": "Comerciante prefere receber em D+1.",
  "pendencias": [
    { "descricao": "Enviar comprovante de faturamento dos últimos 3 meses.", "criada_em": "2026-11-12T14:10:00Z" }
  ],
  "resumo": {
    "cnpj": "00000000000191",
    "nome": "NOME DA EMPRESA",
    "faixa": "B",
    "limite_credito_simulado": 50000.00,
    "economia_mensal": 169.80
  },
  "criada_em": "2026-11-12T14:03:00Z",
  "atualizada_em": "2026-11-12T14:10:00Z",
  "aviso": "Simulação. Não é oferta de crédito."
}
```

`resumo` traz o que a matriz precisa para decidir sem abrir a consulta. `resumo.economia_mensal` é `null` quando a consulta não teve economia.

Entrada de `PATCH /v1/propostas/{proposta_id}`:

```json
{ "status": "pendente", "pendencias": [ { "descricao": "Enviar comprovante de faturamento dos últimos 3 meses." } ] }
```

Status possíveis: `enviada`, `pendente`, `aprovada`, `recusada`. Transições permitidas: de `enviada` ou `pendente` para `pendente`, `aprovada` ou `recusada`. `aprovada` e `recusada` são finais. Pedir `pendente` exige ao menos uma pendência, e pendência só vale com `pendente` (com outro status, `422`). As pendências se acumulam, cada uma com a data em que foi pedida. Outra transição devolve `409`, sem mudar nada. Cada decisão publica o evento `proposta.<status>`.

Saída de `GET /v1/saude`:

```json
{ "status": "ok", "modo_demo": true }
```

### Evento

Cada evento do SSE vai em uma mensagem com `id: <id do evento>`, `event: <tipo>` e o JSON abaixo em `data:`. Quem conecta recebe só os eventos novos (o painel carrega a lista com `GET /v1/propostas` antes). Se a conexão cair, o navegador reconecta sozinho mandando o cabeçalho `Last-Event-ID`, e a API reenvia o que ficou para trás. A API manda um comentário de tempo em tempo para a conexão não ser fechada por inatividade.

```json
{
  "id": "e_01",
  "tipo": "proposta.criada",
  "ocorrido_em": "2026-11-12T14:03:00Z",
  "proposta_id": "p_01",
  "dados": { "faixa": "B", "limite_credito_simulado": 50000.00 },
  "aviso": "Simulação. Não é oferta de crédito."
}
```

Tipos: `proposta.criada`, `proposta.pendente`, `proposta.aprovada`, `proposta.recusada`. Se `WEBHOOK_MATRIZ_URL` estiver definida, a API também faz `POST` do mesmo evento com a assinatura HMAC no cabeçalho `X-Assinatura`. Isso cumpre o "webhook para o painel" do documento original e mantém o SSE como caminho principal da demo.

Por enquanto, consultas, propostas e eventos ficam na memória da API (`api/app/memoria.py`) e somem quando ela reinicia. O Postgres entra no lugar quando o banco for criado. Como a demo é pública e sem login, a memória tem limites: 1000 consultas e 1000 propostas (as mais antigas saem), 1000 eventos para reenvio, 50 painéis conectados e 100 eventos não lidos por painel (um painel lento perde os mais antigos e recarrega a lista).

O site chama a API de outro endereço. Só as origens de `CORS_ORIGENS` (`.env.example`) podem chamá-la.

## Modelo de dados (proposta)

| Tabela | Campos principais |
| --- | --- |
| `consultas` | `id`, `cnpj`, `faturamento_informado`, `resultado` (JSON), `criado_em` |
| `propostas` | `id`, `consulta_id`, `agente`, `status`, `observacoes`, `pendencias` (JSON), `criada_em`, `atualizada_em` |
| `eventos` | `id`, `tipo`, `proposta_id`, `dados` (JSON), `ocorrido_em` |
| `cache_fontes` | `chave`, `dados` (JSON já sanitizados), `buscado_em`, `ttl_s` |

Só guardamos dados públicos de empresa já sanitizados (ver `docs/DADOS.md`). Sem tabela de pessoas.

## Pontuação por regras

- Entrada: dados sanitizados da empresa, séries do Banco Central e faturamento informado.
- Porta de entrada: situação cadastral diferente de ativa gera faixa E e limite zero, sem calcular o resto.
- Regras (exemplos, Kayke define e calibra): tempo de atividade, porte, capital social em relação ao faturamento informado, inadimplência de referência do Banco Central, atividade (CNAE).
- Pesos e tabelas em `api/scoring/config.yaml`, com comentário de onde veio cada premissa. **Premissas do time não são estatística.** Diga isso no README e no vídeo.
- Saída: pontos, faixa de A a E e lista de fatores com contribuição e explicação em português.
- Limite = faturamento mensal informado multiplicado por um múltiplo da faixa. Taxa = base de referência mais prêmio por faixa. Tabelas ilustrativas, a calibrar.
- Catálogo de demonstração fictício (nomes, faixas de volume e taxas inventados e marcados como ilustrativos). Não usar marcas reais nem taxas reais de provedor sem fonte e data.

## Simulador de custo (proposta, vem do RFC do Comparador)

- Função pura em `api/recomendacao/`, sem rede, sem banco e sem LLM. Mesma entrada, mesma saída.
- Custo mensal de uma oferta = soma, para cada forma de pagamento, de faturamento × participação no mix × taxa; mais o custo mensal da máquina (compra dividida em 12 meses, ou aluguel); mais o custo de antecipação, quando o prazo desejado for menor que o padrão da oferta.
- Pix entra com a taxa informada ou a do catálogo. Não assuma taxa zero: confira.
- Economia = custo atual menos custo com a oferta. Se houver custo de saída, mostrar em quantos meses a economia o compensa.
- Se o catálogo tiver mais de uma máquina, ordenar sempre por menor custo e mostrar o custo de cada uma.
- **Caso de teste de referência** (do RFC): R$ 15.000 por mês, 40% débito, 40% crédito à vista, 20% Pix, Pix sem taxa nos dois cenários, sem custo de máquina. Taxas atuais 1,99% e 4,98%; taxas da oferta 0,99% e 3,15%. Esperado: custo atual R$ 418,20, custo com a oferta R$ 248,40 e economia de R$ 169,80 por mês (R$ 2.037,60 por ano).
- Referência de mercado: o MDR do Banco Central é agregado, defasado e **nunca** aparece como taxa de provedor. Ver `docs/DADOS.md`.

## Privacidade e modo demo

- `MODO_DEMO=true` (padrão no ambiente público): só aceita CNPJs de `fixtures/cnpjs_demo.json` (empresas grandes e CNPJs fictícios válidos). Outro CNPJ recebe `422` com explicação. (proposta D-005)
- Sanitização na entrada das fontes: descartar sócios, e-mails, telefones e endereço detalhado. Para MEI e empresário individual, ocultar o nome (a razão social costuma conter o nome da pessoa).
- Logs não registram o corpo das respostas das fontes.

## Fontes externas

Detalhes, limites e resultados dos testes em `docs/DADOS.md`. Regras comuns: hosts fixos, timeout de 1,2 s, cache com TTL, fallback para o último dado em cache marcado como tal, e fixtures para a demo.

## Deploy (D-020)

Passo a passo em `docs/DEPLOY.md`.

- Site no Netlify (pasta `/web`) e API no Render (pasta `/api`, configurada em `render.yaml`), em HTTPS, com deploy automático da `main`.
- Variáveis de ambiente no provedor, nunca no repositório. Modelo em `.env.example`.
- Evitar hospedagem que "dorme": o primeiro acesso lento quebra a demo e o vídeo. O despertador `.github/workflows/despertar-api.yml` chama `/v1/saude` a cada 10 minutos; mesmo assim, abra a demo antes de gravar e antes da avaliação.
- Congelar a versão para avaliação e manter o repositório público até 15/12.
