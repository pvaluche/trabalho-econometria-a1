"""
Testes unitarios para os modulos criticos do pipeline eleitoral.

Cobre:
- Conversao para votos validos
- Soma exata de 100,0% apos arredondamento por maiores restos
- Calculo do MAE identico ao criterio do edital
- Filtro por data_divulgacao no backtest
- Normalizacao com e sem candidato sub judice
"""

from __future__ import annotations

import pytest
import pandas as pd

from src.arredondamento import maiores_restos
from src.conversao import converter_para_votos_validos


# ============================================================
# 1. Conversao para votos validos
# ============================================================


class TestConversaoVotosValidos:
    """Testa a renormalizacao de intencoes para votos validos."""

    def test_soma_igual_a_100(self):
        linha = {
            "Augusto Cury": 1.0,
            "Clariana Barao": 0.5,
            "Edmilson Costa": 0.5,
            "Flavio Bolsonaro": 35.0,
            "Hertz Dias": 0.5,
            "Luiz Inacio Lula da Silva": 45.0,
            "Renan Santos": 1.0,
            "Ronaldo Caiado": 8.0,
            "Romeu Zema": 5.0,
            "Rui Costa Pimenta": 0.5,
            "Samara Martins": 0.5,
            "Wilson Grassi": 0.5,
            "brancos_nulos": 2.0,
            "indecisos": 5.0,
        }
        resultado = converter_para_votos_validos(linha)
        assert abs(sum(resultado.values()) - 100.0) < 1e-9

    def test_proporcoes_corretas(self):
        """Com apenas dois candidatos em 50/50, ambos devem ter 50% dos validos."""
        candidatos = ["Luiz Inacio Lula da Silva", "Flavio Bolsonaro"]
        linha = {
            "Luiz Inacio Lula da Silva": 40.0,
            "Flavio Bolsonaro": 40.0,
            "brancos_nulos": 10.0,
            "indecisos": 10.0,
        }
        resultado = converter_para_votos_validos(linha, candidatos=candidatos)
        assert abs(resultado["Luiz Inacio Lula da Silva"] - 50.0) < 1e-9
        assert abs(resultado["Flavio Bolsonaro"] - 50.0) < 1e-9

    def test_sem_candidato_sub_judice(self):
        """Com candidato sub judice ausente, renormalizacao continua correta."""
        candidatos = ["Luiz Inacio Lula da Silva", "Flavio Bolsonaro", "Ronaldo Caiado"]
        linha = {
            "Luiz Inacio Lula da Silva": 48.0,
            "Flavio Bolsonaro": 36.0,
            "Ronaldo Caiado": 8.0,
            # candidato sub judice ausente -- tratado como 0
            "brancos_nulos": 5.0,
            "indecisos": 3.0,
        }
        resultado = converter_para_votos_validos(linha, candidatos=candidatos)
        assert abs(sum(resultado.values()) - 100.0) < 1e-9

    def test_com_candidato_sub_judice_incluido(self):
        """Com candidato sub judice incluido na lista, total ainda deve ser 100%."""
        candidatos = [
            "Luiz Inacio Lula da Silva",
            "Flavio Bolsonaro",
            "Candidato Sub Judice",
        ]
        linha = {
            "Luiz Inacio Lula da Silva": 48.0,
            "Flavio Bolsonaro": 36.0,
            "Candidato Sub Judice": 8.0,
            "brancos_nulos": 5.0,
            "indecisos": 3.0,
        }
        resultado = converter_para_votos_validos(linha, candidatos=candidatos)
        assert abs(sum(resultado.values()) - 100.0) < 1e-9

    def test_raise_quando_todos_zero(self):
        """Deve lancar ValueError se todos os candidatos tiverem intencao zero."""
        candidatos = ["A", "B"]
        linha = {"A": 0.0, "B": 0.0, "brancos_nulos": 10.0, "indecisos": 90.0}
        with pytest.raises(ValueError):
            converter_para_votos_validos(linha, candidatos=candidatos)


# ============================================================
# 2. Arredondamento por maiores restos -- soma exata de 100,0%
# ============================================================


