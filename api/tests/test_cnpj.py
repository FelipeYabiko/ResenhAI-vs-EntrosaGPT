"""CNPJ check digit validation (RF-01)."""

import pytest
from fastapi.testclient import TestClient

from app.cnpj import cnpj_valido
from app.main import _nao_implementado, app

# 00000000000191 belongs to a large public company (allowed by docs/DADOS.md).
# 98765435000121 is fictitious: valid check digits, not found in the public source on 18/11/2026.
VALIDOS = ["00000000000191", "98765435000121"]

INVALIDOS = [
    "00000000000192",  # wrong second check digit
    "00000000000181",  # wrong first check digit
    "98765435000120",
    "11111111111111",
    "00000000000000",  # passes the check digit formula, but is not a real CNPJ
    "9876543500012",  # 13 digits
    "987654350001211",  # 15 digits
    "98.765.435/0001-21",  # mask must be removed by the front end
    "9876543500012a",
    "",
]


@pytest.mark.parametrize("cnpj", VALIDOS)
def test_aceita_cnpj_com_digitos_corretos(cnpj):
    assert cnpj_valido(cnpj)


@pytest.mark.parametrize("cnpj", INVALIDOS)
def test_recusa_cnpj_invalido(cnpj):
    assert not cnpj_valido(cnpj)


cliente = TestClient(app)


def _espiao(chamadas: list):
    """Stand-in for the next step: records the call, then answers 501 like the real stub."""

    def proxima_etapa(entrada):
        chamadas.append(entrada)
        raise _nao_implementado()

    return proxima_etapa


def _consultar(cnpj: str):
    return cliente.post("/v1/consultas", json={"cnpj": cnpj, "perfil_vendas": {"faturamento_mensal": 10000}})


def test_consulta_com_digito_errado_devolve_cnpj_invalido():
    resposta = _consultar("98765435000120")
    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "cnpj_invalido"


def test_cnpj_invalido_e_recusado_antes_de_qualquer_outra_etapa(monkeypatch):
    chamadas = []
    monkeypatch.setattr("app.main._depois_da_validacao", _espiao(chamadas))
    resposta = _consultar("98765435000120")
    assert resposta.status_code == 422
    assert chamadas == []


def test_cnpj_valido_segue_para_a_proxima_etapa(monkeypatch):
    chamadas = []
    monkeypatch.setattr("app.main._depois_da_validacao", _espiao(chamadas))
    resposta = _consultar("98765435000121")
    assert len(chamadas) == 1
    assert resposta.status_code == 501
