# Relatório Oficial do Backtest do 2º Turno (Desafio Eleições 2026 FGV EPGE)

> **Arquivo gerado 100% automaticamente por `scripts/executar_backtest_2t.py` (sem edição manual).**

- **Protocolo:** `protocolo/PRE_REGISTRO_2T.md` (Protocolo do 2º turno definido em 21/10/2026)
- **Script Reprodutível:** `scripts/executar_backtest_2t.py`
- **Suíte de Testes:** `tests/test_pipeline_2t.py`

---

## 1. Etapa 1 (Aba 1 — Votos Válidos, $K=2$): Seleção do Modelo Base no Expanding Window

Avaliação prospectiva nas 3 eleições de teste (`2014`, `2018`, `2022`), onde $\text{MAE}_{2T} = \lvert \hat{V}_{\text{PT}} - V_{\text{PT}} \rvert = \lvert \hat{V}_{\text{Adv}} - V_{\text{Adv}} \rvert$:

| Modelo Base | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio Expanding (p.p.)** | EP (p.p.) | Diferença vs. M0_2T (p.p.) | EP(Diferença) | Supera M0_2T (> 1 EP)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `M0_2T` | 0,6315 | 1,8217 | 0,2920 | 0,9151 | 0,4638 | 0,0000 | 0,0000 | Baseline |
| `M1_2T (h=3)` | 0,7660 | 0,9567 | 0,4509 | 0,7245 | 0,1475 | -0,1905 | 0,3373 | Não |
| `M1_2T (h=5)` | 0,4950 | 1,4243 | 0,4153 | 0,7782 | 0,3239 | -0,1369 | 0,1503 | Não |
| `M1_2T (h=7)` | 0,3125 | 1,6665 | 0,4128 | 0,7972 | 0,4356 | -0,1178 | 0,1283 | Não |
| **`M2_2T (sigma0=1.5)`** | **0,5588** | **1,2912** | **0,0965** | **0,6489** | **0,3478** | **-0,2662** | **0,1368** | **SIM (1,95 EP)** |
| `M2_2T (sigma0=2.5)` | 0,5637 | 1,2724 | 0,1126 | 0,6496 | 0,3376 | -0,2655 | 0,1455 | SIM (1,82 EP) |

- **Vencedor Formal da Etapa 1 (Regra de 1 EP + Parcimônia):** **`M2_2T (sigma0=1.5)`**.

---

## 2. Etapa 2 (Aba 1): Avaliação Isolada de Ajustes sobre `M2_2T (sigma0=1.5)`

| Configuração / Ajuste | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio (p.p.)** | EP (p.p.) | Diferença vs. Base (p.p.) | EP(Diferença) | Aprovado (> 1 EP)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`M2_2T (sigma0=1.5) (Base Puro)`** | **0,5588** | **1,2912** | **0,0965** | **0,6489** | **0,3478** | **0,0000** | **0,0000** | **Vencedor (Base)** |
| `+ Persistência 1T (rho=0.20)` | 0,5131 | 1,4427 | 0,3396 | 0,7651 | 0,3425 | +0,1163 | 0,0852 | Não |
| `+ Persistência 1T (rho=0.35)` | 1,3170 | 1,5564 | 0,5218 | 1,1318 | 0,3127 | +0,4829 | 0,1452 | Não |
| `+ Persistência 1T (rho=OLS_treino)` | 0,2929 | 1,4025 | 0,0135 | 0,5696 | 0,4242 | -0,0792 | 0,1089 | Empate Técnico (< 1 EP) |
| `+ Viés Comum 2T (k_mu=1)` | 0,4231 | 1,5326 | 0,0315 | 0,6624 | 0,4496 | +0,0136 | 0,1158 | Não |
| `+ Viés Comum 2T (k_mu=3)` | 0,4774 | 1,4522 | 0,0501 | 0,6599 | 0,4149 | +0,0110 | 0,0756 | Não |
| `+ Shrinkage Prior 1T tau médio (lambda=0.10)` | 1,6104 | 0,9897 | 0,2382 | 0,9461 | 0,3967 | +0,2973 | 0,3983 | Não |
| `+ Shrinkage Prior 1T tau médio (lambda=0.25)` | 3,1878 | 0,5376 | 0,7403 | 1,4885 | 0,8516 | +0,8397 | 0,9814 | Não |
| `+ Shrinkage Prior 1T tau mediano (lambda=0.10)` | 1,6104 | 1,6188 | 0,1169 | 1,1154 | 0,4992 | +0,4665 | 0,3057 | Não |
| `+ Shrinkage Prior 1T tau mediano (lambda=0.25)` | 3,1878 | 2,1102 | 0,4372 | 1,9117 | 0,8002 | +1,2629 | 0,6969 | Não |

