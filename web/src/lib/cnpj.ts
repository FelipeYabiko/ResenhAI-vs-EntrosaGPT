// CNPJ helpers for the form. Same rule as the API (api/app/cnpj.py), so the user
// gets the error before anything is sent (RF-01). The API checks again.
// Numeric CNPJ only; alphanumeric CNPJ is an open question in docs/STATUS.md.

const PESOS_PRIMEIRO = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
const PESOS_SEGUNDO = [6, ...PESOS_PRIMEIRO];

export function soDigitos(texto: string): string {
  return texto.replace(/\D/g, "");
}

/** 00.000.000/0000-00 while typing; extra digits are dropped. */
export function mascararCnpj(texto: string): string {
  const d = soDigitos(texto).slice(0, 14);
  return d
    .replace(/^(\d{2})(\d)/, "$1.$2")
    .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/\.(\d{3})(\d)/, ".$1/$2")
    .replace(/(\d{4})(\d)/, "$1-$2");
}

function digito(numeros: number[], pesos: number[]): number {
  const resto = numeros.reduce((soma, n, i) => soma + n * pesos[i], 0) % 11;
  return resto < 2 ? 0 : 11 - resto;
}

/** True for 14 digits (mask allowed) with both check digits right. */
export function cnpjValido(texto: string): boolean {
  const d = soDigitos(texto);
  if (d.length !== 14 || new Set(d).size === 1) return false;
  const numeros = [...d].map(Number);
  const primeiro = digito(numeros.slice(0, 12), PESOS_PRIMEIRO);
  const segundo = digito([...numeros.slice(0, 12), primeiro], PESOS_SEGUNDO);
  return numeros[12] === primeiro && numeros[13] === segundo;
}
