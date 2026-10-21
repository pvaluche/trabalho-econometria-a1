"""
scripts/executar_backtest_2t.py
Executa o protocolo sequencial completo de backtest historico para o 2o Turno (Expanding Window e LOEO),
seleciona formalmente os modelos da Aba 1 e da Aba 2 sob a regra de 1 SE(Delta), gera a tabela de
sensibilidade para 2026 e produz a planilha preliminar outputs/previsao_2026_2t.xlsx e o relatorio
reports/relatorio_backtest_2t.md.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
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
    carregar_pesquisas_2026_2t,
    carregar_pesquisas_2t_historicas,
    estimar_m0_2t,
    estimar_m1_2t,
    estimar_m2_2t_peso_1t,
    estimar_rho_ols_treino,
    obter_semi_erros_margem_1t,
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
        linhas.append({
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
        })

    df_res = pd.DataFrame(linhas)
    print(df_res[["modelo", "2014", "2018", "2022", "mae_medio", "se", "delta_vs_m0", "se_delta", "supera_m0_1se"]].round(4).to_string(index=False))

    # Selecao formal: verifica se algum modelo supera M0_2T por mais de 1 SE(Delta)
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

    # Identifica modo_base e param_base
    if vencedor_base == "M0_2T":
        modo_base, param_base = "M0_2T", 0.0
    elif vencedor_base.startswith("M1_2T"):
        modo_base = "M1_2T"
        param_base = float(vencedor_base.split("=")[1].replace(")", ""))
    else:
        modo_base = "M2_2T"
        param_base = float(vencedor_base.split("=")[1].replace(")", ""))

    erros_base = [calcular_mae_2t(preds_todos_anos[vencedor_base][t], t) for t in ANOS_TESTE_EXPANDING]

    ajustes = {
        f"{vencedor_base} (Base Puro)": lambda t, tr: preds_todos_anos[vencedor_base][t],
        "+ Persistência 1T (rho=0.20)": lambda t, tr: aplicar_ajuste_persistencia_1t(
            carregar_pesquisas_2t_historicas(t), t, rho=0.20, modo_base=modo_base, param_base=param_base
        ),
        "+ Persistência 1T (rho=0.35)": lambda t, tr: aplicar_ajuste_persistencia_1t(
            carregar_pesquisas_2t_historicas(t), t, rho=0.35, modo_base=modo_base, param_base=param_base
        ),
        "+ Persistência 1T (rho=OLS_treino)": lambda t, tr: aplicar_ajuste_persistencia_1t(
            carregar_pesquisas_2t_historicas(t), t, rho=estimar_rho_ols_treino(tr), modo_base=modo_base, param_base=param_base
        ),
        "+ Viés Comum 2T (k_mu=1)": lambda t, tr: aplicar_ajuste_vies_comum_2t(
            preds_todos_anos[vencedor_base][t], tr, k_mu=1.0, preds_base_por_ano=preds_todos_anos[vencedor_base]
        ),
        "+ Viés Comum 2T (k_mu=3)": lambda t, tr: aplicar_ajuste_vies_comum_2t(
            preds_todos_anos[vencedor_base][t], tr, k_mu=3.0, preds_base_por_ano=preds_todos_anos[vencedor_base]
        ),
        "+ Shrinkage Prior 1T (lambda=0.10)": lambda t, tr: (
            0.90 * preds_todos_anos[vencedor_base][t] + 0.10 * calcular_prior_estrutural_1t(t, tr)
        ),
        "+ Shrinkage Prior 1T (lambda=0.25)": lambda t, tr: (
            0.75 * preds_todos_anos[vencedor_base][t] + 0.25 * calcular_prior_estrutural_1t(t, tr)
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
        linhas.append({
            "ajuste": nome,
            "2014": erros[0],
            "2018": erros[1],
            "2022": erros[2],
            "mae_medio": mae_med,
            "se": se,
            "delta_vs_base": d_base,
            "se_delta": se_d,
            "aprovado": aprovado,
        })

    df_aj = pd.DataFrame(linhas)
    print(df_aj[["ajuste", "2014", "2018", "2022", "mae_medio", "delta_vs_base", "se_delta", "aprovado"]].round(4).to_string(index=False))
    return df_aj, modo_base, param_base


def rodar_loeo_2t(preds_todos_anos: dict[str, dict[int, float]]):
    print("\n" + "=" * 85)
    print("VALIDACAO COMPLEMENTAR LOEO (2006, 2010, 2014, 2018, 2022)")
    print("=" * 85)

    linhas = []
    for nome, mapa_anos in preds_todos_anos.items():
        erros = {a: calcular_mae_2t(mapa_anos[a], a) for a in TODOS_ANOS_LOEO}
        vals = [erros[a] for a in TODOS_ANOS_LOEO]
        linhas.append({
            "modelo": nome,
            "2006": erros[2006],
            "2010": erros[2010],
            "2014": erros[2014],
            "2018": erros[2018],
            "2022": erros[2022],
            "mae_loeo": float(np.mean(vals)),
            "se_loeo": float(np.std(vals, ddof=1) / math.sqrt(len(vals))),
        })

    # Adiciona tambem M2_2T + Persistencia 1T (rho=0.20) no LOEO
    for base_tag, m_base, p_base in [("M0_2T", "M0_2T", 0.0), ("M2_2T (sigma0=1.5)", "M2_2T", 1.5)]:
        for rho in [0.20, 0.35]:
            erros = {
                a: calcular_mae_2t(
                    aplicar_ajuste_persistencia_1t(carregar_pesquisas_2t_historicas(a), a, rho=rho, modo_base=m_base, param_base=p_base),
                    a,
                )
                for a in TODOS_ANOS_LOEO
            }
            vals = [erros[a] for a in TODOS_ANOS_LOEO]
            linhas.append({
                "modelo": f"{base_tag} + Persist 1T (rho={rho:.2f})",
                "2006": erros[2006],
                "2010": erros[2010],
                "2014": erros[2014],
                "2018": erros[2018],
                "2022": erros[2022],
                "mae_loeo": float(np.mean(vals)),
                "se_loeo": float(np.std(vals, ddof=1) / math.sqrt(len(vals))),
            })

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
            preds = {}
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
                    # Calcula delta medio no ultimo ano de treino (ou media de treino) para UFs com e sem Gov2T
                    sub_tr = df_uf[df_uf["eleicao"] == tr[-1]]
                    g1 = sub_tr[sub_tr["gov2t"] == 1]
                    g0 = sub_tr[sub_tr["gov2t"] == 0]
                    d_com = float(np.average(g1["delta_abst"], weights=g1["aptos_2t"])) if len(g1) else deltas[tr[-1]]
                    d_sem = float(np.average(g0["delta_abst"], weights=g0["aptos_2t"])) if len(g0) else deltas[tr[-1]]
                    sub_t = df_uf[df_uf["eleicao"] == t]
                    sh_t = sub_t[sub_t["gov2t"] == 1]["aptos_2t"].sum() / sub_t["aptos_2t"].sum()
                    pred = y1[t] + sh_t * d_com + (1.0 - sh_t) * d_sem
                preds[t] = pred
                erros.append(abs(pred - y2[t]))

            mae_med = float(np.mean(erros))
            se = float(np.std(erros, ddof=1) / math.sqrt(len(erros)))
            if met == "Zero_Delta (y2=y1)":
                d_z, se_d, supera_z = 0.0, 0.0, False
            else:
                d_z, se_d = calcular_diferenca_e_se(erros, erros_zero)
                supera_z = bool(d_z < -se_d)
            linhas_var.append({
                "metodo": met,
                "2014": erros[0],
                "2018": erros[1],
                "2022": erros[2],
                "mae_medio": mae_med,
                "se": se,
                "delta_vs_zero": d_z,
                "se_delta": se_d,
                "supera_zero_1se": supera_z,
            })

        df_v = pd.DataFrame(linhas_var)
        print(df_v.round(4).to_string(index=False))
        aprov = df_v[df_v["supera_zero_1se"]].sort_values("mae_medio")
        vencedor_v = str(aprov.iloc[0]["metodo"]) if not aprov.empty else "Zero_Delta (y2=y1)"
        print(f"  >>> Vencedor formal para {var}: {vencedor_v}")
        vencedores_aba2[var] = vencedor_v
        tabelas_aba2[var] = df_v

    return vencedores_aba2, tabelas_aba2


def projetar_2026_2t(vencedor_base: str, df_aj: pd.DataFrame, modo_base: str, param_base: float, vencedores_aba2: dict[str, str]):
    print("\n" + "=" * 85)
    print("PROJECOES E TABELA DE SENSIBILIDADE PARA O 2o TURNO DE 2026 (CORTE PARCIAL 21/10)")
    print("=" * 85)

    df_2026_2t = carregar_pesquisas_2026_2t()
    tr_all = TODOS_ANOS_LOEO

    # Calcula todas as especificacoes para 2026
    p_m0 = estimar_m0_2t(df_2026_2t)
    p_m1_h3 = estimar_m1_2t(df_2026_2t, 2026, meia_vida=3.0)
    p_m1_h5 = estimar_m1_2t(df_2026_2t, 2026, meia_vida=5.0)
    p_m1_h7 = estimar_m1_2t(df_2026_2t, 2026, meia_vida=7.0)
    p_m2_s15 = estimar_m2_2t_peso_1t(df_2026_2t, 2026, sigma0=1.5)
    p_m2_s25 = estimar_m2_2t_peso_1t(df_2026_2t, 2026, sigma0=2.5)

    rho_ols = estimar_rho_ols_treino(tr_all)
    p_m0_rho20 = aplicar_ajuste_persistencia_1t(df_2026_2t, 2026, rho=0.20, modo_base="M0_2T")
    p_m2_rho20 = aplicar_ajuste_persistencia_1t(df_2026_2t, 2026, rho=0.20, modo_base="M2_2T", param_base=1.5)
    p_m2_rho_ols = aplicar_ajuste_persistencia_1t(df_2026_2t, 2026, rho=rho_ols, modo_base="M2_2T", param_base=1.5)
    p_prior_1t = calcular_prior_estrutural_1t(2026, tr_all)

    # Identifica a projecao do modelo vencedor formal do backtest
    mapa_base_2026 = {
        "M0_2T": p_m0,
        "M1_2T (h=3)": p_m1_h3,
        "M1_2T (h=5)": p_m1_h5,
        "M1_2T (h=7)": p_m1_h7,
        "M2_2T (sigma0=1.5)": p_m2_s15,
        "M2_2T (sigma0=2.5)": p_m2_s25,
    }
    p_vencedor_etapa1 = mapa_base_2026[vencedor_base]

    # Verifica se algum ajuste da Etapa 2 foi aprovado
    aj_aprovados = df_aj[(df_aj["aprovado"]) & (~df_aj["ajuste"].str.endswith("(Base Puro)"))].sort_values("mae_medio")
    if not aj_aprovados.empty:
        melhor_aj = str(aj_aprovados.iloc[0]["ajuste"])
        if "rho=0.20" in melhor_aj:
            p_oficial_pt = aplicar_ajuste_persistencia_1t(df_2026_2t, 2026, rho=0.20, modo_base=modo_base, param_base=param_base)
        elif "rho=0.35" in melhor_aj:
            p_oficial_pt = aplicar_ajuste_persistencia_1t(df_2026_2t, 2026, rho=0.35, modo_base=modo_base, param_base=param_base)
        elif "rho=OLS" in melhor_aj:
            p_oficial_pt = aplicar_ajuste_persistencia_1t(df_2026_2t, 2026, rho=rho_ols, modo_base=modo_base, param_base=param_base)
        elif "lambda=0.10" in melhor_aj:
            p_oficial_pt = 0.90 * p_vencedor_etapa1 + 0.10 * p_prior_1t
        elif "lambda=0.25" in melhor_aj:
            p_oficial_pt = 0.75 * p_vencedor_etapa1 + 0.25 * p_prior_1t
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
        ("Prior Estrutural Puro de Transferência 1T", p_prior_1t),
        (f">>> MODELO OFICIAL SELECIONADO ({nome_modelo_final})", p_oficial_pt),
    ]

    linhas_sens = []
    for desc, val_lula in especificacoes_2026:
        val_flavio = 100.0 - val_lula
        arr = maiores_restos([val_flavio, val_lula], total=100.0, casas=1)
        linhas_sens.append({
            "Especificação": desc,
            "Flávio Bolsonaro (Contínuo %)": round(val_flavio, 2),
            "Lula (Contínuo %)": round(val_lula, 2),
            "Flávio (Arred 1 casa)": arr[0],
            "Lula (Arred 1 casa)": arr[1],
        })
    df_sens = pd.DataFrame(linhas_sens)
    print(df_sens.to_string(index=False))

    # Projecao Aba 2 para 2026
    with open(PROCESSED_DIR / "tse_2026_1t_oficial.json", "r", encoding="utf-8") as f:
        tse_2026_1t = json.load(f)
    df_nac = pd.read_parquet(PROCESSED_DIR / "tse_historico_2t.parquet").set_index("eleicao")

    y1_2026 = {
        "abstencao": float(tse_2026_1t["abstencao_pct"]),
        "brancos": float(tse_2026_1t["brancos_pct"]),
        "nulos": float(tse_2026_1t["nulos_pct"]),
    }

    adicionais_2026 = {}
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
        print(f"  {var:12s} | 1T Oficial = {val_1t:.2f}% | Método Vencedor = {met_venc:20s} -> Projeção 2T = {pred_v:.2f}% (Arred: {adicionais_2026[var]:.1f}%)")

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
    return df_sens, previsoes_cand_2026, adicionais_2026, nome_modelo_final


if __name__ == "__main__":
    df_e1, preds_all, vencedor_e1 = rodar_etapa_1_aba1()
    df_e2, modo_b, param_b = rodar_etapa_2_aba1(vencedor_e1, preds_all)
    df_loeo = rodar_loeo_2t(preds_all)
    vencedores_aba2, tabelas_aba2 = rodar_backtest_aba2_2t()
    df_sens, prev_cand, prev_ad, nome_final = projetar_2026_2t(
        vencedor_e1, df_e2, modo_b, param_b, vencedores_aba2
    )
