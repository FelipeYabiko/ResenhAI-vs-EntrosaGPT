"""Simulated contract PDF, generated only for approved proposals (RF-09)."""

import io

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app
from app.memoria import memoria
from app.schemas import ConsultaResultado

CONSULTA = ConsultaResultado.model_validate(ConsultaResultado.model_config["json_schema_extra"]["examples"][0])
cliente = TestClient(app)


@pytest.fixture(autouse=True)
def memoria_limpa():
    memoria.limpar()
    memoria.consultas[CONSULTA.consulta_id] = CONSULTA
    sem_nome = CONSULTA.model_copy(
        update={"consulta_id": "c_mei", "empresa": CONSULTA.empresa.model_copy(update={"nome": None})}
    )
    memoria.consultas["c_mei"] = sem_nome
    yield
    memoria.limpar()


def _proposta(consulta_id: str = "c_01", aprovar: bool = True) -> str:
    proposta_id = cliente.post("/v1/propostas", json={"consulta_id": consulta_id, "agente": "agente_demo"}).json()[
        "proposta_id"
    ]
    if aprovar:
        cliente.patch(f"/v1/propostas/{proposta_id}", json={"status": "aprovada"})
    return proposta_id


def _texto(pdf: bytes) -> str:
    leitor = PdfReader(io.BytesIO(pdf))
    return "\n".join(pagina.extract_text() for pagina in leitor.pages)


def test_proposta_aprovada_gera_pdf_para_baixar():
    proposta_id = _proposta()
    resposta = cliente.get(f"/v1/propostas/{proposta_id}/contrato")
    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "application/pdf"
    assert resposta.headers["content-disposition"] == f'attachment; filename="contrato-simulado-{proposta_id}.pdf"'
    assert resposta.content.startswith(b"%PDF")


def test_pdf_traz_os_dados_da_proposta_e_o_aviso():
    proposta_id = _proposta()
    texto = _texto(cliente.get(f"/v1/propostas/{proposta_id}/contrato").content)
    for trecho in (
        "SIMULAÇÃO",
        "Simulação. Não é oferta de crédito.",
        proposta_id,
        "00.000.000/0001-91",
        "NOME DA EMPRESA",
        "Faixa de risco: B",
        "R$ 50.000,00",
        "R$ 169,80",
        "agente_demo",
    ):
        assert trecho in texto, trecho


def test_pdf_tem_marca_dagua_em_todas_as_paginas_e_metadados():
    proposta_id = _proposta()
    leitor = PdfReader(io.BytesIO(cliente.get(f"/v1/propostas/{proposta_id}/contrato").content))
    assert all("SIMULAÇÃO" in pagina.extract_text() for pagina in leitor.pages)
    assert leitor.metadata.title == f"Contrato simulado {proposta_id}"


def test_empresa_sem_nome_nao_inventa_nome():
    texto = _texto(cliente.get(f"/v1/propostas/{_proposta('c_mei')}/contrato").content)
    assert "NOME DA EMPRESA" not in texto
    assert "não exibido" in texto


def test_proposta_sem_economia_nao_mostra_economia():
    memoria.consultas["c_sem"] = CONSULTA.model_copy(update={"consulta_id": "c_sem", "economia": None})
    texto = _texto(cliente.get(f"/v1/propostas/{_proposta('c_sem')}/contrato").content)
    assert "R$ 169,80" not in texto
    assert "Economia" not in texto


@pytest.mark.parametrize("status", [None, "pendente", "recusada"])
def test_sem_aprovacao_nao_ha_contrato(status):
    proposta_id = _proposta(aprovar=False)
    if status:
        corpo = {"status": status}
        if status == "pendente":
            corpo["pendencias"] = [{"descricao": "Enviar comprovante."}]
        cliente.patch(f"/v1/propostas/{proposta_id}", json=corpo)
    resposta = cliente.get(f"/v1/propostas/{proposta_id}/contrato")
    assert resposta.status_code == 409
    assert resposta.json()["erro"]["codigo"] == "transicao_invalida"


def test_proposta_inexistente_devolve_404():
    resposta = cliente.get("/v1/propostas/p_nao_existe/contrato")
    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "nao_encontrado"


@pytest.mark.parametrize(
    ("digitado", "no_pdf"),
    [
        ("Enviar comprovante — urgente", "Enviar comprovante - urgente"),
        ("Anexar nota “fiscal” e ‘recibo’", "Anexar nota \"fiscal\" e 'recibo'"),
        ("Conferir os dados… depois", "Conferir os dados... depois"),
        ("Verificar ✅ dados", "Verificar ? dados"),
    ],
)
def test_pendencia_com_caracteres_do_celular_nao_quebra_o_pdf(digitado, no_pdf):
    # Phones and word processors insert dashes, curly quotes and emoji on their own.
    proposta_id = _proposta(aprovar=False)
    cliente.patch(f"/v1/propostas/{proposta_id}", json={"status": "pendente", "pendencias": [{"descricao": digitado}]})
    cliente.patch(f"/v1/propostas/{proposta_id}", json={"status": "aprovada"})
    resposta = cliente.get(f"/v1/propostas/{proposta_id}/contrato")
    assert resposta.status_code == 200
    assert no_pdf in _texto(resposta.content)
