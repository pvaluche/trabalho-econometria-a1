"""
Testes unitarios e de integracao para os modulos criticos do pipeline eleitoral.
FGV EPGE -- Desafio de Estatistica e Econometria 2026.

Todas as funcoes de negocio sao IMPORTADAS de src/ ou scripts/.
Nenhuma logica de negocio e definida neste arquivo.
"""

from __future__ import annotations

import io
from pathlib import Path
import re

import numpy as np
import openpyxl
import pandas as pd
import pytest

from scripts.validar_entrega import validar_xlsx
from src.arredondamento import maiores_restos
from src.backtest import (
    calcular_diferenca_e_se,
    calcular_house_effects_relativos,
    estimar_m0,
    estimar_m1,
    renormalizar_votos,
)
from src.entrega import gerar_planilha_entrega
from src.config import (
    CANDIDATOS_EDITAL,
    DOCS_DIR,
    MANIFEST_PATH,
    OUTPUTS_DIR,
    PARTIDOS_EDITAL,
    PESQUISAS_2026_PATH,
    PESQUISAS_2026_SCHEMA,
    PROCESSED_DIR,
    RAW_DIR,
    verificar_sanidade_2022,
)
from src.conversao import converter_para_votos_validos
from src.filtros import DIAS_ELEICAO, VESPERAS, filtrar_por_vespera
from src.metricas import calcular_mae
from src.pesquisas import agregar_institutos, carregar_pesquisas_historicas
from src.tse import calcular_denominadores, calcular_votos_validos_candidatos


# ============================================================
# 1. Conversao para votos validos
# ============================================================


class TestConversaoVotosValidos:
    def _linha_completa(self, **kwargs) -> dict:
        base = {c: 10.0 for c in CANDIDATOS_EDITAL}
        base["brancos_nulos"] = 5.0
        base["indecisos"] = 5.0
        base.update(kwargs)
        return base

    def test_soma_igual_a_100(self):
        resultado = converter_para_votos_validos(self._linha_completa())
        assert abs(sum(resultado.values()) - 100.0) < 1e-9

    def test_proporcoes_corretas_dois_candidatos(self):
        cands = ["Luiz Inácio Lula da Silva", "Flávio Bolsonaro"]
        linha = {
            "Luiz Inácio Lula da Silva": 40.0,
            "Flávio Bolsonaro": 40.0,
            "brancos_nulos": 10.0,
            "indecisos": 10.0,
        }
        resultado = converter_para_votos_validos(linha, candidatos=cands)
        assert abs(resultado["Luiz Inácio Lula da Silva"] - 50.0) < 1e-9
        assert abs(resultado["Flávio Bolsonaro"] - 50.0) < 1e-9

    def test_candidato_sub_judice_fora_de_candidatos_edital_descartado(self):
        """
        Candidato sub judice presente na linha mas ausente em CANDIDATOS_EDITAL
        deve ser ignorado antes da renormalizacao; os 12 do edital somam 100%.
        """
        linha = {c: 10.0 for c in CANDIDATOS_EDITAL}
        linha["Candidato Sub Judice"] = 99.0
        linha["brancos_nulos"] = 5.0
        linha["indecisos"] = 5.0
        resultado = converter_para_votos_validos(linha, candidatos=CANDIDATOS_EDITAL)
        assert "Candidato Sub Judice" not in resultado
        assert abs(sum(resultado.values()) - 100.0) < 1e-9
        assert len(resultado) == 12

    def test_nan_tratado_como_zero(self):
        linha = {c: 10.0 for c in CANDIDATOS_EDITAL}
        linha["Augusto Cury"] = float("nan")
        linha["brancos_nulos"] = 5.0
        linha["indecisos"] = 5.0
        resultado = converter_para_votos_validos(linha)
        assert abs(sum(resultado.values()) - 100.0) < 1e-9
        assert resultado["Augusto Cury"] == pytest.approx(0.0)

    def test_zero_e_nan_resultam_em_zero_pct(self):
        cands = ["Luiz Inácio Lula da Silva", "Flávio Bolsonaro", "Romeu Zema"]
        l_zero = {"Luiz Inácio Lula da Silva": 60.0, "Flávio Bolsonaro": 40.0, "Romeu Zema": 0.0}
        l_nan = {"Luiz Inácio Lula da Silva": 60.0, "Flávio Bolsonaro": 40.0, "Romeu Zema": float("nan")}
        r_zero = converter_para_votos_validos(l_zero, candidatos=cands)
        r_nan = converter_para_votos_validos(l_nan, candidatos=cands)
        assert abs(r_zero["Romeu Zema"] - 0.0) < 1e-9
        assert abs(r_nan["Romeu Zema"] - 0.0) < 1e-9
        assert abs(r_zero["Luiz Inácio Lula da Silva"] - r_nan["Luiz Inácio Lula da Silva"]) < 1e-9

    def test_raise_quando_todos_zero(self):
        cands = ["A", "B"]
        with pytest.raises(ValueError):
            converter_para_votos_validos({"A": 0.0, "B": 0.0}, candidatos=cands)


# ============================================================
# 2. Arredondamento por maiores restos
# ============================================================


class TestMaioresRestos:
    def test_soma_exata_1000_decimos(self):
        vals = [48.43, 43.20, 4.1, 1.5, 0.8, 0.6, 0.5, 0.4, 0.3, 0.3, 0.1, 0.1]
        assert round(sum(maiores_restos(vals)) * 10) == 1000

    def test_entrada_que_soma_9997(self):
        assert round(sum(maiores_restos([33.0, 33.0, 33.97])) * 10) == 1000

    def test_cada_valor_a_menos_de_01_do_original(self):
        vals = [48.43, 43.20, 4.1, 1.5, 0.8, 0.6, 0.5, 0.4, 0.3, 0.3, 0.1, 0.1]
        total = sum(vals)
        for orig, arr in zip(vals, maiores_restos(vals)):
            assert abs(arr - orig * 100.0 / total) < 0.1

    def test_soma_exata_tres_candidatos(self):
        assert round(sum(maiores_restos([33.3333, 33.3333, 33.3334])) * 10) == 1000

    def test_comprimento_preservado(self):
        assert len(maiores_restos([10.0, 20.0, 70.0])) == 3

    def test_uma_casa_decimal(self):
        for v in maiores_restos([33.3333, 33.3333, 33.3334]):
            assert round(v, 1) == v

    def test_valor_negativo_lanca_erro(self):
        with pytest.raises(ValueError):
            maiores_restos([50.0, -10.0, 60.0])


# ============================================================
# 3. MAE -- importado de src/metricas.py
# ============================================================


