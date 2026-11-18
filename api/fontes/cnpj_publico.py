"""Public CNPJ source (open.cnpja.com): download, sanitize and keep as fixtures.

Rules (docs/DADOS.md): fixed host, timeout, and personal data dropped on the way in.
The answer brings partners (with masked CPF), e-mails, phones and the full address:
`sanitizar` copies only company fields, so nothing personal is ever stored or logged.
"""

import json
import re
import urllib.request
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.cnpj import cnpj_valido
from app.schemas import Empresa

URL_FONTE = "https://open.cnpja.com/office/"
TEMPO_LIMITE_S = 1.2
NOME_FONTE = "cnpj_publico"
PASTA_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "respostas_fontes"

# Legal natures whose legal name usually carries the owner's name: hide it (docs/DADOS.md).
_NATUREZA_DE_PESSOA = re.compile(r"individual|unipessoal", re.IGNORECASE)


class DadosEmpresa(BaseModel):
    model_config = ConfigDict(extra="forbid")

    atualizado_em: date
    empresa: Empresa


def _cnae(codigo: int) -> str:
    """6422100 -> 6422-1/00."""
    d = f"{codigo:07d}"
    return f"{d[:4]}-{d[4]}/{d[5:]}"


def sanitizar(resposta: dict) -> DadosEmpresa:
    """Keep only company data from a source answer. Raises ValueError if fields are missing."""
    try:
        empresa = resposta["company"]
        pessoa_no_nome = empresa["simei"]["optant"] or _NATUREZA_DE_PESSOA.search(empresa["nature"]["text"])
        return DadosEmpresa(
            atualizado_em=date.fromisoformat(resposta["updated"][:10]),
            empresa=Empresa(
                cnpj=resposta["taxId"],
                nome=None if pessoa_no_nome else empresa["name"],
                situacao=resposta["status"]["text"].upper(),
                cnae_principal=_cnae(resposta["mainActivity"]["id"]),
                porte=empresa["size"]["acronym"],
                abertura=date.fromisoformat(resposta["founded"]),
                capital_social=float(empresa["equity"]),
                municipio_uf=f"{resposta['address']['city']}/{resposta['address']['state']}",
            ),
        )
    except (KeyError, TypeError) as erro:
        raise ValueError(f"Resposta da fonte de CNPJ fora do formato esperado (campo {erro}).") from None


def baixar(cnpj: str, tempo_limite_s: float = TEMPO_LIMITE_S) -> dict:
    """Raw answer from the source. Never log or store it: pass it straight to `sanitizar`.

    The source allows 5 queries per minute per IP. Do not call it in a loop.
    """
    if not cnpj_valido(cnpj):
        raise ValueError("CNPJ inválido: a fonte só é chamada com CNPJ válido.")
    with urllib.request.urlopen(URL_FONTE + cnpj, timeout=tempo_limite_s) as resposta:
        return json.load(resposta)


def salvar_fixture(dados: DadosEmpresa) -> Path:
    arquivo = PASTA_FIXTURES / f"{dados.empresa.cnpj}.json"
    conteudo = {"fonte": NOME_FONTE, **dados.model_dump(mode="json")}
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return arquivo


def carregar_fixture(cnpj: str) -> DadosEmpresa | None:
    """Sanitized company data saved earlier, or None if there is no fixture for this CNPJ."""
    arquivo = PASTA_FIXTURES / f"{cnpj}.json"
    if not cnpj_valido(cnpj) or not arquivo.exists():
        return None
    conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
    conteudo.pop("fonte", None)
    return DadosEmpresa.model_validate(conteudo)
