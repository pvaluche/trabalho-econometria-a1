# PRE-REGISTRO METODOLOGICO: PREVISAO ELEITORAL PRESIDENCIAL 2026

**Data de Congelamento:** 02/10/2026  
**Desafio:** Estatistica e Econometria, FGV EPGE  
**Tag Git:** `pre-registro`  
**Status:** CONGELADO E IMUTAVEL (Nenhuma alteracao posterior permitida; desvios vao em `DECISOES.md`)

---

## 1. Objetivo e Escopo da Previsao

O objetivo e prever o resultado oficial do 1o turno da Eleicao Presidencial de 2026 (Brasil), a ser realizado em 04/10/2026, com base exclusivamente em informacoes publicas disponiveis ate o horario de corte.

### Entregaveis Oficiais:
1. **Aba 1 (Candidatos):** Previsao pontual de votos validos (%) para os 12 candidatos oficiais do Edital FGV EPGE, somando exatamente 100,0% com 1 casa decimal:
   - Augusto Cury (Avante)
   - Clariana Barão (DC)
   - Edmilson Costa (PCB)
   - Flávio Bolsonaro (PL)
   - Hertz Dias (PSTU)
   - Luiz Inácio Lula da Silva (PT)
   - Renan Santos (Missão)
   - Ronaldo Caiado (PSD)
   - Romeu Zema (Novo)
   - Rui Costa Pimenta (PCO)
   - Samara Martins (UP)
   - Wilson Grassi (Democrata)
2. **Aba 2 (Adicionais):** Previsao pontual com 1 casa decimal para:
   - Abstencao (% sobre o total de eleitores aptos)
   - Votos Brancos (% sobre o total de votos registrados na urna / comparecimento)
   - Votos Nulos (% sobre o total de votos registrados na urna / comparecimento)

---

## 2. Horario de Corte dos Dados

- **Data e Horario:** Sabado, 03/10/2026, as 20h00 BRT (`2026-10-03T20:00:00-03:00`).
- **Regra:** Nenhuma pesquisa divulgada apos este horario podera entrar no pipeline de previsao oficial.

---

## 3. Modelos Candidatos e Grades de Hiperparametros

Para evitar sobreajuste (overfitting) em uma amostra historica pequena (5 eleicoes presidenciais anteriores: 2006, 2010, 2014, 2018 e 2022), todos os modelos possuem no maximo 2 hiperparametros com grades pequenas, discretas e previamente fixadas:

### Modelo M0: Baseline de Parcimonia
- **Definicao:** Media simples da ultima pesquisa divulgada de cada instituto disponivel dentro da janela de corte (ultimos 21 dias ate a vespera).
- **Hiperparametros:** Nenhum (0 parametros livres).

### Modelo M1: Media Ponderada por Recencia e Amostra
- **Definicao:** Ponderacao exponencial decrescente pela idade da pesquisa combinada com a raiz quadrada do tamanho da amostra:
  $$w_{i} = \sqrt{N_i} \cdot \exp\left(-\frac{\ln(2) \cdot \Delta t_i}{h}\right)$$
  onde $\Delta t_i$ e a idade da pesquisa em dias em relacao a data de corte e $h$ e a meia-vida.
- **Grade de Hiperparametros:**
  - Meia-vida $h \in \{7, 14, 21\}$ dias. Padrao default: $h = 14$ dias.

### Modelo M2: Correcao de House Effect com Shrinkage
- **Definicao:** Modelo M1 com correcao do efeito instituto relativo (house effect) estimado no historico e regularizado por shrinkage bayesiano em direcao a zero:
  $$\hat{\beta}_{j} = c \cdot \bar{\beta}_{j}^{hist}$$
  onde $c \in [0, 1]$ e o fator de encolhimento que penaliza institutos com poucas observacoes historicas.
- **Grade de Hiperparametros:**
  - Fator de shrinkage $c \in \{0.1, 0.5, 1.0\}$.
- **Tratamento Ibope e Ipec:** O Ipec e tratado como continuador operacional do Ibope Inteligencia (mesma equipe tecnica e metodologia presencial estratificada), com shrinkage avaliado separadamente no backtest.
- **Viés Comum da Eleicao:** Distincao conceitual estrita: o house effect corrige o desvio relativo entre institutos; a correcao de vies comum da eleicao (quando todos os institutos erram conjuntamente na mesma direcao) so entra no modelo final se demonstrar reducao empirica consistente do erro no backtest expanding window.

