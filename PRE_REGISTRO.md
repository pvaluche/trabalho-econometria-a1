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
