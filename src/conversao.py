"""
conversao.py
Converte pesquisas de intencao de voto (com brancos, nulos e indecisos)
para percentuais de votos validos, seguindo o criterio do TSE.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import CANDIDATOS_2026


def converter_para_votos_validos(
    linha: pd.Series | dict,
    candidatos: list[str] | None = None,
    col_brancos_nulos: str = "brancos_nulos",
    col_indecisos: str = "indecisos",
) -> dict[str, float]:
    """
    Converte uma linha de pesquisa para percentuais de votos validos.

    O metodo exclui brancos, nulos e indecisos e renormaliza
    proporcionalmente: identico ao criterio do TSE.

    Parameters
    ----------
    linha : pd.Series ou dict
        Linha da base de pesquisas com colunas por candidato.
    candidatos : list[str], optional
        Lista de candidatos a incluir. Padrao: CANDIDATOS_2026.
    col_brancos_nulos : str
        Nome da coluna com o percentual de brancos+nulos.
    col_indecisos : str
        Nome da coluna com o percentual de indecisos.

    Returns
    -------
    dict[str, float]
        Dicionario {candidato: pct_votos_validos}, com valores somando 100.0.

    Raises
    ------
    ValueError
        Se nenhum candidato tiver valor positivo apos exclusao.
    """
    if candidatos is None:
        candidatos = CANDIDATOS_2026

    linha = dict(linha)

    # Extrair intencoes brutas (tratando ausentes como 0)
    intencoes: dict[str, float] = {}
    for cand in candidatos:
        val = linha.get(cand, np.nan)
        intencoes[cand] = float(val) if pd.notna(val) else 0.0

    # Soma apenas das intencoes dos candidatos
    soma = sum(intencoes.values())
    if soma <= 0:
        raise ValueError(
            f"Soma das intencoes dos candidatos e zero ou negativa: {soma}"
        )

    # Renormaliza para 100% em votos validos
    validos = {cand: (v / soma) * 100.0 for cand, v in intencoes.items()}
    return validos


def converter_dataframe(
    df: pd.DataFrame,
    candidatos: list[str] | None = None,
    col_brancos_nulos: str = "brancos_nulos",
    col_indecisos: str = "indecisos",
    prefixo_saida: str = "vv_",
) -> pd.DataFrame:
    """
    Aplica a conversao para votos validos em todas as linhas de um DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de pesquisas com colunas por candidato.
    candidatos : list[str], optional
        Lista de candidatos. Padrao: CANDIDATOS_2026.
    col_brancos_nulos : str
        Coluna de brancos+nulos (ignorada na renormalizacao, usada como referencia).
    col_indecisos : str
        Coluna de indecisos (excluidos da renormalizacao).
    prefixo_saida : str
        Prefixo adicionado ao nome das colunas de saida.

    Returns
    -------
    pd.DataFrame
        DataFrame original com colunas extras {prefixo_saida}{candidato}.
    """
    if candidatos is None:
        candidatos = CANDIDATOS_2026

    df = df.copy()
    resultados = df.apply(
        lambda row: pd.Series(
            converter_para_votos_validos(
                row,
                candidatos=candidatos,
                col_brancos_nulos=col_brancos_nulos,
                col_indecisos=col_indecisos,
            )
        ),
        axis=1,
    )
    resultados.columns = [f"{prefixo_saida}{c}" for c in resultados.columns]
    return pd.concat([df, resultados], axis=1)
