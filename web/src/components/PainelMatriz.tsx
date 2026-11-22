"use client";

// Back-office panel (issue #24, T-15): proposals arrive live over SSE (RF-06), without reloading the page.
import { useCallback, useEffect, useId, useState } from "react";
import { listarPropostas, obterProposta, ouvirEventos, type Evento, type Proposta } from "@/lib/api";
import { mascararCnpj } from "@/lib/cnpj";
import { mensagemDeFalha } from "@/lib/mensagens";
import { CartaoProposta, NOMES_DOS_STATUS } from "./CartaoProposta";
import formulario from "./FormularioAnalise.module.css";
import estilos from "./PainelMatriz.module.css";

type Status = Proposta["status"];
type Conexao = "conectando" | "ao_vivo" | "reconectando" | "desligada";

const TIPOS_DE_EVENTO: Evento["tipo"][] = [
  "proposta.criada",
  "proposta.pendente",
  "proposta.aprovada",
  "proposta.recusada",
];

const TEXTO_DA_CONEXAO: Record<Conexao, string> = {
  conectando: "Conectando ao vivo…",
  ao_vivo: "Ao vivo: novas propostas aparecem sozinhas.",
  reconectando: "Conexão caiu. Tentando de novo…",
  desligada: "Sem conexão ao vivo.",
};

const maisNovaPrimeiro = (a: Proposta, b: Proposta) => b.criada_em.localeCompare(a.criada_em);

function anunciar(evento: Evento, proposta: Proposta): string {
  const quem = proposta.resumo.nome ?? `CNPJ ${mascararCnpj(proposta.resumo.cnpj)}`;
  if (evento.tipo === "proposta.criada") return `Nova proposta: ${quem}, faixa ${proposta.resumo.faixa}.`;
  return `Proposta de ${quem}: ${NOMES_DOS_STATUS[proposta.status]}.`;
}

export function PainelMatriz() {
  const id = useId();
  const [propostas, setPropostas] = useState<Proposta[] | null>(null);
  const [erroLista, setErroLista] = useState<string | null>(null);
  const [conexao, setConexao] = useState<Conexao>("conectando");
  const [tentativa, setTentativa] = useState(0);
  const [filtro, setFiltro] = useState<Status | "todas">("todas");
  const [anuncio, setAnuncio] = useState("");

  const guardar = useCallback((proposta: Proposta) => {
    setPropostas((lista) =>
      [proposta, ...(lista ?? []).filter((p) => p.proposta_id !== proposta.proposta_id)].sort(maisNovaPrimeiro),
    );
  }, []);

  useEffect(() => {
    let ativo = true;
    let caiu = false;

    async function carregarLista() {
      const resposta = await listarPropostas();
      if (!ativo) return;
      if (resposta.tipo === "ok") {
        setPropostas([...resposta.resultado.propostas].sort(maisNovaPrimeiro));
        setErroLista(null);
      } else {
        setErroLista(mensagemDeFalha(resposta) ?? (resposta.tipo === "erro" ? resposta.erro.mensagem : null));
      }
    }

    // The event only says which proposal changed; the panel reads the proposal itself, so it never
    // shows a status it did not get from the API.
    async function aoEvento(mensagem: MessageEvent<string>) {
      let evento: Evento;
      try {
        evento = JSON.parse(mensagem.data);
      } catch {
        return;
      }
      const resposta = await obterProposta(evento.proposta_id);
      if (!ativo || resposta.tipo !== "ok") return;
      guardar(resposta.resultado);
      setAnuncio(anunciar(evento, resposta.resultado));
    }

    carregarLista();
    const fonte = ouvirEventos();
    fonte.onopen = () => {
      setConexao("ao_vivo");
      // Back after a drop: reload the list, so nothing that happened meanwhile is missing.
      if (caiu) carregarLista();
      caiu = false;
    };
    fonte.onerror = () => {
      caiu = true;
      // CLOSED: the browser gave up (for example, 503 "muitos painéis"). Otherwise it retries by itself.
      setConexao(fonte.readyState === EventSource.CLOSED ? "desligada" : "reconectando");
    };
    for (const tipo of TIPOS_DE_EVENTO) fonte.addEventListener(tipo, aoEvento);

    return () => {
      ativo = false;
      fonte.close();
    };
  }, [guardar, tentativa]);

  const visiveis = (propostas ?? []).filter((p) => filtro === "todas" || p.status === filtro);

  return (
    <div className={estilos.painel}>
      <h1>Painel da matriz</h1>
      <p className={estilos.avisoSimulacao}>
        <strong>Simulação. Não é oferta de crédito.</strong> Propostas de demonstração: aprovar gera um contrato simulado,
        sem valor legal.
      </p>

      <div className={estilos.barraPainel}>
        <p className={estilos.conexao} data-conexao={conexao}>
          {TEXTO_DA_CONEXAO[conexao]}
        </p>
        {conexao === "desligada" && (
          <button
            type="button"
            className={`botao ${estilos.secundario}`}
            onClick={() => {
              setConexao("conectando");
              setTentativa((n) => n + 1);
            }}
          >
            Reconectar
          </button>
        )}
        <div className={`${formulario.campo} ${estilos.filtro}`}>
          <label htmlFor={`${id}-filtro`}>Mostrar</label>
          <select
            id={`${id}-filtro`}
            value={filtro}
            onChange={(e) => setFiltro(e.target.value as Status | "todas")}
          >
            <option value="todas">Todas as propostas</option>
            {(Object.keys(NOMES_DOS_STATUS) as Status[]).map((status) => (
              <option key={status} value={status}>
                {NOMES_DOS_STATUS[status]}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* New proposals and decisions are announced here without moving the focus. */}
      <p role="status" aria-live="polite" className={estilos.anuncio}>
        {anuncio}
      </p>

      {erroLista && (
        <p role="alert" className={estilos.erroLista}>
          Não foi possível carregar a lista. {erroLista}{" "}
          <button type="button" className={`botao ${estilos.secundario}`} onClick={() => setTentativa((n) => n + 1)}>
            Tentar de novo
          </button>
        </p>
      )}

      {propostas === null && !erroLista && <p>Carregando as propostas…</p>}

      {propostas !== null && (
        <>
          <p className={estilos.contagem}>
            {visiveis.length === 1 ? "1 proposta" : `${visiveis.length} propostas`}
            {filtro !== "todas" && ` com o status "${NOMES_DOS_STATUS[filtro]}"`}.
          </p>
          {visiveis.length === 0 ? (
            <p>
              {propostas.length === 0
                ? "Nenhuma proposta ainda. Quando um agente enviar, ela aparece aqui sem recarregar a página."
                : "Nenhuma proposta com esse status."}
            </p>
          ) : (
            <ul className={estilos.lista}>
              {visiveis.map((proposta) => (
                <li key={proposta.proposta_id}>
                  <CartaoProposta proposta={proposta} aoMudar={guardar} />
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
