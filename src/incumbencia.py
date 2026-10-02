"""
Mapeamento formal de incumbencia governista para as eleicoes presidenciais (2006-2026).
Incumbencia = 1 para o candidato presidente em exercicio ou formalmente apoiado pelo
Executivo Federal incumbente daquele ciclo eleitoral; 0 para a oposicao.
"""

INCUMBENCIA_HISTORICA: dict[int, dict[str, int]] = {
    2006: {
        "Luiz Inácio Lula da Silva": 1,
        "Geraldo Alckmin": 0,
        "Heloísa Helena": 0,
        "Cristovam Buarque": 0,
        "Ana Maria Rangel": 0,
        "José Maria Eymael": 0,
        "Luciano Bivar": 0,
        "Rui Costa Pimenta": 0,
    },
    2010: {
        "Dilma Rousseff": 1,  # Apoiada expressamente pelo governo Lula em exercicio
        "José Serra": 0,
        "Marina Silva": 0,
        "Plínio de Arruda Sampaio": 0,
        "Ivan Pinheiro": 0,
        "José Maria de Almeida": 0,
        "José Maria Eymael": 0,
        "Levy Fidelix": 0,
        "Rui Costa Pimenta": 0,
    },
    2014: {
        "Dilma Rousseff": 1,  # Presidente em exercicio
        "Aécio Neves": 0,
        "Marina Silva": 0,
        "Luciana Genro": 0,
        "Pastor Everaldo": 0,
        "Eduardo Jorge": 0,
        "Levy Fidelix": 0,
        "José Maria de Almeida": 0,
        "José Maria Eymael": 0,
        "Mauro Iasi": 0,
        "Rui Costa Pimenta": 0,
    },
    2018: {
        "Henrique Meirelles": 1,  # Candidato governista (ex-Ministro da Fazenda de Michel Temer)
        "Jair Bolsonaro": 0,
        "Fernando Haddad": 0,
        "Ciro Gomes": 0,
        "Geraldo Alckmin": 0,
        "João Amoêdo": 0,
        "Marina Silva": 0,
        "Alvaro Dias": 0,
        "Guilherme Boulos": 0,
        "Cabo Daciolo": 0,
        "Vera": 0,
        "José Maria Eymael": 0,
        "João Goulart Filho": 0,
    },
    2022: {
        "Jair Bolsonaro": 1,  # Presidente em exercicio
        "Luiz Inácio Lula da Silva": 0,
        "Ciro Gomes": 0,
        "Simone Tebet": 0,
        "Soraya Thronicke": 0,
        "Felipe D'Avila": 0,
        "Padre Kelmon": 0,
        "Léo Péricles": 0,
        "Sofia Manzano": 0,
        "Vera": 0,
        "Constituinte Eymael": 0,
    },
    2026: {
        "Luiz Inácio Lula da Silva": 1,  # Presidente em exercicio
        "Flávio Bolsonaro": 0,
        "Augusto Cury": 0,
        "Renan Santos": 0,
        "Ronaldo Caiado": 0,
        "Romeu Zema": 0,
        "Clariana Barão": 0,
        "Edmilson Costa": 0,
        "Hertz Dias": 0,
        "Rui Costa Pimenta": 0,
        "Samara Martins": 0,
        "Wilson Grassi": 0,
    },
}


def obter_incumbencia(eleicao: int, candidato: str) -> int:
    """Retorna 1 se o candidato for governista/incumbente na eleicao, 0 caso contrario."""
    ano_dict = INCUMBENCIA_HISTORICA.get(eleicao, {})
    if candidato in ano_dict:
        return ano_dict[candidato]
    # Busca por correspondencia de primeiro e ultimo nome
    cand_norm = candidato.lower().strip()
    for k, v in ano_dict.items():
        if k.lower().strip() == cand_norm:
            return v
    # Default: candidato de oposicao
    return 0