### Modelo M3: Ridge Regression Regularizada
- **Definicao:** Regressao Ridge do resultado oficial na urna sobre os estimadores das pesquisas e atributos estruturais dos candidatos (media das pesquisas, incumbencia, posicao no ranking e campo ideologico).
- **Grade de Hiperparametros:**
  - Penalidade L2 $\alpha \in \{0.01, 0.1, 1.0, 10.0\}$, selecionada estritamente por validacao cruzada interna dentro das eleicoes de treinamento, sem olhar a eleicao de teste.

---

## 4. Modelagem de Abstencao, Votos Brancos e Nulos

Os tres agregados da Aba 2 sao modelados respeitando seus denominadores institucionais estritos do TSE:
- Abstencao = $\text{Abstenções} / \text{Eleitorado Apto}$.
- Votos Brancos = $\text{Brancos} / \text{Comparecimento}$.
- Votos Nulos = $\text{Nulos} / \text{Comparecimento}$.

### Modelos Testados:
1. **Persistencia (Random Walk):** Ultimo valor observado (resultado oficial do 1o turno de 2022).
2. **Media Movel Historica:** Media das eleicoes anteriores.
3. **Tendencia Linear:** Regressao linear temporal sobre a serie historica do TSE (2006-2022).
- **Validacao:** Avaliada por validacao temporal expanding window (serie temporal), garantindo ordem cronologica.

---

## 5. Protocolo de Validacao e Criterio de Decisao

### Protocolos de Validacao Dupla:
1. **Leave-One-Election-Out (LOO):** Para cada ano entre 2006 e 2022, treina-se com as outras 4 eleicoes e testa-se na eleicao retida.
2. **Expanding Window Temporal:** Valida a capacidade preditiva puramente prospectiva:
   - Teste 2014 treinado em 2006-2010.
   - Teste 2018 treinado em 2006-2014.
   - Teste 2022 treinado em 2006-2018.

### Criterio Numerico de Selecao do Modelo Principal:
1. A metrica soberana de avaliacao e o **MAE medio** calculado sobre os candidatos, identico a formula de avaliacao da FGV EPGE:
   $$\text{MAE} = \frac{1}{K} \sum_{k=1}^{K} |y_k - \hat{y}_k|$$
2. O modelo escolhido para a previsao final sera aquele que apresentar o **menor MAE medio no backtest temporal expanding window**.
3. **Criterio de Desempate e Parcimonia:** Em caso de diferenca de MAE inferior ao desvio padrao entre eleicoes (empate tecnico), adota-se o modelo mais simples (principio da parcimonia).
4. **Regra de Seguranca contra Overfitting:** Se o MAE expanding window do modelo complexo selecionado (M1, M2 ou M3) for maior ou igual ao do baseline M0, o modelo M0 sera obrigatoriamente utilizado na entrega final.

---

## 6. Tratamento de Candidatos Nanicos e Hipotese de Voto Util

1. **Calibracao de Nanicos:** Para candidatos nanicos (intencao residual), o modelo avalia a combinacao da mediana historica da votacao de legendas equivalentes no TSE (2006-2022) com o percentual das pesquisas, mitigando distorcoes de arredondamento em levantamentos telefonicos e presenciais.
2. **Hipotese de Voto Util:** No 1o turno de 2022, observou-se uma concentracao tardia de votos no top-2, resultando em uma perda conjunta de cerca de 5,6 p.p. dos candidatos da terceira via entre as pesquisas de vespera e o fechamento das urnas. A hipotese de migracao de voto util (de candidatos em 3o e 4o lugar em direcao aos dois lideres) sera testada no backtest expanding window; caso reduza o MAE empirico, sera incorporada formalmente na sensibilidade; caso contrario, mantem-se a projecao direta das pesquisas sem calibracao manual discricionaria.

---

## 7. Construcao das Faixas de Incerteza

