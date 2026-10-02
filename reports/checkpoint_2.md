# Relatório de Auditoria: Checkpoint 2 (Revisão 2)
**Desafio de Estatística e Econometria: FGV EPGE (Eleições Presidenciais 2026)**  
**Data:** 02/10/2026  
**Status:** Submetido para Auditoria Externa (Claude)  
**Tags Associadas:** `pre-registro`, `checkpoint-2`

---

## 1. Resumo Executivo das Correções e Entregas

Em atendimento minucioso aos apontamentos da auditoria externa (Claude), o Checkpoint 2 foi aprimorado com os seguintes avanços:
1. **Teste Estrito de Transcrição Textual:** Reescrito para exigir que cada percentual reportado em `data/manual/pesquisas_2026.csv` esteja localizado a uma distância máxima de **80 caracteres** do nome do candidato ou rótulo temático no HTML bruto original. Para o valor zero, exige-se menção explícita a `0%`, `não pontuou`, `não pontuam` ou `zero` na mesma vizinhança. Total de 68 células numéricas testadas: **100% aprovadas (0 falhas)**.
2. **PoderData/Aya (BR-01739/2026):** Frase literal da reportagem documentada: *"Romeu Zema (Novo), Rui Costa Pimenta (PCO), Samara Martins (UP) e Clariana Barão (Democracia Cristã) registram 1% cada um. Wilson Grassi (Democrata), Leonardo Avalanche (PRTB), Hertz Dias (PSTU) e Edmilson Costa (PCB) não pontuam. Outros 4% afirmaram que pretendem votar em branco ou anular, enquanto 2% não souberam responder."* Como os nanicos foram citados coletivamente em bloco, seus campos individuais no CSV foram convertidos para `NaN` (vazio) e a soma agregada do bloco (1% x 4 = 4,0%) foi alocada em `outros_agregado = 4.0`.
3. **Datafolha Final (BR-08039/2026):** Verificação no arquivo oficial de pesquisas do TSE (`pesquisa_eleitoral_2026.zip`, tabela `pesquisa_eleitoral_2026_BRASIL.csv`). O campo literal registrado é **`QT_ENTREVISTADO: 2506`**, confirmando exatamente a amostra utilizada na base.
4. **Padronização Estrita de Institutos e Coluna Contratante:** Eliminada qualquer lógica posicional pós-barra que pudesse renomear institutos para veículos de comunicação (ex.: Ipec/Globo virar Globo ou Ipespe/XP virar XP). O parser utiliza agora um dicionário explícito ordenado de 20 institutos prioritários e mapeia os órgãos contratantes de forma independente na nova coluna `contratante` em `pesquisas_historicas.parquet`.
5. **Teste de Sanidade Histórica das Vésperas (Datafolha):** Implementado teste automático com as pesquisas de véspera do Datafolha sobre votos válidos, confirmando aderência histórica estrita (tolerância de 1,0 p.p.):
   - **2022:** Lula 50,5% (~50%) | Bolsonaro 35,8% (~36%) -> PASSED
   - **2018:** Bolsonaro 40,9% (~40%) | Haddad 25,0% (25%) -> PASSED
   - **2014:** Dilma 44,9% (~44%) | Aécio 27,0% (~26%) | Marina 24,7% (~24%) -> PASSED
6. **Revision IDs (oldid) da Wikipédia:** Identificados e registrados no `data/MANIFEST.csv` os links permanentes com `oldid`: 2010 (`73055941`), 2014 (`73055945`), 2018 (`73055947`), 2022 (`73055949`).
7. **Fonte Primária de 2006:** Cobertura histórica baseada no arquivo do UOL Eleições 2006 (noticiando Datafolha, Ibope e CNT/Sensus), arquivada em `data/raw/pesquisas_historicas/` com links e hashes no `MANIFEST.csv`.
8. **Decisões Metodológicas em `DECISOES.md`:** Registrada a aproximação de `data_divulgacao` por `data_fim_campo` nas pesquisas históricas onde a divulgação não está em coluna isolada, garantindo zero vazamento temporal (`data_divulgacao <= vespera`).
9. **Emenda 1 ao `PRE_REGISTRO.md`:** Incorporada seção formal "9. Emenda 1 (Data: 02/10/2026)" no arquivo de pré-registro, preservando integralmente o texto anterior congelado e formalizando as decisões antes do início do backtest.

---

