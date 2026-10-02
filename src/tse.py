"""
tse.py
Processamento dos dados historicos do TSE.

Formato esperado de `detalhe_votacao_munzona`:
    sep=';', encoding='latin-1', colunas relevantes:
    NR_TURNO, CD_CARGO, QT_APTOS, QT_COMPARECIMENTO,
    QT_ABSTENCOES, QT_VOTOS_VALIDOS, QT_VOTOS_BRANCOS, QT_VOTOS_NULOS

Formato esperado de `votacao_candidato_munzona`:
    sep=';', encoding='latin-1', colunas relevantes:
    NR_TURNO, CD_CARGO, DS_CARGO, NM_URNA_CANDIDATO (ou NM_CANDIDATO),
    QT_VOTOS_NOMINAIS (ou QT_VOTOS)
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
          "abstencoes": int,
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
        "QT_VOTOS_BRANCOS",
        "QT_VOTOS_NULOS",
    }
    faltando = colunas_obrigatorias - set(df.columns)
    col_validos = "QT_TOTAL_VOTOS_VALIDOS" if "QT_TOTAL_VOTOS_VALIDOS" in df.columns else "QT_VOTOS_VALIDOS"
    if col_validos not in df.columns:
        faltando.add("QT_TOTAL_VOTOS_VALIDOS")
    if faltando:
        raise ValueError(f"Colunas obrigatorias ausentes: {faltando}")
    if df.empty:
        raise ValueError("DataFrame de detalhe_votacao esta vazio.")

    aptos = int(df["QT_APTOS"].sum())
    comparecimento = int(df["QT_COMPARECIMENTO"].sum())
    abstencoes = int(df["QT_ABSTENCOES"].sum())
    votos_validos = int(df[col_validos].sum())
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


def calcular_votos_validos_candidatos(df: pd.DataFrame) -> dict[str, float]:
    """
    Calcula percentual de votos validos por candidato a partir do arquivo
    votacao_candidato_munzona do TSE.

    Aplica filtros obrigatorios:
    - Cargo Presidente (DS_CARGO contendo 'PRESIDENTE' ou CD_CARGO == 1)
    - 1o turno (NR_TURNO == 1)

    Agrega em nivel nacional e normaliza sobre a soma dos votos dos candidatos
    (votos validos).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame no formato votacao_candidato_munzona do TSE.

    Returns
    -------
    dict[str, float]
        {nome_candidato: percentual_votos_validos}
        Ordenado decrescente por votacao.

    Raises
    ------
    ValueError
        Se o DataFrame estiver vazio ou faltar informacoes essenciais.
    """
    if df.empty:
        raise ValueError("DataFrame de votacao_candidato esta vazio.")

    df_filtrado = df.copy()

    # Filtro de turno
    if "NR_TURNO" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["NR_TURNO"].astype(int) == 1]
    elif "NUM_TURNO" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["NUM_TURNO"].astype(int) == 1]

    # Filtro de cargo Presidente
    if "CD_CARGO" in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado["CD_CARGO"].astype(int) == 1]
    elif "DS_CARGO" in df_filtrado.columns:
        df_filtrado = df_filtrado[
            df_filtrado["DS_CARGO"].astype(str).str.upper().str.contains("PRESIDENTE")
        ]

    if df_filtrado.empty:
        raise ValueError("Nenhum registro encontrado apos filtrar Presidente e 1o turno.")

    # Identificacao da coluna de nome
    col_nome = None
    for cand_col in ["NM_URNA_CANDIDATO", "NM_CANDIDATO", "NOME_URNA_CANDIDATO", "NOME_CANDIDATO"]:
        if cand_col in df_filtrado.columns:
            col_nome = cand_col
            break
    if col_nome is None:
        raise ValueError("Coluna de nome do candidato nao encontrada.")

    # Identificacao da coluna de votos
    col_votos = None
    for cand_voto in ["QT_VOTOS_NOMINAIS", "QT_VOTOS", "TOTAL_VOTOS"]:
        if cand_voto in df_filtrado.columns:
            col_votos = cand_voto
            break
    if col_votos is None:
        raise ValueError("Coluna de contagem de votos nao encontrada.")

    # Agregacao nacional
    votos_por_cand = (
        df_filtrado.groupby(col_nome)[col_votos]
        .sum()
        .astype(float)
    )

    total_validos = votos_por_cand.sum()
    if total_validos <= 0:
        raise ValueError("Total de votos validos apurados e zero ou negativo.")

    pct_por_cand = (votos_por_cand / total_validos * 100.0).sort_values(ascending=False)

    return pct_por_cand.to_dict()
