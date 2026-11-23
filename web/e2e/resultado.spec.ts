// Result screen (issue #22). The API is mocked in each test; the numbers are the RF-11 reference case.
import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const API = "http://localhost:8000";

const RESULTADO = {
  consulta_id: "c_01",
  empresa: {
    cnpj: "98765432000198",
    nome: "MERCADINHO BOA VISTA (FICTÍCIO)",
    situacao: "ATIVA",
    cnae_principal: "4712-1/00",
    porte: "ME",
    abertura: "2018-03-12",
    capital_social: 20000,
    municipio_uf: "São Paulo/SP",
  },
  fontes: [{ nome: "cnpj_publico", status: "cache", atualizado_em: "2026-11-18", em_cache: true }],
  pontuacao: {
    faixa: "C",
    pontos: 55,
    fatores: [
      { regra: "tempo_de_atividade", contribuicao: 10, explicacao: "Regra de teste A" },
      { regra: "outra", contribuicao: -5, explicacao: "Regra de teste B" },
    ],
  },
  recomendacao: {
    maquina: { modelo: "Modelo Teste", motivo: "Motivo de teste" },
    limite_credito_simulado: 12000,
    taxas_antecipacao_simuladas: { mensal_percentual: 1.5 },
  },
  economia: {
    custo_mensal_atual: 418.2,
    custo_mensal_oferta: 248.4,
    economia_mensal: 169.8,
    economia_anual: 2037.6,
    meses_para_compensar_saida: 3,
    estimado: true,
  },
  benchmark_mercado: { disponivel: false, referencia: "Banco Central, taxas de desconto (MDR)", data_referencia: null },
  tempo_ms: 840,
  aviso: "Simulação. Não é oferta de crédito.",
};

/** Fills the landing form with an answer from the mocked API and waits for the result page. */
async function consultar(page: Page, corpo: object = RESULTADO) {
  await page.route(`${API}/v1/consultas`, (rota) =>
    rota.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(corpo) }),
  );
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765432000198");
  await page.getByLabel("Faturamento mensal estimado").fill("15000");
  await page.getByRole("button", { name: "Analisar" }).click();
  await expect(page).toHaveURL(/\/resultado$/);
}

/** Mocks POST /v1/propostas and returns the bodies it received. */
async function simularPropostas(page: Page, status: number, corpo: unknown) {
  const chamadas: unknown[] = [];
  await page.route(`${API}/v1/propostas`, async (rota) => {
    chamadas.push(rota.request().postDataJSON());
    await rota.fulfill({ status, contentType: "application/json", body: JSON.stringify(corpo) });
  });
  return chamadas;
}

test("mostra o que a API devolveu, com o aviso de simulação", async ({ page }) => {
  await consultar(page);
  const tela = page.getByRole("main");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Resultado da análise");
  await expect(page.getByRole("heading", { level: 1 })).toBeFocused();
  await expect(tela).toContainText("Simulação. Não é oferta de crédito.");
  await expect(tela).toContainText("R$ 169,80 por mês");
  await expect(tela).toContainText("R$ 2.037,60 por ano");
  await expect(tela).toContainText("R$ 418,20");
  await expect(tela).toContainText("R$ 248,40");
  await expect(tela).toContainText("compensa o custo de saída em 3 meses");
  await expect(tela).toContainText("Faixa C");
  await expect(tela).toContainText("Regra de teste A: +10 pontos");
  await expect(tela).toContainText("Regra de teste B: -5 pontos");
  await expect(tela).toContainText("Modelo Teste");
  await expect(tela).toContainText("R$ 12.000,00");
  await expect(tela).toContainText("1,5% ao mês");
  await expect(tela).toContainText("98.765.432/0001-98");
  await expect(tela).toContainText("12/03/2018");
  await expect(tela).toContainText("fonte fora do ar, mostrando o último dado guardado (dado de 18/11/2026)");
  await expect(tela).toContainText("Referência do Banco Central indisponível");
  await expect(tela).not.toContainText("Exemplo ilustrativo");
});

test("sem economia calculada, não mostra valor nenhum", async ({ page }) => {
  await consultar(page, { ...RESULTADO, economia: null });
  const bloco = page.getByRole("region", { name: "Economia estimada" });
  await expect(bloco).toContainText("Nenhuma economia foi estimada");
  await expect(bloco).not.toContainText("R$");
});

