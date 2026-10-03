"""Gera docs/tabela_pesquisas_2026.tex a partir de data/manual/pesquisas_2026.csv.

Mostra as pesquisas de 2026 usadas na previsao, em votos totais, como divulgadas.
Uso: python scripts/gerar_tabela_pesquisas_tex.py
"""
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "data" / "manual" / "pesquisas_2026.csv"
SAIDA = RAIZ / "docs" / "tabela_pesquisas_2026.tex"


def fmt(x) -> str:
    if pd.isna(x):
        return "--"
    s = f"{float(x):.1f}".replace(".", ",")
    return s[:-2] if s.endswith(",0") else s


def main() -> None:
    df = pd.read_csv(CSV).sort_values(["data_divulgacao", "instituto"])
    linhas = []
    for _, r in df.iterrows():
        campo = (pd.to_datetime(r["data_inicio_campo"]).strftime("%d/%m") + " a "
                 + pd.to_datetime(r["data_fim_campo"]).strftime("%d/%m"))
        linhas.append(
            f"{r['instituto']} & {r['registro_tse']} & {campo} & {int(r['amostra']):,}".replace(",", ".")
            + f" & {fmt(r['Luiz Inácio Lula da Silva'])} & {fmt(r['Flávio Bolsonaro'])}"
            + f" & {fmt(r['Augusto Cury'])} & {fmt(r['Ronaldo Caiado'])} & {fmt(r['Renan Santos'])}"
            + f" & {fmt(r['Romeu Zema'])} & {fmt(r['brancos_nulos'])} & {fmt(r['indecisos'])} \\\\"
        )
    SAIDA.write_text("% Gerado por scripts/gerar_tabela_pesquisas_tex.py. Nao editar a mao.\n"
                     + "\n".join(linhas) + "\n", encoding="utf-8")
    print(f"OK: {SAIDA} ({len(linhas)} pesquisas)")


if __name__ == "__main__":
    main()