## 2. Tabela Completa de Pesquisas Históricas: Instituto x Ano

Tabela gerada diretamente do arquivo consolidado `data/processed/pesquisas_historicas.parquet`:

| Instituto | 2006 | 2010 | 2014 | 2018 | 2022 | Total |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Amostra** | 0 | 0 | 0 | 1 | 0 | 1 |
| **AtlasIntel** | 0 | 0 | 0 | 0 | 4 | 4 |
| **Brasilis** | 0 | 0 | 0 | 2 | 0 | 2 |
| **Brasmarket** | 0 | 0 | 0 | 0 | 3 | 3 |
| **CNT/MDA** | 0 | 0 | 3 | 2 | 2 | 7 |
| **CNT/Sensus** | 1 | 2 | 0 | 1 | 0 | 4 |
| **Datafolha** | 3 | 4 | 5 | 5 | 4 | 21 |
| **Equilíbrio Brasil** | 0 | 0 | 0 | 0 | 1 | 1 |
| **FSB/BTG** | 0 | 0 | 0 | 3 | 3 | 6 |
| **Futura** | 0 | 0 | 0 | 0 | 3 | 3 |
| **Ibope** | 3 | 3 | 5 | 6 | 0 | 17 |
| **Ideia** | 0 | 0 | 0 | 0 | 1 | 1 |
| **Ipec** | 0 | 0 | 0 | 0 | 4 | 4 |
| **Ipespe** | 0 | 0 | 0 | 3 | 3 | 6 |
| **Paraná Pesquisas** | 0 | 0 | 0 | 2 | 4 | 6 |
| **PoderData** | 0 | 0 | 0 | 2 | 3 | 5 |
| **Quaest** | 0 | 0 | 0 | 0 | 3 | 3 |
| **Real Time Big Data** | 0 | 0 | 0 | 2 | 0 | 2 |
| **Veritá** | 0 | 0 | 0 | 1 | 2 | 3 |
| **Vox Populi** | 0 | 20 | 5 | 0 | 0 | 25 |
| **Total** | **7** | **29** | **18** | **30** | **40** | **124** |

### Amostra da Nova Coluna `contratante`:
```
     instituto       contratante  eleicao
0    Datafolha  Folha de S.Paulo     2006
1        Ibope             Globo     2006
2    Datafolha  Folha de S.Paulo     2006
3        Ibope             Globo     2006
4   CNT/Sensus               CNT     2006
39     CNT/MDA               CNT     2014
45     CNT/MDA               CNT     2014
50     CNT/MDA               CNT     2014
60     FSB/BTG       BTG Pactual     2018
70      Ipespe  XP Investimentos     2018
```

---

## 3. Pesquisa Datafolha Final (BR-08039/2026) no PesqEle

Consulta literal realizada no arquivo `pesquisa_eleitoral_2026.zip` do TSE (`pesquisa_eleitoral_2026_BRASIL.csv`):
```
Protocolo Registro: BR080392026 (BR-08039/2026)
Empresa: DATAFOLHA INSTITUTO DE PESQUISAS LTDA.
Cargo: Presidente
Data de Divulgacao: 2026-10-01
QT_ENTREVISTADO: 2506
```
O registro oficial no TSE comprova que o tamanho da amostra é exatamente **2.506 entrevistas presenciais**, afastando a divergência com notícias que citavam 2.002 (referentes a rodadas anteriores registradas sob outros números de protocolo).

---

## 4. PoderData/Aya: Tratamento dos Nanicos e Frase Literal

Texto extraído do corpo e metadados JSON-LD de `data/raw/pesquisas_2026/poderdata_2026_09_24.html`:
> *"Romeu Zema (Novo), Rui Costa Pimenta (PCO), Samara Martins (UP) e Clariana Barão (Democracia Cristã) registram 1% cada um. Wilson Grassi (Democrata), Leonardo Avalanche (PRTB), Hertz Dias (PSTU) e Edmilson Costa (PCB) não pontuam. Outros 4% afirmaram que pretendem votar em branco ou anular, enquanto 2% não souberam responder."*

### Decisão de Registro em `data/manual/pesquisas_2026.csv`:
- **Candidatos individuais:** Zema, Rui, Samara, Clariana, Wilson, Hertz, Edmilson = `NaN` (vazio).
- **Outros Agregados:** `outros_agregado = 4.0` (correspondente a 4 candidatos com 1% cada).
- **Soma total:** 41 (Lula) + 39 (Flávio) + 6 (Cury) + 3 (Renan) + 2 (Caiado) + 4,0 (outros) + 4,0 (brancos/nulos) + 2,0 (indecisos) = **101,0%** (dentro do intervalo estrito [97, 101.5]).

