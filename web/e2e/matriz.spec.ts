// Back-office panel (issue #24). A fake API in each test keeps the proposals and sends live events (SSE).
import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page, type Route } from "@playwright/test";

const API = "http://localhost:8000";
const AVISO = "Simulação. Não é oferta de crédito.";

type Proposta = {
  proposta_id: string;
  status: "enviada" | "pendente" | "aprovada" | "recusada";
  pendencias: { descricao: string; criada_em: string }[];
  [campo: string]: unknown;
};

function proposta(id: string, nome: string, extra: Partial<Proposta> = {}): Proposta {
  return {
    proposta_id: id,
    consulta_id: "c_01",
    agente: "agente_demo",
    status: "enviada",
    observacoes: "Prefere receber em D+1.",
    pendencias: [],
    resumo: {
      cnpj: "98765432000198",
      nome,
      faixa: "B",
      limite_credito_simulado: 50000,
      economia_mensal: 169.8,
    },
    criada_em: "2026-11-22T13:00:00Z",
    atualizada_em: "2026-11-22T13:00:00Z",
    aviso: AVISO,
    ...extra,
  };
}

const json = (rota: Route, status: number, corpo: unknown) =>
  rota.fulfill({ status, contentType: "application/json", body: JSON.stringify(corpo) });

/**
 * Fake API: GET/PATCH proposals and GET /v1/eventos. The SSE answer ends right away with "retry: 200",
 * so the browser reconnects every 200 ms and picks up whatever event the test queued meanwhile.
 */
async function apiFalsa(page: Page, iniciais: Proposta[]) {
  const propostas = new Map(iniciais.map((p) => [p.proposta_id, p]));
  const fila: string[] = [];
  const pedidos: unknown[] = [];
  let respostaDoPatch: { status: number; corpo: unknown } | null = null;
  let n = 0;

  const evento = (tipo: string, p: Proposta) => {
    n += 1;
    const dados = { id: `e_${String(n).padStart(12, "0")}`, tipo, ocorrido_em: "2026-11-22T13:05:00Z", proposta_id: p.proposta_id, dados: { faixa: "B", limite_credito_simulado: 50000 }, aviso: AVISO };
    fila.push(`id: ${dados.id}\nevent: ${tipo}\ndata: ${JSON.stringify(dados)}\n\n`);
  };

  await page.route(`${API}/v1/eventos`, (rota) =>
    rota.fulfill({ status: 200, contentType: "text/event-stream", body: `retry: 200\n\n${fila.splice(0).join("")}` }),
  );
  await page.route(`${API}/v1/propostas`, (rota) => json(rota, 200, { propostas: [...propostas.values()] }));
  await page.route(/\/v1\/propostas\/p_[a-z0-9]+$/, async (rota) => {
    const id = rota.request().url().split("/").pop()!;
    const atual = propostas.get(id);
    if (!atual) return json(rota, 404, { erro: { codigo: "nao_encontrado", mensagem: "Proposta não encontrada." } });
    if (rota.request().method() === "GET") return json(rota, 200, atual);

    const corpo = rota.request().postDataJSON();
    pedidos.push(corpo);
    if (respostaDoPatch) return json(rota, respostaDoPatch.status, respostaDoPatch.corpo);
    const novas = (corpo.pendencias ?? []).map((p: { descricao: string }) => ({ ...p, criada_em: "2026-11-22T13:10:00Z" }));
    const nova = { ...atual, status: corpo.status, pendencias: [...atual.pendencias, ...novas] };
    propostas.set(id, nova);
    evento(`proposta.${corpo.status}`, nova);
    return json(rota, 200, nova);
  });

  return {
    pedidos,
    /** A new proposal sent by an agent in another tab. */
    chegar(p: Proposta) {
      propostas.set(p.proposta_id, p);
      evento("proposta.criada", p);
    },
    /** Someone else decided first (or the API answers an error) on the next PATCH. */
    responderPatch(status: number, corpo: unknown, estadoReal?: Proposta) {
      respostaDoPatch = { status, corpo };
      if (estadoReal) propostas.set(estadoReal.proposta_id, estadoReal);
    },
  };
}

