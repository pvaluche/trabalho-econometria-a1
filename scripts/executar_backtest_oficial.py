"""
scripts/executar_backtest_oficial.py
Executa o protocolo oficial e sequencial de backtest historico (Checkpoint 3).
Inclui auditoria completa: MAE sobre todos os candidatos da urna, regra de empate
na Aba 2 com contas de Delta e SE, P80 das faixas, estatisticas da margem do Top-2
e geracao da tabela de sensibilidade de 2026.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.arredondamento import maiores_restos
from src.backtest import (
    aplicar_ajuste_priors_nanicos,
    aplicar_ajuste_vies_comum,
    aplicar_ajuste_voto_util,
    calcular_diferenca_e_se,
    calcular_mae_eleicao,
    carregar_resultado_tse,
    estimar_m0,
    estimar_m1,
    estimar_m2,
    estimar_m3,
)
from src.config import MANUAL_DIR, OUTPUTS_DIR, PARTIDOS_EDITAL
from src.entrega import gerar_planilha_entrega
from src.pesquisas import carregar_pesquisas_historicas

ANOS_TESTE_EXPANDING = [2014, 2018, 2022]
TREINO_EXPANDING = {
    2014: [2006, 2010],
    2018: [2006, 2010, 2014],
    2022: [2006, 2010, 2014, 2018],
}
TODOS_ANOS_LOEO = [2006, 2010, 2014, 2018, 2022]


def aplicar_maiores_restos_dict(d: dict[str, float]) -> dict[str, float]:
    keys = list(d.keys())
    vals = [d[k] for k in keys]
    arr = maiores_restos(vals, total=100.0, casas=1)
    return {k: round(v, 1) for k, v in zip(keys, arr)}


def rodar_etapa_1_modelos_base():
    """Etapa 1: Avalia as 11 configuracoes dos modelos base puros via Expanding Window."""
    print("=" * 80)
    print("ETAPA 1: AVALIACAO DOS MODELOS BASE NO EXPANDING WINDOW (URNA COMPLETA)")
    print("=" * 80)

    configs = {}
    configs["M0"] = lambda df, t, tr: estimar_m0(df, t)

    for h in [7.0, 14.0, 21.0]:
        configs[f"M1 (h={int(h)})"] = (lambda h_val: lambda df, t, tr: estimar_m1(df, t, meia_vida=h_val))(h)

    # Determina melhor h preliminarmente
    maes_m1 = {}
    for h in [7.0, 14.0, 21.0]:
        m_list = []
        for t in ANOS_TESTE_EXPANDING:
            df_t = carregar_pesquisas_historicas(t)
            res_tse = carregar_resultado_tse(t)
            p = estimar_m1(df_t, t, meia_vida=h)
            m_list.append(calcular_mae_eleicao(p, res_tse))
        maes_m1[h] = np.mean(m_list)

    best_h = min(maes_m1.keys(), key=lambda h: maes_m1[h])

    for k in [1.0, 3.0, 10.0]:
        configs[f"M2 (h={int(best_h)}, k={int(k)})"] = (
            lambda k_val: lambda df, t, tr: estimar_m2(df, t, tr, meia_vida=best_h, k_shrinkage=k_val)
        )(k)

    for alpha in [0.01, 0.1, 1.0, 10.0]:
        configs[f"M3 (alpha={alpha})"] = (
            lambda a_val: lambda df, t, tr: estimar_m3(df, t, tr, meia_vida=best_h, alpha=a_val)
        )(alpha)

    tabela_base = []
    preds_armazenadas = {}

    for nome, func in configs.items():
        maes_ano = {}
        for t in ANOS_TESTE_EXPANDING:
            tr = TREINO_EXPANDING[t]
            df_t = carregar_pesquisas_historicas(t)
            res_tse = carregar_resultado_tse(t)
            p = func(df_t, t, tr)
            preds_armazenadas[(nome, t)] = p
            maes_ano[t] = calcular_mae_eleicao(p, res_tse)

        mae_vals = [maes_ano[t] for t in ANOS_TESTE_EXPANDING]
        mae_med = float(np.mean(mae_vals))
        mae_se = float(np.std(mae_vals, ddof=1) / math.sqrt(len(mae_vals)))

        tabela_base.append({
            "modelo": nome,
            "2014": maes_ano[2014],
            "2018": maes_ano[2018],
            "2022": maes_ano[2022],
            "mae_medio": mae_med,
            "se": mae_se,
            "maes_ano": mae_vals,
        })

    df_base = pd.DataFrame(tabela_base).sort_values("mae_medio")
    print(df_base[["modelo", "2014", "2018", "2022", "mae_medio", "se"]].to_string(index=False))

    return df_base, preds_armazenadas, best_h


def rodar_etapa_2_ajustes(base_nome, base_func, preds_base, best_h):
    """Etapa 2: Avalia os 3 ajustes opcionais isoladamente sobre o modelo base vencedor."""
    print("\n" + "=" * 80)
    print(f"ETAPA 2: AVALIACAO DOS AJUSTES OPCIONAIS SOBRE O MODELO BASE: {base_nome}")
    print("=" * 80)

    ajustes = {}
    for k_mu in [1.0, 3.0]:
        ajustes[f"+ Viés Comum (k_mu={int(k_mu)})"] = (
            lambda k_val: lambda p, t, tr: aplicar_ajuste_vies_comum(p, t, tr, k_mu=k_val)
        )(k_mu)

    for gamma in [0.5, 1.0]:
        ajustes[f"+ Voto Útil (gamma={gamma})"] = (
            lambda g_val: lambda p, t, tr: aplicar_ajuste_voto_util(p, t, tr, gamma=g_val)
        )(gamma)

    for w in [0.5, 1.0]:
        ajustes[f"+ Prior Nanicos (w={w})"] = (
            lambda w_val: lambda p, t, tr: aplicar_ajuste_priors_nanicos(p, t, w=w_val)
        )(w)

    tabela_ajustes = []
    mae_base_vals = [
        calcular_mae_eleicao(preds_base[(base_nome, t)], carregar_resultado_tse(t))
        for t in ANOS_TESTE_EXPANDING
    ]
    tabela_ajustes.append({
        "ajuste": f"{base_nome} (Base Puro)",
        "2014": mae_base_vals[0],
        "2018": mae_base_vals[1],
        "2022": mae_base_vals[2],
        "mae_medio": np.mean(mae_base_vals),
        "se": np.std(mae_base_vals, ddof=1) / math.sqrt(len(mae_base_vals)),
        "delta_vs_base": 0.0,
        "se_delta": 0.0,
        "aprovado": True,
    })

    for a_nome, a_func in ajustes.items():
        maes_ano = {}
        for t in ANOS_TESTE_EXPANDING:
            tr = TREINO_EXPANDING[t]
            p_base = preds_base[(base_nome, t)]
            p_adj = a_func(p_base, t, tr)
            res_tse = carregar_resultado_tse(t)
            maes_ano[t] = calcular_mae_eleicao(p_adj, res_tse)

        mae_vals = [maes_ano[t] for t in ANOS_TESTE_EXPANDING]
        mae_med = float(np.mean(mae_vals))
        mae_se = float(np.std(mae_vals, ddof=1) / math.sqrt(len(mae_vals)))

        delta_bar, se_delta = calcular_diferenca_e_se(mae_vals, mae_base_vals)
        aprovado = bool(delta_bar < -se_delta)

        tabela_ajustes.append({
            "ajuste": a_nome,
            "2014": maes_ano[2014],
            "2018": maes_ano[2018],
            "2022": maes_ano[2022],
            "mae_medio": mae_med,
            "se": mae_se,
            "delta_vs_base": delta_bar,
            "se_delta": se_delta,
            "aprovado": aprovado,
        })

    df_aj = pd.DataFrame(tabela_ajustes)
    print(df_aj[["ajuste", "2014", "2018", "2022", "mae_medio", "delta_vs_base", "se_delta", "aprovado"]].to_string(index=False))
    return df_aj


def rodar_loeo_completo(base_func, best_h):
    """Executa validacao Leave-One-Election-Out (LOEO) para comparacao metodologica."""
    print("\n" + "=" * 80)
    print("VALIDACAO LEAVE-ONE-ELECTION-OUT (LOEO: 2006, 2010, 2014, 2018, 2022)")
    print("=" * 80)

    configs_loeo = {
        "M0": lambda df, t, tr: estimar_m0(df, t),
        f"M1 (h={int(best_h)})": lambda df, t, tr: estimar_m1(df, t, meia_vida=best_h),
        f"M2 (h={int(best_h)}, k=3)": lambda df, t, tr: estimar_m2(df, t, tr, meia_vida=best_h, k_shrinkage=3.0),
        "M3 (alpha=1.0)": lambda df, t, tr: estimar_m3(df, t, tr, meia_vida=best_h, alpha=1.0),
    }

    tabela_loeo = []
    for nome, func in configs_loeo.items():
        maes_ano = {}
        for t in TODOS_ANOS_LOEO:
            tr = [y for y in TODOS_ANOS_LOEO if y != t]
            df_t = carregar_pesquisas_historicas(t)
            res_tse = carregar_resultado_tse(t)
            p = func(df_t, t, tr)
            maes_ano[t] = calcular_mae_eleicao(p, res_tse)

        vals = [maes_ano[y] for y in TODOS_ANOS_LOEO]
        tabela_loeo.append({
            "modelo": nome,
            "2006": maes_ano[2006],
            "2010": maes_ano[2010],
            "2014": maes_ano[2014],
            "2018": maes_ano[2018],
            "2022": maes_ano[2022],
            "mae_medio": np.mean(vals),
            "se": np.std(vals, ddof=1) / math.sqrt(len(vals)),
        })

    df_loeo = pd.DataFrame(tabela_loeo)
    print(df_loeo[["modelo", "2006", "2010", "2014", "2018", "2022", "mae_medio", "se"]].to_string(index=False))
    return df_loeo


def rodar_backtest_adicionais_com_contas():
    """Backtest da Aba 2 com as contas exatas de diferenca e erro padrao."""
    print("\n" + "=" * 80)
    print("BACKTEST DA ABA 2: AGREGADOS ELEITORAIS E REGRA DE EMPATE COM CONTAS")
    print("=" * 80)

    tse_adicionais = {
        2006: {"abstencao": 16.75, "brancos": 2.73, "nulos": 5.68},
        2010: {"abstencao": 18.12, "brancos": 3.13, "nulos": 5.51},
        2014: {"abstencao": 19.39, "brancos": 3.84, "nulos": 5.80},
        2018: {"abstencao": 20.33, "brancos": 2.65, "nulos": 6.14},
        2022: {"abstencao": 20.95, "brancos": 1.59, "nulos": 2.82},
    }

    metodos = ["Persistência (Random Walk)", "Média Móvel Histórica", "Tendência Linear"]
    variaveis = ["abstencao", "brancos", "nulos"]

    resultados = {}
    for var in variaveis:
        print(f"\n--- Agregado: {var.upper()} ---")
        erros_por_metodo = {}
        for met in metodos:
            erros = []
            for t in ANOS_TESTE_EXPANDING:
                tr = TREINO_EXPANDING[t]
                y_tr = [tse_adicionais[y][var] for y in tr]
                y_real = tse_adicionais[t][var]

                if met == "Persistência (Random Walk)":
                    pred = y_tr[-1]
                elif met == "Média Móvel Histórica":
                    pred = float(np.mean(y_tr))
                elif met == "Tendência Linear":
                    X_tr = np.array(tr).reshape(-1, 1)
                    reg = LinearRegression().fit(X_tr, y_tr)
                    pred = float(reg.predict(np.array([[t]]))[0])

                erros.append(abs(pred - y_real))
            erros_por_metodo[met] = erros
            print(f"  {met:30s}: 2014={erros[0]:.3f}, 2018={erros[1]:.3f}, 2022={erros[2]:.3f} | MAE={np.mean(erros):.4f}")

        # Compara pares
        e_lin = erros_por_metodo["Tendência Linear"]
        e_pers = erros_por_metodo["Persistência (Random Walk)"]
        e_med = erros_por_metodo["Média Móvel Histórica"]

        d_lin_pers, se_lin_pers = calcular_diferenca_e_se(e_lin, e_pers)
        d_med_pers, se_med_pers = calcular_diferenca_e_se(e_med, e_pers)
        d_lin_med, se_lin_med = calcular_diferenca_e_se(e_lin, e_med)

        print("  Contas de Desempate:")
        print(f"    Linear vs Persistência: Delta={d_lin_pers:+.4f}, SE={se_lin_pers:.4f} -> Empate? {abs(d_lin_pers) < se_lin_pers}")
        print(f"    Média vs Persistência:  Delta={d_med_pers:+.4f}, SE={se_med_pers:.4f} -> Empate? {abs(d_med_pers) < se_med_pers}")
        print(f"    Linear vs Média:        Delta={d_lin_med:+.4f}, SE={se_lin_med:.4f} -> Empate? {abs(d_lin_med) < se_lin_med}")

        resultados[var] = erros_por_metodo

    return resultados, tse_adicionais


def calcular_estatisticas_margem_top2_e_p80():
    """Calcula o erro da margem do Top-2 (1o menos 2o) e faixas empiricas com P80."""
    print("\n" + "=" * 80)
    print("ESTATISTICAS DA MARGEM DO TOP-2 E FAIXAS EMPIRICAS COM PERCENTIL 80 (P80)")
    print("=" * 80)

    erros_margem_m0 = []
    erros_margem_final = []

    erros_top2 = []
    erros_34 = []
    erros_demais = []

    for t in ANOS_TESTE_EXPANDING:
        df_t = carregar_pesquisas_historicas(t)
        res_tse = carregar_resultado_tse(t)
        tr = TREINO_EXPANDING[t]

        cands_sorted_real = sorted(res_tse.keys(), key=lambda c: res_tse[c], reverse=True)
        c1_real, c2_real = cands_sorted_real[0], cands_sorted_real[1]
        margem_real = res_tse[c1_real] - res_tse[c2_real]

        # M0
        p0 = estimar_m0(df_t, t)
        margem_p0 = p0[c1_real] - p0[c2_real]
        err_m_p0 = abs(margem_p0 - margem_real)
        erros_margem_m0.append(err_m_p0)

        # Final Aprovado (M0 + Vies k=3 + Voto Util gamma=1.0)
        p_f = aplicar_ajuste_vies_comum(p0, t, tr, k_mu=3.0)
        p_f = aplicar_ajuste_voto_util(p_f, t, tr, gamma=1.0)
        margem_f = p_f[c1_real] - p_f[c2_real]
        err_m_f = abs(margem_f - margem_real)
        erros_margem_final.append(err_m_f)

        print(f"Ano {t}: Margem Real ({c1_real} - {c2_real}) = {margem_real:.2f}%")
        print(f"         M0 Margem = {margem_p0:.2f}% | Erro Margem M0 = {err_m_p0:.2f} p.p.")
        print(f"         Final Margem = {margem_f:.2f}% | Erro Margem Final = {err_m_f:.2f} p.p.")

        cands_by_pesq = sorted(p_f.keys(), key=lambda c: p_f[c], reverse=True)
        for rank, c in enumerate(cands_by_pesq, 1):
            err = abs(p_f[c] - res_tse[c])
            if rank <= 2:
                erros_top2.append(err)
            elif rank in [3, 4]:
                erros_34.append(err)
            else:
                erros_demais.append(err)

    print("\nResumo da Margem do Top-2:")
    print(f"  Erro Margem M0:    Media = {np.mean(erros_margem_m0):.2f} p.p., Max = {np.max(erros_margem_m0):.2f} p.p., P80 = {np.percentile(erros_margem_m0, 80):.2f} p.p.")
    print(f"  Erro Margem Final: Media = {np.mean(erros_margem_final):.2f} p.p., Max = {np.max(erros_margem_final):.2f} p.p., P80 = {np.percentile(erros_margem_final, 80):.2f} p.p.")

    print("\nFaixas Empiricas de Incerteza do Backtest:")
    print(f"  Grupo 1 (Top-2):   Media = {np.mean(erros_top2):.2f} p.p., P80 = {np.percentile(erros_top2, 80):.2f} p.p.")
    print(f"  Grupo 2 (3º e 4º): Media = {np.mean(erros_34):.2f} p.p., P80 = {np.percentile(erros_34, 80):.2f} p.p.")
    print(f"  Grupo 3 (Demais):  Media = {np.mean(erros_demais):.2f} p.p., P80 = {np.percentile(erros_demais, 80):.2f} p.p.")


def gerar_tabela_sensibilidade_2026(df_2026):
    """Gera tabela de sensibilidade confrontando todas as configuracoes para 2026."""
    print("\n" + "=" * 80)
    print("TABELA DE SENSIBILIDADE: PROJECOES PARA 2026 SOB TODAS AS CONFIGURACOES")
    print("=" * 80)

    tr_all = [2006, 2010, 2014, 2018, 2022]
    p0 = estimar_m0(df_2026, 2026)
    p_vies1 = aplicar_ajuste_vies_comum(p0, 2026, tr_all, k_mu=1.0)
    p_vies3 = aplicar_ajuste_vies_comum(p0, 2026, tr_all, k_mu=3.0)
    p_util05 = aplicar_ajuste_voto_util(p0, 2026, tr_all, gamma=0.5)
    p_util10 = aplicar_ajuste_voto_util(p0, 2026, tr_all, gamma=1.0)
    p_nan05 = aplicar_ajuste_priors_nanicos(p0, 2026, w=0.5)

    # Modelo Oficial Aprovado na Etapa 2 (w=0, pois o prior foi neutro no backtest)
    p_final_oficial = aplicar_ajuste_voto_util(p_vies3, 2026, tr_all, gamma=1.0)

    # Modelo com Prior de Nanicos (Sensibilidade w=0.5)
    p_sens_w05 = aplicar_ajuste_priors_nanicos(p_final_oficial, 2026, w=0.5)

    configs = {
        "M0 Puro": aplicar_maiores_restos_dict(p0),
        "M0 + Viés (k=1)": aplicar_maiores_restos_dict(p_vies1),
        "M0 + Viés (k=3)": aplicar_maiores_restos_dict(p_vies3),
        "M0 + Útil (g=0.5)": aplicar_maiores_restos_dict(p_util05),
        "M0 + Útil (g=1.0)": aplicar_maiores_restos_dict(p_util10),
        "M0 + Nanicos (w=0.5)": aplicar_maiores_restos_dict(p_nan05),
        "Modelo Oficial (w=0)": aplicar_maiores_restos_dict(p_final_oficial),
        "Sensibilidade (w=0.5)": aplicar_maiores_restos_dict(p_sens_w05),
    }

    df_sens = pd.DataFrame(configs)
    df_sens["Partido"] = [PARTIDOS_EDITAL[c] for c in df_sens.index]
    cols_order = ["Partido", "M0 Puro", "M0 + Viés (k=3)", "M0 + Útil (g=1.0)", "Modelo Oficial (w=0)", "Sensibilidade (w=0.5)"]
    print(df_sens[cols_order].to_string())

    return p_final_oficial, configs


if __name__ == "__main__":
    df_base, preds_base, best_h = rodar_etapa_1_modelos_base()

    def func_base(df, t, tr):
        return estimar_m0(df, t)

    df_ajustes = rodar_etapa_2_ajustes("M0", func_base, preds_base, best_h)
    df_loeo = rodar_loeo_completo(func_base, best_h)
    res_ad, tse_ad = rodar_backtest_adicionais_com_contas()
    calcular_estatisticas_margem_top2_e_p80()

    df_2026 = pd.read_csv(MANUAL_DIR / "pesquisas_2026.csv")
    p_final_oficial, configs_sens = gerar_tabela_sensibilidade_2026(df_2026)

    # Gera planilha oficial de entrega preliminar
    ad2026 = {"abstencao": 22.3, "brancos": 1.6, "nulos": 2.8}
    gerar_planilha_entrega(p_final_oficial, ad2026, OUTPUTS_DIR / "previsao_2026.xlsx")
    print("\nOK: outputs/previsao_2026.xlsx gerada com o Modelo Oficial Aprovado (w=0).")
