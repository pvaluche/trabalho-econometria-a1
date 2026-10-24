"""
scripts/coletar_dados_2t.py
Extrai, padroniza e persiste todos os dados necessarios para o 2o Turno:
1. Pesquisas historicas de 2o turno (2006, 2010, 2014, 2018, 2022) -> data/processed/pesquisas_historicas_2t.parquet
2. Resultados oficiais TSE de 1o e 2o turno (2006-2022) nacional e por UF -> data/processed/tse_historico_2t.parquet e tse_uf_historico_2t.parquet
3. Resultado oficial TSE do 1o turno de 2026 (nacional, por UF e indicador de 2o turno para Governador) -> data/processed/tse_2026_1t_oficial.json
"""

from __future__ import annotations

import datetime
import hashlib
import json
import sys
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.coletar_pesquisas_historicas import (
    clean_cand_pct,
    limpar_numero,
    padronizar_instituto_e_contratante,
    parse_intervalo_datas,
)
from src.config import MANIFEST_PATH, PROCESSED_DIR, RAW_DIR, TSE_BASE_URL

JANELAS_2T = {
    2006: (date(2006, 10, 2), date(2006, 10, 28)),
    2010: (date(2010, 10, 4), date(2010, 10, 30)),
    2014: (date(2014, 10, 6), date(2014, 10, 25)),
    2018: (date(2018, 10, 8), date(2018, 10, 27)),
    2022: (date(2022, 10, 3), date(2022, 10, 29)),
}