class TestMAE:
    def test_mae_zero_previsao_perfeita(self):
        prev = {c: 100.0 / 12 for c in CANDIDATOS_EDITAL}
        real = {c: 100.0 / 12 for c in CANDIDATOS_EDITAL}
        assert calcular_mae(prev, real) == pytest.approx(0.0)

    def test_mae_simetrico(self):
        prev = {c: 10.0 for c in CANDIDATOS_EDITAL}
        real = {c: 10.0 for c in CANDIDATOS_EDITAL}
        real[CANDIDATOS_EDITAL[0]] = 20.0
        assert calcular_mae(prev, real) == pytest.approx(10.0 / 12, rel=1e-6)

    def test_nanicos_pesam_igual_ao_top2(self):
        prev = {c: 10.0 for c in CANDIDATOS_EDITAL}
        real = {c: 10.0 for c in CANDIDATOS_EDITAL}
        real[CANDIDATOS_EDITAL[-1]] = 20.0
        assert calcular_mae(prev, real) == pytest.approx(10.0 / 12, rel=1e-6)

    def test_candidato_ausente_em_realizados_lanca_keyerror(self):
        prev = {c: 100.0 / 12 for c in CANDIDATOS_EDITAL}
        real = {c: 100.0 / 12 for c in CANDIDATOS_EDITAL}
        del real[CANDIDATOS_EDITAL[0]]
        with pytest.raises(KeyError):
            calcular_mae(prev, real)

    def test_previstos_vazio_lanca_valueerror(self):
        with pytest.raises(ValueError):
            calcular_mae({}, {})


# ============================================================
# 4. Filtro por data_divulgacao -- importado de src/filtros.py
# ============================================================


@pytest.mark.parametrize("ano", [2006, 2010, 2014, 2018, 2022, 2026])
def test_filtro_vespera_inclui_vespera(ano):
    vespera = VESPERAS[ano]
    dia_eleicao = DIAS_ELEICAO[ano]
    df = pd.DataFrame(
        {"data_divulgacao": [vespera - pd.Timedelta(days=1), vespera, dia_eleicao],
         "nota": ["antes", "vespera", "dia_eleicao"]}
    )
    filtrado = filtrar_por_vespera(df, vespera)
    assert any(filtrado["nota"] == "vespera")


@pytest.mark.parametrize("ano", [2006, 2010, 2014, 2018, 2022, 2026])
def test_filtro_vespera_exclui_dia_da_eleicao(ano):
    vespera = VESPERAS[ano]
    dia_eleicao = DIAS_ELEICAO[ano]
    df = pd.DataFrame(
        {"data_divulgacao": [vespera - pd.Timedelta(days=1), vespera, dia_eleicao],
         "nota": ["antes", "vespera", "dia_eleicao"]}
    )
    filtrado = filtrar_por_vespera(df, vespera)
    assert not any(filtrado["nota"] == "dia_eleicao")


@pytest.mark.parametrize("ano", [2006, 2010, 2014, 2018, 2022, 2026])
def test_filtro_vespera_inclui_pesquisa_anterior(ano):
    vespera = VESPERAS[ano]
    dia_eleicao = DIAS_ELEICAO[ano]
    df = pd.DataFrame(
        {"data_divulgacao": [vespera - pd.Timedelta(days=1), vespera, dia_eleicao],
         "nota": ["antes", "vespera", "dia_eleicao"]}
    )
    filtrado = filtrar_por_vespera(df, vespera)
    assert any(filtrado["nota"] == "antes")


# ============================================================
# 5. Denominadores -- importado de src/tse.py
# ============================================================


class TestDenominadores:
    """
    Testa a funcao calcular_denominadores com DataFrame no formato
    detalhe_votacao_munzona do TSE.
    """

    def _df_urna(
        self,
        aptos=1_000_000,
        comparecimento=790_500,
        votos_validos=740_000,
        votos_brancos=25_250,
        votos_nulos=25_250,
    ) -> pd.DataFrame:
        abstencoes = aptos - comparecimento
        return pd.DataFrame({
            "QT_APTOS": [aptos],
            "QT_COMPARECIMENTO": [comparecimento],
            "QT_ABSTENCOES": [abstencoes],
            "QT_VOTOS_VALIDOS": [votos_validos],
            "QT_VOTOS_BRANCOS": [votos_brancos],
            "QT_VOTOS_NULOS": [votos_nulos],
        })

    def test_abstencao_sobre_aptos(self):
        res = calcular_denominadores(self._df_urna())
        assert abs(res["abstencao_pct"] - 20.95) < 0.01

    def test_brancos_sobre_comparecimento(self):
        res = calcular_denominadores(self._df_urna())
        assert abs(res["brancos_pct"] - 25_250 / 790_500 * 100) < 0.01

    def test_nulos_sobre_comparecimento(self):
        res = calcular_denominadores(self._df_urna())
        assert abs(res["nulos_pct"] - 25_250 / 790_500 * 100) < 0.01

    def test_validos_mais_brancos_mais_nulos_igual_comparecimento(self):
        df = self._df_urna()
        res = calcular_denominadores(df)
        assert res["votos_validos"] + res["votos_brancos"] + res["votos_nulos"] == res["comparecimento"]

    def test_multiplas_linhas_somadas(self):
        """Verifica que linhas de zonas/municipios sao somadas antes do calculo."""
        df = pd.DataFrame({
            "QT_APTOS": [500_000, 500_000],
            "QT_COMPARECIMENTO": [395_250, 395_250],
            "QT_ABSTENCOES": [104_750, 104_750],
            "QT_VOTOS_VALIDOS": [370_000, 370_000],
            "QT_VOTOS_BRANCOS": [12_625, 12_625],
            "QT_VOTOS_NULOS": [12_625, 12_625],
        })
        res = calcular_denominadores(df)
        assert res["aptos"] == 1_000_000
        assert abs(res["abstencao_pct"] - 20.95) < 0.01

    def test_colunas_faltando_lanca_valueerror(self):
        df = pd.DataFrame({"QT_APTOS": [100]})
        with pytest.raises(ValueError, match="ausentes"):
            calcular_denominadores(df)

    def test_df_vazio_lanca_valueerror(self):
        df = pd.DataFrame(columns=[
            "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES",
            "QT_VOTOS_VALIDOS", "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS",
        ])
        with pytest.raises(ValueError, match="vazio"):
            calcular_denominadores(df)


# ============================================================
# 6. Agregacao entre institutos -- importado de src/pesquisas.py
# ============================================================


class TestAgregacaoInstitutos:
    def test_nan_fica_fora_da_media(self):
        """NaN (ausente) nao conta no denominador da media."""
        df = pd.DataFrame({
            "Luiz Inácio Lula da Silva": [48.0, 50.0, float("nan")],
            "Flávio Bolsonaro": [36.0, 38.0, 40.0],
        })
        res = agregar_institutos(df, candidatos=["Luiz Inácio Lula da Silva", "Flávio Bolsonaro"])
        # Lula: media de [48, 50] = 49; Bolsonaro: media de [36, 38, 40] = 38
        assert abs(res["Luiz Inácio Lula da Silva"] - 49.0) < 1e-9
        assert abs(res["Flávio Bolsonaro"] - 38.0) < 1e-9

    def test_zero_entra_como_zero(self):
        """0 (medido como zero) entra no denominador da media."""
        df = pd.DataFrame({
            "Augusto Cury": [1.0, 0.0],
        })
        res = agregar_institutos(df, candidatos=["Augusto Cury"])
        assert abs(res["Augusto Cury"] - 0.5) < 1e-9  # media de [1, 0]

    def test_todos_nan_retorna_nan(self):
        df = pd.DataFrame({"Wilson Grassi": [float("nan"), float("nan")]})
        res = agregar_institutos(df, candidatos=["Wilson Grassi"])
        assert np.isnan(res["Wilson Grassi"])

    def test_candidato_ausente_no_df_retorna_nan(self):
        df = pd.DataFrame({"Luiz Inácio Lula da Silva": [48.0]})
        res = agregar_institutos(df, candidatos=["Luiz Inácio Lula da Silva", "Inexistente"])
        assert np.isnan(res["Inexistente"])

    def test_df_vazio_retorna_todos_nan(self):
        df = pd.DataFrame(columns=CANDIDATOS_EDITAL)
        res = agregar_institutos(df)
        assert all(np.isnan(v) for v in res.values())


