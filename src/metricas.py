"""
metricas.py
Funcoes de avaliacao do modelo eleitoral.
Importar daqui em testes e no pipeline -- nunca redefinir nos testes.
"""

from __future__ import annotations


def calcular_mae(
    previstos: dict[str, float],
    realizados: dict[str, float],
) -> float:
    """
    Calcula o MAE com peso igual por candidato, conforme criterio do edital
    FGV EPGE (Desafio de Estatistica e Econometria 2026).

    Parameters
    ----------
    previstos : dict[str, float]
        Percentuais de votos validos previstos, por nome de candidato.
    realizados : dict[str, float]
        Percentuais de votos validos realizados (TSE), por nome de candidato.

    Returns
    -------
    float
        MAE medio entre todos os candidatos do dicionario `previstos`.

    Raises
    ------
    KeyError
        Se algum candidato de `previstos` nao estiver em `realizados`.
    ValueError
        Se `previstos` estiver vazio.

    Examples
    --------
    >>> calcular_mae({"A": 50.0, "B": 50.0}, {"A": 50.0, "B": 50.0})
    0.0
    >>> calcular_mae({"A": 40.0, "B": 60.0}, {"A": 50.0, "B": 50.0})
    10.0
    """
    candidatos = list(previstos.keys())
    if not candidatos:
        raise ValueError("Dicionario de previstos esta vazio.")

    # Lanca KeyError se candidato ausente em realizados
    erros = [abs(previstos[c] - realizados[c]) for c in candidatos]
    return sum(erros) / len(erros)


def calcular_mae_por_candidato(
    previstos: dict[str, float],
    realizados: dict[str, float],
) -> dict[str, float]:
    """
    Retorna o erro absoluto por candidato (util para ablation e interface).

    Parameters
    ----------
    previstos : dict[str, float]
        Percentuais previstos.
    realizados : dict[str, float]
        Percentuais realizados.

    Returns
    -------
    dict[str, float]
        {candidato: erro_absoluto_em_pp}
    """
    candidatos = list(previstos.keys())
    if not candidatos:
        raise ValueError("Dicionario de previstos esta vazio.")
    return {c: abs(previstos[c] - realizados[c]) for c in candidatos}