const cartao = (page: Page, nome: string) => page.getByRole("article", { name: nome });

test("mostra as propostas com status em texto e o aviso de simulação", async ({ page }) => {
  await apiFalsa(page, [proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)")]);
  await page.goto("/matriz");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Painel da matriz");
  await expect(page.getByRole("main")).toContainText(AVISO);
  const c = cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)");
  await expect(c).toContainText("Nova, aguardando análise");
  await expect(c).toContainText("98.765.432/0001-98");
  await expect(c).toContainText("Faixa B");
  await expect(c).toContainText("R$ 50.000,00");
  await expect(c).toContainText("R$ 169,80 por mês");
  await expect(c).toContainText("Prefere receber em D+1.");
  await expect(page.getByText("1 proposta.")).toBeVisible();
});

test("axe não encontra violações no painel", async ({ page }) => {
  await apiFalsa(page, [proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)")]);
  await page.goto("/matriz");
  await expect(cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)")).toBeVisible();
  const resultado = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  expect(resultado.violations.map((v) => `${v.id}: ${v.nodes.length}`)).toEqual([]);
});

test("RF-06: nova proposta aparece ao vivo, sem recarregar, e é anunciada", async ({ page }) => {
  const api = await apiFalsa(page, []);
  await page.goto("/matriz");
  await expect(page.getByText("Nenhuma proposta ainda.")).toBeVisible();

  const inicio = Date.now();
  api.chegar(proposta("p_000000000002", "SALÃO BELEZA PURA (FICTÍCIO)"));
  await expect(cartao(page, "SALÃO BELEZA PURA (FICTÍCIO)")).toBeVisible({ timeout: 2000 });
  expect(Date.now() - inicio).toBeLessThan(2000);
  await expect(page.getByRole("status").filter({ hasText: "Nova proposta" })).toHaveText(
    "Nova proposta: SALÃO BELEZA PURA (FICTÍCIO), faixa B.",
  );
});

test("aprovar muda o status e libera o contrato simulado", async ({ page }) => {
  const api = await apiFalsa(page, [proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)")]);
  await page.goto("/matriz");
  const c = cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)");
  await c.getByRole("button", { name: "Aprovar" }).click();
  await expect(c).toContainText("Aprovada (simulação)");
  await expect(c.getByRole("button", { name: "Aprovar" })).toHaveCount(0);
  await expect(c.getByRole("link", { name: "Baixar contrato simulado (PDF)" })).toHaveAttribute(
    "href",
    `${API}/v1/propostas/p_000000000001/contrato`,
  );
  expect(api.pedidos).toEqual([{ status: "aprovada" }]);
});

test("recusar muda o status e não oferece contrato", async ({ page }) => {
  const api = await apiFalsa(page, [proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)")]);
  await page.goto("/matriz");
  const c = cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)");
  await c.getByRole("button", { name: "Recusar" }).click();
  await expect(c).toContainText("Recusada");
  await expect(c.getByRole("link", { name: /contrato/ })).toHaveCount(0);
  expect(api.pedidos).toEqual([{ status: "recusada" }]);
});

test("pedir pendência: campo vazio avisa; texto vai para a API e aparece no cartão", async ({ page }) => {
  const api = await apiFalsa(page, [proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)")]);
  await page.goto("/matriz");
  const c = cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)");
  await c.getByRole("button", { name: "Pedir pendência" }).click();
  const campo = c.getByLabel("O que o agente precisa enviar");
  await expect(campo).toBeFocused();

  await c.getByRole("button", { name: "Enviar pendência" }).click();
  await expect(c.getByRole("alert")).toHaveText(/Escreva o que o agente precisa enviar/);
  await expect(campo).toBeFocused();
  expect(api.pedidos).toHaveLength(0);

  await campo.fill("Comprovante de faturamento dos últimos 3 meses.");
  await c.getByRole("button", { name: "Enviar pendência" }).click();
  await expect(c).toContainText("Pendência pedida ao agente");
  await expect(c.getByRole("list")).toContainText("Comprovante de faturamento dos últimos 3 meses.");
  expect(api.pedidos).toEqual([
    { status: "pendente", pendencias: [{ descricao: "Comprovante de faturamento dos últimos 3 meses." }] },
  ]);
});

test("pendência recusada pela API mostra erro no campo", async ({ page }) => {
  const api = await apiFalsa(page, [proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)")]);
  api.responderPatch(422, { erro: { codigo: "entrada_invalida", mensagem: "Confira estes campos: pendencias.0.descricao." } });
  await page.goto("/matriz");
  const c = cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)");
  await c.getByRole("button", { name: "Pedir pendência" }).click();
  const campo = c.getByLabel("O que o agente precisa enviar");
  await campo.fill("texto recusado");
  await c.getByRole("button", { name: "Enviar pendência" }).click();
  await expect(c.getByRole("alert")).toContainText("não pode ter nome, CPF, telefone ou e-mail");
  await expect(campo).toHaveAttribute("aria-invalid", "true");
  await expect(campo).toBeFocused();
});

test("decisão que chegou tarde mostra o estado real, sem adivinhar", async ({ page }) => {
  const api = await apiFalsa(page, [proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)")]);
  await page.goto("/matriz");
  const c = cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)");
  await expect(c).toContainText("Nova, aguardando análise");
  api.responderPatch(
    409,
    { erro: { codigo: "transicao_invalida", mensagem: "A proposta já foi recusada e não pode mudar." } },
    proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)", { status: "recusada" }),
  );
  await c.getByRole("button", { name: "Aprovar" }).click();
  await expect(c).toContainText("A proposta já foi recusada e não pode mudar.");
  await expect(c).toContainText("Recusada");
  await expect(c.getByRole("button", { name: "Aprovar" })).toHaveCount(0);
});

