# Relatório Oficial do Backtest do 2º Turno (Desafio Eleições 2026 FGV EPGE)

**Data de Execução:** 21/10/2026  
**Script Reprodutível:** `scripts/executar_backtest_2t.py`  
**Suíte de Testes:** `tests/test_pipeline_2t.py` (`5 passed`)

---

## 1. Etapa 1 (Aba 1 — Votos Válidos, $K=2$): Seleção do Modelo Base no Expanding Window

Avaliação prospectiva nas 3 eleições de teste (`2014`, `2018`, `2022`), onde $\text{MAE}_{2T} = |\hat{V}_{\text{PT}} - V_{\text{PT}}| = |\hat{V}_{\text{Adv}} - V_{\text{Adv}}|$:

| Modelo Base | MAE 2014 (p.p.) | MAE 2018 (p.p.) | MAE 2022 (p.p.) | **MAE Médio Expanding (p.p.)** | EP (p.p.) | $\bar{\Delta}$ vs. `M0_2T` | $\text{EP}(\Delta)$ | Supera `M0_2T` ($> 1\text{ EP}$)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `M0_2T` (Média Simples Última de cada Instituto) | 0,6315 | 1,8217 | 0,2920 | 0,9151 | 0,4638 | 0,0000 | 0,0000 | Baseline |
| `M1_2T (h=3)` (Recência + $\sqrt{N}$) | 0,7660 | 0,9567 | 0,4509 | 0,7245 | 0,1475 | -0,1905 | 0,3373 | Não |
| `M1_2T (h=5)` (Recência + $\sqrt{N}$) | 0,4950 | 1,4243 | 0,4153 | 0,7782 | 0,3239 | -0,1369 | 0,1503 | Não |
| `M1_2T (h=7)` (Recência + $\sqrt{N}$) | 0,3125 | 1,6665 | 0,4128 | 0,7972 | 0,4356 | -0,1178 | 0,1283 | Não |
| **`M2_2T (sigma0=1.5)` (Peso Inverso Erro 1T)** | **0,5588** | **1,2912** | **0,0965** | **0,6489** | **0,3478** | **-0,2662** | **0,1368** | **SIM ($\mathbf{1,95\text{ EP}}$)** |
| `M2_2T (sigma0=2.5)` (Peso Inverso Erro 1T) | 0,5637 | 1,2724 | 0,1126 | 0,6496 | 0,3376 | -0,2655 | 0,1455 | SIM ($1,82\text{ EP}$) |

- **Vencedor Formal da Etapa 1:** **`M2_2T (sigma0=1.5)`**, que pondera a última pesquisa de cada instituto no 2º turno pelo inverso do erro quadrático cometido pelo próprio instituto 21 dias antes na margem do 1º turno ($w_j = \frac{1}{(e_{j, 1T}^{\text{margem}/2})^2 + 1,5^2}$). Reduz o MAE médio de `0,9151 p.p.` para **`0,6489 p.p.`** ($\bar{\Delta} = -0,2662 < -\text{EP}(\Delta) = -0,1368$), vencendo `M0_2T` nas 3 eleições de teste!

---

## 2. Etapa 2 (Aba 1): Avaliação Isolada de Ajustes sobre `M2_2T (sigma0=1.5)`