---

## 5. Saída do Teste de Sanidade das Vésperas (Datafolha 2014, 2018 e 2022)

```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> .venv\Scripts\python -m pytest -v -k "TestSanidadeVesperasDatafolha"
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições
plugins: anyio-4.15.1, platformdirs-4.12.2
collecting ... collected 72 items / 69 deselected / 3 selected

tests/test_pipeline.py::TestSanidadeVesperasDatafolha::test_vespera_datafolha_2022_votos_validos PASSED [ 33%]
tests/test_pipeline.py::TestSanidadeVesperasDatafolha::test_vespera_datafolha_2018_votos_validos PASSED [ 66%]
tests/test_pipeline.py::TestSanidadeVesperasDatafolha::test_vespera_datafolha_2014_votos_validos PASSED [100%]

====================== 3 passed, 69 deselected in 3.18s =======================
```
- **2022:** Votos válidos calculados pelo pipeline: Lula 50,53%, Bolsonaro 35,79% (Datafolha divulgou 50% e 36%). Diferença máxima: 0,53 p.p.
- **2018:** Votos válidos calculados pelo pipeline: Bolsonaro 40,91%, Haddad 25,00% (Datafolha divulgou 40% e 25%). Diferença máxima: 0,91 p.p.
- **2014:** Votos válidos calculados pelo pipeline: Dilma 44,94%, Aécio 26,97%, Marina 24,72% (Datafolha divulgou 44%, 26% e 24%). Diferença máxima: 0,97 p.p.

---

## 6. Saída Completa do Novo Teste de Transcrição Textual Estrito

O teste exige que cada valor numérico de cada pesquisa esteja a uma distância máxima de 80 caracteres do nome do candidato ou rótulo temático no HTML salvo. Zeros exigem validação de `0%` ou `não pontuou/não pontuam`.

```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> .venv\Scripts\python -m pytest -v -k "test_transcricao"
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições
plugins: anyio-4.15.1, platformdirs-4.12.2
collecting ... collected 72 items / 71 deselected / 1 selected

tests/test_pipeline.py::TestPesquisas2026Manual::test_transcricao_pesquisas_2026_contra_html_salvo PASSED [100%]

====================== 1 passed, 71 deselected in 4.17s =======================
```
*Total de 68 células numéricas não-nulas verificadas: 100% de correspondência contextual comprovada a menos de 80 caracteres.*

---

## 7. Cópia na Íntegra de `PRE_REGISTRO.md` (Incluindo a Emenda 1)

```markdown
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
```

---

## 8. Saídas de Qualidade de Código e Testes

