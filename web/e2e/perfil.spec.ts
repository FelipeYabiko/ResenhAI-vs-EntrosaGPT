import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";

async function capturarConsultas(page: Page) {
  const corpos: unknown[] = [];
  await page.route(`${API}/v1/consultas`, async (rota) => {
    corpos.push(rota.request().postDataJSON());
    await rota.fulfill({
      status: 501,
      contentType: "application/json",
      body: JSON.stringify({ erro: { codigo: "nao_implementado", mensagem: "Aguarda premissas." } }),
    });
  });
  return corpos;
}

async function abrirPerfil(page: Page) {
  await page.getByText("Comparar com a maquininha atual").click();
}

test("o exemplo do mercadinho preenche tudo e envia o perfil completo", async ({ page }) => {
  const corpos = await capturarConsultas(page);
  await page.goto("/");
  await abrirPerfil(page);
  await page.getByRole("button", { name: /Preencher com o exemplo do mercadinho/ }).click();
  await expect(page.getByLabel("CNPJ")).toHaveValue("98.765.432/0001-98");
  await expect(page.getByLabel("Faturamento mensal estimado")).toHaveValue("15.000");
  await expect(page.getByText("Soma: 100%")).toBeVisible();
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.getByRole("status").first()).toContainText("construção");
  expect(corpos).toEqual([
    {
      cnpj: "98765432000198",
      perfil_vendas: {
        faturamento_mensal: 15000,
        mix: { debito: 40, credito_a_vista: 40, credito_parcelado: 0, pix: 20 },
      },
      situacao_atual: {
        taxas: { debito: 1.99, credito_a_vista: 4.98, credito_parcelado: null, pix: 0 },
        custo_maquina_mensal: 0,
        custo_saida: 0,
      },
    },
  ]);
});

test("sem abrir a comparação, a consulta continua só com CNPJ e faturamento", async ({ page }) => {
  const corpos = await capturarConsultas(page);
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765432000198");
  await page.getByLabel("Faturamento mensal estimado").fill("10000");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.getByRole("status").first()).toContainText("construção");
  expect(corpos).toEqual([{ cnpj: "98765432000198", perfil_vendas: { faturamento_mensal: 10000 } }]);
});

test("mix que não soma 100% é recusado antes de chamar a API", async ({ page }) => {
  const corpos = await capturarConsultas(page);
  await page.goto("/");
  await abrirPerfil(page);
  await page.getByRole("button", { name: /Preencher com o exemplo do mercadinho/ }).click();
  await page.getByLabel("Débito: parte das vendas (%)").fill("50");
  await expect(page.getByText("Soma: 110%")).toBeVisible();
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.locator("form").getByRole("alert")).toContainText("somar 100%");
  await expect(page.getByLabel("Débito: parte das vendas (%)")).toBeFocused();
  expect(corpos).toHaveLength(0);
});

test("forma de pagamento com vendas precisa da taxa de hoje", async ({ page }) => {
  const corpos = await capturarConsultas(page);
  await page.goto("/");
  await abrirPerfil(page);
  await page.getByRole("button", { name: /Preencher com o exemplo do mercadinho/ }).click();
  await page.getByLabel("Pix: taxa que paga hoje (%)").fill("");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.locator("form").getByRole("alert")).toContainText("taxa de Pix");
  await expect(page.getByLabel("Pix: taxa que paga hoje (%)")).toBeFocused();
  await expect(page.getByLabel("Pix: taxa que paga hoje (%)")).toHaveAttribute("aria-invalid", "true");
  expect(corpos).toHaveLength(0);
});

test("custo da máquina e de troca entram quando informados", async ({ page }) => {
  const corpos = await capturarConsultas(page);
  await page.goto("/");
  await abrirPerfil(page);
  await page.getByRole("button", { name: /Preencher com o exemplo do mercadinho/ }).click();
  await page.getByLabel("Custo mensal da máquina atual (R$)").fill("49,90");
  await page.getByLabel("Custo para trocar de máquina (R$)").fill("500");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.getByRole("status").first()).toContainText("construção");
  const [corpo] = corpos as { situacao_atual: { custo_maquina_mensal: number; custo_saida: number } }[];
  expect(corpo.situacao_atual.custo_maquina_mensal).toBe(49.9);
  expect(corpo.situacao_atual.custo_saida).toBe(500);
});

test("axe sem violações com a comparação aberta", async ({ page }) => {
  await page.goto("/");
  await abrirPerfil(page);
  const resultado = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  expect(resultado.violations.map((v) => `${v.id}: ${v.nodes.length}`)).toEqual([]);
});

test("só com teclado: abrir, preencher o exemplo e enviar", async ({ page, isMobile }) => {
  test.skip(isMobile, "teclado físico só no desktop");
  const corpos = await capturarConsultas(page);
  await page.goto("/");
  await page.getByText("Comparar com a maquininha atual").focus();
  await page.keyboard.press("Enter");
  await page.getByRole("button", { name: /Preencher com o exemplo do mercadinho/ }).focus();
  await page.keyboard.press("Enter");
  await page.getByLabel("CNPJ").focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("status").first()).toContainText("construção");
  expect(corpos).toHaveLength(1);
});


test("só taxas digitadas não somem: pede o mix", async ({ page }) => {
  const corpos = await capturarConsultas(page);
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765432000198");
  await page.getByLabel("Faturamento mensal estimado").fill("10000");
  await abrirPerfil(page);
  await page.getByLabel("Débito: taxa que paga hoje (%)").fill("1,99");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page.locator("form").getByRole("alert")).toContainText("somar 100%");
  for (const nome of ["Débito", "Crédito à vista", "Crédito parcelado", "Pix"]) {
    await expect(page.getByLabel(`${nome}: parte das vendas (%)`)).toHaveAttribute("aria-invalid", "true");
  }
  expect(corpos).toHaveLength(0);
});

test("o exemplo preenchido é anunciado", async ({ page }) => {
  await page.goto("/");
  await abrirPerfil(page);
  await page.getByRole("button", { name: /Preencher com o exemplo do mercadinho/ }).click();
  await expect(page.locator("form").getByRole("status")).toContainText("Exemplo fictício do mercadinho preenchido");
});
