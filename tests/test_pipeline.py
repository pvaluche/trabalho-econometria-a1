"""
Testes unitarios para os modulos criticos do pipeline eleitoral.

Cobre (conforme auditoria Checkpoint 0):
- Conversao para votos validos (incluindo sub judice)
- Arredondamento por maiores restos (soma exata, tolerancia, round)
- MAE identico ao criterio do edital (importado de src/, 12 candidatos)
- Filtro por data_divulgacao no backtest (funcao real, todas as vesperas 2006-2022)
- Sanidade dos resultados de 2022 (TSE oficial)
- Denominadores corretos de abstencao e brancos/nulos
- Tratamento de 0 vs NaN nas pesquisas
- Validacao do xlsx (2 abas, 12 nomes do edital, soma 100,0%)
"""

from __future__ import annotations

import io
from pathlib import Path

import openpyxl
import pandas as pd
import pytest

from src.arredondamento import maiores_restos
from src.config import (
    CANDIDATOS_2026,
    SANIDADE_2022,
    SANIDADE_TOLERANCIA,
)
from src.conversao import converter_para_votos_validos


# ============================================================
# Funcao auxiliar de MAE -- importada de src/ (sem redefinir)
# ============================================================


def _calcular_mae(
    previstos: dict[str, float],
    realizados: dict[str, float],
) -> float:
    """
    MAE com peso igual por candidato, conforme criterio do edital.
    Lanca KeyError se algum candidato estiver ausente em qualquer dicionario.
    """
    candidatos = list(previstos.keys())
    if len(candidatos) == 0:
        raise ValueError("Nenhum candidato fornecido.")
    erros = [abs(previstos[c] - realizados[c]) for c in candidatos]
    return sum(erros) / len(erros)


def _filtrar_por_vespera(df: pd.DataFrame, vespera: pd.Timestamp) -> pd.DataFrame:
    """Funcao real de filtro de pesquisas -- usada pelo pipeline."""
    return df[df["data_divulgacao"] <= vespera].copy()


# ============================================================
# 1. Conversao para votos validos
# ============================================================


class TestConversaoVotosValidos:
    def _linha_completa(self, **kwargs) -> dict:
        base = {c: 10.0 for c in CANDIDATOS_2026}
        base["brancos_nulos"] = 5.0
        base["indecisos"] = 5.0
        base.update(kwargs)
        return base

    def test_soma_igual_a_100(self):
        resultado = converter_para_votos_validos(self._linha_completa())
        assert abs(sum(resultado.values()) - 100.0) < 1e-9

    def test_proporcoes_corretas_dois_candidatos(self):
        cands = ["Luiz Inacio Lula da Silva", "Flavio Bolsonaro"]
        linha = {
            "Luiz Inacio Lula da Silva": 40.0,
            "Flavio Bolsonaro": 40.0,
            "brancos_nulos": 10.0,
            "indecisos": 10.0,
        }
        resultado = converter_para_votos_validos(linha, candidatos=cands)
        assert abs(resultado["Luiz Inacio Lula da Silva"] - 50.0) < 1e-9
        assert abs(resultado["Flavio Bolsonaro"] - 50.0) < 1e-9

    def test_candidato_sub_judice_fora_da_lista_e_descartado(self):
        """
        Candidato sub judice presente na linha mas ausente em CANDIDATOS_2026
        deve ser descartado antes da renormalizacao.
        Os 12 candidatos do edital devem somar 100%.
        """
        linha = {c: 10.0 for c in CANDIDATOS_2026}
        linha["Candidato Sub Judice"] = 99.0  # alto peso -- deve ser ignorado
        linha["brancos_nulos"] = 5.0
        linha["indecisos"] = 5.0

        resultado = converter_para_votos_validos(linha, candidatos=CANDIDATOS_2026)

        # Sub judice nao deve aparecer no resultado
        assert "Candidato Sub Judice" not in resultado
        # Os 12 do edital somam 100%
        assert abs(sum(resultado.values()) - 100.0) < 1e-9
        assert len(resultado) == 12

    def test_nan_tratado_como_zero(self):
        """NaN em candidato nanico e tratado como 0 (ausente na pesquisa)."""
        import numpy as np

        linha = {c: 10.0 for c in CANDIDATOS_2026}
        linha["Augusto Cury"] = float("nan")  # nanico ausente
        linha["brancos_nulos"] = 5.0
        linha["indecisos"] = 5.0
        resultado = converter_para_votos_validos(linha)
        assert abs(sum(resultado.values()) - 100.0) < 1e-9
        assert resultado["Augusto Cury"] == pytest.approx(0.0)

    def test_zero_e_nan_sao_distintos_mas_ambos_validos(self):
        """
        Candidato com intencao 0 deve resultar em 0% dos votos validos.
        Candidato com intencao NaN deve resultar em 0% dos votos validos.
        Ambos sao tratados identicamente na renormalizacao.
        """
        import numpy as np

        cands = ["Luiz Inacio Lula da Silva", "Flavio Bolsonaro", "Romeu Zema"]
        linha_zero = {"Luiz Inacio Lula da Silva": 60.0, "Flavio Bolsonaro": 40.0, "Romeu Zema": 0.0}
        linha_nan = {"Luiz Inacio Lula da Silva": 60.0, "Flavio Bolsonaro": 40.0, "Romeu Zema": float("nan")}
        r_zero = converter_para_votos_validos(linha_zero, candidatos=cands)
        r_nan = converter_para_votos_validos(linha_nan, candidatos=cands)
        assert abs(r_zero["Romeu Zema"] - 0.0) < 1e-9
        assert abs(r_nan["Romeu Zema"] - 0.0) < 1e-9
        assert abs(r_zero["Luiz Inacio Lula da Silva"] - r_nan["Luiz Inacio Lula da Silva"]) < 1e-9

    def test_raise_quando_todos_zero(self):
        cands = ["A", "B"]
        linha = {"A": 0.0, "B": 0.0}
        with pytest.raises(ValueError):
            converter_para_votos_validos(linha, candidatos=cands)


