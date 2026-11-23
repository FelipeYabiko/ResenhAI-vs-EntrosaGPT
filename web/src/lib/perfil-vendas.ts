// Optional "compare with the current card machine" part of the form: how the merchant gets paid
// (share of sales per payment type) and what they pay today. Without it the API cannot estimate
// savings (D-019); with it, every payment type that has sales needs today's rate, so nothing is
// guessed (the API never treats a missing rate as zero). This file only reads and checks what
// was typed: all the math is done by the API.
import { lerReais } from "./formato";

export const MODALIDADES = [
  { chave: "debito", nome: "Débito" },
  { chave: "credito_a_vista", nome: "Crédito à vista" },
  { chave: "credito_parcelado", nome: "Crédito parcelado" },
  { chave: "pix", nome: "Pix" },
] as const;

export type Modalidade = (typeof MODALIDADES)[number]["chave"];
type PorModalidade<T> = Record<Modalidade, T>;

export type PerfilDigitado = {
  mix: PorModalidade<string>;
  taxas: PorModalidade<string>;
  custoMaquina: string;
  custoSaida: string;
};

const vazio = { debito: "", credito_a_vista: "", credito_parcelado: "", pix: "" };
export const PERFIL_VAZIO: PerfilDigitado = { mix: { ...vazio }, taxas: { ...vazio }, custoMaquina: "", custoSaida: "" };

// The project's reference case (docs/PRODUTO.md, RF-11; docs/ARQUITETURA.md, "Simulador de custo")
// on the fictitious demo merchant. Pix without fee is part of that documented case.
export const EXEMPLO_MERCADINHO = {
  cnpj: "98.765.432/0001-98",
  faturamento: "15.000",
  perfil: {
    mix: { debito: "40", credito_a_vista: "40", credito_parcelado: "0", pix: "20" },
    taxas: { debito: "1,99", credito_a_vista: "4,98", credito_parcelado: "", pix: "0" },
    custoMaquina: "",
    custoSaida: "",
  } satisfies PerfilDigitado,
};

/** Field ids used to point errors and focus at the right input. */
export const campoDoMix = (m: Modalidade) => `mix-${m}`;
export const campoDaTaxa = (m: Modalidade) => `taxa-${m}`;

/** `grupo: "mix"` marks an error about the shares as a whole (the sum), shown on all four share fields. */
export type ErroPerfil = { campo: string; mensagem: string; grupo?: "mix" };

export type PerfilLido = {
  mix: PorModalidade<number>;
  taxas: PorModalidade<number | null>;
  custo_maquina_mensal: number;
  custo_saida: number;
};

/** True when anything in the section was typed: then it is checked, so nothing typed is silently dropped. */
export function perfilEmUso(perfil: PerfilDigitado): boolean {
  const textos = [...Object.values(perfil.mix), ...Object.values(perfil.taxas), perfil.custoMaquina, perfil.custoSaida];
  return textos.some((v) => v.trim() !== "");
}

/** Same tolerance as the API contract (api/app/schemas.py, Mix). */
export function somaFechaCem(soma: number): boolean {
  return Math.abs(soma - 100) <= 0.01;
}

function lerNumero(texto: string): number | null {
  return lerReais(texto.replace("%", ""));
}

/** Sum of the typed shares, or null while a share is not a number. */
export function somaDoMix(perfil: PerfilDigitado): number | null {
  let soma = 0;
  for (const { chave } of MODALIDADES) {
    const texto = perfil.mix[chave].trim();
    if (texto === "") continue;
    const valor = lerNumero(texto);
    if (valor === null) return null;
    soma += valor;
  }
  return Math.round(soma * 100) / 100;
}

export function lerPerfil(perfil: PerfilDigitado): { ok: true; perfil: PerfilLido } | { ok: false; erro: ErroPerfil } {
  const mix = {} as PorModalidade<number>;
  for (const { chave, nome } of MODALIDADES) {
    const texto = perfil.mix[chave].trim();
    const valor = texto === "" ? 0 : lerNumero(texto);
    if (valor === null || valor < 0 || valor > 100) {
      return { ok: false, erro: { campo: campoDoMix(chave), mensagem: `A parte de ${nome} precisa ser um número de 0 a 100.` } };
    }
    mix[chave] = valor;
  }
  const soma = somaDoMix(perfil) ?? 0;
  if (!somaFechaCem(soma)) {
    return {
      ok: false,
      erro: {
        grupo: "mix",
        campo: campoDoMix("debito"),
        mensagem: `As formas de pagamento precisam somar 100% (hoje somam ${soma.toLocaleString("pt-BR")}%).`,
      },
    };
  }

  const taxas = {} as PorModalidade<number | null>;
  for (const { chave, nome } of MODALIDADES) {
    const texto = perfil.taxas[chave].trim();
    const valor = texto === "" ? null : lerNumero(texto);
    if (texto !== "" && (valor === null || valor > 100)) {
      return { ok: false, erro: { campo: campoDaTaxa(chave), mensagem: `A taxa de ${nome} precisa ser um número, como 1,99.` } };
    }
    if (mix[chave] > 0 && valor === null) {
      return {
        ok: false,
        erro: {
          campo: campoDaTaxa(chave),
          mensagem: `Informe a taxa de ${nome} que o comerciante paga hoje: essa forma tem vendas. Se não houver taxa, escreva 0.`,
        },
      };
    }
    taxas[chave] = valor;
  }

  const custos: number[] = [];
  for (const [texto, campo, nome] of [
    [perfil.custoMaquina, "custo-maquina", "O custo mensal da máquina"],
    [perfil.custoSaida, "custo-saida", "O custo para trocar de máquina"],
  ] as const) {
    const valor = texto.trim() === "" ? 0 : lerReais(texto);
    if (valor === null || valor < 0) {
      return { ok: false, erro: { campo, mensagem: `${nome} precisa ser um valor em reais, como 49,90.` } };
    }
    custos.push(valor);
  }

  return { ok: true, perfil: { mix, taxas, custo_maquina_mensal: custos[0], custo_saida: custos[1] } };
}
