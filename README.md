# 🗳️ Previsão Eleitoral: 1º Turno Presidencial 2026

> **FGV EPGE - Escola Brasileira de Economia e Finanças**  
> **Desafio de Estatística e Econometria | Prof. Valdemar Pinho**  
> Modelo econométrico quantitativo de agregação de pesquisas eleitorais para a previsão dos resultados do 1º turno presidencial de 4 de outubro de 2026.  
> **Horário de corte dos dados:** Sábado, 03/10/2026, às 20h00 BRT (`2026-10-03T20:00:00-03:00`).

---

## 👥 Integrantes do Grupo

- **João Pedro Valuche**
- **Arthur Caron Lyra**
- **Lethicia Manfioletti Possamai**

---

## 🎯 Visão Geral do Desafio

O **Desafio de Estatística e Econometria da FGV EPGE** propõe a modelagem preditiva do 1º turno da Eleição Presidencial de 2026 no Brasil. A entrega oficial compõe-se de:
1. **Planilha XLSX pontual com exatamente 2 abas:**
   - **Aba 1 (Candidatos):** Projeção de votos válidos (%) para os 12 candidatos oficiais do edital, com soma fechada em exatamente **100,0%** (1 casa decimal) pelo método dos maiores restos.
   - **Aba 2 (Adicionais):** Projeção pontual de **Abstenção** (% sobre eleitorado apto), **Votos Brancos** (% sobre comparecimento) e **Votos Nulos** (% sobre comparecimento).
2. **Relatório Metodológico em PDF (até 2 páginas):** Justificativa econométrica, equações formais, faixas de incerteza empíricas e registro do horário de corte.

A métrica soberana de avaliação é o **MAE (Erro Absoluto Médio)** com **peso igual entre todos os 12 candidatos**:
$$\text{MAE} = \frac{1}{12} \sum_{k=1}^{12} |y_k - \hat{y}_k|$$
Candidatos nanicos pesam rigorosamente o mesmo que os líderes polarizados, tornando crucial mitigar distorções de arredondamento e evitar prever 0,0% para candidaturas com histórico de votos.

---

## 📊 Projeção Oficial de Votos Válidos (Aba 1)

| Candidato(a) | Partido | Previsão (%) | Resultado Oficial TSE (%) | Erro Absoluto (p.p.) |
| :--- | :--- | :---: | :---: | :---: |
| **Augusto Cury** | Avante | *A definir (CP4)* | - | - |
| **Clariana Barão** | Democracia Cristã (DC) | *A definir (CP4)* | - | - |
| **Edmilson Costa** | PCB | *A definir (CP4)* | - | - |
| **Flávio Bolsonaro** | PL | *A definir (CP4)* | - | - |
| **Hertz Dias** | PSTU | *A definir (CP4)* | - | - |
| **Luiz Inácio Lula da Silva** | PT | *A definir (CP4)* | - | - |
| **Renan Santos** | Missão | *A definir (CP4)* | - | - |
| **Ronaldo Caiado** | PSD | *A definir (CP4)* | - | - |
| **Romeu Zema** | Novo | *A definir (CP4)* | - | - |
| **Rui Costa Pimenta** | PCO | *A definir (CP4)* | - | - |
| **Samara Martins** | UP | *A definir (CP4)* | - | - |
| **Wilson Grassi** | Democrata | *A definir (CP4)* | - | - |
| **Total Votos Válidos** | | **100,0%** | **100,0%** | - |

*Aba 2 (Agregados Eleitorais):*
- **Abstenção (% sobre aptos):** *A definir no Checkpoint 4*
- **Votos Brancos (% sobre comparecimento):** *A definir no Checkpoint 4*
- **Votos Nulos (% sobre comparecimento):** *A definir no Checkpoint 4*

---

## 🔬 Metodologia Econométrica