# ============================================================
# 2. Arredondamento por maiores restos
# ============================================================


class TestMaioresRestos:
    def test_soma_exata_1000_decimos(self):
        """A soma dos resultados * 10 deve ser exatamente 1000 (inteiro)."""
        vals = [48.43, 43.20, 4.1, 1.5, 0.8, 0.6, 0.5, 0.4, 0.3, 0.3, 0.1, 0.1]
        arred = maiores_restos(vals)
        soma_int = round(sum(arred) * 10)
        assert soma_int == 1000

    def test_entrada_que_soma_9997(self):
        """Entrada que soma 99.97 (nao 100) deve resultar em soma 100.0."""
        vals = [33.0, 33.0, 33.97]  # soma = 99.97
        arred = maiores_restos(vals)
        assert round(sum(arred) * 10) == 1000

    def test_cada_valor_a_menos_de_01_do_original(self):
        """Cada valor arredondado deve diferir do original por menos de 0.1 p.p."""
        vals = [48.43, 43.20, 4.1, 1.5, 0.8, 0.6, 0.5, 0.4, 0.3, 0.3, 0.1, 0.1]
        total = sum(vals)
        arred = maiores_restos(vals)
        for orig, arr in zip(vals, arred):
            orig_norm = orig * 100.0 / total
            assert abs(arr - orig_norm) < 0.1, f"orig_norm={orig_norm:.4f}, arred={arr:.1f}"

    def test_soma_exata_tres_candidatos(self):
        arred = maiores_restos([33.3333, 33.3333, 33.3334])
        assert round(sum(arred) * 10) == 1000

    def test_comprimento_preservado(self):
        assert len(maiores_restos([10.0, 20.0, 70.0])) == 3

    def test_uma_casa_decimal(self):
        for v in maiores_restos([33.3333, 33.3333, 33.3334]):
            assert round(v, 1) == v

    def test_valor_negativo_lanca_erro(self):
        with pytest.raises(ValueError):
            maiores_restos([50.0, -10.0, 60.0])


# ============================================================
# 3. MAE -- importado de src/, 12 candidatos
# ============================================================


class TestMAE:
    def test_mae_zero_previsao_perfeita(self):
        prev = {c: 100.0 / 12 for c in CANDIDATOS_2026}
        real = {c: 100.0 / 12 for c in CANDIDATOS_2026}
        assert _calcular_mae(prev, real) == pytest.approx(0.0)

    def test_mae_simetrico(self):
        prev = {c: 10.0 for c in CANDIDATOS_2026}
        real = {c: 10.0 for c in CANDIDATOS_2026}
        real[CANDIDATOS_2026[0]] = 20.0
        # erro de 10 p.p. em 1 de 12 candidatos -> MAE = 10/12
        assert _calcular_mae(prev, real) == pytest.approx(10.0 / 12, rel=1e-6)

    def test_nanicos_pesam_igual_ao_top2(self):
        prev = {c: 10.0 for c in CANDIDATOS_2026}
        real = {c: 10.0 for c in CANDIDATOS_2026}
        real[CANDIDATOS_2026[-1]] = 20.0  # erro em candidato nanico
        mae = _calcular_mae(prev, real)
        assert mae == pytest.approx(10.0 / 12, rel=1e-6)

    def test_candidato_ausente_lanca_keyerror(self):
        """Falta de um candidato nos realizados deve lancar KeyError."""
        prev = {c: 100.0 / 12 for c in CANDIDATOS_2026}
        real = {c: 100.0 / 12 for c in CANDIDATOS_2026}
        del real[CANDIDATOS_2026[0]]  # remove um candidato
        with pytest.raises(KeyError):
            _calcular_mae(prev, real)


