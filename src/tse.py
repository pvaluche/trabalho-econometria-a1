"""
tse.py
Processamento dos dados historicos do TSE.

Formato esperado de `detalhe_votacao_munzona`:
    sep=';', encoding='latin-1', colunas relevantes:
    NR_TURNO, CD_CARGO, QT_APTOS, QT_COMPARECIMENTO,
    QT_ABSTENCOES, QT_VOTOS_VALIDOS, QT_VOTOS_BRANCOS, QT_VOTOS_NULOS
"""

from __future__ import annotations

import pandas as pd


def calcular_denominadores(df: pd.DataFrame) -> dict[str, float]:
    """
    Calcula abstencao, brancos e nulos a partir de um DataFrame no formato
    do arquivo detalhe_votacao_munzona do TSE, ja filtrado para cargo
    Presidente (CD_CARGO == 1) e 1o turno (NR_TURNO == 1).

    Os denominadores seguem o criterio oficial do edital:
    - Abstencao  = QT_ABSTENCOES / QT_APTOS * 100
    - Brancos    = QT_VOTOS_BRANCOS / QT_COMPARECIMENTO * 100
    - Nulos      = QT_VOTOS_NULOS   / QT_COMPARECIMENTO * 100

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame com as colunas TSE padrao. Pode conter multiplas linhas
        (zonas/municipios) -- os totais sao calculados por soma.

    Returns
    -------
    dict[str, float]
        {
          "aptos": int,
          "comparecimento": int,
          "votos_validos": int,
          "votos_brancos": int,
          "votos_nulos": int,
          "abstencao_pct": float,   # sobre aptos
          "brancos_pct": float,     # sobre comparecimento
          "nulos_pct": float,       # sobre comparecimento
        }

    Raises
    ------
    ValueError
        Se o DataFrame estiver vazio ou faltar colunas obrigatorias.
    ZeroDivisionError
        Se QT_APTOS ou QT_COMPARECIMENTO totalizarem zero.
    """
    colunas_obrigatorias = {
        "QT_APTOS",
        "QT_COMPARECIMENTO",
        "QT_ABSTENCOES",
        "QT_VOTOS_VALIDOS",
        "QT_VOTOS_BRANCOS",
        "QT_VOTOS_NULOS",
    }
    faltando = colunas_obrigatorias - set(df.columns)
    if faltando:
        raise ValueError(f"Colunas obrigatorias ausentes: {faltando}")
    if df.empty:
        raise ValueError("DataFrame de detalhe_votacao esta vazio.")

    aptos = int(df["QT_APTOS"].sum())
    comparecimento = int(df["QT_COMPARECIMENTO"].sum())
    abstencoes = int(df["QT_ABSTENCOES"].sum())
    votos_validos = int(df["QT_VOTOS_VALIDOS"].sum())
    votos_brancos = int(df["QT_VOTOS_BRANCOS"].sum())
    votos_nulos = int(df["QT_VOTOS_NULOS"].sum())

    if aptos == 0:
        raise ZeroDivisionError("QT_APTOS totaliza zero -- dados invalidos.")
    if comparecimento == 0:
        raise ZeroDivisionError("QT_COMPARECIMENTO totaliza zero -- dados invalidos.")

    return {
        "aptos": aptos,
        "comparecimento": comparecimento,
        "abstencoes": abstencoes,
        "votos_validos": votos_validos,
        "votos_brancos": votos_brancos,
        "votos_nulos": votos_nulos,
        "abstencao_pct": abstencoes / aptos * 100.0,
        "brancos_pct": votos_brancos / comparecimento * 100.0,
        "nulos_pct": votos_nulos / comparecimento * 100.0,
    }