# ============================================================
# 7. Sanidade TSE 2022 -- importado de src/config.py
# ============================================================


class TestSanidade2022:
    def _resultados_corretos(self) -> dict:
        return {
            "Luiz Inácio Lula da Silva": 48.43,
            "Jair Messias Bolsonaro": 43.20,
            "abstencao_pct": 20.95,
        }

    def test_sanidade_pass_com_resultados_corretos(self):
        assert verificar_sanidade_2022(self._resultados_corretos()) is True

    def test_sanidade_fail_com_lula_errado(self):
        res = self._resultados_corretos()
        res["Luiz Inácio Lula da Silva"] = 45.0
        assert verificar_sanidade_2022(res) is False

    def test_sanidade_fail_com_abstencao_errada(self):
        res = self._resultados_corretos()
        res["abstencao_pct"] = 15.0
        assert verificar_sanidade_2022(res) is False


# ============================================================
# 8. Integracao: sanidade 2022 lendo data/processed
#    (executa diretamente lendo os parquets gerados no Checkpoint 1)
# ============================================================

_PARQUET_DETALHE_2022 = PROCESSED_DIR / "detalhe_votacao_2022.parquet"
_PARQUET_CANDIDATO_2022 = PROCESSED_DIR / "votacao_candidato_2022.parquet"


@pytest.mark.skipif(
    not (_PARQUET_DETALHE_2022.exists() and _PARQUET_CANDIDATO_2022.exists()),
    reason="Arquivos parquet de 2022 nao existem em data/processed/",
)
def test_integracao_sanidade_2022_do_parquet():
    """
    Teste de integracao: le os parquets processados do TSE 2022.
    - Percentuais de votos validos dos candidatos vem de votacao_candidato_2022.parquet
      via calcular_votos_validos_candidatos (sem .get silencioso).
    - Abstencao vem de detalhe_votacao_2022.parquet via calcular_denominadores.
    """
    df_detalhe = pd.read_parquet(_PARQUET_DETALHE_2022)
    df_candidato = pd.read_parquet(_PARQUET_CANDIDATO_2022)

    res_denominadores = calcular_denominadores(df_detalhe)
    res_candidatos = calcular_votos_validos_candidatos(df_candidato)

    # Acesso direto sem .get silencioso: lanca KeyError se o candidato nao estiver presente
    lula_pct = res_candidatos["LULA"]
    bolsonaro_pct = res_candidatos["JAIR BOLSONARO"]
    abstencao_pct = res_denominadores["abstencao_pct"]

    assert verificar_sanidade_2022({
        "Luiz Inácio Lula da Silva": lula_pct,
        "Jair Messias Bolsonaro": bolsonaro_pct,
        "abstencao_pct": abstencao_pct,
    }) is True


# ============================================================
# 9. Validacao do XLSX -- importado de scripts/validar_entrega.py
# ============================================================


def _criar_xlsx_valido() -> bytes:
    """XLSX de exemplo conforme requisitos do edital."""
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Candidatos"
    ws1.append(["Candidato(a)", "Partido", "Previsão de votos válidos (%)"])
    # Distribui igualmente (maiores restos) para que soma seja exatamente 100,0%
    pcts = maiores_restos([100.0 / 12] * 12)
    for i, (nome, pct) in enumerate(zip(CANDIDATOS_EDITAL, pcts), start=2):
        ws1.append([nome, PARTIDOS_EDITAL[nome], pct])
        ws1.cell(row=i, column=3).number_format = "0.0"
    linha_total_idx = len(CANDIDATOS_EDITAL) + 2
    ws1.append(["Total", "", 100.0])
    ws1.cell(row=linha_total_idx, column=3).number_format = "0.0"

    ws2 = wb.create_sheet("Adicionais")
    ws2.append(["Resultado", "Previsão (%)"])
    ws2.append(["Abstenção", 20.95])
    ws2.cell(row=2, column=2).number_format = "0.0"
    ws2.append(["Votos brancos", 2.5])
    ws2.cell(row=3, column=2).number_format = "0.0"
    ws2.append(["Votos nulos", 2.5])
    ws2.cell(row=4, column=2).number_format = "0.0"

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _salvar_xlsx_temporario(conteudo: bytes, tmp_path: Path) -> Path:
    p = tmp_path / "previsao.xlsx"
    p.write_bytes(conteudo)
    return p