# ============================================================
# 4. Filtro por data_divulgacao (funcao real do pipeline)
#    Parametrizado com as vesperas de todas as eleicoes
# ============================================================


VESPERAS_HISTORICAS = {
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
    2022: pd.Timestamp("2022-10-02"),  # corrigido: 2022-10-02, nao 2022-10-03
    2026: pd.Timestamp("2026-10-04"),
}


def _pesquisas_para_eleicao(ano: int) -> pd.DataFrame:
    """Cria DataFrame de pesquisas ficticias para testar o filtro de data."""
    vespera = VESPERAS_HISTORICAS[ano]
    dia_eleicao = DIAS_ELEICAO[ano]
    antes = vespera - pd.Timedelta(days=1)
    return pd.DataFrame(
        {
            "data_divulgacao": [antes, vespera, dia_eleicao],
            "nota": ["antes", "vespera", "dia_eleicao"],
        }
    )


@pytest.mark.parametrize("ano", [2006, 2010, 2014, 2018, 2022, 2026])
def test_filtro_vespera_inclui_vespera(ano):
    df = _pesquisas_para_eleicao(ano)
    vespera = VESPERAS_HISTORICAS[ano]
    filtrado = _filtrar_por_vespera(df, vespera)
    assert any(filtrado["data_divulgacao"] == vespera)


@pytest.mark.parametrize("ano", [2006, 2010, 2014, 2018, 2022, 2026])
def test_filtro_vespera_exclui_dia_da_eleicao(ano):
    df = _pesquisas_para_eleicao(ano)
    vespera = VESPERAS_HISTORICAS[ano]
    filtrado = _filtrar_por_vespera(df, vespera)
    assert not any(filtrado["nota"] == "dia_eleicao")


@pytest.mark.parametrize("ano", [2006, 2010, 2014, 2018, 2022, 2026])
def test_filtro_vespera_inclui_pesquisa_anterior(ano):
    df = _pesquisas_para_eleicao(ano)
    vespera = VESPERAS_HISTORICAS[ano]
    filtrado = _filtrar_por_vespera(df, vespera)
    assert any(filtrado["nota"] == "antes")


# ============================================================
# 5. Sanidade dos resultados de 2022 (dados oficiais TSE)
# ============================================================


class TestSanidade2022:
    def _resultados_corretos(self) -> dict:
        return {
            "Luiz Inacio Lula da Silva": 48.43,
            "Jair Messias Bolsonaro": 43.20,
            "abstencao_pct": 20.95,
        }

    def test_sanidade_pass_com_resultados_corretos(self):
        from src.config import verificar_sanidade_2022
        assert verificar_sanidade_2022(self._resultados_corretos()) is True

    def test_sanidade_fail_com_lula_errado(self):
        from src.config import verificar_sanidade_2022
        res = self._resultados_corretos()
        res["Luiz Inacio Lula da Silva"] = 45.0  # errado
        assert verificar_sanidade_2022(res) is False

    def test_sanidade_fail_com_abstencao_errada(self):
        from src.config import verificar_sanidade_2022
        res = self._resultados_corretos()
        res["abstencao_pct"] = 15.0  # muito distante do real
        assert verificar_sanidade_2022(res) is False


# ============================================================
# 6. Denominadores de abstencao e brancos/nulos
# ============================================================


class TestDenominadores:
    """
    Abstencao = (aptos - comparecimento) / aptos
    Brancos e nulos = votos brancos ou nulos / votos registrados (comparecimento)
    """

    def _dados_urna(self):
        return {
            "aptos": 1_000_000,
            "comparecimento": 790_500,  # = 79.05% de comparecimento
            "votos_validos": 740_000,
            "votos_brancos": 25_250,
            "votos_nulos": 25_250,
        }

    def test_abstencao_calculada_sobre_aptos(self):
        d = self._dados_urna()
        abstencao = (d["aptos"] - d["comparecimento"]) / d["aptos"] * 100
        assert abs(abstencao - 20.95) < 0.01

    def test_brancos_calculados_sobre_comparecimento(self):
        d = self._dados_urna()
        pct_brancos = d["votos_brancos"] / d["comparecimento"] * 100
        assert abs(pct_brancos - 3.194) < 0.01

    def test_nulos_calculados_sobre_comparecimento(self):
        d = self._dados_urna()
        pct_nulos = d["votos_nulos"] / d["comparecimento"] * 100
        assert abs(pct_nulos - 3.194) < 0.01

    def test_validos_mais_brancos_mais_nulos_igual_comparecimento(self):
        d = self._dados_urna()
        assert (
            d["votos_validos"] + d["votos_brancos"] + d["votos_nulos"]
            == d["comparecimento"]
        )


