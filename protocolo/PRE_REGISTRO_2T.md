# PRE-REGISTRO METODOLOGICO — 2o TURNO: PREVISAO ELEITORAL PRESIDENCIAL 2026

**Data de Definicao:** 21/10/2026  
**Desafio:** Estatistica e Econometria, FGV EPGE — 2o Turno (25/10/2026)  
**Status:** Protocolo do 2o turno (definido em 21/10/2026)

---

## 1. Objetivo, Escopo e Funcao Perda no 2o Turno ($K = 2$)

O objetivo e prever o resultado oficial do **2o turno da Eleicao Presidencial de 2026 (Brasil)**, a ser realizado em **25/10/2026**, com base exclusivamente em informacoes publicas disponiveis ate o horario de corte e nos resultados oficiais do 1o turno apurados pelo TSE em 04/10/2026.

### Entregaveis Oficiais (Edital 2o Turno):
1. **Aba 1 (`Candidatos`):** Previsao pontual de votos validos (%) para os 2 candidatos finalistas, somando exatamente `100,0%` com 1 casa decimal:
   - `Flávio Bolsonaro` (`PL`)
   - `Luiz Inácio Lula da Silva` (`PT`)
   - Linha `Total` (`100,0%`)
2. **Aba 2 (`Adicionais`):** Previsao pontual com 1 casa decimal para:
   - `Abstenção` (% sobre o eleitorado apto)
   - `Votos brancos` (% sobre o total de votos registrados na urna / comparecimento)
   - `Votos nulos` (% sobre o total de votos registrados na urna / comparecimento)

### Identidade Exata da Funcao Objetivo no 2o Turno:
Como $K = 2$ e $\hat{V}_{\text{Flávio}} + \hat{V}_{\text{Lula}} = V_{\text{Flávio}} + V_{\text{Lula}} = 100\%$, o Erro Absoluto Medio (MAE) da Aba 1 reduz-se exatamente ao erro absoluto de um unico candidato e a metade do erro da margem:
$$\text{MAE}_{2T} = \frac{1}{2} \sum_{k=1}^{2} \lvert \hat{V}_k - V_k \rvert = \lvert \hat{V}_{\text{Lula}} - V_{\text{Lula}} \rvert = \lvert \hat{V}_{\text{Flávio}} - V_{\text{Flávio}} \rvert = \frac{1}{2} \left\lvert (\hat{V}_{\text{Flávio}} - \hat{V}_{\text{Lula}}) - (V_{\text{Flávio}} - V_{\text{Lula}}) \right\rvert$$

---

## 2. Horario de Corte dos Dados

- **Data e Horario de Corte das Pesquisas:** Sabado, **24/10/2026, as 20h00 BRT** (`2026-10-24T20:00:00-03:00`), respeitando o prazo limite de submissao no Eclass (24/10/2026 as 22h00 BRT).
- **Janela do 2o Turno:** Pesquisas nacionais estimuladas de 2o turno realizadas e divulgadas apos o 1o turno (de `05/10/2026` ate `24/10/2026` as 20h00 BRT).

---

## 3. Protocolo Sequencial em 2 Etapas para Votos Validos ($K = 2$)

Mantendo estrita continuidade metodologica com o 1o turno, adota-se o **protocolo sequencial em 2 etapas** avaliado prospectivamente via **Expanding Window** ($n = 3$: 2014 treinado em 2006–2010; 2018 treinado em 2006–2014; 2022 treinado em 2006–2018) e auditado via **Leave-One-Election-Out (LOEO, $n = 5$: 2006–2022)**, sob a regra formal de parcimonia: um modelo/ajuste mais complexo $A$ so supera $B$ se $\bar{\Delta} = \text{MAE}_A - \text{MAE}_B \lt -\text{SE}(\Delta)$.

### Etapa 1: Selecao do Agregador Base de 2o Turno ($M^*_{2T}$)
1. **`M0_2T` (Baseline de Parcimonia):**
   - Media simples da ultima pesquisa de 2o turno divulgada por cada instituto na janela do 2o turno, convertida em votos validos ($\hat{v}_{j, k} = \frac{P_{j, k}}{P_{j, 1} + P_{j, 2}} \times 100$).
   - 0 hiperparametros livres.