Embora a entrega da planilha XLSX seja estritamente pontual, a faixa de incerteza metodologica apresentada no relatorio, PDF e interface sera construida a partir dos erros absolutos empiricos observados no backtest historico, agrupados pela posicao do candidato na media das pesquisas na data de corte:
- **Grupo 1 (Top-2):** Disputa polarizada de primeiro escalao (maior volume e variabilidade absoluta).
- **Grupo 2 (3o e 4o colocados):** Candidaturas intermediarias (sujeitas a dinamica de voto util de reta final).
- **Grupo 3 (Demais candidatos / nanicos):** Candidaturas residuais (limitadas inferiormente em 0,0%).

---

## 8. Regra de Conversao e Arredondamento

1. **Conversao para Votos Validos:** Descarte proporcional dos votos brancos, nulos e indecisos:
   $$V_k = \frac{P_k}{\sum_{j \in \text{Edital}} P_j} \times 100$$
2. **Candidatos Fora do Edital (ex.: Sub Judice / Renuncia):** Votos atribuidos a candidatos fora da lista dos 12 do edital sao descartados antes da normalizacao dos validos.
3. **Metodo dos Maiores Restos (Hamilton):** Para eliminar discrepancias de arredondamento e garantir que a soma dos 12 candidatos resulte exatamente em 100,0%, aplica-se o metodo dos maiores restos com precisao de decimos (`round(sum * 10) == 1000`), garantindo que cada candidato fique a menos de 0,1 p.p. do seu valor matematico original.

---

## 9. Emenda 1 (Data: 02/10/2026)

**Origem e Motivação:** Auditoria externa do Checkpoint 2 (Claude). Formalizações metodológicas complementares introduzidas antes da execução de qualquer rotina do backtest histórico (Checkpoint 3).

1. **Aproximação Temporal em Pesquisas Históricas (2006-2022):**
   Nas tabelas históricas da Wikipédia onde a data exata de divulgação jornalística não for explicitamente discriminada em coluna própria, a data de divulgação é aproximada conservadoramente pela data final de campo (`data_fim_campo`), garantindo sempre a regra causal inviolável:
   $$\text{data\_divulgacao} \le \text{vespera}$$
   Nenhuma pesquisa coletada no dia do pleito ou pós-pleito ingressa na base de modelagem (vazamento temporal zero).

2. **Tratamento de Nanicos sem Divulgação Individualizada:**
   Quando um instituto de pesquisa divulga candidatos com baixa intenção de forma agregada (por exemplo, "outros candidatos: X%" ou "registram 1% cada um" sem discriminação isolada por linha em tabela oficial), os candidatos sem número unívoco individualizado permanecem registrados como `NaN` (vazio) no banco de dados. O percentual agregado é alocado na coluna `outros_agregado`. Para fins de cálculo do MAE e normalização de válidos, candidatos ausentes ou `NaN` em determinada pesquisa não distorcem a média dos institutos que os divulgaram individualmente.

3. **Separação Estrutural entre Instituto e Contratante:**
   A base de pesquisas históricas e de 2026 passa a discriminar formalmente o instituto responsável pela metodologia de campo (`instituto`) do veículo contratante ou financiador (`contratante`, ex.: Globo, Folha, XP, BTG, CNT, Aya Bancah). O modelo M2 de correção de viés institucional (house effect) opera exclusivamente sobre o identificador do instituto pesquisador, prevenindo contaminações por rotação de contratantes.

4. **Validação de Sanidade das Vésperas (Datafolha):**
   Fica pré-registrado o teste de sanidade empírica das pesquisas de véspera do Datafolha sobre votos válidos, exigindo aderência aos registros históricos com tolerância estrita de 1,0 p.p.:
   - **2022:** Lula 50,0% | Bolsonaro 36,0%
   - **2018:** Bolsonaro 40,0% | Haddad 25,0%
   - **2014:** Dilma 44,0% | Aécio 26,0% | Marina 24,0%

---

## 10. Emenda 2 (Data: 02/10/2026)

**Origem e Motivação:** Auditoria externa do Checkpoint 2 (Claude). Formalização definitiva das equações, regras de decisão, hiperparâmetros e protocolos de validação antes do início do backtest histórico (Checkpoint 3).