class TestValidacaoXLSX:
    def test_xlsx_valido_passa(self, tmp_path):
        p = _salvar_xlsx_temporario(_criar_xlsx_valido(), tmp_path)
        res = validar_xlsx(p)
        assert res["valido"], res["erros"]

    def test_gerar_planilha_entrega_produz_arquivo_valido(self, tmp_path):
        cands = {c: 100.0 / 12 for c in CANDIDATOS_EDITAL}
        ad = {"abstencao": 22.3, "brancos": 1.6, "nulos": 2.8}
        out_file = tmp_path / "entrega_teste.xlsx"
        gerar_planilha_entrega(cands, ad, out_file)
        res = validar_xlsx(out_file)
        assert res["valido"], res["erros"]

    def test_xlsx_com_uma_aba_falha(self, tmp_path):
        wb = openpyxl.Workbook()
        buf = io.BytesIO()
        wb.save(buf)
        p = tmp_path / "invalido.xlsx"
        p.write_bytes(buf.getvalue())
        res = validar_xlsx(p)
        assert not res["valido"]
        assert any("2 abas" in e for e in res["erros"])

    def test_xlsx_nome_errado_falha(self, tmp_path):
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = "Candidatos"
        ws1.append(["Candidato(a)", "Partido", "Previsão de votos válidos (%)"])
        ws1.append(["Nome Errado", "Partido X", 100.0])
        ws1.cell(row=2, column=3).number_format = "0.0"
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Resultado", "Previsão (%)"])
        ws2.append(["Abstenção", 20.0])
        ws2.cell(row=2, column=2).number_format = "0.0"
        ws2.append(["Votos brancos", 2.0])
        ws2.cell(row=3, column=2).number_format = "0.0"
        ws2.append(["Votos nulos", 2.0])
        ws2.cell(row=4, column=2).number_format = "0.0"
        buf = io.BytesIO()
        wb.save(buf)
        p = tmp_path / "nome_errado.xlsx"
        p.write_bytes(buf.getvalue())
        res = validar_xlsx(p)
        assert not res["valido"]
        assert any("extra" in e or "faltando" in e for e in res["erros"])

    def test_xlsx_partido_errado_falha(self, tmp_path):
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = "Candidatos"
        ws1.append(["Candidato(a)", "Partido", "Previsão de votos válidos (%)"])
        pcts = maiores_restos([100.0 / 12] * 12)
        for i, (nome, pct) in enumerate(zip(CANDIDATOS_EDITAL, pcts), start=2):
            partido = PARTIDOS_EDITAL[nome] if nome != "Augusto Cury" else "PARTIDO_ERRADO"
            ws1.append([nome, partido, pct])
            ws1.cell(row=i, column=3).number_format = "0.0"
        ws1.append(["Total", "", 100.0])
        ws1.cell(row=len(CANDIDATOS_EDITAL) + 2, column=3).number_format = "0.0"
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Resultado", "Previsão (%)"])
        ws2.append(["Abstenção", 21.0])
        ws2.cell(row=2, column=2).number_format = "0.0"
        ws2.append(["Votos brancos", 2.0])
        ws2.cell(row=3, column=2).number_format = "0.0"
        ws2.append(["Votos nulos", 2.0])
        ws2.cell(row=4, column=2).number_format = "0.0"
        buf = io.BytesIO()
        wb.save(buf)
        p = tmp_path / "partido_errado.xlsx"
        p.write_bytes(buf.getvalue())
        res = validar_xlsx(p)
        assert not res["valido"]
        assert any("Partido errado" in e for e in res["erros"])

    def test_xlsx_sem_linha_total_falha(self, tmp_path):
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = "Candidatos"
        ws1.append(["Candidato(a)", "Partido", "Previsão de votos válidos (%)"])
        pcts = maiores_restos([100.0 / 12] * 12)
        for i, (nome, pct) in enumerate(zip(CANDIDATOS_EDITAL, pcts), start=2):
            ws1.append([nome, PARTIDOS_EDITAL[nome], pct])
            ws1.cell(row=i, column=3).number_format = "0.0"
        # Sem linha Total
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Resultado", "Previsão (%)"])
        ws2.append(["Abstenção", 21.0])
        ws2.cell(row=2, column=2).number_format = "0.0"
        ws2.append(["Votos brancos", 2.0])
        ws2.cell(row=3, column=2).number_format = "0.0"
        ws2.append(["Votos nulos", 2.0])
        ws2.cell(row=4, column=2).number_format = "0.0"
        buf = io.BytesIO()
        wb.save(buf)
        p = tmp_path / "sem_total.xlsx"
        p.write_bytes(buf.getvalue())
        res = validar_xlsx(p)
        assert not res["valido"]
        assert any("Total" in e for e in res["erros"])

    def test_xlsx_rotulo_sem_acento_falha(self, tmp_path):
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = "Candidatos"
        ws1.append(["Candidato(a)", "Partido", "Previsao de votos validos (%)"])  # sem acento
        pcts = maiores_restos([100.0 / 12] * 12)
        for i, (nome, pct) in enumerate(zip(CANDIDATOS_EDITAL, pcts), start=2):
            ws1.append([nome, PARTIDOS_EDITAL[nome], pct])
            ws1.cell(row=i, column=3).number_format = "0.0"
        ws1.append(["Total", "", 100.0])
        ws1.cell(row=14, column=3).number_format = "0.0"
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Resultado", "Previsão (%)"])
        ws2.append(["Abstenção", 21.0])
        ws2.cell(row=2, column=2).number_format = "0.0"
        ws2.append(["Votos brancos", 2.0])
        ws2.cell(row=3, column=2).number_format = "0.0"
        ws2.append(["Votos nulos", 2.0])
        ws2.cell(row=4, column=2).number_format = "0.0"
        buf = io.BytesIO()
        wb.save(buf)
        p = tmp_path / "sem_acento.xlsx"
        p.write_bytes(buf.getvalue())
        res = validar_xlsx(p)
        assert not res["valido"]
        assert any("Cabecalho da Aba 1 invalido" in e for e in res["erros"])

    def test_xlsx_number_format_invalido_falha(self, tmp_path):
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = "Candidatos"
        ws1.append(["Candidato(a)", "Partido", "Previsão de votos válidos (%)"])
        pcts = maiores_restos([100.0 / 12] * 12)
        for i, (nome, pct) in enumerate(zip(CANDIDATOS_EDITAL, pcts), start=2):
            ws1.append([nome, PARTIDOS_EDITAL[nome], pct])
            # number_format padrao 'General', nao '0.0'
        ws1.append(["Total", "", 100.0])
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Resultado", "Previsão (%)"])
        ws2.append(["Abstenção", 21.0])
        ws2.cell(row=2, column=2).number_format = "0.0"
        ws2.append(["Votos brancos", 2.0])
        ws2.cell(row=3, column=2).number_format = "0.0"
        ws2.append(["Votos nulos", 2.0])
        ws2.cell(row=4, column=2).number_format = "0.0"
        buf = io.BytesIO()
        wb.save(buf)
        p = tmp_path / "format_invalido.xlsx"
        p.write_bytes(buf.getvalue())
        res = validar_xlsx(p)
        assert not res["valido"]
        assert any("Formato numerico invalido" in e for e in res["erros"])

    def test_valores_numeros_finais_latex_coincidem_com_xlsx(self):
        """
        Garante que os valores em docs/numeros_finais.tex sao identicos
        aos da Aba 1 (Candidatos) e Aba 2 (Adicionais) de outputs/previsao_2026.xlsx.
        """
        xlsx_path = OUTPUTS_DIR / "previsao_2026.xlsx"
        tex_path = DOCS_DIR / "numeros_finais.tex"
        assert xlsx_path.exists(), "outputs/previsao_2026.xlsx deve existir"
        assert tex_path.exists(), "docs/numeros_finais.tex deve existir"

        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        ws1 = wb["Candidatos"]
        ws2 = wb["Adicionais"]

        # Le Aba 1
        cands_xlsx = {}
        for row in ws1.iter_rows(min_row=2, values_only=True):
            nome = str(row[0] or "").strip()
            if nome and nome.lower() != "total":
                cands_xlsx[nome] = round(float(row[2]), 1)

        # Le Aba 2
        aba2_xlsx = {}
        for row in ws2.iter_rows(min_row=2, values_only=True):
            item = str(row[0] or "").strip()
            if item:
                aba2_xlsx[item.lower()] = round(float(row[1]), 1)

        # Parse macros de docs/numeros_finais.tex
        tex_content = tex_path.read_text(encoding="utf-8")
        macros = {}
        for match in re.finditer(r"\\newcommand\{\\([a-zA-Z0-9]+)\}\{([^}]+)\}", tex_content):
            macros[match.group(1)] = match.group(2).strip()

        # Mapeamento oficial dos candidatos
        mapa_cands = {
            "Luiz Inácio Lula da Silva": "pLula",
            "Flávio Bolsonaro": "pFlavio",
            "Augusto Cury": "pCury",
            "Ronaldo Caiado": "pCaiado",
            "Renan Santos": "pRenan",
            "Romeu Zema": "pZema",
            "Samara Martins": "pSamara",
            "Clariana Barão": "pClariana",
            "Edmilson Costa": "pEdmilson",
            "Hertz Dias": "pHertz",
            "Rui Costa Pimenta": "pRui",
            "Wilson Grassi": "pWilson",
        }

        # Confere cada candidato da Aba 1
        for cand, macro in mapa_cands.items():
            assert macro in macros, f"Macro \\{macro} nao encontrada em numeros_finais.tex"
            val_tex = float(macros[macro].replace(",", "."))
            val_xlsx = cands_xlsx[cand]
            assert val_tex == val_xlsx, f"Divergencia em {cand}: tex={val_tex} vs xlsx={val_xlsx}"

        # Confere Aba 2
        p_abst_tex = float(macros["pAbst"].replace(",", "."))
        p_brancos_tex = float(macros["pBrancos"].replace(",", "."))
        p_nulos_tex = float(macros["pNulos"].replace(",", "."))

        p_abst_xlsx = next(v for k, v in aba2_xlsx.items() if "abst" in k)
        p_brancos_xlsx = next(v for k, v in aba2_xlsx.items() if "branco" in k)
        p_nulos_xlsx = next(v for k, v in aba2_xlsx.items() if "nulo" in k)

        assert p_abst_tex == p_abst_xlsx, f"Abstencao diverge: tex={p_abst_tex} vs xlsx={p_abst_xlsx}"
        assert p_brancos_tex == p_brancos_xlsx, f"Brancos diverge: tex={p_brancos_tex} vs xlsx={p_brancos_xlsx}"
        assert p_nulos_tex == p_nulos_xlsx, f"Nulos diverge: tex={p_nulos_tex} vs xlsx={p_nulos_xlsx}"



