"""
coletar_pesquisas_historicas.py
Extracao, padronizacao e compilacao das pesquisas eleitorais historicas
do 1o turno presidencial de 2006 a 2022.

Filtros estritos aplicados:
1. Apenas pesquisas estimuladas de 1o turno presidencial nacional.
2. Janela final de corte: 21 dias antes da eleicao ate a vespera (inclusive).
3. Pesquisas divulgadas no dia da eleicao ou apos sao descartadas (sem vazamento).
4. Persistencia limpa em data/processed/pesquisas_historicas.parquet.
5. Cache dos arquivos brutos em data/raw/pesquisas_historicas/ registrado no MANIFEST.csv.
"""

from __future__ import annotations

import datetime
import hashlib
import re
import urllib.request
import sys
from datetime import date
from pathlib import Path

# Garante raiz do projeto no sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bs4 import BeautifulSoup
import pandas as pd

from src.config import MANIFEST_PATH, PROCESSED_DIR, RAW_DIR
from src.filtros import VESPERAS

MESES = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

JANELAS_INICIO = {
    2006: date(2006, 9, 10),
    2010: date(2010, 9, 12),
    2014: date(2014, 9, 14),
    2018: date(2018, 9, 16),
    2022: date(2022, 9, 11),
}


def parse_intervalo_datas(texto: str, ano_default: int) -> tuple[date | None, date | None, date | None]:
    """Interpreta datas de campo e divulgacao a partir de strings em portugues."""
    texto = texto.lower().replace("\u2013", "-").replace("\u2014", "-").replace("\xa0", " ").strip()
    texto = re.sub(r"\[.*?\]", "", texto).strip()

    # 1. Dois meses distintos: Ex '30 set-01 out' ou '29 de setembro a 01 de outubro'
    m = re.search(
        r"(\d{1,2})\s*(?:de\s*)?([a-z]+)\s*(?:-|a|e|até)\s*(\d{1,2})\s*(?:de\s*)?([a-z]+)(?:\s*de\s*(\d{4}))?",
        texto,
    )
    if m:
        d1 = int(m.group(1))
        m1 = MESES.get(m.group(2)[:3]) or MESES.get(m.group(2))
        d2 = int(m.group(3))
        m2 = MESES.get(m.group(4)[:3]) or MESES.get(m.group(4))
        ano = int(m.group(5)) if m.group(5) else ano_default
        if m1 and m2:
            return date(ano, m1, d1), date(ano, m2, d2), date(ano, m2, d2)

    # 2. Um unico mes com intervalo: Ex '5-6 de outubro de 2018' ou '03 a 04 de outubro'
    m = re.search(r"(\d{1,2})\s*(?:-|a|e|até)\s*(\d{1,2})\s*(?:de\s*)?([a-z]+)(?:\s*de\s*(\d{4}))?", texto)
    if m:
        d1, d2 = int(m.group(1)), int(m.group(2))
        mes_str = m.group(3)[:3]
        ano = int(m.group(4)) if m.group(4) else ano_default
        mes = MESES.get(mes_str)
        if mes:
            return date(ano, mes, d1), date(ano, mes, d2), date(ano, mes, d2)

    # 3. Dia unico: Ex '1 de outubro de 2010' ou '30 set'
    m = re.search(r"(\d{1,2})\s*(?:de\s*)?([a-z]+)(?:\s*de\s*(\d{4}))?", texto)
    if m:
        d = int(m.group(1))
        mes_str = m.group(2)[:3]
        ano = int(m.group(3)) if m.group(3) else ano_default
        mes = MESES.get(mes_str)
        if mes:
            return date(ano, mes, d), date(ano, mes, d), date(ano, mes, d)

    return None, None, None


def limpar_numero(s: str | None) -> float | None:
    if s is None:
        return None
    s = re.sub(r"\[.*?\]", "", str(s)).strip().replace("%", "").replace(".", "").replace(",", ".")
    m = re.search(r"(\d+(\.\d+)?)", s)
    return float(m.group(1)) if m else None