### 1. House Effect por Instituto x Bloco Temático
O viés de instituto (house effect) no modelo M2 não é estimado candidato a candidato de forma livre, mas sim particionado estritamente por blocos políticos funcionais comparáveis entre eleições:
- **Bloco PT ($B_1$):** Candidato apoiado pela legenda do Partido dos Trabalhadores (2006 Lula, 2010 Dilma, 2014 Dilma, 2018 Haddad, 2022 Lula, 2026 Lula).
- **Bloco Principal Adversário do PT ($B_2$):** Principal competidor polarizado da eleição (2006 Geraldo Alckmin, 2010 José Serra, 2014 Aécio Neves, 2018 Jair Bolsonaro, 2022 Jair Bolsonaro, 2026 Flávio Bolsonaro).
- **Bloco Demais Candidatos ($B_3$):** Candidatos intermediários e nanicos (3º colocado em diante).

O erro de cada pesquisa $i$ do instituto $j$ no bloco $b$ sobre a eleição $t$ é definido em **votos válidos**:
$$e_{i, c, t} = \hat{v}_{i, c} - v_{c, t}^{\text{TSE}}$$
onde $\hat{v}_{i, c}$ representa o percentual do candidato $c$ na pesquisa recalculado sobre os votos válidos (após descarte de brancos, nulos e indecisos) e $v_{c, t}^{\text{TSE}}$ é o resultado oficial do 1º turno apurado pelo TSE.

O erro médio histórico bruto do instituto $j$ no bloco $b$ ao longo das eleições de treino é:
$$\bar{\beta}_{j, b} = \frac{1}{|S_{j, b}|} \sum_{(i, c, t) \in S_{j, b}} (\hat{v}_{i, c} - v_{c, t}^{\text{TSE}})$$
onde $S_{j, b}$ é o conjunto de observações históricas do instituto $j$ para candidatos do bloco $b$.

### 2. Shrinkage Empírico Dependente do Histórico ($n_j$)
Para institutos com poucas eleições no histórico, a estimativa pontual $\bar{\beta}_{j, b}$ é encolhida em direção a zero via credibilidade empírica Bayesiana:
$$\beta_{j, b} = \frac{n_j}{n_j + k} \cdot \bar{\beta}_{j, b}$$
onde:
- $n_j \in \{0, 1, 2, 3, 4, 5\}$ é o número de eleições prévias em que o instituto $j$ realizou pesquisas na base de treino.
- $k \in \{1, 3, 10\}$ é a constante de regularização (hiperparâmetro a ser avaliado no expanding window).
- Se $n_j = 0$ (instituto estreante, sem histórico no conjunto de treino), $\beta_{j, b} = 0$, garantindo que nenhuma correção arbitrária seja aplicada a institutos novos.

### 3. Decisão Metodológica Única: Ibope e Ipec
- **Decisão Oficial:** Adota-se a **série unificada (Ibope -> Ipec)** como especificação principal. O Ipec é tratado como continuador institucional e metodológico do Ibope Inteligência (mesma diretoria executiva, equipe estatística e desenho amostral presencial domiciliar estratificado por cotas).
- A especificação com séries estritamente separadas será calculada e apresentada no relatório técnico exclusivamente a título de análise de sensibilidade.

### 4. Critério Numérico de Empate Técnico e Regra de Parcimônia
Sejam $M_A$ e $M_B$ dois modelos concorrentes (com $M_A$ mais complexo que $M_B$). Define-se a diferença de MAE na eleição de teste $t \in \{2014, 2018, 2022\}$ como $\Delta_t = \text{MAE}_{M_A, t} - \text{MAE}_{M_B, t}$.
- Média das diferenças: $\bar{\Delta} = \frac{1}{3} \sum_{t} \Delta_t$.
- Desvio-padrão amostral das diferenças: $s_\Delta = \sqrt{\frac{1}{2} \sum_{t=1}^{3} (\Delta_t - \bar{\Delta})^2}$.
- Erro-padrão da média das diferenças: $\text{SE}(\Delta) = \frac{s_\Delta}{\sqrt{3}}$.
- **Critério de Empate:** Se $|\bar{\Delta}| < \text{SE}(\Delta)$, conclui-se que não há evidência empírica de superioridade preditiva do modelo mais complexo.
- **Hierarquia de Parcimônia:** Havendo empate técnico, adota-se compulsoriamente o modelo mais simples, conforme a ordem formal:
  $$\text{M0} \prec \text{M1} \prec \text{M2} \prec \text{M3}$$

