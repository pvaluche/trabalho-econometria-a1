"""
src/entrega.py
Gera a planilha XLSX oficial de previsoes para o Desafio FGV EPGE 2026.
Garante total conformidade com as regras do edital e scripts/validar_entrega.py.
"""

from __future__ import annotations

from pathlib import Path
import openpyxl

from src.arredondamento import maiores_restos
from src.config import CANDIDATOS_EDITAL, OUTPUTS_DIR, PARTIDOS_EDITAL


def gerar_planilha_entrega(
    previsoes_candidatos: dict[str, float],
    adicionais: dict[str, float],
    caminho_saida: Path | str | None = None,
) -> Path:
    """
    Gera a planilha XLSX de entrega com 2 abas perfeitamente formatadas.

    Aba 1: Votos Validos dos 12 candidatos do edital com partidos e linha Total (100,0%).
    Aba 2: Agregados Eleitorais (Abstencao, Votos brancos, Votos nulos).
    """
    if caminho_saida is None:
        caminho_saida = OUTPUTS_DIR / "previsao_2026.xlsx"
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    # Garante fechamento de 100,0% via maiores restos
    valores_ordenados = [previsoes_candidatos.get(c, 0.0) for c in CANDIDATOS_EDITAL]
    valores_fechados = maiores_restos(valores_ordenados, total=100.0, casas=1)

    wb = openpyxl.Workbook()

    # Aba 1: Candidatos
    ws1 = wb.active
    ws1.title = "Candidatos"
    ws1.append(["Candidato(a)", "Partido", "Previsao de votos validos (%)"])

    for nome, pct in zip(CANDIDATOS_EDITAL, valores_fechados):
        ws1.append([nome, PARTIDOS_EDITAL[nome], round(float(pct), 1)])

    ws1.append(["Total", "", 100.0])

    # Aba 2: Adicionais
    ws2 = wb.create_sheet("Adicionais")
    ws2.append(["Resultado", "Previsao (%)"])
    ws2.append(["Abstencao", round(float(adicionais.get("abstencao", 22.3)), 1)])
    ws2.append(["Votos brancos", round(float(adicionais.get("brancos", 1.6)), 1)])
    ws2.append(["Votos nulos", round(float(adicionais.get("nulos", 2.8)), 1)])

    wb.save(caminho_saida)
    return caminho_saida