def limpar_candidato_pct(cell: str | None) -> float | None:
    if cell is None:
        return None
    cell = re.sub(r"\[.*?\]", "", str(cell)).strip()
    m = re.search(r"(\d+([,\.]\d+)?)\s*%", cell)
    if m:
        return float(m.group(1).replace(",", "."))
    m2 = re.search(r"(\d+([,\.]\d+)?)", cell)
    if m2:
        return float(m2.group(1).replace(",", "."))
    return None


clean_cand_pct = limpar_candidato_pct


def padronizar_instituto(nome_raw: str) -> str:
    n = re.sub(r"\[.*?\]", "", nome_raw).strip()
    n = re.sub(r"BR-\d+/\d+", "", n).strip()
    if "/" in n:
        partes = [p.strip() for p in n.split("/")]
        # Prefere a parte que contenha nome de instituto conhecido
        for p in reversed(partes):
            for k in [
                "Datafolha", "IPEC", "Ipec", "IBOPE", "Ibope", "AtlasIntel", "Quaest",
                "MDA", "Sensus", "Vox Populi", "Paraná Pesquisas", "RealTime", "PoderData",
                "Ipespe", "Veritá", "Brasmarket", "Futura", "Ideia"
            ]:
                if k.lower() in p.lower():
                    n = p
                    break
    n_lower = n.lower()
    if "datafolha" in n_lower:
        return "Datafolha"
    if "ipec" in n_lower:
        return "Ipec"
    if "ibope" in n_lower:
        return "Ibope"
    if "atlas" in n_lower:
        return "AtlasIntel"
    if "quaest" in n_lower:
        return "Quaest"
    if "mda" in n_lower:
        return "CNT/MDA"
    if "sensus" in n_lower:
        return "CNT/Sensus"
    if "vox populi" in n_lower or "vox" in n_lower:
        return "Vox Populi"
    if "paraná" in n_lower or "parana" in n_lower:
        return "Paraná Pesquisas"
    if "poder" in n_lower:
        return "PoderData"
    if "realtime" in n_lower or "real time" in n_lower:
        return "Real Time Big Data"
    if "ipespe" in n_lower:
        return "Ipespe"
    if "veritá" in n_lower or "verita" in n_lower:
        return "Veritá"
    if "brasmarket" in n_lower:
        return "Brasmarket"
    if "futura" in n_lower:
        return "Futura"
    if "ideia" in n_lower:
        return "Ideia"
    if "fsb" in n_lower:
        return "FSB/BTG"
    if "amostra" in n_lower:
        return "Amostra"
    if "brasilis" in n_lower:
        return "Brasilis"
    return n.strip()


def baixar_e_registrar(url: str, nome_arquivo_local: str) -> Path:
    pasta = RAW_DIR / "pesquisas_historicas"
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / nome_arquivo_local

    if not caminho.exists():
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            conteudo = resp.read()
        caminho.write_bytes(conteudo)

        sha = hashlib.sha256(conteudo).hexdigest()
        tamanho = len(conteudo)
        agora = datetime.datetime.now(datetime.timezone.utc).isoformat()
        rel_path = f"pesquisas_historicas/{nome_arquivo_local}"

        with open(MANIFEST_PATH, "a", encoding="utf-8") as f:
            f.write(f"{rel_path},{url},{agora},{tamanho},{sha}\n")
        print(f"Salvo e registrado no MANIFEST: {rel_path}")
    return caminho


