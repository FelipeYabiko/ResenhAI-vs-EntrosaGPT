// Comparison examples shown on the landing page.
// D-017: these values come from Amanda's prototype and are ILLUSTRATIVE, not the simulator's output
// and not any provider's real fees. When the simulator (issue #18) exists, the cards show its result.
// Only profiles with values in the prototype are listed; nothing here is invented.

export type ExemploComparacao = {
  id: string;
  perfil: string;
  custoAtualMensal: number;
  custoRecomendadoMensal: number;
  taxaAtual: string;
  taxaRecomendada: string;
};

export const EXEMPLOS: ExemploComparacao[] = [
  {
    id: "mercadinho",
    perfil: "Mercadinho",
    custoAtualMensal: 350,
    custoRecomendadoMensal: 240,
    taxaAtual: "3,5%",
    taxaRecomendada: "2,4%",
  },
];
