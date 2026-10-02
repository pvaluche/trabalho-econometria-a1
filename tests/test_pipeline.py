"""
Testes unitarios e de integracao para os modulos criticos do pipeline eleitoral.
FGV EPGE -- Desafio de Estatistica e Econometria 2026.

Todas as funcoes de negocio sao IMPORTADAS de src/ ou scripts/.
Nenhuma logica de negocio e definida neste arquivo.
"""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
import pytest

from scripts.validar_entrega import validar_xlsx
from src.arredondamento import maiores_restos
from src.config import (
    CANDIDATOS_EDITAL,
    MANIFEST_PATH,
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
from src.pesquisas import agregar_institutos
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
    ws1.append(["Candidato(a)", "Partido", "Previsao de votos validos (%)"])
    # Distribui igualmente (maiores restos) para que soma seja exatamente 100,0%
    pcts = maiores_restos([100.0 / 12] * 12)
    for nome, pct in zip(CANDIDATOS_EDITAL, pcts):
        ws1.append([nome, PARTIDOS_EDITAL[nome], pct])
    ws1.append(["Total", "", 100.0])

    ws2 = wb.create_sheet("Adicionais")
    ws2.append(["Resultado", "Previsao (%)"])
    ws2.append(["Abstencao", 20.95])
    ws2.append(["Votos brancos", 2.5])
    ws2.append(["Votos nulos", 2.5])

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
        ws1.append(["Candidato(a)", "Partido", "Previsao (%)"])
        ws1.append(["Nome Errado", "Partido X", 100.0])
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Abstencao", 20.0])
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
        ws1.append(["Candidato(a)", "Partido", "Previsao (%)"])
        pcts = maiores_restos([100.0 / 12] * 12)
        for nome, pct in zip(CANDIDATOS_EDITAL, pcts):
            partido = PARTIDOS_EDITAL[nome] if nome != "Augusto Cury" else "PARTIDO_ERRADO"
            ws1.append([nome, partido, pct])
        ws1.append(["Total", "", 100.0])
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Resultado", "Previsao (%)"])
        ws2.append(["Abstencao", 21.0])
        ws2.append(["Votos brancos", 2.0])
        ws2.append(["Votos nulos", 2.0])
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
        ws1.append(["Candidato(a)", "Partido", "Previsao (%)"])
        pcts = maiores_restos([100.0 / 12] * 12)
        for nome, pct in zip(CANDIDATOS_EDITAL, pcts):
            ws1.append([nome, PARTIDOS_EDITAL[nome], pct])
        # Sem linha Total
        ws2 = wb.create_sheet("Adicionais")
        ws2.append(["Resultado", "Previsao (%)"])
        ws2.append(["Abstencao", 21.0])
        ws2.append(["Votos brancos", 2.0])
        ws2.append(["Votos nulos", 2.0])
        buf = io.BytesIO()
        wb.save(buf)
        p = tmp_path / "sem_total.xlsx"
        p.write_bytes(buf.getvalue())
        res = validar_xlsx(p)
        assert not res["valido"]
        assert any("Total" in e for e in res["erros"])


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
        Para cada celula numerica nao-NaN de pesquisas_2026.csv, o valor
        deve aparecer comprovadamente no texto do HTML bruto salvo correspondente.
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

        for idx, row in df.iterrows():
            url = row["fonte_url"]
            assert url in manifest_map, f"URL {url} nao encontrada no MANIFEST.csv"
            rel_file = manifest_map[url]
            html_path = RAW_DIR / rel_file
            assert html_path.exists(), f"Arquivo HTML {html_path} nao existe"

            with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
                text = BeautifulSoup(f.read(), "html.parser").get_text()

            colunas_numericas = (
                ["amostra"]
                + CANDIDATOS_EDITAL
                + ["outros_agregado", "brancos_nulos", "indecisos"]
            )
            for col in colunas_numericas:
                val = row[col]
                if pd.isna(val) or val == "":
                    continue
                num = float(val)
                num_int = int(num) if num.is_integer() else None

                if col == "amostra":
                    pats = [f"{num_int:,}".replace(",", "."), str(num_int)]
                elif num == 0.0:
                    pats = [
                        "0%", " 0 ", "(0)", "zero", "não pontuou", "não pontua",
                        "não pontuam", "0,0%"
                    ]
                elif num_int is not None:
                    pats = [
                        f"{num_int}%", f"{num_int} %", f"{num_int},0%",
                        f"{num_int}.0%", f"{num_int}"
                    ]
                else:
                    s_virg = f"{num:.1f}".replace(".", ",")
                    s_ponto = f"{num:.1f}"
                    pats = [
                        f"{s_virg}%", f"{s_virg} %", f"{s_ponto}%",
                        f"{s_ponto} %", s_virg, s_ponto
                    ]

                found = any(re.search(re.escape(p), text, re.IGNORECASE) for p in pats)
                assert found, (
                    f"Falha de transcricao na linha {idx} ({row['instituto']}): "
                    f"coluna '{col}'={val} nao encontrada no HTML {html_path} "
                    f"(padroes testados: {pats[:4]})"
                )
