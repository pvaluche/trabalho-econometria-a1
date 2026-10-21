"""
scripts/gerar_figuras_readme.py
Gera as figuras do README (docs/img/) a partir dos dados e das planilhas do repositorio.

Uso:
    python scripts/gerar_figuras_readme.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.dates

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.backtest import estimar_m0
from src.backtest_2t import carregar_pesquisas_2026_2t
from src.config import MANUAL_DIR, OUTPUTS_DIR, PROCESSED_DIR

IMG = ROOT / "docs" / "img"
AZUL, CINZA, VERMELHO = "#1F3A5F", "#9AA3AD", "#B03A2E"

plt.rcParams.update(
    {
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#E3E6EA",
        "grid.linestyle": "--",
        "axes.axisbelow": True,
        "figure.dpi": 150,
    }
)


def virg(x: float, casas: int = 2) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def ler_planilha(caminho: Path) -> dict[str, float]:
    ws = openpyxl.load_workbook(caminho)["Candidatos"]
    return {
        r[0].value: float(r[2].value)
        for r in ws.iter_rows(min_row=2)
        if r[0].value and r[0].value != "Total"
    }


def figura_1t() -> None:
    tse = json.loads((PROCESSED_DIR / "tse_2026_1t_oficial.json").read_text(encoding="utf-8"))
    real = {c: v["pct_validos"] for c, v in tse["candidatos"].items()}
    final = ler_planilha(OUTPUTS_DIR / "previsao_2026.xlsx")
    m0 = estimar_m0(pd.read_csv(MANUAL_DIR / "pesquisas_2026.csv"), 2026)

    mae_f = sum(abs(final[c] - real[c]) for c in final) / len(final)
    mae_0 = sum(abs(m0.get(c, 0.0) - real[c]) for c in final) / len(final)

    nomes = {
        "Flávio Bolsonaro": "Flávio",
        "Luiz Inácio Lula da Silva": "Lula",
        "Augusto Cury": "Cury",
        "Renan Santos": "Renan",
        "Ronaldo Caiado": "Caiado",
        "Romeu Zema": "Zema",
    }
    cands = list(nomes)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), gridspec_kw={"width_ratios": [1, 2.2]})
    for ax, grupo in zip(axes, (cands[:2], cands[2:])):
        x = range(len(grupo))
        w = 0.27
        ax.bar([i - w for i in x], [m0[c] for c in grupo], w, color=CINZA, label="Média simples")
        ax.bar(list(x), [final[c] for c in grupo], w, color=AZUL, label="Nosso modelo")
        ax.bar([i + w for i in x], [real[c] for c in grupo], w, color=VERMELHO, label="Urna (TSE)")
        ax.set_xticks(list(x), [nomes[c] for c in grupo])
        ax.set_ylabel("% dos votos válidos")
    axes[0].set_ylim(38, 49)
    axes[1].legend(frameon=False, loc="upper right")
    fig.suptitle(
        f"1º turno de 2026: MAE de {virg(mae_f)} p.p. do nosso modelo contra "
        f"{virg(mae_0)} da média simples das pesquisas",
        fontsize=11,
        x=0.01,
        ha="left",
    )
    fig.tight_layout()
    fig.savefig(IMG / "resultado_1t.png", bbox_inches="tight")
    plt.close(fig)


def figura_2t() -> None:
    df = carregar_pesquisas_2026_2t()
    df["data"] = pd.to_datetime(df["data_divulgacao"])
    df["flavio"] = 100.0 - df["pct_pt_validos"]
    prev = ler_planilha(OUTPUTS_DIR / "previsao_2026_2t.xlsx")["Flávio Bolsonaro"]

    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.scatter(df["data"], df["flavio"], s=22, color=CINZA, label="Pesquisas (votos válidos)")
    ax.axhline(prev, color=AZUL, lw=2, label=f"Nossa previsão: {virg(prev, 1)}%")
    ax.axhline(50, color=VERMELHO, lw=1, ls=":", label="50%")
    ax.set_ylabel("Flávio, % dos válidos")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d/%m"))
    ax.set_title("2º turno de 2026: pesquisas e previsão", loc="left", fontsize=11)
    fig.tight_layout()
    fig.savefig(IMG / "pesquisas_2t.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    IMG.mkdir(parents=True, exist_ok=True)
    figura_1t()
    figura_2t()
    print(f"OK: figuras em {IMG}")
