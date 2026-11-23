"use client";

import {
  campoDaTaxa,
  campoDoMix,
  MODALIDADES,
  somaDoMix,
  type ErroPerfil,
  type Modalidade,
  type PerfilDigitado,
} from "@/lib/perfil-vendas";
import estilos from "./PerfilVendas.module.css";

type Props = {
  idBase: string;
  perfil: PerfilDigitado;
  aoMudar: (perfil: PerfilDigitado) => void;
  erro: ErroPerfil | null;
  aberto: boolean;
  aoAbrir: (aberto: boolean) => void;
  aoPreencherExemplo: () => void;
};

/** Optional section: how the merchant gets paid and what they pay today, so the API can estimate savings. */
export function PerfilVendas({ idBase, perfil, aoMudar, erro, aberto, aoAbrir, aoPreencherExemplo }: Props) {
  const id = (campo: string) => `${idBase}-${campo}`;
  const idErro = id("perfil-erro");
  const soma = somaDoMix(perfil);

  function campo(nome: string, rotulo: string, valor: string, mudar: (v: string) => void, dica?: string) {
    const comErro = erro?.campo === nome;
    return (
      <div className={estilos.campo}>
        <label htmlFor={id(nome)}>{rotulo}</label>
        <input
          id={id(nome)}
          inputMode="decimal"
          autoComplete="off"
          value={valor}
          onChange={(e) => mudar(e.target.value)}
          aria-invalid={comErro ? true : undefined}
          aria-describedby={[comErro ? idErro : null, dica].filter(Boolean).join(" ") || undefined}
        />
      </div>
    );
  }

  const mudarMix = (m: Modalidade) => (v: string) => aoMudar({ ...perfil, mix: { ...perfil.mix, [m]: v } });
  const mudarTaxa = (m: Modalidade) => (v: string) => aoMudar({ ...perfil, taxas: { ...perfil.taxas, [m]: v } });

  return (
    <details className={estilos.perfil} open={aberto} onToggle={(e) => aoAbrir(e.currentTarget.open)}>
      <summary>Comparar com a maquininha atual (opcional)</summary>
      <div className={estilos.conteudo}>
        <p>
          Para estimar a economia, informe como o comerciante recebe e quanto paga hoje. São estimativas do
          comerciante.
        </p>
        <button type="button" className="botao" onClick={aoPreencherExemplo}>
          Preencher com o exemplo do mercadinho (fictício)
        </button>

        <fieldset className={estilos.grupo} aria-describedby={id("soma")}>
          <legend>Como o comerciante recebe (% das vendas)</legend>
          <div className={estilos.grade}>
            {MODALIDADES.map(({ chave, nome }) =>
              campo(campoDoMix(chave), `${nome}: parte das vendas (%)`, perfil.mix[chave], mudarMix(chave)),
            )}
          </div>
          <p id={id("soma")} className={estilos.soma}>
            {soma === null ? "Soma: confira os números" : `Soma: ${soma.toLocaleString("pt-BR")}%`}
            {soma !== null && soma !== 100 && " (precisa dar 100%)"}
          </p>
        </fieldset>

        <fieldset className={estilos.grupo}>
          <legend>Taxa que paga hoje em cada forma (%)</legend>
          <p id={id("taxas-dica")} className={estilos.dica}>
            Obrigatória para as formas com vendas. Sem taxa, escreva 0.
          </p>
          <div className={estilos.grade}>
            {MODALIDADES.map(({ chave, nome }) =>
              campo(
                campoDaTaxa(chave),
                `${nome}: taxa que paga hoje (%)`,
                perfil.taxas[chave],
                mudarTaxa(chave),
                id("taxas-dica"),
              ),
            )}
          </div>
        </fieldset>

        <fieldset className={estilos.grupo}>
          <legend>Custos da máquina atual (opcional)</legend>
          <div className={estilos.grade}>
            {campo("custo-maquina", "Custo mensal da máquina atual (R$)", perfil.custoMaquina, (v) =>
              aoMudar({ ...perfil, custoMaquina: v }),
            )}
            {campo(
              "custo-saida",
              "Custo para trocar de máquina (R$)",
              perfil.custoSaida,
              (v) => aoMudar({ ...perfil, custoSaida: v }),
              id("saida-dica"),
            )}
          </div>
          <p id={id("saida-dica")} className={estilos.dica}>
            Multa ou máquina já paga. Mostra em quantos meses a economia compensa a troca.
          </p>
        </fieldset>

        {erro && (
          <p id={idErro} className={estilos.erro} role="alert">
            {erro.mensagem}
          </p>
        )}
      </div>
    </details>
  );
}
