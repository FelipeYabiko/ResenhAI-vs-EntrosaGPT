"""Public CNPJ source: sanitization and fixtures (RF-03, docs/DADOS.md)."""

import json
from datetime import date
from pathlib import Path

import pytest

from fontes import cnpj_publico
from fontes.cnpj_publico import carregar_fixture, sanitizar

# Same shape as the real open.cnpja.com answer (checked on 18/11/2026), with INVENTED personal data.
PESSOA_FALSA = "FULANO DE TAL FICTICIO"
CPF_FALSO = "***123456**"
EMAIL_FALSO = "contato@exemplo-ficticio.com"
TELEFONE_FALSO = "99999999"
RUA_FALSA = "RUA INVENTADA"


def resposta_da_fonte(**mudancas) -> dict:
    resposta = {
        "updated": "2026-11-17T20:15:30.532Z",
        "taxId": "11222333000181",
        "alias": "NOME FANTASIA",
        "founded": "2010-03-15",
        "head": True,
        "company": {
            "members": [
                {
                    "since": "2010-03-15",
                    "person": {"id": "x", "type": "NATURAL", "name": PESSOA_FALSA, "taxId": CPF_FALSO, "age": "41-50"},
                    "role": {"id": 49, "text": "Sócio-Administrador"},
                }
            ],
            "name": "EMPRESA FICTICIA LTDA",
            "jurisdiction": "SP",
            "equity": 50000,
            "nature": {"id": 2062, "text": "Sociedade Empresária Limitada"},
            "size": {"id": 1, "acronym": "ME", "text": "Microempresa"},
            "simples": {"optant": True, "since": None, "history": [], "events": []},
            "simei": {"optant": False, "since": None, "history": []},
            "id": "x",
        },
        "statusDate": "2010-03-15",
        "status": {"id": 2, "text": "Ativa"},
        "address": {
            "municipality": 1,
            "street": RUA_FALSA,
            "number": "123",
            "district": "CENTRO",
            "city": "São Paulo",
            "state": "SP",
            "details": "SALA 1",
            "zip": "01000000",
            "country": {"id": 76, "name": "Brasil"},
        },
        "phones": [{"type": "LANDLINE", "area": "11", "number": TELEFONE_FALSO}],
        "emails": [{"ownership": "CORPORATE", "address": EMAIL_FALSO, "domain": "exemplo-ficticio.com"}],
        "mainActivity": {"id": 4711302, "text": "Comércio varejista de mercadorias em geral"},
        "sideActivities": [],
        "suframa": [],
    }
    resposta["company"].update(mudancas.pop("company", {}))
    resposta.update(mudancas)
    return resposta


def test_sanitizar_mantem_so_dados_da_empresa():
    dados = sanitizar(resposta_da_fonte())
    assert dados.atualizado_em == date(2026, 11, 17)
    assert dados.empresa.model_dump(mode="json") == {
        "cnpj": "11222333000181",
        "nome": "EMPRESA FICTICIA LTDA",
        "situacao": "ATIVA",
        "cnae_principal": "4711-3/02",
        "porte": "ME",
        "abertura": "2010-03-15",
        "capital_social": 50000.0,
        "municipio_uf": "São Paulo/SP",
    }


def test_nenhum_dado_pessoal_sobra_depois_de_sanitizar():
    texto = json.dumps(sanitizar(resposta_da_fonte()).model_dump(mode="json"), ensure_ascii=False)
    for dado_pessoal in (PESSOA_FALSA, CPF_FALSO, EMAIL_FALSO, TELEFONE_FALSO, RUA_FALSA, "Sócio"):
        assert dado_pessoal not in texto


@pytest.mark.parametrize(
    "mudanca",
    [
        {"company": {"simei": {"optant": True, "since": None, "history": []}}},
        {"company": {"nature": {"id": 2135, "text": "Empresário (Individual)"}}},
        {"company": {"nature": {"id": 2305, "text": "Empresa Individual de Responsabilidade Limitada"}}},
        {"company": {"nature": {"id": 2321, "text": "Sociedade Unipessoal de Advocacia"}}},
    ],
)
def test_mei_e_empresario_individual_ficam_sem_nome(mudanca):
    # The legal name of these companies usually carries the owner's name (docs/DADOS.md).
    assert sanitizar(resposta_da_fonte(**mudanca)).empresa.nome is None


def test_resposta_de_outro_cnpj_ou_incompleta_e_recusada():
    with pytest.raises(ValueError):
        sanitizar({"taxId": "11222333000181"})


def test_fixture_salva_e_carregada_sem_mudar(tmp_path, monkeypatch):
    monkeypatch.setattr(cnpj_publico, "PASTA_FIXTURES", tmp_path)
    dados = sanitizar(resposta_da_fonte())
    cnpj_publico.salvar_fixture(dados)
    assert carregar_fixture("11222333000181") == dados
    assert carregar_fixture("00000000000191") is None


FIXTURES_REAIS = sorted(cnpj_publico.PASTA_FIXTURES.glob("*.json"))


@pytest.mark.parametrize("arquivo", FIXTURES_REAIS, ids=lambda p: p.name)
def test_fixtures_do_repositorio_so_tem_campos_permitidos(arquivo: Path):
    conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
    assert set(conteudo) == {"fonte", "atualizado_em", "empresa"}
    assert set(conteudo["empresa"]) == {
        "cnpj",
        "nome",
        "situacao",
        "cnae_principal",
        "porte",
        "abertura",
        "capital_social",
        "municipio_uf",
    }
    assert arquivo.stem == conteudo["empresa"]["cnpj"]
    assert carregar_fixture(arquivo.stem) is not None


def test_endereco_da_fonte_e_fixo():
    assert cnpj_publico.URL_FONTE == "https://open.cnpja.com/office/"
    with pytest.raises(ValueError):
        cnpj_publico.baixar("../../outra-coisa")
