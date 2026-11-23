"""Full query POST /v1/consultas (RF-01, RF-03, RF-04, RF-05, RF-11)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app
from app.memoria import memoria
from scoring.premissas import carregar_premissas

PREMISSAS_TESTE = carregar_premissas(Path(__file__).with_name("premissas_teste.toml"))
MERCADINHO = "98765432000198"  # fictitious, in the demo list
BB = "00000000000191"  # large company, in the demo list
cliente = TestClient(app)

MIX = {"debito": 40, "credito_a_vista": 40, "credito_parcelado": 0, "pix": 20}
TAXAS_ATUAIS = {"debito": 1.99, "credito_a_vista": 4.98, "credito_parcelado": None, "pix": 0.0}


@pytest.fixture(autouse=True)
def ambiente(monkeypatch):
    memoria.limpar()
    monkeypatch.setattr(main, "carregar_premissas", lambda: PREMISSAS_TESTE)
    monkeypatch.delenv("MODO_DEMO", raising=False)
    yield
    memoria.limpar()


def consultar(cnpj=MERCADINHO, faturamento=15000, mix=None, taxas=None, **situacao):
    perfil = {"faturamento_mensal": faturamento} | ({"mix": mix} if mix else {})
    corpo = {"cnpj": cnpj, "perfil_vendas": perfil}
    if taxas:
        corpo["situacao_atual"] = {"taxas": taxas} | situacao
    return cliente.post("/v1/consultas", json=corpo)


def test_consulta_completa_com_o_caso_de_referencia():
    resposta = consultar(mix=MIX, taxas=TAXAS_ATUAIS)
    assert resposta.status_code == 200
    r = resposta.json()
    assert r["empresa"]["nome"] == "MERCADINHO BOA VISTA (FICTÍCIO)"
    assert r["pontuacao"]["faixa"] in "ABCDE"
    assert r["recomendacao"]["maquina"]["modelo"] == "Plus"
    assert r["economia"] == {
        "custo_mensal_atual": 418.2,
        "custo_mensal_oferta": 248.4,
        "economia_mensal": 169.8,
        "economia_anual": 2037.6,
        "meses_para_compensar_saida": 0,
        "estimado": True,
    }
    assert r["aviso"] == "Simulação. Não é oferta de crédito."
    assert r["consulta_id"] in memoria.consultas  # a proposal can be created from it


def test_limite_e_antecipacao_vem_da_faixa():
    r = consultar(faturamento=10000).json()
    faixa = r["pontuacao"]["faixa"]
    multiplo = PREMISSAS_TESTE.recomendacao.multiplo_limite[faixa]
    premio = PREMISSAS_TESTE.recomendacao.antecipacao_premio_mensal[faixa]
    assert r["recomendacao"]["limite_credito_simulado"] == 10000 * multiplo
    assert r["recomendacao"]["taxas_antecipacao_simuladas"]["mensal_percentual"] == 1.5 + premio


def test_formulario_da_landing_so_com_cnpj_e_faturamento_nao_inventa_economia():
    r = consultar().json()
    assert r["economia"] is None
    assert r["pontuacao"]["fatores"]


def test_taxa_atual_faltando_para_forma_com_vendas_deixa_economia_nula():
    r = consultar(mix=MIX, taxas=TAXAS_ATUAIS | {"pix": None}).json()
    assert r["economia"] is None


def test_custo_de_saida_entra_na_conta():
    r = consultar(mix=MIX, taxas=TAXAS_ATUAIS, custo_saida=500.0).json()
    assert r["economia"]["meses_para_compensar_saida"] == 3


def test_ficticio_usa_so_o_fixture_e_nunca_chama_a_fonte(monkeypatch):
    def proibido(*_):
        raise AssertionError("fictitious CNPJ must never reach the public source")

    monkeypatch.setattr(main, "baixar", proibido)
    monkeypatch.setenv("MODO_DEMO", "false")
    r = consultar().json()
    assert r["fontes"][0]["nome"] == "dados_ficticios"


def test_empresa_grande_da_demo_usa_os_dados_guardados_com_data():
    r = consultar(cnpj=BB).json()
    [fonte] = [f for f in r["fontes"] if f["nome"] == "cnpj_publico"]
    assert fonte["em_cache"] is True
    assert fonte["atualizado_em"]


def test_fora_da_lista_da_demo_e_recusado_antes_de_qualquer_fonte(monkeypatch):
    monkeypatch.setattr(main, "baixar", lambda *_: (_ for _ in ()).throw(AssertionError("no source call")))
    resposta = consultar(cnpj="98765435000121")
    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "cnpj_fora_da_demo"


def test_sem_modo_demo_cnpj_fora_da_lista_vai_a_fonte_e_falha_com_502(monkeypatch):
    import urllib.error

    def fonte_fora(*_):
        raise urllib.error.URLError("timeout")

    monkeypatch.setenv("MODO_DEMO", "false")
    monkeypatch.setattr(main, "baixar", fonte_fora)
    resposta = consultar(cnpj="98765435000121")
    assert resposta.status_code == 502
    assert resposta.json()["erro"]["codigo"] == "fonte_indisponivel"


def test_premissas_nao_aprovadas_respondem_em_construcao(monkeypatch):
    from scoring.premissas import PremissasPendentes

    def pendentes():
        raise PremissasPendentes("x")

    monkeypatch.setattr(main, "carregar_premissas", pendentes)
    resposta = consultar()
    assert resposta.status_code == 501
    assert "premissas" in resposta.json()["erro"]["mensagem"]


def test_cnpj_invalido_continua_recusado_primeiro():
    assert consultar(cnpj="98765432000199").json()["erro"]["codigo"] == "cnpj_invalido"


def test_proposta_pode_ser_criada_da_consulta():
    consulta_id = consultar().json()["consulta_id"]
    proposta = cliente.post("/v1/propostas", json={"consulta_id": consulta_id, "agente": "agente_demo"})
    assert proposta.status_code == 201
    assert proposta.json()["resumo"]["nome"] == "MERCADINHO BOA VISTA (FICTÍCIO)"


def test_premissas_com_erro_respondem_501_com_mensagem_clara(monkeypatch):
    from scoring.premissas import PremissasInvalidas

    def quebradas():
        raise PremissasInvalidas("premissas.toml incompleto: faixas")

    monkeypatch.setattr(main, "carregar_premissas", quebradas)
    resposta = consultar()
    assert resposta.status_code == 501
    assert "precisam de correção" in resposta.json()["erro"]["mensagem"]


def test_conexao_que_cai_no_meio_vira_502_e_nao_500(monkeypatch):
    def cai(*_):
        raise ConnectionResetError

    monkeypatch.setenv("MODO_DEMO", "false")
    monkeypatch.setattr(main, "baixar", cai)
    assert consultar(cnpj="98765435000121").status_code == 502