test("filtro por status", async ({ page }) => {
  await apiFalsa(page, [
    proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)"),
    proposta("p_000000000002", "SALÃO BELEZA PURA (FICTÍCIO)", { status: "aprovada", criada_em: "2026-11-22T12:00:00Z" }),
  ]);
  await page.goto("/matriz");
  await expect(page.getByText("2 propostas.")).toBeVisible();
  await page.getByLabel("Mostrar").selectOption("aprovada");
  await expect(cartao(page, "SALÃO BELEZA PURA (FICTÍCIO)")).toBeVisible();
  await expect(cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)")).toHaveCount(0);
  await expect(page.getByText('1 proposta com o status "Aprovada (simulação)".')).toBeVisible();
});

test("lista fora do ar mostra erro claro, nunca lista inventada", async ({ page }) => {
  await page.route(`${API}/v1/eventos`, (rota) => rota.abort("connectionrefused"));
  await page.route(`${API}/v1/propostas`, (rota) => rota.abort("connectionrefused"));
  await page.goto("/matriz");
  await expect(page.getByRole("main").getByRole("alert")).toContainText("Não foi possível carregar a lista.");
  await expect(page.getByRole("button", { name: "Tentar de novo" })).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(0);
});

test("o painel não rola na horizontal", async ({ page }) => {
  await apiFalsa(page, [proposta("p_000000000001", "MERCADINHO BOA VISTA (FICTÍCIO)")]);
  await page.goto("/matriz");
  await expect(cartao(page, "MERCADINHO BOA VISTA (FICTÍCIO)")).toBeVisible();
  const larguras = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  expect(larguras[0]).toBeLessThanOrEqual(larguras[1]);
});
