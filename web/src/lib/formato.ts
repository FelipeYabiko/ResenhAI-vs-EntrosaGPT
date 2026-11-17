const reais = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const reaisInteiros = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0,
});

export function formatarReais(valor: number, { centavos = true } = {}): string {
  return (centavos ? reais : reaisInteiros).format(valor);
}

/** Reads "10.000", "10000,50" or "R$ 10.000,00" as a number. Returns null when empty or not a number. */
export function lerReais(texto: string): number | null {
  const limpo = texto.replace(/[^\d,]/g, "").replace(",", ".");
  if (!limpo) return null;
  const valor = Number(limpo);
  return Number.isFinite(valor) ? valor : null;
}
