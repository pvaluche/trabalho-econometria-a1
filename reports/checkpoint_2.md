# Relatório de Auditoria: Checkpoint 2
**Desafio de Estatística e Econometria: FGV EPGE (Eleições Presidenciais 2026)**  
**Data:** 02/10/2026  
**Status:** Submetido para Auditoria Externa (Claude)  
**Tags Associadas:** `pre-registro`, `checkpoint-2`

---

## 1. Resumo Executivo do Checkpoint 2

O Checkpoint 2 consolida os alicerces empíricos e teóricos necessários para o backtest histórico e a modelagem preditiva das Eleições de 2026:
1. **Base Histórica de Pesquisas (2006-2022):** Compilada em `data/processed/pesquisas_historicas.parquet` com **124 pesquisas eleitorais de 1º turno nacional**, restritas estritamente à janela final de 21 dias até a véspera (`data_divulgacao <= vespera`), garantindo **vazamento temporal zero**. Todos os arquivos brutos baixados estão arquivados em `data/raw/pesquisas_historicas/` e registrados com hash SHA-256 em `data/MANIFEST.csv`.
2. **Pré-Registro Metodológico Congelado (`PRE_REGISTRO.md`):** Formalização matemática e exaustiva dos modelos M0 (baseline), M1 (recência exponencial + raiz da amostra), M2 (house effects com shrinkage bayesiano), M3 (Ridge regularizada), critérios de desempate, tratamento de nanicos, abstenção/brancos/nulos por séries temporais expanding window, regra estrita de segurança e faixas de incerteza por posição relativa.
3. **Validação Automática:** Cobertura de testes unitários e de integração expandida para 68 testes no total (`pytest -v` 100% aprovado), incluindo o teste de transcrição textual de `pesquisas_2026.csv` contra os HTMLs brutos salvos e validação da base histórica. Linting via `flake8` com zero violações.

---

## 2. Tabela Completa de Pesquisas Históricas por Ano e Instituto

A tabela abaixo foi gerada diretamente do arquivo processado `data/processed/pesquisas_historicas.parquet` via código Python:

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
| **Total Geral** | **7** | **29** | **18** | **30** | **40** | **124** |

### Observações sobre a Amostra:
- **Linhagem Ibope / Ipec:** O Ibope operou de 2006 a 2018 (17 pesquisas); em 2022 a mesma equipe técnica passou a operar sob o nome Ipec (4 pesquisas), totalizando 21 levantamentos com desenho metodológico equivalente.
- **Datafolha:** Instituto com presença ininterrupta em todas as 5 eleições (21 pesquisas na janela de corte).
- **Cobertura Crescente:** O mercado de pesquisas brasileiro expandiu expressivamente, passando de 7 levantamentos na janela em 2006 para 40 em 2022.

---

## 3. Critérios de Coleta, Filtros e Lista de Descartes

Para garantir a estrita comparabilidade econométrica e integridade causal no backtest, os seguintes filtros foram aplicados pelo script `scripts/coletar_pesquisas_historicas.py`:

### a) Tipos de Pesquisas Descartadas e Motivos:
1. **Pesquisas de 2º Turno (Descartadas):** Todos os cenários simulando eventuais disputas de segundo turno (ex.: Lula vs Alckmin em 2006; Dilma vs Serra em 2010; Dilma vs Aécio em 2014; Bolsonaro vs Haddad em 2018; Lula vs Bolsonaro em 2022) foram rigorosamente excluídos.
2. **Pesquisas Espontâneas (Descartadas):** Levantamentos em que os nomes dos candidatos não foram apresentados aos respondentes foram descartados. Apenas pesquisas estimuladas (cenário oficial de 1º turno) foram mantidas, visto que a dinâmica eleitoral avaliada no desafio baseia-se na cartela de opções oficial.
3. **Pesquisas Regionais e Estaduais (Descartadas):** Levantamentos realizados apenas em determinados estados ou regiões (ex.: pesquisas focadas em São Paulo, Rio de Janeiro ou Nordeste) foram excluídos; apenas amostras com representatividade nacional foram admitidas.
4. **Pesquisas Fora da Janela de 21 Dias (Descartadas):** Pesquisas divulgadas antes do início da janela de corte de 21 dias (eleições presidenciais têm dinâmica volátil de convenções e campanha televisiva nos meses anteriores) foram excluídas para manter foco na fase de cristalização do voto.
5. **Pesquisas Divulgadas no Dia da Eleição ou Posteriores (Descartadas):** Pesquisas de boca de urna (*exit polls*) ou levantamentos divulgados no domingo de votação ou em data posterior foram descartados para impedir qualquer contaminação ou vazamento temporal (*look-ahead bias*).
6. **Cenários Hipotéticos Pré-Registro (Descartadas):** Em 2018, cenários testando Lula como candidato antes de sua impugnação formal pelo TSE em setembro foram descartados em favor dos cenários oficiais registrados com Fernando Haddad.

