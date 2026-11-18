"""Simulated contract PDF for an approved proposal (RF-09).

Pure function: proposal in, PDF bytes out. It only prints what the proposal already holds;
no rate, term or clause is invented. Every page carries the "SIMULAÇÃO" watermark and the
simulation notice. Text stays real text (not an image), so screen readers can read it.
"""

from fpdf import FPDF

from app.schemas import AVISO_SIMULACAO, Proposta

MARINHO = (48, 58, 149)  # same navy as the site
MARCA_DAGUA = (222, 224, 238)

CLAUSULA = (
    "Este documento foi gerado automaticamente para a demonstração do CredFácil (Hack Brasil 2026). "
    "É uma simulação: não é oferta de crédito, não cria obrigação para nenhuma parte e não tem valor legal. "
    "Faixa, limite e economia vêm de regras e premissas do time, não de uma análise real de crédito."
)


def _reais(valor: float) -> str:
    """50000.0 -> R$ 50.000,00 (no locale dependency)."""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def _cnpj(digitos: str) -> str:
    return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"


class _Documento(FPDF):
    def header(self) -> None:
        # Drawn first on every page, so the content prints over it.
        self.set_font("Helvetica", "B", 90)
        self.set_text_color(*MARCA_DAGUA)
        with self.rotation(angle=45, x=self.w / 2, y=self.h / 2):
            self.text(x=self.w / 2 - 95, y=self.h / 2 + 12, text="SIMULAÇÃO")
        self.set_text_color(*MARINHO)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 8, f"{AVISO_SIMULACAO}  Página {self.page_no()}/{{nb}}", align="C")


def gerar_contrato_pdf(proposta: Proposta) -> bytes:
    pdf = _Documento(format="A4")
    pdf.set_title(f"Contrato simulado {proposta.proposta_id}")
    pdf.set_author("CredFácil (demonstração)")
    pdf.set_lang("pt-BR")
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, "CredFácil", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Contrato simulado de crédito", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_draw_color(*MARINHO)
    pdf.set_line_width(0.6)
    pdf.set_font("Helvetica", "B", 12)
    pdf.multi_cell(0, 9, AVISO_SIMULACAO, border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    def secao(titulo: str, linhas: list[str]) -> None:
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, titulo, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        for linha in linhas:
            pdf.multi_cell(0, 6.5, linha, new_x="LMARGIN", new_y="NEXT")

    resumo = proposta.resumo
    secao(
        "Proposta",
        [
            f"Número da proposta: {proposta.proposta_id}",
            f"Consulta de origem: {proposta.consulta_id}",
            f"Aprovada em: {proposta.atualizada_em:%d/%m/%Y %H:%M} (UTC)",
            f"Perfil de demonstração do vendedor: {proposta.agente}",
        ],
    )
    secao(
        "Empresa",
        [
            f"CNPJ: {_cnpj(resumo.cnpj)}",
            f"Nome: {resumo.nome or 'não exibido (pode identificar uma pessoa)'}",
        ],
    )
    resultado = [
        f"Faixa de risco: {resumo.faixa}",
        f"Limite de crédito simulado: {_reais(resumo.limite_credito_simulado)}",
    ]
    if resumo.economia_mensal is not None:
        resultado.append(f"Economia estimada com a maquininha: {_reais(resumo.economia_mensal)} por mês")
    secao("Resultado da análise (simulação)", resultado)
    if proposta.pendencias:
        secao(
            "Pendências pedidas durante a análise",
            [f"{p.criada_em:%d/%m/%Y}: {p.descricao}" for p in proposta.pendencias],
        )
    secao("Natureza deste documento", [CLAUSULA])

    return bytes(pdf.output())
