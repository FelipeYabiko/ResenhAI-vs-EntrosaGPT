"""Demo CNPJ list (fixtures/cnpjs_demo.json): the only CNPJs the public demo accepts (MODO_DEMO=true).

Large companies were confirmed in the public source; fictitious ones have valid check digits and were
confirmed as NOT existing in the source (scripts/gerar_cnpj_ficticio.py), so none of them is a person.
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

ARQUIVO = Path(__file__).resolve().parents[2] / "fixtures" / "cnpjs_demo.json"


class CnpjDemo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cnpj: str
    apelido: str
    origem: Literal["real_empresa_grande", "ficticio"]
    perfil: Literal["mercadinho", "salao", "loja_construcao"] | None = None
    conferido_em: str


def cnpjs_da_demo() -> dict[str, CnpjDemo]:
    conteudo = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    return {item["cnpj"]: CnpjDemo.model_validate(item) for item in conteudo["cnpjs"]}


def esta_na_demo(cnpj: str) -> bool:
    return cnpj in cnpjs_da_demo()
