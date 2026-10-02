"""
arredondamento.py
Implementa o metodo dos maiores restos para arredondar porcentagens para
1 casa decimal de forma que a soma seja exatamente 100,0%.
"""

from __future__ import annotations

import math
from typing import Sequence


def maiores_restos(
    valores: Sequence[float],
    total: float = 100.0,
    casas: int = 1,
) -> list[float]:
    """
    Arredonda uma sequencia de valores nao-negativos para `casas` decimais
    de forma que a soma seja exatamente `total`, usando o metodo dos maiores
    restos (Hamilton/Hare method).

    Parameters
    ----------
    valores : Sequence[float]
        Valores a arredondar. Devem somar aproximadamente `total`.
    total : float
        Soma alvo apos arredondamento (padrao: 100.0).
    casas : int
        Numero de casas decimais do resultado (padrao: 1).

    Returns
    -------
    list[float]
        Lista de valores arredondados com a mesma ordem dos originais,
        somando exatamente `total`.

    Raises
    ------
    ValueError
        Se algum valor for negativo.

    Examples
    --------
    >>> maiores_restos([33.3333, 33.3333, 33.3334])
    [33.3, 33.3, 33.4]

    >>> sum(maiores_restos([48.426, 43.201, 4.102, 1.150, 0.821, 0.601, 0.499,
    ...                     0.400, 0.300, 0.300, 0.100, 0.100]))
    100.0
    """
    if any(v < 0 for v in valores):
        raise ValueError("Todos os valores devem ser nao-negativos.")

    soma_original = sum(valores)
    if soma_original <= 0:
        raise ValueError("A soma dos valores deve ser positiva.")

    # Normaliza para somar exatamente `total`, eliminando imprecisao acumulada
    valores_norm = [v * total / soma_original for v in valores]

    fator = 10**casas
    total_int = round(total * fator)

    # Escala para inteiros -- round(x, 10) remove ruido de ponto flutuante
    # (ex: 0.3 * 10 = 2.9999... -> round para 10 casas -> 3.0)
    escalados = [round(v * fator, 10) for v in valores_norm]
    partes_inteiras = [math.floor(s) for s in escalados]
    restos = [(escalados[i] - partes_inteiras[i], i) for i in range(len(valores))]

    soma_inteiras = sum(partes_inteiras)
    restante = total_int - soma_inteiras

    # Ordena por resto decrescente (desempate por indice crescente, para determinismo)
    restos_ordenados = sorted(restos, key=lambda x: (-x[0], x[1]))

    # Distribui as unidades restantes para os maiores restos
    resultado = list(partes_inteiras)
    for k in range(restante):
        idx = restos_ordenados[k][1]
        resultado[idx] += 1

    return [r / fator for r in resultado]


def formatar_tabela(
    candidatos: list[str],
    percentuais: list[float],
    casas: int = 1,
) -> str:
    """
    Retorna uma tabela markdown com candidatos e percentuais arredondados.

    Parameters
    ----------
    candidatos : list[str]
        Nomes dos candidatos.
    percentuais : list[float]
        Percentuais de votos validos (antes do arredondamento).
    casas : int
        Casas decimais.

    Returns
    -------
    str
        Tabela formatada em markdown.
    """
    arredondados = maiores_restos(percentuais, total=100.0, casas=casas)
    fmt = f".{casas}f"
    linhas = ["| Candidato | Votos Validos (%) |", "|---|---|"]
    for cand, pct in zip(candidatos, arredondados):
        linhas.append(f"| {cand} | {pct:{fmt}} |")
    linhas.append(f"| **Total** | **{sum(arredondados):{fmt}}** |")
    return "\n".join(linhas)