- **Modelo Final Selecionado para a Aba 1:** **`M2_2T (sigma0=1.5) (Puro)`**.

---

## 3. Validação Complementar LOEO (`2006, 2010, 2014, 2018, 2022`, $n=5$)

| Modelo | 2006 | 2010 | 2014 | 2018 | 2022 | **MAE Médio LOEO (p.p.)** | EP LOEO |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `M0_2T` | 0,8821 | 0,2470 | 0,6315 | 1,8217 | 0,2920 | 0,7749 | 0,2863 |
| `M1_2T (h=3)` | 0,5176 | 0,1657 | 0,7660 | 0,9567 | 0,4509 | 0,5714 | 0,1357 |
| `M1_2T (h=5)` | 0,4673 | 0,2166 | 0,4950 | 1,4243 | 0,4153 | 0,6037 | 0,2108 |
| `M1_2T (h=7)` | 0,4393 | 0,2375 | 0,3125 | 1,6665 | 0,4128 | 0,6137 | 0,2657 |
| **`M2_2T (sigma0=1.5)`** | **0,4397** | **0,0327** | **0,5588** | **1,2912** | **0,0965** | **0,4838** | **0,2250** |
| `M2_2T (sigma0=2.5)` | 0,4611 | 0,0163 | 0,5637 | 1,2724 | 0,1126 | 0,4852 | 0,2219 |
| `M0_2T + Persist 1T (rho=0.20)` | 0,1549 | 0,7454 | 0,4579 | 2,1828 | 0,4952 | 0,8072 | 0,3564 |
| `M0_2T + Persist 1T (rho=0.35)` | 0,9325 | 1,4898 | 1,2749 | 2,4536 | 0,6476 | 1,3597 | 0,3091 |
| `M2_2T (sigma0=1.5) + Persist 1T (rho=0.20)` | 0,2892 | 0,9552 | 0,5131 | 1,4427 | 0,3396 | 0,7080 | 0,2180 |
| `M2_2T (sigma0=1.5) + Persist 1T (rho=0.35)` | 0,8359 | 1,6471 | 1,3170 | 1,5564 | 0,5218 | 1,1757 | 0,2157 |

---

## 4. Parâmetros de Transferência Estrutural $1\text{T} \to 2\text{T}$ ($\tau_t$ por Eleição)

Fração aparente dos votos de terceiros colocados no 1º turno capturada pelo candidato do PT no 2º turno, $\tau_t = \frac{V_{\text{PT}, 2T, t} - V_{\text{PT}, 1T, t}}{100 - V_{\text{PT}, 1T, t} - V_{\text{Adv}, 1T, t}}$:

| Eleição | PT 1T (%) | Adv 1T (%) | Terceiros 1T (%) | PT 2T (%) | Adv 2T (%) | $\Delta$ PT ($2\text{T}-1\text{T}$) | $\Delta$ Adv ($2\text{T}-1\text{T}$) | **$\tau_t$ (PT)** | Observação |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 2006 | 48,61% | 41,64% | 9,75% | 60,83% | 39,17% | +12,22 p.p. | -2,47 p.p. | **1,2530** | Outlier ($\tau > 1$): adversário (Alckmin) perdeu votos do 1T para o 2T |
| 2010 | 46,91% | 32,61% | 20,48% | 56,05% | 43,95% | +9,14 p.p. | +11,34 p.p. | **0,4464** | Transferência regular ($0 < \tau < 1$) |
| 2014 | 41,59% | 33,55% | 24,86% | 51,64% | 48,36% | +10,05 p.p. | +14,81 p.p. | **0,4042** | Transferência regular ($0 < \tau < 1$) |
| 2018 | 29,28% | 46,03% | 24,69% | 44,87% | 55,13% | +15,59 p.p. | +9,10 p.p. | **0,6314** | Transferência regular ($0 < \tau < 1$) |
| 2022 | 48,43% | 43,20% | 8,37% | 50,90% | 49,10% | +2,47 p.p. | +5,90 p.p. | **0,2954** | Transferência regular ($0 < \tau < 1$) |

- **Média histórica ($\bar{\tau}_{2006\text{--}2022}$):** `0,6061` (inflada pelo outlier de 2006, $\tau_{2006} = 1,2530$, quando Geraldo Alckmin caiu de 41,64% no 1º turno para 39,17% no 2º turno).
- **Mediana histórica ($\tilde{\tau}_{2006\text{--}2022}$):** `0,4464` (estimador robusto ao outlier de 2006).

