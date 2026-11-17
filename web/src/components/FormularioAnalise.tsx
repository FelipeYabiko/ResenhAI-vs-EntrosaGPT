"use client";

import { useId, useRef, useState, type FormEvent } from "react";
import { consultar, type ConsultaResultado } from "@/lib/api";
import { cnpjValido, mascararCnpj, soDigitos } from "@/lib/cnpj";
import { formatarReais, lerReais } from "@/lib/formato";
import estilos from "./FormularioAnalise.module.css";

type Erros = { cnpj?: string; faturamento?: string };
type Situacao =
  | { tipo: "ocioso" }
  | { tipo: "enviando" }
  | { tipo: "resultado"; resultado: ConsultaResultado }
  | { tipo: "aviso"; mensagem: string };

const MENSAGEM_EM_CONSTRUCAO =
  "O CNPJ está certo. A análise completa ainda está em construção: por enquanto o servidor só confere o CNPJ.";

export function FormularioAnalise() {
  const id = useId();
  const [cnpj, setCnpj] = useState("");
  const [faturamento, setFaturamento] = useState("");
  const [erros, setErros] = useState<Erros>({});
  const [situacao, setSituacao] = useState<Situacao>({ tipo: "ocioso" });
  const campoCnpj = useRef<HTMLInputElement>(null);
  const campoFaturamento = useRef<HTMLInputElement>(null);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setSituacao({ tipo: "ocioso" }); // a new attempt clears the previous answer
    const valor = lerReais(faturamento);
    const novosErros: Erros = {};
    if (!cnpjValido(cnpj)) novosErros.cnpj = "CNPJ inválido. Confira os 14 dígitos.";
    if (valor === null || valor <= 0) {
      novosErros.faturamento = "Informe o faturamento mensal estimado em reais, por exemplo 10.000 ou 10.000,50.";
    }
    setErros(novosErros);
    if (novosErros.cnpj) return campoCnpj.current?.focus();
    if (novosErros.faturamento) return campoFaturamento.current?.focus();

    setSituacao({ tipo: "enviando" });
    const resposta = await consultar({ cnpj: soDigitos(cnpj), perfil_vendas: { faturamento_mensal: valor! } });

    if (resposta.tipo === "ok") return setSituacao({ tipo: "resultado", resultado: resposta.resultado });
    if (resposta.tipo === "demorou") {
      return setSituacao({
        tipo: "aviso",
        mensagem: "O servidor demorou demais para responder. Ele pode estar ligando; tente de novo em instantes.",
      });
    }
    if (resposta.tipo === "falha_servidor") {
      return setSituacao({
        tipo: "aviso",
        mensagem: "O servidor não respondeu como esperado. Tente de novo em alguns segundos.",
      });
    }
    if (resposta.tipo === "sem_conexao") {
      return setSituacao({
        tipo: "aviso",
        mensagem: "Não foi possível falar com o servidor. Confira a conexão e tente de novo.",
      });
    }
    const { codigo, mensagem } = resposta.erro;
    if (codigo === "cnpj_invalido" || codigo === "cnpj_fora_da_demo") {
      setSituacao({ tipo: "ocioso" });
      setErros({ cnpj: mensagem });
      return campoCnpj.current?.focus();
    }
    setSituacao({ tipo: "aviso", mensagem: codigo === "nao_implementado" ? MENSAGEM_EM_CONSTRUCAO : mensagem });
  }

  const enviando = situacao.tipo === "enviando";

  return (
    <form className={estilos.formulario} onSubmit={enviar} noValidate aria-describedby={`${id}-demo`}>
      <p id={`${id}-demo`} className={estilos.demo}>
        Demonstração com dados ilustrativos.
      </p>

      <div className={estilos.campos}>
        <div className={estilos.campo}>
          <label htmlFor={`${id}-cnpj`}>CNPJ</label>
          <input
            ref={campoCnpj}
            id={`${id}-cnpj`}
            name="cnpj"
            inputMode="numeric"
            autoComplete="off"
            value={cnpj}
            onChange={(e) => setCnpj(mascararCnpj(e.target.value))}
            aria-invalid={erros.cnpj ? true : undefined}
            aria-describedby={erros.cnpj ? `${id}-cnpj-erro` : `${id}-cnpj-dica`}
          />
          {erros.cnpj ? (
            <p id={`${id}-cnpj-erro`} className={estilos.erro} role="alert">
              {erros.cnpj}
            </p>
          ) : (
            <p id={`${id}-cnpj-dica`} className={estilos.dica}>
              Só números. Ex.: 00.000.000/0001-91
            </p>
          )}
        </div>

        <div className={estilos.campo}>
          <label htmlFor={`${id}-faturamento`}>Faturamento mensal estimado</label>
          <div className={estilos.comPrefixo}>
            <span aria-hidden="true">R$</span>
            <input
              ref={campoFaturamento}
              id={`${id}-faturamento`}
              name="faturamento"
              inputMode="decimal"
              autoComplete="off"
              value={faturamento}
              onChange={(e) => setFaturamento(e.target.value)}
              aria-invalid={erros.faturamento ? true : undefined}
              aria-describedby={erros.faturamento ? `${id}-faturamento-erro` : `${id}-faturamento-dica`}
            />
          </div>
          {erros.faturamento ? (
            <p id={`${id}-faturamento-erro`} className={estilos.erro} role="alert">
              {erros.faturamento}
            </p>
          ) : (
            <p id={`${id}-faturamento-dica`} className={estilos.dica}>
              Estimativa do comerciante, em reais. Ex.: 10.000
            </p>
          )}
        </div>

        <button type="submit" className={`botao botao-laranja ${estilos.enviar}`} disabled={enviando}>
          {enviando ? "Analisando…" : "Analisar"}
        </button>
      </div>

      <div className={estilos.retorno} role="status" aria-live="polite">
        {situacao.tipo === "enviando" && <p>Analisando o CNPJ… Na primeira consulta do dia pode levar até um minuto.</p>}
        {situacao.tipo === "aviso" && <p className={estilos.aviso}>{situacao.mensagem}</p>}
        {situacao.tipo === "resultado" && <Resumo resultado={situacao.resultado} />}
      </div>
    </form>
  );
}

function Resumo({ resultado }: { resultado: ConsultaResultado }) {
  const { pontuacao, recomendacao, economia, aviso } = resultado;
  return (
    <div className={estilos.resumo}>
      <h3>Resultado da análise</h3>
      <ul>
        <li>Faixa de risco: {pontuacao.faixa}</li>
        <li>Máquina indicada: {recomendacao.maquina.modelo}</li>
        <li>Limite de crédito simulado: {formatarReais(recomendacao.limite_credito_simulado)}</li>
        {economia && <li>Economia estimada: {formatarReais(economia.economia_mensal)} por mês</li>}
      </ul>
      <p className={estilos.aviso}>{aviso}</p>
    </div>
  );
}