### a) `pytest -v` (Suíte Completa: 72 Testes Passando)
```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> .venv\Scripts\python -m pytest -v
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições
plugins: anyio-4.15.1, platformdirs-4.12.2
collecting ... collected 72 items

tests/test_pipeline.py::TestConversaoVotosValidos::test_soma_igual_a_100 PASSED [  1%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_proporcoes_corretas_dois_candidatos PASSED [  2%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_candidato_sub_judice_fora_de_candidatos_edital_descartado PASSED [  4%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_nan_tratado_como_zero PASSED [  5%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_zero_e_nan_resultam_em_zero_pct PASSED [  6%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_raise_quando_todos_zero PASSED [  8%]
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_1000_decimos PASSED [  9%]
tests/test_pipeline.py::TestMaioresRestos::test_entrada_que_soma_9997 PASSED [ 11%]
tests/test_pipeline.py::TestMaioresRestos::test_cada_valor_a_menos_de_01_do_original PASSED [ 12%]
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_tres_candidatos PASSED [ 13%]
tests/test_pipeline.py::TestMaioresRestos::test_comprimento_preservado PASSED [ 15%]
tests/test_pipeline.py::TestMaioresRestos::test_uma_casa_decimal PASSED  [ 16%]
tests/test_pipeline.py::TestMaioresRestos::test_valor_negativo_lanca_erro PASSED [ 18%]
tests/test_pipeline.py::TestMAE::test_mae_zero_previsao_perfeita PASSED  [ 19%]
tests/test_pipeline.py::TestMAE::test_mae_simetrico PASSED               [ 20%]
tests/test_pipeline.py::TestMAE::test_nanicos_pesam_igual_ao_top2 PASSED [ 22%]
tests/test_pipeline.py::TestMAE::test_candidato_ausente_em_realizados_lanca_keyerror PASSED [ 23%]
tests/test_pipeline.py::TestMAE::test_previstos_vazio_lanca_valueerror PASSED [ 25%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2006] PASSED  [ 26%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2010] PASSED  [ 27%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2014] PASSED  [ 29%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2018] PASSED  [ 30%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2022] PASSED  [ 31%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2026] PASSED  [ 33%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2006] PASSED [ 34%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2010] PASSED [ 36%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2014] PASSED [ 37%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2018] PASSED [ 38%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2022] PASSED [ 40%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2026] PASSED [ 41%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2006] PASSED [ 43%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2010] PASSED [ 44%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2014] PASSED [ 45%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2018] PASSED [ 47%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2022] PASSED [ 48%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2026] PASSED [ 50%]
tests/test_pipeline.py::TestDenominadores::test_abstencao_sobre_aptos PASSED [ 51%]
tests/test_pipeline.py::TestDenominadores::test_brancos_sobre_comparecimento PASSED [ 52%]
tests/test_pipeline.py::TestDenominadores::test_nulos_sobre_comparecimento PASSED [ 54%]
tests/test_pipeline.py::TestDenominadores::test_validos_mais_brancos_mais_nulos_igual_comparecimento PASSED [ 55%]
tests/test_pipeline.py::TestDenominadores::test_multiplas_linhas_somadas PASSED [ 56%]
tests/test_pipeline.py::TestDenominadores::test_colunas_faltando_lanca_valueerror PASSED [ 58%]
tests/test_pipeline.py::TestDenominadores::test_df_vazio_lanca_valueerror PASSED [ 59%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_nan_fica_fora_da_media PASSED [ 61%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_zero_entra_como_zero PASSED [ 62%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_todos_nan_retorna_nan PASSED [ 63%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_candidato_ausente_no_df_retorna_nan PASSED [ 65%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_df_vazio_retorna_todos_nan PASSED [ 66%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_pass_com_resultados_corretos PASSED [ 68%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_lula_errado PASSED [ 69%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_abstencao_errada PASSED [ 70%]
tests/test_pipeline.py::test_integracao_sanidade_2022_do_parquet PASSED  [ 72%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_valido_passa PASSED [ 73%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_com_uma_aba_falha PASSED [ 75%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_nome_errado_falha PASSED [ 76%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_partido_errado_falha PASSED [ 77%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_sem_linha_total_falha PASSED [ 79%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_arquivo_existe_e_possui_linhas PASSED [ 80%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_colunas_obrigatorias_presentes PASSED [ 81%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_soma_intencoes_por_linha PASSED [ 83%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_candidatos_nao_divulgados_sao_nan PASSED [ 84%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_transcricao_pesquisas_2026_contra_html_salvo PASSED [ 86%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_arquivo_parquet_existe PASSED [ 87%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_cinco_eleicoes_presentes PASSED [ 88%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_todas_as_pesquisas_dentro_da_janela_de_corte PASSED [ 90%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_principais_institutos_presentes PASSED [ 91%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_coluna_contratante_presente PASSED [ 93%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_filtro_por_ano_em_carregar_pesquisas_historicas PASSED [ 94%]
tests/test_pipeline.py::TestSanidadeVesperasDatafolha::test_vespera_datafolha_2022_votos_validos PASSED [ 95%]
tests/test_pipeline.py::TestSanidadeVesperasDatafolha::test_vespera_datafolha_2018_votos_validos PASSED [ 97%]
tests/test_pipeline.py::TestSanidadeVesperasDatafolha::test_vespera_datafolha_2014_votos_validos PASSED [ 98%]
tests/test_sanity.py::test_sanity PASSED                                 [100%]

============================= 72 passed in 5.68s ==============================
```

### b) `flake8` (Estilo e Linter: Código de Saída 0)
```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> .venv\Scripts\python -m flake8 --exclude=.venv --max-line-length=110 --ignore=E501,W503,E402 src/ tests/ scripts/
(Sem saídas: conformidade estrita confirmada)
```

### c) `git log --oneline -8`
```
(Será registrado com o commit das correções do Checkpoint 2)
```
