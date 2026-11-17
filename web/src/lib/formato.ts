const reais = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const reaisInteiros = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0,
});

export function formatarReais(valor: number, { centavos = true } = {}): string {
  return (centavos ? reais : reaisInteiros).format(valor);
}

/**
 * Reads a Brazilian money value: "10000", "10.000", "10.000,50", "R$ 10.000,00" or "10000.50".
 * Returns null when empty or ambiguous, so a typo never turns into a different amount.
 */
export function lerReais(texto: string): number | null {
  const t = texto.replace(/R\$|\s/g, "");
  let normal: string | null = null;
  if (/^\d{1,3}(\.\d{3})+(,\d{1,2})?$/.test(t)) normal = t.replace(/\./g, "").replace(",", "."); // 10.000,50
  else if (/^\d+(,\d{1,2})?$/.test(t)) normal = t.replace(",", "."); // 10000,50
  else if (/^\d+\.\d{1,2}$/.test(t)) normal = t; // 10000.50
  return normal === null ? null : Number(normal);
}
