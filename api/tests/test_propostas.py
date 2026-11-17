"""Proposals and live events (RF-06)."""

import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.memoria import memoria
from app.schemas import ConsultaResultado

CONSULTA = ConsultaResultado.model_validate(ConsultaResultado.model_config["json_schema_extra"]["examples"][0])
cliente = TestClient(app)


@pytest.fixture(autouse=True)
def memoria_limpa():
    memoria.limpar()
    memoria.consultas[CONSULTA.consulta_id] = CONSULTA
    yield
    memoria.limpar()


def _enviar(**extra):
    corpo = {"consulta_id": CONSULTA.consulta_id, "agente": "agente_demo", **extra}
    return cliente.post("/v1/propostas", json=corpo)


def test_cria_proposta_a_partir_da_consulta():
    resposta = _enviar(observacoes="Prefere receber em D+1.")
    assert resposta.status_code == 201
    proposta = resposta.json()
    assert proposta["status"] == "enviada"
    assert proposta["pendencias"] == []
    assert proposta["aviso"] == "Simulação. Não é oferta de crédito."
    assert proposta["resumo"] == {
        "cnpj": "00000000000191",
        "nome": "NOME DA EMPRESA",
        "faixa": "B",
        "limite_credito_simulado": 50000.0,
        "economia_mensal": 169.8,
    }


def test_resumo_sem_economia_quando_a_consulta_nao_teve():
    sem_economia = CONSULTA.model_copy(update={"consulta_id": "c_02", "economia": None})
    memoria.consultas["c_02"] = sem_economia
    resposta = cliente.post("/v1/propostas", json={"consulta_id": "c_02", "agente": "agente_demo"})
    assert resposta.json()["resumo"]["economia_mensal"] is None


def test_consulta_inexistente_devolve_404():
    resposta = cliente.post("/v1/propostas", json={"consulta_id": "c_nao_existe", "agente": "agente_demo"})
    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "nao_encontrado"


def test_lista_e_detalhe():
    criada = _enviar().json()
    lista = cliente.get("/v1/propostas").json()["propostas"]
    assert [p["proposta_id"] for p in lista] == [criada["proposta_id"]]
    assert cliente.get(f"/v1/propostas/{criada['proposta_id']}").json() == criada


def test_lista_filtra_por_status():
    _enviar()
    assert len(cliente.get("/v1/propostas?status=enviada").json()["propostas"]) == 1
    assert cliente.get("/v1/propostas?status=aprovada").json()["propostas"] == []


def test_lista_mostra_a_mais_recente_primeiro():
    primeira = _enviar().json()
    segunda = _enviar().json()
    ids = [p["proposta_id"] for p in cliente.get("/v1/propostas").json()["propostas"]]
    assert ids == [segunda["proposta_id"], primeira["proposta_id"]]


def test_detalhe_inexistente_devolve_404():
    resposta = cliente.get("/v1/propostas/p_nao_existe")
    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "nao_encontrado"


def test_criar_proposta_publica_evento():
    proposta = _enviar().json()
    [evento] = memoria.eventos.historico()
    assert evento.tipo == "proposta.criada"
    assert evento.proposta_id == proposta["proposta_id"]
    assert evento.dados.faixa == "B"
    assert evento.dados.limite_credito_simulado == 50000.0
    assert evento.aviso == "Simulação. Não é oferta de crédito."


def test_quem_esta_ouvindo_recebe_o_evento_na_hora():
    async def cenario():
        assinatura = memoria.eventos.assinar(depois_de=None)
        proximo = asyncio.ensure_future(anext(assinatura))
        await asyncio.sleep(0)  # the listener is now waiting
        memoria.eventos.publicar(_evento_de_teste("e_1"))
        recebido = await asyncio.wait_for(proximo, timeout=1)
        await assinatura.aclose()
        return recebido

    assert asyncio.run(cenario()).id == "e_1"


def test_quem_reconecta_recebe_so_o_que_perdeu():
    for i in (1, 2, 3):
        memoria.eventos.publicar(_evento_de_teste(f"e_{i}"))

    async def primeiros(depois_de, quantidade):
        assinatura = memoria.eventos.assinar(depois_de=depois_de)
        recebidos = [(await anext(assinatura)).id for _ in range(quantidade)]
        await assinatura.aclose()
        return recebidos

    assert asyncio.run(primeiros("e_1", 2)) == ["e_2", "e_3"]
    assert asyncio.run(primeiros("id_desconhecido", 3)) == ["e_1", "e_2", "e_3"]


def test_fluxo_sse_entrega_o_evento_no_formato_do_contrato():
    _enviar()
    proposta = _enviar().json()
    [primeiro, _] = memoria.eventos.historico()
    # The browser sends Last-Event-ID when it reconnects; the API resends what came after it.
    with cliente.stream("GET", "/v1/eventos", headers={"Last-Event-ID": primeiro.id}) as resposta:
        assert resposta.headers["content-type"].startswith("text/event-stream")
        linhas = []
        for linha in resposta.iter_lines():
            if linha == "" and linhas:  # a blank line ends one SSE message
                break
            if linha:
                linhas.append(linha)
    assert "event: proposta.criada" in linhas
    assert f"id: {memoria.eventos.historico()[1].id}" in linhas
    [dados_json] = [linha.removeprefix("data:").strip() for linha in linhas if linha.startswith("data:")]
    dados = json.loads(dados_json)
    assert dados["proposta_id"] == proposta["proposta_id"]
    assert dados["aviso"] == "Simulação. Não é oferta de crédito."


def _evento_de_teste(id_):
    from app.schemas import DadosEvento, Evento

    return Evento(
        id=id_,
        tipo="proposta.criada",
        ocorrido_em="2026-11-12T14:03:00Z",
        proposta_id="p_1",
        dados=DadosEvento(faixa="B", limite_credito_simulado=1000.0),
        aviso="Simulação. Não é oferta de crédito.",
    )
