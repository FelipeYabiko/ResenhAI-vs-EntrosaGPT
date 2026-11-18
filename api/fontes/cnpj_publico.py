"""Public CNPJ source (open.cnpja.com): download, sanitize and keep as fixtures.

Rules (docs/DADOS.md): fixed host, timeout, and personal data dropped on the way in.
The answer brings partners (with masked CPF), e-mails, phones and the full address:
`sanitizar` copies only company fields, so nothing personal is ever stored or logged.
"""

import json
import urllib.request
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError

from app.cnpj import cnpj_valido
from app.schemas import Empresa

URL_FONTE = "https://open.cnpja.com/office/"
TEMPO_LIMITE_S = 1.2
NOME_FONTE = "cnpj_publico"
PASTA_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "respostas_fontes"

TAMANHO_MAXIMO = 200_000  # bytes; a normal answer is about 10 KB

# The company name is shown ONLY for legal natures that cannot be one person:
# public administration (1xxx) and corporations / state companies. Everything else
# (LTDA, which may have a single owner; MEI; individual entrepreneur; natural persons, 4xxx)
# gets name = null, because the legal name often carries the owner's name (docs/DADOS.md).
NATUREZAS_COM_NOME = {
    2011,  # Empresa Pública
    2038,  # Sociedade de Economia Mista
    2046,  # Sociedade Anônima Aberta
    2054,  # Sociedade Anônima Fechada
}


def nome_pode_aparecer(natureza_id: int, mei: bool) -> bool:
    return not mei and (1000 <= natureza_id < 2000 or natureza_id in NATUREZAS_COM_NOME)


class DadosEmpresa(BaseModel):
    model_config = ConfigDict(extra="forbid")

    atualizado_em: date
    empresa: Empresa


def _cnae(codigo: int) -> str:
    """6422100 -> 6422-1/00."""
    d = f"{codigo:07d}"
    return f"{d[:4]}-{d[4]}/{d[5:]}"


def sanitizar(resposta: dict, cnpj_pedido: str) -> DadosEmpresa:
    """Keep only company data from a source answer. Raises ValueError if it is not the CNPJ asked for
    or not in the expected format. Error messages never echo values from the answer."""
    try:
        if resposta["taxId"] != cnpj_pedido or not cnpj_valido(cnpj_pedido):
            raise ValueError("Resposta da fonte de CNPJ é de outro CNPJ.")
        empresa = resposta["company"]
        com_nome = nome_pode_aparecer(int(empresa["nature"]["id"]), mei=bool(empresa["simei"]["optant"]))
        return DadosEmpresa(
            atualizado_em=date.fromisoformat(resposta["updated"][:10]),
            empresa=Empresa(
                cnpj=resposta["taxId"],
                nome=empresa["name"] if com_nome else None,
                situacao=resposta["status"]["text"].upper(),
                cnae_principal=_cnae(resposta["mainActivity"]["id"]),
                porte=empresa["size"]["acronym"],
                abertura=date.fromisoformat(resposta["founded"]),
                capital_social=float(empresa["equity"]),
                municipio_uf=f"{resposta['address']['city']}/{resposta['address']['state']}",
            ),
        )
    except ValueError as erro:
        if "outro CNPJ" in str(erro):
            raise
        raise ValueError("Resposta da fonte de CNPJ fora do formato esperado.") from None
    except (KeyError, TypeError, ValidationError):
        raise ValueError("Resposta da fonte de CNPJ fora do formato esperado.") from None


def baixar(cnpj: str, tempo_limite_s: float = TEMPO_LIMITE_S) -> dict:
    """Raw answer from the source. Never log or store it: pass it straight to `sanitizar`.

    The source allows 5 queries per minute per IP. Do not call it in a loop.
    """
    if not cnpj_valido(cnpj):
        raise ValueError("CNPJ inválido: a fonte só é chamada com CNPJ válido.")
    with urllib.request.urlopen(URL_FONTE + cnpj, timeout=tempo_limite_s) as resposta:
        if not resposta.geturl().startswith(URL_FONTE):
            raise ValueError("A fonte de CNPJ redirecionou para outro endereço.")
        corpo = resposta.read(TAMANHO_MAXIMO + 1)
    if len(corpo) > TAMANHO_MAXIMO:
        raise ValueError("Resposta da fonte de CNPJ grande demais.")
    return json.loads(corpo)


def salvar_fixture(dados: DadosEmpresa) -> Path:
    if not cnpj_valido(dados.empresa.cnpj):
        raise ValueError("CNPJ inválido.")
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
