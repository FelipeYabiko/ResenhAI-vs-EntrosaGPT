import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";

/** Answers POST /v1/consultas with the given status and body, and counts the calls. */
async function simularApi(page: Page, status: number, corpo: unknown) {
  const chamadas: unknown[] = [];
  await page.route(`${API}/v1/consultas`, async (rota) => {
    chamadas.push(rota.request().postDataJSON());
    await rota.fulfill({ status, contentType: "application/json", body: JSON.stringify(corpo) });
  });
  return chamadas;
}

test("estrutura: idioma, um h1 e regiões", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("html")).toHaveAttribute("lang", "pt-BR");
  await expect(page.locator("h1")).toHaveCount(1);
  await expect(page.getByRole("banner")).toBeVisible();
  await expect(page.getByRole("main")).toBeVisible();
  await expect(page.getByRole("contentinfo")).toBeVisible();
  await expect(page.getByText("Simulação. Não é oferta de crédito.")).toBeVisible();
});

test("axe não encontra violações WCAG 2.1 A/AA", async ({ page }) => {
  await page.goto("/");
  const resultado = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  expect(resultado.violations.map((v) => `${v.id}: ${v.nodes.length}`)).toEqual([]);
});

test("CNPJ inválido mostra erro no campo e não chama a API", async ({ page }) => {
  const chamadas = await simularApi(page, 200, {});
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765435000120");
  await page.getByLabel("Faturamento mensal estimado").fill("10000");
  await page.getByRole("button", { name: "Analisar" }).click();

  const campo = page.getByLabel("CNPJ");
  await expect(page.locator("form").getByRole("alert")).toHaveText(/CNPJ inválido/);
  await expect(campo).toHaveAttribute("aria-invalid", "true");
  await expect(campo).toBeFocused();
  expect(chamadas).toHaveLength(0);
});

test("o campo coloca a máscara do CNPJ e envia só os dígitos", async ({ page }) => {
  const chamadas = await simularApi(page, 501, {
    erro: { codigo: "nao_implementado", mensagem: "Rota prevista no contrato v1, ainda em construção." },
  });
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765435000121");
  await expect(page.getByLabel("CNPJ")).toHaveValue("98.765.435/0001-21");
  await page.getByLabel("Faturamento mensal estimado").fill("10.000");
  await page.getByRole("button", { name: "Analisar" }).click();

  await expect(page.getByRole("status")).toContainText("ainda está em construção");
  expect(chamadas).toEqual([{ cnpj: "98765435000121", perfil_vendas: { faturamento_mensal: 10000 } }]);
});

test("resultado da API aparece com o aviso de simulação", async ({ page }) => {
  await simularApi(page, 200, {
    consulta_id: "c_01",
    empresa: {},
    fontes: [],
    pontuacao: { faixa: "B", pontos: 72, fatores: [] },
    recomendacao: {
      maquina: { modelo: "Plus", motivo: "" },
      limite_credito_simulado: 50000,
      taxas_antecipacao_simuladas: { mensal_percentual: 0 },
    },
    economia: null,
    benchmark_mercado: { disponivel: false, referencia: "", data_referencia: null },
    tempo_ms: 10,
    aviso: "Simulação. Não é oferta de crédito.",
  });
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765435000121");
  await page.getByLabel("Faturamento mensal estimado").fill("10000");
  await page.getByRole("button", { name: "Analisar" }).click();

  const retorno = page.getByRole("status");
  await expect(retorno).toContainText("Faixa de risco: B");
  await expect(retorno).toContainText("R$ 50.000,00");
  await expect(retorno).toContainText("Simulação. Não é oferta de crédito.");
  await expect(retorno).not.toContainText("Economia");
});

test("sem servidor, a mensagem diz isso em vez de inventar resultado", async ({ page }) => {
  await page.route(`${API}/v1/consultas`, (rota) => rota.abort("connectionrefused"));
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765435000121");
  await page.getByLabel("Faturamento mensal estimado").fill("10000");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.getByRole("status")).toContainText("Não foi possível falar com o servidor");
});

test("faturamento vazio mostra erro e leva o foco ao campo", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765435000121");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.locator("form").getByRole("alert")).toHaveText(/Informe o faturamento/);
  await expect(page.getByLabel("Faturamento mensal estimado")).toBeFocused();
});