| Configuração / Ajuste | MAE 2014 | MAE 2018 | MAE 2022 | **MAE Médio (p.p.)** | $\bar{\Delta}$ vs. Base | $\text{EP}(\Delta)$ | Aprovado ($> 1\text{ EP}$)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`M2_2T (sigma0=1.5)` (Base Puro)** | **0,5588** | **1,2912** | **0,0965** | **0,6489** | **0,0000** | **0,0000** | **Vencedor** |
| `+ Persistência 1T (rho=OLS_treino)` | 0,2929 | 1,4025 | 0,0135 | 0,5696 | -0,0792 | 0,1089 | Empate Técnico ($\implies$ Parcimônia) |
| `+ Persistência 1T (rho=0.20)` | 0,5131 | 1,4427 | 0,3396 | 0,7651 | +0,1163 | 0,0852 | Não |
| `+ Persistência 1T (rho=0.35)` | 1,3170 | 1,5564 | 0,5218 | 1,1318 | +0,4829 | 0,1452 | Não |
| `+ Viés Comum 2T (k_mu=1)` | 0,4231 | 1,5326 | 0,0315 | 0,6624 | +0,0136 | 0,1158 | Não |
| `+ Viés Comum 2T (k_mu=3)` | 0,4774 | 1,4522 | 0,0501 | 0,6599 | +0,0110 | 0,0756 | Não |
| `+ Shrinkage Prior 1T (lambda=0.10)` | 1,6104 | 0,9897 | 0,2382 | 0,9461 | +0,2973 | 0,3983 | Não |
| `+ Shrinkage Prior 1T (lambda=0.25)` | 3,1878 | 0,5376 | 0,7403 | 1,4885 | +0,8397 | 0,9814 | Não |

---

## 3. Validação Complementar LOEO (`2006, 2010, 2014, 2018, 2022`, $n=5$)

| Modelo | 2006 | 2010 | 2014 | 2018 | 2022 | **MAE Médio LOEO (p.p.)** | EP LOEO |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `M0_2T` | 0,8821 | 0,2470 | 0,6315 | 1,8217 | 0,2920 | 0,7749 | 0,2863 |
| `M1_2T (h=3)` | 0,5176 | 0,1657 | 0,7660 | 0,9567 | 0,4509 | 0,5714 | 0,1357 |
| `M1_2T (h=5)` | 0,4673 | 0,2166 | 0,4950 | 1,4243 | 0,4153 | 0,6037 | 0,2108 |
| **`M2_2T (sigma0=1.5)`** | **0,4397** | **0,0327** | **0,5588** | **1,2912** | **0,0965** | **0,4838** | **0,2250** |
| `M2_2T (sigma0=2.5)` | 0,4611 | 0,0163 | 0,5637 | 1,2724 | 0,1126 | 0,4852 | 0,2219 |

*(Nota: `M2_2T (sigma0=1.5)` vence `M0_2T` em **todas as 5 eleições presidenciais históricas** de 2006 a 2022!)*

---

## 4. Tabela de Sensibilidade para o 2º Turno de 2026 (Corte Parcial: 21/10/2026)

| Especificação | Flávio Bolsonaro (Contínuo %) | Lula (Contínuo %) | **Flávio (Arred 1 casa)** | **Lula (Arred 1 casa)** |
| :--- | :---: | :---: | :---: | :---: |
| `M0_2T` (Média Simples Última de cada Instituto) | 51,32% | 48,68% | **51,3%** | **48,7%** |
| `M1_2T (h=3 dias)` | 51,09% | 48,91% | **51,1%** | **48,9%** |
| `M1_2T (h=5 dias)` | 51,16% | 48,84% | **51,2%** | **48,8%** |
| `M1_2T (h=7 dias)` | 51,20% | 48,80% | **51,2%** | **48,8%** |
| **`M2_2T (sigma0=1.5)` — Vencedor Formal Etapa 1** | **51,29%** | **48,71%** | **51,3%** | **48,7%** |
| `M2_2T (sigma0=1.5)` (incluindo Gerp no peso 1T) | 51,81% | 48,19% | **51,8%** | **48,2%** |
| `M2_2T (sigma0=1.5) + Persistência 1T (rho_OLS=0.15)` | 51,67% | 48,33% | **51,7%** | **48,3%** |
| `M2_2T (sigma0=1.5) + Persistência 1T (rho=0.20)` | 51,78% | 48,22% | **51,8%** | **48,2%** |
| `M0_2T + Persistência 1T (rho=0.20)` | 51,83% | 48,17% | **51,8%** | **48,2%** |
| Prior Estrutural de Transferência por Blocos 1T | 51,50% | 48,50% | **51,5%** | **48,5%** |
