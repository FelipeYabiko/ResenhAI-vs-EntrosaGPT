"""CredFácil API v1.

This module declares the contract routes. Routes that are not built yet
answer 501 with the standard error body; each one points to its issue.
"""

import os
import re
import time
import urllib.error
from collections.abc import AsyncIterable
from datetime import UTC, date, datetime
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, Response
from fastapi.sse import EventSourceResponse, ServerSentEvent

from app.cnpj import cnpj_valido
from app.consulta import montar_resultado
from app.contrato_pdf import gerar_contrato_pdf
from app.memoria import memoria
from app.schemas import (
    AVISO_SIMULACAO,
    ConsultaEntrada,
    ConsultaResultado,
    DadosEvento,
    Empresa,
    Erro,
    Evento,
    Fonte,
    ListaPropostas,
    Pendencia,
    Proposta,
    PropostaAtualizacao,
    PropostaEntrada,
    ResumoProposta,
    Saude,
    StatusProposta,
)
from fontes.cnpj_publico import baixar, carregar_fixture, sanitizar
from fontes.demo import CnpjDemo, cnpjs_da_demo
from scoring.premissas import PremissasPendentes, carregar_premissas

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
    return Saude(status="ok", modo_demo=_modo_demo())


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


def _modo_demo() -> bool:
    return os.getenv("MODO_DEMO", "true").lower() == "true"


def _dados_da_empresa(cnpj: str, item_demo: CnpjDemo | None) -> tuple[Empresa, Fonte]:
    """Company data: fixture for demo CNPJs (fictitious ones NEVER go to the source), live source otherwise."""
    salvo = carregar_fixture(cnpj) if item_demo else None
    if item_demo and item_demo.origem == "ficticio":
        if salvo is None:
            raise ErroApi(502, "fonte_indisponivel", "Dados da empresa fictícia não encontrados.")
        fonte = Fonte(nome="dados_ficticios", status="ok", atualizado_em=salvo.atualizado_em, em_cache=False)
        return salvo.empresa, fonte
    if salvo is not None:
        return salvo.empresa, Fonte(nome="cnpj_publico", status="ok", atualizado_em=salvo.atualizado_em, em_cache=True)
    try:
        dados = sanitizar(baixar(cnpj), cnpj)
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise ErroApi(502, "fonte_indisponivel", "Não foi possível consultar a fonte pública de CNPJ agora.") from None
    return dados.empresa, Fonte(nome="cnpj_publico", status="ok", atualizado_em=dados.atualizado_em, em_cache=False)


def _depois_da_validacao(entrada: ConsultaEntrada) -> ConsultaResultado:
    """Rest of the query (demo list, premises, company data, result). Tests swap it to prove validation runs first."""
    inicio = time.perf_counter()
    item_demo = cnpjs_da_demo().get(entrada.cnpj)
    if _modo_demo() and item_demo is None:
        raise ErroApi(
            422, "cnpj_fora_da_demo", "Na demonstração, só os CNPJs da lista de exemplo podem ser consultados."
        )
    try:
        premissas = carregar_premissas()
    except PremissasPendentes:
        raise ErroApi(
            501,
            "nao_implementado",
            "A análise completa aguarda a aprovação das premissas do time (pontuação e catálogo).",
        ) from None
    empresa, fonte = _dados_da_empresa(entrada.cnpj, item_demo)
    tempo_ms = round((time.perf_counter() - inicio) * 1000)
    resultado = montar_resultado(entrada, empresa, [fonte], premissas, date.today(), tempo_ms)
    memoria.consultas[resultado.consulta_id] = resultado  # so a proposal can be created from it (#23)
    return resultado


ID_EVENTO = re.compile(r"e_[0-9a-f]{12}")


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
    # Proposal routes are async (with no await) on purpose: they run on the event loop one at a time,
    # so the in-memory dict is never read while another request changes it, and listeners are woken
    # on the same loop that serves /v1/eventos.
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
    _publicar(proposta, "proposta.criada", agora)
    return proposta