test("só com teclado: do link de pular ao envio do formulário", async ({ page, isMobile }) => {
  test.skip(isMobile, "teclado físico só no desktop");
  await simularApi(page, 501, { erro: { codigo: "nao_implementado", mensagem: "" } });
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Pular para o conteúdo" })).toBeFocused();
  await page.getByLabel("CNPJ").focus();
  await page.keyboard.type("98765435000121");
  await page.keyboard.press("Tab");
  await expect(page.getByLabel("Faturamento mensal estimado")).toBeFocused();
  await page.keyboard.type("10000");
  await page.keyboard.press("Enter");
  await expect(page.getByRole("status")).toContainText("ainda está em construção");
});

test("o foco é visível", async ({ page, isMobile }) => {
  test.skip(isMobile, "teclado físico só no desktop");
  await page.goto("/");
  await page.keyboard.press("Tab");
  const contorno = await page
    .getByRole("link", { name: "Pular para o conteúdo" })
    .evaluate((el) => getComputedStyle(el).outlineStyle);
  expect(contorno).toBe("solid");
});

test("reduzir movimento: liga, desliga e lembra a escolha", async ({ page }) => {
  await page.goto("/");
  const interruptor = page.getByLabel("Reduzir movimento");
  await interruptor.check();
  await expect(page.locator("html")).toHaveAttribute("data-movimento", "reduzido");
  await page.reload();
  await expect(page.getByLabel("Reduzir movimento")).toBeChecked();
  await page.getByLabel("Reduzir movimento").uncheck();
  await expect(page.locator("html")).toHaveAttribute("data-movimento", "normal");
});

test("a página não rola na horizontal (celular e zoom)", async ({ page }) => {
  await page.goto("/");
  const larguras = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  expect(larguras[0]).toBeLessThanOrEqual(larguras[1]);
});

test("nova tentativa apaga a resposta anterior", async ({ page }) => {
  await simularApi(page, 501, { erro: { codigo: "nao_implementado", mensagem: "" } });
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765435000121");
  await page.getByLabel("Faturamento mensal estimado").fill("10000");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.getByRole("status")).toContainText("ainda está em construção");

  await page.getByLabel("CNPJ").fill("98765435000120");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.locator("form").getByRole("alert")).toHaveText(/CNPJ inválido/);
  await expect(page.getByRole("status")).toBeEmpty();
});

test("resposta fora do contrato vira falha, nunca 'CNPJ certo'", async ({ page }) => {
  await page.route(`${API}/v1/consultas`, (rota) =>
    rota.fulfill({ status: 502, contentType: "text/html", body: "<html>Bad gateway</html>" }),
  );
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765435000121");
  await page.getByLabel("Faturamento mensal estimado").fill("10000");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.getByRole("status")).toContainText("não respondeu como esperado");
  await expect(page.getByRole("status")).not.toContainText("CNPJ está certo");
});

test("200 sem corpo válido não quebra a tela", async ({ page }) => {
  await page.route(`${API}/v1/consultas`, (rota) => rota.fulfill({ status: 200, body: "" }));
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765435000121");
  await page.getByLabel("Faturamento mensal estimado").fill("10000");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.getByRole("status")).toContainText("não respondeu como esperado");
});

for (const [digitado, enviado] of [
  ["10.000", 10000],
  ["10.000,50", 10000.5],
  ["10000,50", 10000.5],
  ["10000.50", 10000.5],
  ["R$ 1.500", 1500],
] as const) {
  test(`faturamento "${digitado}" é lido como ${enviado}`, async ({ page }) => {
    const chamadas = await simularApi(page, 501, { erro: { codigo: "nao_implementado", mensagem: "" } });
    await page.goto("/");
    await page.getByLabel("CNPJ").fill("98765435000121");
    await page.getByLabel("Faturamento mensal estimado").fill(digitado);
    await page.getByRole("button", { name: "Analisar" }).click();
    await expect(page.getByRole("status")).toContainText("construção");
    expect(chamadas).toEqual([{ cnpj: "98765435000121", perfil_vendas: { faturamento_mensal: enviado } }]);
  });
}

for (const ambiguo of ["10,000.50", "10.00.0", "dez mil"]) {
  test(`faturamento ambíguo "${ambiguo}" é recusado`, async ({ page }) => {
    const chamadas = await simularApi(page, 200, {});
    await page.goto("/");
    await page.getByLabel("CNPJ").fill("98765435000121");
    await page.getByLabel("Faturamento mensal estimado").fill(ambiguo);
    await page.getByRole("button", { name: "Analisar" }).click();
    await expect(page.locator("form").getByRole("alert")).toHaveText(/Informe o faturamento/);
    expect(chamadas).toHaveLength(0);
  });
}
