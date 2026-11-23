"""Builds the query result from company data, the sales profile and the approved premises.

Pure function: no network, no database, no LLM. Score, limit, fee and savings are all
deterministic code (AGENTS.md). Missing inputs give a null economy, never a guessed one.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4

from app.schemas import (
    AVISO_SIMULACAO,
    BenchmarkMercado,
    ConsultaEntrada,
    ConsultaResultado,
    Economia,
    Empresa,
    Fonte,
    Maquina,
    Recomendacao,
    TaxasAntecipacao,
)
from recomendacao.simulador import CenarioAtual, Oferta, TaxaNaoInformada, comparar_ofertas
from scoring.premissas import Premissas
from scoring.regras import pontuar


def _decimal(valor: float | None) -> Decimal | None:
    return None if valor is None else Decimal(str(valor))  # str(): Decimal(33.33) would be 33.3299...


def _ofertas(premissas: Premissas) -> list[Oferta]:
    return [
        Oferta(
            nome=m.modelo,
            taxas={k: _decimal(v) for k, v in m.taxas.model_dump().items()},
            custo_maquina_mensal=_decimal(m.custo_maquina_mensal),
        )
        for m in premissas.catalogo
    ]


def _economia(entrada: ConsultaEntrada, premissas: Premissas) -> tuple[Economia | None, str | None]:
    """Savings with the cheapest catalog machine, or (None, None) when there is nothing to compare."""
    perfil, atual = entrada.perfil_vendas, entrada.situacao_atual
    if perfil.mix is None or atual is None:
        return None, None
    try:
        melhor = comparar_ofertas(
            _decimal(perfil.faturamento_mensal),
            {k: _decimal(v) for k, v in perfil.mix.model_dump().items()},
            CenarioAtual(
                taxas={k: _decimal(v) for k, v in atual.taxas.model_dump().items()},
                custo_maquina_mensal=_decimal(atual.custo_maquina_mensal),
                custo_saida=_decimal(atual.custo_saida),
            ),
            _ofertas(premissas),
        )[0]
    except (TaxaNaoInformada, ValueError):
        # A rate is missing on one side: no comparison, no invented number. (Invalid mix or revenue never
        # gets here: the API schema already refuses them.)
        return None, None
    return melhor.para_contrato(), melhor.oferta


def montar_resultado(
    entrada: ConsultaEntrada, empresa: Empresa, fontes: list[Fonte], premissas: Premissas, hoje: date, tempo_ms: int
) -> ConsultaResultado:
    faturamento = _decimal(entrada.perfil_vendas.faturamento_mensal)
    pontuacao = pontuar(empresa, faturamento, premissas, hoje)
    regras = premissas.recomendacao

    economia, modelo_mais_barato = _economia(entrada, premissas)
    maquina = next(m for m in premissas.catalogo if m.modelo == (modelo_mais_barato or premissas.catalogo[0].modelo))

    limite = (faturamento * Decimal(str(regras.multiplo_limite[pontuacao.faixa]))).quantize(
        Decimal("0.01"), ROUND_HALF_UP
    )
    antecipacao = Decimal(str(regras.antecipacao_base_mensal)) + Decimal(
        str(regras.antecipacao_premio_mensal[pontuacao.faixa])
    )

    return ConsultaResultado(
        consulta_id=f"c_{uuid4().hex[:12]}",
        empresa=empresa,
        fontes=fontes,
        pontuacao=pontuacao,
        recomendacao=Recomendacao(
            maquina=Maquina(modelo=maquina.modelo, motivo=maquina.motivo),
            limite_credito_simulado=float(limite),
            taxas_antecipacao_simuladas=TaxasAntecipacao(mensal_percentual=float(antecipacao)),
        ),
        economia=economia,
        benchmark_mercado=BenchmarkMercado(
            disponivel=False, referencia="Banco Central, taxas de desconto (MDR)", data_referencia=None
        ),
        tempo_ms=tempo_ms,
        aviso=AVISO_SIMULACAO,
    )
