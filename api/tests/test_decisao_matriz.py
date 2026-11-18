"""Back office decisions on a proposal: pendency, approval, refusal (RF-07, RF-08)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.memoria import memoria
from app.schemas import ConsultaResultado

CONSULTA = ConsultaResultado.model_validate(ConsultaResultado.model_config["json_schema_extra"]["examples"][0])
cliente = TestClient(app)
PENDENCIA = {"descricao": "Enviar comprovante de faturamento dos últimos 3 meses."}


@pytest.fixture(autouse=True)
def memoria_limpa():
    memoria.limpar()
    memoria.consultas[CONSULTA.consulta_id] = CONSULTA
    yield
    memoria.limpar()


def _nova_proposta() -> dict:
    return cliente.post("/v1/propostas", json={"consulta_id": "c_01", "agente": "agente_demo"}).json()


def _mudar(proposta_id: str, status: str, pendencias: list | None = None):
    corpo = {"status": status} | ({"pendencias": pendencias} if pendencias is not None else {})
    return cliente.patch(f"/v1/propostas/{proposta_id}", json=corpo)


@pytest.mark.parametrize("status", ["aprovada", "recusada"])
def test_matriz_aprova_ou_recusa_proposta_enviada(status):
    proposta = _nova_proposta()
    resposta = _mudar(proposta["proposta_id"], status)
    assert resposta.status_code == 200
    atualizada = resposta.json()
    assert atualizada["status"] == status
    assert atualizada["atualizada_em"] >= proposta["atualizada_em"]
    assert atualizada["aviso"] == "Simulação. Não é oferta de crédito."
    assert cliente.get(f"/v1/propostas/{proposta['proposta_id']}").json() == atualizada


def test_pedir_pendencia_guarda_o_texto_com_data():
    proposta = _nova_proposta()
    atualizada = _mudar(proposta["proposta_id"], "pendente", [PENDENCIA]).json()
    assert atualizada["status"] == "pendente"
    [pendencia] = atualizada["pendencias"]
    assert pendencia["descricao"] == PENDENCIA["descricao"]
    assert pendencia["criada_em"]


def test_pendencias_se_acumulam_e_a_proposta_ainda_pode_ser_aprovada():
    proposta = _nova_proposta()
    _mudar(proposta["proposta_id"], "pendente", [PENDENCIA])
    segunda = {"descricao": "Confirmar o prazo de recebimento desejado."}
    atualizada = _mudar(proposta["proposta_id"], "pendente", [segunda]).json()
    assert [p["descricao"] for p in atualizada["pendencias"]] == [PENDENCIA["descricao"], segunda["descricao"]]
    assert _mudar(proposta["proposta_id"], "aprovada").json()["status"] == "aprovada"


@pytest.mark.parametrize("final", ["aprovada", "recusada"])
@pytest.mark.parametrize("depois", ["pendente", "aprovada", "recusada"])
def test_aprovada_e_recusada_sao_finais(final, depois):
    proposta = _nova_proposta()
    _mudar(proposta["proposta_id"], final)
    resposta = _mudar(proposta["proposta_id"], depois, [PENDENCIA] if depois == "pendente" else None)
    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "transicao_invalida"
    assert cliente.get(f"/v1/propostas/{proposta['proposta_id']}").json()["status"] == final


def test_pendente_sem_pendencia_e_recusado():
    proposta = _nova_proposta()
    resposta = _mudar(proposta["proposta_id"], "pendente", [])
    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "entrada_invalida"


@pytest.mark.parametrize("status", ["aprovada", "recusada"])
def test_pendencia_junto_com_aprovacao_ou_recusa_e_recusada(status):
    # Silently dropping the text would hide a mistake from the analyst.
    proposta = _nova_proposta()
    assert _mudar(proposta["proposta_id"], status, [PENDENCIA]).status_code == 422


def test_pendencia_com_cara_de_dado_pessoal_e_recusada():
    proposta = _nova_proposta()
    resposta = _mudar(proposta["proposta_id"], "pendente", [{"descricao": "Ligar para (11) 98765-4321"}])
    assert resposta.status_code == 422


def test_status_enviada_nao_pode_ser_pedido():
    proposta = _nova_proposta()
    assert _mudar(proposta["proposta_id"], "enviada").status_code == 422


def test_proposta_inexistente_devolve_404():
    resposta = _mudar("p_nao_existe", "aprovada")
    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "nao_encontrado"


@pytest.mark.parametrize(("status", "pendencias"), [("pendente", [PENDENCIA]), ("aprovada", None), ("recusada", None)])
def test_cada_decisao_publica_um_evento(status, pendencias):
    proposta = _nova_proposta()
    _mudar(proposta["proposta_id"], status, pendencias)
    criada, decisao = memoria.eventos.historico()
    assert criada.tipo == "proposta.criada"
    assert decisao.tipo == f"proposta.{status}"
    assert decisao.proposta_id == proposta["proposta_id"]
    assert decisao.dados.faixa == "B"
    assert decisao.dados.limite_credito_simulado == proposta["resumo"]["limite_credito_simulado"]
    assert decisao.aviso == "Simulação. Não é oferta de crédito."


def test_transicao_recusada_nao_publica_evento():
    proposta = _nova_proposta()
    _mudar(proposta["proposta_id"], "recusada")
    _mudar(proposta["proposta_id"], "aprovada")
    assert [e.tipo for e in memoria.eventos.historico()] == ["proposta.criada", "proposta.recusada"]


def test_lista_filtra_pelo_status_novo():
    proposta = _nova_proposta()
    _mudar(proposta["proposta_id"], "aprovada")
    assert cliente.get("/v1/propostas?status=enviada").json()["propostas"] == []
    [aprovada] = cliente.get("/v1/propostas?status=aprovada").json()["propostas"]
    assert aprovada["proposta_id"] == proposta["proposta_id"]


def test_pendente_pode_terminar_recusada_e_cada_pendencia_gera_evento():
    proposta = _nova_proposta()
    _mudar(proposta["proposta_id"], "pendente", [PENDENCIA])
    _mudar(proposta["proposta_id"], "pendente", [{"descricao": "Confirmar o prazo de recebimento."}])
    assert _mudar(proposta["proposta_id"], "recusada").json()["status"] == "recusada"
    tipos = [e.tipo for e in memoria.eventos.historico()]
    assert tipos == ["proposta.criada", "proposta.pendente", "proposta.pendente", "proposta.recusada"]