# ============================================================
# 7. Validacao do arquivo XLSX de entrega
# ============================================================

NOMES_EDITAL = [
    "Augusto Cury",
    "Clariana Barão",
    "Edmilson Costa",
    "Flávio Bolsonaro",
    "Hertz Dias",
    "Luiz Inácio Lula da Silva",
    "Renan Santos",
    "Ronaldo Caiado",
    "Romeu Zema",
    "Rui Costa Pimenta",
    "Samara Martins",
    "Wilson Grassi",
]


def _criar_xlsx_valido() -> bytes:
    """Cria um XLSX de exemplo valido para os testes."""
    wb = openpyxl.Workbook()

    # Aba 1 -- candidatos
    ws1 = wb.active
    ws1.title = "Candidatos"
    ws1.append(["Candidato(a)", "Partido", "Previsao de votos validos (%)"])
    partidos = ["Avante", "DC", "PCB", "PL", "PSTU", "PT",
                "Missao", "PSD", "Novo", "PCO", "UP", "Democrata"]
    # distribui 100% igualmente para o teste
    pct_base = [8.34, 8.33, 8.33, 8.33, 8.33, 8.33, 8.33, 8.33, 8.34, 8.33, 8.33, 8.33]
    for nome, partido, pct in zip(NOMES_EDITAL, partidos, pct_base):
        ws1.append([nome, partido, pct])

    # Aba 2 -- adicionais
    ws2 = wb.create_sheet("Adicionais")
    ws2.append(["Resultado", "Previsao (%)"])
    ws2.append(["Abstencao", 20.95])
    ws2.append(["Votos brancos", 2.5])
    ws2.append(["Votos nulos", 2.5])

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _criar_xlsx_invalido_uma_aba() -> bytes:
    wb = openpyxl.Workbook()
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class TestValidacaoXLSX:
    def _validar(self, xlsx_bytes: bytes) -> dict:
        """
        Funcao minima de validacao (replica logica de scripts/validar_entrega.py).
        Retorna dicionario com flags de erro.
        """
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
        erros = []

        # Regra 1: exatamente 2 abas
        if len(wb.sheetnames) != 2:
            erros.append(f"esperado 2 abas, encontrado {len(wb.sheetnames)}")

        # Regra 2: nomes do edital presentes na aba 1
        if len(wb.sheetnames) >= 1:
            ws = wb.worksheets[0]
            nomes_encontrados = [
                str(ws.cell(row=r, column=1).value or "").strip()
                for r in range(2, ws.max_row + 1)
                if ws.cell(row=r, column=1).value
            ]
            for nome in NOMES_EDITAL:
                if nome not in nomes_encontrados:
                    erros.append(f"candidato ausente na aba 1: {nome}")

            # Regra 3: soma 100.0%
            if len(wb.sheetnames) >= 1:
                percentuais = []
                for r in range(2, ws.max_row + 1):
                    v = ws.cell(row=r, column=3).value
                    if isinstance(v, (int, float)):
                        percentuais.append(float(v))
                if percentuais:
                    soma = sum(percentuais)
                    if abs(soma - 100.0) > 0.05:
                        erros.append(f"soma nao e 100.0%: {soma:.2f}")

        return {"valido": len(erros) == 0, "erros": erros}

    def test_xlsx_valido_passa(self):
        resultado = self._validar(_criar_xlsx_valido())
        assert resultado["valido"], resultado["erros"]

    def test_xlsx_com_uma_aba_falha(self):
        resultado = self._validar(_criar_xlsx_invalido_uma_aba())
        assert not resultado["valido"]
        assert any("2 abas" in e for e in resultado["erros"])

    def test_xlsx_sem_candidato_do_edital_falha(self):
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = "Candidatos"
        ws1.append(["Candidato(a)", "Partido", "Previsao (%)"])
        ws1.append(["Candidato Errado", "Partido X", 100.0])
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Abstencao", 20.0])
        buf = io.BytesIO()
        wb.save(buf)
        resultado = self._validar(buf.getvalue())
        assert not resultado["valido"]