# ============================================================
# 10. Validacao do arquivo manual pesquisas_2026.csv
# ============================================================


class TestPesquisas2026Manual:
    def test_arquivo_existe_e_possui_linhas(self):
        assert PESQUISAS_2026_PATH.exists()
        df = pd.read_csv(PESQUISAS_2026_PATH)
        assert len(df) >= 6

    def test_colunas_obrigatorias_presentes(self):
        df = pd.read_csv(PESQUISAS_2026_PATH)
        for col in PESQUISAS_2026_SCHEMA:
            assert col in df.columns, f"Coluna obrigatoria ausente: {col}"

    def test_soma_intencoes_por_linha(self):
        """
        Soma dos candidatos detalhados + outros_agregado + brancos/nulos + indecisos
        deve estar entre 97.0 e 101.5% por linha.
        """
        df = pd.read_csv(PESQUISAS_2026_PATH)
        for idx, row in df.iterrows():
            cand_vals = [row[c] for c in CANDIDATOS_EDITAL if pd.notna(row[c])]
            outros = (
                row["outros_agregado"]
                if "outros_agregado" in df.columns and pd.notna(row["outros_agregado"])
                else 0.0
            )
            bn = row["brancos_nulos"] if pd.notna(row["brancos_nulos"]) else 0.0
            ind = row["indecisos"] if pd.notna(row["indecisos"]) else 0.0
            soma = sum(cand_vals) + outros + bn + ind
            assert 97.0 <= soma <= 101.5, (
                f"Linha {idx} ({row['instituto']}) tem soma={soma:.1f} fora de [97, 101.5]"
            )

    def test_candidatos_nao_divulgados_sao_nan(self):
        """
        Candidatos que nao foram divulgados individualmente pelo instituto
        devem ser NaN (vazio), nao 0.0.
        """
        df = pd.read_csv(PESQUISAS_2026_PATH)
        atlas = df[df["instituto"] == "AtlasIntel"]
        if not atlas.empty:
            assert pd.isna(atlas.iloc[0]["Clariana Barão"])
            assert pd.isna(atlas.iloc[0]["Edmilson Costa"])

    def test_transcricao_pesquisas_2026_contra_html_salvo(self):
        """
        Teste estrito de transcricao: para cada celula numerica nao-NaN de
        pesquisas_2026.csv, o valor deve aparecer comprovadamente a uma distancia
        maxima de 130 caracteres do nome do candidato ou rotulo tematico correspondente.
        Para valores iguais a 0.0, exige mencao explicita a '0%', 'nao pontuou' ou similar.
        """
        import csv
        import re
        from bs4 import BeautifulSoup

        assert MANIFEST_PATH.exists()
        manifest_map = {}
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                manifest_map[row["url"]] = row["arquivo"]

        df = pd.read_csv(PESQUISAS_2026_PATH)
        assert len(df) >= 6

        aliases_map = {
            "Luiz Inácio Lula da Silva": ["lula da silva", "lula"],
            "Flávio Bolsonaro": ["flávio bolsonaro", "flavio bolsonaro", "flávio", "flavio"],
            "Augusto Cury": ["augusto cury", "cury"],
            "Renan Santos": ["renan santos", "renan"],
            "Ronaldo Caiado": ["ronaldo caiado", "caiado"],
            "Romeu Zema": ["romeu zema", "zema"],
            "Clariana Barão": ["clariana barão", "clariana barao", "clariana"],
            "Edmilson Costa": ["edmilson costa", "edmilson"],
            "Hertz Dias": ["hertz dias", "hertz"],
            "Rui Costa Pimenta": ["rui costa pimenta", "rui pimenta", "rui costa", "rui"],
            "Samara Martins": ["samara martins", "samara"],
            "Wilson Grassi": ["wilson grassi", "wilson"],
            "brancos_nulos": ["branco", "brancos", "nulo", "nulos", "branco/nulo", "brancos/nulos"],
            "indecisos": ["indeciso", "indecisos", "não sabe", "nao sabe", "não souberam", "nao souberam", "não responderam", "nao responderam", "ns/nr"],
            "outros_agregado": ["outros", "demais", "outros candidatos", "cada um"],
        }

        for idx, row in df.iterrows():
            url = row["fonte_url"]
            assert url in manifest_map, f"URL {url} nao encontrada no MANIFEST.csv"
            rel_file = manifest_map[url]
            html_path = RAW_DIR / rel_file
            assert html_path.exists(), f"Arquivo HTML {html_path} nao existe"

            with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = BeautifulSoup(f.read(), "html.parser").get_text()

            # Normaliza espacos
            text_norm = re.sub(r"\s+", " ", raw_text).lower()

            colunas_a_testar = [
                c for c in aliases_map.keys() if c in df.columns
            ]
            for col in colunas_a_testar:
                val = row[col]
                if pd.isna(val) or val == "":
                    continue
                num = float(val)
                termos = aliases_map[col]

                # Localiza janelas de 130 chars em torno de qualquer dos termos
                janelas = []
                for termo in termos:
                    for m in re.finditer(re.escape(termo), text_norm):
                        s_idx = max(0, m.start() - 130)
                        e_idx = min(len(text_norm), m.end() + 130)
                        janelas.append(text_norm[s_idx:e_idx])

                assert janelas, (
                    f"Linha {idx} ({row['instituto']}): nenhum termo de {termos} "
                    f"encontrado no HTML {html_path}"
                )

                num_int = int(round(num)) if abs(num - round(num)) < 1e-6 else None
                if num == 0.0:
                    padroes = [
                        "0%", "0 %", "0,0%", "0.0%", "não pontuou", "nao pontuou",
                        "não pontuam", "nao pontuam", "não pontuaram", "nao pontuaram", "zero"
                    ]
                elif num_int is not None:
                    padroes = [
                        f"{num_int}%", f"{num_int} %", f"{num_int},", f"{num_int}.",
                        f" {num_int} ", f"{num_int} ponto", f"{num_int} pontos"
                    ]
                else:
                    s_virg = f"{num:.1f}".replace(".", ",")
                    s_pt = f"{num:.1f}"
                    padroes = [f"{s_virg}%", f"{s_virg} %", f"{s_pt}%", f"{s_pt} %", s_virg, s_pt]

                found = any(any(p in j for p in padroes) for j in janelas)
                assert found, (
                    f"Linha {idx} ({row['instituto']}): valor {val} para '{col}' "
                    f"nao encontrado em raio de 130 caracteres dos termos {termos} no HTML {html_path}"
                )


