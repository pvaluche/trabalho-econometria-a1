"""
filtros.py
Funcoes de filtragem de pesquisas eleitorais por data de divulgacao.
Importar daqui em testes e no pipeline -- nunca redefinir nos testes.
"""

from __future__ import annotations

import pandas as pd


def filtrar_por_vespera(
    df: pd.DataFrame,
    vespera: pd.Timestamp | str,
    col_data: str = "data_divulgacao",
) -> pd.DataFrame:
    """
    Filtra pesquisas com data de divulgacao ate (inclusive) a vespera
    do 1o turno.

    Regra: so entra no backtest de uma eleicao o que estava publicamente
    disponivel ate a vespera (data_divulgacao <= vespera).
    Pesquisas divulgadas no dia da eleicao ou depois ficam de fora.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de pesquisas com coluna de data de divulgacao.
    vespera : pd.Timestamp ou str
        Data maxima de divulgacao permitida (inclusiva).
    col_data : str
        Nome da coluna de data. Padrao: "data_divulgacao".

    Returns
    -------
    pd.DataFrame
        Subconjunto das pesquisas com data <= vespera.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"data_divulgacao": pd.to_datetime(
    ...     ["2022-09-30", "2022-10-01", "2022-10-02"])})
    >>> filtrar_por_vespera(df, "2022-10-01")
    # Retorna apenas as linhas de 30/09 e 01/10
    """
    vespera = pd.Timestamp(vespera)
    return df[df[col_data] <= vespera].copy()


# Datas de referencia por eleicao (exportadas para uso nos testes e no pipeline)
VESPERAS = {
    2006: pd.Timestamp("2006-09-30"),
    2010: pd.Timestamp("2010-10-02"),
    2014: pd.Timestamp("2014-10-04"),
    2018: pd.Timestamp("2018-10-06"),
    2022: pd.Timestamp("2022-10-01"),
    2026: pd.Timestamp("2026-10-03"),
}

DIAS_ELEICAO = {
    2006: pd.Timestamp("2006-10-01"),
    2010: pd.Timestamp("2010-10-03"),
    2014: pd.Timestamp("2014-10-05"),
    2018: pd.Timestamp("2018-10-07"),
    2022: pd.Timestamp("2022-10-02"),
    2026: pd.Timestamp("2026-10-04"),
}
