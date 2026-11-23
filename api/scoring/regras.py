"""Rule-based risk score (RF-04). Pure function: no network, no database, no LLM.

Gate: a registration that is not active goes straight to band E (docs/ARQUITETURA.md).
Otherwise: base points + one contribution per rule, clamped to 0..100, then the band.
Every factor carries its contribution and a plain-language explanation.
"""

from datetime import date
from decimal import Decimal

from app.schemas import Empresa, Fator, Pontuacao
from scoring.premissas import Premissas


def _anos_completos(desde: date, hoje: date) -> int:
    return hoje.year - desde.year - ((hoje.month, hoje.day) < (desde.month, desde.day))


def faixa_para(pontos: int, premissas: Premissas) -> str:
    for faixa in ("A", "B", "C", "D"):
        if pontos >= premissas.pontuacao.faixas[faixa]:
            return faixa
    return "E"


def pontuar(empresa: Empresa, faturamento_mensal: Decimal, premissas: Premissas, hoje: date) -> Pontuacao:
    if empresa.situacao != "ATIVA":
        fator = Fator(
            regra="situacao_cadastral",
            contribuicao=0,
            explicacao=f"Situação cadastral {empresa.situacao.lower()}: sem análise de crédito",
        )
        return Pontuacao(faixa="E", pontos=0, fatores=[fator])

    regras = premissas.pontuacao
    anos = _anos_completos(empresa.abertura, hoje)
    tempo = max((f for f in regras.tempo_de_atividade if anos >= f.anos_min), key=lambda f: f.anos_min)
    fatores = [Fator(regra="tempo_de_atividade", contribuicao=tempo.pontos, explicacao=tempo.explicacao)]

    if empresa.porte in regras.porte:
        fatores.append(
            Fator(regra="porte", contribuicao=regras.porte[empresa.porte], explicacao=f"Porte {empresa.porte}")
        )
    else:
        fatores.append(
            Fator(regra="porte", contribuicao=0, explicacao=f"Porte {empresa.porte}: não tem regra, não pesa")
        )

    pontos = max(0, min(100, regras.pontos_base + sum(f.contribuicao for f in fatores)))
    return Pontuacao(faixa=faixa_para(pontos, premissas), pontos=pontos, fatores=fatores)