### 5. Especificação Objetiva de Features do Modelo M3
Elimina-se categoricamente qualquer classificação baseada em "campo ideológico", prevenindo taxonomias subjetivas ou arbitrárias. O modelo M3 utiliza exclusivamente covariáveis observáveis:
1. $X_{1, c}$: Previsão preliminar de votos válidos do candidato $c$ obtida pela média ponderada das pesquisas recentes (saída do modelo M1).
2. $X_{2, c} \in \{0, 1\}$: Indicadora binária de incumbência governista ($1$ para candidato apoiado pela situação federal em exercício; $0$ para oposição).
3. $X_{3, c} \in \{1, 2, \dots, 12\}$: Posição ordinal (ranking) do candidato na média das pesquisas na data de corte (1º, 2º, ..., 12º colocado).

### 6. Viés Comum da Eleição (Common Election Bias)
O viés comum mede o desvio médio compartilhado por todos os institutos em relação à apuração oficial da urna em determinada eleição:
$$\bar{\mu}_b = \frac{1}{|E_{\text{treino}}|} \sum_{t \in E_{\text{treino}}} \left( \bar{v}_{b, t}^{\text{pesquisas}} - v_{b, t}^{\text{TSE}} \right)$$
onde $\bar{v}_{b, t}^{\text{pesquisas}}$ é a média agregada de todas as pesquisas no bloco $b$ na eleição $t$.
O ajuste regularizado é dado por:
$$\hat{\mu}_b = \frac{N_{\text{eleic}}}{N_{\text{eleic}} + k_{\mu}} \cdot \bar{\mu}_b, \quad \text{com } k_{\mu} \in \{1, 3\}$$
**Regra de Ativação:** O termo $\hat{\mu}_b$ só será incorporado ao modelo final se demonstrar redução estrita do MAE médio no backtest expanding window. Caso contrário, $\hat{\mu}_b = 0$.

### 7. Hipótese e Modelagem do Voto Útil de Reta Final
A perda de fôlego de candidaturas de terceira via na véspera em favor da polarização é modelada pela perda histórica agregada do 3º e 4º colocados entre a pesquisa de corte e o resultado do TSE:
$$\delta_t = \max\left(0, \sum_{c \in \{3^\circ, 4^\circ\}} (\hat{v}_{c, t} - v_{c, t}^{\text{TSE}})\right)$$
com média histórica nas eleições de treino $\bar{\delta} = \frac{1}{|E_{\text{treino}}|} \sum_{t} \delta_t$.
No teste ou na projeção de 2026, subtrai-se a fração calibrada $\gamma \cdot \bar{\delta}$ do 3º e 4º colocados e transfere-se para os dois líderes (Top-2):
$$\hat{v}_{k}^{\text{util}} = \max\left(0.0, \, \hat{v}_k - \gamma \cdot \bar{\delta} \cdot \frac{\hat{v}_k}{\hat{v}_3 + \hat{v}_4}\right), \quad \text{para } k \in \{3, 4\}$$
$$\hat{v}_{m}^{\text{util}} = \hat{v}_m + \gamma \cdot \bar{\delta} \cdot \frac{\hat{v}_m}{\hat{v}_1 + \hat{v}_2}, \quad \text{para } m \in \{1, 2\}$$
com $\gamma \in \{0.0, 0.5, 1.0\}$.
**Regra de Ativação:** A migração de voto útil entra no modelo final apenas se reduzir o MAE médio no expanding window. Caso contrário, fixa-se $\gamma = 0$.

### 8. Prior Histórico para Candidatos Nanicos
Para candidaturas com intenção residual nas pesquisas, adota-se a calibragem com o desempenho histórico de legendas equivalentes no TSE (2006-2022):

| Candidato 2026 | Partido 2026 | Legendas Históricas TSE Equivalentes (2006-2022) | Mediana Histórica TSE (%) |
| :--- | :--- | :--- | :--- |
| Clariana Barão | Democracia Cristã (DC) | PSDC / DC | 0,15% |
| Edmilson Costa | PCB | PCB | 0,08% |
| Hertz Dias | PSTU | PSTU | 0,12% |
| Rui Costa Pimenta | PCO | PCO | 0,03% |
| Samara Martins | UP | UP (2022) / PCR / PGT | 0,07% |
| Wilson Grassi | Democrata | PRTB / PEN / PHS | 0,10% |

