"""CNPJ check digit validation (RF-01)."""

import pytest
from fastapi.testclient import TestClient

from app.cnpj import cnpj_valido
from app.main import _nao_implementado, app

# 00000000000191 belongs to a large public company (allowed by docs/DADOS.md).
# 11222333000181 is a fictitious number with valid check digits.
VALIDOS = ["00000000000191", "11222333000181"]

INVALIDOS = [
    "00000000000192",  # wrong second check digit
    "00000000000181",  # wrong first check digit
    "11222333000180",
    "11111111111111",
    "00000000000000",  # passes the check digit formula, but is not a real CNPJ
    "1122233300018",  # 13 digits
    "112223330001811",  # 15 digits
    "11.222.333/0001-81",  # mask must be removed by the front end
    "1122233300018a",
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
    resposta = _consultar("11222333000180")
    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "cnpj_invalido"


def test_cnpj_invalido_e_recusado_antes_de_qualquer_outra_etapa(monkeypatch):
    chamadas = []
    monkeypatch.setattr("app.main._depois_da_validacao", _espiao(chamadas))
    resposta = _consultar("11222333000180")
    assert resposta.status_code == 422
    assert chamadas == []


def test_cnpj_valido_segue_para_a_proxima_etapa(monkeypatch):
    chamadas = []
    monkeypatch.setattr("app.main._depois_da_validacao", _espiao(chamadas))
    resposta = _consultar("11222333000181")
    assert len(chamadas) == 1
    assert resposta.status_code == 501
