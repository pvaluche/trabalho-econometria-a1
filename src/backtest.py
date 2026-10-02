"""
src/backtest.py
Motor econometrico de backtest historico e avaliacao de modelos (M0, M1, M2, M3 + Ajustes).
Segue estritamente as regras de governanca do PRE_REGISTRO.md e Emendas 1, 2 e 3.
"""

from __future__ import annotations

import math
from datetime import date
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from src.config import CANDIDATOS_EDITAL, PROCESSED_DIR
from src.filtros import VESPERAS
from src.incumbencia import obter_incumbencia
from src.nanicos import calcular_priors_nanicos_tse
from src.pesquisas import carregar_pesquisas_historicas
from src.tse import calcular_votos_validos_candidatos

# --------------------------------------------------------------------------- #
# Mapeamentos e Candidatos por Eleicao
# --------------------------------------------------------------------------- #

CANDIDATOS_URNA_TSE: dict[int, dict[str, str]] = {
    2006: {
        "Luiz Inácio Lula da Silva": "LULA",
        "Geraldo Alckmin": "GERALDO ALCKMIN",
        "Heloísa Helena": "HELOÍSA HELENA",
        "Cristovam Buarque": "CRISTOVAM BUARQUE",
        "Ana Maria Rangel": "ANA MARIA RANGEL",
        "José Maria Eymael": "JOSÉ MARIA EYMAEL",
        "Luciano Bivar": "LUCIANO BIVAR",
    },
    2010: {
        "Dilma Rousseff": "DILMA",
        "José Serra": "JOSÉ SERRA",
        "Marina Silva": "MARINA SILVA",
        "Plínio de Arruda Sampaio": "PLÍNIO",
        "José Maria Eymael": "EYMAEL",
        "Zé Maria": "ZÉ MARIA",
        "Levy Fidelix": "LEVY FIDELIX",
        "Ivan Pinheiro": "IVAN PINHEIRO",
        "Rui Costa Pimenta": "RUI COSTA PIMENTA",
    },
    2014: {
        "Dilma Rousseff": "DILMA",
        "Aécio Neves": "AÉCIO NEVES",
        "Marina Silva": "MARINA SILVA",
        "Luciana Genro": "LUCIANA GENRO",
        "Pastor Everaldo": "PASTOR EVERALDO",
        "Eduardo Jorge": "EDUARDO JORGE",
        "Levy Fidelix": "LEVY FIDELIX",
        "Zé Maria": "ZÉ MARIA",
        "José Maria Eymael": "EYMAEL",
        "Mauro Iasi": "MAURO IASI",
        "Rui Costa Pimenta": "RUI COSTA PIMENTA",
    },
    2018: {
        "Jair Bolsonaro": "JAIR BOLSONARO",
        "Fernando Haddad": "FERNANDO HADDAD",
        "Ciro Gomes": "CIRO GOMES",
        "Geraldo Alckmin": "GERALDO ALCKMIN",
        "João Amoêdo": "JOÃO AMOÊDO",
        "Cabo Daciolo": "CABO DACIOLO",
        "Henrique Meirelles": "HENRIQUE MEIRELLES",
        "Marina Silva": "MARINA SILVA",
        "Alvaro Dias": "ALVARO DIAS",
        "Guilherme Boulos": "GUILHERME BOULOS",
        "Vera Lúcia": "VERA",
        "José Maria Eymael": "EYMAEL",
        "João Goulart Filho": "JOÃO GOULART FILHO",
    },
    2022: {
        "Luiz Inácio Lula da Silva": "LULA",
        "Jair Bolsonaro": "JAIR BOLSONARO",
        "Simone Tebet": "SIMONE TEBET",
        "Ciro Gomes": "CIRO GOMES",
        "Soraya Thronicke": "SORAYA THRONICKE",
        "Felipe D'Avila": "FELIPE D AVILA",
        "Padre Kelmon": "PADRE KELMON",
        "Léo Péricles": "LÉO PÉRICLES",
        "Sofia Manzano": "SOFIA MANZANO",
        "Vera Lúcia": "VERA",
        "Constituinte Eymael": "CONSTITUINTE EYMAEL",
    },
}

