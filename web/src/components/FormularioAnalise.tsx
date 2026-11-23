"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useId, useRef, useState, type FormEvent } from "react";
import { consultar } from "@/lib/api";
import { cnpjValido, mascararCnpj, soDigitos } from "@/lib/cnpj";
import { limparConsulta, salvarConsulta } from "@/lib/consulta-salva";
import { lerReais } from "@/lib/formato";
import { mensagemDeFalha } from "@/lib/mensagens";
import {
  EXEMPLO_MERCADINHO,
  lerPerfil,
  PERFIL_VAZIO,
  perfilEmUso,
  type ErroPerfil,
  type PerfilDigitado,
} from "@/lib/perfil-vendas";
import estilos from "./FormularioAnalise.module.css";
import { PerfilVendas } from "./PerfilVendas";

type Erros = { cnpj?: string; faturamento?: string };
type Situacao =
  | { tipo: "ocioso" }
  | { tipo: "enviando" }
  | { tipo: "abrindo_resultado" }
  | { tipo: "aviso"; mensagem: string; comExemplo?: boolean };

const MENSAGEM_EM_CONSTRUCAO = "O CNPJ está certo. A análise completa ainda está em construção.";

export function FormularioAnalise() {
  const id = useId();
  const router = useRouter();
  const [cnpj, setCnpj] = useState("");
  const [faturamento, setFaturamento] = useState("");
  const [erros, setErros] = useState<Erros>({});
  const [situacao, setSituacao] = useState<Situacao>({ tipo: "ocioso" });
  const campoCnpj = useRef<HTMLInputElement>(null);
  const campoFaturamento = useRef<HTMLInputElement>(null);
  const [perfil, setPerfil] = useState<PerfilDigitado>(PERFIL_VAZIO);
  const [perfilAberto, setPerfilAberto] = useState(false);
  const [erroPerfil, setErroPerfil] = useState<ErroPerfil | null>(null);

  function preencherExemplo() {
    setCnpj(EXEMPLO_MERCADINHO.cnpj);
    setFaturamento(EXEMPLO_MERCADINHO.faturamento);
    setPerfil(EXEMPLO_MERCADINHO.perfil);
    setErros({});
    setErroPerfil(null);
    setSituacao({ tipo: "aviso", mensagem: "Exemplo fictício do mercadinho preenchido. Confira e clique em Analisar." });
  }

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

    // Optional comparison: only sent when the merchant's payment mix was typed.
    let comparacao = null;
    if (perfilEmUso(perfil)) {
      const lido = lerPerfil(perfil);
      if (!lido.ok) {
        setErroPerfil(lido.erro);
        setPerfilAberto(true);
        // Wait for the section to be open and the error rendered before moving focus.
        return requestAnimationFrame(() => document.getElementById(`${id}-${lido.erro.campo}`)?.focus());
      }
      comparacao = lido.perfil;
    }
    setErroPerfil(null);

    setSituacao({ tipo: "enviando" });
    limparConsulta(); // a query is really going out: forget the last result, so a failure never shows it
    const resposta = await consultar({
      cnpj: soDigitos(cnpj),
      perfil_vendas: { faturamento_mensal: valor!, ...(comparacao && { mix: comparacao.mix }) },
      ...(comparacao && {
        situacao_atual: {
          taxas: comparacao.taxas,
          custo_maquina_mensal: comparacao.custo_maquina_mensal,
          custo_saida: comparacao.custo_saida,
        },
      }),
    });

    if (resposta.tipo === "ok") {
      salvarConsulta(resposta.resultado);
      setSituacao({ tipo: "abrindo_resultado" });
      return router.push("/resultado");
    }
    const falha = mensagemDeFalha(resposta);
    if (falha) return setSituacao({ tipo: "aviso", mensagem: falha });
    if (resposta.tipo !== "erro") return;
    const { codigo, mensagem } = resposta.erro;
    if (codigo === "cnpj_invalido" || codigo === "cnpj_fora_da_demo") {
      setSituacao({ tipo: "ocioso" });
      setErros({ cnpj: mensagem });
      return campoCnpj.current?.focus();
    }
    if (codigo === "nao_implementado") {
      return setSituacao({ tipo: "aviso", mensagem: MENSAGEM_EM_CONSTRUCAO, comExemplo: true });
    }
    setSituacao({ tipo: "aviso", mensagem });
  }

  const enviando = situacao.tipo === "enviando" || situacao.tipo === "abrindo_resultado";

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

      <PerfilVendas
        idBase={id}
        perfil={perfil}
        aoMudar={setPerfil}
        erro={erroPerfil}
        aberto={perfilAberto}
        aoAbrir={setPerfilAberto}
        aoPreencherExemplo={preencherExemplo}
      />

      <div className={estilos.retorno} role="status" aria-live="polite">
        {situacao.tipo === "enviando" && <p>Analisando o CNPJ… Na primeira consulta do dia pode levar até um minuto.</p>}
        {situacao.tipo === "abrindo_resultado" && <p>Análise pronta. Abrindo o resultado…</p>}
        {situacao.tipo === "aviso" && (
          <p className={estilos.aviso}>
            {situacao.mensagem}{" "}
            {situacao.comExemplo && <Link href="/resultado?exemplo">Ver um exemplo ilustrativo do resultado</Link>}
          </p>
        )}
      </div>
    </form>
  );
}