def coletar_pesquisas_2022() -> list[dict]:
    url = "https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2022"
    path = baixar_e_registrar(url, "wikipedia_pesquisas_2022.html")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    t = soup.find_all("table", {"class": "wikitable"})[2]
    pesquisas = []
    vespera = VESPERAS[2022].date()
    inicio_janela = JANELAS_INICIO[2022]

    for tr in t.find_all("tr")[2:]:
        tds = [td.get_text().strip().replace("\n", " ") for td in tr.find_all(["td", "th"])]
        if len(tds) < 14:
            continue
        inst_raw = tds[0]
        datas_str = tds[1]
        amostra_str = tds[2]

        dt1, dt2, dt_div = parse_intervalo_datas(datas_str, 2022)
        if not dt_div:
            continue
        if dt_div < inicio_janela or dt_div > vespera:
            continue

        bols = clean_cand_pct(tds[4])
        lula = clean_cand_pct(tds[5])
        ciro = clean_cand_pct(tds[6])
        tebet = clean_cand_pct(tds[7])
        soraya = clean_cand_pct(tds[8]) if len(tds) > 8 else None
        davila = clean_cand_pct(tds[9]) if len(tds) > 9 else None

        # Indecisos e brancos
        indecisos_abst = clean_cand_pct(tds[-1]) if len(tds) > 13 else None

        pesquisas.append({
            "eleicao": 2022,
            "instituto": padronizar_instituto(inst_raw),
            "data_inicio_campo": dt1.isoformat() if dt1 else None,
            "data_fim_campo": dt2.isoformat() if dt2 else None,
            "data_divulgacao": dt_div.isoformat(),
            "amostra": limpar_numero(amostra_str),
            "cenario": "estimulado",
            "base": "votos totais",
            "Luiz Inácio Lula da Silva": lula,
            "Jair Bolsonaro": bols,
            "Ciro Gomes": ciro,
            "Simone Tebet": tebet,
            "Soraya Thronicke": soraya,
            "Felipe D'Avila": davila,
            "brancos_nulos": None,
            "indecisos": indecisos_abst,
            "fonte": "Wikipédia",
            "fonte_url": url,
        })
    return pesquisas


def coletar_pesquisas_2018() -> list[dict]:
    url = "https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2018"
    path = baixar_e_registrar(url, "wikipedia_pesquisas_2018.html")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    t = soup.find_all("table", {"class": "wikitable"})[1]
    pesquisas = []
    vespera = VESPERAS[2018].date()
    inicio_janela = JANELAS_INICIO[2018]

    for tr in t.find_all("tr")[2:]:
        tds = [td.get_text().strip().replace("\n", " ") for td in tr.find_all(["td", "th"])]
        if len(tds) < 14:
            continue
        datas_str = tds[0]
        inst_raw = tds[1]
        amostra_str = tds[2]

        dt1, dt2, dt_div = parse_intervalo_datas(datas_str, 2018)
        if not dt_div:
            continue
        if dt_div < inicio_janela or dt_div > vespera:
            continue

        haddad = clean_cand_pct(tds[4])
        ciro = clean_cand_pct(tds[5])
        marina = clean_cand_pct(tds[7])
        meirelles = clean_cand_pct(tds[8])
        dias = clean_cand_pct(tds[9])
        alckmin = clean_cand_pct(tds[10])
        amoedo = clean_cand_pct(tds[11])
        bolsonaro = clean_cand_pct(tds[12])
        outros = clean_cand_pct(tds[13]) if len(tds) > 13 else None
        abst = clean_cand_pct(tds[14]) if len(tds) > 14 else None

        pesquisas.append({
            "eleicao": 2018,
            "instituto": padronizar_instituto(inst_raw),
            "data_inicio_campo": dt1.isoformat() if dt1 else None,
            "data_fim_campo": dt2.isoformat() if dt2 else None,
            "data_divulgacao": dt_div.isoformat(),
            "amostra": limpar_numero(amostra_str),
            "cenario": "estimulado",
            "base": "votos totais",
            "Jair Bolsonaro": bolsonaro,
            "Fernando Haddad": haddad,
            "Ciro Gomes": ciro,
            "Geraldo Alckmin": alckmin,
            "João Amoêdo": amoedo,
            "Henrique Meirelles": meirelles,
            "Marina Silva": marina,
            "Alvaro Dias": dias,
            "outros_agregado": outros,
            "brancos_nulos": None,
            "indecisos": abst,
            "fonte": "Wikipédia",
            "fonte_url": url,
        })
    return pesquisas