HISTORICO_CANDIDATOS: dict[int, list[str]] = {
    ano: list(cands.keys()) for ano, cands in CANDIDATOS_URNA_TSE.items()
}
HISTORICO_CANDIDATOS[2026] = CANDIDATOS_EDITAL

TSE_NAMES_MAP: dict[int, dict[str, str]] = CANDIDATOS_URNA_TSE

BLOCOS_POLITICOS: dict[int, dict[str, list[str]]] = {
    2006: {
        "pt": ["Luiz Inácio Lula da Silva"],
        "adv": ["Geraldo Alckmin"],
    },
    2010: {
        "pt": ["Dilma Rousseff"],
        "adv": ["José Serra"],
    },
    2014: {
        "pt": ["Dilma Rousseff"],
        "adv": ["Aécio Neves"],
    },
    2018: {
        "pt": ["Fernando Haddad"],
        "adv": ["Jair Bolsonaro"],
    },
    2022: {
        "pt": ["Luiz Inácio Lula da Silva"],
        "adv": ["Jair Bolsonaro"],
    },
    2026: {
        "pt": ["Luiz Inácio Lula da Silva"],
        "adv": ["Flávio Bolsonaro"],
    },
}


def identificar_bloco(eleicao: int, candidato: str) -> str:
    """Classifica o candidato no bloco 'pt', 'adv' ou 'demais'."""
    blocos = BLOCOS_POLITICOS.get(eleicao, {})
    if candidato in blocos.get("pt", []):
        return "pt"
    if candidato in blocos.get("adv", []):
        return "adv"
    return "demais"


def padronizar_nome_instituto(inst: str) -> str:
    """Aplica a unificacao metodologica oficial Ibope -> Ipec."""
    if str(inst).strip().lower() in ["ibope", "ipec"]:
        return "Ibope/Ipec"
    return str(inst).strip()


_CACHE_TSE: dict[int, dict[str, float]] = {}
_CACHE_PESQUISAS: dict[int, pd.DataFrame] = {}


def carregar_resultado_tse(eleicao: int) -> dict[str, float]:
    """Carrega os resultados oficiais do TSE em percentual de votos validos com cache em memoria."""
    if eleicao == 2026:
        return {}
    if eleicao not in _CACHE_TSE:
        tse_path = PROCESSED_DIR / f"votacao_candidato_{eleicao}.parquet"
        df_tse = pd.read_parquet(tse_path)
        res_tse = calcular_votos_validos_candidatos(df_tse)
        mapping = TSE_NAMES_MAP[eleicao]
        _CACHE_TSE[eleicao] = {p_cand: res_tse[tse_name] for p_cand, tse_name in mapping.items()}
    return _CACHE_TSE[eleicao]


def obter_pesquisas_eleicao(eleicao: int) -> pd.DataFrame:
    """Retorna pesquisas historicas da eleicao com cache em memoria."""
    if eleicao not in _CACHE_PESQUISAS:
        _CACHE_PESQUISAS[eleicao] = carregar_pesquisas_historicas(eleicao)
    return _CACHE_PESQUISAS[eleicao].copy()


def renormalizar_votos(preds: dict[str, float]) -> dict[str, float]:
    """Trunca valores negativos em zero e renormaliza para somar 100,0%."""
    clipped = {k: max(0.0, float(v)) for k, v in preds.items()}
    soma = sum(clipped.values())
    if soma <= 0:
        n = len(clipped)
        return {k: 100.0 / n for k in clipped}
    return {k: (v / soma) * 100.0 for k, v in clipped.items()}


