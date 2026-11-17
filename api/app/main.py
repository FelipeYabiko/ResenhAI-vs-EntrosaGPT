"""CredFácil API v1.

This module declares the contract routes. Routes that are not built yet
answer 501 with the standard error body; each one points to its issue.
"""

import os
from collections.abc import AsyncIterable
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, Response
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.cnpj import cnpj_valido
from app.memoria import memoria
from app.schemas import (
    AVISO_SIMULACAO,
    ConsultaEntrada,
    ConsultaResultado,
    DadosEvento,
    Erro,
    Evento,
    ListaPropostas,
    Proposta,
    PropostaAtualizacao,
    PropostaEntrada,
    ResumoProposta,
    Saude,
    StatusProposta,
)

app = FastAPI(
    title="CredFácil API",
    version="1.0.0",
    description="Simulação. Não é oferta de crédito. Todo limite, taxa e aprovação é simulado.",
)

# The web app runs on another origin (Next.js). Only the origins listed here may call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGENS", "http://localhost:3000").split(",") if o.strip()],
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "Last-Event-ID"],
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


def _nao_implementado() -> ErroApi:
    return ErroApi(501, "nao_implementado", "Rota prevista no contrato v1, ainda em construção.")


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
    # RF-01: reject a wrong CNPJ before any other step, so no external source is called.
    if not cnpj_valido(entrada.cnpj):
        raise ErroApi(422, "cnpj_invalido", "CNPJ inválido. Confira os 14 dígitos.")
    return _depois_da_validacao(entrada)


def _depois_da_validacao(entrada: ConsultaEntrada) -> ConsultaResultado:
    """Next step of the query (sources, scoring, simulation). Tests swap it to prove validation runs first."""
    raise _nao_implementado()  # built in issue #16


def _agora() -> datetime:
    return datetime.now(UTC)


def _proposta_ou_404(proposta_id: str) -> Proposta:
    proposta = memoria.propostas.get(proposta_id)
    if proposta is None:
        raise ErroApi(404, "nao_encontrado", "Proposta não encontrada.")
    return proposta


@app.post(
    "/v1/propostas",
    response_model=Proposta,
    status_code=201,
    responses=_erros(404, 422),
    tags=["propostas"],
)
async def criar_proposta(entrada: PropostaEntrada) -> Proposta:
    # async: publishing to listeners must run on the event loop that serves /v1/eventos.
    consulta = memoria.consultas.get(entrada.consulta_id)
    if consulta is None:
        raise ErroApi(404, "nao_encontrado", "Consulta não encontrada. Faça a consulta antes de enviar a proposta.")
    agora = _agora()
    proposta = Proposta(
        proposta_id=f"p_{uuid4().hex[:12]}",
        consulta_id=consulta.consulta_id,
        agente=entrada.agente,
        status="enviada",
        observacoes=entrada.observacoes,
        pendencias=[],
        resumo=ResumoProposta(
            cnpj=consulta.empresa.cnpj,
            nome=consulta.empresa.nome,
            faixa=consulta.pontuacao.faixa,
            limite_credito_simulado=consulta.recomendacao.limite_credito_simulado,
            economia_mensal=consulta.economia.economia_mensal if consulta.economia else None,
        ),
        criada_em=agora,
        atualizada_em=agora,
        aviso=AVISO_SIMULACAO,
    )
    memoria.propostas[proposta.proposta_id] = proposta
    memoria.eventos.publicar(
        Evento(
            id=f"e_{uuid4().hex[:12]}",
            tipo="proposta.criada",
            ocorrido_em=agora,
            proposta_id=proposta.proposta_id,
            dados=DadosEvento(
                faixa=proposta.resumo.faixa, limite_credito_simulado=proposta.resumo.limite_credito_simulado
            ),
            aviso=AVISO_SIMULACAO,
        )
    )
    return proposta


@app.get("/v1/propostas", response_model=ListaPropostas, responses=_erros(422), tags=["propostas"])
def listar_propostas(status: StatusProposta | None = None) -> ListaPropostas:
    propostas = [p for p in memoria.propostas.values() if status is None or p.status == status]
    return ListaPropostas(propostas=sorted(propostas, key=lambda p: p.criada_em, reverse=True))


@app.get(
    "/v1/propostas/{proposta_id}",
    response_model=Proposta,
    responses=_erros(404, 422),
    tags=["propostas"],
)
def obter_proposta(proposta_id: str) -> Proposta:
    return _proposta_ou_404(proposta_id)


@app.patch(
    "/v1/propostas/{proposta_id}",
    response_model=Proposta,
    responses=_erros(404, 409, 422, 501),
    tags=["propostas"],
)
def atualizar_proposta(proposta_id: str, entrada: PropostaAtualizacao) -> Proposta:
    raise _nao_implementado()  # built in issue #24


@app.get(
    "/v1/propostas/{proposta_id}/contrato",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}, **_erros(404, 409, 422, 501)},
    tags=["propostas"],
)
def contrato_simulado(proposta_id: str) -> Response:
    raise _nao_implementado()  # built in issue #24


@app.get(
    "/v1/eventos",
    response_class=EventSourceResponse,
    responses={
        200: {
            "description": "Server-Sent Events. Each message: `id`, `event: <tipo>` and the Evento JSON in `data:`.",
            "content": {"text/event-stream": {"schema": {"$ref": "#/components/schemas/Evento"}}},
        }
    },
    tags=["eventos"],
)
async def eventos(last_event_id: str | None = Header(default=None)) -> AsyncIterable[ServerSentEvent]:
    """Live proposal events for the back-office panel. New listeners get only new events;
    a browser that reconnects sends Last-Event-ID and gets what it missed."""
    async for evento in memoria.eventos.assinar(depois_de=last_event_id):
        yield ServerSentEvent(id=evento.id, event=evento.tipo, data=evento.model_dump(mode="json"))


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
