"use client";

// Sends the proposal to the back office (POST /v1/propostas, RF-06).
import Link from "next/link";
import { useId, useRef, useState, type FormEvent } from "react";
import { enviarProposta, type Proposta } from "@/lib/api";
import { mensagemDeFalha } from "@/lib/mensagens";
import estilos from "./FormularioAnalise.module.css";

// Demo profile until "Entrar na demonstração" exists (D-015). Never a real name.
const AGENTE_DEMO = "agente_demo";

type Situacao =
  | { tipo: "ocioso" }
  | { tipo: "enviando" }
  | { tipo: "enviada"; proposta: Proposta }
  | { tipo: "aviso"; mensagem: string; refazerConsulta?: boolean };

export function EnviarProposta({ consultaId }: { consultaId: string }) {
  const id = useId();
  const [observacoes, setObservacoes] = useState("");
  const [erroCampo, setErroCampo] = useState<string | null>(null);
  const [situacao, setSituacao] = useState<Situacao>({ tipo: "ocioso" });
  const campo = useRef<HTMLTextAreaElement>(null);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setErroCampo(null);
    setSituacao({ tipo: "enviando" });
    const texto = observacoes.trim();
    const resposta = await enviarProposta({
      consulta_id: consultaId,
      agente: AGENTE_DEMO,
      observacoes: texto === "" ? null : texto,
    });

    if (resposta.tipo === "ok") return setSituacao({ tipo: "enviada", proposta: resposta.resultado });
    const falha = mensagemDeFalha(resposta);
    if (falha) return setSituacao({ tipo: "aviso", mensagem: falha });
    if (resposta.tipo !== "erro") return;

    const { codigo, mensagem } = resposta.erro;
    if (codigo === "entrada_invalida" && mensagem.includes("observacoes")) {
      // The API refuses notes that look like personal data: the agent fixes the text and sends again.
      setSituacao({ tipo: "ocioso" });
      setErroCampo("Revise as observações: elas não podem ter nome, CPF, telefone ou e-mail, e vão até 500 caracteres.");
      return campo.current?.focus();
    }
    if (codigo === "nao_encontrado") {
      return setSituacao({
        tipo: "aviso",
        mensagem:
          "Esta consulta não está mais no servidor (ele pode ter reiniciado). Faça a consulta de novo para enviar a proposta.",
        refazerConsulta: true,
      });
    }
    setSituacao({ tipo: "aviso", mensagem });
  }

  if (situacao.tipo === "enviada") {
    const { proposta } = situacao;
    return (
      <div className={estilos.retorno} role="status" aria-live="polite">
        <p className={estilos.aviso}>Proposta enviada. A matriz já pode vê-la no painel.</p>
        <p>
          Número da proposta: {proposta.proposta_id}. Situação: {proposta.status}.
        </p>
        <p>{proposta.aviso}</p>
      </div>
    );
  }

  const enviando = situacao.tipo === "enviando";

  return (
    <form className={estilos.formulario} onSubmit={enviar} noValidate>
      <div className={estilos.campo}>
        <label htmlFor={`${id}-obs`}>Observações para a matriz (opcional)</label>
        <textarea
          ref={campo}
          id={`${id}-obs`}
          name="observacoes"
          rows={3}
          maxLength={500}
          value={observacoes}
          onChange={(e) => setObservacoes(e.target.value)}
          aria-invalid={erroCampo ? true : undefined}
          aria-describedby={erroCampo ? `${id}-obs-erro` : `${id}-obs-dica`}
        />
        {erroCampo ? (
          <p id={`${id}-obs-erro`} className={estilos.erro} role="alert">
            {erroCampo}
          </p>
        ) : (
          <p id={`${id}-obs-dica`} className={estilos.dica}>
            Só sobre a venda, por exemplo o prazo de recebimento preferido. Não escreva nome, CPF, telefone ou e-mail.
          </p>
        )}
      </div>

      <button type="submit" className="botao botao-laranja" disabled={enviando}>
        {enviando ? "Enviando…" : "Enviar proposta"}
      </button>

      <div className={estilos.retorno} role="status" aria-live="polite">
        {enviando && <p>Enviando a proposta…</p>}
        {situacao.tipo === "aviso" && (
          <p className={estilos.aviso}>
            {situacao.mensagem} {situacao.refazerConsulta && <Link href="/#analise">Fazer nova consulta</Link>}
          </p>
        )}
      </div>
    </form>
  );
}
