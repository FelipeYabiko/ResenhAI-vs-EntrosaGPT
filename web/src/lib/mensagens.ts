// Messages for calls that never reached a contract answer. Shared by every screen that calls the API.
import type { Resposta } from "./api";

export function mensagemDeFalha(resposta: Resposta<unknown>): string | null {
  switch (resposta.tipo) {
    case "demorou":
      return "O servidor demorou demais para responder. Ele pode estar ligando; tente de novo em instantes.";
    case "falha_servidor":
      return "O servidor não respondeu como esperado. Tente de novo em alguns segundos.";
    case "sem_conexao":
      return "Não foi possível falar com o servidor. Confira a conexão e tente de novo.";
    default:
      return null;
  }
}
