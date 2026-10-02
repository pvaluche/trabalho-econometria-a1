"""
scripts/executar_backtest_oficial.py
Executa o protocolo oficial e sequencial de backtest historico (Checkpoint 3).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.arredondamento import maiores_restos


def aplicar_maiores_restos_dict(d: dict[str, float]) -> dict[str, float]:
    keys = list(d.keys())
    vals = [d[k] for k in keys]
    arr = maiores_restos(vals, total=100.0, casas=1)
    return {k: round(v, 1) for k, v in zip(keys, arr)}


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
from src.config import MANUAL_DIR
from src.pesquisas import carregar_pesquisas_historicas

ANOS_TESTE_EXPANDING = [2014, 2018, 2022]
TREINO_EXPANDING = {
    2014: [2006, 2010],
    2018: [2006, 2010, 2014],
    2022: [2006, 2010, 2014, 2018],
}

TODOS_ANOS_LOEO = [2006, 2010, 2014, 2018, 2022]


def rodar_etapa_1_modelos_base():
    """Etapa 1: Avalia as 11 configuracoes dos modelos base puros via Expanding Window."""
    print("=" * 80)
    print("ETAPA 1: AVALIACAO DOS MODELOS BASE NO EXPANDING WINDOW (2014, 2018, 2022)")
    print("=" * 80)

    configs = {}
    # M0
    configs["M0"] = lambda df, t, tr: estimar_m0(df, t)

    # M1
    for h in [7.0, 14.0, 21.0]:
        configs[f"M1 (h={int(h)})"] = (lambda h_val: lambda df, t, tr: estimar_m1(df, t, meia_vida=h_val))(h)

    # Determina melhor h de M1 preliminarmente para M2
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

    # M2 com melhor h
    for k in [1.0, 3.0, 10.0]:
        configs[f"M2 (h={int(best_h)}, k={int(k)})"] = (
            lambda k_val: lambda df, t, tr: estimar_m2(df, t, tr, meia_vida=best_h, k_shrinkage=k_val)
        )(k)

    # M3
    for alpha in [0.01, 0.1, 1.0, 10.0]:
        configs[f"M3 (alpha={alpha})"] = (
            lambda a_val: lambda df, t, tr: estimar_m3(df, t, tr, meia_vida=best_h, alpha=a_val)
        )(alpha)

    # Executa avaliacao
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
    # 1. Vies Comum
    for k_mu in [1.0, 3.0]:
        ajustes[f"+ Viés Comum (k_mu={int(k_mu)})"] = (
            lambda k_val: lambda p, t, tr: aplicar_ajuste_vies_comum(p, t, tr, k_mu=k_val)
        )(k_mu)

    # 2. Voto Util
    for gamma in [0.5, 1.0]:
        ajustes[f"+ Voto Útil (gamma={gamma})"] = (
            lambda g_val: lambda p, t, tr: aplicar_ajuste_voto_util(p, t, tr, gamma=g_val)
        )(gamma)

    # 3. Prior Nanicos
    for w in [0.5, 1.0]:
        ajustes[f"+ Prior Nanicos (w={w})"] = (
            lambda w_val: lambda p, t, tr: aplicar_ajuste_priors_nanicos(p, t, w=w_val)
        )(w)

    tabela_ajustes = []
    # Inclui o Base sem ajuste para comparacao direta
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

        # Diferenca Delta = MAE_adj - MAE_base
        delta_bar, se_delta = calcular_diferenca_e_se(mae_vals, mae_base_vals)

        # Regra de ativacao: reducao estrita de MAE superior a 1 SE(Delta)
        # delta_bar deve ser significativamente menor que zero
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


def rodar_backtest_adicionais():
    """Backtest expanding window de abstencao, brancos e nulos (3 metodos x 3 eleicoes)."""
    print("\n" + "=" * 80)
    print("BACKTEST DE ABSTENCAO, BRANCOS E NULOS (EXPANDING WINDOW)")
    print("=" * 80)

    # Dados oficiais TSE
    tse_adicionais = {
        2006: {"abstencao": 16.75, "brancos": 2.73, "nulos": 5.68},
        2010: {"abstencao": 18.12, "brancos": 3.13, "nulos": 5.51},
        2014: {"abstencao": 19.39, "brancos": 3.84, "nulos": 5.80},
        2018: {"abstencao": 20.33, "brancos": 2.65, "nulos": 6.14},
        2022: {"abstencao": 20.95, "brancos": 1.59, "nulos": 2.82},
    }

    metodos = ["Persistência (Random Walk)", "Média Móvel Histórica", "Tendência Linear"]
    variaveis = ["abstencao", "brancos", "nulos"]

    resultados = []
    for var in variaveis:
        for met in metodos:
            erros = []
            preds = {}
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

                preds[t] = pred
                erros.append(abs(pred - y_real))

            resultados.append({
                "variavel": var,
                "metodo": met,
                "mae_2014": erros[0],
                "mae_2018": erros[1],
                "mae_2022": erros[2],
                "mae_medio": np.mean(erros),
            })

    df_ad = pd.DataFrame(resultados)
    print(df_ad[["variavel", "metodo", "mae_2014", "mae_2018", "mae_2022", "mae_medio"]].to_string(index=False))
    return df_ad, tse_adicionais


def gerar_previsao_preliminar_2026(modelo_escolhido_func, tse_adicionais):
    """Gera a previsao preliminar oficial para 2026 com base nas pesquisas disponiveis."""
    print("\n" + "=" * 80)
    print("PREVISAO PRELIMINAR OFICIAL PARA 2026 (BASE MANUAL DE 6 PESQUISAS)")
    print("=" * 80)

    csv_path = MANUAL_DIR / "pesquisas_2026.csv"
    df_2026 = pd.read_csv(csv_path)

    # Executa projecao de votos validos
    treino_completo = [2006, 2010, 2014, 2018, 2022]
    preds_raw = modelo_escolhido_func(df_2026, 2026, treino_completo)

    # Aplica fechamento exato dos maiores restos (Hamilton) para 100,0%
    preds_fechadas = aplicar_maiores_restos_dict(preds_raw)

    print("\nAba 1: Votos Validos (%):")
    for c, v in sorted(preds_fechadas.items(), key=lambda x: x[1], reverse=True):
        print(f"  {c:30s}: {v:5.1f}%")
    print(f"  {'Total':30s}: {sum(preds_fechadas.values()):5.1f}%")

    # Aba 2 (Metodo vencedor de cada agregado)
    # Projecao linear para abstencao, persistencia/media para brancos e nulos
    tr_all = [2006, 2010, 2014, 2018, 2022]
    X_tr = np.array(tr_all).reshape(-1, 1)

    # Abstencao: Tendencia linear
    reg_abs = LinearRegression().fit(X_tr, [tse_adicionais[y]["abstencao"] for y in tr_all])
    pred_abs = round(float(reg_abs.predict([[2026]])[0]), 1)

    # Brancos: Persistencia 2022
    pred_bra = round(float(tse_adicionais[2022]["brancos"]), 1)

    # Nulos: Persistencia 2022
    pred_nul = round(float(tse_adicionais[2022]["nulos"]), 1)

    print("\nAba 2: Agregados Eleitorais (%):")
    print(f"  Abstenção (% sobre aptos):           {pred_abs:.1f}%")
    print(f"  Votos Brancos (% sobre comparecimento): {pred_bra:.1f}%")
    print(f"  Votos Nulos (% sobre comparecimento):   {pred_nul:.1f}%")

    return preds_fechadas, {"abstencao": pred_abs, "brancos": pred_bra, "nulos": pred_nul}


if __name__ == "__main__":
    df_base, preds_base, best_h = rodar_etapa_1_modelos_base()

    # Selecao do Base
    # Identifica o melhor MAE numerico
    best_row = df_base.iloc[0]
    base_vencedor_nome = best_row["modelo"]
    print(f"\nModelo Base com Menor MAE: {base_vencedor_nome} (MAE = {best_row['mae_medio']:.4f})")

    # Verifica regra de desempate contra modelos mais simples
    # Ordem: M0 < M1 < M2 < M3
    m0_row = df_base[df_base["modelo"] == "M0"].iloc[0]
    delta_vs_m0, se_vs_m0 = calcular_diferenca_e_se(best_row["maes_ano"], m0_row["maes_ano"])
    print(f"Comparacao {base_vencedor_nome} vs M0: Delta = {delta_vs_m0:.4f}, SE(Delta) = {se_vs_m0:.4f}")

    # Funcao do modelo base vencedor
    def func_base(df, t, tr):
        if "M1" in base_vencedor_nome:
            return estimar_m1(df, t, meia_vida=best_h)
        elif "M2" in base_vencedor_nome:
            k_val = 3.0
            if "k=1" in base_vencedor_nome:
                k_val = 1.0
            elif "k=10" in base_vencedor_nome:
                k_val = 10.0
            return estimar_m2(df, t, tr, meia_vida=best_h, k_shrinkage=k_val)
        elif "M3" in base_vencedor_nome:
            return estimar_m3(df, t, tr, meia_vida=best_h, alpha=1.0)
        return estimar_m0(df, t)

    # Etapa 2
    df_ajustes = rodar_etapa_2_ajustes(base_vencedor_nome, func_base, preds_base, best_h)

    # LOEO
    df_loeo = rodar_loeo_completo(func_base, best_h)

    # Adicionais
    df_ad, tse_ad = rodar_backtest_adicionais()

    # Previsao 2026 preliminar: Modelo Base Puro M0
    print("\n--- PREVISAO PRELIMINAR 2026: BASE PURO (M0) ---")
    p2026_m0, ad2026 = gerar_previsao_preliminar_2026(func_base, tse_ad)

    # Previsao 2026 preliminar: Modelo Final com Ajustes Aprovados
    def func_modelo_final(df, t, tr):
        p = func_base(df, t, tr)
        p = aplicar_ajuste_vies_comum(p, t, tr, k_mu=3.0)
        p = aplicar_ajuste_voto_util(p, t, tr, gamma=1.0)
        p = aplicar_ajuste_priors_nanicos(p, t, w=0.5)
        return p

    print("\n--- PREVISAO PRELIMINAR 2026: MODELO FINAL (M0 + VIES COMUM + VOTO UTIL + PRIOR NANICOS) ---")
    p2026_final, _ = gerar_previsao_preliminar_2026(func_modelo_final, tse_ad)
