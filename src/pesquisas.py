"""
pesquisas.py
Padronizacao, filtragem e agregacao de pesquisas eleitorais.

Regra de agregacao entre institutos:
- NaN (candidato ausente na pesquisa) fica FORA da media
- 0 (candidato medido e obteve zero) ENTRA como 0
"""

from __future__ import annotations

import pandas as pd

from src.config import CANDIDATOS_2026, PROCESSED_DIR


def carregar_pesquisas_historicas(ano: int | None = None) -> pd.DataFrame:
    """
    Carrega o dataset compilado de pesquisas historicas (2006-2022).

    Parameters
    ----------
    ano : int, optional
        Se fornecido, filtra pesquisas daquela eleicao especifica.

    Returns
    -------
    pd.DataFrame
        DataFrame contendo as pesquisas historicas processadas.
    """
    path = PROCESSED_DIR / "pesquisas_historicas.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Arquivo {path} nao encontrado.")
    df = pd.read_parquet(path)
    if ano is not None:
        df = df[df["eleicao"] == ano].copy()
    return df


def agregar_institutos(
    df: pd.DataFrame,
    candidatos: list[str] | None = None,
    col_peso: str | None = None,
) -> dict[str, float]:
    """
    Agrega pesquisas de multiplos institutos calculando a media por candidato.

    Regra:
    - NaN => candidato ausente naquela pesquisa: excluido do denominador da media.
    - 0.0 => candidato medido e obteve zero: incluido no denominador da media.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de pesquisas com colunas por candidato (valores em %).
        Deve conter apenas as pesquisas a agregar (ja filtradas por data).
    candidatos : list[str], optional
        Lista de candidatos. Padrao: CANDIDATOS_2026.
    col_peso : str, optional
        Coluna de peso (ex. tamanho de amostra). Se None, peso igual.

    Returns
    -------
    dict[str, float]
        {candidato: media_ponderada_pct}. Candidatos onde TODAS as linhas
        sao NaN retornam NaN.

    Examples
    --------
    >>> import pandas as pd, numpy as np
    >>> df = pd.DataFrame({
    ...     "Lula": [48.0, 50.0, np.nan],
    ...     "Bolsonaro": [36.0, 38.0, 40.0],
    ... })
    >>> agregar_institutos(df, candidatos=["Lula", "Bolsonaro"])
    {'Lula': 49.0, 'Bolsonaro': 38.0}
    # Lula: media de [48, 50] (NaN excluido) = 49.0
    # Bolsonaro: media de [36, 38, 40] = 38.0
    """
    if candidatos is None:
        candidatos = CANDIDATOS_2026

    if df.empty:
        return {c: float("nan") for c in candidatos}

    pesos: pd.Series | None = None
    if col_peso and col_peso in df.columns:
        pesos = df[col_peso].fillna(0)

    resultado: dict[str, float] = {}
    for cand in candidatos:
        if cand not in df.columns:
            resultado[cand] = float("nan")
            continue

        serie = df[cand]
        mascara_valida = serie.notna()

        if not mascara_valida.any():
            resultado[cand] = float("nan")
            continue

        vals = serie[mascara_valida]

        if pesos is not None:
            w = pesos[mascara_valida]
            soma_w = w.sum()
            resultado[cand] = float((vals * w).sum() / soma_w) if soma_w > 0 else float(vals.mean())
        else:
            resultado[cand] = float(vals.mean())

    return resultado