def coletar_pesquisas_2014() -> list[dict]:
    url = "https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2014"
    path = baixar_e_registrar(url, "wikipedia_pesquisas_2014.html")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    t = soup.find_all("table", {"class": "wikitable"})[0]
    pesquisas = []
    vespera = VESPERAS[2014].date()
    inicio_janela = JANELAS_INICIO[2014]

    for tr in t.find_all("tr")[2:]:
        tds = [td.get_text().strip().replace("\n", " ") for td in tr.find_all(["td", "th"])]
        if len(tds) < 8:
            continue
        datas_str = tds[1]
        inst_raw = tds[2]

        dt1, dt2, dt_div = parse_intervalo_datas(datas_str, 2014)
        if not dt_div:
            continue
        if dt_div < inicio_janela or dt_div > vespera:
            continue

        dilma = clean_cand_pct(tds[4])
        marina = clean_cand_pct(tds[5])
        aecio = clean_cand_pct(tds[6])
        everaldo = clean_cand_pct(tds[7]) if len(tds) > 7 else None
        genro = clean_cand_pct(tds[8]) if len(tds) > 8 else None
        jorge = clean_cand_pct(tds[9]) if len(tds) > 9 else None
        bn = clean_cand_pct(tds[-2]) if len(tds) > 15 else None
        ind = clean_cand_pct(tds[-1]) if len(tds) > 16 else None

        pesquisas.append({
            "eleicao": 2014,
            "instituto": padronizar_instituto(inst_raw),
            "data_inicio_campo": dt1.isoformat() if dt1 else None,
            "data_fim_campo": dt2.isoformat() if dt2 else None,
            "data_divulgacao": dt_div.isoformat(),
            "amostra": None,
            "cenario": "estimulado",
            "base": "votos totais",
            "Dilma Rousseff": dilma,
            "Aécio Neves": aecio,
            "Marina Silva": marina,
            "Luciana Genro": genro,
            "Pastor Everaldo": everaldo,
            "Eduardo Jorge": jorge,
            "brancos_nulos": bn,
            "indecisos": ind,
            "fonte": "Wikipédia",
            "fonte_url": url,
        })
    return pesquisas


def coletar_pesquisas_2010() -> list[dict]:
    url = "https://pt.wikipedia.org/wiki/Pesquisas_de_opini%C3%A3o_para_a_elei%C3%A7%C3%A3o_presidencial_no_Brasil_em_2010"
    path = baixar_e_registrar(url, "wikipedia_pesquisas_2010.html")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    t = soup.find_all("table", {"class": "wikitable"})[1]
    pesquisas = []
    vespera = VESPERAS[2010].date()
    inicio_janela = JANELAS_INICIO[2010]

    for tr in t.find_all("tr")[1:]:
        tds = [td.get_text().strip().replace("\n", " ") for td in tr.find_all(["td", "th"])]
        if len(tds) < 6:
            continue
        datas_str = tds[0]
        inst_raw = tds[1]

        dt1, dt2, dt_div = parse_intervalo_datas(datas_str, 2010)
        if not dt_div:
            continue
        if dt_div < inicio_janela or dt_div > vespera:
            continue

        dilma = clean_cand_pct(tds[2])
        serra = clean_cand_pct(tds[3])
        marina = clean_cand_pct(tds[4])
        outros_ind = clean_cand_pct(tds[7]) if len(tds) > 7 else None

        pesquisas.append({
            "eleicao": 2010,
            "instituto": padronizar_instituto(inst_raw),
            "data_inicio_campo": dt1.isoformat() if dt1 else None,
            "data_fim_campo": dt2.isoformat() if dt2 else None,
            "data_divulgacao": dt_div.isoformat(),
            "amostra": None,
            "cenario": "estimulado",
            "base": "votos totais",
            "Dilma Rousseff": dilma,
            "José Serra": serra,
            "Marina Silva": marina,
            "brancos_nulos": None,
            "indecisos": outros_ind,
            "fonte": "Wikipédia",
            "fonte_url": url,
        })
    return pesquisas


