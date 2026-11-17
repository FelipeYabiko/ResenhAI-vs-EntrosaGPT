"""Proposals and live events (RF-06)."""

import asyncio
import json
import threading
import time

import httpx
import pytest
import uvicorn
from fastapi.testclient import TestClient

from app import memoria as modulo_memoria
from app.main import app
from app.memoria import memoria
from app.schemas import ConsultaResultado, DadosEvento, Evento

CONSULTA = ConsultaResultado.model_validate(ConsultaResultado.model_config["json_schema_extra"]["examples"][0])
cliente = TestClient(app)


def _evento_de_teste(id_):
    return Evento(
        id=id_,
        tipo="proposta.criada",
        ocorrido_em="2026-11-12T14:03:00Z",
        proposta_id="p_1",
        dados=DadosEvento(faixa="B", limite_credito_simulado=1000.0),
        aviso="Simulação. Não é oferta de crédito.",
    )


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
    assert memoria.eventos.total_ouvintes() == 0  # closing the subscription removes the listener


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


@pytest.fixture
def servidor():
    """The real API on a free local port, like a browser would see it."""
    servidor = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=0, log_level="warning"))
    thread = threading.Thread(target=servidor.run, daemon=True)
    thread.start()
    while not servidor.started:
        time.sleep(0.01)
    porta = servidor.servers[0].sockets[0].getsockname()[1]
    yield f"http://127.0.0.1:{porta}"
    servidor.should_exit = True
    thread.join(5)


def _esperar(condicao, segundos=2.0):
    limite = time.monotonic() + segundos
    while not condicao():
        assert time.monotonic() < limite, "timed out"
        time.sleep(0.01)


def test_rf06_matriz_recebe_a_proposta_em_ate_2_segundos(servidor):
    recebido = {}

    def matriz():
        with httpx.stream("GET", f"{servidor}/v1/eventos", timeout=5) as resposta:
            for linha in resposta.iter_lines():
                if linha.startswith("data:"):
                    recebido["quando"] = time.monotonic()
                    recebido["dados"] = json.loads(linha.removeprefix("data:"))
                    return

    aba_da_matriz = threading.Thread(target=matriz)
    aba_da_matriz.start()
    _esperar(lambda: memoria.eventos.total_ouvintes() == 1)

    enviada_em = time.monotonic()
    proposta = httpx.post(f"{servidor}/v1/propostas", json={"consulta_id": "c_01", "agente": "agente_demo"}).json()
    aba_da_matriz.join(3)

    assert recebido["dados"]["proposta_id"] == proposta["proposta_id"]
    assert recebido["quando"] - enviada_em < 2
    # The tab closed its connection: the API forgets the listener.
    _esperar(lambda: memoria.eventos.total_ouvintes() == 0)


@pytest.mark.parametrize(
    "texto",
    [
        "Falar com fulano@exemplo.com",
        "CPF 123.456.789-09",
        "Ligar (11) 98765-4321",
        "telefone 11987654321",
    ],
)
def test_observacao_com_cara_de_dado_pessoal_e_recusada(texto):
    resposta = _enviar(observacoes=texto)
    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "entrada_invalida"
    assert memoria.propostas == {}


def test_observacao_comum_e_aceita():
    texto = "Fatura uns R$ 15.000,00 por mês e quer receber em D+1. Volta dia 25/11."
    assert _enviar(observacoes=texto).status_code == 201


def test_memoria_guarda_no_maximo_o_limite_e_descarta_as_mais_antigas(monkeypatch):
    monkeypatch.setattr(modulo_memoria, "LIMITE_GUARDADOS", 3)
    ids = [_enviar().json()["proposta_id"] for _ in range(5)]
    assert list(memoria.propostas) == ids[2:]


def test_ouvinte_lento_perde_os_mais_antigos_sem_derrubar_o_envio(monkeypatch):
    monkeypatch.setattr(modulo_memoria, "LIMITE_FILA", 2)

    async def cenario():
        assinatura = memoria.eventos.assinar(depois_de=None)
        primeiro = asyncio.ensure_future(anext(assinatura))
        await asyncio.sleep(0)  # the listener is connected, but does not read yet
        for i in range(1, 6):
            memoria.eventos.publicar(_evento_de_teste(f"e_{i}"))  # never raises, even with a full queue
        recebidos = [(await primeiro).id, (await anext(assinatura)).id]
        await assinatura.aclose()
        return recebidos

    # Room for 2: the 3 oldest were dropped.
    assert asyncio.run(cenario()) == ["e_4", "e_5"]


def test_com_muitos_paineis_conectados_responde_503(monkeypatch):
    monkeypatch.setattr(modulo_memoria, "LIMITE_OUVINTES", 0)
    resposta = cliente.get("/v1/eventos")
    assert resposta.status_code == 503
    assert resposta.json()["erro"]["codigo"] == "muitas_conexoes"


@pytest.mark.parametrize(
    ("cabecalho", "esperado"),
    [("nao-e-um-id", None), ("e_123", None), ("e_0123456789ab", "e_0123456789ab")],
)
def test_last_event_id_fora_do_formato_e_tratado_como_ouvinte_novo(monkeypatch, cabecalho, esperado):
    pedidos = []

    async def assinar_falso(depois_de):
        pedidos.append(depois_de)
        return
        yield  # makes this an (empty) async generator

    monkeypatch.setattr(memoria.eventos, "assinar", assinar_falso)
    with cliente.stream("GET", "/v1/eventos", headers={"Last-Event-ID": cabecalho}) as resposta:
        resposta.read()
    assert pedidos == [esperado]
