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
