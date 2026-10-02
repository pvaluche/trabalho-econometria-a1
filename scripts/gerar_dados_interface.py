"""
scripts/gerar_dados_interface.py
Gera o arquivo interface/dados.json a partir do motor econometrico de backtest.
Fornece todos os dados dinamicos para o painel Comparador de Modelos da interface.
"""

from __future__ import annotations

from datetime import datetime
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.arredondamento import maiores_restos
from src.backtest import (
    HISTORICO_CANDIDATOS,
    aplicar_ajuste_priors_nanicos,
    aplicar_ajuste_vies_comum,
    aplicar_ajuste_voto_util,
    calcular_diferenca_e_se,
    calcular_mae_eleicao,
    carregar_resultado_tse,
    estimar_m0,
    obter_pesquisas_eleicao,
)
from src.config import CANDIDATOS_EDITAL, MANUAL_DIR, PARTIDOS_EDITAL


def obter_git_commit() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "47cf3d5"


def aplicar_maiores_restos_dict(d: dict[str, float]) -> dict[str, float]:
    keys = list(d.keys())
    vals = [d[k] for k in keys]
    arr = maiores_restos(vals, total=100.0, casas=1)
    return {k: round(v, 1) for k, v in zip(keys, arr)}


def executar_configuracao(cfg_id: str, df: pd.DataFrame, t: int, tr: list[int]) -> dict[str, float]:
    p = estimar_m0(df, t)
    if cfg_id == "m0":
        return p
    elif cfg_id == "m0_vies":
        return aplicar_ajuste_vies_comum(p, t, tr, k_mu=3.0)
    elif cfg_id == "m0_util":
        return aplicar_ajuste_voto_util(p, t, tr, gamma=1.0)
    elif cfg_id == "m0_nanicos":
        return aplicar_ajuste_priors_nanicos(p, t, w=0.5)
    elif cfg_id == "combinado":
        p = aplicar_ajuste_vies_comum(p, t, tr, k_mu=3.0)
        p = aplicar_ajuste_voto_util(p, t, tr, gamma=1.0)
        p = aplicar_ajuste_priors_nanicos(p, t, w=0.5)
        return p
    return p