# ============================================================
# 11. Validacao do arquivo processado pesquisas_historicas.parquet
# ============================================================


class TestPesquisasHistoricas:
    def test_arquivo_parquet_existe(self):
        caminho = PROCESSED_DIR / "pesquisas_historicas.parquet"
        assert caminho.exists(), "pesquisas_historicas.parquet nao encontrado"

    def test_cinco_eleicoes_presentes(self):
        df = carregar_pesquisas_historicas()
        anos = sorted(df["eleicao"].unique().tolist())
        assert anos == [2006, 2010, 2014, 2018, 2022]

    def test_todas_as_pesquisas_dentro_da_janela_de_corte(self):
        """
        Para cada eleicao, data_divulgacao deve ser <= vespera e >= janela de 21 dias.
        Nenhuma pesquisa divulgada no dia da eleicao ou apos pode estar presente.
        """
        df = carregar_pesquisas_historicas()
        for ano in [2006, 2010, 2014, 2018, 2022]:
            df_ano = df[df["eleicao"] == ano]
            vespera = VESPERAS[ano].strftime("%Y-%m-%d")
            dia_eleicao = DIAS_ELEICAO[ano].strftime("%Y-%m-%d")

            max_div = df_ano["data_divulgacao"].max()
            assert max_div <= vespera, (
                f"Eleicao {ano}: pesquisa divulgada apos a vespera ({max_div} > {vespera})"
            )
            assert max_div < dia_eleicao, (
                f"Eleicao {ano}: pesquisa divulgada no dia da eleicao ({max_div})"
            )

    def test_principais_institutos_presentes(self):
        df = carregar_pesquisas_historicas()
        institutos = set(df["instituto"].unique())
        assert "Datafolha" in institutos
        assert "Ibope" in institutos
        assert "Ipec" in institutos

    def test_coluna_contratante_presente(self):
        df = carregar_pesquisas_historicas()
        assert "contratante" in df.columns, "Coluna 'contratante' ausente no parquet"

    def test_filtro_por_ano_em_carregar_pesquisas_historicas(self):
        df_2022 = carregar_pesquisas_historicas(2022)
        assert len(df_2022) >= 30
        assert (df_2022["eleicao"] == 2022).all()

    def test_sem_dupla_contagem_ou_sobreposicao_campo(self):
        """
        Auditoria Checkpoint 3 (Item 5):
        Garante que nao ha linhas duplicadas em pesquisas_historicas.parquet e que
        o tracking do Vox Populi em 2010 respeita o espacamento de 4 dias sem sobreposicao.
        """
        df = carregar_pesquisas_historicas()

        # 1. Zero duplicatas exatas por eleicao, instituto, data_divulgacao e amostra
        cols_id = ["eleicao", "instituto", "data_divulgacao", "amostra"]
        dups = df[df.duplicated(subset=cols_id, keep=False)]
        assert len(dups) == 0, f"Encontradas {len(dups)} linhas duplicadas: {dups[cols_id]}"

        # 2. Tracking Vox Populi 2010: rodadas consecutivas espacadas em pelo menos 4 dias
        vp_2010 = df[(df["eleicao"] == 2010) & (df["instituto"] == "Vox Populi")].sort_values("data_divulgacao")
        datas_vp = pd.to_datetime(vp_2010["data_divulgacao"]).tolist()
        for i in range(len(datas_vp) - 1):
            dias_diff = (datas_vp[i + 1] - datas_vp[i]).days
            assert dias_diff >= 4, (
                f"Sobreposicao no Vox Populi 2010: rodada {datas_vp[i]} e {datas_vp[i + 1]} com apenas {dias_diff} dias de diferenca"
            )


# ============================================================
# 12. Sanidade historica das vesperas do Datafolha (2014, 2018, 2022)
# ============================================================


class TestSanidadeVesperasDatafolha:
    """
    Verifica a sanidade historica das pesquisas de vespera do Datafolha
    em votos validos (tolerancia de 1,0 p.p.):
    - 2022: Lula 50%, Bolsonaro 36%
    - 2018: Bolsonaro 40%, Haddad 25%
    - 2014: Dilma 44%, Aecio 26%, Marina 24%
    """

    def test_vespera_datafolha_2022_votos_validos(self):
        df = carregar_pesquisas_historicas(2022)
        vespera = df[(df["instituto"] == "Datafolha") & (df["data_divulgacao"] == "2022-10-01")].iloc[0]
        cands = ["Luiz Inácio Lula da Silva", "Jair Bolsonaro", "Ciro Gomes", "Simone Tebet", "Soraya Thronicke", "Felipe D'Avila"]
        soma = sum(vespera[c] for c in cands if pd.notna(vespera[c]))
        lula_val = (vespera["Luiz Inácio Lula da Silva"] / soma) * 100
        bols_val = (vespera["Jair Bolsonaro"] / soma) * 100
        assert abs(lula_val - 50.0) <= 1.0, f"Lula 2022 vespera esperado ~50, obtido {lula_val:.2f}"
        assert abs(bols_val - 36.0) <= 1.0, f"Bolsonaro 2022 vespera esperado ~36, obtido {bols_val:.2f}"

    def test_vespera_datafolha_2018_votos_validos(self):
        df = carregar_pesquisas_historicas(2018)
        vespera = df[(df["instituto"] == "Datafolha") & (df["data_divulgacao"] == "2018-10-06")].iloc[0]
        cands = ["Jair Bolsonaro", "Fernando Haddad", "Ciro Gomes", "Geraldo Alckmin", "Marina Silva", "João Amoêdo", "Henrique Meirelles", "Alvaro Dias"]
        soma = sum(vespera[c] for c in cands if pd.notna(vespera[c]))
        bols_val = (vespera["Jair Bolsonaro"] / soma) * 100
        had_val = (vespera["Fernando Haddad"] / soma) * 100
        assert abs(bols_val - 40.0) <= 1.0, f"Bolsonaro 2018 vespera esperado ~40, obtido {bols_val:.2f}"
        assert abs(had_val - 25.0) <= 1.0, f"Haddad 2018 vespera esperado ~25, obtido {had_val:.2f}"

    def test_vespera_datafolha_2014_votos_validos(self):
        df = carregar_pesquisas_historicas(2014)
        vespera = df[(df["instituto"] == "Datafolha") & (df["data_divulgacao"] == "2014-10-04")].iloc[0]
        cands = ["Dilma Rousseff", "Aécio Neves", "Marina Silva", "Luciana Genro", "Pastor Everaldo", "Eduardo Jorge"]
        soma = sum(vespera[c] for c in cands if pd.notna(vespera[c]))
        dilma_val = (vespera["Dilma Rousseff"] / soma) * 100
        aecio_val = (vespera["Aécio Neves"] / soma) * 100
        marina_val = (vespera["Marina Silva"] / soma) * 100
        assert abs(dilma_val - 44.0) <= 1.0, f"Dilma 2014 vespera esperado ~44, obtido {dilma_val:.2f}"
        assert abs(aecio_val - 26.0) <= 1.0, f"Aecio 2014 vespera esperado ~26, obtido {aecio_val:.2f}"
        assert abs(marina_val - 24.0) <= 1.0, f"Marina 2014 vespera esperado ~24, obtido {marina_val:.2f}"