A projeção calibrada do candidato nanico é dada pela combinação convexa:
$$\hat{y}_c = (1 - w) \cdot \hat{v}_c^{\text{pesquisas}} + w \cdot \text{Prior}_c^{\text{hist}}$$
com $w \in \{0.0, 0.5, 1.0\}$. O peso $w$ é computado no teto formal de hiperparâmetros do modelo (máximo de 2 hiperparâmetros livres por modelo).

### 9. Protocolo Oficial de Decisão e Nota de Limitação Amostral ($n=3$)
- **Protocolo de Decisão Soberano:** O modelo que definirá as previsões oficiais de 2026 será selecionado exclusivamente com base no **menor MAE médio nas 3 janelas prospectivas temporais da validação por expanding window** (2014 com treino 2006-2010; 2018 com treino 2006-2014; 2022 com treino 2006-2018).
- A validação Leave-One-Election-Out (LOEO) será calculada e reportada integralmente no relatório como protocolo complementar e de sensibilidade, ressaltando explicitamente sua natureza acausal (utilização de eleições cronologicamente futuras no treino).
- **Nota Formal de Limitação Amostral ($n=3$):** Registra-se com rigor a limitação amostral de dispormos de exatamente 3 pontos de validação prospectiva ($n = 3$). Em decorrência do tamanho amostral reduzido, a aplicação da regra de parcimônia definida na Seção 4 desta Emenda é mandatória para evitar a escolha de modelos sobreajustados.

---

## 11. Emenda 3 (Data: 02/10/2026)

**Origem e Motivação:** Auditoria externa do Checkpoint 2 rodada 3 (Claude). Aperfeiçoamento econométrico do viés institucional, apuração automatizada dos priors históricos via TSE, substituição da grade combinatória por protocolo sequencial parcimonioso e publicação de parâmetros estruturais antes do backtest (Checkpoint 3).

### 1. House Effect Relativo (Separação entre Viés Institucional e Viés Comum)
Na formulação anterior, o house effect de cada instituto usava o erro bruto em relação à apuração oficial, absorvendo inadvertidamente o viés comum compartilhado por todas as pesquisas em eleições com desvio sistêmico (como 2018 e 2022).

Para assegurar a separação teórica postulada em `docs/ENTENDIMENTO.md`, o viés de cada instituto $j$ no bloco $b \in \{B_1, B_2, B_3\}$ na eleição $t$ é definido como o seu **desvio relativo em relação à média de todos os institutos** naquela mesma eleição e bloco:

1. Erro médio do instituto $j$ no bloco $b$ na eleição $t$:
   $$e_{j, b, t} = \frac{1}{|S_{j, b, t}|} \sum_{i \in \text{pesquisas}(j, t)} \sum_{c \in b} (\hat{v}_{i, c} - v_{c, t}^{\text{TSE}})$$

2. Erro médio de todos os institutos no bloco $b$ na eleição $t$:
   $$\bar{e}_{b, t} = \frac{1}{|S_{b, t}|} \sum_{i \in \text{todas pesquisas}(t)} \sum_{c \in b} (\hat{v}_{i, c} - v_{c, t}^{\text{TSE}})$$

3. Desvio institucional relativo da eleição $t$:
   $$d_{j, b, t} = e_{j, b, t} - \bar{e}_{b, t}$$

4. House effect relativo histórico consolidado nas eleições de treino:
   $$\bar{\beta}_{j, b}^{\text{rel}} = \frac{1}{n_{j}} \sum_{t \in E_{\text{treino}, j}} d_{j, b, t}$$

5. Ajuste encolhido com shrinkage empírico Bayesiano:
   $$\beta_{j, b}^{\text{rel}} = \frac{n_j}{n_j + k} \cdot \bar{\beta}_{j, b}^{\text{rel}}, \quad \text{com } k \in \{1, 3, 10\}$$
   onde $n_j$ é o número de eleições de treino com presença do instituto $j$. Institutos sem histórico ($n_j = 0$) recebem correção nula ($\beta = 0$).