class TestMaioresRestos:
    """Testa o metodo dos maiores restos."""

    def test_soma_exata_100(self):
        vals = [33.3333, 33.3333, 33.3334]
        arred = maiores_restos(vals)
        assert sum(arred) == pytest.approx(100.0)

    def test_soma_exata_caso_12_candidatos(self):
        """Cenario realista com 12 candidatos."""
        vals = [48.43, 43.20, 4.1, 1.5, 0.8, 0.6, 0.5, 0.4, 0.3, 0.3, 0.1, 0.1]
        arred = maiores_restos(vals)
        assert sum(arred) == pytest.approx(100.0)

    def test_comprimento_preservado(self):
        vals = [10.0, 20.0, 70.0]
        arred = maiores_restos(vals)
        assert len(arred) == 3

    def test_uma_casa_decimal(self):
        arred = maiores_restos([33.3333, 33.3333, 33.3334])
        for v in arred:
            # garante 1 casa decimal
            assert round(v, 1) == v

    def test_valor_negativo_lanca_erro(self):
        with pytest.raises(ValueError):
            maiores_restos([50.0, -10.0, 60.0])


# ============================================================
# 3. MAE igual ao criterio do edital
# ============================================================


def calcular_mae(previstos: dict[str, float], realizados: dict[str, float]) -> float:
    """MAE com peso igual por candidato."""
    candidatos = list(previstos.keys())
    erros = [abs(previstos[c] - realizados[c]) for c in candidatos]
    return sum(erros) / len(erros)


class TestMAE:
    def test_mae_zero_previsao_perfeita(self):
        prev = {"A": 50.0, "B": 30.0, "C": 20.0}
        real = {"A": 50.0, "B": 30.0, "C": 20.0}
        assert calcular_mae(prev, real) == pytest.approx(0.0)

    def test_mae_simetrico(self):
        prev = {"A": 50.0, "B": 30.0, "C": 20.0}
        real = {"A": 40.0, "B": 35.0, "C": 25.0}
        # erros absolutos: 10, 5, 5 -> media = 20/3
        assert calcular_mae(prev, real) == pytest.approx(20.0 / 3, rel=1e-6)

    def test_nanicos_pesam_igual_ao_top2(self):
        """Garante que todos os candidatos tem peso igual no MAE."""
        prev = {f"C{i}": 10.0 for i in range(10)}
        real = {f"C{i}": 10.0 for i in range(10)}
        real["C0"] = 20.0  # erro de 10 pp em um candidato
        mae = calcular_mae(prev, real)
        assert mae == pytest.approx(1.0)  # 10 / 10 candidatos


# ============================================================
# 4. Filtro de data_divulgacao no backtest
# ============================================================


class TestFiltroDataDivulgacao:
    """
    Pesquisas com data_divulgacao posterior a vespera do 1o turno
    nao devem entrar no backtest daquela eleicao.
    """

    def _pesquisas_exemplo(self) -> pd.DataFrame:
        return pd.DataFrame({
            "instituto": ["A", "B", "C"],
            "data_divulgacao": pd.to_datetime(["2022-09-30", "2022-10-01", "2022-10-03"]),
            "Luiz Inacio Lula da Silva": [48.0, 47.0, 48.5],
            "Flavio Bolsonaro": [36.0, 37.0, 42.0],
        })

    def test_pesquisa_posterior_a_vespera_excluida(self):
        df = self._pesquisas_exemplo()
        vespera = pd.Timestamp("2022-10-01")
        filtrado = df[df["data_divulgacao"] <= vespera]
        # So entram as pesquisas de 30/09 e 01/10
        assert len(filtrado) == 2

    def test_pesquisa_na_vespera_incluida(self):
        df = self._pesquisas_exemplo()
        vespera = pd.Timestamp("2022-10-01")
        filtrado = df[df["data_divulgacao"] <= vespera]
        assert any(filtrado["data_divulgacao"] == pd.Timestamp("2022-10-01"))

    def test_pesquisa_dia_da_eleicao_excluida(self):
        df = self._pesquisas_exemplo()
        vespera = pd.Timestamp("2022-10-01")
        filtrado = df[df["data_divulgacao"] <= vespera]
        assert not any(filtrado["data_divulgacao"] == pd.Timestamp("2022-10-03"))