2. **`M1_2T` (Media Ponderada por Recencia e Amostra):**
   - Ponderacao por tamanho amostral e decaimento exponencial na janela curta de 21 dias do 2o turno:
     $$w_{i} = \sqrt{N_i} \cdot 2^{-\Delta t_i / h}, \quad h \in \{3, 5, 7\}\text{ dias}$$
3. **`M2_2T` (Ponderacao pela Precisao Empirica do Instituto no 1o Turno da Mesma Eleicao):**
   - No 2o turno, o erro observado de cada instituto $j$ no 1o turno realizado 21 dias antes fornece uma medida direta de calibracao amostral no proprio ciclo eleitoral. Define-se o semi-erro da margem Top-2 no 1o turno:
     $$e_{j, 1T}^{\text{margem}/2} = \frac{(\hat{v}_{j, \text{PT}, 1T} - \hat{v}_{j, \text{Adv}, 1T}) - (v_{\text{PT}, 1T}^{\text{TSE}} - v_{\text{Adv}, 1T}^{\text{TSE}})}{2}$$
   - O peso da ultima pesquisa de cada instituto $j$ no 2o turno e inversamente proporcional ao erro quadratico no 1o turno regularizado por $\sigma_0^2$:
     $$w_{j, 2T} = \frac{1}{\left(e_{j, 1T}^{\text{margem}/2}\right)^2 + \sigma_0^2}, \quad \sigma_0 \in \{1.5, \, 2.5\}\text{ p.p.}$$
   - Institutos sem pesquisa na reta final do 1o turno recebem a mediana de $\lvert e_{1T}^{\text{margem}/2} \rvert$ dos institutos avaliados naquela eleicao.

### Etapa 2: Avaliacao Individual e Isolada de Ajustes Opcionais sobre $M^*_{2T}$
Sobre o agregador base vencedor $M^*_{2T}$, avalia-se cada ajuste isoladamente (exigindo $\bar{\Delta} \lt -\text{SE}(\Delta)$ para ativacao):
1. **Ajuste 1 — Persistencia Parcial do Erro do 1o Turno (Correcao Intra-Ciclo de House Effect, $\rho$):**
   - Corrige-se a pesquisa de 2o turno de cada instituto $j$ descontando uma fracao amortecida $\rho$ do seu semi-erro na margem do 1o turno:
     $$\hat{v}_{j, \text{PT}, 2T}^{\text{corr}} = \hat{v}_{j, \text{PT}, 2T} - \rho \cdot e_{j, 1T}^{\text{margem}/2}, \quad \rho \in \{0.20, \, 0.35\}$$
   - Alternativamente, avalia-se $\hat{\rho}_{\text{OLS}}$ estimado por minimos quadrados ordinarios exclusivamente nas eleicoes de treino ($e_{j, \text{PT}, 2T} = \rho \cdot e_{j, 1T}^{\text{margem}/2}$).
2. **Ajuste 2 — Correcao de Vies Comum Historico de 2o Turno ($k_\mu$):**
   - Desconta-se o vies comum medio historico dos 2os turnos anteriores com shrinkage Bayesiano:
     $$\hat{\mu}_{\text{PT}, 2T} = \frac{N_{\text{treino}}}{N_{\text{treino}} + k_\mu} \cdot \bar{e}_{\text{PT}, 2T}^{\text{treino}}, \quad k_\mu \in \{1, \, 3\}$$
3. **Ajuste 3 — Shrinkage com Prior Estrutural de Transferencia de Votos do 1o Turno ($\lambda$):**
   - Combina-se a agregacao das pesquisas de 2o turno com o prior estrutural de transferencia dos votos validos do 1o turno ($p_{2T}^{\text{prior}} = v_{\text{PT}, 1T} + \tau \cdot v_{\text{Terceiros}, 1T}$, avaliado tanto com $\tau$ medio quanto com $\tau$ mediano nos anos de treino, dado que 2006 apresenta $\tau = 1{,}2530 \gt 1$ porque o adversario perdeu votos entre o 1o e o 2o turno):
     $$\hat{p}_{\text{PT}, 2T} = (1 - \lambda) \cdot \hat{p}_{\text{PT}, 2T}^{\text{pesq}} + \lambda \cdot p_{2T}^{\text{prior}}, \quad \lambda \in \{0.10, \, 0.25\}$$

