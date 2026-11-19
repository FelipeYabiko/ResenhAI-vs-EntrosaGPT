"""Cost simulator core (RF-11, RF-12): pure, deterministic, no network, no LLM.

Reference case from docs/ARQUITETURA.md and docs/PRODUTO.md (RF-11).
"""

from decimal import Decimal as D

import pytest

from recomendacao.simulador import Oferta, SituacaoAtual, TaxaNaoInformada, comparar_ofertas, simular

MIX_REFERENCIA = {"debito": D(40), "credito_a_vista": D(40), "credito_parcelado": D(0), "pix": D(20)}
ATUAL_REFERENCIA = SituacaoAtual(
    taxas={"debito": D("1.99"), "credito_a_vista": D("4.98"), "credito_parcelado": None, "pix": D(0)}
)
OFERTA_REFERENCIA = Oferta(
    nome="Oferta de referência",
    taxas={"debito": D("0.99"), "credito_a_vista": D("3.15"), "credito_parcelado": D("9.9"), "pix": D(0)},
)


def test_caso_de_referencia_do_rf11():
    r = simular(D(15000), MIX_REFERENCIA, ATUAL_REFERENCIA, OFERTA_REFERENCIA)
    assert r.custo_mensal_atual == D("418.20")
    assert r.custo_mensal_oferta == D("248.40")
    assert r.economia_mensal == D("169.80")
    assert r.economia_anual == D("2037.60")
    assert r.meses_para_compensar_saida == 0


def test_exemplo_da_landing_bate_com_o_simulador():
    # D-017: the landing shows R$ 350 -> R$ 240 (illustrative 3.5% -> 2.4% on R$ 10,000, single rate).
    so_credito = {"debito": D(0), "credito_a_vista": D(100), "credito_parcelado": D(0), "pix": D(0)}
    atual = SituacaoAtual(taxas={"debito": None, "credito_a_vista": D("3.5"), "credito_parcelado": None, "pix": None})
    oferta = Oferta(
        nome="x", taxas={"debito": None, "credito_a_vista": D("2.4"), "credito_parcelado": None, "pix": None}
    )
    r = simular(D(10000), so_credito, atual, oferta)
    assert (r.custo_mensal_atual, r.custo_mensal_oferta, r.economia_mensal) == (D("350.00"), D("240.00"), D("110.00"))


def test_mesma_entrada_mesma_saida():
    a = simular(D(15000), MIX_REFERENCIA, ATUAL_REFERENCIA, OFERTA_REFERENCIA)
    b = simular(D(15000), MIX_REFERENCIA, ATUAL_REFERENCIA, OFERTA_REFERENCIA)
    assert a == b


def test_custo_da_maquina_entra_no_custo_mensal():
    atual = SituacaoAtual(taxas=ATUAL_REFERENCIA.taxas, custo_maquina_mensal=D("49.90"))
    oferta = Oferta(nome="x", taxas=OFERTA_REFERENCIA.taxas, custo_maquina_mensal=D("19.90"))
    r = simular(D(15000), MIX_REFERENCIA, atual, oferta)
    assert r.custo_mensal_atual == D("468.10")
    assert r.custo_mensal_oferta == D("268.30")
    assert r.economia_mensal == D("199.80")


@pytest.mark.parametrize(
    ("custo_saida", "meses"),
    [(D(0), 0), (D("169.80"), 1), (D("169.81"), 2), (D(500), 3)],
)
def test_custo_de_saida_diz_em_quantos_meses_se_paga(custo_saida, meses):
    # RF-12: rounded up, a partial month counts as one more month.
    atual = SituacaoAtual(taxas=ATUAL_REFERENCIA.taxas, custo_saida=custo_saida)
    assert simular(D(15000), MIX_REFERENCIA, atual, OFERTA_REFERENCIA).meses_para_compensar_saida == meses


def test_oferta_mais_cara_mostra_economia_negativa_e_nunca_compensa():
    cara = Oferta(
        nome="cara", taxas={k: (v + D(1) if v is not None else None) for k, v in ATUAL_REFERENCIA.taxas.items()}
    )
    atual = SituacaoAtual(taxas=ATUAL_REFERENCIA.taxas, custo_saida=D(100))
    r = simular(D(15000), MIX_REFERENCIA, atual, cara)
    assert r.economia_mensal < 0
    assert r.meses_para_compensar_saida is None


@pytest.mark.parametrize("lado", ["atual", "oferta"])
def test_taxa_nao_informada_de_modalidade_usada_nao_vira_zero(lado):
    # docs/DADOS.md: never assume Pix (or any rate) is zero.
    sem_pix = {**ATUAL_REFERENCIA.taxas, "pix": None}
    atual = SituacaoAtual(taxas=sem_pix) if lado == "atual" else ATUAL_REFERENCIA
    oferta = Oferta(nome="x", taxas=sem_pix) if lado == "oferta" else OFERTA_REFERENCIA
    with pytest.raises(TaxaNaoInformada, match="pix"):
        simular(D(15000), MIX_REFERENCIA, atual, oferta)


def test_taxa_nao_informada_de_modalidade_sem_vendas_nao_atrapalha():
    # credito_parcelado is 0% of the mix, so its missing current rate does not matter.
    assert simular(D(15000), MIX_REFERENCIA, ATUAL_REFERENCIA, OFERTA_REFERENCIA).economia_mensal == D("169.80")


@pytest.mark.parametrize(
    "mix",
    [
        {"debito": D(50), "credito_a_vista": D(40), "credito_parcelado": D(0), "pix": D(20)},  # 110%
        {"debito": D(40), "credito_a_vista": D(40), "pix": D(20)},  # missing key
        {"debito": D(-10), "credito_a_vista": D(90), "credito_parcelado": D(0), "pix": D(20)},
    ],
)
def test_mix_invalido_e_recusado(mix):
    with pytest.raises(ValueError):
        simular(D(15000), mix, ATUAL_REFERENCIA, OFERTA_REFERENCIA)


def test_faturamento_precisa_ser_positivo():
    with pytest.raises(ValueError):
        simular(D(0), MIX_REFERENCIA, ATUAL_REFERENCIA, OFERTA_REFERENCIA)


def test_comparar_ofertas_ordena_da_mais_barata_para_a_mais_cara():
    barata = Oferta(nome="barata", taxas={**OFERTA_REFERENCIA.taxas, "debito": D("0.50")})
    media = OFERTA_REFERENCIA
    cara = Oferta(nome="cara", taxas={**OFERTA_REFERENCIA.taxas, "debito": D("1.50")})
    resultados = comparar_ofertas(D(15000), MIX_REFERENCIA, ATUAL_REFERENCIA, [cara, barata, media])
    assert [r.oferta for r in resultados] == ["barata", "Oferta de referência", "cara"]
    assert resultados[0].custo_mensal_oferta < resultados[1].custo_mensal_oferta < resultados[2].custo_mensal_oferta


def test_resultado_vira_o_formato_do_contrato():
    economia = simular(D(15000), MIX_REFERENCIA, ATUAL_REFERENCIA, OFERTA_REFERENCIA).para_contrato()
    assert economia.model_dump() == {
        "custo_mensal_atual": 418.2,
        "custo_mensal_oferta": 248.4,
        "economia_mensal": 169.8,
        "economia_anual": 2037.6,
        "meses_para_compensar_saida": 0,
        "estimado": True,
    }
