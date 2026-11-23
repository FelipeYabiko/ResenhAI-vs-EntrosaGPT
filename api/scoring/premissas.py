"""Team premises for scoring, credit limit, advance fee and the demo machine catalog.

They live in api/premissas.toml so they can be reviewed and changed without touching code.
The file starts as status = "proposta"; the API only uses it once the team sets
status = "aprovada" (docs/STATUS.md, T-05). Premises are team choices, not statistics.
"""

import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ARQUIVO = Path(__file__).resolve().parents[1] / "premissas.toml"
FAIXAS = ("A", "B", "C", "D", "E")


class PremissasPendentes(Exception):
    """The premises file is not approved yet."""


class _Modelo(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FaixaDeTempo(_Modelo):
    anos_min: int = Field(ge=0)
    pontos: int
    explicacao: str


class Pontuacao(_Modelo):
    pontos_base: int = Field(ge=0, le=100)
    faixas: dict[Literal["A", "B", "C", "D"], int]  # minimum points for each band; below D is E
    tempo_de_atividade: list[FaixaDeTempo] = Field(min_length=1)
    porte: dict[str, int]


class Recomendacao(_Modelo):
    multiplo_limite: dict[Literal["A", "B", "C", "D", "E"], float]
    antecipacao_base_mensal: float = Field(ge=0)
    antecipacao_premio_mensal: dict[Literal["A", "B", "C", "D", "E"], float]


class TaxasMaquina(_Modelo):
    debito: float | None = None
    credito_a_vista: float | None = None
    credito_parcelado: float | None = None
    pix: float | None = None


class Maquina(_Modelo):
    modelo: str
    motivo: str
    custo_maquina_mensal: float = Field(ge=0)
    taxas: TaxasMaquina


class Premissas(_Modelo):
    status: Literal["proposta", "aprovada"]
    pontuacao: Pontuacao
    recomendacao: Recomendacao
    catalogo: list[Maquina] = Field(min_length=1)


def ler_premissas(arquivo: Path = ARQUIVO) -> Premissas:
    with arquivo.open("rb") as f:
        return Premissas.model_validate(tomllib.load(f))


def carregar_premissas(arquivo: Path = ARQUIVO) -> Premissas:
    """Approved premises, or PremissasPendentes while the team has not approved them."""
    premissas = ler_premissas(arquivo)
    if premissas.status != "aprovada":
        raise PremissasPendentes("As premissas de pontuação e do catálogo ainda não foram aprovadas pelo time.")
    return premissas