def coletar_pesquisas_2t_2022() -> list[dict]:
    path = RAW_DIR / "pesquisas_historicas" / "wikipedia_pesquisas_2022.html"
    url = "https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2022"
    with open(path, encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    t = soup.find_all("table", {"class": "wikitable"})[15]
    pesquisas = []
    ini, vesp = JANELAS_2T[2022]

    for tr in t.find_all("tr")[2:]:
        tds = [td.get_text().strip().replace("\n", " ") for td in tr.find_all(["td", "th"])]
        if len(tds) < 6:
            continue
        inst_raw, datas_str, amostra_str = tds[0], tds[1], tds[2]
        try:
            dt1, dt2, dt_div = parse_intervalo_datas(datas_str, 2022)
        except ValueError:
            continue
        if not dt_div or dt_div < ini or dt_div > vesp:
            continue

        bols = clean_cand_pct(tds[3])
        lula = clean_cand_pct(tds[4])
        ind_abst = clean_cand_pct(tds[5])
        if bols is None or lula is None:
            continue

        inst, contr = padronizar_instituto_e_contratante(inst_raw)
        if inst == "Ipec":
            inst = "Ibope/Ipec"
        pesquisas.append(
            {
                "eleicao": 2022,
                "instituto": inst,
                "contratante": contr,
                "data_inicio_campo": dt1.isoformat() if dt1 else None,
                "data_fim_campo": dt2.isoformat() if dt2 else None,
                "data_divulgacao": dt_div.isoformat(),
                "amostra": limpar_numero(amostra_str),
                "cand_pt": "Luiz Inácio Lula da Silva",
                "cand_adv": "Jair Bolsonaro",
                "pct_pt_total": lula,
                "pct_adv_total": bols,
                "pct_pt_validos": lula / (lula + bols) * 100.0,
                "pct_adv_validos": bols / (lula + bols) * 100.0,
                "brancos_nulos_indecisos": ind_abst,
                "fonte_url": url,
            }
        )
    return pesquisas


def coletar_pesquisas_2t_2018() -> list[dict]:
    path = RAW_DIR / "pesquisas_historicas" / "wikipedia_pesquisas_2018.html"
    url = "https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018"
    with open(path, encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    t = soup.find_all("table", {"class": "wikitable"})[3]
    pesquisas = []
    ini, vesp = JANELAS_2T[2018]

    for tr in t.find_all("tr")[2:]:
        tds = [td.get_text().strip().replace("\n", " ") for td in tr.find_all(["td", "th"])]
        if len(tds) < 7:
            continue
        datas_str, inst_raw, amostra_str = tds[0], tds[1], tds[2]
        dt1, dt2, dt_div = parse_intervalo_datas(datas_str, 2018)
        if not dt_div or dt_div < ini or dt_div > vesp:
            continue

        haddad = clean_cand_pct(tds[4])
        bols = clean_cand_pct(tds[5])
        ind_abst = clean_cand_pct(tds[6])
        if haddad is None or bols is None:
            continue

        inst, contr = padronizar_instituto_e_contratante(inst_raw)
        if inst == "Ibope":
            inst = "Ibope/Ipec"
        pesquisas.append(
            {
                "eleicao": 2018,
                "instituto": inst,
                "contratante": contr,
                "data_inicio_campo": dt1.isoformat() if dt1 else None,
                "data_fim_campo": dt2.isoformat() if dt2 else None,
                "data_divulgacao": dt_div.isoformat(),
                "amostra": limpar_numero(amostra_str),
                "cand_pt": "Fernando Haddad",
                "cand_adv": "Jair Bolsonaro",
                "pct_pt_total": haddad,
                "pct_adv_total": bols,
                "pct_pt_validos": haddad / (haddad + bols) * 100.0,
                "pct_adv_validos": bols / (haddad + bols) * 100.0,
                "brancos_nulos_indecisos": ind_abst,
                "fonte_url": url,
            }
        )
    return pesquisas


def coletar_pesquisas_2t_2014() -> list[dict]:
    path = RAW_DIR / "pesquisas_historicas" / "wikipedia_pesquisas_2014.html"
    url = "https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2014"
    with open(path, encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    t = soup.find_all("table", {"class": "wikitable"})[1]
    pesquisas = []
    ini, vesp = JANELAS_2T[2014]

    amostras_padrao_2014 = {
        "Datafolha": 4300.0,
        "Ibope/Ipec": 3010.0,
        "Vox Populi": 2000.0,
        "CNT/MDA": 2002.0,
        "Ipespe": 2000.0,
    }

    for tr in t.find_all("tr")[2:]:
        tds = [td.get_text().strip().replace("\n", " ") for td in tr.find_all(["td", "th"])]
        if len(tds) < 8:
            continue
        datas_str, inst_raw = tds[1], tds[2]
        dt1, dt2, dt_div = parse_intervalo_datas(datas_str, 2014)
        if not dt_div or dt_div < ini or dt_div > vesp:
            continue

        dilma = clean_cand_pct(tds[4])
        aecio = clean_cand_pct(tds[5])
        bn = clean_cand_pct(tds[6])
        ind = clean_cand_pct(tds[7])
        if dilma is None or aecio is None:
            continue

        inst, contr = padronizar_instituto_e_contratante(inst_raw)
        if inst == "Ibope":
            inst = "Ibope/Ipec"
        pesquisas.append(
            {
                "eleicao": 2014,
                "instituto": inst,
                "contratante": contr,
                "data_inicio_campo": dt1.isoformat() if dt1 else None,
                "data_fim_campo": dt2.isoformat() if dt2 else None,
                "data_divulgacao": dt_div.isoformat(),
                "amostra": amostras_padrao_2014.get(inst, 2000.0),
                "cand_pt": "Dilma Rousseff",
                "cand_adv": "Aécio Neves",
                "pct_pt_total": dilma,
                "pct_adv_total": aecio,
                "pct_pt_validos": dilma / (dilma + aecio) * 100.0,
                "pct_adv_validos": aecio / (dilma + aecio) * 100.0,
                "brancos_nulos_indecisos": (bn or 0.0) + (ind or 0.0),
                "fonte_url": url,
            }
        )
    return pesquisas


def coletar_pesquisas_2t_2010_e_2006() -> list[dict]:
    """Pesquisas verificadas do 2o turno de 2006 e 2010 (Datafolha, Ibope, Vox Populi, CNT/Sensus)."""
    dados_brutos = [
        # 2006 2o Turno (Lula vs Alckmin)
        (
            2006,
            "Datafolha",
            "Folha/Globo",
            "2006-10-27",
            "2006-10-28",
            "2006-10-28",
            14722.0,
            "Luiz Inácio Lula da Silva",
            "Geraldo Alckmin",
            58.0,
            37.0,
            5.0,
        ),
        (
            2006,
            "Ibope/Ipec",
            "Globo",
            "2006-10-27",
            "2006-10-28",
            "2006-10-28",
            3010.0,
            "Luiz Inácio Lula da Silva",
            "Geraldo Alckmin",
            57.0,
            35.0,
            8.0,
        ),
        (
            2006,
            "CNT/Sensus",
            "CNT",
            "2006-10-23",
            "2006-10-25",
            "2006-10-26",
            2000.0,
            "Luiz Inácio Lula da Silva",
            "Geraldo Alckmin",
            57.5,
            33.5,
            9.0,
        ),
        (
            2006,
            "Datafolha",
            "Folha/Globo",
            "2006-10-23",
            "2006-10-24",
            "2006-10-24",
            7124.0,
            "Luiz Inácio Lula da Silva",
            "Geraldo Alckmin",
            57.0,
            38.0,
            5.0,
        ),
        (
            2006,
            "Ibope/Ipec",
            "Globo",
            "2006-10-21",
            "2006-10-23",
            "2006-10-24",
            3010.0,
            "Luiz Inácio Lula da Silva",
            "Geraldo Alckmin",
            57.0,
            36.0,
            7.0,
        ),
        (
            2006,
            "Vox Populi",
            "Band",
            "2006-10-17",
            "2006-10-18",
            "2006-10-19",
            2000.0,
            "Luiz Inácio Lula da Silva",
            "Geraldo Alckmin",
            57.0,
            37.0,
            6.0,
        ),
        # 2010 2o Turno (Dilma vs Serra)
        (
            2010,
            "Datafolha",
            "Folha/Globo",
            "2010-10-29",
            "2010-10-30",
            "2010-10-30",
            13096.0,
            "Dilma Rousseff",
            "José Serra",
            51.0,
            41.0,
            8.0,
        ),
        (
            2010,
            "Ibope/Ipec",
            "Globo/Estadão",
            "2010-10-29",
            "2010-10-30",
            "2010-10-30",
            3010.0,
            "Dilma Rousseff",
            "José Serra",
            52.0,
            40.0,
            8.0,
        ),
        (
            2010,
            "Vox Populi",
            "Band/iG",
            "2010-10-29",
            "2010-10-30",
            "2010-10-30",
            3000.0,
            "Dilma Rousseff",
            "José Serra",
            51.0,
            39.0,
            10.0,
        ),
        (
            2010,
            "CNT/Sensus",
            "CNT",
            "2010-10-28",
            "2010-10-29",
            "2010-10-30",
            2000.0,
            "Dilma Rousseff",
            "José Serra",
            50.3,
            37.6,
            12.1,
        ),
        (
            2010,
            "Datafolha",
            "Folha/Globo",
            "2010-10-27",
            "2010-10-27",
            "2010-10-28",
            4158.0,
            "Dilma Rousseff",
            "José Serra",
            49.0,
            38.0,
            13.0,
        ),
        (
            2010,
            "Ibope/Ipec",
            "Globo/Estadão",
            "2010-10-25",
            "2010-10-27",
            "2010-10-27",
            3010.0,
            "Dilma Rousseff",
            "José Serra",
            52.0,
            39.0,
            9.0,
        ),
        (
            2010,
            "CNT/Sensus",
            "CNT",
            "2010-10-23",
            "2010-10-25",
            "2010-10-26",
            2000.0,
            "Dilma Rousseff",
            "José Serra",
            51.9,
            36.7,
            11.4,
        ),
        (
            2010,
            "Datafolha",
            "Folha/Globo",
            "2010-10-21",
            "2010-10-21",
            "2010-10-22",
            4037.0,
            "Dilma Rousseff",
            "José Serra",
            50.0,
            40.0,
            10.0,
        ),
    ]
    pesquisas = []
    for ano, inst, contr, d1, d2, d_div, n, c_pt, c_adv, v_pt, v_adv, bni in dados_brutos:
        # Ajuste exato dos validos reportados em 2010 na vespera (Datafolha 55/45, Ibope 56/44, Vox 57/43, Sensus 57.2/42.8)
        if ano == 2010 and d_div == "2010-10-30":
            val_map = {
                "Datafolha": (55.0, 45.0),
                "Ibope/Ipec": (56.0, 44.0),
                "Vox Populi": (57.0, 43.0),
                "CNT/Sensus": (57.2, 42.8),
            }
            vp, va = val_map[inst]
        else:
            vp = v_pt / (v_pt + v_adv) * 100.0
            va = v_adv / (v_pt + v_adv) * 100.0

        pesquisas.append(
            {
                "eleicao": ano,
                "instituto": inst,
                "contratante": contr,
                "data_inicio_campo": d1,
                "data_fim_campo": d2,
                "data_divulgacao": d_div,
                "amostra": n,
                "cand_pt": c_pt,
                "cand_adv": c_adv,
                "pct_pt_total": v_pt,
                "pct_adv_total": v_adv,
                "pct_pt_validos": vp,
                "pct_adv_validos": va,
                "brancos_nulos_indecisos": bni,
                "fonte_url": f"https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_{ano}",
            }
        )
    return pesquisas


def processar_tse_historico_2t() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extrai dados nacionais e por UF de 1o e 2o turno (2006-2022) dos ZIPs locais do TSE."""
    rows_nac = []
    rows_uf = []

    for ano in [2006, 2010, 2014, 2018, 2022]:
        z_det_path = RAW_DIR / f"detalhe_votacao_munzona_{ano}.zip"
        z_vot_path = RAW_DIR / f"votacao_candidato_munzona_{ano}.zip"

        with zipfile.ZipFile(z_det_path) as zd:
            df_br_det = pd.read_csv(
                zd.open(f"detalhe_votacao_munzona_{ano}_BR.csv"),
                sep=";",
                encoding="latin-1",
                low_memory=False,
            )
            df_brasil_det = pd.read_csv(
                zd.open(f"detalhe_votacao_munzona_{ano}_BRASIL.csv"),
                sep=";",
                encoding="latin-1",
                low_memory=False,
            )

        with zipfile.ZipFile(z_vot_path) as zv:
            df_br_vot = pd.read_csv(
                zv.open(f"votacao_candidato_munzona_{ano}_BR.csv"),
                sep=";",
                encoding="latin-1",
                low_memory=False,
            )

        col_val = (
            "QT_TOTAL_VOTOS_VALIDOS"
            if "QT_TOTAL_VOTOS_VALIDOS" in df_br_det.columns
            else "QT_VOTOS_VALIDOS"
        )
        col_voto_cand = (
            "QT_VOTOS_NOMINAIS" if "QT_VOTOS_NOMINAIS" in df_br_vot.columns else "QT_VOTOS"
        )

        # Indicador de quais UFs tiveram 2o turno para Governador (CD_CARGO == 3 e NR_TURNO == 2)
        gov2_ufs = set(
            df_brasil_det[(df_brasil_det["CD_CARGO"] == 3) & (df_brasil_det["NR_TURNO"] == 2)][
                "SG_UF"
            ].unique()
        )

        # Nacional 1T e 2T
        res_turnos = {}
        for turno in [1, 2]:
            d_t = df_br_det[(df_br_det["CD_CARGO"] == 1) & (df_br_det["NR_TURNO"] == turno)]
            v_t = df_br_vot[(df_br_vot["CD_CARGO"] == 1) & (df_br_vot["NR_TURNO"] == turno)]

            aptos = int(d_t["QT_APTOS"].sum())
            comp = int(d_t["QT_COMPARECIMENTO"].sum())
            abst = int(d_t["QT_ABSTENCOES"].sum())
            brancos = int(d_t["QT_VOTOS_BRANCOS"].sum())
            nulos = int(d_t["QT_VOTOS_NULOS"].sum())
            validos = int(d_t[col_val].sum())

            votos_cand = v_t.groupby("NR_CANDIDATO")[col_voto_cand].sum().to_dict()
            total_val_cand = sum(votos_cand.values())
            pct_pt = votos_cand.get(13, 0) / total_val_cand * 100.0
            # Adversario no 2o turno e o outro candidato presente no 2o turno
            if turno == 2:
                nr_adv = [k for k in votos_cand.keys() if k != 13][0]
            res_turnos[turno] = {
                "aptos": aptos,
                "comparecimento": comp,
                "abstencao_pct": abst / aptos * 100.0,
                "brancos_pct": brancos / comp * 100.0,
                "nulos_pct": nulos / comp * 100.0,
                "validos": validos,
                "votos_cand": votos_cand,
                "total_val_cand": total_val_cand,
                "pct_pt": pct_pt,
            }

        nr_adv = [k for k in res_turnos[2]["votos_cand"].keys() if k != 13][0]
        pct_adv_1t = (
            res_turnos[1]["votos_cand"].get(nr_adv, 0) / res_turnos[1]["total_val_cand"] * 100.0
        )
        pct_adv_2t = (
            res_turnos[2]["votos_cand"].get(nr_adv, 0) / res_turnos[2]["total_val_cand"] * 100.0
        )

        # Estadual por UF (excluindo ZZ/VT)
        pres_uf = df_br_det[(df_br_det["CD_CARGO"] == 1) & (~df_br_det["SG_UF"].isin(["ZZ", "VT"]))]
        for uf, grp in pres_uf.groupby("SG_UF"):
            t1, t2 = grp[grp["NR_TURNO"] == 1], grp[grp["NR_TURNO"] == 2]
            if len(t1) and len(t2):
                a1 = t1["QT_ABSTENCOES"].sum() / t1["QT_APTOS"].sum() * 100.0
                a2 = t2["QT_ABSTENCOES"].sum() / t2["QT_APTOS"].sum() * 100.0
                b1 = t1["QT_VOTOS_BRANCOS"].sum() / t1["QT_COMPARECIMENTO"].sum() * 100.0
                b2 = t2["QT_VOTOS_BRANCOS"].sum() / t2["QT_COMPARECIMENTO"].sum() * 100.0
                n1 = t1["QT_VOTOS_NULOS"].sum() / t1["QT_COMPARECIMENTO"].sum() * 100.0
                n2 = t2["QT_VOTOS_NULOS"].sum() / t2["QT_COMPARECIMENTO"].sum() * 100.0
                rows_uf.append(
                    {
                        "eleicao": ano,
                        "uf": uf,
                        "gov2t": int(uf in gov2_ufs),
                        "aptos_1t": int(t1["QT_APTOS"].sum()),
                        "aptos_2t": int(t2["QT_APTOS"].sum()),
                        "abst_1t": a1,
                        "abst_2t": a2,
                        "delta_abst": a2 - a1,
                        "brancos_1t": b1,
                        "brancos_2t": b2,
                        "nulos_1t": n1,
                        "nulos_2t": n2,
                    }
                )

        df_uf_ano = pd.DataFrame([r for r in rows_uf if r["eleicao"] == ano])
        share_gov2t = (
            df_uf_ano[df_uf_ano["gov2t"] == 1]["aptos_2t"].sum()
            / df_uf_ano["aptos_2t"].sum()
            * 100.0
        )

        rows_nac.append(
            {
                "eleicao": ano,
                "nr_adv": int(nr_adv),
                "pct_pt_1t": res_turnos[1]["pct_pt"],
                "pct_adv_1t": pct_adv_1t,
                "pct_terceiros_1t": 100.0 - res_turnos[1]["pct_pt"] - pct_adv_1t,
                "pct_pt_2t": res_turnos[2]["pct_pt"],
                "pct_adv_2t": pct_adv_2t,
                "abstencao_1t": res_turnos[1]["abstencao_pct"],
                "abstencao_2t": res_turnos[2]["abstencao_pct"],
                "delta_abstencao": res_turnos[2]["abstencao_pct"] - res_turnos[1]["abstencao_pct"],
                "brancos_1t": res_turnos[1]["brancos_pct"],
                "brancos_2t": res_turnos[2]["brancos_pct"],
                "delta_brancos": res_turnos[2]["brancos_pct"] - res_turnos[1]["brancos_pct"],
                "ratio_brancos": res_turnos[2]["brancos_pct"] / res_turnos[1]["brancos_pct"],
                "nulos_1t": res_turnos[1]["nulos_pct"],
                "nulos_2t": res_turnos[2]["nulos_pct"],
                "delta_nulos": res_turnos[2]["nulos_pct"] - res_turnos[1]["nulos_pct"],
                "ratio_nulos": res_turnos[2]["nulos_pct"] / res_turnos[1]["nulos_pct"],
                "share_eleitorado_gov2t": share_gov2t,
            }
        )

    return pd.DataFrame(rows_nac), pd.DataFrame(rows_uf)


def baixar_e_extrair_tse_2026_1t() -> dict:
    """Baixa/usa cache dos arquivos de 2026 do TSE e extrai todos os resultados oficiais do 1o turno."""
    url_vot = f"{TSE_BASE_URL}/votacao_candidato_munzona/votacao_candidato_munzona_2026.zip"
    url_det = f"{TSE_BASE_URL}/detalhe_votacao_munzona/detalhe_votacao_munzona_2026.zip"

    path_vot = RAW_DIR / "votacao_candidato_munzona_2026.zip"
    path_det = RAW_DIR / "detalhe_votacao_munzona_2026.zip"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for url, p in [(url_vot, path_vot), (url_det, path_det)]:
        if not p.exists():
            print(f"Baixando {url} ...")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as resp:
                conteudo = resp.read()
            p.write_bytes(conteudo)
            sha = hashlib.sha256(conteudo).hexdigest()
            agora = datetime.datetime.now(datetime.UTC).isoformat()
            with open(MANIFEST_PATH, "a", encoding="utf-8") as mf:
                mf.write(f"{p.name},{url},{agora},{len(conteudo)},{sha}\n")
            print(f"Salvo: {p.name} ({len(conteudo)} bytes)")

    with zipfile.ZipFile(path_det) as zd:
        df_det_br = pd.read_csv(
            zd.open("detalhe_votacao_munzona_2026_BR.csv"),
            sep=";",
            encoding="latin-1",
            low_memory=False,
        )
        # Verifica tambem Governador (CD_CARGO == 3) em todas as UFs para saber quais UFs tem 2o turno estadual
        ufs_gov2t = []
        ufs_sem_gov2t = []

    with zipfile.ZipFile(path_vot) as zv:
        df_vot_br = pd.read_csv(
            zv.open("votacao_candidato_munzona_2026_BR.csv"),
            sep=";",
            encoding="latin-1",
            low_memory=False,
        )
        # Checa Governador (CD_CARGO == 3) por UF nos arquivos estaduais
        for name in sorted(zv.namelist()):
            if (
                name.endswith(".csv")
                and not name.endswith("_BR.csv")
                and not name.endswith("_BRASIL.csv")
                and not name.endswith("_ZZ.csv")
                and not name.endswith("_VT.csv")
            ):
                uf = name.split("_")[-1].split(".")[0]
                df_uf_v = pd.read_csv(zv.open(name), sep=";", encoding="latin-1", low_memory=False)
                gov = df_uf_v[(df_uf_v["CD_CARGO"] == 3) & (df_uf_v["NR_TURNO"] == 1)]
                if not gov.empty:
                    col_v = (
                        "QT_VOTOS_NOMINAIS_VALIDOS"
                        if "QT_VOTOS_NOMINAIS_VALIDOS" in gov.columns
                        else "QT_VOTOS_NOMINAIS"
                    )
                    v_por_cand = gov.groupby("NR_CANDIDATO")[col_v].sum()
                    tot_gov = v_por_cand.sum()
                    max_share = (v_por_cand.max() / tot_gov * 100.0) if tot_gov > 0 else 100.0
                    # No DF/estados, se max_share <= 50.0%, ha 2o turno para Governador
                    if max_share < 50.0:
                        ufs_gov2t.append(uf)
                    else:
                        ufs_sem_gov2t.append(uf)

    d1 = df_det_br[(df_det_br["CD_CARGO"] == 1) & (df_det_br["NR_TURNO"] == 1)]
    col_val = (
        "QT_TOTAL_VOTOS_VALIDOS" if "QT_TOTAL_VOTOS_VALIDOS" in d1.columns else "QT_VOTOS_VALIDOS"
    )
    aptos = int(d1["QT_APTOS"].sum())
    comp = int(d1["QT_COMPARECIMENTO"].sum())
    abst = int(d1["QT_ABSTENCOES"].sum())
    brancos = int(d1["QT_VOTOS_BRANCOS"].sum())
    nulos = int(d1["QT_VOTOS_NULOS"].sum())
    validos = int(d1[col_val].sum())

    v1 = df_vot_br[(df_vot_br["CD_CARGO"] == 1) & (df_vot_br["NR_TURNO"] == 1)]
    col_v_cand = (
        "QT_VOTOS_NOMINAIS_VALIDOS"
        if "QT_VOTOS_NOMINAIS_VALIDOS" in v1.columns
        else "QT_VOTOS_NOMINAIS"
    )
    v_por_nome = (
        v1.groupby(["NR_CANDIDATO", "NM_URNA_CANDIDATO", "SG_PARTIDO"])[col_v_cand]
        .sum()
        .reset_index()
    )
    v_por_nome = v_por_nome.sort_values(col_v_cand, ascending=False)

    mapa_nomes_edital = {
        22: "Flávio Bolsonaro",
        13: "Luiz Inácio Lula da Silva",
        70: "Augusto Cury",
        14: "Renan Santos",
        55: "Ronaldo Caiado",
        30: "Romeu Zema",
        80: "Samara Martins",
        16: "Hertz Dias",
        27: "Clariana Barão",
        21: "Edmilson Costa",
        35: "Wilson Grassi",
        29: "Rui Costa Pimenta",
    }

    candidatos_1t = {}
    for _, row in v_por_nome.iterrows():
        nr = int(row["NR_CANDIDATO"])
        nome = mapa_nomes_edital.get(nr, str(row["NM_URNA_CANDIDATO"]))
        votos = int(row[col_v_cand])
        candidatos_1t[nome] = {
            "numero": nr,
            "partido": str(row["SG_PARTIDO"]),
            "votos": votos,
            "pct_validos": votos / validos * 100.0,
        }

    # Abstencao por UF no 1o turno de 2026
    uf_stats = {}
    for uf, grp in d1[~d1["SG_UF"].isin(["ZZ", "VT"])].groupby("SG_UF"):
        ap_u = int(grp["QT_APTOS"].sum())
        ab_u = int(grp["QT_ABSTENCOES"].sum())
        uf_stats[str(uf)] = {
            "aptos": ap_u,
            "abstencoes": ab_u,
            "abstencao_1t_pct": ab_u / ap_u * 100.0 if ap_u > 0 else 0.0,
            "gov2t": int(str(uf) in ufs_gov2t),
        }

    aptos_br_internos = sum(v["aptos"] for v in uf_stats.values())
    aptos_gov2t = sum(v["aptos"] for v in uf_stats.values() if v["gov2t"] == 1)

    res_2026 = {
        "eleicao": 2026,
        "turno": 1,
        "data_eleicao": "2026-10-04",
        "aptos": aptos,
        "comparecimento": comp,
        "abstencoes": abst,
        "votos_validos": validos,
        "votos_brancos": brancos,
        "votos_nulos": nulos,
        "abstencao_pct": abst / aptos * 100.0,
        "brancos_pct": brancos / comp * 100.0,
        "nulos_pct": nulos / comp * 100.0,
        "candidatos": candidatos_1t,
        "ufs_com_gov2t": ufs_gov2t,
        "ufs_sem_gov2t": ufs_sem_gov2t,
        "share_eleitorado_gov2t_pct": aptos_gov2t / aptos_br_internos * 100.0
        if aptos_br_internos > 0
        else 0.0,
        "uf_stats": uf_stats,
    }
    return res_2026


if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("1. Coletando pesquisas historicas de 2o turno (2006-2022)...")
    p_2t = (
        coletar_pesquisas_2t_2010_e_2006()
        + coletar_pesquisas_2t_2014()
        + coletar_pesquisas_2t_2018()
        + coletar_pesquisas_2t_2022()
    )
    df_p2t = pd.DataFrame(p_2t)
    out_p2t = PROCESSED_DIR / "pesquisas_historicas_2t.parquet"
    df_p2t.to_parquet(out_p2t, index=False)
    print(f"   Salvo {out_p2t} com {len(df_p2t)} pesquisas de 2o turno.")
    print(df_p2t.groupby(["eleicao", "instituto"]).size().unstack(fill_value=0))

    print("\n2. Processando resultados historicos TSE (1T e 2T, 2006-2022)...")
    df_nac_2t, df_uf_2t = processar_tse_historico_2t()
    df_nac_2t.to_parquet(PROCESSED_DIR / "tse_historico_2t.parquet", index=False)
    df_uf_2t.to_parquet(PROCESSED_DIR / "tse_uf_historico_2t.parquet", index=False)
    print("   Resumo Nacional 1T vs 2T (2006-2022):")
    print(df_nac_2t.round(2).to_string(index=False))

    print("\n3. Extraindo resultados oficiais do 1o turno de 2026 do TSE...")
    res_2026_1t = baixar_e_extrair_tse_2026_1t()
    out_json_2026 = PROCESSED_DIR / "tse_2026_1t_oficial.json"
    with open(out_json_2026, "w", encoding="utf-8") as f:
        json.dump(res_2026_1t, f, ensure_ascii=False, indent=2)
    print(f"   Salvo {out_json_2026}")
    print(
        f"   UFs com 2o turno para Governador em 2026 ({len(res_2026_1t['ufs_com_gov2t'])}): {res_2026_1t['ufs_com_gov2t']}"
    )
    print(
        f"   Share do eleitorado nacional com 2o turno para Governador em 2026: {res_2026_1t['share_eleitorado_gov2t_pct']:.2f}%"
    )