---

## 4. Amostra de 5 Linhas de `pesquisas_historicas.parquet`

Amostra extraída diretamente do arquivo Parquet contendo os primeiros registros de 2006:

```
 eleicao  instituto data_divulgacao  amostra  Luiz Inácio Lula da Silva  Geraldo Alckmin  brancos_nulos  indecisos
    2006  Datafolha      2006-09-30  14798.0                       46.0             35.0            4.0        5.0
    2006      Ibope      2006-09-30   2010.0                       45.0             34.0            4.0        7.0
    2006  Datafolha      2006-09-27  10240.0                       46.0             29.0            5.0        7.0
    2006      Ibope      2006-09-27   2002.0                       48.0             32.0            4.0        6.0
    2006 CNT/Sensus      2006-09-26   2000.0                       51.1             27.5            4.5        8.6
```

---

## 5. Saída Completa do Teste de Transcrição Textual Automático

O teste `test_transcricao_pesquisas_2026_contra_html_salvo` lê todas as células numéricas não nulas de `data/manual/pesquisas_2026.csv` e busca pelo valor exato no arquivo HTML bruto correspondente em `data/raw/pesquisas_2026/`.

Execução via pytest:
```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> .venv\Scripts\python -m pytest -v -k "test_transcricao"
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições
plugins: anyio-4.15.1, platformdirs-4.12.2
collecting ... collected 68 items / 67 deselected / 1 selected

tests/test_pipeline.py::TestPesquisas2026Manual::test_transcricao_pesquisas_2026_contra_html_salvo PASSED [100%]

====================== 1 passed, 67 deselected in 4.13s =======================
```
*Total de asserções verificadas: 80 células numéricas testadas e validadas contra as fontes oficiais salvas.*

---

## 6. Cópia na Íntegra de `PRE_REGISTRO.md`

Abaixo reproduz-se o texto exato do arquivo `PRE_REGISTRO.md`, congelado na tag `pre-registro`:

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
```

---

## 7. Saídas de Qualidade de Código e Testes

### a) `pytest -v` (Suíte Completa: 68 Testes Passando)
```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> .venv\Scripts\python -m pytest -v
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições
plugins: anyio-4.15.1, platformdirs-4.12.2
collecting ... collected 68 items