test("oferta mais cara não aparece como economia", async ({ page }) => {
  await consultar(page, {
    ...RESULTADO,
    economia: { ...RESULTADO.economia, custo_mensal_oferta: 500, economia_mensal: -81.8, economia_anual: -981.6 },
  });
  const bloco = page.getByRole("region", { name: "Economia estimada" });
  await expect(bloco).toContainText("a oferta não reduz o custo mensal");
  await expect(bloco).not.toContainText("por mês");
});

test("axe não encontra violações na tela de resultado", async ({ page }) => {
  await consultar(page);
  const resultado = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  expect(resultado.violations.map((v) => `${v.id}: ${v.nodes.length}`)).toEqual([]);
});

test("a tela não rola na horizontal", async ({ page }) => {
  await consultar(page);
  const larguras = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  expect(larguras[0]).toBeLessThanOrEqual(larguras[1]);
});

test("recarregar a página mantém o resultado da aba", async ({ page }) => {
  await consultar(page);
  await page.reload();
  await expect(page.getByRole("main")).toContainText("R$ 169,80 por mês");
});

test("sem consulta, a tela diz isso e não inventa resultado", async ({ page }) => {
  await page.goto("/resultado");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Nenhum resultado para mostrar");
  await expect(page.getByRole("main")).not.toContainText("R$");
});

test("exemplo ilustrativo é marcado e não envia proposta", async ({ page }) => {
  const chamadas = await simularPropostas(page, 201, {});
  await page.goto("/resultado?exemplo");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Exemplo de resultado");
  await expect(page.getByRole("main")).toContainText("Exemplo ilustrativo.");
  await expect(page.getByRole("main")).toContainText("FICTÍCIO");
  await expect(page.getByRole("button", { name: "Enviar proposta" })).toHaveCount(0);
  expect(chamadas).toHaveLength(0);
});

test("API em construção (501) oferece o exemplo ilustrativo", async ({ page }) => {
  await page.route(`${API}/v1/consultas`, (rota) =>
    rota.fulfill({
      status: 501,
      contentType: "application/json",
      body: JSON.stringify({ erro: { codigo: "nao_implementado", mensagem: "" } }),
    }),
  );
  await page.goto("/");
  await page.getByLabel("CNPJ").fill("98765432000198");
  await page.getByLabel("Faturamento mensal estimado").fill("15000");
  await page.getByRole("button", { name: "Analisar" }).click();
  await page.getByRole("link", { name: "Ver um exemplo ilustrativo do resultado" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Exemplo de resultado");
});

test("envia a proposta com o perfil de demonstração", async ({ page }) => {
  const chamadas = await simularPropostas(page, 201, {
    proposta_id: "p_0123456789ab",
    consulta_id: "c_01",
    agente: "agente_demo",
    status: "enviada",
    aviso: "Simulação. Não é oferta de crédito.",
  });
  await consultar(page);
  await page.getByLabel("Observações para a matriz (opcional)").fill("Prefere receber em D+1.");
  await page.getByRole("button", { name: "Enviar proposta" }).click();
  await expect(page.getByRole("region", { name: "Enviar proposta à matriz" })).toContainText(
    "Proposta enviada. A matriz já pode vê-la no painel.",
  );
  await expect(page.getByRole("region", { name: "Enviar proposta à matriz" })).toContainText("p_0123456789ab");
  expect(chamadas).toEqual([{ consulta_id: "c_01", agente: "agente_demo", observacoes: "Prefere receber em D+1." }]);
});

test("observação recusada pela API mostra erro no campo", async ({ page }) => {
  await simularPropostas(page, 422, {
    erro: { codigo: "entrada_invalida", mensagem: "Confira estes campos: observacoes." },
  });
  await consultar(page);
  const campo = page.getByLabel("Observações para a matriz (opcional)");
  await campo.fill("texto recusado");
  await page.getByRole("button", { name: "Enviar proposta" }).click();
  await expect(page.getByRole("region", { name: "Enviar proposta à matriz" }).getByRole("alert")).toContainText(
    "não podem ter nome, CPF, telefone ou e-mail",
  );
  await expect(campo).toHaveAttribute("aria-invalid", "true");
  await expect(campo).toBeFocused();
});

test("consulta que sumiu do servidor pede nova consulta", async ({ page }) => {
  await simularPropostas(page, 404, { erro: { codigo: "nao_encontrado", mensagem: "Consulta não encontrada." } });
  await consultar(page);
  await page.getByRole("button", { name: "Enviar proposta" }).click();
  await expect(page.getByRole("link", { name: "Fazer nova consulta" })).toBeVisible();
});