---

## 5. Backtest da Aba 2 no 2º Turno (Ancorado no 1º Turno da Mesma Eleição)

### 5.1. Abstenção (% do Eleitorado Apto)

| Método | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio (p.p.)** | EP (p.p.) | Diferença vs. Zero_Delta (p.p.) | EP(Diferença) | Supera Zero_Delta (> 1 EP)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Zero_Delta (y2=y1)`** | **1,7077** | **0,9716** | **0,3646** | **1,0146** | **0,3883** | **0,0000** | **0,0000** | **Vencedor (Parcimônia)** |
| `Persistencia_Delta` | 1,6698 | 0,7361 | 1,3362 | 1,2474 | 0,2732 | +0,2327 | 0,3738 | Não |
| `Media_Delta` | 1,1017 | 1,4706 | 2,4391 | 1,6705 | 0,3988 | +0,6558 | 0,7778 | Não |
| `Ratio_Media` | 1,3969 | 1,7943 | 2,7526 | 1,9813 | 0,4024 | +0,9666 | 0,7824 | Não |
| `BottomUp_UF_Gov2T` | 1,7957 | 0,9569 | 1,3764 | 1,3764 | 0,2421 | +0,3617 | 0,3264 | Não |

- **Vencedor Formal para `abstencao`:** **`Zero_Delta (y2=y1)`**.

### 5.2. Votos Brancos (% dos Votos Totais)

| Método | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio (p.p.)** | EP (p.p.) | Diferença vs. Zero_Delta (p.p.) | EP(Diferença) | Supera Zero_Delta (> 1 EP)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Zero_Delta (y2=y1)`** | **2,1343** | **0,5024** | **0,1643** | **0,9337** | **0,6082** | **0,0000** | **0,0000** | **Vencedor (Parcimônia)** |
| `Persistencia_Delta` | 1,3058 | 1,6319 | 0,3381 | 1,0919 | 0,3885 | +0,1583 | 0,5653 | Não |
| `Media_Delta` | 1,0154 | 0,9550 | 1,0543 | 1,0082 | 0,0289 | +0,0746 | 0,6100 | Não |
| `Ratio_Media` | 0,6364 | 0,6765 | 0,4417 | 0,5849 | 0,0725 | -0,3488 | 0,5753 | Empate Técnico (< 1 EP) |

- **Vencedor Formal para `brancos`:** **`Zero_Delta (y2=y1)`**.

### 5.3. Votos Nulos (% dos Votos Totais)