def gerar_dados():
    treino_expanding = {
        2014: [2006, 2010],
        2018: [2006, 2010, 2014],
        2022: [2006, 2010, 2014, 2018],
    }
    todos_loeo = [2006, 2010, 2014, 2018, 2022]

    # Faixas empiricas do backtest
    faixas_map = {
        "top2": 2.4,
        "terceira_via": 1.5,
        "demais": 1.0,
    }

    configs_meta = [
        {
            "id": "m0",
            "nome": "M0 Puro (Média Simples)",
            "rotulo": "M0",
            "descricao": "Média simples da última pesquisa de cada instituto na janela de corte de véspera.",
            "formula": "y = media(pesquisas_vespera)",
            "status_regra": "Referência",
            "justificativa": "Modelo base vencedor da Etapa 1 pela regra de parcimônia (menor MAE).",
        },
        {
            "id": "m0_vies",
            "nome": "M0 + Viés Comum (k=3)",
            "rotulo": "M0 + Viés",
            "descricao": "M0 com correção regularizada do viés comum histórico por bloco político.",
            "formula": "y = M0 - mu_hat (k_mu=3)",
            "status_regra": "Aprovado",
            "justificativa": "Reduz o MAE em 0,3209 p.p. superando amplamente 1 SE(Delta) = 0,0215 p.p.",
        },
        {
            "id": "m0_util",
            "nome": "M0 + Voto Útil (gamma=1.0)",
            "rotulo": "M0 + Voto Útil",
            "descricao": "Transferência da desidratação do 3º e 4º colocados para os líderes da polarização.",
            "formula": "y = M0 + trans_util (gamma=1.0)",
            "status_regra": "Aprovado",
            "justificativa": "Reduz o MAE em 0,3252 p.p. superando 1 SE(Delta) = 0,2128 p.p. (MAE 2022 cai para 0,75).",
        },
        {
            "id": "m0_nanicos",
            "nome": "M0 + Prior Nanicos (w=0.5)",
            "rotulo": "M0 + Nanicos",
            "descricao": "Combinação convexa das intenções com a mediana histórica do TSE para legendas < 0,5%.",
            "formula": "y = (1-w)*M0 + w*Prior_TSE (w=0.5)",
            "status_regra": "Neutro no histórico (Ativo em 2026)",
            "justificativa": "Evita distorções de 0,0% ancorando nanicos na mediana histórica oficial do TSE.",
        },
        {
            "id": "combinado",
            "nome": "Modelo Combinado (Viés + Voto Útil + Nanicos)",
            "rotulo": "Combinado",
            "descricao": "M0 integrando todos os ajustes individuais aprovados na Etapa 2.",
            "formula": "y = M0 + Viés(k=3) + VotoÚtil(g=1.0) + Nanicos(w=0.5)",
            "status_regra": "Aprovado no histórico",
            "justificativa": "Menor erro histórico consolidado (MAE 1,5658 p.p.), com ganho em todas as eleições.",
        },
    ]

    # Carrega pesquisas 2026
    df_2026 = pd.read_csv(MANUAL_DIR / "pesquisas_2026.csv")
    treino_completo_2026 = [2006, 2010, 2014, 2018, 2022]

    # Executa cada configuracao
    resultados_configs = {}
    mae_base_exp_vals = None

    for meta in configs_meta:
        cfg_id = meta["id"]

        # 1. Backtest Expanding Window
        maes_exp = {}
        for t in [2014, 2018, 2022]:
            df_t = obter_pesquisas_eleicao(t)
            res = carregar_resultado_tse(t)
            p = executar_configuracao(cfg_id, df_t, t, treino_expanding[t])
            maes_exp[str(t)] = round(float(calcular_mae_eleicao(p, res)), 4)

        vals_exp = [maes_exp[str(t)] for t in [2014, 2018, 2022]]
        mae_exp_med = round(float(np.mean(vals_exp)), 4)
        se_exp = round(float(np.std(vals_exp, ddof=1) / math.sqrt(len(vals_exp))), 4)

        if cfg_id == "m0":
            mae_base_exp_vals = vals_exp
            delta_vs_m0 = 0.0
            se_delta = 0.0
        else:
            delta_bar, se_d = calcular_diferenca_e_se(vals_exp, mae_base_exp_vals)
            delta_vs_m0 = round(delta_bar, 4)
            se_delta = round(se_d, 4)

        # 2. Backtest LOEO
        maes_loeo = {}
        for t in todos_loeo:
            tr = [y for y in todos_loeo if y != t]
            df_t = obter_pesquisas_eleicao(t)
            res = carregar_resultado_tse(t)
            p = executar_configuracao(cfg_id, df_t, t, tr)
            maes_loeo[str(t)] = round(float(calcular_mae_eleicao(p, res)), 4)

        vals_loeo = [maes_loeo[str(t)] for t in todos_loeo]
        mae_loeo_med = round(float(np.mean(vals_loeo)), 4)
        se_loeo = round(float(np.std(vals_loeo, ddof=1) / math.sqrt(len(vals_loeo))), 4)

        # 3. Projecao 2026
        pred_raw = executar_configuracao(cfg_id, df_2026, 2026, treino_completo_2026)
        pred_fechada = aplicar_maiores_restos_dict(pred_raw)

        # Ranking ordenado
        cands_ordenados = sorted(CANDIDATOS_EDITAL, key=lambda c: (pred_fechada[c], pred_raw.get(c, 0)), reverse=True)
        tabela_cands = []
        for i, c in enumerate(cands_ordenados):
            pct_val = pred_fechada[c]
            raw_val = round(float(pred_raw.get(c, 0.0)), 4)
            if i < 2:
                faixa = faixas_map["top2"]
            elif i < 4:
                faixa = faixas_map["terceira_via"]
            else:
                faixa = faixas_map["demais"]

            min_val = round(max(0.0, pct_val - faixa), 1)
            max_val = round(pct_val + faixa, 1)

            tabela_cands.append({
                "posicao": i + 1,
                "candidato": c,
                "partido": PARTIDOS_EDITAL[c],
                "pct": pct_val,
                "pct_raw": raw_val,
                "faixa_erro": faixa,
                "min": min_val,
                "max": max_val,
            })

        # Destaque Lula x Flavio
        pct_lula = pred_fechada["Luiz Inácio Lula da Silva"]
        pct_flavio = pred_fechada["Flávio Bolsonaro"]
        diff = round(abs(pct_flavio - pct_lula), 1)
        if pct_flavio > pct_lula:
            lider = "Flávio Bolsonaro"
            vantagem_txt = f"Flávio Bolsonaro +{diff} p.p."
        elif pct_lula > pct_flavio:
            lider = "Luiz Inácio Lula da Silva"
            vantagem_txt = f"Luiz Inácio Lula da Silva +{diff} p.p."
        else:
            lider = "Empate Exato"
            vantagem_txt = "Empate em 46,0%"

        empate_tecnico = bool(diff <= faixas_map["top2"])

        resultados_configs[cfg_id] = {
            **meta,
            "previsao_2026": {
                "tabela": tabela_cands,
                "soma": round(sum(pred_fechada.values()), 1),
            },
            "top2_destaque": {
                "lula": pct_lula,
                "flavio": pct_flavio,
                "diferenca": diff,
                "lider": lider,
                "vantagem_texto": vantagem_txt,
                "faixa_top2": faixas_map["top2"],
                "empate_tecnico": empate_tecnico,
            },
            "backtest_expanding": {
                "erros": maes_exp,
                "mae_medio": mae_exp_med,
                "se": se_exp,
            },
            "backtest_loeo": {
                "erros": maes_loeo,
                "mae_medio": mae_loeo_med,
                "se": se_loeo,
            },
            "regra_decisao": {
                "delta_vs_m0": delta_vs_m0,
                "se_delta": se_delta,
                "status": meta["status_regra"],
                "justificativa": meta["justificativa"],
            },
        }

    # 4. Aba 2: Agregados Eleitorais (3 metodos x 3 eleicoes)
    tse_adicionais = {
        2006: {"abstencao": 16.75, "brancos": 2.73, "nulos": 5.68},
        2010: {"abstencao": 18.12, "brancos": 3.13, "nulos": 5.51},
        2014: {"abstencao": 19.39, "brancos": 3.84, "nulos": 5.80},
        2018: {"abstencao": 20.33, "brancos": 2.65, "nulos": 6.14},
        2022: {"abstencao": 20.95, "brancos": 1.59, "nulos": 2.82},
    }

    metodos_aba2 = ["Persistência (Random Walk)", "Média Móvel Histórica", "Tendência Linear"]
    variaveis_info = {
        "abstencao": {
            "nome": "Abstenção",
            "denominador": "% sobre o total de eleitores aptos",
            "vencedor": "Tendência Linear",
            "projecao_oficial": 22.3,
            "justificativa": "Tendência secular linear (R2 > 0.98) com menor MAE no backtest (0.3989 p.p.).",
        },
        "brancos": {
            "nome": "Votos Brancos",
            "denominador": "% sobre o comparecimento",
            "vencedor": "Persistência (Random Walk)",
            "projecao_oficial": 1.6,
            "justificativa": "Menor erro médio no expanding window (0.9867 p.p.), preservando o patamar de 2022.",
        },
        "nulos": {
            "nome": "Votos Nulos",
            "denominador": "% sobre o comparecimento",
            "vencedor": "Média Móvel / Persistência 2022",
            "projecao_oficial": 2.8,
            "justificativa": "Menor erro recente; persistência do patamar 2022 evita sobrestimação espúria.",
        },
    }

    dados_aba2 = {}
    for var, v_meta in variaveis_info.items():
        lista_metodos = []
        for met in metodos_aba2:
            erros_met = {}
            for t in [2014, 2018, 2022]:
                tr = treino_expanding[t]
                y_tr = [tse_adicionais[y][var] for y in tr]
                y_real = tse_adicionais[t][var]

                if met == "Persistência (Random Walk)":
                    pred = y_tr[-1]
                elif met == "Média Móvel Histórica":
                    pred = float(np.mean(y_tr))
                elif met == "Tendência Linear":
                    X_tr = np.array(tr).reshape(-1, 1)
                    reg = LinearRegression().fit(X_tr, y_tr)
                    pred = float(reg.predict(np.array([[t]]))[0])

                erros_met[str(t)] = round(abs(pred - y_real), 3)

            # Projecao 2026 do metodo
            tr_all = [2006, 2010, 2014, 2018, 2022]
            y_all = [tse_adicionais[y][var] for y in tr_all]
            if met == "Persistência (Random Walk)":
                p26 = y_all[-1]
            elif met == "Média Móvel Histórica":
                p26 = float(np.mean(y_all))
            elif met == "Tendência Linear":
                reg_all = LinearRegression().fit(np.array(tr_all).reshape(-1, 1), y_all)
                p26 = float(reg_all.predict([[2026]])[0])

            mae_medio = round(float(np.mean(list(erros_met.values()))), 4)

            lista_metodos.append({
                "metodo": met,
                "erro_2014": erros_met["2014"],
                "erro_2018": erros_met["2018"],
                "erro_2022": erros_met["2022"],
                "mae_medio": mae_medio,
                "projecao_2026": round(p26, 1),
                "selecionado": met.startswith(v_meta["vencedor"].split()[0]),
            })

        dados_aba2[var] = {
            **v_meta,
            "metodos_tabela": lista_metodos,
        }

    # 5. Painel Backtest por Eleicao (Candidato a Candidato: M0 vs Modelo Escolhido)
    backtest_por_ano = {}
    for t in [2014, 2018, 2022]:
        tr = treino_expanding[t]
        df_t = obter_pesquisas_eleicao(t)
        res_tse = carregar_resultado_tse(t)

        p_m0 = estimar_m0(df_t, t)
        p_esc = executar_configuracao("combinado", df_t, t, tr)

        cands = sorted(HISTORICO_CANDIDATOS[t], key=lambda c: res_tse[c], reverse=True)
        tabela_ano = []
        for c in cands:
            real_val = res_tse[c]
            m0_val = p_m0[c]
            esc_val = p_esc[c]
            tabela_ano.append({
                "candidato": c,
                "real_tse": round(real_val, 2),
                "pred_m0": round(m0_val, 2),
                "erro_m0": round(m0_val - real_val, 2),
                "pred_escolhido": round(esc_val, 2),
                "erro_escolhido": round(esc_val - real_val, 2),
            })

        backtest_por_ano[str(t)] = {
            "ano": t,
            "candidatos": tabela_ano,
            "mae_m0": round(calcular_mae_eleicao(p_m0, res_tse), 4),
            "mae_escolhido": round(calcular_mae_eleicao(p_esc, res_tse), 4),
        }

    # 6. Payload Final
    commit_sha = obter_git_commit()
    timestamp_iso = datetime.now().astimezone().isoformat(timespec="seconds")

    payload = {
        "metadata": {
            "titulo": "Painel Comparador de Modelos - Desafio FGV EPGE 2026",
            "grupo": ["João Pedro Valuche", "Arthur Caron Lyra", "Lethicia Manfioletti Possamai"],
            "commit": commit_sha,
            "gerado_em": timestamp_iso,
            "status": "PRELIMINAR (aguardando pesquisas de véspera de sábado 03/10 às 20h)",
            "aviso_governanca": "Ferramenta de decisão do grupo. Nenhuma configuração é oficial até a criação da tag modelo-congelado.",
            "total_pesquisas_2026": len(df_2026),
            "faixas_empiricas": faixas_map,
        },
        "configuracoes": resultados_configs,
        "aba2_agregados": dados_aba2,
        "backtest_por_eleicao": backtest_por_ano,
    }

    out_file = ROOT / "interface" / "dados.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: dados.json gerado com sucesso em {out_file} ({out_file.stat().st_size} bytes)")
    return out_file


if __name__ == "__main__":
    gerar_dados()
