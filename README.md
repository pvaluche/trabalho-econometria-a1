# 🗳️ Previsão Eleitoral — 1º Turno Presidencial 2026

> Modelo quantitativo de agregação de pesquisas e previsão de votos válidos para o 1º turno da eleição presidencial brasileira de 2026.
> Desenvolvido para o **Desafio de Estatística e Econometria — FGV EPGE**.

---

## Resultado Final

| Candidato | Previsto (%) | Realizado (%) |
|---|---|---|
| *a preencher após entrega* | — | — |

**MAE médio no backtest (modelo escolhido):** _a preencher_
**Horário de corte dos dados:** Sábado 03/10/2026 — a confirmar

---

## Visão Geral

- **Objetivo:** Prever a porcentagem de votos válidos dos 12 candidatos oficiais no 1º turno e estimar taxas de abstenção, brancos e nulos.
- **Métrica principal:** MAE médio entre previsto e realizado, com peso igual por candidato (conforme edital).
- **Candidatos:** Augusto Cury (Avante), Clariana Barão (DC), Edmilson Costa (PCB), Flávio Bolsonaro (PL), Hertz Dias (PSTU), Lula (PT), Renan Santos (Missão), Ronaldo Caiado (PSD), Romeu Zema (Novo), Rui Costa Pimenta (PCO), Samara Martins (UP), Wilson Grassi (Democrata).

---

## Metodologia Resumida

```
Pesquisas históricas      Dados TSE (2006–2022)
       │                          │
       ▼                          ▼
  Padronização            Agregação nacional
  + Filtros                + Sanidade 2022
       │                          │
       └──────────┬───────────────┘
                  ▼
         Conversão para votos válidos
         (excluir brancos, nulos, indecisos)
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
    M0 / M1 / M2 / M3    Abstenção / Brancos / Nulos
    (backtest LOEO)       (tendência histórica)
        │
        ▼
   Regra de escolha pré-registrada
        │
        ▼
   Previsão 2026 → XLSX + Interface HTML
```

| Modelo | Descrição |
|---|---|
| **M0** | Média simples da última pesquisa por instituto (baseline) |
| **M1** | Média ponderada por recência (meia-vida) e tamanho de amostra |
| **M2** | M1 + correção de house effect com shrinkage bayesiano |
| **M3** | Ridge regression: resultado ~ média das pesquisas + features |

- **Backtest:** leave-one-election-out em 2006, 2010, 2014, 2018 e 2022.
- **Modelo escolhido:** menor MAE médio no backtest, definido no pré-registro antes de qualquer previsão de 2026.
- **Arredondamento:** método dos maiores restos, garantindo soma exata de 100,0%.

---

## Como Reproduzir

### 1. Pré-requisitos

- Python 3.11 ou superior
- Git
- `uv` (gerenciador de pacotes)

### 2. Configuração do ambiente

```powershell
# Clonar o repositório
git clone https://github.com/pvaluche/trabalho-econometria-a1.git
cd "trabalho-econometria-a1"

# Criar e ativar o ambiente virtual
uv venv .venv
.\.venv\Scripts\activate

# Instalar dependências
uv pip install -r requirements.txt
```

### 3. Executar o pipeline completo

No **sábado de entrega**, após atualizar `data/manual/pesquisas_2026.csv`:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/rodar_pipeline.ps1
```

O script executa os notebooks 04 a 06, valida o XLSX gerado e exporta a interface HTML.

### 4. Executar etapas individualmente

```powershell
# Baixar dados históricos do TSE
.\.venv\Scripts\python.exe notebooks/01_tse_historico.ipynb

# Processar pesquisas históricas
.\.venv\Scripts\python.exe -m papermill notebooks/02_pesquisas.ipynb outputs/02_pesquisas_out.ipynb

# Backtest
.\.venv\Scripts\python.exe -m papermill notebooks/03_backtest.ipynb outputs/03_backtest_out.ipynb
```

### 5. Rodar testes

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

---

## Estrutura de Pastas

```
modelagem eleições/
├── data/
│   ├── raw/               # Arquivos brutos do TSE (não versionados)
│   ├── processed/         # Bases processadas em Parquet
│   ├── manual/            # pesquisas_2026.csv (entrada manual)
│   └── MANIFEST.csv       # Proveniência, hashes SHA-256 e timestamps
├── src/
│   ├── config.py          # Parâmetros centrais e caminhos
│   ├── download.py        # Download com hash e registro no manifest
│   ├── tse.py             # Processamento dos dados históricos do TSE
│   ├── pesquisas.py       # Padronização e filtros de pesquisas
│   ├── conversao.py       # Conversão para votos válidos
│   ├── modelos.py         # Modelos M0–M3
│   ├── backtest.py        # Validação leave-one-election-out
│   ├── arredondamento.py  # Método dos maiores restos
│   └── export.py          # Geração do XLSX e dados da interface
├── notebooks/             # Orquestração analítica (Jupyter + papermill)
├── tests/                 # Testes unitários (pytest)
├── interface/             # Dashboard HTML autocontido
├── reports/               # Relatórios de checkpoint para auditoria
├── docs/                  # Documentação teórica
├── outputs/               # Planilha XLSX final, figuras, tabelas
├── scripts/               # rodar_pipeline.ps1 e validar_entrega.py
├── PRE_REGISTRO.md        # Pré-registro imutável dos modelos e regras
├── DECISOES.md            # Registro de decisões metodológicas
└── requirements.txt
```

---

## Checkpoints e Auditoria

| Checkpoint | Conteúdo | Status |
|---|---|---|
| **0 — Entendimento** | `docs/ENTENDIMENTO.md` + estrutura do repo | ✅ Em andamento |
| **1 — Base TSE** | Totais nacionais 2006–2022, sanidade 2022 | ⏳ Pendente |
| **2 — Pesquisas + Pré-registro** | Base histórica, `pesquisas_2026.csv`, `PRE_REGISTRO.md` | ⏳ Pendente |
| **3 — Backtest** | MAE por modelo e eleição, modelo escolhido | ⏳ Pendente |
| **4 — Entrega final** | Previsão 2026, XLSX validado, interface, PDF | ⏳ Pendente |

Cada checkpoint é auditado de forma independente pelo Claude antes de avançar.

---

## Limitações Conhecidas

- Apenas 5 eleições disponíveis para treinamento: modelos complexos têm alto risco de overfitting.
- House effects estimados com poucos dados por instituto: shrinkage aplicado.
- Pesquisas históricas de nanicos têm alta variabilidade; prior histórico do TSE é combinado com a pesquisa.
- Fatores qualitativos de 2026 (eleitorado mais velho, transporte gratuito) documentados como contexto, sem entrar no modelo.

---

*Projeto acadêmico — FGV EPGE, Desafio de Estatística e Econometria 2026.*
