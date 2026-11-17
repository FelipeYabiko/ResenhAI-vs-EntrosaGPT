"""API v1 contract schemas.

Source of truth for the OpenAPI in api/openapi.json. Every example here must
match the JSON examples in docs/ARQUITETURA.md (checked by tests/test_contrato.py).
"""

import re
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

AVISO_SIMULACAO = "Simulação. Não é oferta de crédito."

Aviso = Literal["Simulação. Não é oferta de crédito."]
Percentual = float  # 40 means 40%
Reais = float
Cnpj = str


class Modelo(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _exemplo(dados: dict) -> ConfigDict:
    return ConfigDict(extra="forbid", json_schema_extra={"examples": [dados]})


_EMAIL = re.compile(r"\S+@\S+\.\S+")
_MUITOS_DIGITOS = re.compile(r"\d(?:[\s.\-()/]*\d){7,}")  # 8+ digits, even with separators: CPF, phone


def _sem_dado_pessoal(texto: str) -> str:
    """Free text is public in the demo (no login): refuse what looks like an e-mail, CPF or phone."""
    if _EMAIL.search(texto) or _MUITOS_DIGITOS.search(texto):
        raise ValueError("Não escreva dados pessoais (CPF, telefone, e-mail) neste campo.")
    return texto


TextoLivre = Annotated[str, AfterValidator(_sem_dado_pessoal)]
IdCurto = Annotated[str, Field(pattern=r"^[a-z0-9_]{1,40}$")]


# --- Errors ---


class ErroDetalhe(Modelo):
    codigo: Literal[
        "nao_encontrado",
        "transicao_invalida",
        "entrada_invalida",
        "cnpj_invalido",
        "cnpj_fora_da_demo",
        "limite_de_uso",
        "muitas_conexoes",
        "nao_implementado",
        "fonte_indisponivel",
    ]
    mensagem: str


class Erro(Modelo):
    model_config = _exemplo({"erro": {"codigo": "cnpj_invalido", "mensagem": "CNPJ inválido. Confira os 14 dígitos."}})
    erro: ErroDetalhe


# --- POST /v1/consultas ---


class Mix(Modelo):
    debito: Percentual = Field(ge=0, le=100)
    credito_a_vista: Percentual = Field(ge=0, le=100)
    credito_parcelado: Percentual = Field(ge=0, le=100)
    pix: Percentual = Field(ge=0, le=100)

    @model_validator(mode="after")
    def soma_100(self) -> "Mix":
        total = self.debito + self.credito_a_vista + self.credito_parcelado + self.pix
        if abs(total - 100) > 0.01:
            raise ValueError("O mix de pagamento precisa somar 100.")
        return self


class PerfilVendas(Modelo):
    faturamento_mensal: Reais = Field(gt=0)
    mix: Mix | None = None
    parcelas_medias: int | None = Field(default=None, ge=1, le=12)
    ticket_medio: Reais | None = Field(default=None, gt=0)
    prazo_recebimento: Literal["D+0", "D+1", "D+2", "D+14", "D+30"] | None = None


class Taxas(Modelo):
    """Rates in percent. null means "not informed", never zero."""

    debito: Percentual | None = Field(default=None, ge=0)
    credito_a_vista: Percentual | None = Field(default=None, ge=0)
    credito_parcelado: Percentual | None = Field(default=None, ge=0)
    pix: Percentual | None = Field(default=None, ge=0)


class SituacaoAtual(Modelo):
    taxas: Taxas
    custo_maquina_mensal: Reais = Field(default=0.0, ge=0)
    custo_saida: Reais = Field(default=0.0, ge=0)


class ConsultaEntrada(Modelo):
    model_config = _exemplo(
        {
            "cnpj": "00000000000191",
            "perfil_vendas": {
                "faturamento_mensal": 15000.00,
                "mix": {"debito": 40, "credito_a_vista": 40, "credito_parcelado": 0, "pix": 20},
                "parcelas_medias": 1,
                "ticket_medio": 60.00,
                "prazo_recebimento": "D+1",
            },
            "situacao_atual": {
                "taxas": {"debito": 1.99, "credito_a_vista": 4.98, "credito_parcelado": None, "pix": 0.0},
                "custo_maquina_mensal": 0.0,
                "custo_saida": 0.0,
            },
        }
    )
    cnpj: Cnpj = Field(pattern=r"^\d{14}$", description="Only the 14 digits, no mask.")
    perfil_vendas: PerfilVendas
    situacao_atual: SituacaoAtual | None = None


class Empresa(Modelo):
    cnpj: Cnpj
    nome: str | None = Field(description="null for MEI and sole proprietors (privacy).")
    situacao: str
    cnae_principal: str
    porte: str
    abertura: date
    capital_social: Reais
    municipio_uf: str


class Fonte(Modelo):
    nome: str
    status: Literal["ok", "cache", "indisponivel"]
    atualizado_em: date | None
    em_cache: bool


class Fator(Modelo):
    regra: str
    contribuicao: int
    explicacao: str


class Pontuacao(Modelo):
    faixa: Literal["A", "B", "C", "D", "E"]
    pontos: int = Field(ge=0, le=100)
    fatores: list[Fator]


class Maquina(Modelo):
    modelo: str
    motivo: str


class TaxasAntecipacao(Modelo):
    mensal_percentual: Percentual = Field(ge=0)


class Recomendacao(Modelo):
    maquina: Maquina
    limite_credito_simulado: Reais = Field(ge=0)
    taxas_antecipacao_simuladas: TaxasAntecipacao


class Economia(Modelo):
    custo_mensal_atual: Reais
    custo_mensal_oferta: Reais
    economia_mensal: Reais
    economia_anual: Reais
    meses_para_compensar_saida: int | None = Field(ge=0)
    estimado: Literal[True]


class BenchmarkMercado(Modelo):
    disponivel: bool
    referencia: str
    data_referencia: date | None


class ConsultaResultado(Modelo):
    model_config = _exemplo(
        {
            "consulta_id": "c_01",
            "empresa": {
                "cnpj": "00000000000191",
                "nome": "NOME DA EMPRESA",
                "situacao": "ATIVA",
                "cnae_principal": "0000-0/00",
                "porte": "DEMAIS",
                "abertura": "1966-08-01",
                "capital_social": 0,
                "municipio_uf": "Cidade/UF",
            },
            "fontes": [
                {"nome": "cnpj_publico", "status": "ok", "atualizado_em": "2026-11-08", "em_cache": True},
                {"nome": "bcb_inadimplencia_pj", "status": "ok", "atualizado_em": "2026-09-01", "em_cache": True},
            ],
            "pontuacao": {
                "faixa": "B",
                "pontos": 72,
                "fatores": [
                    {"regra": "tempo_de_atividade", "contribuicao": 15, "explicacao": "Mais de 10 anos de atividade"}
                ],
            },
            "recomendacao": {
                "maquina": {"modelo": "Plus", "motivo": "Perfil de vendas na faixa do modelo"},
                "limite_credito_simulado": 50000.00,
                "taxas_antecipacao_simuladas": {"mensal_percentual": 0.0},
            },
            "economia": {
                "custo_mensal_atual": 418.20,
                "custo_mensal_oferta": 248.40,
                "economia_mensal": 169.80,
                "economia_anual": 2037.60,
                "meses_para_compensar_saida": 0,
                "estimado": True,
            },
            "benchmark_mercado": {
                "disponivel": False,
                "referencia": "Banco Central, taxas de desconto (MDR)",
                "data_referencia": None,
            },
            "tempo_ms": 840,
            "aviso": AVISO_SIMULACAO,
        }
    )
    consulta_id: str
    empresa: Empresa
    fontes: list[Fonte]
    pontuacao: Pontuacao
    recomendacao: Recomendacao
    economia: Economia | None = Field(description="null when mix or current rates are missing.")
    benchmark_mercado: BenchmarkMercado
    tempo_ms: int = Field(ge=0)
    aviso: Aviso


# --- Proposals ---

StatusProposta = Literal["enviada", "pendente", "aprovada", "recusada"]


class PropostaEntrada(Modelo):
    model_config = _exemplo(
        {"consulta_id": "c_01", "agente": "agente_demo", "observacoes": "Comerciante prefere receber em D+1."}
    )
    consulta_id: IdCurto
    agente: str = Field(
        pattern=r"^[a-z0-9_]{1,40}$",
        description="Demo profile id chosen in 'Entrar na demonstração', e.g. agente_demo. Never a real name.",
    )
    observacoes: TextoLivre | None = Field(
        default=None,
        max_length=500,
        description="Free text about the sale. Text that looks like personal data is refused.",
    )


class PendenciaEntrada(Modelo):
    descricao: TextoLivre = Field(
        min_length=1, max_length=500, description="Text that looks like personal data is refused."
    )


class Pendencia(PendenciaEntrada):
    criada_em: datetime


class ResumoProposta(Modelo):
    cnpj: Cnpj
    nome: str | None
    faixa: Literal["A", "B", "C", "D", "E"]
    limite_credito_simulado: Reais
    economia_mensal: Reais | None


class Proposta(Modelo):
    model_config = _exemplo(
        {
            "proposta_id": "p_01",
            "consulta_id": "c_01",
            "agente": "agente_demo",
            "status": "pendente",
            "observacoes": "Comerciante prefere receber em D+1.",
            "pendencias": [
                {
                    "descricao": "Enviar comprovante de faturamento dos últimos 3 meses.",
                    "criada_em": "2026-11-12T14:10:00Z",
                }
            ],
            "resumo": {
                "cnpj": "00000000000191",
                "nome": "NOME DA EMPRESA",
                "faixa": "B",
                "limite_credito_simulado": 50000.00,
                "economia_mensal": 169.80,
            },
            "criada_em": "2026-11-12T14:03:00Z",
            "atualizada_em": "2026-11-12T14:10:00Z",
            "aviso": AVISO_SIMULACAO,
        }
    )
    proposta_id: str
    consulta_id: str
    agente: str
    status: StatusProposta
    observacoes: str | None
    pendencias: list[Pendencia]
    resumo: ResumoProposta
    criada_em: datetime
    atualizada_em: datetime
    aviso: Aviso


class ListaPropostas(Modelo):
    propostas: list[Proposta]


class PropostaAtualizacao(Modelo):
    model_config = _exemplo(
        {
            "status": "pendente",
            "pendencias": [{"descricao": "Enviar comprovante de faturamento dos últimos 3 meses."}],
        }
    )
    status: Literal["pendente", "aprovada", "recusada"]
    pendencias: list[PendenciaEntrada] = Field(default_factory=list)

    @model_validator(mode="after")
    def pendente_exige_pendencia(self) -> "PropostaAtualizacao":
        if self.status == "pendente" and not self.pendencias:
            raise ValueError("Para pedir pendência, informe ao menos uma pendência.")
        return self


# --- Events and health ---


class DadosEvento(Modelo):
    faixa: Literal["A", "B", "C", "D", "E"]
    limite_credito_simulado: Reais


class Evento(Modelo):
    model_config = _exemplo(
        {
            "id": "e_01",
            "tipo": "proposta.criada",
            "ocorrido_em": "2026-11-12T14:03:00Z",
            "proposta_id": "p_01",
            "dados": {"faixa": "B", "limite_credito_simulado": 50000.00},
            "aviso": AVISO_SIMULACAO,
        }
    )
    id: str
    tipo: Literal["proposta.criada", "proposta.pendente", "proposta.aprovada", "proposta.recusada"]
    ocorrido_em: datetime
    proposta_id: str
    dados: DadosEvento
    aviso: Aviso


class Saude(Modelo):
    model_config = _exemplo({"status": "ok", "modo_demo": True})
    status: Literal["ok"]
    modo_demo: bool
