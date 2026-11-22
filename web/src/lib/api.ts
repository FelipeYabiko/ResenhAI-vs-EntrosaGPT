// Thin client for the CredFácil API. Types come from api/openapi.json (npm run tipos);
// never write API types by hand.
import type { components } from "./api-tipos";

export type ConsultaEntrada = components["schemas"]["ConsultaEntrada"];
export type ConsultaResultado = components["schemas"]["ConsultaResultado"];
export type PropostaEntrada = components["schemas"]["PropostaEntrada"];
export type Proposta = components["schemas"]["Proposta"];
export type ErroApi = components["schemas"]["Erro"]["erro"];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
// The free API host sleeps when idle and takes up to about a minute to wake up.
const TEMPO_LIMITE_MS = 60_000;

/** Every way a call can end. The screens turn each one into a clear message, never into made-up data. */
export type Resposta<T> =
  | { tipo: "ok"; resultado: T }
  | { tipo: "erro"; status: number; erro: ErroApi }
  | { tipo: "sem_conexao" }
  | { tipo: "demorou" }
  | { tipo: "falha_servidor"; status: number };

export type RespostaConsulta = Resposta<ConsultaResultado>;
export type RespostaProposta = Resposta<Proposta>;

async function postar<T>(
  caminho: string,
  entrada: unknown,
  pareceValido: (corpo: Corpo) => boolean,
): Promise<Resposta<T>> {
  let resposta: Response;
  try {
    resposta = await fetch(`${API_URL}${caminho}`, {
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
    if (pareceValido(corpo)) return { tipo: "ok", resultado: corpo as T };
    return { tipo: "falha_servidor", status: resposta.status };
  }
  if (typeof corpo?.erro?.codigo === "string" && typeof corpo?.erro?.mensagem === "string") {
    return { tipo: "erro", status: resposta.status, erro: corpo.erro as ErroApi };
  }
  return { tipo: "falha_servidor", status: resposta.status };
}

type Corpo = Record<string, unknown> | null;

/** Minimum shape the result screen needs. Anything less is treated as a server failure, never shown half-empty. */
export function pareceConsulta(corpo: unknown): corpo is ConsultaResultado {
  const c = corpo as Partial<ConsultaResultado> | null;
  return Boolean(
    typeof c?.consulta_id === "string" &&
      typeof c.empresa?.cnpj === "string" &&
      Array.isArray(c.fontes) &&
      typeof c.pontuacao?.faixa === "string" &&
      Array.isArray(c.pontuacao.fatores) &&
      typeof c.recomendacao?.maquina?.modelo === "string" &&
      c.benchmark_mercado,
  );
}

export function consultar(entrada: ConsultaEntrada): Promise<RespostaConsulta> {
  return postar("/v1/consultas", entrada, pareceConsulta);
}

export function enviarProposta(entrada: PropostaEntrada): Promise<RespostaProposta> {
  return postar("/v1/propostas", entrada, (c: Corpo) => typeof c?.proposta_id === "string");
}