# ============================================================
# 13. Validacao de Priors de Nanicos e Incumbencia Governista
# ============================================================


class TestPriorsNanicosEIncumbencia:
    def test_priors_nanicos_contem_todos_candidatos_e_valores_razoaveis(self):
        from src.nanicos import calcular_priors_nanicos_tse

        priors = calcular_priors_nanicos_tse()
        esperados = [
            "Clariana Barão",
            "Edmilson Costa",
            "Hertz Dias",
            "Rui Costa Pimenta",
            "Samara Martins",
            "Wilson Grassi",
        ]
        for c in esperados:
            assert c in priors, f"Candidato {c} ausente nos priors de nanicos"
            assert 0.005 <= priors[c] <= 0.20, f"Prior {priors[c]} fora da faixa razoavel para {c}"

        # Verifica valores exatos das medianas do TSE
        assert abs(priors["Clariana Barão"] - 0.0589) < 1e-4
        assert abs(priors["Edmilson Costa"] - 0.0386) < 1e-4
        assert abs(priors["Hertz Dias"] - 0.0677) < 1e-4
        assert abs(priors["Rui Costa Pimenta"] - 0.0119) < 1e-4
        assert abs(priors["Samara Martins"] - 0.0453) < 1e-4
        assert abs(priors["Wilson Grassi"] - 0.0546) < 1e-4

    def test_incumbencia_governista_mapeamento_correto(self):
        from src.incumbencia import obter_incumbencia

        # 2006: Lula incumbente
        assert obter_incumbencia(2006, "Luiz Inácio Lula da Silva") == 1
        assert obter_incumbencia(2006, "Geraldo Alckmin") == 0

        # 2010: Dilma apoiada pelo governo
        assert obter_incumbencia(2010, "Dilma Rousseff") == 1
        assert obter_incumbencia(2010, "José Serra") == 0

        # 2014: Dilma incumbente
        assert obter_incumbencia(2014, "Dilma Rousseff") == 1
        assert obter_incumbencia(2014, "Aécio Neves") == 0

        # 2018: Meirelles candidato governista do governo Temer
        assert obter_incumbencia(2018, "Henrique Meirelles") == 1
        assert obter_incumbencia(2018, "Jair Bolsonaro") == 0
        assert obter_incumbencia(2018, "Fernando Haddad") == 0

        # 2022: Bolsonaro incumbente
        assert obter_incumbencia(2022, "Jair Bolsonaro") == 1
        assert obter_incumbencia(2022, "Luiz Inácio Lula da Silva") == 0

        # 2026: Lula incumbente
        assert obter_incumbencia(2026, "Luiz Inácio Lula da Silva") == 1
        assert obter_incumbencia(2026, "Flávio Bolsonaro") == 0