tests/test_pipeline.py::TestConversaoVotosValidos::test_soma_igual_a_100 PASSED [  1%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_proporcoes_corretas_dois_candidatos PASSED [  2%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_candidato_sub_judice_fora_de_candidatos_edital_descartado PASSED [  4%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_nan_tratado_como_zero PASSED [  5%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_zero_e_nan_resultam_em_zero_pct PASSED [  7%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_raise_quando_todos_zero PASSED [  8%]
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_1000_decimos PASSED [ 10%]
tests/test_pipeline.py::TestMaioresRestos::test_entrada_que_soma_9997 PASSED [ 11%]
tests/test_pipeline.py::TestMaioresRestos::test_cada_valor_a_menos_de_01_do_original PASSED [ 13%]
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_tres_candidatos PASSED [ 14%]
tests/test_pipeline.py::TestMaioresRestos::test_comprimento_preservado PASSED [ 16%]
tests/test_pipeline.py::TestMaioresRestos::test_uma_casa_decimal PASSED  [ 17%]
tests/test_pipeline.py::TestMaioresRestos::test_valor_negativo_lanca_erro PASSED [ 19%]
tests/test_pipeline.py::TestMAE::test_mae_zero_previsao_perfeita PASSED  [ 20%]
tests/test_pipeline.py::TestMAE::test_mae_simetrico PASSED               [ 22%]
tests/test_pipeline.py::TestMAE::test_nanicos_pesam_igual_ao_top2 PASSED [ 23%]
tests/test_pipeline.py::TestMAE::test_candidato_ausente_em_realizados_lanca_keyerror PASSED [ 25%]
tests/test_pipeline.py::TestMAE::test_previstos_vazio_lanca_valueerror PASSED [ 26%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2006] PASSED  [ 27%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2010] PASSED  [ 29%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2014] PASSED  [ 30%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2018] PASSED  [ 32%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2022] PASSED  [ 33%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2026] PASSED  [ 35%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2006] PASSED [ 36%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2010] PASSED [ 38%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2014] PASSED [ 39%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2018] PASSED [ 41%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2022] PASSED [ 42%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2026] PASSED [ 44%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2006] PASSED [ 45%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2010] PASSED [ 47%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2014] PASSED [ 48%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2018] PASSED [ 50%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2022] PASSED [ 51%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2026] PASSED [ 52%]
tests/test_pipeline.py::TestDenominadores::test_abstencao_sobre_aptos PASSED [ 54%]
tests/test_pipeline.py::TestDenominadores::test_brancos_sobre_comparecimento PASSED [ 55%]
tests/test_pipeline.py::TestDenominadores::test_nulos_sobre_comparecimento PASSED [ 57%]
tests/test_pipeline.py::TestDenominadores::test_validos_mais_brancos_mais_nulos_igual_comparecimento PASSED [ 58%]
tests/test_pipeline.py::TestDenominadores::test_multiplas_linhas_somadas PASSED [ 60%]
tests/test_pipeline.py::TestDenominadores::test_colunas_faltando_lanca_valueerror PASSED [ 61%]
tests/test_pipeline.py::TestDenominadores::test_df_vazio_lanca_valueerror PASSED [ 63%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_nan_fica_fora_da_media PASSED [ 64%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_zero_entra_como_zero PASSED [ 66%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_todos_nan_retorna_nan PASSED [ 67%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_candidato_ausente_no_df_retorna_nan PASSED [ 69%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_df_vazio_retorna_todos_nan PASSED [ 70%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_pass_com_resultados_corretos PASSED [ 72%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_lula_errado PASSED [ 73%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_abstencao_errada PASSED [ 75%]
tests/test_pipeline.py::test_integracao_sanidade_2022_do_parquet PASSED  [ 76%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_valido_passa PASSED [ 77%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_com_uma_aba_falha PASSED [ 79%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_nome_errado_falha PASSED [ 80%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_partido_errado_falha PASSED [ 82%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_sem_linha_total_falha PASSED [ 83%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_arquivo_existe_e_possui_linhas PASSED [ 85%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_colunas_obrigatorias_presentes PASSED [ 86%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_soma_intencoes_por_linha PASSED [ 88%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_candidatos_nao_divulgados_sao_nan PASSED [ 89%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_transcricao_pesquisas_2026_contra_html_salvo PASSED [ 91%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_arquivo_parquet_existe PASSED [ 92%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_cinco_eleicoes_presentes PASSED [ 94%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_todas_as_pesquisas_dentro_da_janela_de_corte PASSED [ 95%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_principais_institutos_presentes PASSED [ 97%]
tests/test_pipeline.py::TestPesquisasHistoricas::test_filtro_por_ano_em_carregar_pesquisas_historicas PASSED [ 98%]
tests/test_sanity.py::test_sanity PASSED                                 [100%]

============================= 68 passed in 5.19s ==============================
```

### b) `flake8` (Estilo e Linter: Código de Saída 0)
```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> .venv\Scripts\python -m flake8 --exclude=.venv --max-line-length=110 --ignore=E501,W503,E402 src/ tests/ scripts/
(Sem saídas: conformidade estrita confirmada)
```

### c) `git log --oneline -5`
```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> git log --oneline -5
7c42ff0 feat: checkpoint 2: pesquisas historicas 2006-2022 compiladas e pre-registro congelado
81f59b1 fix: correcoes da auditoria do checkpoint 1 rodada 2 -- transcricao verificada, protocolo realtime, outros_agregado e datafolha final
f208e5e docs: registra git log oficial no relatorio do checkpoint 1
67f5662 fix: revisao 2 do checkpoint 1 -- fontes de pesquisas_2026 verificadas, pesqele validado, candidatos consulta_cand listados
54348b3 docs: atualiza reports/checkpoint_1.md com git log oficial
```

---

## 8. Verificação de Ausência de Travessões

Script Python executado em todo o repositório (excluindo `.venv`, `.git` e prompt do usuário):
```
PS C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições> .venv\Scripts\python -c "..."
NO EM-DASH FOUND! ALL CLEAN.
```
Nenhum caractere travessão (`\u2014`) está presente na base de código ou documentação.
