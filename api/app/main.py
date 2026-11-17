"""CredFácil API v1.

This module declares the contract routes. Routes that are not built yet
answer 501 with the standard error body; each one points to its issue.
"""

import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, Response

from app.schemas import (
    ConsultaEntrada,
    ConsultaResultado,
    Erro,
    Evento,
    ListaPropostas,
    Proposta,
    PropostaAtualizacao,
    PropostaEntrada,
    Saude,
    StatusProposta,
)

app = FastAPI(
    title="CredFácil API",
    version="1.0.0",
    description="Simulação. Não é oferta de crédito. Todo limite, taxa e aprovação é simulado.",
)


class ErroApi(Exception):
    def __init__(self, status: int, codigo: str, mensagem: str):
        self.status, self.codigo, self.mensagem = status, codigo, mensagem


def _erro(status: int, codigo: str, mensagem: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"erro": {"codigo": codigo, "mensagem": mensagem}})


@app.exception_handler(ErroApi)
async def _tratar_erro_api(_: Request, exc: ErroApi) -> JSONResponse:
    return _erro(exc.status, exc.codigo, exc.mensagem)


@app.exception_handler(RequestValidationError)
async def _tratar_validacao(_: Request, exc: RequestValidationError) -> JSONResponse:
    campos = ", ".join(".".join(str(p) for p in e["loc"][1:]) or "corpo" for e in exc.errors())
    return _erro(422, "entrada_invalida", f"Confira estes campos: {campos}.")


def _nao_implementado(issue: int) -> ErroApi:
    return ErroApi(501, "nao_implementado", f"Rota prevista no contrato v1, em construção (issue #{issue}).")


def _erros(*status: int) -> dict:
    return {s: {"model": Erro} for s in status}


@app.get("/v1/saude", response_model=Saude, tags=["saude"])
def saude() -> Saude:
    return Saude(status="ok", modo_demo=os.getenv("MODO_DEMO", "true").lower() == "true")


@app.post(
    "/v1/consultas",
    response_model=ConsultaResultado,
    responses=_erros(422, 429, 501, 502),
    tags=["consultas"],
)
def criar_consulta(entrada: ConsultaEntrada) -> ConsultaResultado:
    raise _nao_implementado(16)


@app.post(
    "/v1/propostas",
    response_model=Proposta,
    status_code=201,
    responses=_erros(404, 422, 501),
    tags=["propostas"],
)
def criar_proposta(entrada: PropostaEntrada) -> Proposta:
    raise _nao_implementado(23)


@app.get("/v1/propostas", response_model=ListaPropostas, responses=_erros(422, 501), tags=["propostas"])
def listar_propostas(status: StatusProposta | None = None) -> ListaPropostas:
    raise _nao_implementado(23)


@app.get(
    "/v1/propostas/{proposta_id}",
    response_model=Proposta,
    responses=_erros(404, 422, 501),
    tags=["propostas"],
)
def obter_proposta(proposta_id: str) -> Proposta:
    raise _nao_implementado(23)


@app.patch(
    "/v1/propostas/{proposta_id}",
    response_model=Proposta,
    responses=_erros(404, 409, 422, 501),
    tags=["propostas"],
)
def atualizar_proposta(proposta_id: str, entrada: PropostaAtualizacao) -> Proposta:
    raise _nao_implementado(24)


@app.get(
    "/v1/propostas/{proposta_id}/contrato",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}, **_erros(404, 409, 422, 501)},
    tags=["propostas"],
)
def contrato_simulado(proposta_id: str) -> Response:
    raise _nao_implementado(24)


@app.get(
    "/v1/eventos",
    response_class=Response,
    responses={
        200: {
            "description": "Server-Sent Events. Each message: `event: <tipo>` and the Evento JSON in `data:`.",
            "content": {"text/event-stream": {"schema": {"$ref": "#/components/schemas/Evento"}}},
        },
        **_erros(501),
    },
    tags=["eventos"],
)
def eventos() -> Response:
    raise _nao_implementado(23)


def _openapi() -> dict:
    """Add Evento (sent over SSE, not as a JSON body) to the OpenAPI components."""
    if app.openapi_schema is None:
        esquema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
        evento = Evento.model_json_schema(ref_template="#/components/schemas/{model}")
        componentes = esquema["components"]["schemas"]
        componentes.update(evento.pop("$defs", {}))
        componentes["Evento"] = evento
        app.openapi_schema = esquema
    return app.openapi_schema


app.openapi = _openapi
