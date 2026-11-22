// ILLUSTRATIVE result, used only on /resultado?exemplo while POST /v1/consultas is not finished (issue #16).
// The page always labels it as an example and never lets it become a proposal.
// Shape: the ConsultaResultado example in docs/ARQUITETURA.md. Changes from that example:
// - company: the fictitious "Mercadinho Boa Vista" (fixtures/respostas_fontes/98765432000198.json), not a
//   real company, so no real company appears with a risk band (open question in docs/STATUS.md, 18/11);
// - economy: the RF-11 reference case (docs/PRODUTO.md), the same numbers the simulator tests check.
// Score, machine, limit and rates are placeholders until the scoring premises exist (T-05).
import type { ConsultaResultado } from "./api";

export const RESULTADO_EXEMPLO: ConsultaResultado = {
  consulta_id: "exemplo",
  empresa: {
    cnpj: "98765432000198",
    nome: "MERCADINHO BOA VISTA (FICTÍCIO)",
    situacao: "ATIVA",
    cnae_principal: "4712-1/00",
    porte: "ME",
    abertura: "2018-03-12",
    capital_social: 20000,
    municipio_uf: "São Paulo/SP",
  },
  fontes: [
    { nome: "cnpj_publico", status: "ok", atualizado_em: "2026-11-18", em_cache: true },
  ],
  pontuacao: {
    faixa: "B",
    pontos: 72,
    fatores: [
      { regra: "tempo_de_atividade", contribuicao: 10, explicacao: "Empresa aberta há mais de 5 anos (fator ilustrativo)" },
    ],
  },
  recomendacao: {
    maquina: { modelo: "Plus", motivo: "Perfil de vendas na faixa do modelo" },
    limite_credito_simulado: 50000,
    taxas_antecipacao_simuladas: { mensal_percentual: 0 },
  },
  economia: {
    custo_mensal_atual: 418.2,
    custo_mensal_oferta: 248.4,
    economia_mensal: 169.8,
    economia_anual: 2037.6,
    meses_para_compensar_saida: 0,
    estimado: true,
  },
  benchmark_mercado: {
    disponivel: false,
    referencia: "Banco Central, taxas de desconto (MDR)",
    data_referencia: null,
  },
  tempo_ms: 840,
  aviso: "Simulação. Não é oferta de crédito.",
};
