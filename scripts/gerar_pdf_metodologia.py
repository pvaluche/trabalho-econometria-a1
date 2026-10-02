"""
scripts/gerar_pdf_metodologia.py
Compila a Nota Metodologica oficial do Desafio FGV EPGE 2026 em PDF
com layout profissional diagramado para EXATAMENTE 2 paginas (A4).
Zero travessoes em todo o arquivo.
"""

from __future__ import annotations

from pathlib import Path
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = ROOT / "docs" / "metodologia.pdf"


class NumberedCanvas(canvas.Canvas):
    """Canvas de dois passos para impressao exata de rodape 'Pagina X de Y'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Cabecalho discreto
        self.drawString(
            45,
            815,
            "FGV EPGE | Desafio de Estatistica e Econometria - Eleicoes Presidenciais 2026",
        )
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(45, 810, 550, 810)

        # Rodape
        self.line(45, 38, 550, 38)
        self.drawString(
            45,
            26,
            "Nota Metodologica Oficial | Codigo congelado na tag Git: modelo-congelado",
        )
        page_text = f"Pagina {self._pageNumber} de {page_count}"
        self.drawRightString(550, 26, page_text)
        self.restoreState()


def compilar_pdf_metodologia():
    """Gera o documento PDF diagramado em estritamente 2 paginas."""
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=42,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    # Estilos customizados compactos para caber perfeitamente em 2 paginas
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_LEFT,
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155"),
    )
    sec_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=4,
        spaceAfter=2,
    )
    subsec_style = ParagraphStyle(
        "SubSectionHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=3,
        spaceAfter=1,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.6,
        leading=9.8,
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_JUSTIFY,
        spaceAfter=2.5,
    )
    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    bullet_style = ParagraphStyle(
        "CompactBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.4,
        leading=9.4,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=8,
        firstLineIndent=-6,
        spaceAfter=1.8,
    )
    box_style = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor("#0f172a"),
        alignment=TA_JUSTIFY,
    )

    story = []

    # =========================================================================
    # PAGINA 1: Contexto, Dados, Modelos M0-M3, Backtest e Decisao de Ajustes
    # =========================================================================

    story.append(
        Paragraph("NOTA METODOLOGICA: MODELO DE PREVISAO PRESIDENCIAL 2026", title_style)
    )
    story.append(Spacer(1, 2))
    story.append(
        Paragraph(
            "<b>Desafio de Estatistica e Econometria FGV EPGE</b> | "
            "<b>Grupo:</b> Joao Pedro Valuche, Arthur Caron Lyra, Lethicia Manfioletti Possamai | "
            "<b>Tag:</b> <code>modelo-congelado</code>",
            meta_style,
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f766e"), spaceAfter=4)
    )

    # 1. Dados e Pre-processamento
    story.append(Paragraph("1. Dados, Fontes e Pre-processamento", sec_style))
    story.append(
        Paragraph(
            "A base do projeto congrega pesquisas de intencao de voto registradas no sistema PesqEle/TSE "
            "conduzidas por institutos nacionais de primeira linha (Datafolha, Quaest, AtlasIntel, PoderData e Real Time Big Data). "
            "O pre-processamento segue estritamente tres regras: "
            "(i) <b>Filtro de Vespera e Corte:</b> levantamentos na janela de tres semanas anteriores ao pleito, com corte as 20h00 de sabado (03/10/2026); "
            "(ii) <b>Conversao para Validos:</b> exclusao de votos brancos, nulos e indecisos com renormalizacao a 100,0% "
            "(<i>p<sub>i,j</sub> = v<sub>i,j</sub> / &sum; v<sub>k,j</sub> &times; 100%</i>) para os 12 candidatos oficiais do edital; "
            "(iii) <b>Arredondamento:</b> aplicacao do algoritmo de Maiores Restos (Hamilton-Hare) na entrega em uma casa decimal, garantindo soma exata de 100,0%.",
            body_style,
        )
    )

    # 2. Formulacao dos Modelos Base
    story.append(Paragraph("2. Formulacao Formal dos Modelos Base (M0 a M3)", sec_style))
    story.append(
        Paragraph(
            "&bull; <b>M0 (Media Simples por Instituto):</b> &nbsp; <i>p_hat<sub>i</sub><sup>M0</sup> = (1/J) sum<sub>j=1</sub><sup>J</sup> p<sub>i,j</sub></i> &nbsp; "
            "(agrega a ultima pesquisa valida de cada instituto na vespera).<br/>"
            "&bull; <b>M1 (Decaimento Temporal Exponencial):</b> &nbsp; <i>p_hat<sub>i</sub><sup>M1</sup> = sum w<sub>j</sub> p<sub>i,j</sub> / sum w<sub>j</sub></i>, "
            "com <i>w<sub>j</sub> = exp(-ln(2)*dt<sub>j</sub> / h)</i>, testado para meia-vida <i>h em {7, 14, 21}</i> dias.<br/>"
            "&bull; <b>M2 (Efeito de Casa com Regularizacao Shrinkage):</b> &nbsp; <i>p_hat<sub>i</sub><sup>M2</sup> = sum w<sub>j</sub> (p<sub>i,j</sub> - beta_hat<sub>i,inst</sub>)</i>, "
            "com <i>beta_hat<sub>i,inst</sub> = [n<sub>inst</sub> / (n<sub>inst</sub> + k)] delta_bar<sub>i,inst</sub></i>, <i>k em {1, 3, 10}</i>.<br/>"
            "&bull; <b>M3 (Regressao Ridge com Incumbencia):</b> &nbsp; <i>p_hat<sub>i</sub><sup>M3</sup> = x<sub>i</sub>' beta_hat</i>, regularizado com penalidade L2 "
            "(alpha em {0.01, 0.1, 1.0, 10.0}) incluindo variavel binaria de governismo.",
            body_style,
        )
    )

    # 3. Backtest Expanding Window
    story.append(Paragraph("3. Backtest Historico e Selecao de Modelos (Expanding Window)", sec_style))
    story.append(
        Paragraph(
            "O backtest avaliou causalmente as eleicoes de 2014, 2018 e 2022 (treino restrito a t-1; total de 11 a 13 candidatos da urna oficial apurada pelo TSE). "
            "A metrica primaria e o Mean Absolute Error (MAE) sobre todos os concorrentes da urna:",
            body_style,
        )
    )

    tabela_e1_data = [
        ["Modelo Avaliado", "2014 (p.p.)", "2018 (p.p.)", "2022 (p.p.)", "Media Exp.", "Decisao pela Regra Pre-registrada"],
        ["M0 Puro", "1,3317", "1,4964", "0,8341", "1,2207", "VENCEDOR ETAPA 1 (Menor Erro e Parcimonia)"],
        ["M1 (h=7d)", "1,4898", "2,0585", "0,9151", "1,4878", "Rejeitado (MAE superior ao M0)"],
        ["M1 (h=14d)", "1,5142", "2,0585", "0,9151", "1,4959", "Rejeitado (MAE superior ao M0)"],
        ["M2 (k=1)", "1,4890", "2,0601", "0,9180", "1,4890", "Rejeitado (MAE superior ao M0)"],
        ["M2 (k=3)", "1,5004", "2,0594", "0,9167", "1,4922", "Rejeitado (MAE superior ao M0)"],
        ["M2 (k=10)", "1,5098", "2,0588", "0,9156", "1,4947", "Rejeitado (MAE superior ao M0)"],
        ["M3 (alpha=0.1)", "1,4954", "2,0585", "0,9151", "1,4897", "Rejeitado (MAE superior ao M0)"],
        ["M3 (alpha=1.0)", "1,5078", "2,0585", "0,9151", "1,4938", "Rejeitado (MAE superior ao M0)"],
    ]

    t_e1 = Table(
        tabela_e1_data,
        colWidths=[95, 52, 52, 52, 58, 196],
        style=[
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6.8),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (4, -1), "CENTER"),
            ("ALIGN", (5, 0), (5, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f0fdf4")),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ],
    )
    story.append(t_e1)
    story.append(Spacer(1, 3))

    # Justificativa dos Ajustes
    story.append(Paragraph("Ajustes da Etapa 2 Incorporados e Rejeitados sobre o M0:", subsec_style))
    story.append(
        Paragraph(
            "&bull; <b>Vies Comum de Pesquisa (k_mu=3): APROVADO.</b> "
            "Corrige a subestimacao sistematica de votos do principal adversario do PT observada nas vesperas. "
            "Reduz o MAE medio em <b>0,1834 p.p.</b>, superando com folga o limiar estatistico de 1 SE (Delta_bar &gt; SE = 0,1026 p.p.).<br/>"
            "&bull; <b>Voto Util Estrategico (gamma=1.0): APROVADO.</b> "
            "Modela a migracao dos eleitores do 3o e 4o colocados para os dois ponteiros na reta final. "
            "Reduz o MAE em <b>0,1301 p.p.</b> (Delta_bar &gt; SE = 0,0889 p.p.), derrubando o erro de 2022 para 0,5284 p.p.<br/>"
            "&bull; <b>Efeito de Casa (M2): REJEITADO.</b> "
            "Na vespera imediata, as divergencias entre institutos refletem primariamente variancia amostral; o shrinkage nao superou M0.<br/>"
            "&bull; <b>Prior de Nanicos (w=0.5): REJEITADO PELA REGRA FORMAL.</b> "
            "Testado causalmente por partido historico. Obteve ganho de apenas Delta_bar = 0,0040 p.p. com SE = 0,0067 p.p. "
            "Como Delta_bar &le; SE, o efeito e indistinguivel de zero (limitacao estrutural das pesquisas historicas que agregavam nanicos em 'outros'). "
            "Fixa-se compulsoriamente <b>w=0.0 no Modelo Oficial</b>, retendo w=0.5 apenas para analise de sensibilidade.<br/>"
            "&bull; <b>Modelo Oficial Aprovado:</b> M0 + Vies Comum (k=3) + Voto Util (gamma=1.0) com w=0.0. "
            "O MAE medio despenca para <b>0,9640 p.p.</b>, com reducao consolidada de <b>0,2568 p.p. (&gt; 6 &times; SE)</b>.",
            body_style,
        )
    )

    # Forca quebra para a pagina 2
    story.append(PageBreak())

    # =========================================================================
    # PAGINA 2: Sensibilidade, Moderacao da Margem, Aba 2 e Protocolo de Sabado
    # =========================================================================

    # 4. Sensibilidade e Moderacao da Margem
    story.append(Paragraph("4. Analise de Sensibilidade, Moderacao da Margem e Limitacao Honesta", sec_style))
    story.append(
        Paragraph(
            "<b>Confronto Preliminar 2026 (Lula x Flavio Bolsonaro):</b><br/>"
            "&bull; <b>M0 Puro:</b> Lula 45,4% vs Flavio Bolsonaro 41,5% (Lula +3,9 p.p.) -> <i>[NUMERO FINAL APOS CORTE DE SABADO]</i>.<br/>"
            "&bull; <b>Modelo Oficial Aprovado (w=0.0):</b> Flavio Bolsonaro 45,9% vs Lula 45,6% (Flavio +0,3 p.p.) -> <i>[NUMERO FINAL APOS CORTE DE SABADO]</i>.<br/>"
            "&bull; <b>Sensibilidade com Nanicos (w=0.5):</b> Flavio Bolsonaro 45,8% vs Lula 45,5% (Flavio +0,3 p.p.) -> <i>[NUMERO FINAL APOS CORTE DE SABADO]</i>.<br/>"
            "<b>Mecanismo de Moderacao da Margem:</b> O Modelo Oficial eleva a pontuacao de Flavio ao expurgar o vies historico anti-oposicao "
            "e expande a votacao dos dois lideres simultaneamente via voto util, comprimindo a diferenca liquida entre ambos. "
            "Como a distancia projetada (0,3 p.p.) situa-se amplamente abaixo do Erro Medio Historico da Margem Top-2 (<b>4,54 p.p.</b>, n=3) "
            "e do Percentil 80 da Margem (<b>5,16 p.p.</b>), caracteriza-se tecnicamente que a <b>diferenca projetada e inferior ao erro historico da margem</b>, "
            "sendo estatisticamente indistinguivel de empate no ruido amostral.",
            body_style,
        )
    )

    # Box de Transparencia Honesta
    box_data = [
        [
            Paragraph(
                "<b>Transparencia Econometrica e Limitacao Honesta (Erro da Margem em 2022):</b><br/>"
                "Em 2022, o M0 Puro previu Lula com 46,88% e Bolsonaro com 40,35% (margem de 6,53 p.p. vs 5,23 p.p. do TSE, gerando erro de <b>1,29 p.p.</b>). "
                "O Modelo Oficial projetou Bolsonaro em 44,76% (+1,57 p.p. vs TSE) e Lula em 45,67% (-2,76 p.p. vs TSE), resultando em margem de 0,91 p.p. "
                "Com isso, o <b>erro na margem polarizada subiu para 4,32 p.p.</b> no Modelo Oficial. "
                "Conclusao: embora o Modelo Oficial reduza fortemente o erro medio de todos os candidatos da urna (de 0,83 para 0,58 p.p.), "
                "ele tende a aproximar excessivamente os lideres em eleicoes de polarizacao atipica. Essa limitacao e documentada com total integridade.",
                box_style,
            )
        ]
    ]
    t_box = Table(
        box_data,
        colWidths=[505],
        style=[
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffbeb")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#f59e0b")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ],
    )
    story.append(t_box)
    story.append(Spacer(1, 3))

    # 5. Aba 2: Agregados Eleitorais e Contas Formais de Desempate
    story.append(Paragraph("5. Aba 2: Agregados Eleitorais e Contas Formais de Desempate", sec_style))
    story.append(
        Paragraph(
            "Tres abordagens concorrentes foram testadas no expanding window: Persistencia (Random Walk), Media Movel e Tendencia Linear.<br/>"
            "1. <b>Abstencao (% sobre Aptos):</b> Persistencia = 0,9433 | Media Movel = 2,1669 | <b>Tendencia Linear = 0,3989 p.p.</b><br/>"
            "&nbsp;&nbsp;&bull; Conta formal: Delta_bar = MAE_Linear - MAE_Persist = -0,5444 p.p. com SE(Delta) = 0,3608 p.p.<br/>"
            "&nbsp;&nbsp;&bull; Decisao: Como |Delta_bar| = 0,5444 &gt; SE = 0,3608, a Tendencia Linear e estatisticamente superior e vence sem necessidade da regra de parcimonia. "
            "<b>Projecao Oficial 2026: 22,3%</b> sobre aptos.<br/>"
            "2. <b>Votos Brancos (% sobre Comparecimento):</b> <b>Persistencia = 0,9867</b> | Media Movel = 0,9969 | Tendencia Linear = 1,2061 p.p.<br/>"
            "&nbsp;&nbsp;&bull; Conta formal: Delta_bar = MAE_Media - MAE_Persist = +0,0103 p.p. com SE(Delta) = 0,3160 p.p.<br/>"
            "&nbsp;&nbsp;&bull; Decisao: Como |Delta_bar| = 0,0103 &le; SE = 0,3160, ha empate tecnico. Pela regra formal de parcimonia, seleciona-se a Persistencia (patamar de 2022). "
            "<b>Projecao Oficial 2026: 1,6%</b> sobre comparecimento.<br/>"
            "3. <b>Votos Nulos (% sobre Comparecimento):</b> Persistencia = 1,3167 | <b>Media Movel = 1,2147</b> | Tendencia Linear = 1,3989 p.p.<br/>"
            "&nbsp;&nbsp;&bull; Conta formal: Delta_bar = MAE_Media - MAE_Persist = -0,1019 p.p. com SE(Delta) = 0,1429 p.p.<br/>"
            "&nbsp;&nbsp;&bull; Decisao: Como |Delta_bar| = 0,1019 &le; SE = 0,1429, a diferenca e inferior a 1 SE (empate estatistico). Pela regra de parcimonia, vence a Persistencia. "
            "<b>Projecao Oficial 2026: 2,8%</b> sobre comparecimento.",
            body_style,
        )
    )

    # 6. Protocolo de Sabado
    story.append(Paragraph("6. Protocolo de Fechamento do Corte de Sabado (Checkpoint 4)", sec_style))
    story.append(
        Paragraph(
            "O pipeline processara os dados definitivos no corte de <b>sabado 03/10/2026 as 20h00</b>. "
            "Pesquisas registradas no PesqEle/TSE com divulgacao programada: "
            "<b>Datafolha</b> (BR-01708/2026, n=4.006), <b>Quaest</b> (BR-02197/2026, n=3.702), "
            "<b>AtlasIntel</b> (BR-00999/2026, n=5.000), <b>PoderData</b> (BR-03519/2026, n=4.000) e "
            "<b>Real Time Big Data</b> (BR-01068/2026, n=2.000). "
            "Caso algum levantamento nao seja publicado ate as 20h00, o motivo sera registrado em <code>reports/checkpoint_4.md</code> "
            "e a projecao final utilizara as pesquisas homologadas disponiveis. "
            "Os valores finais preencherao os marcadores <code>[NUMERO FINAL]</code> no relatorio e na planilha <code>outputs/previsao_2026.xlsx</code>.",
            body_style,
        )
    )

    # 7. Equipe e Assinatura
    story.append(Spacer(1, 2))
    t_equipe_data = [
        [
            Paragraph("<b>Joao Pedro Valuche</b><br/>Estatistica e Econometria", meta_style),
            Paragraph("<b>Arthur Caron Lyra</b><br/>Estatistica e Econometria", meta_style),
            Paragraph("<b>Lethicia Manfioletti Possamai</b><br/>Estatistica e Econometria", meta_style),
        ]
    ]
    t_eq = Table(
        t_equipe_data,
        colWidths=[168, 168, 168],
        style=[
            ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#0f766e")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ],
    )
    story.append(t_eq)

    # Constrói o documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"OK: PDF compilado com sucesso em {OUTPUT_PDF}")


if __name__ == "__main__":
    compilar_pdf_metodologia()