def _publicar(proposta: Proposta, tipo: str, quando: datetime) -> None:
    memoria.eventos.publicar(
        Evento(
            id=f"e_{uuid4().hex[:12]}",
            tipo=tipo,
            ocorrido_em=quando,
            proposta_id=proposta.proposta_id,
            dados=DadosEvento(
                faixa=proposta.resumo.faixa, limite_credito_simulado=proposta.resumo.limite_credito_simulado
            ),
            aviso=AVISO_SIMULACAO,
        )
    )


@app.get("/v1/propostas", response_model=ListaPropostas, responses=_erros(422), tags=["propostas"])
async def listar_propostas(status: StatusProposta | None = None) -> ListaPropostas:
    propostas = [p for p in memoria.propostas.values() if status is None or p.status == status]
    return ListaPropostas(propostas=sorted(propostas, key=lambda p: p.criada_em, reverse=True))


@app.get(
    "/v1/propostas/{proposta_id}",
    response_model=Proposta,
    responses=_erros(404, 422),
    tags=["propostas"],
)
async def obter_proposta(proposta_id: str) -> Proposta:
    return _proposta_ou_404(proposta_id)


@app.patch(
    "/v1/propostas/{proposta_id}",
    response_model=Proposta,
    responses=_erros(404, 409, 422),
    tags=["propostas"],
)
async def atualizar_proposta(proposta_id: str, entrada: PropostaAtualizacao) -> Proposta:
    # Back office decision (RF-07, RF-08); aprovada and recusada are final.
    # Keep no await between reading the status and saving: that is what makes two decisions safe.
    proposta = _proposta_ou_404(proposta_id)
    if proposta.status not in ("enviada", "pendente"):
        raise ErroApi(409, "transicao_invalida", f"A proposta já foi {proposta.status} e não pode mudar.")
    agora = _agora()
    novas = [Pendencia(descricao=p.descricao, criada_em=agora) for p in entrada.pendencias]
    proposta = proposta.model_copy(
        update={"status": entrada.status, "pendencias": [*proposta.pendencias, *novas], "atualizada_em": agora}
    )
    memoria.propostas[proposta_id] = proposta
    _publicar(proposta, f"proposta.{entrada.status}", agora)
    return proposta


@app.get(
    "/v1/propostas/{proposta_id}/contrato",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}, **_erros(404, 409, 422)},
    tags=["propostas"],
)
async def contrato_simulado(proposta_id: str) -> Response:
    # RF-09: only an approved proposal has a (simulated) contract. A one-page PDF takes ~10 ms, so it
    # runs on the event loop like the other proposal routes (no thread, no lock needed).
    proposta = _proposta_ou_404(proposta_id)
    if proposta.status != "aprovada":
        raise ErroApi(409, "transicao_invalida", "O contrato simulado só existe depois que a proposta é aprovada.")
    return Response(
        content=gerar_contrato_pdf(proposta),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="contrato-simulado-{proposta_id}.pdf"'},
    )


async def _vaga_para_ouvinte() -> None:
    # Checked before the stream starts, so the client gets a real 503 instead of a broken stream.
    if memoria.eventos.lotado():
        raise ErroApi(503, "muitas_conexoes", "Muitos painéis conectados agora. Tente de novo em instantes.")


@app.get(
    "/v1/eventos",
    response_class=EventSourceResponse,
    responses={
        200: {
            "description": "Server-Sent Events. Each message: `id`, `event: <tipo>` and the Evento JSON in `data:`.",
            "content": {"text/event-stream": {"schema": {"$ref": "#/components/schemas/Evento"}}},
        },
        **_erros(422, 503),
    },
    tags=["eventos"],
)
async def eventos(
    last_event_id: str | None = Header(default=None), _: None = Depends(_vaga_para_ouvinte)
) -> AsyncIterable[ServerSentEvent]:
    # Live proposal events for the back-office panel. New listeners get only new events;
    # a browser that reconnects sends Last-Event-ID and gets what it missed.
    if last_event_id is not None and not ID_EVENTO.fullmatch(last_event_id):
        last_event_id = None  # not one of our ids: treat as a new listener
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