def converter_pesquisa_validos(row: pd.Series, candidatos: list[str]) -> dict[str, float]:
    """Converte intencoes brutas de uma pesquisa para votos validos."""
    vals = {}
    for c in candidatos:
        val = row.get(c, np.nan)
        if pd.isna(val) and c == "Felipe D'Avila":
            val = row.get("Felipe D Avila", np.nan)
        if pd.notna(val) and float(val) > 0:
            vals[c] = float(val)
        else:
            vals[c] = 0.0
    soma = sum(vals.values())
    if soma <= 0:
        return {c: 100.0 / len(candidatos) for c in candidatos}
    return {c: (v / soma) * 100.0 for c, v in vals.items()}


# --------------------------------------------------------------------------- #
# Modelos Base
# --------------------------------------------------------------------------- #


def estimar_m0(df_pesquisas: pd.DataFrame, eleicao: int) -> dict[str, float]:
    """
    Modelo M0: Media simples da ultima pesquisa de cada instituto.
    """
    candidatos = HISTORICO_CANDIDATOS[eleicao]
    df = df_pesquisas.copy()
    df["instituto_clean"] = df["instituto"].apply(padronizar_nome_instituto)

    # Identifica ultima pesquisa por instituto
    df_sorted = df.sort_values("data_divulgacao", ascending=False)
    ultimas = df_sorted.drop_duplicates(subset=["instituto_clean"])

    pesquisas_validas = []
    for _, row in ultimas.iterrows():
        pesquisas_validas.append(converter_pesquisa_validos(row, candidatos))

    if not pesquisas_validas:
        return {c: 100.0 / len(candidatos) for c in candidatos}

    # Media simples entre institutos
    res = {}
    for c in candidatos:
        res[c] = float(np.mean([p[c] for p in pesquisas_validas]))

    return renormalizar_votos(res)


def estimar_m1(df_pesquisas: pd.DataFrame, eleicao: int, meia_vida: float = 14.0) -> dict[str, float]:
    """
    Modelo M1: Media ponderada por recencia (meia-vida exponencial) e tamanho de amostra.
    """
    candidatos = HISTORICO_CANDIDATOS[eleicao]
    vespera = VESPERAS[eleicao].date()

    pesquisas_validas = []
    pesos = []

    for _, row in df_pesquisas.iterrows():
        p_dict = converter_pesquisa_validos(row, candidatos)
        dt_div_str = row["data_divulgacao"]
        dt_div = date.fromisoformat(dt_div_str)
        delta_t = max(0, (vespera - dt_div).days)

        amostra = row.get("amostra", np.nan)
        if pd.isna(amostra) or amostra <= 0:
            amostra = 2000.0  # Padrao historico mediano

        peso = math.sqrt(amostra) * math.exp(-math.log(2) * delta_t / meia_vida)
        pesquisas_validas.append(p_dict)
        pesos.append(peso)

    if not pesquisas_validas or sum(pesos) <= 0:
        return estimar_m0(df_pesquisas, eleicao)

    pesos = np.array(pesos)
    res = {}
    for c in candidatos:
        vals = np.array([p[c] for p in pesquisas_validas])
        res[c] = float(np.sum(vals * pesos) / np.sum(pesos))

    return renormalizar_votos(res)