### 1. Modelos Candidatos no Pré-Registro
Todos os modelos possuem no máximo **2 hiperparâmetros** com grades discretas e pré-fixadas em [PRE_REGISTRO.md](file:///c:/Users/PedroValuchedeAndrad/Desktop/university/modelagem%20eleições/PRE_REGISTRO.md):

- **M0 (Baseline de Parcimônia):** Média simples da última pesquisa de cada instituto na janela final de 21 dias. Zero hiperparâmetros livres.
- **M1 (Média Ponderada Temporal):** Ponderação exponencial decrescente pela recência combinada com a raiz quadrada do tamanho amostral:
  $$w_{i} = \sqrt{N_i} \cdot \exp\left(-\frac{\ln(2) \cdot \Delta t_i}{h}\right), \quad h \in \{7, 14, 21\} \text{ dias}$$
- **M2 (Correção de House Effect com Shrinkage Bayesiano):** Correção do viés institucional particionado por bloco político (`PT`, `Principal Adversário`, `Demais`), com encolhimento empírico dependente do número de eleições prévias do instituto ($n_j$):
  $$\beta_{j, b} = \frac{n_j}{n_j + k} \cdot \bar{\beta}_{j, b}, \quad k \in \{1, 3, 10\}$$
  *Decisão Unificada:* Ipec é tratado formalmente como continuador operacional do Ibope.
- **M3 (Regressão Regularizada Ridge):** Projeção regularizada com base exclusivamente em features observáveis pré-definidas: média das pesquisas ($X_1$), incumbência federal governista ($X_2 \in \{0, 1\}$) e ranking ordinal na média das pesquisas ($X_3 \in \{1, \dots, 12\}$). Baniu-se qualquer categorização ideológica subjetiva.

### 2. Protocolo Oficial de Decisão e Regra de Desempate
- **Critério Soberano:** O modelo vencedor será selecionado pelo menor MAE médio nas 3 janelas prospectivas temporais da validação por **expanding window**:
  - Teste 2014 (treinado em 2006-2010)
  - Teste 2018 (treinado em 2006-2014)
  - Teste 2022 (treinado em 2006-2018)
- **Empate Técnico e Parcimônia:** Se a diferença média de MAE for inferior a 1 erro-padrão amostral dessas diferenças ($|\bar{\Delta}| < \text{SE}(\Delta)$), prevalece compulsoriamente o modelo mais simples:
  $$\text{M0} \prec \text{M1} \prec \text{M2} \prec \text{M3}$$
- **Limitação Amostral ($n=3$):** Reconhecimento formal de que dispomos de 3 pontos de validação temporal prospectiva.

### 3. Mecanismos Especiais Pré-Registrados
- **Viés Comum da Eleição:** Correção do viés sistêmico médio de todos os institutos, condicionada a demonstrar ganho empírico estrito no backtest.
- **Voto Útil de Reta Final:** Modelagem da migração tardia de eleitores do 3º e 4º colocados em direção ao Top-2 polarizado, ativada somente se reduzir o MAE no expanding window.
- **Priors de Candidatos Nanicos:** Combinação convexa da intenção da pesquisa com a mediana histórica das respectivas legendas no TSE (2006-2022), mitigando ruído de arredondamento e o risco de projeções nulas.
- **Fechamento Hamilton (Maiores Restos):** Garante a soma exata de 100,0% com 1 casa decimal sem arbitrariedade discricionária.

---

## 📁 Dados e Rastreabilidade

O projeto adota rastreabilidade estrita em [data/MANIFEST.csv](file:///c:/Users/PedroValuchedeAndrad/Desktop/university/modelagem%20eleições/data/MANIFEST.csv) com hash SHA-256 e timestamp UTC de download:
- **Base TSE (2006-2022):** Consolidação oficial de votos nominais, abstenção, brancos e nulos diretamente dos microdados brutos do Tribunal Superior Eleitoral.
- **Pesquisas Históricas (2006-2022):** 109 pesquisas na janela final de 3 semanas, com revisão permanente via Wikipedia `oldid` e partição limpa de dados (tracking Vox Populi 2010 filtrado a cada 4 dias para zero sobreposição de entrevistas).
- **Pesquisas 2026:** Transcrição direta de fontes primárias com teste contextual automatizado (raio de 130 caracteres) e conferência de protocolos no PesqEle do TSE.

---

## 💻 Como Reproduzir

### 1. Clonagem e Configuração do Ambiente

```powershell
# Clonar o repositorio
git clone https://github.com/pvaluche/trabalho-econometria-a1.git
cd "trabalho-econometria-a1"

# Criar e ativar o ambiente virtual (Python 3.11+)
python -m venv .venv
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Execução da Suíte de Testes

```powershell
# Executar todos os 72 testes automatizados
.\.venv\Scripts\python -m pytest -v
```

### 3. Verificação de Código e Linter

```powershell
# Conformidade estrita PEP 8
.\.venv\Scripts\python -m flake8 --exclude=.venv --max-line-length=110 --ignore=E501,W503,E402 src/ tests/ scripts/
```

### 4. Execução do Pipeline Completo (Dia da Eleição)

```powershell
# Executa a esteira analitica completa, validacao do XLSX e exportacao do dashboard
powershell -ExecutionPolicy Bypass -File scripts/rodar_pipeline.ps1
```

---

## 🗂️ Estrutura do Repositório

```text
modelagem eleições/
├── data/
│   ├── raw/               # Microdados brutos do TSE e páginas HTML de pesquisas
│   ├── processed/         # Bases consolidadas em Parquet (TSE e pesquisas históricas)
│   ├── manual/            # pesquisas_2026.csv (rastreabilidade e protocolos do PesqEle)
│   └── MANIFEST.csv       # Hashes SHA-256, URLs de origem e timestamps UTC
├── src/
│   ├── config.py          # Fonte da verdade: 12 candidatos do edital, datas e parâmetros
│   ├── download.py        # Coleta automatizada com registro no manifesto
│   ├── tse.py             # Agregação nacional e sanidade dos dados do TSE
│   ├── pesquisas.py       # Padronização e filtros de pesquisas eleitorais
│   ├── conversao.py       # Conversão proporcional para votos válidos
│   ├── arredondamento.py  # Algoritmo dos maiores restos (Hamilton) para 100,0%
│   ├── metricas.py        # Cálculo do MAE oficial da FGV EPGE
│   ├── filtros.py         # Filtros causais por véspera de eleição (zero vazamento)
│   └── export.py          # Exportação e validação da planilha XLSX oficial
├── tests/
│   ├── test_pipeline.py   # 71 testes unitários, de integração e transcrição
│   └── test_sanity.py     # Teste de sanidade do ambiente
├── reports/               # Relatórios formais de auditoria (Checkpoints 0 a 4)
├── docs/
│   └── ENTENDIMENTO.md    # Fundamentação teórica, literatura e equações
├── scripts/
│   ├── coletar_pesquisas_historicas.py # Parser de pesquisas 2006-2022
│   ├── processar_tse_historico.py      # Agregação dos microdados do TSE
│   ├── validar_entrega.py              # Validador estrito da planilha XLSX
│   └── rodar_pipeline.ps1              # Script PowerShell de execução ponta a ponta
├── PRE_REGISTRO.md        # Pré-registro imutável + Emendas 1 e 2 datadas
├── DECISOES.md            # Caderno de registro cronológico de decisões técnicas
└── requirements.txt       # Dependências congeladas do projeto
```

---

## 🛡️ Status de Governança e Auditoria Externa

| Checkpoint | Escopo | Status |
| :---: | :--- | :---: |
| **0** | Fundamentação metodológica (`docs/ENTENDIMENTO.md`) e testes base | ✅ **Aprovado** |
| **1** | Processamento TSE 2006-2022, sanidade 2022 e pesquisas 2026 verificadas | ✅ **Aprovado** |
| **2** | Pesquisas históricas (109 pesquisas) e `PRE_REGISTRO.md` com Emendas 1 e 2 | ⏳ **Auditado (Emenda 2 Submetida)** |
| **3** | Backtest comparativo (Expanding Window + LOEO) e seleção do modelo | 🔒 **Congelado (Aguardando Liberação)** |
| **4** | Previsão oficial 2026, planilha XLSX auditada e rascunho do PDF metodológico | 🔒 **Pendente** |

---

## 📚 Referências Bibliográficas Verificadas

- **Jackman, S. (2005).** "Pooling the Polls Over an Election Campaign." *Australian Journal of Political Science*, 40(4), 499-517. DOI: `10.1080/10361140500302472`.
- **Linzer, D. A. (2013).** "Dynamic Bayesian Forecasting of Presidential Elections in the States." *Journal of the American Statistical Association*, 108(501), 124-134. DOI: `10.1080/01621459.2012.737735`.
- **Shirani-Mehr, H., Rothschild, D., Goel, S., & Gelman, A. (2018).** "Disentangling Bias and Variance in Election Polls." *Journal of the American Statistical Association*, 113(522), 607-614. DOI: `10.1080/01621459.2018.1460029`.
- **Vehtari, A., Gelman, A., & Gabry, J. (2017).** "Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC." *Statistics and Computing*, 27(5), 1413-1432. DOI: `10.1007/s11222-016-9696-4`.
