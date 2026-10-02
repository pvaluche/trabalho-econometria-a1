// Gerado automaticamente por scripts/gerar_dados_interface.py
window.DADOS = {
  "metadata": {
    "titulo": "Painel Comparador de Modelos - Desafio FGV EPGE 2026",
    "grupo": [
      "João Pedro Valuche",
      "Arthur Caron Lyra",
      "Lethicia Manfioletti Possamai"
    ],
    "commit": "a44b0a3",
    "gerado_em": "2026-10-02T15:43:45-03:00",
    "status": "PRELIMINAR (aguardando pesquisas de véspera de sábado 03/10 às 20h)",
    "aviso_governanca": "Ferramenta de decisão do grupo. Nenhuma configuração é a oficial até a criação da tag modelo-congelado.",
    "total_pesquisas_2026": 6,
    "faixas_empiricas": {
      "top2": {
        "media": 2.72,
        "p80": 4.92,
        "label": "Top-2 (Líderes)"
      },
      "terceira_via": {
        "media": 1.35,
        "p80": 2.46,
        "label": "3º e 4º colocados"
      },
      "demais": {
        "media": 0.44,
        "p80": 0.62,
        "label": "Demais candidatos"
      }
    },
    "protocolos_sabado": [
      {
        "instituto": "Datafolha",
        "protocolo": "BR-01708/2026",
        "amostra": 4006,
        "campo": "01 a 03/10/2026",
        "divulgacao": "03/10/2026"
      },
      {
        "instituto": "Quaest",
        "protocolo": "BR-02197/2026",
        "amostra": 3702,
        "campo": "02 a 03/10/2026",
        "divulgacao": "03/10/2026"
      },
      {
        "instituto": "AtlasIntel",
        "protocolo": "BR-00999/2026",
        "amostra": 5000,
        "campo": "28/09 a 02/10/2026",
        "divulgacao": "03/10/2026"
      },
      {
        "instituto": "PoderData",
        "protocolo": "BR-03519/2026",
        "amostra": 4000,
        "campo": "01 a 03/10/2026",
        "divulgacao": "03/10/2026"
      },
      {
        "instituto": "Real Time Big Data",
        "protocolo": "BR-01068/2026",
        "amostra": 2000,
        "campo": "01 a 02/10/2026",
        "divulgacao": "03/10/2026"
      }
    ]
  },
  "configuracoes": {
    "modelo_oficial": {
      "id": "modelo_oficial",
      "nome": "Modelo Oficial Aprovado (w=0)",
      "rotulo": "Modelo Oficial",
      "descricao": "M0 integrando os ajustes aprovados pela regra formal: Viés Comum (k_mu=3) e Voto Útil (gamma=1.0), com w=0 para nanicos.",
      "formula": "y = M0 + Vies(k=3) + VotoUtil(g=1.0) + Nanicos(w=0.0)",
      "status_regra": "Modelo Oficial Aprovado",
      "justificativa": "Menor erro médio consolidado no expanding window (MAE 0,9640 p.p.), com redução consistente em todas as eleições.",
      "is_default": true,
      "previsao_2026": {
        "tabela": [
          {
            "posicao": 1,
            "candidato": "Flávio Bolsonaro",
            "partido": "PL",
            "pct": 45.9,
            "pct_raw": 45.883,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 41.0,
            "max": 50.8
          },
          {
            "posicao": 2,
            "candidato": "Luiz Inácio Lula da Silva",
            "partido": "PT",
            "pct": 45.6,
            "pct_raw": 45.5757,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 40.7,
            "max": 50.5
          },
          {
            "posicao": 3,
            "candidato": "Ronaldo Caiado",
            "partido": "PSD",
            "pct": 2.6,
            "pct_raw": 2.6422,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 0.1,
            "max": 5.1
          },
          {
            "posicao": 4,
            "candidato": "Augusto Cury",
            "partido": "Avante",
            "pct": 2.6,
            "pct_raw": 2.6417,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 0.1,
            "max": 5.1
          },
          {
            "posicao": 5,
            "candidato": "Renan Santos",
            "partido": "Missão",
            "pct": 2.5,
            "pct_raw": 2.4944,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 1.9,
            "max": 3.1
          },
          {
            "posicao": 6,
            "candidato": "Romeu Zema",
            "partido": "Novo",
            "pct": 0.7,
            "pct_raw": 0.6965,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.1,
            "max": 1.3
          },
          {
            "posicao": 7,
            "candidato": "Samara Martins",
            "partido": "UP",
            "pct": 0.1,
            "pct_raw": 0.0665,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.7
          },
          {
            "posicao": 8,
            "candidato": "Clariana Barão",
            "partido": "DC",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 9,
            "candidato": "Edmilson Costa",
            "partido": "PCB",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 10,
            "candidato": "Hertz Dias",
            "partido": "PSTU",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 11,
            "candidato": "Rui Costa Pimenta",
            "partido": "PCO",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 12,
            "candidato": "Wilson Grassi",
            "partido": "Democrata",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          }
        ],
        "soma": 100.0
      },
      "top2_destaque": {
        "lula": 45.6,
        "flavio": 45.9,
        "diferenca": 0.3,
        "lider": "Flávio Bolsonaro",
        "vantagem_texto": "Flávio Bolsonaro +0.3 p.p.",
        "erro_margem_stats": {
          "por_ano": {
            "2014": 5.72,
            "2018": 3.58,
            "2022": 4.32
          },
          "media": 4.54,
          "p80": 5.16,
          "max": 5.72
        },
        "empate_tecnico": true,
        "explicacao_empate": "Diferença projetada (0.3 p.p.) é inferior ao P80 do erro da margem histórica (5.2 p.p.) e ao erro máximo (5.7 p.p.), confirmando empate técnico na disputa pela liderança."
      },
      "backtest_expanding": {
        "erros": {
          "2014": 0.9245,
          "2018": 1.3855,
          "2022": 0.5819
        },
        "mae_medio": 0.964,
        "se": 0.2328
      },
      "backtest_loeo": {
        "erros": {
          "2006": 1.3923,
          "2010": 2.1393,
          "2014": 0.8784,
          "2018": 1.2182,
          "2022": 0.5819
        },
        "mae_medio": 1.242,
        "se": 0.2642
      },
      "regra_decisao": {
        "delta_vs_m0": -0.2568,
        "se_delta": 0.0856,
        "status": "Modelo Oficial Aprovado",
        "justificativa": "Menor erro médio consolidado no expanding window (MAE 0,9640 p.p.), com redução consistente em todas as eleições."
      }
    },
    "m0": {
      "id": "m0",
      "nome": "M0 Puro (Média Simples)",
      "rotulo": "M0 Puro",
      "descricao": "Média simples da última pesquisa de cada instituto na véspera (sem ponderação, sem ajustes).",
      "formula": "y = media(pesquisas_vespera)",
      "status_regra": "Referência Base",
      "justificativa": "Modelo base vencedor da Etapa 1 pela regra de parcimônia (MAE 1,2207 p.p. vs M1=1,4878 e M2=1,4890).",
      "is_default": false,
      "previsao_2026": {
        "tabela": [
          {
            "posicao": 1,
            "candidato": "Luiz Inácio Lula da Silva",
            "partido": "PT",
            "pct": 45.4,
            "pct_raw": 45.3895,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 40.5,
            "max": 50.3
          },
          {
            "posicao": 2,
            "candidato": "Flávio Bolsonaro",
            "partido": "PL",
            "pct": 41.5,
            "pct_raw": 41.435,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 36.6,
            "max": 46.4
          },
          {
            "posicao": 3,
            "candidato": "Augusto Cury",
            "partido": "Avante",
            "pct": 4.1,
            "pct_raw": 4.1204,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 1.6,
            "max": 6.6
          },
          {
            "posicao": 4,
            "candidato": "Renan Santos",
            "partido": "Missão",
            "pct": 3.9,
            "pct_raw": 3.9106,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 1.4,
            "max": 6.4
          },
          {
            "posicao": 5,
            "candidato": "Ronaldo Caiado",
            "partido": "PSD",
            "pct": 3.0,
            "pct_raw": 3.0222,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 2.4,
            "max": 3.6
          },
          {
            "posicao": 6,
            "candidato": "Romeu Zema",
            "partido": "Novo",
            "pct": 1.1,
            "pct_raw": 1.0607,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.5,
            "max": 1.7
          },
          {
            "posicao": 7,
            "candidato": "Samara Martins",
            "partido": "UP",
            "pct": 0.4,
            "pct_raw": 0.4256,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 1.0
          },
          {
            "posicao": 8,
            "candidato": "Wilson Grassi",
            "partido": "Democrata",
            "pct": 0.2,
            "pct_raw": 0.2151,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.8
          },
          {
            "posicao": 9,
            "candidato": "Clariana Barão",
            "partido": "DC",
            "pct": 0.2,
            "pct_raw": 0.2105,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.8
          },
          {
            "posicao": 10,
            "candidato": "Rui Costa Pimenta",
            "partido": "PCO",
            "pct": 0.2,
            "pct_raw": 0.2105,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.8
          },
          {
            "posicao": 11,
            "candidato": "Edmilson Costa",
            "partido": "PCB",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 12,
            "candidato": "Hertz Dias",
            "partido": "PSTU",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          }
        ],
        "soma": 100.0
      },
      "top2_destaque": {
        "lula": 45.4,
        "flavio": 41.5,
        "diferenca": 3.9,
        "lider": "Luiz Inácio Lula da Silva",
        "vantagem_texto": "Luiz Inácio Lula da Silva +3.9 p.p.",
        "erro_margem_stats": {
          "por_ano": {
            "2014": 10.89,
            "2018": 3.58,
            "2022": 1.29
          },
          "media": 5.25,
          "p80": 7.97,
          "max": 10.89
        },
        "empate_tecnico": true,
        "explicacao_empate": "Diferença projetada (3.9 p.p.) é inferior ao P80 do erro da margem histórica (8.0 p.p.) e ao erro máximo (10.9 p.p.), confirmando empate técnico na disputa pela liderança."
      },
      "backtest_expanding": {
        "erros": {
          "2014": 1.3317,
          "2018": 1.4964,
          "2022": 0.8341
        },
        "mae_medio": 1.2207,
        "se": 0.1991
      },
      "backtest_loeo": {
        "erros": {
          "2006": 1.7974,
          "2010": 1.7775,
          "2014": 1.3317,
          "2018": 1.4964,
          "2022": 0.8341
        },
        "mae_medio": 1.4474,
        "se": 0.1765
      },
      "regra_decisao": {
        "delta_vs_m0": 0.0,
        "se_delta": 0.0,
        "status": "Referência Base",
        "justificativa": "Modelo base vencedor da Etapa 1 pela regra de parcimônia (MAE 1,2207 p.p. vs M1=1,4878 e M2=1,4890)."
      }
    },
    "m0_vies": {
      "id": "m0_vies",
      "nome": "M0 + Viés Comum (k=3)",
      "rotulo": "M0 + Viés",
      "descricao": "M0 com correção regularizada do viés histórico comum por bloco político (PT, Principal Adversário, Demais).",
      "formula": "y = M0 - mu_hat (k_mu=3)",
      "status_regra": "Aprovado na Etapa 2",
      "justificativa": "Reduz o MAE em 0,1834 p.p. superando 1 SE(Delta) = 0,1026 p.p. (reduz erro em 2014 e 2022).",
      "is_default": false,
      "previsao_2026": {
        "tabela": [
          {
            "posicao": 1,
            "candidato": "Flávio Bolsonaro",
            "partido": "PL",
            "pct": 44.8,
            "pct_raw": 44.8199,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 39.9,
            "max": 49.7
          },
          {
            "posicao": 2,
            "candidato": "Luiz Inácio Lula da Silva",
            "partido": "PT",
            "pct": 44.5,
            "pct_raw": 44.5198,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 39.6,
            "max": 49.4
          },
          {
            "posicao": 3,
            "candidato": "Augusto Cury",
            "partido": "Avante",
            "pct": 3.7,
            "pct_raw": 3.7316,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 1.2,
            "max": 6.2
          },
          {
            "posicao": 4,
            "candidato": "Renan Santos",
            "partido": "Missão",
            "pct": 3.5,
            "pct_raw": 3.5235,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 1.0,
            "max": 6.0
          },
          {
            "posicao": 5,
            "candidato": "Ronaldo Caiado",
            "partido": "PSD",
            "pct": 2.7,
            "pct_raw": 2.6422,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 2.1,
            "max": 3.3
          },
          {
            "posicao": 6,
            "candidato": "Romeu Zema",
            "partido": "Novo",
            "pct": 0.7,
            "pct_raw": 0.6965,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.1,
            "max": 1.3
          },
          {
            "posicao": 7,
            "candidato": "Samara Martins",
            "partido": "UP",
            "pct": 0.1,
            "pct_raw": 0.0665,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.7
          },
          {
            "posicao": 8,
            "candidato": "Clariana Barão",
            "partido": "DC",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 9,
            "candidato": "Edmilson Costa",
            "partido": "PCB",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 10,
            "candidato": "Hertz Dias",
            "partido": "PSTU",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 11,
            "candidato": "Rui Costa Pimenta",
            "partido": "PCO",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 12,
            "candidato": "Wilson Grassi",
            "partido": "Democrata",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          }
        ],
        "soma": 100.0
      },
      "top2_destaque": {
        "lula": 44.5,
        "flavio": 44.8,
        "diferenca": 0.3,
        "lider": "Flávio Bolsonaro",
        "vantagem_texto": "Flávio Bolsonaro +0.3 p.p.",
        "erro_margem_stats": {
          "por_ano": {
            "2014": 5.66,
            "2018": 3.27,
            "2022": 4.34
          },
          "media": 4.42,
          "p80": 5.13,
          "max": 5.66
        },
        "empate_tecnico": true,
        "explicacao_empate": "Diferença projetada (0.3 p.p.) é inferior ao P80 do erro da margem histórica (5.1 p.p.) e ao erro máximo (5.7 p.p.), confirmando empate técnico na disputa pela liderança."
      },
      "backtest_expanding": {
        "erros": {
          "2014": 0.9479,
          "2018": 1.4517,
          "2022": 0.7124
        },
        "mae_medio": 1.0373,
        "se": 0.2181
      },
      "backtest_loeo": {
        "erros": {
          "2006": 1.2068,
          "2010": 1.5507,
          "2014": 1.0056,
          "2018": 1.3275,
          "2022": 0.7124
        },
        "mae_medio": 1.1606,
        "se": 0.1427
      },
      "regra_decisao": {
        "delta_vs_m0": -0.1834,
        "se_delta": 0.1026,
        "status": "Aprovado na Etapa 2",
        "justificativa": "Reduz o MAE em 0,1834 p.p. superando 1 SE(Delta) = 0,1026 p.p. (reduz erro em 2014 e 2022)."
      }
    },
    "m0_util": {
      "id": "m0_util",
      "nome": "M0 + Voto Útil (gamma=1.0)",
      "rotulo": "M0 + Voto Útil",
      "descricao": "Transferência da desidratação de véspera dos 3º e 4º colocados para os líderes polarizados.",
      "formula": "y = M0 + trans_util (gamma=1.0)",
      "status_regra": "Aprovado na Etapa 2",
      "justificativa": "Reduz o MAE em 0,1301 p.p. superando 1 SE(Delta) = 0,0889 p.p. (MAE 2022 cai para 0,5284 p.p.).",
      "is_default": false,
      "previsao_2026": {
        "tabela": [
          {
            "posicao": 1,
            "candidato": "Luiz Inácio Lula da Silva",
            "partido": "PT",
            "pct": 46.5,
            "pct_raw": 46.4972,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 41.6,
            "max": 51.4
          },
          {
            "posicao": 2,
            "candidato": "Flávio Bolsonaro",
            "partido": "PL",
            "pct": 42.5,
            "pct_raw": 42.4462,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 37.6,
            "max": 47.4
          },
          {
            "posicao": 3,
            "candidato": "Augusto Cury",
            "partido": "Avante",
            "pct": 3.0,
            "pct_raw": 3.0333,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 0.5,
            "max": 5.5
          },
          {
            "posicao": 4,
            "candidato": "Ronaldo Caiado",
            "partido": "PSD",
            "pct": 3.0,
            "pct_raw": 3.0222,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 0.5,
            "max": 5.5
          },
          {
            "posicao": 5,
            "candidato": "Renan Santos",
            "partido": "Missão",
            "pct": 2.9,
            "pct_raw": 2.8788,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 2.3,
            "max": 3.5
          },
          {
            "posicao": 6,
            "candidato": "Romeu Zema",
            "partido": "Novo",
            "pct": 1.1,
            "pct_raw": 1.0607,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.5,
            "max": 1.7
          },
          {
            "posicao": 7,
            "candidato": "Samara Martins",
            "partido": "UP",
            "pct": 0.4,
            "pct_raw": 0.4256,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 1.0
          },
          {
            "posicao": 8,
            "candidato": "Wilson Grassi",
            "partido": "Democrata",
            "pct": 0.2,
            "pct_raw": 0.2151,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.8
          },
          {
            "posicao": 9,
            "candidato": "Clariana Barão",
            "partido": "DC",
            "pct": 0.2,
            "pct_raw": 0.2105,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.8
          },
          {
            "posicao": 10,
            "candidato": "Rui Costa Pimenta",
            "partido": "PCO",
            "pct": 0.2,
            "pct_raw": 0.2105,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.8
          },
          {
            "posicao": 11,
            "candidato": "Edmilson Costa",
            "partido": "PCB",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 12,
            "candidato": "Hertz Dias",
            "partido": "PSTU",
            "pct": 0.0,
            "pct_raw": 0.0,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          }
        ],
        "soma": 100.0
      },
      "top2_destaque": {
        "lula": 46.5,
        "flavio": 42.5,
        "diferenca": 4.0,
        "lider": "Luiz Inácio Lula da Silva",
        "vantagem_texto": "Luiz Inácio Lula da Silva +4.0 p.p.",
        "erro_margem_stats": {
          "por_ano": {
            "2014": 10.97,
            "2018": 3.37,
            "2022": 1.42
          },
          "media": 5.25,
          "p80": 7.93,
          "max": 10.97
        },
        "empate_tecnico": true,
        "explicacao_empate": "Diferença projetada (4.0 p.p.) é inferior ao P80 do erro da margem histórica (7.9 p.p.) e ao erro máximo (11.0 p.p.), confirmando empate técnico na disputa pela liderança."
      },
      "backtest_expanding": {
        "erros": {
          "2014": 1.3135,
          "2018": 1.4302,
          "2022": 0.5284
        },
        "mae_medio": 1.0907,
        "se": 0.2832
      },
      "backtest_loeo": {
        "erros": {
          "2006": 1.851,
          "2010": 2.1551,
          "2014": 1.2174,
          "2018": 1.3867,
          "2022": 0.5284
        },
        "mae_medio": 1.4277,
        "se": 0.2795
      },
      "regra_decisao": {
        "delta_vs_m0": -0.13,
        "se_delta": 0.0889,
        "status": "Aprovado na Etapa 2",
        "justificativa": "Reduz o MAE em 0,1301 p.p. superando 1 SE(Delta) = 0,0889 p.p. (MAE 2022 cai para 0,5284 p.p.)."
      }
    },
    "sensibilidade_nanicos": {
      "id": "sensibilidade_nanicos",
      "nome": "Sensibilidade com Prior Nanicos (w=0.5)",
      "rotulo": "Sensibilidade (w=0.5)",
      "descricao": "Variação do modelo aplicando combinação convexa (w=0.5) com as medianas históricas do TSE para legendas nanicas.",
      "formula": "y = ModeloOficial + PriorNanicos(w=0.5)",
      "status_regra": "Análise de Sensibilidade",
      "justificativa": "Prior teve ganho nulo no histórico (delta=0), por isso w=0 no oficial; mantido aqui para avaliar sensibilidade a zero espúrio.",
      "is_default": false,
      "previsao_2026": {
        "tabela": [
          {
            "posicao": 1,
            "candidato": "Flávio Bolsonaro",
            "partido": "PL",
            "pct": 45.8,
            "pct_raw": 45.8347,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 40.9,
            "max": 50.7
          },
          {
            "posicao": 2,
            "candidato": "Luiz Inácio Lula da Silva",
            "partido": "PT",
            "pct": 45.5,
            "pct_raw": 45.5278,
            "faixa_media": 2.72,
            "faixa_p80": 4.92,
            "min": 40.6,
            "max": 50.4
          },
          {
            "posicao": 3,
            "candidato": "Ronaldo Caiado",
            "partido": "PSD",
            "pct": 2.7,
            "pct_raw": 2.6394,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 0.2,
            "max": 5.2
          },
          {
            "posicao": 4,
            "candidato": "Augusto Cury",
            "partido": "Avante",
            "pct": 2.7,
            "pct_raw": 2.6389,
            "faixa_media": 1.35,
            "faixa_p80": 2.46,
            "min": 0.2,
            "max": 5.2
          },
          {
            "posicao": 5,
            "candidato": "Renan Santos",
            "partido": "Missão",
            "pct": 2.5,
            "pct_raw": 2.4918,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 1.9,
            "max": 3.1
          },
          {
            "posicao": 6,
            "candidato": "Romeu Zema",
            "partido": "Novo",
            "pct": 0.7,
            "pct_raw": 0.6958,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.1,
            "max": 1.3
          },
          {
            "posicao": 7,
            "candidato": "Samara Martins",
            "partido": "UP",
            "pct": 0.1,
            "pct_raw": 0.0558,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.7
          },
          {
            "posicao": 8,
            "candidato": "Hertz Dias",
            "partido": "PSTU",
            "pct": 0.0,
            "pct_raw": 0.0338,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 9,
            "candidato": "Clariana Barão",
            "partido": "DC",
            "pct": 0.0,
            "pct_raw": 0.0294,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 10,
            "candidato": "Wilson Grassi",
            "partido": "Democrata",
            "pct": 0.0,
            "pct_raw": 0.0273,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 11,
            "candidato": "Edmilson Costa",
            "partido": "PCB",
            "pct": 0.0,
            "pct_raw": 0.0193,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          },
          {
            "posicao": 12,
            "candidato": "Rui Costa Pimenta",
            "partido": "PCO",
            "pct": 0.0,
            "pct_raw": 0.0059,
            "faixa_media": 0.44,
            "faixa_p80": 0.62,
            "min": 0.0,
            "max": 0.6
          }
        ],
        "soma": 100.0
      },
      "top2_destaque": {
        "lula": 45.5,
        "flavio": 45.8,
        "diferenca": 0.3,
        "lider": "Flávio Bolsonaro",
        "vantagem_texto": "Flávio Bolsonaro +0.3 p.p.",
        "erro_margem_stats": {
          "por_ano": {
            "2014": 5.72,
            "2018": 3.58,
            "2022": 4.32
          },
          "media": 4.54,
          "p80": 5.16,
          "max": 5.72
        },
        "empate_tecnico": true,
        "explicacao_empate": "Diferença projetada (0.3 p.p.) é inferior ao P80 do erro da margem histórica (5.2 p.p.) e ao erro máximo (5.7 p.p.), confirmando empate técnico na disputa pela liderança."
      },
      "backtest_expanding": {
        "erros": {
          "2014": 0.9245,
          "2018": 1.3855,
          "2022": 0.5819
        },
        "mae_medio": 0.964,
        "se": 0.2328
      },
      "backtest_loeo": {
        "erros": {
          "2006": 1.3923,
          "2010": 2.1393,
          "2014": 0.8784,
          "2018": 1.2182,
          "2022": 0.5819
        },
        "mae_medio": 1.242,
        "se": 0.2642
      },
      "regra_decisao": {
        "delta_vs_m0": -0.2568,
        "se_delta": 0.0856,
        "status": "Análise de Sensibilidade",
        "justificativa": "Prior teve ganho nulo no histórico (delta=0), por isso w=0 no oficial; mantido aqui para avaliar sensibilidade a zero espúrio."
      }
    }
  },
  "aba2_agregados": {
    "abstencao": {
      "nome": "Abstenção",
      "denominador": "% sobre o total de eleitores aptos",
      "vencedor": "Tendência Linear",
      "projecao_oficial": 22.3,
      "justificativa": "Tendência linear apresenta menor MAE (0,3989 p.p.) vs Persistência (0,9433 p.p.). Delta = -0,5444 p.p. com SE(Delta) = 0,3608 p.p. (|Delta| > SE, sem empate técnico).",
      "contas_desempate": {
        "comparacao": "Tendência Linear vs Persistência",
        "delta": -0.5444,
        "se_delta": 0.3608,
        "empate_tecnico": false,
        "criterio": "Vitória estatística inequívoca da Tendência Linear."
      },
      "metodos_tabela": [
        {
          "metodo": "Persistência (Random Walk)",
          "erro_2014": 1.27,
          "erro_2018": 0.94,
          "erro_2022": 0.62,
          "mae_medio": 0.9433,
          "projecao_2026": 20.9,
          "selecionado": false
        },
        {
          "metodo": "Média Móvel Histórica",
          "erro_2014": 1.955,
          "erro_2018": 2.243,
          "erro_2022": 2.302,
          "mae_medio": 2.1667,
          "projecao_2026": 19.1,
          "selecionado": false
        },
        {
          "metodo": "Tendência Linear",
          "erro_2014": 0.1,
          "erro_2018": 0.397,
          "erro_2022": 0.7,
          "mae_medio": 0.399,
          "projecao_2026": 22.3,
          "selecionado": true
        }
      ]
    },
    "brancos": {
      "nome": "Votos Brancos",
      "denominador": "% sobre o comparecimento",
      "vencedor": "Persistência (Random Walk)",
      "projecao_oficial": 1.6,
      "justificativa": "Persistência obtém menor erro médio (0,9867 p.p.). Média Móvel (0,9969 p.p.) tem Delta = +0,0103 p.p. vs SE = 0,3160 p.p. Configura empate técnico (|Delta| <= SE). Pela regra formal de parcimônia, vence o modelo mais simples (Persistência / 2022).",
      "contas_desempate": {
        "comparacao": "Média Móvel vs Persistência",
        "delta": 0.0103,
        "se_delta": 0.316,
        "empate_tecnico": true,
        "criterio": "Empate técnico (|Delta| <= SE). Vence Persistência por parcimônia pré-registrada."
      },
      "metodos_tabela": [
        {
          "metodo": "Persistência (Random Walk)",
          "erro_2014": 0.71,
          "erro_2018": 1.19,
          "erro_2022": 1.06,
          "mae_medio": 0.9867,
          "projecao_2026": 1.6,
          "selecionado": true
        },
        {
          "metodo": "Média Móvel Histórica",
          "erro_2014": 0.91,
          "erro_2018": 0.583,
          "erro_2022": 1.497,
          "mae_medio": 0.9967,
          "projecao_2026": 2.8,
          "selecionado": false
        },
        {
          "metodo": "Tendência Linear",
          "erro_2014": 0.31,
          "erro_2018": 1.693,
          "erro_2022": 1.615,
          "mae_medio": 1.206,
          "projecao_2026": 2.0,
          "selecionado": false
        }
      ]
    },
    "nulos": {
      "nome": "Votos Nulos",
      "denominador": "% sobre o comparecimento",
      "vencedor": "Persistência (Random Walk)",
      "projecao_oficial": 2.8,
      "justificativa": "Média Móvel (MAE 1,2147 p.p.) vs Persistência (MAE 1,3167 p.p.) apresenta Delta = -0,1019 p.p. com SE(Delta) = 0,1429 p.p. Como |-0,1019| <= 0,1429, ocorre empate técnico. Pela regra de parcimônia do edital, seleciona-se Persistência.",
      "contas_desempate": {
        "comparacao": "Média Móvel vs Persistência",
        "delta": -0.1019,
        "se_delta": 0.1429,
        "empate_tecnico": true,
        "criterio": "Empate técnico (|Delta| <= SE). Vence Persistência por parcimônia pré-registrada."
      },
      "metodos_tabela": [
        {
          "metodo": "Persistência (Random Walk)",
          "erro_2014": 0.29,
          "erro_2018": 0.34,
          "erro_2022": 3.32,
          "mae_medio": 1.3167,
          "projecao_2026": 2.8,
          "selecionado": true
        },
        {
          "metodo": "Média Móvel Histórica",
          "erro_2014": 0.205,
          "erro_2018": 0.477,
          "erro_2022": 2.962,
          "mae_medio": 1.2147,
          "projecao_2026": 5.2,
          "selecionado": false
        },
        {
          "metodo": "Tendência Linear",
          "erro_2014": 0.46,
          "erro_2018": 0.357,
          "erro_2022": 3.38,
          "mae_medio": 1.399,
          "projecao_2026": 3.7,
          "selecionado": false
        }
      ]
    }
  },
  "backtest_por_eleicao": {
    "2014": {
      "ano": 2014,
      "total_candidatos": 11,
      "candidatos": [
        {
          "candidato": "Dilma Rousseff",
          "real_tse": 41.59,
          "pred_m0": 45.93,
          "erro_m0": 4.33,
          "pred_oficial": 42.39,
          "erro_oficial": 0.8
        },
        {
          "candidato": "Aécio Neves",
          "real_tse": 33.55,
          "pred_m0": 26.99,
          "erro_m0": -6.55,
          "pred_oficial": 28.62,
          "erro_oficial": -4.92
        },
        {
          "candidato": "Marina Silva",
          "real_tse": 21.32,
          "pred_m0": 23.98,
          "erro_m0": 2.66,
          "pred_oficial": 23.78,
          "erro_oficial": 2.46
        },
        {
          "candidato": "Luciana Genro",
          "real_tse": 1.55,
          "pred_m0": 1.45,
          "erro_m0": -0.1,
          "pred_oficial": 1.69,
          "erro_oficial": 0.14
        },
        {
          "candidato": "Pastor Everaldo",
          "real_tse": 0.75,
          "pred_m0": 1.08,
          "erro_m0": 0.33,
          "pred_oficial": 1.34,
          "erro_oficial": 0.59
        },
        {
          "candidato": "Eduardo Jorge",
          "real_tse": 0.61,
          "pred_m0": 0.56,
          "erro_m0": -0.04,
          "pred_oficial": 0.83,
          "erro_oficial": 0.22
        },
        {
          "candidato": "Levy Fidelix",
          "real_tse": 0.43,
          "pred_m0": 0.0,
          "erro_m0": -0.43,
          "pred_oficial": 0.27,
          "erro_oficial": -0.16
        },
        {
          "candidato": "Zé Maria",
          "real_tse": 0.09,
          "pred_m0": 0.0,
          "erro_m0": -0.09,
          "pred_oficial": 0.27,
          "erro_oficial": 0.18
        },
        {
          "candidato": "José Maria Eymael",
          "real_tse": 0.06,
          "pred_m0": 0.0,
          "erro_m0": -0.06,
          "pred_oficial": 0.27,
          "erro_oficial": 0.21
        },
        {
          "candidato": "Mauro Iasi",
          "real_tse": 0.05,
          "pred_m0": 0.0,
          "erro_m0": -0.05,
          "pred_oficial": 0.27,
          "erro_oficial": 0.22
        },
        {
          "candidato": "Rui Costa Pimenta",
          "real_tse": 0.01,
          "pred_m0": 0.0,
          "erro_m0": -0.01,
          "pred_oficial": 0.27,
          "erro_oficial": 0.26
        }
      ],
      "mae_m0": 1.3317,
      "mae_oficial": 0.9245
    },
    "2018": {
      "ano": 2018,
      "total_candidatos": 13,
      "candidatos": [
        {
          "candidato": "Jair Bolsonaro",
          "real_tse": 46.03,
          "pred_m0": 40.4,
          "erro_m0": -5.63,
          "pred_oficial": 44.69,
          "erro_oficial": -1.34
        },
        {
          "candidato": "Fernando Haddad",
          "real_tse": 29.28,
          "pred_m0": 27.22,
          "erro_m0": -2.05,
          "pred_oficial": 24.36,
          "erro_oficial": -4.92
        },
        {
          "candidato": "Ciro Gomes",
          "real_tse": 12.47,
          "pred_m0": 12.38,
          "erro_m0": -0.09,
          "pred_oficial": 11.67,
          "erro_oficial": -0.79
        },
        {
          "candidato": "Geraldo Alckmin",
          "real_tse": 4.76,
          "pred_m0": 8.37,
          "erro_m0": 3.61,
          "pred_oficial": 7.88,
          "erro_oficial": 3.12
        },
        {
          "candidato": "João Amoêdo",
          "real_tse": 2.5,
          "pred_m0": 3.21,
          "erro_m0": 0.7,
          "pred_oficial": 3.15,
          "erro_oficial": 0.65
        },
        {
          "candidato": "Cabo Daciolo",
          "real_tse": 1.26,
          "pred_m0": 0.0,
          "erro_m0": -1.26,
          "pred_oficial": 0.0,
          "erro_oficial": -1.26
        },
        {
          "candidato": "Henrique Meirelles",
          "real_tse": 1.2,
          "pred_m0": 2.16,
          "erro_m0": 0.96,
          "pred_oficial": 2.1,
          "erro_oficial": 0.9
        },
        {
          "candidato": "Marina Silva",
          "real_tse": 1.0,
          "pred_m0": 4.09,
          "erro_m0": 3.1,
          "pred_oficial": 4.04,
          "erro_oficial": 3.04
        },
        {
          "candidato": "Alvaro Dias",
          "real_tse": 0.8,
          "pred_m0": 2.17,
          "erro_m0": 1.36,
          "pred_oficial": 2.11,
          "erro_oficial": 1.31
        },
        {
          "candidato": "Guilherme Boulos",
          "real_tse": 0.58,
          "pred_m0": 0.0,
          "erro_m0": -0.58,
          "pred_oficial": 0.0,
          "erro_oficial": -0.58
        },
        {
          "candidato": "Vera Lúcia",
          "real_tse": 0.05,
          "pred_m0": 0.0,
          "erro_m0": -0.05,
          "pred_oficial": 0.0,
          "erro_oficial": -0.05
        },
        {
          "candidato": "José Maria Eymael",
          "real_tse": 0.04,
          "pred_m0": 0.0,
          "erro_m0": -0.04,
          "pred_oficial": 0.0,
          "erro_oficial": -0.04
        },
        {
          "candidato": "João Goulart Filho",
          "real_tse": 0.03,
          "pred_m0": 0.0,
          "erro_m0": -0.03,
          "pred_oficial": 0.0,
          "erro_oficial": -0.03
        }
      ],
      "mae_m0": 1.4964,
      "mae_oficial": 1.3855
    },
    "2022": {
      "ano": 2022,
      "total_candidatos": 11,
      "candidatos": [
        {
          "candidato": "Luiz Inácio Lula da Silva",
          "real_tse": 48.43,
          "pred_m0": 46.88,
          "erro_m0": -1.55,
          "pred_oficial": 45.67,
          "erro_oficial": -2.76
        },
        {
          "candidato": "Jair Bolsonaro",
          "real_tse": 43.2,
          "pred_m0": 40.35,
          "erro_m0": -2.85,
          "pred_oficial": 44.76,
          "erro_oficial": 1.57
        },
        {
          "candidato": "Simone Tebet",
          "real_tse": 4.16,
          "pred_m0": 5.23,
          "erro_m0": 1.08,
          "pred_oficial": 4.03,
          "erro_oficial": -0.13
        },
        {
          "candidato": "Ciro Gomes",
          "real_tse": 3.04,
          "pred_m0": 5.84,
          "erro_m0": 2.79,
          "pred_oficial": 4.52,
          "erro_oficial": 1.48
        },
        {
          "candidato": "Soraya Thronicke",
          "real_tse": 0.51,
          "pred_m0": 1.01,
          "erro_m0": 0.5,
          "pred_oficial": 0.66,
          "erro_oficial": 0.16
        },
        {
          "candidato": "Felipe D'Avila",
          "real_tse": 0.47,
          "pred_m0": 0.69,
          "erro_m0": 0.22,
          "pred_oficial": 0.35,
          "erro_oficial": -0.12
        },
        {
          "candidato": "Padre Kelmon",
          "real_tse": 0.07,
          "pred_m0": 0.0,
          "erro_m0": -0.07,
          "pred_oficial": 0.0,
          "erro_oficial": -0.07
        },
        {
          "candidato": "Léo Péricles",
          "real_tse": 0.05,
          "pred_m0": 0.0,
          "erro_m0": -0.05,
          "pred_oficial": 0.0,
          "erro_oficial": -0.05
        },
        {
          "candidato": "Sofia Manzano",
          "real_tse": 0.04,
          "pred_m0": 0.0,
          "erro_m0": -0.04,
          "pred_oficial": 0.0,
          "erro_oficial": -0.04
        },
        {
          "candidato": "Vera Lúcia",
          "real_tse": 0.02,
          "pred_m0": 0.0,
          "erro_m0": -0.02,
          "pred_oficial": 0.0,
          "erro_oficial": -0.02
        },
        {
          "candidato": "Constituinte Eymael",
          "real_tse": 0.01,
          "pred_m0": 0.0,
          "erro_m0": -0.01,
          "pred_oficial": 0.0,
          "erro_oficial": -0.01
        }
      ],
      "mae_m0": 0.8341,
      "mae_oficial": 0.5819
    }
  }
};