O viés comum da eleição ($\mu_b$) permanece tratado de forma estritamente independente na Seção 6.

### 2. Priors dos Nanicos Calculados por Código via Microdados do TSE
Os valores dos priors históricos para candidatos nanicos em 2026 são computados de forma programática pelo módulo `src/nanicos.py`, lendo diretamente os arquivos processados de votação nominal do TSE (`data/processed/votacao_candidato_*.parquet`, 2006-2022). O prior de cada legenda corresponde à **mediana** de sua série de votos válidos no 1º turno:

| Candidato 2026 | Partido 2026 | Legenda de Referência no TSE | Votação Válida Histórica Ano a Ano (%) | Mediana TSE (Prior Oficial) |
| :--- | :--- | :--- | :--- | :---: |
| **Clariana Barão** | DC | PSDC / DC | 2006 (0,0659%), 2010 (0,0880%), 2014 (0,0589%), 2018 (0,0390%), 2022 (0,0140%) | **0,0589%** |
| **Edmilson Costa** | PCB | PCB | 2010 (0,0385%), 2014 (0,0460%), 2022 (0,0386%) | **0,0386%** |
| **Hertz Dias** | PSTU | PSTU | 2010 (0,0833%), 2014 (0,0877%), 2018 (0,0521%), 2022 (0,0217%) | **0,0677%** |
| **Rui Costa Pimenta**| PCO | PCO | 2010 (0,0120%), 2014 (0,0118%) | **0,0119%** |
| **Samara Martins** | UP | UP | 2022 (0,0453%) | **0,0453%** |
| **Wilson Grassi** | Democrata | Candidaturas TSE < 0,5% (2006-2022) | 22 candidaturas presidenciais com < 0,5% no TSE (PSL 2006, PRP 2006, PRTB 2010/2014, PPL 2018, PTB 2022, NOVO 2022, etc.) | **0,0546%** |

A combinação convexa para nanicos é:
$$\hat{y}_c = (1 - w) \cdot \hat{v}_c^{\text{pesquisas}} + w \cdot \text{Prior}_c^{\text{hist}}, \quad w \in \{0.5, 1.0\}$$

### 3. Protocolo Sequencial de Decisão (Prevenção de Overfitting)
Substitui-se a busca em grade combinatória conjunta (que geraria 162 combinações para apenas 3 eleições de teste) por um protocolo sequencial parcimonioso de 2 etapas:

- **Etapa 1: Seleção do Modelo Base ($M^*$):**
  Avaliam-se exclusivamente os modelos base puros nas 3 janelas prospectivas do expanding window (2014, 2018, 2022):
  - M0 (Baseline simples): 1 configuração.
  - M1 (Média ponderada temporal): $h \in \{7, 14, 21\}$ dias (3 configurações).
  - M2 (M1 com melhor $h$ + House Effect Relativo): $k \in \{1, 3, 10\}$ (3 configurações).
  - M3 (Ridge Regression regularizada): $\alpha \in \{0.01, 0.1, 1.0, 10.0\}$ (4 configurações).
  *Total da Etapa 1:* 11 configurações avaliadas.
  *Critério de Escolha:* Seleciona-se o modelo com menor MAE médio, sujeito à regra estrita de empate técnico: se $|\bar{\Delta}| < \text{SE}(\Delta)$, adota-se compulsoriamente o modelo mais simples ($\text{M0} \prec \text{M1} \prec \text{M2} \prec \text{M3}$).

- **Etapa 2: Avaliação Individual e Isolada de Ajustes Opcionais:**
  Sobre o modelo base $M^*$ vencedor da Etapa 1, avalia-se **um único ajuste por vez**, comparado diretamente contra $M^*$ puro:
  1. *Ajuste por Viés Comum:* $M^* + \hat{\mu}_b$ com $k_\mu \in \{1, 3\}$ (2 configurações).
  2. *Ajuste por Voto Útil:* $M^* + \text{Voto Útil}$ com $\gamma \in \{0.5, 1.0\}$ (2 configurações).
  3. *Ajuste por Prior de Nanicos:* $M^* + \text{Prior TSE}$ com $w \in \{0.5, 1.0\}$ (2 configurações).
  *Total da Etapa 2:* 6 configurações avaliadas.
  *Regra de Ativação:* Cada ajuste só ingressa no modelo final se demonstrar redução estrita do MAE em relação a $M^*$ por uma margem superior a $1 \text{ SE}(\Delta)$ da diferença. Ajustes empatados ou inferiores são rejeitados.

