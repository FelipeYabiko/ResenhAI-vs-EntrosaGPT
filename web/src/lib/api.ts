// Thin client for the CredFácil API. Types come from api/openapi.json (npm run tipos);
// never write API types by hand.
import type { components } from "./api-tipos";

export type ConsultaEntrada = components["schemas"]["ConsultaEntrada"];
export type ConsultaResultado = components["schemas"]["ConsultaResultado"];
export type ErroApi = components["schemas"]["Erro"]["erro"];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type RespostaConsulta =
  | { tipo: "ok"; resultado: ConsultaResultado }
  | { tipo: "erro"; status: number; erro: ErroApi }
  | { tipo: "sem_conexao" };

export async function consultar(entrada: ConsultaEntrada): Promise<RespostaConsulta> {
  let resposta: Response;
  try {
    resposta = await fetch(`${API_URL}/v1/consultas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entrada),
    });
  } catch {
    return { tipo: "sem_conexao" };
  }
  const corpo = await resposta.json().catch(() => null);
  if (resposta.ok) return { tipo: "ok", resultado: corpo as ConsultaResultado };
  const erro: ErroApi = corpo?.erro ?? { codigo: "nao_implementado", mensagem: "Resposta inesperada do servidor." };
  return { tipo: "erro", status: resposta.status, erro };
}