| Método | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio (p.p.)** | EP (p.p.) | Diferença vs. Zero_Delta (p.p.) | EP(Diferença) | Supera Zero_Delta (> 1 EP)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Zero_Delta (y2=y1)`** | **1,1690** | **1,2850** | **0,3435** | **0,9325** | **0,2964** | **0,0000** | **0,0000** | **Vencedor (Parcimônia)** |
| `Persistencia_Delta` | 0,0601 | 2,4540 | 0,9415 | 1,1519 | 0,6990 | +0,2194 | 0,6843 | Não |
| `Media_Delta` | 0,1300 | 2,3674 | 0,8340 | 1,1105 | 0,6605 | +0,1780 | 0,6320 | Não |
| `Ratio_Media` | 0,0904 | 2,4585 | 0,6002 | 1,0497 | 0,7196 | +0,1172 | 0,6539 | Não |

- **Vencedor Formal para `nulos`:** **`Zero_Delta (y2=y1)`**.

### 5.4. Limitações da Aba 2: Share do Eleitorado com 2º Turno de Governador (2006–2022 vs. 2026)

Em 2026, apenas **6 Unidades da Federação** (`AC, AM, DF, ES, RN, TO`) têm disputa de 2º turno para Governador, o que corresponde a apenas **7,92%** do eleitorado nacional apto, contra uma faixa histórica de **14,36% a 62,97%** entre 2006 e 2022 (média histórica de **41,56%**):

| Eleição | Nº UFs com Gov 2T | UFs com Gov 2T | Share Eleitorado **COM** Gov 2T (%) | Share Eleitorado **SEM** Gov 2T (%) | $\Delta$ Abst COM Gov 2T (p.p.) | $\Delta$ Abst SEM Gov 2T (p.p.) | $\Delta$ Abst Nacional (p.p.) |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 2006 | 10 | `GO, MA, PA, PB, PE, PR, RJ, RN, RS, SC` | 41,53% | 58,47% | +2,15 | +2,31 | +2,24 |
| 2010 | 9 | `AL, AP, DF, GO, PA, PB, PI, RO, RR` | 14,36% | 85,64% | +3,89 | +3,29 | +3,38 |
| 2014 | 15 | `AC, AM, AP, CE, DF, GO, MS, PA, PB, RJ, RN, RO, RR, RS, TO` | 35,67% | 64,33% | +2,22 | +1,43 | +1,71 |
| 2018 | 14 | `AM, AP, DF, MG, MS, PA, RJ, RN, RO, RR, RS, SC, SE, SP` | 62,97% | 37,03% | +0,83 | +1,22 | +0,97 |
| 2022 | 12 | `AL, AM, BA, ES, MS, PB, PE, RO, RS, SC, SE, SP` | 53,26% | 46,74% | -0,47 | -0,24 | -0,36 |
| **2026** | **6** | `AC, AM, DF, ES, RN, TO` | **7,92%** | **92,08%** | — | — | — |

- **Análise de Limitação Estrutural:** Entre 2006 e 2022, a fração média do eleitorado nacional com disputa simultânea para Governador no 2º turno foi de **`41,56%`** (mínimo anterior de `14,36%` em 2010 e máximo de `62,97%` em 2018), e a variação média da abstenção foi de `+1,72 p.p.` nas UFs com 2º turno estadual vs. `+1,60 p.p.` nas UFs sem disputa estadual. Em 2026, **`92,08%`** do eleitorado nacional vai às urnas apenas para Presidente (share com Gov 2T = **`7,92%`**, o menor da série histórica). Caso a ausência de campanha estadual desmobilize eleitores nos estados já decididos no 1º turno, a regra `Zero_Delta` (`21,1%`) pode subestimar ligeiramente a abstenção do 2º turno.

---

## 6. Tabela de Sensibilidade para o 2º Turno de 2026 (Corte Parcial: 21/10/2026)

| Especificação | Flávio Bolsonaro (Contínuo %) | Lula (Contínuo %) | **Flávio (Arred 1 casa)** | **Lula (Arred 1 casa)** |
| :--- | :---: | :---: | :---: | :---: |
| M0_2T (Média Simples Última de cada Instituto) | 51,32% | 48,68% | **51,3%** | **48,7%** |
| M1_2T (h=3 dias, Recência + Raiz Amostra) | 51,09% | 48,91% | **51,1%** | **48,9%** |
| M1_2T (h=5 dias, Recência + Raiz Amostra) | 51,16% | 48,84% | **51,2%** | **48,8%** |
| M1_2T (h=7 dias, Recência + Raiz Amostra) | 51,20% | 48,80% | **51,2%** | **48,8%** |
| M2_2T (sigma0=1.5, Peso Inverso Erro 1T) | 51,29% | 48,71% | **51,3%** | **48,7%** |
| M2_2T (sigma0=2.5, Peso Inverso Erro 1T) | 51,31% | 48,69% | **51,3%** | **48,7%** |
| M0_2T + Persistência 1T (rho=0.20) | 51,83% | 48,17% | **51,8%** | **48,2%** |
| M2_2T (sigma0=1.5) + Persistência 1T (rho=0.20) | 51,78% | 48,22% | **51,8%** | **48,2%** |
| M2_2T (sigma0=1.5) + Persistência 1T (rho_OLS=0.15) | 51,67% | 48,33% | **51,7%** | **48,3%** |
| Prior transferência com tau médio (tau=0.6061) | 50,10% | 49,90% | **50,1%** | **49,9%** |
| Prior transferência com tau mediano (tau=0.4464) | 51,35% | 48,65% | **51,4%** | **48,6%** |
| **>>> MODELO OFICIAL SELECIONADO (M2_2T (sigma0=1.5) (Puro))** | **51,29%** | **48,71%** | **51,3%** | **48,7%** |

### 6.1. Resumo das Projeções da Aba 2 para 2026

| Variável (Aba 2) | Oficial 1º Turno 2026 (%) | Método Vencedor (Backtest) | Projeção Contínua 2T (%) | **Previsão Oficial 2T (1 casa)** |
| :--- | :---: | :--- | :---: | :---: |
| **Abstenção** | 21,08% | `Zero_Delta (y2=y1)` | 21,08% | **21,1%** |
| **Votos brancos** | 1,84% | `Zero_Delta (y2=y1)` | 1,84% | **1,8%** |
| **Votos nulos** | 2,93% | `Zero_Delta (y2=y1)` | 2,93% | **2,9%** |