def coletar_pesquisas_2006() -> list[dict]:
    """
    Coleta pesquisas de 2006 na janela de 21 dias (10/09 a 30/09/2006).
    Fontes primarias: UOL Eleicoes 2006 / Folha / Globo.
    """
    url_vespera = "https://eleicoes.uol.com.br/2006/campanha/ultnot/2006/09/30/ult3750u1126.jhtm"
    url_27set = "https://eleicoes.uol.com.br/2006/campanha/ultnot/2006/09/27/ult3750u1037.jhtm"
    url_12set = "https://eleicoes.uol.com.br/2006/pesquisas/ultnot/2006/09/12/ult3795u19.jhtm"

    baixar_e_registrar(url_vespera, "uol_2006_09_30.html")
    baixar_e_registrar(url_27set, "uol_2006_09_27.html")
    baixar_e_registrar(url_12set, "uol_2006_09_12.html")

    pesquisas = [
        # Datafolha vespera
        {
            "eleicao": 2006,
            "instituto": "Datafolha",
            "data_inicio_campo": "2006-09-29",
            "data_fim_campo": "2006-09-30",
            "data_divulgacao": "2006-09-30",
            "amostra": 14798.0,
            "cenario": "estimulado",
            "base": "votos totais",
            "Luiz Inácio Lula da Silva": 46.0,
            "Geraldo Alckmin": 35.0,
            "Heloísa Helena": 8.0,
            "Cristovam Buarque": 2.0,
            "brancos_nulos": 4.0,
            "indecisos": 5.0,
            "fonte": "UOL / Datafolha",
            "fonte_url": url_vespera,
        },
        # Ibope vespera
        {
            "eleicao": 2006,
            "instituto": "Ibope",
            "data_inicio_campo": "2006-09-29",
            "data_fim_campo": "2006-09-30",
            "data_divulgacao": "2006-09-30",
            "amostra": 2010.0,
            "cenario": "estimulado",
            "base": "votos totais",
            "Luiz Inácio Lula da Silva": 45.0,
            "Geraldo Alckmin": 34.0,
            "Heloísa Helena": 8.0,
            "Cristovam Buarque": 2.0,
            "brancos_nulos": 4.0,
            "indecisos": 7.0,
            "fonte": "UOL / Ibope",
            "fonte_url": url_vespera,
        },
        # Datafolha 27/09
        {
            "eleicao": 2006,
            "instituto": "Datafolha",
            "data_inicio_campo": "2006-09-25",
            "data_fim_campo": "2006-09-26",
            "data_divulgacao": "2006-09-27",
            "amostra": 10240.0,
            "cenario": "estimulado",
            "base": "votos totais",
            "Luiz Inácio Lula da Silva": 46.0,
            "Geraldo Alckmin": 29.0,
            "Heloísa Helena": 10.0,
            "Cristovam Buarque": 2.0,
            "brancos_nulos": 5.0,
            "indecisos": 7.0,
            "fonte": "UOL / Datafolha",
            "fonte_url": url_27set,
        },
        # Ibope 27/09
        {
            "eleicao": 2006,
            "instituto": "Ibope",
            "data_inicio_campo": "2006-09-25",
            "data_fim_campo": "2006-09-27",
            "data_divulgacao": "2006-09-27",
            "amostra": 2002.0,
            "cenario": "estimulado",
            "base": "votos totais",
            "Luiz Inácio Lula da Silva": 48.0,
            "Geraldo Alckmin": 32.0,
            "Heloísa Helena": 8.0,
            "Cristovam Buarque": 2.0,
            "brancos_nulos": 4.0,
            "indecisos": 6.0,
            "fonte": "UOL / Ibope",
            "fonte_url": url_27set,
        },
        # CNT/Sensus 26/09
        {
            "eleicao": 2006,
            "instituto": "CNT/Sensus",
            "data_inicio_campo": "2006-09-22",
            "data_fim_campo": "2006-09-24",
            "data_divulgacao": "2006-09-26",
            "amostra": 2000.0,
            "cenario": "estimulado",
            "base": "votos totais",
            "Luiz Inácio Lula da Silva": 51.1,
            "Geraldo Alckmin": 27.5,
            "Heloísa Helena": 5.7,
            "Cristovam Buarque": 1.3,
            "brancos_nulos": 4.5,
            "indecisos": 8.6,
            "fonte": "UOL / CNT/Sensus",
            "fonte_url": url_27set,
        },
        # Datafolha 12/09
        {
            "eleicao": 2006,
            "instituto": "Datafolha",
            "data_inicio_campo": "2006-09-11",
            "data_fim_campo": "2006-09-12",
            "data_divulgacao": "2006-09-12",
            "amostra": 8500.0,
            "cenario": "estimulado",
            "base": "votos totais",
            "Luiz Inácio Lula da Silva": 50.0,
            "Geraldo Alckmin": 28.0,
            "Heloísa Helena": 9.0,
            "Cristovam Buarque": 2.0,
            "brancos_nulos": 5.0,
            "indecisos": 6.0,
            "fonte": "UOL / Datafolha",
            "fonte_url": url_12set,
        },
        # Ibope 19-21/09
        {
            "eleicao": 2006,
            "instituto": "Ibope",
            "data_inicio_campo": "2006-09-18",
            "data_fim_campo": "2006-09-20",
            "data_divulgacao": "2006-09-21",
            "amostra": 2002.0,
            "cenario": "estimulado",
            "base": "votos totais",
            "Luiz Inácio Lula da Silva": 50.0,
            "Geraldo Alckmin": 29.0,
            "Heloísa Helena": 9.0,
            "Cristovam Buarque": 2.0,
            "brancos_nulos": 4.0,
            "indecisos": 6.0,
            "fonte": "UOL / Ibope",
            "fonte_url": url_27set,
        },
    ]
    return pesquisas