*Contabilidade Total:* Exatamente **17 configurações avaliadas** no total, eliminando a inflação de graus de liberdade. O relatório do Checkpoint 3 deve reportar o MAE de todas as 17 configurações na tabela de ablation.

### 4. Renormalização Obrigatória para 100,0%
Qualquer transformação aritmética sobre as intenções de voto (correção de house effect relativo, subtração de viés comum, transferência de voto útil ou combinação convexa de nanicos) pode gerar desvios de soma ou valores marginais negativos. Fica estabelecido como regra causal invariante que:
1. Todo valor projetado negativo é truncado em zero: $\hat{v}_k \leftarrow \max(0.0, \, \hat{v}_k)$.
2. O vetor de candidatos é compulsoriamente renormalizado para somar 100,0%:
   $$\hat{v}_k^{\text{norm}} = \frac{\hat{v}_k}{\sum_{j=1}^{K} \hat{v}_j} \times 100$$
Essa renormalização ocorre imediatamente antes do cálculo de qualquer métrica de validação (MAE).

### 5. Tabela Oficial de Incumbência Governista (2006-2026)
A variável binária $X_{2, c} \in \{0, 1\}$ do modelo M3 é codificada a partir do alinhamento formal com a chefia do Poder Executivo Federal em exercício na data da eleição:

| Eleição | Candidato(a) Governista ($X_{2} = 1$) | Justificativa Institucional | Candidatos de Oposição ($X_{2} = 0$) |
| :---: | :--- | :--- | :--- |
| **2006** | **Luiz Inácio Lula da Silva** (PT) | Presidente da República em exercício de mandato | Geraldo Alckmin, Heloísa Helena, Cristovam Buarque e demais |
| **2010** | **Dilma Rousseff** (PT) | Candidata oficial apoiada pelo Presidente Lula em exercício | José Serra, Marina Silva, Plínio de Arruda Sampaio e demais |
| **2014** | **Dilma Rousseff** (PT) | Presidente da República em exercício de mandato | Aécio Neves, Marina Silva, Luciana Genro, Pastor Everaldo e demais |
| **2018** | **Henrique Meirelles** (MDB) | Candidato da situação (ex-Ministro da Fazenda do Governo Michel Temer) | Jair Bolsonaro, Fernando Haddad, Ciro Gomes, Geraldo Alckmin e demais |
| **2022** | **Jair Bolsonaro** (PL) | Presidente da República em exercício de mandato | Luiz Inácio Lula da Silva, Ciro Gomes, Simone Tebet e demais |
| **2026** | **Luiz Inácio Lula da Silva** (PT) | Presidente da República em exercício de mandato | Flávio Bolsonaro, Augusto Cury, Renan Santos, Ronaldo Caiado e demais |

### 6. Esclarecimento sobre o Arquivo `tests/test_sanity.py`
O arquivo `tests/test_sanity.py` consiste em um teste preliminar de verificação de ambiente (`test_sanity()` com `assert True`). Ele foi gerado na fase zero de configuração para testar a comunicação do runner `pytest` sob o Windows e não contém nenhuma lógica de negócio, parâmetros de modelagem ou dados eleitorais.

### 7. Errata: Soma da Pesquisa PoderData/Aya 2026
Registra-se formalmente a errata aritmética: a soma das intenções de voto estimuladas da pesquisa PoderData/Aya (protocolo BR-01739/2026) em `data/manual/pesquisas_2026.csv` totaliza **101,0%** ($41 + 39 + 6 + 3 + 2 + 1 + 1 + 1 + 1 + 0 + 0 + 0 + 4 \text{ brancos/nulos} + 2 \text{ indecisos}$), decorrente de arredondamento comercial dos percentuais unitários, enquadrando-se perfeitamente na tolerância técnica pré-registrada de $[97,0\%, 101,5\%]$.

