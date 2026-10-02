"""
config.py
Parametros centrais do projeto de previsao eleitoral 2026.
Todos os caminhos sao derivados de ROOT -- nunca hardcode caminhos absolutos fora deste arquivo.

FONTE UNICA DE VERDADE para nomes e partidos dos candidatos do edital.
Pipeline, testes e xlsx usam CANDIDATOS_EDITAL e PARTIDOS_EDITAL.
"""

from pathlib import Path

# --------------------------------------------------------------------------- #
# Raiz do projeto
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------- #
# Diretorios principais
# --------------------------------------------------------------------------- #
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MANUAL_DIR = DATA_DIR / "manual"
MANIFEST_PATH = DATA_DIR / "MANIFEST.csv"

OUTPUTS_DIR = ROOT / "outputs"
REPORTS_DIR = ROOT / "reports"
DOCS_DIR = ROOT / "docs"
INTERFACE_DIR = ROOT / "interface"
NOTEBOOKS_DIR = ROOT / "notebooks"

# --------------------------------------------------------------------------- #
# Horario de corte (a ser confirmado pelo usuario antes do pre-registro)
# --------------------------------------------------------------------------- #
# Sabado 03/10/2026 -- horario exato a definir e registrar em PRE_REGISTRO.md.
# Formato ISO 8601 com fuso -03:00.
HORARIO_CORTE = "2026-10-03T20:00:00-03:00"

# --------------------------------------------------------------------------- #
# Eleicoes historicas (treinamento e backtest)
# --------------------------------------------------------------------------- #
ANOS_HISTORICO = [2006, 2010, 2014, 2018, 2022]

# --------------------------------------------------------------------------- #
# Candidatos oficiais do 1o turno de 2026 -- EXATAMENTE como no edital FGV EPGE
# (com acentos). Esta e a UNICA fonte de verdade para nomes e partidos.
# Pipeline, testes e arquivo xlsx usam esta lista.
# --------------------------------------------------------------------------- #
CANDIDATOS_EDITAL = [
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

PARTIDOS_EDITAL = {
    "Augusto Cury": "Avante",
    "Clariana Barão": "DC",
    "Edmilson Costa": "PCB",
    "Flávio Bolsonaro": "PL",
    "Hertz Dias": "PSTU",
    "Luiz Inácio Lula da Silva": "PT",
    "Renan Santos": "Missão",
    "Ronaldo Caiado": "PSD",
    "Romeu Zema": "Novo",
    "Rui Costa Pimenta": "PCO",
    "Samara Martins": "UP",
    "Wilson Grassi": "Democrata",
}

# Alias para compatibilidade com codigo existente
CANDIDATOS_2026 = CANDIDATOS_EDITAL

# Candidatos nanicos (esperado << 5% com base em historico)
CANDIDATOS_NANICOS = [
    "Augusto Cury",
    "Clariana Barão",
    "Edmilson Costa",
    "Hertz Dias",
    "Renan Santos",
    "Rui Costa Pimenta",
    "Samara Martins",
    "Wilson Grassi",
]

# --------------------------------------------------------------------------- #
# Sementes aleatorias (reproducibilidade)
# --------------------------------------------------------------------------- #
RANDOM_SEED = 42

# --------------------------------------------------------------------------- #
# Parametros dos modelos (grades declaradas; alteracoes devem ir em DECISOES.md)
# --------------------------------------------------------------------------- #

# M1: meia-vida para ponderacao por recencia (em dias)
M1_MEIASVIDAS_GRID = [7, 14, 21]
M1_MEIAVIDA_DEFAULT = 14

# M2: parametro de regularizacao do house effect (shrinkage para zero)
M2_SHRINKAGE_GRID = [0.1, 0.5, 1.0]

# M3: Ridge regression -- alpha escolhido por CV interno
M3_ALPHA_GRID = [0.01, 0.1, 1.0, 10.0]

# Janela de pesquisas para o modelo principal (dias antes do 1o turno)
JANELA_DIAS = 21  # 3 semanas

# --------------------------------------------------------------------------- #
# URLs das fontes do TSE
# --------------------------------------------------------------------------- #
TSE_BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele"

TSE_URLS = {
    ano: {
        "votacao": (
            f"{TSE_BASE_URL}/votacao_candidato_munzona/"
            f"votacao_candidato_munzona_{ano}.zip"
        ),
        "detalhe": (
            f"{TSE_BASE_URL}/detalhe_votacao_munzona/"
            f"detalhe_votacao_munzona_{ano}.zip"
        ),
    }
    for ano in ANOS_HISTORICO
}

TSE_CANDIDATOS_2026_URL = (
    f"{TSE_BASE_URL}/consulta_cand/consulta_cand_2026.zip"
)

# --------------------------------------------------------------------------- #
# Schema do arquivo de pesquisas manuais de 2026
# --------------------------------------------------------------------------- #
PESQUISAS_2026_PATH = MANUAL_DIR / "pesquisas_2026.csv"

PESQUISAS_2026_SCHEMA = (
    [
        "instituto",
        "data_inicio_campo",
        "data_fim_campo",
        "data_divulgacao",
        "amostra",
        "registro_tse",
        "metodo_coleta",
    ]
    + CANDIDATOS_EDITAL
    + ["brancos_nulos", "indecisos", "fonte_url"]
)

# --------------------------------------------------------------------------- #
# Verificacoes de sanidade para backtest 2022 (valores oficiais TSE)
# --------------------------------------------------------------------------- #
SANIDADE_2022 = {
    "Luiz Inácio Lula da Silva": 48.43,
    "Jair Messias Bolsonaro": 43.20,
    "abstencao_pct": 20.95,
}

SANIDADE_TOLERANCIA = 0.05  # pontos percentuais


def verificar_sanidade_2022(resultados: dict) -> bool:
    """
    Verifica se os resultados calculados do TSE para 2022 batem com os
    valores oficiais dentro da tolerancia definida.

    Parameters
    ----------
    resultados : dict
        Dicionario {candidato: pct_votos_validos, 'abstencao_pct': float}

    Returns
    -------
    bool
        True se todos os valores estiverem dentro da tolerancia.
    """
    ok = True
    for chave, esperado in SANIDADE_2022.items():
        calculado = resultados.get(chave)
        if calculado is None:
            print(f"SANIDADE FAIL: '{chave}' nao encontrado nos resultados.")
            ok = False
            continue
        diff = abs(calculado - esperado)
        if diff > SANIDADE_TOLERANCIA:
            print(
                f"SANIDADE FAIL: '{chave}' "
                f"esperado={esperado:.2f}%, calculado={calculado:.2f}%, "
                f"diferenca={diff:.3f}pp > tolerancia={SANIDADE_TOLERANCIA}pp"
            )
            ok = False
        else:
            print(
                f"SANIDADE OK:   '{chave}' "
                f"esperado={esperado:.2f}%, calculado={calculado:.2f}%, "
                f"diferenca={diff:.3f}pp"
            )
    return ok
