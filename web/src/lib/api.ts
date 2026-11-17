// Thin client for the CredFácil API. Types come from api/openapi.json (npm run tipos);
// never write API types by hand.
import type { components } from "./api-tipos";

export type ConsultaEntrada = components["schemas"]["ConsultaEntrada"];
export type ConsultaResultado = components["schemas"]["ConsultaResultado"];
export type ErroApi = components["schemas"]["Erro"]["erro"];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
// The free API host sleeps when idle and takes up to about a minute to wake up.
const TEMPO_LIMITE_MS = 60_000;

export type RespostaConsulta =
  | { tipo: "ok"; resultado: ConsultaResultado }
  | { tipo: "erro"; status: number; erro: ErroApi }
  | { tipo: "sem_conexao" }
  | { tipo: "demorou" }
  | { tipo: "falha_servidor"; status: number };

export async function consultar(entrada: ConsultaEntrada): Promise<RespostaConsulta> {
  let resposta: Response;
  try {
    resposta = await fetch(`${API_URL}/v1/consultas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entrada),
      signal: AbortSignal.timeout(TEMPO_LIMITE_MS),
    });
  } catch (erro) {
    return erro instanceof DOMException && erro.name === "TimeoutError" ? { tipo: "demorou" } : { tipo: "sem_conexao" };
  }
  const corpo = await resposta.json().catch(() => null);
  // Never guess: an answer outside the contract (HTML error page, empty body) is a server failure.
  if (resposta.ok) {
    if (corpo?.pontuacao && corpo?.recomendacao) return { tipo: "ok", resultado: corpo as ConsultaResultado };
    return { tipo: "falha_servidor", status: resposta.status };
  }
  if (typeof corpo?.erro?.codigo === "string" && typeof corpo?.erro?.mensagem === "string") {
    return { tipo: "erro", status: resposta.status, erro: corpo.erro as ErroApi };
  }
  return { tipo: "falha_servidor", status: resposta.status };
}