---

## 4. Modelagem da Aba 2 (Abstencao, Votos Brancos e Votos Nulos no 2o Turno)

Diferentemente do 1o turno, no 2o turno ja conhecemos os valores oficiais realizados 21 dias antes no 1o turno da mesma eleicao ($y_{1T, t}^{\text{TSE}}$). Todos os modelos candidatos da Aba 2 sao ancorados em $y_{1T, t}^{\text{TSE}}$ e avaliados no Expanding Window (2014, 2018, 2022) sob a mesma regra de desempate ($\lvert \bar{\Delta} \rvert \le \text{SE}(\Delta) \implies$ modelo mais simples):

1. **`Zero_Delta` (Persistencia Direta do 1o Turno — Baseline de Parcimonia):**
   $$\hat{y}_{2T, t} = y_{1T, t}^{\text{TSE}} \quad (\Delta = 0\text{, 0 parametros estimados})$$
2. **`Persistencia_Delta` (Persistencia da Variacao $1\text{T} \to 2\text{T}$ da Eleicao Anterior):**
   $$\hat{y}_{2T, t} = y_{1T, t}^{\text{TSE}} + (y_{2T, t-1}^{\text{TSE}} - y_{1T, t-1}^{\text{TSE}})$$
3. **`Media_Delta` (Media Historica da Variacao Aditiva $1\text{T} \to 2\text{T}$):**
   $$\hat{y}_{2T, t} = y_{1T, t}^{\text{TSE}} + \frac{1}{\lvert E_{\text{treino}} \rvert} \sum_{s \in E_{\text{treino}}} (y_{2T, s}^{\text{TSE}} - y_{1T, s}^{\text{TSE}})$$
4. **`Ratio_Media` (Escala Multiplicativa Historica $2\text{T} / 1\text{T}$):**
   $$\hat{y}_{2T, t} = y_{1T, t}^{\text{TSE}} \times \left[ \frac{1}{\lvert E_{\text{treino}} \rvert} \sum_{s \in E_{\text{treino}}} \left(\frac{y_{2T, s}^{\text{TSE}}}{y_{1T, s}^{\text{TSE}}}\right) \right]$$
   *(Especialmente adequado para Votos Brancos, cujo nivel base caiu ao longo do tempo e cuja queda proporcional no 2o turno ocorreu em 100% das eleicoes historicas).*
5. **`BottomUp_UF_Gov2T` (Decomposicao Estadual por Presenca de 2o Turno para Governador — especifico para Abstencao):**
   - Projeta a variacao de abstencao separadamente para UFs com disputa de 2o turno para Governador ($\text{Gov2T}_{u, t} = 1$) e UFs com Governador ja decidido no 1o turno ($\text{Gov2T}_{u, t} = 0$), agregando nacionalmente pelo peso do eleitorado apto de cada UF.

### 4.1. Limitacoes da Aba 2: Share do Eleitorado com 2o Turno de Governador (2026 vs. 2006–2022)
- Em 2026, apenas **6 UFs** (`AC, AM, DF, ES, RN, TO`) possuem disputa de 2o turno para Governador, representando apenas **7,92%** do eleitorado nacional apto (`92,08%` sem disputa estadual), ante uma media historica de **41,56%** no ciclo 2006–2022 (`2006: 41,53% [10 UFs]`, `2010: 14,36% [9 UFs]`, `2014: 35,67% [15 UFs]`, `2018: 62,97% [14 UFs]`, `2022: 53,26% [12 UFs]`).
- Embora o modelo `BottomUp_UF_Gov2T` nao supere `Zero_Delta` em mais de 1 erro-padrao no backtest historico ($n=3$), o fato de 2026 apresentar o menor percentual da serie historica de eleitores com campanha estadual ativa no 2o turno constitui uma limitacao estrutural documentada para a projecao de abstencao.

