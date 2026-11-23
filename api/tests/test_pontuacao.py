"""Rule-based scoring (RF-04): pure, explainable, same input gives same output."""

from datetime import date
from decimal import Decimal as D
from pathlib import Path

import pytest

from app.schemas import Empresa
from scoring.premissas import PremissasPendentes, carregar_premissas
from scoring.regras import pontuar

PREMISSAS = carregar_premissas(Path(__file__).with_name("premissas_teste.toml"))
HOJE = date(2026, 11, 23)


def empresa(**mudancas) -> Empresa:
    base = {
        "cnpj": "98765432000198",
        "nome": "MERCADINHO BOA VISTA (FICTÍCIO)",
        "situacao": "ATIVA",
        "cnae_principal": "4712-1/00",
        "porte": "ME",
        "abertura": date(2018, 3, 12),
        "capital_social": 20000.0,
        "municipio_uf": "São Paulo/SP",
    }
    return Empresa(**(base | mudancas))


def test_soma_das_regras_e_faixa():
    p = pontuar(empresa(), D(15000), PREMISSAS, HOJE)
    # base 50 + more than 5 years (+15) + ME (0) = 65 -> B (>= 60)
    assert (p.pontos, p.faixa) == (65, "B")
    assert [(f.regra, f.contribuicao) for f in p.fatores] == [("tempo_de_atividade", 15), ("porte", 0)]
    assert p.fatores[0].explicacao == "Mais de 5 anos de atividade"


@pytest.mark.parametrize(
    ("abertura", "pontos"),
    [(date(2026, 6, 1), 35), (date(2024, 11, 23), 50), (date(2021, 11, 23), 65)],
)
def test_tempo_de_atividade_por_faixa_de_anos(abertura, pontos):
    assert pontuar(empresa(abertura=abertura), D(15000), PREMISSAS, HOJE).pontos == pontos


@pytest.mark.parametrize(("porte", "pontos"), [("ME", 65), ("EPP", 70), ("DEMAIS", 75)])
def test_porte(porte, pontos):
    assert pontuar(empresa(porte=porte), D(15000), PREMISSAS, HOJE).pontos == pontos


def test_porte_desconhecido_vale_zero_e_aparece_na_explicacao():
    p = pontuar(empresa(porte="XYZ"), D(15000), PREMISSAS, HOJE)
    assert p.pontos == 65
    assert "não tem regra" in p.fatores[1].explicacao


@pytest.mark.parametrize(("pontos_alvo", "faixa"), [(75, "A"), (74, "B"), (60, "B"), (45, "C"), (30, "D"), (29, "E")])
def test_limites_das_faixas(pontos_alvo, faixa):
    from scoring.regras import faixa_para

    assert faixa_para(pontos_alvo, PREMISSAS) == faixa


@pytest.mark.parametrize("situacao", ["BAIXADA", "SUSPENSA", "INAPTA"])
def test_empresa_nao_ativa_vai_direto_para_e(situacao):
    # docs/ARQUITETURA.md: gate. Non-active registration means band E and zero limit, nothing else computed.
    p = pontuar(empresa(situacao=situacao), D(15000), PREMISSAS, HOJE)
    assert (p.pontos, p.faixa) == (0, "E")
    assert [f.regra for f in p.fatores] == ["situacao_cadastral"]


def test_pontos_ficam_entre_0_e_100():
    muito_novo = PREMISSAS.model_copy(deep=True)
    muito_novo.pontuacao.pontos_base = 5
    assert pontuar(empresa(abertura=date(2026, 11, 1)), D(15000), muito_novo, HOJE).pontos == 0


def test_mesma_entrada_mesma_saida():
    assert pontuar(empresa(), D(15000), PREMISSAS, HOJE) == pontuar(empresa(), D(15000), PREMISSAS, HOJE)


def test_premissas_em_proposta_nao_sao_usadas(tmp_path):
    arquivo = tmp_path / "p.toml"
    arquivo.write_text(Path(__file__).with_name("premissas_teste.toml").read_text().replace('"aprovada"', '"proposta"'))
    with pytest.raises(PremissasPendentes):
        carregar_premissas(arquivo)


def test_premissas_do_projeto_sao_validas_mesmo_em_proposta():
    # The real file must always parse, so the team can flip status without surprises.
    from scoring.premissas import ARQUIVO, ler_premissas

    assert ler_premissas(ARQUIVO).status in {"proposta", "aprovada"}
