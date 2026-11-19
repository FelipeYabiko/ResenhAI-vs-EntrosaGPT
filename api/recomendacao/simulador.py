"""Cost simulator core (RF-11, RF-12). Pure function: no network, no database, no LLM.

Monthly cost of a card terminal setup = sum over payment types of
revenue x share of the mix x rate, plus the monthly machine cost (docs/ARQUITETURA.md).
Savings = current cost - cost with the offer. Exact decimals, rounded to cents at the end.

Not here on purpose (open premises, owned by Kayke, issue #18): the demo catalog of offers,
the Pix rate of each offer, and the cost of receivable advance when the desired payout term
is shorter than the offer's. Callers pass offers and rates in; nothing is assumed.
"""

import math
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from app.schemas import Economia

MODALIDADES = ("debito", "credito_a_vista", "credito_parcelado", "pix")
CENTAVO = Decimal("0.01")
CEM = Decimal(100)

Taxas = dict[str, Decimal | None]  # percent per payment type; None = not informed (never zero)


class TaxaNaoInformada(ValueError):
    """A payment type with sales has no rate. We refuse to guess it (docs/DADOS.md: never assume Pix is free)."""


@dataclass(frozen=True)
class SituacaoAtual:
    taxas: Taxas
    custo_maquina_mensal: Decimal = Decimal(0)
    custo_saida: Decimal = Decimal(0)  # fine or machine already paid for, to leave the current provider


@dataclass(frozen=True)
class Oferta:
    nome: str
    taxas: Taxas
    custo_maquina_mensal: Decimal = Decimal(0)


@dataclass(frozen=True)
class ResultadoSimulacao:
    oferta: str
    custo_mensal_atual: Decimal
    custo_mensal_oferta: Decimal
    economia_mensal: Decimal
    economia_anual: Decimal
    meses_para_compensar_saida: int | None  # None: the offer never pays the exit cost back
    estimado: bool = field(default=True)

    def para_contrato(self) -> Economia:
        return Economia(
            custo_mensal_atual=float(self.custo_mensal_atual),
            custo_mensal_oferta=float(self.custo_mensal_oferta),
            economia_mensal=float(self.economia_mensal),
            economia_anual=float(self.economia_anual),
            meses_para_compensar_saida=self.meses_para_compensar_saida,
            estimado=True,
        )


def _validar(faturamento: Decimal, mix: dict[str, Decimal]) -> None:
    if faturamento <= 0:
        raise ValueError("O faturamento mensal precisa ser maior que zero.")
    if set(mix) != set(MODALIDADES):
        raise ValueError(f"O mix precisa ter exatamente: {', '.join(MODALIDADES)}.")
    if any(parte < 0 for parte in mix.values()) or sum(mix.values()) != CEM:
        raise ValueError("O mix de pagamento precisa ter partes positivas que somam 100.")


def _custo_das_taxas(faturamento: Decimal, mix: dict[str, Decimal], taxas: Taxas, lado: str) -> Decimal:
    total = Decimal(0)
    for modalidade in MODALIDADES:
        if mix[modalidade] == 0:
            continue
        taxa = taxas.get(modalidade)
        if taxa is None:
            raise TaxaNaoInformada(f"Falta a taxa de {modalidade} ({lado}), e ela tem vendas no mix.")
        total += faturamento * mix[modalidade] / CEM * taxa / CEM
    return total


def simular(faturamento: Decimal, mix: dict[str, Decimal], atual: SituacaoAtual, oferta: Oferta) -> ResultadoSimulacao:
    _validar(faturamento, mix)
    custo_atual = _custo_das_taxas(faturamento, mix, atual.taxas, "situação atual") + atual.custo_maquina_mensal
    custo_oferta = _custo_das_taxas(faturamento, mix, oferta.taxas, oferta.nome) + oferta.custo_maquina_mensal

    custo_atual = custo_atual.quantize(CENTAVO, ROUND_HALF_UP)
    custo_oferta = custo_oferta.quantize(CENTAVO, ROUND_HALF_UP)
    economia = custo_atual - custo_oferta

    if atual.custo_saida <= 0:
        meses = 0
    elif economia <= 0:
        meses = None
    else:
        meses = math.ceil(atual.custo_saida / economia)  # a partial month counts as a whole month

    return ResultadoSimulacao(
        oferta=oferta.nome,
        custo_mensal_atual=custo_atual,
        custo_mensal_oferta=custo_oferta,
        economia_mensal=economia,
        economia_anual=economia * 12,
        meses_para_compensar_saida=meses,
    )


def comparar_ofertas(
    faturamento: Decimal, mix: dict[str, Decimal], atual: SituacaoAtual, ofertas: list[Oferta]
) -> list[ResultadoSimulacao]:
    """Every offer simulated, cheapest first (docs/ARQUITETURA.md: always show the cost of each one)."""
    return sorted((simular(faturamento, mix, atual, o) for o in ofertas), key=lambda r: r.custo_mensal_oferta)
