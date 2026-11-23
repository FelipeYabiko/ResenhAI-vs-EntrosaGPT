"use client";

// One proposal in the back-office panel, with the decisions (RF-07, RF-08) and the contract (RF-09).
import { useId, useRef, useState } from "react";
import { decidirProposta, enderecoDoContrato, obterProposta, type Proposta, type PropostaAtualizacao } from "@/lib/api";
import { mascararCnpj } from "@/lib/cnpj";
import { formatarDataHora, formatarReais } from "@/lib/formato";
import { mensagemDeFalha } from "@/lib/mensagens";
import formulario from "./FormularioAnalise.module.css";
import estilos from "./PainelMatriz.module.css";

export const NOMES_DOS_STATUS: Record<Proposta["status"], string> = {
  enviada: "Nova, aguardando análise",
  pendente: "Pendência pedida ao agente",
  aprovada: "Aprovada (simulação)",
  recusada: "Recusada",
};

type Acao = "aprovada" | "recusada" | "pendente";

export function CartaoProposta({ proposta, aoMudar }: { proposta: Proposta; aoMudar: (p: Proposta) => void }) {
  const id = useId();
  const [pedindoPendencia, setPedindoPendencia] = useState(false);
  const [pendencia, setPendencia] = useState("");
  const [erroCampo, setErroCampo] = useState<string | null>(null);
  const [aviso, setAviso] = useState("");
  const [enviando, setEnviando] = useState(false);
  const campo = useRef<HTMLTextAreaElement>(null);
  const botaoPendencia = useRef<HTMLButtonElement>(null);

  const { resumo } = proposta;
  const titulo = resumo.nome ?? `CNPJ ${mascararCnpj(resumo.cnpj)}`;
  const podeDecidir = proposta.status === "enviada" || proposta.status === "pendente";

  async function decidir(acao: Acao) {
    const texto = pendencia.trim();
    if (acao === "pendente" && texto === "") {
      setErroCampo("Escreva o que o agente precisa enviar.");
      return campo.current?.focus();
    }
    const entrada: PropostaAtualizacao =
      acao === "pendente" ? { status: "pendente", pendencias: [{ descricao: texto }] } : { status: acao };

    setErroCampo(null);
    setAviso("");
    setEnviando(true);
    const resposta = await decidirProposta(proposta.proposta_id, entrada);
    setEnviando(false);

    if (resposta.tipo === "ok") {
      aoMudar(resposta.resultado);
      setPendencia("");
      setPedindoPendencia(false);
      return;
    }
    const falha = mensagemDeFalha(resposta);
    if (falha) return setAviso(falha);
    if (resposta.tipo !== "erro") return;

    const { codigo, mensagem } = resposta.erro;
    if (codigo === "entrada_invalida" && acao === "pendente") {
      setErroCampo("Revise a pendência: ela não pode ter nome, CPF, telefone ou e-mail, e vai até 500 caracteres.");
      return campo.current?.focus();
    }
    if (codigo === "transicao_invalida" || codigo === "nao_encontrado") {
      // Someone else decided first (or the API restarted): show the current state instead of guessing.
      const atual = await obterProposta(proposta.proposta_id);
      if (atual.tipo === "ok") aoMudar(atual.resultado);
    }
    setAviso(mensagem);
  }

  function cancelarPendencia() {
    setPedindoPendencia(false);
    setPendencia("");
    setErroCampo(null);
    botaoPendencia.current?.focus();
  }

  return (
    <article className={estilos.cartao} aria-labelledby={`${id}-titulo`}>
      <h2 id={`${id}-titulo`} className={estilos.tituloCartao}>
        {titulo}
      </h2>
      <p className={estilos.status}>
        <span className="selo">{NOMES_DOS_STATUS[proposta.status]}</span>
      </p>

      <dl className={estilos.dados}>
        <div>
          <dt>CNPJ</dt>
          <dd>{mascararCnpj(resumo.cnpj)}</dd>
        </div>
        <div>
          <dt>Faixa de risco</dt>
          <dd>Faixa {resumo.faixa}</dd>
        </div>
        <div>
          <dt>Limite de crédito simulado</dt>
          <dd>{formatarReais(resumo.limite_credito_simulado)}</dd>
        </div>
        <div>
          <dt>Economia estimada</dt>
          <dd>{resumo.economia_mensal === null ? "Não calculada" : `${formatarReais(resumo.economia_mensal)} por mês`}</dd>
        </div>
        <div>
          <dt>Perfil do vendedor</dt>
          <dd>{proposta.agente}</dd>
        </div>
        <div>
          <dt>Recebida em</dt>
          <dd>{formatarDataHora(proposta.criada_em)}</dd>
        </div>
        <div>
          <dt>Número</dt>
          <dd>{proposta.proposta_id}</dd>
        </div>
      </dl>

      {proposta.observacoes && (
        <p>
          <strong>Observações do agente:</strong> {proposta.observacoes}
        </p>
      )}

      {proposta.pendencias.length > 0 && (
        <div>
          <h3 className={estilos.subtitulo}>Pendências pedidas</h3>
          <ul>
            {proposta.pendencias.map((p) => (
              <li key={`${p.criada_em}-${p.descricao}`}>
                {p.descricao} <span className={estilos.detalhe}>({formatarDataHora(p.criada_em)})</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {proposta.status === "aprovada" && (
        <p>
          <a href={enderecoDoContrato(proposta.proposta_id)} download className="botao botao-marinho">
            Baixar contrato simulado (PDF)
          </a>
        </p>
      )}

      {podeDecidir && !pedindoPendencia && (
        <div className={estilos.acoes}>
          <button type="button" className="botao botao-laranja" disabled={enviando} onClick={() => decidir("aprovada")}>
            Aprovar
          </button>
          <button type="button" className="botao botao-marinho" disabled={enviando} onClick={() => decidir("recusada")}>
            Recusar
          </button>
          <button
            ref={botaoPendencia}
            type="button"
            className={`botao ${estilos.secundario}`}
            disabled={enviando}
            onClick={() => {
              setPedindoPendencia(true);
              // Wait for the field to exist, then move the focus to it.
              requestAnimationFrame(() => campo.current?.focus());
            }}
          >
            Pedir pendência
          </button>
        </div>
      )}

      {podeDecidir && pedindoPendencia && (
        <form
          className={formulario.formulario}
          noValidate
          onSubmit={(e) => {
            e.preventDefault();
            decidir("pendente");
          }}
        >
          <div className={formulario.campo}>
            <label htmlFor={`${id}-pendencia`}>O que o agente precisa enviar</label>
            <textarea
              ref={campo}
              id={`${id}-pendencia`}
              rows={3}
              maxLength={500}
              value={pendencia}
              onChange={(e) => setPendencia(e.target.value)}
              aria-invalid={erroCampo ? true : undefined}
              aria-describedby={erroCampo ? `${id}-pendencia-erro` : `${id}-pendencia-dica`}
            />
            {erroCampo ? (
              <p id={`${id}-pendencia-erro`} className={formulario.erro} role="alert">
                {erroCampo}
              </p>
            ) : (
              <p id={`${id}-pendencia-dica`} className={formulario.dica}>
                Por exemplo: comprovante de faturamento dos últimos 3 meses. Não escreva nome, CPF, telefone ou e-mail.
              </p>
            )}
          </div>
          <div className={estilos.acoes}>
            <button type="submit" className="botao botao-laranja" disabled={enviando}>
              {enviando ? "Enviando…" : "Enviar pendência"}
            </button>
            <button type="button" className={`botao ${estilos.secundario}`} onClick={cancelarPendencia}>
              Cancelar
            </button>
          </div>
        </form>
      )}

      <p role="status" aria-live="polite" className={estilos.aviso}>
        {enviando && !pedindoPendencia ? "Enviando a decisão…" : aviso}
      </p>
    </article>
  );
}