class TestBacktestHistorico:
    """Valida motores de estimacao e metricas do Checkpoint 3."""

    def test_renormalizar_votos_soma_100_e_trunca_negativos(self):
        d = {"A": 40.0, "B": 40.0, "C": -10.0}
        norm = renormalizar_votos(d)
        assert abs(sum(norm.values()) - 100.0) < 1e-6
        assert norm["C"] == 0.0
        assert norm["A"] == 50.0
        assert norm["B"] == 50.0

    def test_estimar_m0_2022_soma_100_e_contem_candidatos(self):
        df_2022 = carregar_pesquisas_historicas(2022)
        p0 = estimar_m0(df_2022, 2022)
        assert abs(sum(p0.values()) - 100.0) < 1e-4
        assert "Luiz Inácio Lula da Silva" in p0
        assert "Jair Bolsonaro" in p0
        assert p0["Luiz Inácio Lula da Silva"] > 40.0
        assert p0["Jair Bolsonaro"] > 35.0

    def test_estimar_m1_2022_soma_100(self):
        df_2022 = carregar_pesquisas_historicas(2022)
        p1 = estimar_m1(df_2022, 2022, meia_vida=7.0)
        assert abs(sum(p1.values()) - 100.0) < 1e-4
        assert all(v >= 0.0 for v in p1.values())

    def test_calcular_house_effects_relativos_com_shrinkage(self):
        he = calcular_house_effects_relativos([2006, 2010, 2014, 2018], k_shrinkage=3.0)
        assert isinstance(he, dict)
        for (inst, b), val in he.items():
            assert isinstance(inst, str)
            assert b in ["pt", "adv", "demais"]
            assert isinstance(val, float)

    def test_calcular_diferenca_e_se_valores_conhecidos(self):
        mae_a = [2.0, 3.0, 4.0]
        mae_b = [1.0, 2.0, 3.0]
        d_bar, se_d = calcular_diferenca_e_se(mae_a, mae_b)
        assert abs(d_bar - 1.0) < 1e-6
        assert abs(se_d - 0.0) < 1e-6

        # Com variabilidade
        mae_a2 = [1.0, 2.0, 3.0]
        mae_b2 = [1.0, 1.0, 1.0]
        # deltas = [0, 1, 2] -> media = 1.0, s = 1.0, se = 1.0 / sqrt(3)
        d_bar2, se_d2 = calcular_diferenca_e_se(mae_a2, mae_b2)
        assert abs(d_bar2 - 1.0) < 1e-6
        assert abs(se_d2 - (1.0 / np.sqrt(3))) < 1e-6

    def test_mae_calculado_sobre_todos_candidatos_urna_tse(self):
        """Item 1: Denominador do MAE deve ser o total de candidatos da urna oficial."""
        from src.backtest import calcular_mae_eleicao, carregar_resultado_tse

        res_2022 = carregar_resultado_tse(2022)
        assert len(res_2022) == 11, "2022 deve conter 11 candidatos oficiais na urna"
        # Previsao hipotetica onde um nanico falta: deve receber 0.0 e ser penalizado
        preds = {c: res_2022[c] for c in list(res_2022.keys())[:-1]}
        mae = calcular_mae_eleicao(preds, res_2022)
        ultimo_cand = list(res_2022.keys())[-1]
        assert mae == pytest.approx(res_2022[ultimo_cand] / 11.0)

    def test_prior_nanicos_rejeitado_pela_regra_no_historico(self):
        """Item 2: Prior de nanicos e neutro no historico (delta=0), entao w=0 no modelo oficial."""
        from src.backtest import aplicar_ajuste_priors_nanicos

        # Em eleicoes anteriores a 2026, nao altera predicoes
        preds_2022 = {"Luiz Inácio Lula da Silva": 50.0, "Jair Bolsonaro": 50.0}
        adj = aplicar_ajuste_priors_nanicos(preds_2022, 2022, w=0.5)
        assert adj == preds_2022

        # Em 2026, com w=0, predicoes que somam 100% permanecem inalteradas
        preds_2026 = {
            "Luiz Inácio Lula da Silva": 50.0,
            "Flávio Bolsonaro": 49.6,
            "Clariana Barão": 0.2,
            "Wilson Grassi": 0.2,
        }
        adj_w0 = aplicar_ajuste_priors_nanicos(preds_2026, 2026, w=0.0)
        assert abs(adj_w0["Clariana Barão"] - 0.2) < 1e-4
        assert abs(adj_w0["Wilson Grassi"] - 0.2) < 1e-4

    def test_consistencia_mae_vs_tabela_candidato_a_candidato(self):
        """
        Auditoria Checkpoint 3 (Rodada 3): Para cada eleicao (2014, 2018, 2022) e configuracao
        (M0 e Modelo Oficial), o MAE reportado no relatorio coincide com a media dos desvios
        absolutos (|erro|) da tabela candidato a candidato com tolerancia menor que 0.001.
        """
        import re
        from src.config import REPORTS_DIR

        relatorio_path = REPORTS_DIR / "checkpoint_3.md"
        assert relatorio_path.exists(), "checkpoint_3.md deve existir"
        texto = relatorio_path.read_text(encoding="utf-8")

        for ano in [2014, 2018, 2022]:
            padrao = rf"### Eleicao {ano} \(\$K=\d+\$ Candidatos\)(.*?)(?=### Eleicao|\n---|\Z)"
            match = re.search(padrao, texto, re.DOTALL)
            assert match is not None, f"Secao da eleicao {ano} deve existir no relatorio"
            bloco = match.group(1)

            linhas = [linha.strip() for linha in bloco.strip().splitlines() if linha.startswith("|")]
            assert len(linhas) >= 4, f"Tabela de {ano} deve conter cabecalho e candidatos"

            linhas_cands = [
                linha for linha in linhas[2:] if "MAE da Eleição" not in linha and "MAE da Eleicao" not in linha
            ]
            linha_rodape = [
                linha for linha in linhas[2:] if "MAE da Eleição" in linha or "MAE da Eleicao" in linha
            ]
            assert len(linha_rodape) == 1, f"Tabela de {ano} deve conter exatamente 1 linha de rodape com MAE"

            erros_m0 = []
            erros_ofic = []
            for linha in linhas_cands:
                partes = [p.strip() for p in linha.split("|")[1:-1]]
                err_m0_str = partes[3].replace("%", "").replace(",", ".").replace("+", "")
                err_ofic_str = partes[5].replace("%", "").replace(",", ".").replace("+", "")
                erros_m0.append(abs(float(err_m0_str)))
                erros_ofic.append(abs(float(err_ofic_str)))

            partes_rodape = [p.strip() for p in linha_rodape[0].split("|")[1:-1]]
            mae_m0_rep = float(partes_rodape[3].replace("**", "").replace(",", "."))
            mae_ofic_rep = float(partes_rodape[5].replace("**", "").replace(",", "."))

            media_erros_m0 = float(np.mean(erros_m0))
            media_erros_ofic = float(np.mean(erros_ofic))

            assert abs(mae_m0_rep - media_erros_m0) < 0.001, (
                f"Ano {ano} M0: MAE reportado ({mae_m0_rep}) difere da media da tabela ({media_erros_m0:.4f})"
            )
            assert abs(mae_ofic_rep - media_erros_ofic) < 0.001, (
                f"Ano {ano} Oficial: MAE reportado ({mae_ofic_rep}) difere da media da tabela ({media_erros_ofic:.4f})"
            )


class TestMetodologiaPDF:
    """Testes de conformidade estrita para o PDF oficial docs/metodologia.pdf."""

    def test_metodologia_pdf_existe_e_tem_exatamente_duas_paginas(self):
        import pypdf
        from src.config import DOCS_DIR

        pdf_path = DOCS_DIR / "metodologia.pdf"
        assert pdf_path.exists(), "docs/metodologia.pdf deve existir"
        reader = pypdf.PdfReader(pdf_path)
        assert len(reader.pages) == 2, f"docs/metodologia.pdf deve ter exatamente 2 paginas, tem {len(reader.pages)}"

    def test_metodologia_pdf_contem_todos_percentuais_com_virgula_e_sem_preliminar(self):
        import openpyxl
        import pypdf
        from src.config import DOCS_DIR, OUTPUTS_DIR

        pdf_path = DOCS_DIR / "metodologia.pdf"
        assert pdf_path.exists()
        reader = pypdf.PdfReader(pdf_path)
        texto = "\n".join(p.extract_text() for p in reader.pages)

        # Regra: palavra PRELIMINAR proibida no PDF final
        assert "PRELIMINAR" not in texto.upper(), "A palavra PRELIMINAR nao pode aparecer no PDF final"

        # Regra: todos os percentuais do xlsx devem constar com virgula no PDF
        xlsx_path = OUTPUTS_DIR / "previsao_2026.xlsx"
        assert xlsx_path.exists()
        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        ws1 = wb["Candidatos"]
        ws2 = wb["Adicionais"]

        faltantes = []
        for row in ws1.iter_rows(min_row=2, values_only=True):
            nome = str(row[0] or "").strip()
            if nome and nome.lower() != "total":
                val = float(row[2])
                v_str = f"{val:.1f}%".replace(".", ",")
                if v_str not in texto:
                    faltantes.append(f"Aba 1 ({nome}): {v_str}")

        for row in ws2.iter_rows(min_row=2, values_only=True):
            lbl = str(row[0] or "").strip()
            if lbl:
                val = float(row[1])
                v_str = f"{val:.1f}%".replace(".", ",")
                if v_str not in texto:
                    faltantes.append(f"Aba 2 ({lbl}): {v_str}")

        assert not faltantes, f"Percentuais do XLSX nao encontrados no PDF: {faltantes}"

