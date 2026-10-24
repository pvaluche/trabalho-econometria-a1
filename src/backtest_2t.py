"""
src/backtest_2t.py
Motor de modelagem econometrica e backtest (Expanding Window e LOEO) para o 2o Turno.
Implementa estritamente o protocolo definido em protocolo/PRE_REGISTRO_2T.md.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from src.backtest import (
    BLOCOS_POLITICOS,
    HISTORICO_CANDIDATOS,
    converter_pesquisa_validos,
    obter_pesquisas_eleicao,
    padronizar_nome_instituto,
)
from src.config import MANUAL_DIR, PROCESSED_DIR

DATAS_CORTE_2T = {
    2006: date(2006, 10, 28),
    2010: date(2010, 10, 30),
    2014: date(2014, 10, 25),
    2018: date(2018, 10, 27),
    2022: date(2022, 10, 29),
    2026: date(2026, 10, 24),
}

# Resultados oficiais de 1o turno (PT vs Adv principal em % de votos validos)
TSE_1T_TOP2 = {
    2006: (48.61, 41.64),
    2010: (46.91, 32.61),
    2014: (41.59, 33.55),
    2018: (29.28, 46.03),
    2022: (48.43, 43.20),
    2026: (45.1628, 47.0278),
}

# Resultados oficiais de 2o turno (% de votos validos do candidato do PT)
TSE_2T_PT = {
    2006: 60.8265,
    2010: 56.0530,
    2014: 51.6391,
    2018: 44.8698,
    2022: 50.9024,
}


def carregar_pesquisas_2t_historicas(ano: int | None = None) -> pd.DataFrame:
    path = PROCESSED_DIR / "pesquisas_historicas_2t.parquet"
    df = pd.read_parquet(path)
    if ano is not None:
        df = df[df["eleicao"] == ano].copy()
    return df


def carregar_pesquisas_2026_2t() -> pd.DataFrame:
    path = MANUAL_DIR / "pesquisas_2026_2t.csv"
    df = pd.read_csv(path)
    df["instituto"] = df["instituto"].apply(padronizar_nome_instituto)
    df["pct_pt_validos"] = (
        df["Luiz Inácio Lula da Silva"]
        / (df["Luiz Inácio Lula da Silva"] + df["Flávio Bolsonaro"])
        * 100.0
    )
    df["pct_adv_validos"] = 100.0 - df["pct_pt_validos"]
    return df


def obter_semi_erros_margem_1t(ano: int) -> dict[str, float]:
    """
    Retorna o semi-erro da margem Top-2 no 1o turno para cada instituto na eleicao `ano`:
        e_{j, 1T}^{margem/2} = ((v_hat_{PT,1T} - v_hat_{Adv,1T}) - (v_{PT,1T}^{TSE} - v_{Adv,1T}^{TSE})) / 2
    Um valor positivo significa que o instituto superestimou a vantagem do PT sobre o adversario no 1o turno.
    """
    tse_pt, tse_adv = TSE_1T_TOP2[ano]
    margem_real = tse_pt - tse_adv

    if ano == 2026:
        # Usa data/manual/pesquisas_2026.csv + data/manual/vespera_extra_2026.csv
        df_1t = pd.read_csv(MANUAL_DIR / "pesquisas_2026.csv")
        df_1t["inst"] = df_1t["instituto"].apply(padronizar_nome_instituto)
        df_last = df_1t.sort_values("data_divulgacao", ascending=False).drop_duplicates("inst")
        erros = {}
        cands = HISTORICO_CANDIDATOS[2026]
        for _, r in df_last.iterrows():
            val = converter_pesquisa_validos(r, cands)
            m_hat = val["Luiz Inácio Lula da Silva"] - val["Flávio Bolsonaro"]
            erros[r["inst"]] = (m_hat - margem_real) / 2.0

        # Carrega pesquisas de vespera pós-corte de 03/10/2026 auditadas em data/manual/vespera_extra_2026.csv
        path_extra = MANUAL_DIR / "vespera_extra_2026.csv"
        if path_extra.exists():
            df_extra = pd.read_csv(path_extra)
            df_extra["inst"] = df_extra["instituto"].apply(padronizar_nome_instituto)
            for _, r in df_extra.iterrows():
                v_lula = float(r["Luiz Inácio Lula da Silva"])
                v_flavio = float(r["Flávio Bolsonaro"])
                erros[r["inst"]] = ((v_lula - v_flavio) - margem_real) / 2.0
        return erros

    df_1t = obter_pesquisas_eleicao(ano)
    df_1t["inst"] = df_1t["instituto"].apply(padronizar_nome_instituto)
    df_last = df_1t.sort_values("data_divulgacao", ascending=False).drop_duplicates("inst")

    cands = HISTORICO_CANDIDATOS[ano]
    c_pt = BLOCOS_POLITICOS[ano]["pt"][0]
    c_adv = BLOCOS_POLITICOS[ano]["adv"][0]

    erros = {}
    for _, r in df_last.iterrows():
        val = converter_pesquisa_validos(r, cands)
        m_hat = val[c_pt] - val[c_adv]
        erros[r["inst"]] = (m_hat - margem_real) / 2.0
    return erros


def estimar_m0_2t(df_2t: pd.DataFrame) -> float:
    """
    M0_2T: Media simples da ultima pesquisa de cada instituto na janela do 2o turno.
    Retorna o percentual previsto de votos validos do candidato do PT.
    """
    df = df_2t.copy()
    df["inst"] = df["instituto"].apply(padronizar_nome_instituto)
    df_last = df.sort_values("data_divulgacao", ascending=False).drop_duplicates("inst")
    return float(df_last["pct_pt_validos"].mean())


def estimar_m1_2t(df_2t: pd.DataFrame, ano: int, meia_vida: float = 5.0) -> float:
    """
    M1_2T: Media ponderada de todas as pesquisas da janela do 2o turno por recencia e raiz da amostra.
    """
    df = df_2t.copy()
    dt_corte = pd.to_datetime(DATAS_CORTE_2T[ano])
    dt_div = pd.to_datetime(df["data_divulgacao"])
    delta_dias = (dt_corte - dt_div).dt.days.clip(lower=0).astype(float)
    amostra = df["amostra"].fillna(2000.0).clip(lower=500.0).astype(float)

    pesos = np.sqrt(amostra) * np.power(2.0, -delta_dias / float(meia_vida))
    return float(np.average(df["pct_pt_validos"].values, weights=pesos.values))


def estimar_m2_2t_peso_1t(df_2t: pd.DataFrame, ano: int, sigma0: float = 2.0) -> float:
    """
    M2_2T: Pondera a ultima pesquisa de cada instituto no 2o turno pelo inverso do erro
    quadratico cometido pelo instituto na margem do 1o turno (3 semanas antes):
        w_j = 1 / (e_{j,1T}^2 + sigma0^2)
    """
    df = df_2t.copy()
    df["inst"] = df["instituto"].apply(padronizar_nome_instituto)
    df_last = df.sort_values("data_divulgacao", ascending=False).drop_duplicates("inst")

    erros_1t = obter_semi_erros_margem_1t(ano)
    mediana_abs_erro = float(np.median([abs(v) for v in erros_1t.values()])) if erros_1t else 2.5

    pesos = []
    vals = []
    for _, r in df_last.iterrows():
        e1 = erros_1t.get(r["inst"], mediana_abs_erro)
        w = 1.0 / (float(e1) ** 2 + float(sigma0) ** 2)
        pesos.append(w)
        vals.append(float(r["pct_pt_validos"]))

    return float(np.average(vals, weights=pesos))


def aplicar_ajuste_persistencia_1t(
    df_2t: pd.DataFrame,
    ano: int,
    rho: float,
    modo_base: str = "M0_2T",
    param_base: float = 2.0,
) -> float:
    """
    Etapa 2 (Ajuste 1): Desconta de cada instituto no 2o turno uma fracao `rho` do seu
    semi-erro na margem do 1o turno:
        v_hat_{j, PT, 2T}^{corr} = v_hat_{j, PT, 2T} - rho * e_{j, 1T}^{margem/2}
    """
    df = df_2t.copy()
    df["inst"] = df["instituto"].apply(padronizar_nome_instituto)
    erros_1t = obter_semi_erros_margem_1t(ano)

    # Se instituto nao fez pesquisa no 1T, usa o erro medio do 1T (vies comum de 1T)
    media_erro_1t = float(np.mean(list(erros_1t.values()))) if erros_1t else 0.0

    df["pct_pt_validos"] = df.apply(
        lambda r: (
            float(r["pct_pt_validos"]) - float(rho) * float(erros_1t.get(r["inst"], media_erro_1t))
        ),
        axis=1,
    )

    if modo_base == "M0_2T":
        return estimar_m0_2t(df)
    elif modo_base == "M1_2T":
        return estimar_m1_2t(df, ano, meia_vida=param_base)
    elif modo_base == "M2_2T":
        return estimar_m2_2t_peso_1t(df, ano, sigma0=param_base)
    return estimar_m0_2t(df)


def estimar_rho_ols_treino(anos_treino: list[int]) -> float:
    """Estima o coeficiente de persistencia `rho` via OLS sem intercepto nos anos de treino."""
    x_list, y_list = [], []
    for a in anos_treino:
        df_2t = carregar_pesquisas_2t_historicas(a)
        df_2t["inst"] = df_2t["instituto"].apply(padronizar_nome_instituto)
        df_last = df_2t.sort_values("data_divulgacao", ascending=False).drop_duplicates("inst")
        erros_1t = obter_semi_erros_margem_1t(a)
        real_pt = TSE_2T_PT[a]
        for _, r in df_last.iterrows():
            if r["inst"] in erros_1t:
                x_list.append(float(erros_1t[r["inst"]]))
                y_list.append(float(r["pct_pt_validos"]) - real_pt)
    if not x_list:
        return 0.0
    x = np.array(x_list)
    y = np.array(y_list)
    denom = float(np.sum(x**2))
    return float(np.sum(x * y) / denom) if denom > 0 else 0.0


def aplicar_ajuste_vies_comum_2t(
    pred_pt_base: float,
    anos_treino: list[int],
    k_mu: float,
    preds_base_por_ano: dict[int, float],
) -> float:
    """
    Etapa 2 (Ajuste 2): Desconta o vies comum historico das pesquisas no 2o turno
    com shrinkage Bayesiano N / (N + k_mu).
    """
    erros_treino = [preds_base_por_ano[a] - TSE_2T_PT[a] for a in anos_treino]
    n_tr = len(erros_treino)
    if n_tr == 0:
        return pred_pt_base
    mu_bar = float(np.mean(erros_treino))
    mu_hat = (n_tr / (n_tr + float(k_mu))) * mu_bar
    return float(pred_pt_base - mu_hat)


def calcular_taus_historicos(anos: list[int] | None = None) -> dict[int, float]:
    """
    Retorna a fracao aparente `tau_t` dos votos de terceiros colocados do 1o turno
    capturada pelo candidato do PT entre o 1o e o 2o turno:
        tau_t = (V_{PT,2T,t} - V_{PT,1T,t}) / (100 - V_{PT,1T,t} - V_{Adv,1T,t})
    Nota: em 2006, tau = 1.2530 (> 1.0) e um outlier porque o adversario (Alckmin)
    perdeu votos validos do 1o turno (41.64%) para o 2o turno (39.17%).
    """
    if anos is None:
        anos = [2006, 2010, 2014, 2018, 2022]
    taus = {}
    for a in anos:
        v_pt_1t, v_adv_1t = TSE_1T_TOP2[a]
        terc = 100.0 - v_pt_1t - v_adv_1t
        if terc > 0:
            taus[a] = (TSE_2T_PT[a] - v_pt_1t) / terc
    return taus


def calcular_prior_estrutural_1t(
    ano: int,
    anos_treino: list[int],
    estatistica: str = "media",
) -> float:
    """
    Calcula o prior estrutural do 2o turno a partir do resultado oficial do 1o turno:
        pct_pt_2t = pct_pt_1t + tau * pct_terceiros_1t
    onde `tau` pode ser a `"media"` ou a `"mediana"` dos `tau_t` nos anos de treino.
    """
    taus_map = calcular_taus_historicos(anos_treino)
    taus = list(taus_map.values())
    if not taus:
        tau_ref = 0.45
    elif estatistica == "mediana":
        tau_ref = float(np.median(taus))
    else:
        tau_ref = float(np.mean(taus))

    v_pt_1t, v_adv_1t = TSE_1T_TOP2[ano]
    terc = 100.0 - v_pt_1t - v_adv_1t
    return float(np.clip(v_pt_1t + tau_ref * terc, 0.0, 100.0))


def calcular_mae_2t(pred_pt: float, ano: int) -> float:
    """No 2o turno (K=2), MAE = |pred_pt - real_pt| = |pred_adv - real_adv|."""
    return abs(float(pred_pt) - TSE_2T_PT[ano])
