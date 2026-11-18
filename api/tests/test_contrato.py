"""Contract tests: docs/ARQUITETURA.md, the schemas and api/openapi.json agree."""

import json
import re
import sys
from pathlib import Path

import pytest
from app import schemas
from app.main import app
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts"))
from exportar_openapi import gerar

# JSON examples in the order they appear in the "Contrato da API (v1)" section.
MODELOS_DOS_EXEMPLOS: list[type[BaseModel]] = [
    schemas.Erro,
    schemas.ConsultaEntrada,  # full input
    schemas.ConsultaEntrada,  # minimal input (landing form)
    schemas.ConsultaResultado,
    schemas.PropostaEntrada,
    schemas.Proposta,
    schemas.PropostaAtualizacao,
    schemas.Saude,
    schemas.Evento,
]


def exemplos_do_documento() -> list[dict]:
    texto = (RAIZ / "docs" / "ARQUITETURA.md").read_text(encoding="utf-8")
    secao = texto[texto.index("## Contrato da API (v1)") : texto.index("## Modelo de dados")]
    return [json.loads(bloco) for bloco in re.findall(r"```json\n(.*?)```", secao, re.DOTALL)]


def test_documento_tem_um_exemplo_por_modelo():
    assert len(exemplos_do_documento()) == len(MODELOS_DOS_EXEMPLOS)


@pytest.mark.parametrize("indice", range(len(MODELOS_DOS_EXEMPLOS)))
def test_exemplo_do_documento_bate_com_o_schema(indice):
    modelo = MODELOS_DOS_EXEMPLOS[indice]
    exemplo = exemplos_do_documento()[indice]
    lido = modelo.model_validate(exemplo)
    assert lido.model_dump(mode="json", exclude_unset=True) == exemplo


@pytest.mark.parametrize("modelo", sorted(set(MODELOS_DOS_EXEMPLOS), key=lambda m: m.__name__))
def test_exemplo_do_schema_esta_no_documento(modelo):
    exemplo = modelo.model_config["json_schema_extra"]["examples"][0]
    assert exemplo in exemplos_do_documento()


def test_openapi_salvo_esta_atualizado():
    salvo = (RAIZ / "api" / "openapi.json").read_text(encoding="utf-8")
    assert salvo == gerar(), "Rode: python scripts/exportar_openapi.py"


@pytest.mark.parametrize(
    "modelo",
    [schemas.ConsultaResultado, schemas.Proposta, schemas.Evento],
)
def test_resposta_com_valor_simulado_exige_aviso(modelo):
    exemplo = dict(modelo.model_config["json_schema_extra"]["examples"][0])
    exemplo.pop("aviso")
    with pytest.raises(ValidationError):
        modelo.model_validate(exemplo)


def test_mix_precisa_somar_100():
    with pytest.raises(ValidationError):
        schemas.Mix(debito=50, credito_a_vista=40, credito_parcelado=0, pix=20)


def test_cnpj_so_aceita_14_digitos():
    with pytest.raises(ValidationError):
        schemas.ConsultaEntrada.model_validate(
            {"cnpj": "00.000.000/0001-91", "perfil_vendas": {"faturamento_mensal": 1000}}
        )


def test_pendente_exige_pendencia():
    with pytest.raises(ValidationError):
        schemas.PropostaAtualizacao(status="pendente")


def test_campo_desconhecido_e_recusado():
    with pytest.raises(ValidationError):
        schemas.PropostaEntrada(consulta_id="c_01", agente="agente_demo", cpf="000")


cliente = TestClient(app)


def test_saude():
    resposta = cliente.get("/v1/saude")
    assert resposta.status_code == 200
    schemas.Saude.model_validate(resposta.json())


def test_entrada_invalida_usa_formato_de_erro():
    resposta = cliente.post("/v1/consultas", json={"cnpj": "123"})
    assert resposta.status_code == 422
    erro = schemas.Erro.model_validate(resposta.json())
    assert erro.erro.codigo == "entrada_invalida"


def test_rota_em_construcao_responde_501_no_formato_de_erro():
    resposta = cliente.post(
        "/v1/consultas", json={"cnpj": "00000000000191", "perfil_vendas": {"faturamento_mensal": 10000}}
    )
    assert resposta.status_code == 501
    assert schemas.Erro.model_validate(resposta.json()).erro.codigo == "nao_implementado"


def test_agente_e_identificador_de_perfil_demo():
    with pytest.raises(ValidationError):
        schemas.PropostaEntrada(consulta_id="c_01", agente="Maria da Silva")
