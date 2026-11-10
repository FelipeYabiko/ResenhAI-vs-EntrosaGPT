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
| Hospedagem | Vercel, decidido pelo time (D-004, em parte) | Precisa ter HTTPS, ficar no ar até 15/12 e não "dormir" durante a gravação. API em Python, SSE e banco na Vercel ainda não verificados. Plano grátis só permite deploy pelo dono (D-014) |

## Contrato da API (v1)

Fonte da verdade: o OpenAPI gerado pelo FastAPI (`api/openapi.json`). O `/web` gera os tipos a partir dele. Mudou o contrato? Use a skill `contrato-api`.

Convenções: JSON, campos em `snake_case` sem acento, datas em ISO 8601, erros como `{"erro": {"codigo": "...", "mensagem": "..."}}`, mensagens em português.

### `POST /v1/consultas`

Entrada:

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

Mix e taxas em percentual (40 é 40%; 1,99 é 1,99%). O mix soma 100. `situacao_atual` é opcional e sempre tratada como estimativa do comerciante.

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

Os números do exemplo são ilustrativos. Erros: `422` CNPJ inválido ou fora da lista de demonstração, `502` fonte indisponível sem cache, `429` limite de uso.

### Propostas

| Método e caminho | Para quê | Resposta |
| --- | --- | --- |
| `POST /v1/propostas` | Agente envia a proposta (`consulta_id`, `agente`, `observacoes`) | `201` com `proposta_id` e `status: "enviada"` |
| `GET /v1/propostas` | Matriz lista propostas (filtro `status`) | `200` lista |
| `GET /v1/propostas/{id}` | Detalhe | `200` |
| `PATCH /v1/propostas/{id}` | Matriz muda status (`aprovada`, `recusada`, `pendente`) e envia `pendencias[]` | `200` |
| `GET /v1/propostas/{id}/contrato` | PDF simulado, só se aprovada | `200` `application/pdf` |
| `GET /v1/eventos` | Fluxo SSE de eventos | `text/event-stream` |
| `GET /v1/saude` | Verificação de saúde | `200` |

### Evento

```json
{
  "id": "e_01",
  "tipo": "proposta.criada",
  "ocorrido_em": "2026-11-12T14:03:00Z",
  "proposta_id": "p_01",
  "dados": { "faixa": "B", "limite_credito_simulado": 50000.00 }
}
```

Tipos: `proposta.criada`, `proposta.pendente`, `proposta.aprovada`, `proposta.recusada`. Se `WEBHOOK_MATRIZ_URL` estiver definida, a API também faz `POST` do mesmo evento com a assinatura HMAC no cabeçalho `X-Assinatura`. Isso cumpre o "webhook para o painel" do documento original e mantém o SSE como caminho principal da demo.

## Modelo de dados (proposta)

| Tabela | Campos principais |
| --- | --- |
| `consultas` | `id`, `cnpj`, `faturamento_informado`, `resultado` (JSON), `criado_em` |
| `propostas` | `id`, `consulta_id`, `agente`, `status`, `pendencias` (JSON), `criado_em`, `atualizado_em` |
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

## Deploy (proposta)

- Web e API em HTTPS, com deploy automático da `main`.
- Variáveis de ambiente no provedor, nunca no repositório. Modelo em `.env.example`.
- Evitar hospedagem que "dorme": o primeiro acesso lento quebra a demo e o vídeo. Se usar plano gratuito, manter um ping de aquecimento e checar antes de gravar.
- Congelar a versão para avaliação e manter o repositório público até 15/12.
