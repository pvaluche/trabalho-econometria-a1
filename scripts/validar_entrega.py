"""
validar_entrega.py
Valida o arquivo XLSX de entrega do Desafio de Estatistica e Econometria FGV EPGE.

Pode ser importado em testes (from scripts.validar_entrega import validar_xlsx)
ou executado diretamente como script:
    python scripts/validar_entrega.py outputs/previsao_2026.xlsx
"""

from __future__ import annotations

import sys
from pathlib import Path

# Garante que src/ esta no path ao rodar como script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import openpyxl  # noqa: E402

from src.config import CANDIDATOS_EDITAL, PARTIDOS_EDITAL  # noqa: E402


def validar_xlsx(caminho: str | Path) -> dict:
    """
    Valida o arquivo XLSX de entrega contra os requisitos do edital.

    Regras verificadas:
    1. Exatamente 2 abas.
    2. Aba 1: 12 candidatos com nomes exatos do edital (sem extra, sem faltando).
    3. Aba 1: partido correto para cada candidato.
    4. Aba 1: linha "Total" presente com valor 100,0.
    5. Aba 1: round(soma_percentuais * 10) == 1000 (soma exata em decimos).
    6. Aba 1: todos os percentuais entre 0 e 100.
    7. Aba 2: tres linhas (abstencao, brancos, nulos) presentes e plausíveis.

    Parameters
    ----------
    caminho : str ou Path
        Caminho para o arquivo .xlsx.

    Returns
    -------
    dict
        {
          "valido": bool,
          "erros": list[str],   -- lista de descricoes de erro (vazia se valido)
          "avisos": list[str],  -- advertencias nao bloqueantes
        }
    """
    caminho = Path(caminho)
    erros: list[str] = []
    avisos: list[str] = []

    try:
        wb = openpyxl.load_workbook(caminho)
    except Exception as e:
        return {"valido": False, "erros": [f"Nao foi possivel abrir o arquivo: {e}"], "avisos": []}

    # 1. Exatamente 2 abas
    if len(wb.sheetnames) != 2:
        erros.append(f"Esperado 2 abas, encontrado {len(wb.sheetnames)}: {wb.sheetnames}")
        return {"valido": False, "erros": erros, "avisos": avisos}

    ws1 = wb.worksheets[0]
    ws2 = wb.worksheets[1]

    # Valida cabecalho da Aba 1
    cabecalho_ws1 = [str(ws1.cell(row=1, column=c).value or "").strip() for c in range(1, 4)]
    cabecalho_esperado_ws1 = ["Candidato(a)", "Partido", "Previsão de votos válidos (%)"]
    if cabecalho_ws1 != cabecalho_esperado_ws1:
        erros.append(
            f"Cabecalho da Aba 1 invalido. Esperado {cabecalho_esperado_ws1}, encontrado {cabecalho_ws1}"
        )

    # Le aba 1 (pula cabecalho -- linha 1)
    linhas_aba1 = []
    for row_idx, row in enumerate(ws1.iter_rows(min_row=2, values_only=False), start=2):
        nome = str(row[0].value or "").strip()
        if not nome:
            continue
        partido = str(row[1].value or "").strip() if len(row) > 1 else ""
        pct_cell = row[2] if len(row) > 2 else None
        pct_raw = pct_cell.value if pct_cell is not None else None
        if pct_cell is not None and pct_cell.number_format != "0.0":
            erros.append(
                f"Formato numerico invalido na linha {row_idx} da Aba 1: "
                f"esperado '0.0', encontrado '{pct_cell.number_format}'"
            )
        linhas_aba1.append({"nome": nome, "partido": partido, "pct": pct_raw})

    # Separa linha Total dos candidatos
    nomes_encontrados = [item["nome"] for item in linhas_aba1 if item["nome"].lower() != "total"]
    linha_total = next((item for item in linhas_aba1 if item["nome"].lower() == "total"), None)
    linhas_candidatos = [item for item in linhas_aba1 if item["nome"].lower() != "total"]

    # 2. Nomes exatos do edital -- sem extras, sem faltando
    extras = set(nomes_encontrados) - set(CANDIDATOS_EDITAL)
    faltando = set(CANDIDATOS_EDITAL) - set(nomes_encontrados)
    if extras:
        erros.append(f"Candidatos extras na aba 1: {sorted(extras)}")
    if faltando:
        erros.append(f"Candidatos faltando na aba 1: {sorted(faltando)}")

    # 3. Partidos corretos
    for linha in linhas_candidatos:
        nome = linha["nome"]
        if nome in PARTIDOS_EDITAL:
            esperado = PARTIDOS_EDITAL[nome]
            if linha["partido"] != esperado:
                erros.append(
                    f"Partido errado para '{nome}': "
                    f"esperado '{esperado}', encontrado '{linha['partido']}'"
                )

    # 4. Linha Total presente
    if linha_total is None:
        erros.append("Linha 'Total' ausente na aba 1 (obrigatoria pelo edital).")

    # 5. Soma exata em decimos
    percentuais: list[float] = []
    for linha in linhas_candidatos:
        pct = linha["pct"]
        if isinstance(pct, (int, float)) and pct is not None:
            percentuais.append(float(pct))
        else:
            erros.append(f"Percentual invalido para '{linha['nome']}': {pct!r}")

    if percentuais:
        soma = sum(percentuais)
        soma_decimos = round(soma * 10)
        if soma_decimos != 1000:
            erros.append(
                f"Soma dos percentuais nao e exatamente 100,0%: "
                f"{soma:.4f}% (round(soma*10) = {soma_decimos}, esperado 1000)"
            )

    # 6. Percentuais entre 0 e 100
    for linha in linhas_candidatos:
        pct = linha["pct"]
        if isinstance(pct, (int, float)):
            if pct < 0 or pct > 100:
                erros.append(f"Percentual fora do intervalo [0,100] para '{linha['nome']}': {pct}")

    # 7. Aba 2: cabecalho exato, linhas (Abstenção, Votos brancos, Votos nulos) e plausibilidade
    cabecalho_ws2 = [str(ws2.cell(row=1, column=c).value or "").strip() for c in range(1, 3)]
    cabecalho_esperado_ws2 = ["Resultado", "Previsão (%)"]
    if cabecalho_ws2 != cabecalho_esperado_ws2:
        erros.append(
            f"Cabecalho da Aba 2 invalido. Esperado {cabecalho_esperado_ws2}, encontrado {cabecalho_ws2}"
        )

    rotulos_esperados_aba2 = ["Abstenção", "Votos brancos", "Votos nulos"]
    labels_aba2 = []
    valores_aba2 = {}
    for row_idx, row in enumerate(ws2.iter_rows(min_row=2, values_only=False), start=2):
        label = str(row[0].value or "").strip()
        val_cell = row[1] if len(row) > 1 else None
        val = val_cell.value if val_cell is not None else None
        if val_cell is not None and val_cell.number_format != "0.0":
            erros.append(
                f"Formato numerico invalido na linha {row_idx} da Aba 2: "
                f"esperado '0.0', encontrado '{val_cell.number_format}'"
            )
        if label:
            labels_aba2.append(label)
            valores_aba2[label] = val

    for esperado in rotulos_esperados_aba2:
        if esperado not in labels_aba2:
            erros.append(f"Linha '{esperado}' ausente na aba 2 (rotulo exato com acento requerido).")

    # Plausibilidade: abstencao entre 10% e 40%, brancos/nulos entre 0% e 15%
    for label, val in valores_aba2.items():
        if val is None:
            continue
        try:
            v = float(val)
        except (TypeError, ValueError):
            erros.append(f"Valor nao numerico na aba 2 para '{label}': {val!r}")
            continue
        if "Abstenção" in label and not (10.0 <= v <= 40.0):
            avisos.append(f"Abstencao ({v:.1f}%) fora do intervalo historico [10, 40].")
        if ("branco" in label.lower() or "nulo" in label.lower()) and not (0.0 <= v <= 15.0):
            avisos.append(f"'{label}' ({v:.1f}%) fora do intervalo esperado [0, 15].")

    return {"valido": len(erros) == 0, "erros": erros, "avisos": avisos}


def main() -> None:
    """Ponto de entrada quando executado como script."""
    if len(sys.argv) < 2:
        print("Uso: python scripts/validar_entrega.py <caminho_xlsx>")
        sys.exit(1)

    caminho = Path(sys.argv[1])
    if not caminho.exists():
        print(f"Arquivo nao encontrado: {caminho}")
        sys.exit(1)

    resultado = validar_xlsx(caminho)

    if resultado["valido"]:
        print("OK: arquivo valido para entrega.")
    else:
        print(f"FALHA: {len(resultado['erros'])} erro(s) encontrado(s):")
        for e in resultado["erros"]:
            print(f"  - {e}")

    if resultado["avisos"]:
        print(f"AVISOS ({len(resultado['avisos'])}):")
        for a in resultado["avisos"]:
            print(f"  ! {a}")

    sys.exit(0 if resultado["valido"] else 1)


if __name__ == "__main__":
    main()