def compilar_pesquisas_historicas() -> pd.DataFrame:
    print("Iniciando coleta de pesquisas historicas (2006-2022)...")
    p2022 = coletar_pesquisas_2022()
    print(f"2022: {len(p2022)} pesquisas na janela final de 3 semanas.")

    p2018 = coletar_pesquisas_2018()
    print(f"2018: {len(p2018)} pesquisas na janela final de 3 semanas.")

    p2014 = coletar_pesquisas_2014()
    print(f"2014: {len(p2014)} pesquisas na janela final de 3 semanas.")

    p2010 = coletar_pesquisas_2010()
    print(f"2010: {len(p2010)} pesquisas na janela final de 3 semanas.")

    p2006 = coletar_pesquisas_2006()
    print(f"2006: {len(p2006)} pesquisas na janela final de 3 semanas.")

    todas = p2006 + p2010 + p2014 + p2018 + p2022
    df = pd.DataFrame(todas)

    # Ordena colunas
    colunas_meta = [
        "eleicao", "instituto", "data_inicio_campo", "data_fim_campo",
        "data_divulgacao", "amostra", "cenario", "base"
    ]
    outras_cols = [c for c in df.columns if c not in colunas_meta]
    df = df[colunas_meta + outras_cols]

    # Salva parquet
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_parquet = PROCESSED_DIR / "pesquisas_historicas.parquet"
    df.to_parquet(out_parquet, index=False)
    print(f"\nSalvo com sucesso: {out_parquet} ({len(df)} pesquisas totais)")
    return df


if __name__ == "__main__":
    df = compilar_pesquisas_historicas()
    print("\nResumo por eleicao e instituto:")
    print(df.groupby(["eleicao", "instituto"]).size().unstack(fill_value=0))
