"""
scripts/gerar_numeros_latex_2t.py
Gera docs/2t/numeros_2t.tex (macros), as tabelas e os dados das figuras da nota
metodologica do 2o turno a partir do mesmo pipeline de scripts/executar_backtest_2t.py.
Nada na nota e digitado a mao: para atualizar, rodar este script e recompilar.

Uso:
    python scripts/gerar_numeros_latex_2t.py --corte "sábado, 24/10/2026, às 20h00" --status "final"
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import executar_backtest_2t as E  # noqa: E402

from src.backtest import padronizar_nome_instituto  # noqa: E402
from src.backtest_2t import (  # noqa: E402
    TSE_1T_TOP2,
    carregar_pesquisas_2t_historicas,
    carregar_pesquisas_2026_2t,
    obter_semi_erros_margem_1t,
)
from src.config import PROCESSED_DIR  # noqa: E402

OUT = ROOT / "docs" / "2t"
INICIO_JANELA = date(2026, 10, 5)


def f(x: float, c: int = 1) -> str:
    return f"{x:.{c}f}".replace(".", ",")


def fs(x: float, c: int = 2) -> str:
    s = f(abs(x), c)
    return ("$-$" if x < 0 else "+") + s


def macro(nome: str, valor: str) -> str:
    return f"\\newcommand{{\\{nome}}}{{{valor}}}\n"


def linha_e1(df, nome, rotulo, decisao):
    r = df[df["modelo"] == nome].iloc[0]
    d = "" if nome == "M0_2T" else f"{fs(-r['delta_vs_m0'])} / {f(r['se_delta'], 2)}"
    return (
        f"{rotulo} & {f(r['2014'], 2)} & {f(r['2018'], 2)} & {f(r['2022'], 2)} & "
        f"{f(r['mae_medio'], 2)} & {d} & {decisao} \\\\\n"
    )


def linha_e2(df, nome, rotulo):
    r = df[df["ajuste"] == nome].iloc[0]
    if r["delta_vs_base"] < -r["se_delta"]:
        dec = "aprovado"
    elif abs(r["delta_vs_base"]) <= r["se_delta"]:
        dec = "empate: fica a base"
    else:
        dec = "piora"
    return (
        f"{rotulo} & {f(r['2014'], 2)} & {f(r['2018'], 2)} & {f(r['2022'], 2)} & "
        f"{f(r['mae_medio'], 2)} & {fs(-r['delta_vs_base'])} / {f(r['se_delta'], 2)} & {dec} \\\\\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corte", default="sábado, 24/10/2026, às 20h00")
    ap.add_argument("--status", default="preliminar")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        df_e1, preds_all, venc = E.rodar_etapa_1_aba1()
        df_e2, modo_b, param_b = E.rodar_etapa_2_aba1(venc, preds_all)
        df_loeo = E.rodar_loeo_2t(preds_all)
        venc_a2, tab_a2 = E.rodar_backtest_aba2_2t()
        df_taus, df_gov = E.calcular_tabela_taus_e_gov2t()
        df_sens, prev_cand, prev_ad, det_a2, nome_final = E.projetar_2026_2t(
            venc, df_e2, modo_b, param_b, venc_a2, df_taus
        )

    from src.arredondamento import maiores_restos

    fl, lu = maiores_restos(
        [prev_cand["Flávio Bolsonaro"], prev_cand["Luiz Inácio Lula da Silva"]],
        total=100.0,
        casas=1,
    )

    # ---------- pesquisas de 2026 e pesos do M2 ----------
    df26 = carregar_pesquisas_2026_2t()
    df26["inst"] = df26["instituto"].apply(padronizar_nome_instituto)
    df26["flavio_val"] = 100.0 - df26["pct_pt_validos"]
    df26["dia"] = (pd.to_datetime(df26["data_divulgacao"]) - pd.Timestamp(INICIO_JANELA)).dt.days
    ultima = df26.sort_values("data_divulgacao", ascending=False).drop_duplicates("inst")
    erros_1t = obter_semi_erros_margem_1t(2026)
    med = float(np.median([abs(v) for v in erros_1t.values()]))
    sigma0 = param_b if modo_b == "M2_2T" else 1.5
    ultima["e1t"] = ultima["inst"].map(erros_1t)
    ultima["tem_1t"] = ultima["e1t"].notna()
    ultima["peso"] = 1.0 / (ultima["e1t"].fillna(med) ** 2 + sigma0**2)
    ultima["peso_rel"] = ultima["peso"] / ultima["peso"].sum() * 100.0
    ultima = ultima.sort_values("peso_rel")

    with open(OUT / "pesquisas_2026_2t.dat", "w", encoding="utf-8") as fh:
        fh.write("dia flavio\n")
        for _, r in df26.iterrows():
            fh.write(f"{int(r['dia'])} {r['flavio_val']:.2f}\n")

    rotulos = [str(i).replace("&", "\\&") for i in ultima["inst"]]
    with open(OUT / "pesos_2026.dat", "w", encoding="utf-8") as fh:
        fh.write("y peso tem1t\n")
        for k, (_, r) in enumerate(ultima.iterrows()):
            fh.write(f"{k} {r['peso_rel']:.2f} {int(r['tem_1t'])}\n")

    # ---------- macros ----------
    tse26 = json.loads((PROCESSED_DIR / "tse_2026_1t_oficial.json").read_text(encoding="utf-8"))
    lula1t, flav1t = TSE_1T_TOP2[2026]
    terc1t = 100.0 - lula1t - flav1t
    tau_med = float(df_taus["tau_pt"].median())
    tau_mean = float(df_taus["tau_pt"].mean())
    flav_impl = 100.0 - prev_cand["Luiz Inácio Lula da Silva"]
    tau_impl_flav = (flav_impl - flav1t) / terc1t
    hist = carregar_pesquisas_2t_historicas()
    r_venc = df_e1[df_e1["modelo"] == venc].iloc[0]
    r_m0 = df_e1[df_e1["modelo"] == "M0_2T"].iloc[0]
    loeo = df_loeo.set_index("modelo")["mae_loeo"]
    sens = df_sens.set_index("Especificação")

    def sens_flav(chave: str) -> str:
        linhas = [k for k in sens.index if k.startswith(chave)]
        return f(float(sens.loc[linhas[0], "Flávio Bolsonaro (Contínuo %)"]), 1) if linhas else "--"

    sens_alt = df_sens[~df_sens["Especificação"].str.startswith(">>>")]
    col_fl = "Flávio Bolsonaro (Contínuo %)"
    sens_min = float(sens_alt[col_fl].min())
    sens_max = float(sens_alt[col_fl].max())
    g26 = df_gov[df_gov["eleicao"] == "2026"].iloc[0]
    ghist = df_gov[df_gov["eleicao"] != "2026"]

    m = ""
    m += macro("horacorte", args.corte)
    m += macro("statusprevisao", args.status)
    m += macro("pFlavio", f(fl))
    m += macro("pLula", f(lu))
    m += macro("pAbst", f(prev_ad["abstencao"]))
    m += macro("pBrancos", f(prev_ad["brancos"]))
    m += macro("pNulos", f(prev_ad["nulos"]))
    m += macro("nPesq", str(len(df26)))
    m += macro("nInst", str(df26["inst"].nunique()))
    m += macro("nInstUmT", str(int(ultima["tem_1t"].sum())))
    m += macro("nHist", str(len(hist)))
    m += macro("dataUltimaPesq", pd.to_datetime(df26["data_divulgacao"]).max().strftime("%d/%m"))
    m += macro("sigmaZero", f(sigma0))
    m += macro("medErroUmT", f(med, 2))
    m += macro("maeVenc", f(r_venc["mae_medio"], 2))
    m += macro("maeMZero", f(r_m0["mae_medio"], 2))
    m += macro("deltaVenc", f(-r_venc["delta_vs_m0"], 2))
    m += macro("seVenc", f(r_venc["se_delta"], 2))
    m += macro("loeoVenc", f(float(loeo[venc]), 2))
    m += macro("loeoMZero", f(float(loeo["M0_2T"]), 2))
    m += macro("lulaUmT", f(lula1t, 2))
    m += macro("flavioUmT", f(flav1t, 2))
    m += macro("tercUmT", f(terc1t, 2))
    m += macro("flavioDoisCand", f(flav1t / (flav1t + lula1t) * 100.0, 1))
    m += macro("tauMediana", f(tau_med, 2))
    m += macro("tauMedia", f(tau_mean, 2))
    m += macro("tauImplFlavio", f(tau_impl_flav * 100.0, 0))
    m += macro("tauImplLula", f((1.0 - tau_impl_flav) * 100.0, 0))
    m += macro("priorMedianaFlavio", sens_flav("Prior transferência com tau mediano"))
    m += macro("priorMediaFlavio", sens_flav("Prior transferência com tau médio"))
    m += macro("sensMZero", sens_flav("M0_2T (Média"))
    m += macro("sensMUm", sens_flav("M1_2T (h=3"))
    m += macro("sensPersist", sens_flav("M2_2T (sigma0=1.5) + Persistência 1T (rho_OLS"))
    m += macro("sensMin", f(sens_min, 1))
    m += macro("sensMax", f(sens_max, 1))
    m += macro("nSens", str(len(sens_alt)))
    m += macro("abstUmT", f(tse26["abstencao_pct"], 2))
    m += macro("brancosUmT", f(tse26["brancos_pct"], 2))
    m += macro("nulosUmT", f(tse26["nulos_pct"], 2))
    m += macro("govShareVinteSeis", f(g26["share_com_gov2t_pct"], 1))
    m += macro("govNVinteSeis", str(int(g26["n_ufs_gov2t"])))
    m += macro("govShareHist", f(ghist["share_com_gov2t_pct"].mean(), 1))
    m += macro("deltaAbstCom", f(ghist["delta_abst_com_gov2t"].mean(), 2))
    m += macro("deltaAbstSem", f(ghist["delta_abst_sem_gov2t"].mean(), 2))
    m += macro("pesoMax", f(ultima["peso_rel"].max(), 1))
    m += macro("instPesoMax", str(ultima.iloc[-1]["inst"]))
    m += macro("pesoMin", f(ultima["peso_rel"].min(), 1))
    m += macro("instPesoMin", str(ultima.iloc[0]["inst"]))
    m += macro("rotulosPesos", ",".join("{" + r + "}" for r in rotulos))
    m += macro("nPesos", str(len(rotulos) - 1))
    (OUT / "numeros_2t.tex").write_text(
        "% Gerado por scripts/gerar_numeros_latex_2t.py. NAO editar a mao.\n" + m, encoding="utf-8"
    )

    # ---------- Tabela 1: modelos e ajustes ----------
    melhor_m1 = (
        df_e1[df_e1["modelo"].str.startswith("M1")].sort_values("mae_medio").iloc[0]["modelo"]
    )
    outro_m2 = [x for x in df_e1["modelo"] if x.startswith("M2") and x != venc][0]
    t1 = "\\begin{tabular}{lcccccl}\n\\toprule\n"
    t1 += (
        "\\textbf{Etapa 1: agregador} & \\textbf{2014} & \\textbf{2018} & \\textbf{2022} & "
        "\\textbf{Média} & \\textbf{$\\bar\\Delta$ / EP} & \\textbf{Decisão} \\\\\n\\midrule\n"
    )

    def dec_e1(nome):
        if nome == venc:
            return "\\textbf{escolhido}"
        if nome == "M0_2T":
            return "referência"
        r = df_e1[df_e1["modelo"] == nome].iloc[0]
        return "não supera M0" if not r["supera_m0_1se"] else "supera, MAE maior"

    def rot_e1(nome):
        if nome == "M0_2T":
            return "M0 média simples"
        par = nome.split("(")[1].rstrip(")").replace("sigma0", "$\\sigma_0$").replace("h=", "$h$=")
        par = par.replace(".", ",")
        return (
            (
                "M1 recência e amostra ("
                if nome.startswith("M1")
                else "M2 peso pelo erro no 1º turno ("
            )
            + par
            + ")"
        )

    for nome in ["M0_2T", melhor_m1, venc, outro_m2]:
        t1 += linha_e1(df_e1, nome, rot_e1(nome), dec_e1(nome))
    t1 += "\\midrule\n\\textbf{Etapa 2: ajustes sobre o M2} & & & & & & \\\\\n\\midrule\n"
    t1 += linha_e2(
        df_e2,
        "+ Persistência 1T (rho=OLS_treino)",
        "+ correção pelo erro do 1º turno ($\\hat\\rho$ MQO)",
    )
    t1 += linha_e2(
        df_e2, "+ Persistência 1T (rho=0.20)", "+ correção pelo erro do 1º turno ($\\rho=0{,}2$)"
    )
    t1 += linha_e2(
        df_e2, "+ Viés Comum 2T (k_mu=3)", "+ viés comum histórico do 2º turno ($k_\\mu=3$)"
    )
    nome_prior = [x for x in df_e2["ajuste"] if "tau mediano" in x and "0.10" in x][0]
    t1 += linha_e2(df_e2, nome_prior, "+ 10\\% do prior de transferência ($\\tilde\\tau$)")
    t1 += "\\bottomrule\n\\end{tabular}\n"
    (OUT / "tab_modelos.tex").write_text(t1, encoding="utf-8")

    # ---------- Tabela 2: transferencia ----------
    t2 = "\\begin{tabular}{l" + "c" * len(df_taus) + "c}\n\\toprule\n"
    t2 += (
        " & "
        + " & ".join(str(int(a)) for a in df_taus["eleicao"])
        + " & \\textbf{2026} \\\\\n\\midrule\n"
    )
    t2 += (
        "PT no 1º turno & " + " & ".join(f(v) for v in df_taus["pt_1t"]) + f" & {f(lula1t)} \\\\\n"
    )
    t2 += (
        "Demais candidatos no 1º turno & "
        + " & ".join(f(v) for v in df_taus["terceiros_1t"])
        + f" & {f(terc1t)} \\\\\n"
    )
    t2 += "PT no 2º turno & " + " & ".join(f(v) for v in df_taus["pt_2t"]) + " & ? \\\\\n"
    t2 += (
        "$\\tau$ (fração capturada pelo PT) & "
        + " & ".join(f(v, 2) for v in df_taus["tau_pt"])
        + f" & $\\tilde\\tau={f(tau_med, 2)}$ \\\\\n"
    )
    t2 += "\\bottomrule\n\\end{tabular}\n"
    (OUT / "tab_transferencia.tex").write_text(t2, encoding="utf-8")

    # ---------- Tabela 3: Aba 2 ----------
    nomes = {
        "Zero_Delta (y2=y1)": "Repetir o 1º turno",
        "Persistencia_Delta": "1º turno + variação da eleição anterior",
        "Media_Delta": "1º turno + variação média",
        "Ratio_Media": "1º turno $\\times$ razão média 2T/1T",
        "BottomUp_UF_Gov2T": "Por UF, com e sem 2º turno estadual",
    }
    t3 = "\\begin{tabular}{lccc}\n\\toprule\n"
    t3 += "\\textbf{Método} & \\textbf{Abstenção} & \\textbf{Brancos} & \\textbf{Nulos} \\\\\n\\midrule\n"
    for met, rot in nomes.items():
        cel = []
        for var in ["abstencao", "brancos", "nulos"]:
            tb = tab_a2[var]
            sub = tb[tb["metodo"] == met]
            if sub.empty:
                cel.append("n.a.")
                continue
            v = f(float(sub.iloc[0]["mae_medio"]), 2)
            cel.append(f"\\textbf{{{v}}}" if venc_a2[var] == met else v)
        t3 += f"{rot} & " + " & ".join(cel) + " \\\\\n"
    t3 += "\\midrule\n"
    t3 += (
        f"1º turno de 2026 (TSE) & {f(tse26['abstencao_pct'], 2)} & {f(tse26['brancos_pct'], 2)} & "
        f"{f(tse26['nulos_pct'], 2)} \\\\\n"
    )
    t3 += (
        f"\\textbf{{Previsão para o 2º turno}} & \\textbf{{{f(prev_ad['abstencao'])}}} & "
        f"\\textbf{{{f(prev_ad['brancos'])}}} & \\textbf{{{f(prev_ad['nulos'])}}} \\\\\n"
    )
    t3 += "\\bottomrule\n\\end{tabular}\n"
    (OUT / "tab_aba2.tex").write_text(t3, encoding="utf-8")

    print(
        f"OK: {OUT}/numeros_2t.tex | Flávio {f(fl)} Lula {f(lu)} | "
        f"Abst {f(prev_ad['abstencao'])} Br {f(prev_ad['brancos'])} Nu {f(prev_ad['nulos'])}"
    )


if __name__ == "__main__":
    main()