def calcular_house_effects_relativos(
    eleicoes_treino: list[int], k_shrinkage: float
) -> dict[tuple[str, str], float]:
    """
    Calcula o house effect RELATIVO de cada instituto por bloco politico
    nas eleicoes de treino, subtraindo o erro medio de todos os institutos naquele bloco.
    Aplica shrinkage dependente de n_j: beta = n_j / (n_j + k) * d_bar.
    """
    # Coleta desvios relativos por eleicao
    # d_{j, b, t} = e_{j, b, t} - e_bar_{b, t}
    desvios_por_inst_bloco: dict[tuple[str, str], list[float]] = {}
    presencas_inst: dict[str, set[int]] = {}

    for t in eleicoes_treino:
        df_p = obter_pesquisas_eleicao(t)
        res_tse = carregar_resultado_tse(t)
        candidatos = HISTORICO_CANDIDATOS[t]

        # Converte pesquisas e calcula erro por pesquisa e bloco
        # pesquisa -> {candidato: erro}
        erros_por_pesquisa = []
        for _, row in df_p.iterrows():
            inst = padronizar_nome_instituto(row["instituto"])
            presencas_inst.setdefault(inst, set()).add(t)
            p_val = converter_pesquisa_validos(row, candidatos)
            erros_cand = {c: p_val[c] - res_tse[c] for c in candidatos}
            erros_por_pesquisa.append((inst, erros_cand))

        # Erro medio por bloco em t de todos os institutos
        erros_bloco_todos: dict[str, list[float]] = {"pt": [], "adv": [], "demais": []}
        for _, e_cand in erros_por_pesquisa:
            for c, err in e_cand.items():
                b = identificar_bloco(t, c)
                erros_bloco_todos[b].append(err)

        e_bar_bloco_t = {b: float(np.mean(vals)) if vals else 0.0 for b, vals in erros_bloco_todos.items()}

        # Erro medio por instituto e bloco em t
        insts_na_eleicao = {inst for inst, _ in erros_por_pesquisa}
        for inst in insts_na_eleicao:
            erros_inst_b: dict[str, list[float]] = {"pt": [], "adv": [], "demais": []}
            for i_name, e_cand in erros_por_pesquisa:
                if i_name == inst:
                    for c, err in e_cand.items():
                        b = identificar_bloco(t, c)
                        erros_inst_b[b].append(err)

            for b in ["pt", "adv", "demais"]:
                if erros_inst_b[b]:
                    e_j_b_t = float(np.mean(erros_inst_b[b]))
                    d_j_b_t = e_j_b_t - e_bar_bloco_t[b]
                    desvios_por_inst_bloco.setdefault((inst, b), []).append(d_j_b_t)

    # Consolida medias historicas e aplica shrinkage n/(n+k)
    house_effects = {}
    for (inst, b), desvios in desvios_por_inst_bloco.items():
        n_j = len(presencas_inst.get(inst, set()))
        d_bar = float(np.mean(desvios))
        shrinkage = n_j / (n_j + k_shrinkage)
        house_effects[(inst, b)] = shrinkage * d_bar

    return house_effects


def estimar_m2(
    df_pesquisas: pd.DataFrame,
    eleicao: int,
    eleicoes_treino: list[int],
    meia_vida: float = 14.0,
    k_shrinkage: float = 3.0,
) -> dict[str, float]:
    """
    Modelo M2: M1 com correcao de House Effect Relativo por instituto x bloco com shrinkage.
    """
    candidatos = HISTORICO_CANDIDATOS[eleicao]
    vespera = VESPERAS[eleicao].date()

    if not eleicoes_treino:
        return estimar_m1(df_pesquisas, eleicao, meia_vida)

    house_effects = calcular_house_effects_relativos(eleicoes_treino, k_shrinkage)

    pesquisas_corrigidas = []
    pesos = []

    for _, row in df_pesquisas.iterrows():
        p_dict = converter_pesquisa_validos(row, candidatos)
        inst = padronizar_nome_instituto(row["instituto"])

        # Aplica correcao de house effect relativo
        corr_dict = {}
        for c in candidatos:
            b = identificar_bloco(eleicao, c)
            beta = house_effects.get((inst, b), 0.0)
            corr_dict[c] = max(0.0, p_dict[c] - beta)

        # Renormaliza para 100%
        p_norm = renormalizar_votos(corr_dict)

        dt_div = date.fromisoformat(row["data_divulgacao"])
        delta_t = max(0, (vespera - dt_div).days)
        amostra = row.get("amostra", 2000.0)
        if pd.isna(amostra) or amostra <= 0:
            amostra = 2000.0
        peso = math.sqrt(amostra) * math.exp(-math.log(2) * delta_t / meia_vida)

        pesquisas_corrigidas.append(p_norm)
        pesos.append(peso)

    if not pesquisas_corrigidas or sum(pesos) <= 0:
        return estimar_m1(df_pesquisas, eleicao, meia_vida)

    pesos = np.array(pesos)
    res = {}
    for c in candidatos:
        vals = np.array([p[c] for p in pesquisas_corrigidas])
        res[c] = float(np.sum(vals * pesos) / np.sum(pesos))

    return renormalizar_votos(res)


