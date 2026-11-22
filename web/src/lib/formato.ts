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

/** "2026-11-18" -> "18/11/2026". Reads the text directly, so the day never shifts with the time zone. */
export function formatarData(iso: string): string {
  const [ano, mes, dia] = iso.slice(0, 10).split("-");
  return ano && mes && dia ? `${dia}/${mes}/${ano}` : iso;
}

const percentual = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 2 });

/** 1.99 -> "1,99%" (the API sends percentages as numbers: 40 means 40%). */
export function formatarPercentual(valor: number): string {
  return `${percentual.format(valor)}%`;
}

const dataHora = new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" });

/** "2026-11-12T14:03:00Z" -> "12/11/2026, 11:03" (in the viewer's time zone). */
export function formatarDataHora(iso: string): string {
  const data = new Date(iso);
  return Number.isNaN(data.getTime()) ? iso : dataHora.format(data);
}
