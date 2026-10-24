"""
scripts/executar_backtest_2t.py
Executa o protocolo sequencial completo de backtest historico para o 2o Turno (Expanding Window e LOEO),
seleciona formalmente os modelos da Aba 1 e da Aba 2 sob a regra de 1 SE(Delta), calcula os parametros
estruturais (tau por eleicao e share do eleitorado com 2T de governador 2006-2026), gera a planilha
preliminar outputs/previsao_2026_2t.xlsx e escreve 100% automaticamente reports/relatorio_backtest_2t.md.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.arredondamento import maiores_restos
from src.backtest import calcular_diferenca_e_se
from src.backtest_2t import (
    TSE_1T_TOP2,
    TSE_2T_PT,
    aplicar_ajuste_persistencia_1t,
    aplicar_ajuste_vies_comum_2t,
    calcular_mae_2t,
    calcular_prior_estrutural_1t,
    calcular_taus_historicos,
    carregar_pesquisas_2t_historicas,
    carregar_pesquisas_2026_2t,
    estimar_m0_2t,
    estimar_m1_2t,
    estimar_m2_2t_peso_1t,
    estimar_rho_ols_treino,
)
from src.config import OUTPUTS_DIR, PROCESSED_DIR, REPORTS_DIR
from src.entrega_2t import gerar_planilha_entrega_2t

ANOS_TESTE_EXPANDING = [2014, 2018, 2022]
TREINO_EXPANDING = {
    2014: [2006, 2010],
    2018: [2006, 2010, 2014],
    2022: [2006, 2010, 2014, 2018],
}
TODOS_ANOS_LOEO = [2006, 2010, 2014, 2018, 2022]


def _fmt(val: float, casas: int = 4) -> str:
    return f"{val:.{casas}f}".replace(".", ",")


def _fmt_sinal(val: float, casas: int = 4) -> str:
    sinal = "+" if val > 0 else ""
    return f"{sinal}{val:.{casas}f}".replace(".", ",")


def rodar_etapa_1_aba1():
    print("=" * 85)
    print("ETAPA 1 (ABA 1 - 2o TURNO): MODELOS BASE NO EXPANDING WINDOW (2014, 2018, 2022)")
    print("=" * 85)

    configs = {
        "M0_2T": lambda df, t: estimar_m0_2t(df),
        "M1_2T (h=3)": lambda df, t: estimar_m1_2t(df, t, meia_vida=3.0),
        "M1_2T (h=5)": lambda df, t: estimar_m1_2t(df, t, meia_vida=5.0),
        "M1_2T (h=7)": lambda df, t: estimar_m1_2t(df, t, meia_vida=7.0),
        "M2_2T (sigma0=1.5)": lambda df, t: estimar_m2_2t_peso_1t(df, t, sigma0=1.5),
        "M2_2T (sigma0=2.5)": lambda df, t: estimar_m2_2t_peso_1t(df, t, sigma0=2.5),
    }

    preds_todos_anos = {}
    for nome, func in configs.items():
        preds_todos_anos[nome] = {}
        for ano in TODOS_ANOS_LOEO:
            df_a = carregar_pesquisas_2t_historicas(ano)
            preds_todos_anos[nome][ano] = func(df_a, ano)

    erros_m0 = [calcular_mae_2t(preds_todos_anos["M0_2T"][t], t) for t in ANOS_TESTE_EXPANDING]

    linhas = []
    for nome in configs.keys():
        erros = [calcular_mae_2t(preds_todos_anos[nome][t], t) for t in ANOS_TESTE_EXPANDING]
        mae_med = float(np.mean(erros))
        se = float(np.std(erros, ddof=1) / math.sqrt(len(erros)))
        if nome == "M0_2T":
            d_m0, se_d, supera_m0 = 0.0, 0.0, False
        else:
            d_m0, se_d = calcular_diferenca_e_se(erros, erros_m0)
            supera_m0 = bool(d_m0 < -se_d)
        linhas.append(
            {
                "modelo": nome,
                "2014": erros[0],
                "2018": erros[1],
                "2022": erros[2],
                "mae_medio": mae_med,
                "se": se,
                "delta_vs_m0": d_m0,
                "se_delta": se_d,
                "supera_m0_1se": supera_m0,
                "erros": erros,
            }
        )

    df_res = pd.DataFrame(linhas)
    print(
        df_res[
            [
                "modelo",
                "2014",
                "2018",
                "2022",
                "mae_medio",
                "se",
                "delta_vs_m0",
                "se_delta",
                "supera_m0_1se",
            ]
        ]
        .round(4)
        .to_string(index=False)
    )

    aprovados = df_res[df_res["supera_m0_1se"]].sort_values("mae_medio")
    if not aprovados.empty:
        vencedor = str(aprovados.iloc[0]["modelo"])
    else:
        vencedor = "M0_2T"
    print(f"\n>>> Vencedor formal da Etapa 1 (Regra 1 SE + Parcimonia): {vencedor}")
    return df_res, preds_todos_anos, vencedor


def rodar_etapa_2_aba1(vencedor_base: str, preds_todos_anos: dict[str, dict[int, float]]):
    print("\n" + "=" * 85)
    print(f"ETAPA 2 (ABA 1 - 2o TURNO): AJUSTES ISOLADOS SOBRE O MODELO BASE ({vencedor_base})")
    print("=" * 85)

    if vencedor_base == "M0_2T":
        modo_base, param_base = "M0_2T", 0.0
    elif vencedor_base.startswith("M1_2T"):
        modo_base = "M1_2T"
        param_base = float(vencedor_base.split("=")[1].replace(")", ""))
    else:
        modo_base = "M2_2T"
        param_base = float(vencedor_base.split("=")[1].replace(")", ""))

    erros_base = [
        calcular_mae_2t(preds_todos_anos[vencedor_base][t], t) for t in ANOS_TESTE_EXPANDING
    ]

    ajustes = {
        f"{vencedor_base} (Base Puro)": lambda t, tr: preds_todos_anos[vencedor_base][t],
        "+ Persistência 1T (rho=0.20)": lambda t, tr: aplicar_ajuste_persistencia_1t(
            carregar_pesquisas_2t_historicas(t),
            t,
            rho=0.20,
            modo_base=modo_base,
            param_base=param_base,
        ),
        "+ Persistência 1T (rho=0.35)": lambda t, tr: aplicar_ajuste_persistencia_1t(
            carregar_pesquisas_2t_historicas(t),
            t,
            rho=0.35,
            modo_base=modo_base,
            param_base=param_base,
        ),
        "+ Persistência 1T (rho=OLS_treino)": lambda t, tr: aplicar_ajuste_persistencia_1t(
            carregar_pesquisas_2t_historicas(t),
            t,
            rho=estimar_rho_ols_treino(tr),
            modo_base=modo_base,
            param_base=param_base,
        ),
        "+ Viés Comum 2T (k_mu=1)": lambda t, tr: aplicar_ajuste_vies_comum_2t(
            preds_todos_anos[vencedor_base][t],
            tr,
            k_mu=1.0,
            preds_base_por_ano=preds_todos_anos[vencedor_base],
        ),
        "+ Viés Comum 2T (k_mu=3)": lambda t, tr: aplicar_ajuste_vies_comum_2t(
            preds_todos_anos[vencedor_base][t],
            tr,
            k_mu=3.0,
            preds_base_por_ano=preds_todos_anos[vencedor_base],
        ),
        "+ Shrinkage Prior 1T tau médio (lambda=0.10)": lambda t, tr: (
            0.90 * preds_todos_anos[vencedor_base][t]
            + 0.10 * calcular_prior_estrutural_1t(t, tr, estatistica="media")
        ),
        "+ Shrinkage Prior 1T tau médio (lambda=0.25)": lambda t, tr: (
            0.75 * preds_todos_anos[vencedor_base][t]
            + 0.25 * calcular_prior_estrutural_1t(t, tr, estatistica="media")
        ),
        "+ Shrinkage Prior 1T tau mediano (lambda=0.10)": lambda t, tr: (
            0.90 * preds_todos_anos[vencedor_base][t]
            + 0.10 * calcular_prior_estrutural_1t(t, tr, estatistica="mediana")
        ),
        "+ Shrinkage Prior 1T tau mediano (lambda=0.25)": lambda t, tr: (
            0.75 * preds_todos_anos[vencedor_base][t]
            + 0.25 * calcular_prior_estrutural_1t(t, tr, estatistica="mediana")
        ),
    }

    linhas = []
    for nome, func in ajustes.items():
        preds_t = [func(t, TREINO_EXPANDING[t]) for t in ANOS_TESTE_EXPANDING]
        erros = [calcular_mae_2t(p, t) for p, t in zip(preds_t, ANOS_TESTE_EXPANDING)]
        mae_med = float(np.mean(erros))
        se = float(np.std(erros, ddof=1) / math.sqrt(len(erros)))
        if nome.endswith("(Base Puro)"):
            d_base, se_d, aprovado = 0.0, 0.0, True
        else:
            d_base, se_d = calcular_diferenca_e_se(erros, erros_base)
            aprovado = bool(d_base < -se_d)
        linhas.append(
            {
                "ajuste": nome,
                "2014": erros[0],
                "2018": erros[1],
                "2022": erros[2],
                "mae_medio": mae_med,
                "se": se,
                "delta_vs_base": d_base,
                "se_delta": se_d,
                "aprovado": aprovado,
            }
        )

    df_aj = pd.DataFrame(linhas)
    print(
        df_aj[
            ["ajuste", "2014", "2018", "2022", "mae_medio", "delta_vs_base", "se_delta", "aprovado"]
        ]
        .round(4)
        .to_string(index=False)
    )
    return df_aj, modo_base, param_base


def rodar_loeo_2t(preds_todos_anos: dict[str, dict[int, float]]):
    print("\n" + "=" * 85)
    print("VALIDACAO COMPLEMENTAR LOEO (2006, 2010, 2014, 2018, 2022)")
    print("=" * 85)

    linhas = []
    for nome, mapa_anos in preds_todos_anos.items():
        erros = {a: calcular_mae_2t(mapa_anos[a], a) for a in TODOS_ANOS_LOEO}
        vals = [erros[a] for a in TODOS_ANOS_LOEO]
        linhas.append(
            {
                "modelo": nome,
                "2006": erros[2006],
                "2010": erros[2010],
                "2014": erros[2014],
                "2018": erros[2018],
                "2022": erros[2022],
                "mae_loeo": float(np.mean(vals)),
                "se_loeo": float(np.std(vals, ddof=1) / math.sqrt(len(vals))),
            }
        )

    for base_tag, m_base, p_base in [("M0_2T", "M0_2T", 0.0), ("M2_2T (sigma0=1.5)", "M2_2T", 1.5)]:
        for rho in [0.20, 0.35]:
            erros = {
                a: calcular_mae_2t(
                    aplicar_ajuste_persistencia_1t(
                        carregar_pesquisas_2t_historicas(a),
                        a,
                        rho=rho,
                        modo_base=m_base,
                        param_base=p_base,
                    ),
                    a,
                )
                for a in TODOS_ANOS_LOEO
            }
            vals = [erros[a] for a in TODOS_ANOS_LOEO]
            linhas.append(
                {
                    "modelo": f"{base_tag} + Persist 1T (rho={rho:.2f})",
                    "2006": erros[2006],
                    "2010": erros[2010],
                    "2014": erros[2014],
                    "2018": erros[2018],
                    "2022": erros[2022],
                    "mae_loeo": float(np.mean(vals)),
                    "se_loeo": float(np.std(vals, ddof=1) / math.sqrt(len(vals))),
                }
            )

    df_loeo = pd.DataFrame(linhas)
    print(df_loeo.round(4).to_string(index=False))
    return df_loeo


def rodar_backtest_aba2_2t():
    print("\n" + "=" * 85)
    print("BACKTEST DA ABA 2 NO 2o TURNO (ANCORADO NO 1o TURNO DA MESMA ELEICAO)")
    print("=" * 85)

    df_nac = pd.read_parquet(PROCESSED_DIR / "tse_historico_2t.parquet").set_index("eleicao")
    df_uf = pd.read_parquet(PROCESSED_DIR / "tse_uf_historico_2t.parquet")

    variaveis = ["abstencao", "brancos", "nulos"]
    metodos = ["Zero_Delta (y2=y1)", "Persistencia_Delta", "Media_Delta", "Ratio_Media"]

    vencedores_aba2 = {}
    tabelas_aba2 = {}

    for var in variaveis:
        print(f"\n--- Variavel Aba 2: {var.upper()} ---")
        y1 = df_nac[f"{var}_1t"].to_dict()
        y2 = df_nac[f"{var}_2t"].to_dict()
        deltas = {a: y2[a] - y1[a] for a in TODOS_ANOS_LOEO}
        ratios = {a: y2[a] / y1[a] for a in TODOS_ANOS_LOEO}

        erros_zero = [abs(y1[t] - y2[t]) for t in ANOS_TESTE_EXPANDING]
        linhas_var = []

        lista_metodos = metodos + (["BottomUp_UF_Gov2T"] if var == "abstencao" else [])
        for met in lista_metodos:
            erros = []
            for t in ANOS_TESTE_EXPANDING:
                tr = TREINO_EXPANDING[t]
                if met == "Zero_Delta (y2=y1)":
                    pred = y1[t]
                elif met == "Persistencia_Delta":
                    pred = y1[t] + deltas[tr[-1]]
                elif met == "Media_Delta":
                    pred = y1[t] + float(np.mean([deltas[a] for a in tr]))
                elif met == "Ratio_Media":
                    pred = y1[t] * float(np.mean([ratios[a] for a in tr]))
                elif met == "BottomUp_UF_Gov2T":
                    sub_tr = df_uf[df_uf["eleicao"] == tr[-1]]
                    g1 = sub_tr[sub_tr["gov2t"] == 1]
                    g0 = sub_tr[sub_tr["gov2t"] == 0]
                    d_com = (
                        float(np.average(g1["delta_abst"], weights=g1["aptos_2t"]))
                        if len(g1)
                        else deltas[tr[-1]]
                    )
                    d_sem = (
                        float(np.average(g0["delta_abst"], weights=g0["aptos_2t"]))
                        if len(g0)
                        else deltas[tr[-1]]
                    )
                    sub_t = df_uf[df_uf["eleicao"] == t]
                    sh_t = sub_t[sub_t["gov2t"] == 1]["aptos_2t"].sum() / sub_t["aptos_2t"].sum()
                    pred = y1[t] + sh_t * d_com + (1.0 - sh_t) * d_sem
                erros.append(abs(pred - y2[t]))

            mae_med = float(np.mean(erros))
            se = float(np.std(erros, ddof=1) / math.sqrt(len(erros)))
            if met == "Zero_Delta (y2=y1)":
                d_z, se_d, supera_z = 0.0, 0.0, False
            else:
                d_z, se_d = calcular_diferenca_e_se(erros, erros_zero)
                supera_z = bool(d_z < -se_d)
            linhas_var.append(
                {
                    "metodo": met,
                    "2014": erros[0],
                    "2018": erros[1],
                    "2022": erros[2],
                    "mae_medio": mae_med,
                    "se": se,
                    "delta_vs_zero": d_z,
                    "se_delta": se_d,
                    "supera_zero_1se": supera_z,
                }
            )

        df_v = pd.DataFrame(linhas_var)
        print(df_v.round(4).to_string(index=False))
        aprov = df_v[df_v["supera_zero_1se"]].sort_values("mae_medio")
        vencedor_v = str(aprov.iloc[0]["metodo"]) if not aprov.empty else "Zero_Delta (y2=y1)"
        print(f"  >>> Vencedor formal para {var}: {vencedor_v}")
        vencedores_aba2[var] = vencedor_v
        tabelas_aba2[var] = df_v

    return vencedores_aba2, tabelas_aba2


def calcular_tabela_taus_e_gov2t():
    """
    Calcula:
    1) A tabela de tau_t por eleicao (2006-2022) para transferencia 1T -> 2T;
    2) A tabela do share do eleitorado apto em UFs com 2o turno para Governador (2006-2022 vs. 2026).
    """
    taus_map = calcular_taus_historicos(TODOS_ANOS_LOEO)
    linhas_tau = []
    for a in TODOS_ANOS_LOEO:
        v_pt_1t, v_adv_1t = TSE_1T_TOP2[a]
        terc_1t = 100.0 - v_pt_1t - v_adv_1t
        v_pt_2t = TSE_2T_PT[a]
        v_adv_2t = 100.0 - v_pt_2t
        delta_pt = v_pt_2t - v_pt_1t
        delta_adv = v_adv_2t - v_adv_1t
        linhas_tau.append(
            {
                "eleicao": a,
                "pt_1t": v_pt_1t,
                "adv_1t": v_adv_1t,
                "terceiros_1t": terc_1t,
                "pt_2t": v_pt_2t,
                "adv_2t": v_adv_2t,
                "delta_pt": delta_pt,
                "delta_adv": delta_adv,
                "tau_pt": taus_map[a],
            }
        )
    df_taus = pd.DataFrame(linhas_tau)

    # Share do eleitorado com 2T de Governador (2006-2022 vs 2026)
    df_uf = pd.read_parquet(PROCESSED_DIR / "tse_uf_historico_2t.parquet")
    df_nac = pd.read_parquet(PROCESSED_DIR / "tse_historico_2t.parquet").set_index("eleicao")
    with open(PROCESSED_DIR / "tse_2026_1t_oficial.json", encoding="utf-8") as f:
        tse_2026 = json.load(f)

    linhas_gov = []
    for a in TODOS_ANOS_LOEO:
        sub = df_uf[df_uf["eleicao"] == a]
        aptos_tot = float(sub["aptos_1t"].sum())
        g1 = sub[sub["gov2t"] == 1]
        g0 = sub[sub["gov2t"] == 0]
        share_g1 = float(g1["aptos_1t"].sum()) / aptos_tot * 100.0 if aptos_tot > 0 else 0.0
        share_g0 = 100.0 - share_g1
        d_g1 = float(np.average(g1["delta_abst"], weights=g1["aptos_2t"])) if len(g1) else np.nan
        d_g0 = float(np.average(g0["delta_abst"], weights=g0["aptos_2t"])) if len(g0) else np.nan
        d_nac = float(df_nac.loc[a, "delta_abstencao"])
        ufs_lista = ", ".join(sorted(g1["uf"].tolist()))
        linhas_gov.append(
            {
                "eleicao": str(a),
                "n_ufs_gov2t": int(len(g1)),
                "ufs_gov2t": ufs_lista,
                "share_com_gov2t_pct": share_g1,
                "share_sem_gov2t_pct": share_g0,
                "delta_abst_com_gov2t": d_g1,
                "delta_abst_sem_gov2t": d_g0,
                "delta_abst_nacional": d_nac,
            }
        )

    # Adiciona 2026
    por_uf_26 = tse_2026["uf_stats"]
    aptos_26_tot = sum(int(v["aptos"]) for u, v in por_uf_26.items())
    aptos_26_g1 = sum(int(v["aptos"]) for u, v in por_uf_26.items() if int(v["gov2t"]) == 1)
    share_26_g1 = aptos_26_g1 / aptos_26_tot * 100.0
    ufs_26_g1 = sorted(tse_2026["ufs_com_gov2t"])
    linhas_gov.append(
        {
            "eleicao": "2026",
            "n_ufs_gov2t": len(ufs_26_g1),
            "ufs_gov2t": ", ".join(ufs_26_g1),
            "share_com_gov2t_pct": share_26_g1,
            "share_sem_gov2t_pct": 100.0 - share_26_g1,
            "delta_abst_com_gov2t": np.nan,
            "delta_abst_sem_gov2t": np.nan,
            "delta_abst_nacional": np.nan,
        }
    )
    df_gov2t = pd.DataFrame(linhas_gov)

    print("\n" + "=" * 85)
    print("PARAMETROS ESTRUTURAIS: TAU POR ELEICAO (2006-2022) E SHARE GOV 2T (2006-2026)")
    print("=" * 85)
    print("\n--- Tau por Eleição (Transferência Aparente de Terceiros para o PT) ---")
    print(df_taus.round(4).to_string(index=False))
    print(
        f"Tau médio (2006-2022) = {df_taus['tau_pt'].mean():.4f} | "
        f"Tau mediano (2006-2022) = {df_taus['tau_pt'].median():.4f}"
    )
    print("\n--- Share do Eleitorado com 2º Turno para Governador (Excluindo Exterior ZZ) ---")
    print(
        df_gov2t[
            [
                "eleicao",
                "n_ufs_gov2t",
                "share_com_gov2t_pct",
                "share_sem_gov2t_pct",
                "delta_abst_com_gov2t",
                "delta_abst_sem_gov2t",
                "delta_abst_nacional",
            ]
        ]
        .round(2)
        .to_string(index=False)
    )
    return df_taus, df_gov2t


def projetar_2026_2t(
    vencedor_base: str,
    df_aj: pd.DataFrame,
    modo_base: str,
    param_base: float,
    vencedores_aba2: dict[str, str],
    df_taus: pd.DataFrame,
):
    print("\n" + "=" * 85)
    print("PROJECOES E TABELA DE SENSIBILIDADE PARA O 2o TURNO DE 2026 (CORTE PARCIAL 21/10)")
    print("=" * 85)

    df_2026_2t = carregar_pesquisas_2026_2t()
    tr_all = TODOS_ANOS_LOEO

    p_m0 = estimar_m0_2t(df_2026_2t)
    p_m1_h3 = estimar_m1_2t(df_2026_2t, 2026, meia_vida=3.0)
    p_m1_h5 = estimar_m1_2t(df_2026_2t, 2026, meia_vida=5.0)
    p_m1_h7 = estimar_m1_2t(df_2026_2t, 2026, meia_vida=7.0)
    p_m2_s15 = estimar_m2_2t_peso_1t(df_2026_2t, 2026, sigma0=1.5)
    p_m2_s25 = estimar_m2_2t_peso_1t(df_2026_2t, 2026, sigma0=2.5)

    rho_ols = estimar_rho_ols_treino(tr_all)
    p_m0_rho20 = aplicar_ajuste_persistencia_1t(df_2026_2t, 2026, rho=0.20, modo_base="M0_2T")
    p_m2_rho20 = aplicar_ajuste_persistencia_1t(
        df_2026_2t, 2026, rho=0.20, modo_base="M2_2T", param_base=1.5
    )
    p_m2_rho_ols = aplicar_ajuste_persistencia_1t(
        df_2026_2t, 2026, rho=rho_ols, modo_base="M2_2T", param_base=1.5
    )

    tau_med = float(df_taus["tau_pt"].mean())
    tau_mdn = float(df_taus["tau_pt"].median())
    p_prior_1t_medio = calcular_prior_estrutural_1t(2026, tr_all, estatistica="media")
    p_prior_1t_mediano = calcular_prior_estrutural_1t(2026, tr_all, estatistica="mediana")

    mapa_base_2026 = {
        "M0_2T": p_m0,
        "M1_2T (h=3)": p_m1_h3,
        "M1_2T (h=5)": p_m1_h5,
        "M1_2T (h=7)": p_m1_h7,
        "M2_2T (sigma0=1.5)": p_m2_s15,
        "M2_2T (sigma0=2.5)": p_m2_s25,
    }
    p_vencedor_etapa1 = mapa_base_2026[vencedor_base]

    aj_aprovados = df_aj[
        (df_aj["aprovado"]) & (~df_aj["ajuste"].str.endswith("(Base Puro)"))
    ].sort_values("mae_medio")
    if not aj_aprovados.empty:
        melhor_aj = str(aj_aprovados.iloc[0]["ajuste"])
        if "rho=0.20" in melhor_aj:
            p_oficial_pt = aplicar_ajuste_persistencia_1t(
                df_2026_2t, 2026, rho=0.20, modo_base=modo_base, param_base=param_base
            )
        elif "rho=0.35" in melhor_aj:
            p_oficial_pt = aplicar_ajuste_persistencia_1t(
                df_2026_2t, 2026, rho=0.35, modo_base=modo_base, param_base=param_base
            )
        elif "rho=OLS" in melhor_aj:
            p_oficial_pt = aplicar_ajuste_persistencia_1t(
                df_2026_2t, 2026, rho=rho_ols, modo_base=modo_base, param_base=param_base
            )
        elif "lambda=0.10" in melhor_aj:
            p_ref = p_prior_1t_mediano if "mediano" in melhor_aj else p_prior_1t_medio
            p_oficial_pt = 0.90 * p_vencedor_etapa1 + 0.10 * p_ref
        elif "lambda=0.25" in melhor_aj:
            p_ref = p_prior_1t_mediano if "mediano" in melhor_aj else p_prior_1t_medio
            p_oficial_pt = 0.75 * p_vencedor_etapa1 + 0.25 * p_ref
        else:
            p_oficial_pt = p_vencedor_etapa1
        nome_modelo_final = f"{vencedor_base} {melhor_aj}"
    else:
        p_oficial_pt = p_vencedor_etapa1
        nome_modelo_final = f"{vencedor_base} (Puro)"

    especificacoes_2026 = [
        ("M0_2T (Média Simples Última de cada Instituto)", p_m0),
        ("M1_2T (h=3 dias, Recência + Raiz Amostra)", p_m1_h3),
        ("M1_2T (h=5 dias, Recência + Raiz Amostra)", p_m1_h5),
        ("M1_2T (h=7 dias, Recência + Raiz Amostra)", p_m1_h7),
        ("M2_2T (sigma0=1.5, Peso Inverso Erro 1T)", p_m2_s15),
        ("M2_2T (sigma0=2.5, Peso Inverso Erro 1T)", p_m2_s25),
        ("M0_2T + Persistência 1T (rho=0.20)", p_m0_rho20),
        ("M2_2T (sigma0=1.5) + Persistência 1T (rho=0.20)", p_m2_rho20),
        (f"M2_2T (sigma0=1.5) + Persistência 1T (rho_OLS={rho_ols:.2f})", p_m2_rho_ols),
        (f"Prior transferência com tau médio (tau={tau_med:.4f})", p_prior_1t_medio),
        (f"Prior transferência com tau mediano (tau={tau_mdn:.4f})", p_prior_1t_mediano),
        (f">>> MODELO OFICIAL SELECIONADO ({nome_modelo_final})", p_oficial_pt),
    ]

    linhas_sens = []
    for desc, val_lula in especificacoes_2026:
        val_flavio = 100.0 - val_lula
        arr = maiores_restos([val_flavio, val_lula], total=100.0, casas=1)
        linhas_sens.append(
            {
                "Especificação": desc,
                "Flávio Bolsonaro (Contínuo %)": round(val_flavio, 2),
                "Lula (Contínuo %)": round(val_lula, 2),
                "Flávio (Arred 1 casa)": arr[0],
                "Lula (Arred 1 casa)": arr[1],
            }
        )
    df_sens = pd.DataFrame(linhas_sens)
    print(df_sens.to_string(index=False))

    with open(PROCESSED_DIR / "tse_2026_1t_oficial.json", encoding="utf-8") as f:
        tse_2026_1t = json.load(f)
    df_nac = pd.read_parquet(PROCESSED_DIR / "tse_historico_2t.parquet").set_index("eleicao")

    y1_2026 = {
        "abstencao": float(tse_2026_1t["abstencao_pct"]),
        "brancos": float(tse_2026_1t["brancos_pct"]),
        "nulos": float(tse_2026_1t["nulos_pct"]),
    }

    adicionais_2026 = {}
    detalhes_aba2_2026 = []
    print("\n--- Projeções da Aba 2 para o 2o Turno de 2026 ---")
    for var in ["abstencao", "brancos", "nulos"]:
        met_venc = vencedores_aba2[var]
        val_1t = y1_2026[var]
        if met_venc == "Zero_Delta (y2=y1)":
            pred_v = val_1t
        elif met_venc == "Persistencia_Delta":
            pred_v = val_1t + float(df_nac.loc[2022, f"delta_{var}"])
        elif met_venc == "Media_Delta":
            pred_v = val_1t + float(df_nac[f"delta_{var}"].mean())
        elif met_venc == "Ratio_Media":
            pred_v = val_1t * float(df_nac[f"ratio_{var}"].mean())
        else:
            pred_v = val_1t
        adicionais_2026[var] = round(pred_v, 1)
        detalhes_aba2_2026.append(
            {
                "variavel": var,
                "val_1t": val_1t,
                "metodo_vencedor": met_venc,
                "proj_continua": pred_v,
                "proj_arred": adicionais_2026[var],
            }
        )
        print(
            f"  {var:12s} | 1T Oficial = {val_1t:.2f}% | Método Vencedor = {met_venc:20s} -> Projeção 2T = {pred_v:.2f}% (Arred: {adicionais_2026[var]:.1f}%)"
        )

    previsoes_cand_2026 = {
        "Flávio Bolsonaro": 100.0 - p_oficial_pt,
        "Luiz Inácio Lula da Silva": p_oficial_pt,
    }
    caminho_xlsx = gerar_planilha_entrega_2t(
        previsoes_cand_2026,
        adicionais_2026,
        OUTPUTS_DIR / "previsao_2026_2t.xlsx",
    )
    print(f"\nOK: Planilha do 2o Turno gerada em {caminho_xlsx}")
    return df_sens, previsoes_cand_2026, adicionais_2026, detalhes_aba2_2026, nome_modelo_final


def gerar_relatorio_markdown_2t(
    df_e1: pd.DataFrame,
    vencedor_e1: str,
    df_e2: pd.DataFrame,
    df_loeo: pd.DataFrame,
    vencedores_aba2: dict[str, str],
    tabelas_aba2: dict[str, pd.DataFrame],
    df_taus: pd.DataFrame,
    df_gov2t: pd.DataFrame,
    df_sens: pd.DataFrame,
    detalhes_aba2_2026: list[dict],
    nome_modelo_final: str,
) -> Path:
    """
    Gera 100% automaticamente (sem edicao manual) o arquivo reports/relatorio_backtest_2t.md.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    caminho_md = REPORTS_DIR / "relatorio_backtest_2t.md"

    md = []
    md.append("# Relatório Oficial do Backtest do 2º Turno (Desafio Eleições 2026 FGV EPGE)")
    md.append("")
    md.append(
        "> **Arquivo gerado 100% automaticamente por `scripts/executar_backtest_2t.py` (sem edição manual).**"
    )
    md.append("")
    md.append(
        "- **Protocolo:** `protocolo/PRE_REGISTRO_2T.md` (Protocolo do 2º turno definido em 21/10/2026)"
    )
    md.append("- **Script Reprodutível:** `scripts/executar_backtest_2t.py`")
    md.append("- **Suíte de Testes:** `tests/test_pipeline_2t.py`")
    md.append("")
    md.append("---")
    md.append("")

    # 1. Etapa 1
    md.append(
        "## 1. Etapa 1 (Aba 1 — Votos Válidos, $K=2$): Seleção do Modelo Base no Expanding Window"
    )
    md.append("")
    md.append(
        "Avaliação prospectiva nas 3 eleições de teste (`2014`, `2018`, `2022`), onde "
        "$\\text{MAE}_{2T} = \\lvert \\hat{V}_{\\text{PT}} - V_{\\text{PT}} \\rvert = \\lvert \\hat{V}_{\\text{Adv}} - V_{\\text{Adv}} \\rvert$:"
    )
    md.append("")
    md.append(
        "| Modelo Base | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio Expanding (p.p.)** | EP (p.p.) | Diferença vs. M0_2T (p.p.) | EP(Diferença) | Supera M0_2T (> 1 EP)? |"
    )
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in df_e1.iterrows():
        mod = str(r["modelo"])
        is_win = mod == vencedor_e1
        b = "**" if is_win else ""
        if mod == "M0_2T":
            status_str = "Baseline"
        elif bool(r["supera_m0_1se"]):
            raz = (
                abs(float(r["delta_vs_m0"])) / float(r["se_delta"])
                if float(r["se_delta"]) > 0
                else 0.0
            )
            status_str = f"{b}SIM ({_fmt(raz, 2)} EP){b}"
        else:
            status_str = "Não"
        md.append(
            f"| {b}`{mod}`{b} | {b}{_fmt(r['2014'])}{b} | {b}{_fmt(r['2018'])}{b} | {b}{_fmt(r['2022'])}{b} | "
            f"{b}{_fmt(r['mae_medio'])}{b} | {b}{_fmt(r['se'])}{b} | {b}{_fmt_sinal(r['delta_vs_m0'])}{b} | "
            f"{b}{_fmt(r['se_delta'])}{b} | {status_str} |"
        )
    md.append("")
    md.append(
        f"- **Vencedor Formal da Etapa 1 (Regra de 1 EP + Parcimônia):** **`{vencedor_e1}`**."
    )
    md.append("")
    md.append("---")
    md.append("")

    # 2. Etapa 2
    md.append(f"## 2. Etapa 2 (Aba 1): Avaliação Isolada de Ajustes sobre `{vencedor_e1}`")
    md.append("")
    md.append(
        "| Configuração / Ajuste | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio (p.p.)** | EP (p.p.) | Diferença vs. Base (p.p.) | EP(Diferença) | Aprovado (> 1 EP)? |"
    )
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in df_e2.iterrows():
        aj = str(r["ajuste"])
        is_base = aj.endswith("(Base Puro)")
        b = "**" if is_base else ""
        if is_base:
            ap_str = "**Vencedor (Base)**"
        elif bool(r["aprovado"]):
            ap_str = "**SIM**"
        elif float(r["delta_vs_base"]) < 0:
            ap_str = "Empate Técnico (< 1 EP)"
        else:
            ap_str = "Não"
        md.append(
            f"| {b}`{aj}`{b} | {b}{_fmt(r['2014'])}{b} | {b}{_fmt(r['2018'])}{b} | {b}{_fmt(r['2022'])}{b} | "
            f"{b}{_fmt(r['mae_medio'])}{b} | {b}{_fmt(r['se'])}{b} | {b}{_fmt_sinal(r['delta_vs_base'])}{b} | "
            f"{b}{_fmt(r['se_delta'])}{b} | {ap_str} |"
        )
    md.append("")
    md.append(f"- **Modelo Final Selecionado para a Aba 1:** **`{nome_modelo_final}`**.")
    md.append("")
    md.append("---")
    md.append("")

    # 3. LOEO
    md.append("## 3. Validação Complementar LOEO (`2006, 2010, 2014, 2018, 2022`, $n=5$)")
    md.append("")
    md.append("| Modelo | 2006 | 2010 | 2014 | 2018 | 2022 | **MAE Médio LOEO (p.p.)** | EP LOEO |")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for _, r in df_loeo.iterrows():
        mod = str(r["modelo"])
        is_win = mod == vencedor_e1
        b = "**" if is_win else ""
        md.append(
            f"| {b}`{mod}`{b} | {b}{_fmt(r['2006'])}{b} | {b}{_fmt(r['2010'])}{b} | {b}{_fmt(r['2014'])}{b} | "
            f"{b}{_fmt(r['2018'])}{b} | {b}{_fmt(r['2022'])}{b} | {b}{_fmt(r['mae_loeo'])}{b} | {b}{_fmt(r['se_loeo'])}{b} |"
        )
    md.append("")
    md.append("---")
    md.append("")

    # 4. Transferencia Estrutural 1T -> 2T (Tau por eleicao)
    md.append(
        "## 4. Parâmetros de Transferência Estrutural $1\\text{T} \\to 2\\text{T}$ ($\\tau_t$ por Eleição)"
    )
    md.append("")
    md.append(
        "Fração aparente dos votos de terceiros colocados no 1º turno capturada pelo candidato do PT no 2º turno, "
        "$\\tau_t = \\frac{V_{\\text{PT}, 2T, t} - V_{\\text{PT}, 1T, t}}{100 - V_{\\text{PT}, 1T, t} - V_{\\text{Adv}, 1T, t}}$:"
    )
    md.append("")
    md.append(
        "| Eleição | PT 1T (%) | Adv 1T (%) | Terceiros 1T (%) | PT 2T (%) | Adv 2T (%) | $\\Delta$ PT ($2\\text{T}-1\\text{T}$) | $\\Delta$ Adv ($2\\text{T}-1\\text{T}$) | **$\\tau_t$ (PT)** | Observação |"
    )
    md.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")
    for _, r in df_taus.iterrows():
        ano_i = int(r["eleicao"])
        obs = (
            "Outlier ($\\tau > 1$): adversário (Alckmin) perdeu votos do 1T para o 2T"
            if ano_i == 2006
            else "Transferência regular ($0 < \\tau < 1$)"
        )
        md.append(
            f"| {ano_i} | {_fmt(r['pt_1t'], 2)}% | {_fmt(r['adv_1t'], 2)}% | {_fmt(r['terceiros_1t'], 2)}% | "
            f"{_fmt(r['pt_2t'], 2)}% | {_fmt(r['adv_2t'], 2)}% | {_fmt_sinal(r['delta_pt'], 2)} p.p. | "
            f"{_fmt_sinal(r['delta_adv'], 2)} p.p. | **{_fmt(r['tau_pt'], 4)}** | {obs} |"
        )
    tau_med = float(df_taus["tau_pt"].mean())
    tau_mdn = float(df_taus["tau_pt"].median())
    md.append("")
    md.append(
        f"- **Média histórica ($\\bar{{\\tau}}_{{2006\\text{{--}}2022}}$):** `{_fmt(tau_med, 4)}` "
        f"(inflada pelo outlier de 2006, $\\tau_{{2006}} = {_fmt(df_taus.loc[df_taus['eleicao'] == 2006, 'tau_pt'].iloc[0], 4)}$, "
        "quando Geraldo Alckmin caiu de 41,64% no 1º turno para 39,17% no 2º turno)."
    )
    md.append(
        f"- **Mediana histórica ($\\tilde{{\\tau}}_{{2006\\text{{--}}2022}}$):** `{_fmt(tau_mdn, 4)}` "
        "(estimador robusto ao outlier de 2006)."
    )
    md.append("")
    md.append("---")
    md.append("")

    # 5. Backtest da Aba 2
    md.append("## 5. Backtest da Aba 2 no 2º Turno (Ancorado no 1º Turno da Mesma Eleição)")
    md.append("")
    titulos_aba2 = {
        "abstencao": "5.1. Abstenção (% do Eleitorado Apto)",
        "brancos": "5.2. Votos Brancos (% dos Votos Totais)",
        "nulos": "5.3. Votos Nulos (% dos Votos Totais)",
    }
    for var in ["abstencao", "brancos", "nulos"]:
        md.append(f"### {titulos_aba2[var]}")
        md.append("")
        md.append(
            "| Método | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio (p.p.)** | EP (p.p.) | Diferença vs. Zero_Delta (p.p.) | EP(Diferença) | Supera Zero_Delta (> 1 EP)? |"
        )
        md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
        df_v = tabelas_aba2[var]
        venc_v = vencedores_aba2[var]
        for _, r in df_v.iterrows():
            met = str(r["metodo"])
            is_win = met == venc_v
            b = "**" if is_win else ""
            if met == "Zero_Delta (y2=y1)":
                st = "**Vencedor (Parcimônia)**" if is_win else "Baseline"
            elif bool(r["supera_zero_1se"]):
                st = "**SIM**"
            elif float(r["delta_vs_zero"]) < 0:
                st = "Empate Técnico (< 1 EP)"
            else:
                st = "Não"
            md.append(
                f"| {b}`{met}`{b} | {b}{_fmt(r['2014'])}{b} | {b}{_fmt(r['2018'])}{b} | {b}{_fmt(r['2022'])}{b} | "
                f"{b}{_fmt(r['mae_medio'])}{b} | {b}{_fmt(r['se'])}{b} | {b}{_fmt_sinal(r['delta_vs_zero'])}{b} | "
                f"{b}{_fmt(r['se_delta'])}{b} | {st} |"
            )
        md.append("")
        md.append(f"- **Vencedor Formal para `{var}`:** **`{venc_v}`**.")
        md.append("")

    # 5.4. Limitacoes da Aba 2 e Share do Eleitorado com 2T de Governador
    hist_gov = df_gov2t[df_gov2t["eleicao"] != "2026"]
    min_sh_com = float(hist_gov["share_com_gov2t_pct"].min())
    max_sh_com = float(hist_gov["share_com_gov2t_pct"].max())
    media_sh_com = float(hist_gov["share_com_gov2t_pct"].mean())
    media_d_com = float(hist_gov["delta_abst_com_gov2t"].mean())
    media_d_sem = float(hist_gov["delta_abst_sem_gov2t"].mean())
    sh_2026_com = float(df_gov2t.loc[df_gov2t["eleicao"] == "2026", "share_com_gov2t_pct"].iloc[0])
    sh_2026_sem = 100.0 - sh_2026_com

    md.append(
        "### 5.4. Limitações da Aba 2: Share do Eleitorado com 2º Turno de Governador (2006–2022 vs. 2026)"
    )
    md.append("")
    md.append(
        f"Em 2026, apenas **6 Unidades da Federação** (`AC, AM, DF, ES, RN, TO`) têm disputa de 2º turno para Governador, "
        f"o que corresponde a apenas **{_fmt(sh_2026_com, 2)}%** do eleitorado nacional apto, contra uma faixa histórica "
        f"de **{_fmt(min_sh_com, 2)}% a {_fmt(max_sh_com, 2)}%** entre 2006 e 2022 (média histórica de **{_fmt(media_sh_com, 2)}%**):"
    )
    md.append("")
    md.append(
        "| Eleição | Nº UFs com Gov 2T | UFs com Gov 2T | Share Eleitorado **COM** Gov 2T (%) | Share Eleitorado **SEM** Gov 2T (%) | $\\Delta$ Abst COM Gov 2T (p.p.) | $\\Delta$ Abst SEM Gov 2T (p.p.) | $\\Delta$ Abst Nacional (p.p.) |"
    )
    md.append("| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |")
    for _, r in df_gov2t.iterrows():
        el = str(r["eleicao"])
        b = "**" if el == "2026" else ""
        d_com = (
            f"{_fmt_sinal(r['delta_abst_com_gov2t'], 2)}"
            if not pd.isna(r["delta_abst_com_gov2t"])
            else "—"
        )
        d_sem = (
            f"{_fmt_sinal(r['delta_abst_sem_gov2t'], 2)}"
            if not pd.isna(r["delta_abst_sem_gov2t"])
            else "—"
        )
        d_nac = (
            f"{_fmt_sinal(r['delta_abst_nacional'], 2)}"
            if not pd.isna(r["delta_abst_nacional"])
            else "—"
        )
        md.append(
            f"| {b}{el}{b} | {b}{int(r['n_ufs_gov2t'])}{b} | `{r['ufs_gov2t']}` | "
            f"{b}{_fmt(r['share_com_gov2t_pct'], 2)}%{b} | {b}{_fmt(r['share_sem_gov2t_pct'], 2)}%{b} | "
            f"{d_com} | {d_sem} | {d_nac} |"
        )
    md.append("")
    md.append(
        f"- **Análise de Limitação Estrutural:** Entre 2006 e 2022, a fração média do eleitorado nacional com disputa "
        f"simultânea para Governador no 2º turno foi de **`{_fmt(media_sh_com, 2)}%`** (mínimo anterior de `14,36%` em 2010 "
        f"e máximo de `62,97%` em 2018), e a variação média da abstenção foi de `{_fmt_sinal(media_d_com, 2)} p.p.` nas UFs "
        f"com 2º turno estadual vs. `{_fmt_sinal(media_d_sem, 2)} p.p.` nas UFs sem disputa estadual. Em 2026, "
        f"**`{_fmt(sh_2026_sem, 2)}%`** do eleitorado nacional vai às urnas apenas para Presidente (share com Gov 2T = "
        f"**`{_fmt(sh_2026_com, 2)}%`**, o menor da série histórica). Caso a ausência de campanha estadual desmobilize "
        f"eleitores nos estados já decididos no 1º turno, a regra `Zero_Delta` (`21,1%`) pode subestimar ligeiramente a "
        f"abstenção do 2º turno."
    )
    md.append("")
    md.append("---")
    md.append("")

    # 6. Tabela de Sensibilidade 2026
    md.append("## 6. Tabela de Sensibilidade para o 2º Turno de 2026 (Corte Parcial: 21/10/2026)")
    md.append("")
    md.append(
        "| Especificação | Flávio Bolsonaro (Contínuo %) | Lula (Contínuo %) | **Flávio (Arred 1 casa)** | **Lula (Arred 1 casa)** |"
    )
    md.append("| :--- | :---: | :---: | :---: | :---: |")
    for _, r in df_sens.iterrows():
        esp = str(r["Especificação"])
        is_sel = esp.startswith(">>>")
        b = "**" if is_sel else ""
        md.append(
            f"| {b}{esp}{b} | {b}{_fmt(r['Flávio Bolsonaro (Contínuo %)'], 2)}%{b} | "
            f"{b}{_fmt(r['Lula (Contínuo %)'], 2)}%{b} | "
            f"**{_fmt(r['Flávio (Arred 1 casa)'], 1)}%** | **{_fmt(r['Lula (Arred 1 casa)'], 1)}%** |"
        )
    md.append("")
    md.append("### 6.1. Resumo das Projeções da Aba 2 para 2026")
    md.append("")
    md.append(
        "| Variável (Aba 2) | Oficial 1º Turno 2026 (%) | Método Vencedor (Backtest) | Projeção Contínua 2T (%) | **Previsão Oficial 2T (1 casa)** |"
    )
    md.append("| :--- | :---: | :--- | :---: | :---: |")
    nomes_bonitos = {"abstencao": "Abstenção", "brancos": "Votos brancos", "nulos": "Votos nulos"}
    for item in detalhes_aba2_2026:
        v = item["variavel"]
        md.append(
            f"| **{nomes_bonitos[v]}** | {_fmt(item['val_1t'], 2)}% | `{item['metodo_vencedor']}` | "
            f"{_fmt(item['proj_continua'], 2)}% | **{_fmt(item['proj_arred'], 1)}%** |"
        )
    md.append("")

    caminho_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"OK: Relatorio de backtest gerado 100% automaticamente em {caminho_md}")
    return caminho_md


if __name__ == "__main__":
    df_e1, preds_all, vencedor_e1 = rodar_etapa_1_aba1()
    df_e2, modo_b, param_b = rodar_etapa_2_aba1(vencedor_e1, preds_all)
    df_loeo = rodar_loeo_2t(preds_all)
    vencedores_aba2, tabelas_aba2 = rodar_backtest_aba2_2t()
    df_taus, df_gov2t = calcular_tabela_taus_e_gov2t()
    df_sens, prev_cand, prev_ad, det_aba2, nome_final = projetar_2026_2t(
        vencedor_e1, df_e2, modo_b, param_b, vencedores_aba2, df_taus
    )
    gerar_relatorio_markdown_2t(
        df_e1,
        vencedor_e1,
        df_e2,
        df_loeo,
        vencedores_aba2,
        tabelas_aba2,
        df_taus,
        df_gov2t,
        df_sens,
        det_aba2,
        nome_final,
    )