def estimar_m3(
    df_pesquisas: pd.DataFrame,
    eleicao: int,
    eleicoes_treino: list[int],
    meia_vida: float = 14.0,
    alpha: float = 1.0,
) -> dict[str, float]:
    """
    Modelo M3: Ridge Regression sobre projecao M1, incumbencia governista e ranking ordinal.
    """
    candidatos = HISTORICO_CANDIDATOS[eleicao]
    if not eleicoes_treino:
        return estimar_m1(df_pesquisas, eleicao, meia_vida)

    # 1. Monta matriz de treino
    X_train = []
    y_train = []

    for t in eleicoes_treino:
        df_t = obter_pesquisas_eleicao(t)
        m1_t = estimar_m1(df_t, t, meia_vida)
        res_tse_t = carregar_resultado_tse(t)
        cands_t = HISTORICO_CANDIDATOS[t]

        # Ranking ordinal baseado em M1 (1 para o primeiro colocado)
        sorted_cands = sorted(cands_t, key=lambda c: m1_t[c], reverse=True)
        ranking_map = {c: i + 1 for i, c in enumerate(sorted_cands)}

        for c in cands_t:
            x1 = m1_t[c]
            x2 = float(obter_incumbencia(t, c))
            x3 = float(ranking_map[c])
            y = res_tse_t[c]
            X_train.append([x1, x2, x3])
            y_train.append(y)

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    ridge = Ridge(alpha=alpha, fit_intercept=True)
    ridge.fit(X_train, y_train)

    # 2. Projeta no teste
    m1_test = estimar_m1(df_pesquisas, eleicao, meia_vida)
    sorted_test = sorted(candidatos, key=lambda c: m1_test[c], reverse=True)
    rank_test = {c: i + 1 for i, c in enumerate(sorted_test)}

    X_test = []
    for c in candidatos:
        x1 = m1_test[c]
        x2 = float(obter_incumbencia(eleicao, c))
        x3 = float(rank_test[c])
        X_test.append([x1, x2, x3])

    preds = ridge.predict(np.array(X_test))
    res = {c: max(0.0, float(p)) for c, p in zip(candidatos, preds)}
    return renormalizar_votos(res)


# --------------------------------------------------------------------------- #
# Ajustes Opcionais (Etapa 2)
# --------------------------------------------------------------------------- #


def aplicar_ajuste_vies_comum(
    base_preds: dict[str, float],
    eleicao: int,
    eleicoes_treino: list[int],
    k_mu: float = 1.0,
) -> dict[str, float]:
    """
    Ajuste 1: Correcao do vies comum da eleicao por bloco politico.
    """
    if not eleicoes_treino:
        return base_preds

    # Calcula vies comum medio por bloco nas eleicoes de treino
    erros_bloco: dict[str, list[float]] = {"pt": [], "adv": [], "demais": []}

    for t in eleicoes_treino:
        df_t = obter_pesquisas_eleicao(t)
        res_tse = carregar_resultado_tse(t)
        cands_t = HISTORICO_CANDIDATOS[t]

        for _, row in df_t.iterrows():
            p_val = converter_pesquisa_validos(row, cands_t)
            for c in cands_t:
                b = identificar_bloco(t, c)
                erros_bloco[b].append(p_val[c] - res_tse[c])

    n_eleic = len(eleicoes_treino)
    mu_hat = {}
    for b in ["pt", "adv", "demais"]:
        mu_bar = float(np.mean(erros_bloco[b])) if erros_bloco[b] else 0.0
        mu_hat[b] = (n_eleic / (n_eleic + k_mu)) * mu_bar

    adj_preds = {}
    for c, val in base_preds.items():
        b = identificar_bloco(eleicao, c)
        adj_preds[c] = max(0.0, val - mu_hat[b])

    return renormalizar_votos(adj_preds)


