"""The demo CNPJ list is consistent: valid, with data, and nothing that can point to a person."""

import json

import pytest

from app.cnpj import cnpj_valido
from fontes.cnpj_publico import PASTA_FIXTURES, carregar_fixture
from fontes.demo import cnpjs_da_demo, esta_na_demo

DEMO = cnpjs_da_demo()
FONTE_ESPERADA = {"real_empresa_grande": "cnpj_publico", "ficticio": "ficticio"}


def test_lista_tem_empresas_grandes_e_os_tres_perfis_da_landing():
    origens = {item.origem for item in DEMO.values()}
    perfis = {item.perfil for item in DEMO.values() if item.perfil}
    assert origens == {"real_empresa_grande", "ficticio"}
    assert perfis == {"mercadinho", "salao", "loja_construcao"}


@pytest.mark.parametrize("cnpj", sorted(DEMO))
def test_cada_cnpj_e_valido_e_tem_dados(cnpj):
    assert cnpj_valido(cnpj)
    assert carregar_fixture(cnpj) is not None


@pytest.mark.parametrize("cnpj", sorted(DEMO))
def test_origem_bate_com_os_dados(cnpj):
    fonte = json.loads((PASTA_FIXTURES / f"{cnpj}.json").read_text(encoding="utf-8"))["fonte"]
    assert fonte == FONTE_ESPERADA[DEMO[cnpj].origem]


@pytest.mark.parametrize("cnpj", sorted(c for c, item in DEMO.items() if item.origem == "ficticio"))
def test_ficticio_se_apresenta_como_ficticio(cnpj):
    # On screen and in the video, nobody should take these for real merchants.
    assert "(FICTÍCIO)" in carregar_fixture(cnpj).empresa.nome
    assert "(fictício)" in DEMO[cnpj].apelido


@pytest.mark.parametrize("cnpj", sorted(c for c, item in DEMO.items() if item.origem == "real_empresa_grande"))
def test_empresa_real_tem_nome_que_pode_aparecer(cnpj):
    # The sanitizer only keeps the name of large legal natures; a real CNPJ without a name could be a person.
    assert carregar_fixture(cnpj).empresa.nome is not None


def test_cnpj_de_teste_nao_esta_na_demo():
    assert not esta_na_demo("98765435000121")
    assert esta_na_demo("00000000000191")
