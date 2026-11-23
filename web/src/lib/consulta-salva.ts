// Keeps the last query result so the result page can show it.
// The API has no "get query by id" route, and sending the result in the URL would put company data
// in browser history and logs. The result stays in memory (enough for the in-app navigation) and in
// the tab's sessionStorage (so a reload keeps it). If both are empty, the page asks for a new query:
// it never shows a made-up result.
import { pareceConsulta, type ConsultaResultado } from "./api";

const CHAVE = "credfacil-ultima-consulta";
let naMemoria: ConsultaResultado | null = null;

export function salvarConsulta(resultado: ConsultaResultado): void {
  naMemoria = resultado;
  try {
    sessionStorage.setItem(CHAVE, JSON.stringify(resultado));
  } catch {
    // Storage blocked (private mode, browser settings): the in-memory copy still works until a reload.
  }
}

export function lerConsulta(): ConsultaResultado | null {
  if (naMemoria) return naMemoria;
  try {
    const texto = sessionStorage.getItem(CHAVE);
    if (!texto) return null;
    const corpo = JSON.parse(texto);
    // Same check as the API client: anything else is treated as "no result".
    if (!pareceConsulta(corpo)) return null;
    naMemoria = corpo; // later reads return the same object (React needs that)
    return naMemoria;
  } catch {
    return null;
  }
}