def aplicar_ajuste_voto_util(
    base_preds: dict[str, float],
    eleicao: int,
    eleicoes_treino: list[int],
    gamma: float = 0.5,
) -> dict[str, float]:
    """
    Ajuste 2: Transferencia de perda tardia dos 3o e 4o colocados para o Top-2.
    """
    if not eleicoes_treino or len(base_preds) < 4:
        return base_preds

    # Perda media historica de 3o e 4o colocados
    perdas = []
    for t in eleicoes_treino:
        df_t = obter_pesquisas_eleicao(t)
        m0_t = estimar_m0(df_t, t)
        res_tse = carregar_resultado_tse(t)
        cands_t = HISTORICO_CANDIDATOS[t]
        if len(cands_t) < 4:
            continue
        sorted_t = sorted(cands_t, key=lambda c: m0_t[c], reverse=True)
        c3, c4 = sorted_t[2], sorted_t[3]
        perda_t = max(0.0, (m0_t[c3] - res_tse[c3]) + (m0_t[c4] - res_tse[c4]))
        perdas.append(perda_t)

    delta_bar = float(np.mean(perdas)) if perdas else 0.0
    if delta_bar <= 0:
        return base_preds

    # Identifica ranking na base de teste
    sorted_preds = sorted(base_preds.keys(), key=lambda c: base_preds[c], reverse=True)
    c1, c2, c3, c4 = sorted_preds[0], sorted_preds[1], sorted_preds[2], sorted_preds[3]

    transf = gamma * delta_bar
    soma_34 = base_preds[c3] + base_preds[c4]
    soma_12 = base_preds[c1] + base_preds[c2]

    if soma_34 <= 0 or soma_12 <= 0:
        return base_preds

    adj = dict(base_preds)
    # Tira de 3 e 4
    t3 = transf * (base_preds[c3] / soma_34)
    t4 = transf * (base_preds[c4] / soma_34)
    adj[c3] = max(0.0, adj[c3] - t3)
    adj[c4] = max(0.0, adj[c4] - t4)

    # Transfere para 1 e 2
    adj[c1] += transf * (base_preds[c1] / soma_12)
    adj[c2] += transf * (base_preds[c2] / soma_12)

    return renormalizar_votos(adj)


def aplicar_ajuste_priors_nanicos(
    base_preds: dict[str, float],
    eleicao: int,
    w: float = 0.5,
) -> dict[str, float]:
    """
    Ajuste 3: Combinacao convexa de intencoes de candidatos nanicos com prior do TSE.
    """
    if eleicao != 2026:
        # Nas eleicoes historicas, as pesquisas nao divulgaram nanicos individualmente
        return base_preds

    priors = calcular_priors_nanicos_tse()
    adj = dict(base_preds)

    for c in priors:
        if c in adj:
            adj[c] = (1.0 - w) * adj[c] + w * priors[c]

    return renormalizar_votos(adj)


# --------------------------------------------------------------------------- #
# Funcoes de Metrica e Validacao
# --------------------------------------------------------------------------- #


def calcular_mae_eleicao(preds: dict[str, float], realizados: dict[str, float]) -> float:
    """Calcula o MAE entre previsao e realizado sobre TODOS os candidatos da eleicao."""
    cands = list(realizados.keys())
    if not cands:
        return 0.0
    return float(np.mean([abs(preds.get(c, 0.0) - realizados[c]) for c in cands]))


def calcular_diferenca_e_se(mae_A: list[float], mae_B: list[float]) -> tuple[float, float]:
    """
    Calcula a media das diferencas Delta = MAE_A - MAE_B e seu erro-padrao SE(Delta).
    """
    deltas = np.array(mae_A) - np.array(mae_B)
    delta_bar = float(np.mean(deltas))
    if len(deltas) <= 1:
        return delta_bar, 0.0
    s_delta = float(np.std(deltas, ddof=1))
    se_delta = s_delta / math.sqrt(len(deltas))
    return delta_bar, se_delta
