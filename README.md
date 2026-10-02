# 🗳️ Previsão Eleitoral — 1º Turno Presidencial 2026

> **Desafio de Estatística e Econometria — Prof. Valdemar Pinho | FGV EPGE**
>
> Modelo quantitativo de agregação de pesquisas eleitorais para previsão dos resultados do 1º turno presidencial de 4 de outubro de 2026.
> Entrega: **03/10/2026 às 22h via Eclass**.

---

## Resultado Final

| Candidato(a) | Partido | Previsto (%) | Realizado (%) | Erro abs. |
|---|---|---|---|---|
| Augusto Cury | Avante | — | — | — |
| Clariana Barão | DC | — | — | — |
| Edmilson Costa | PCB | — | — | — |
| Flávio Bolsonaro | PL | — | — | — |
| Hertz Dias | PSTU | — | — | — |
| Luiz Inácio Lula da Silva | PT | — | — | — |
| Renan Santos | Missão | — | — | — |
| Ronaldo Caiado | PSD | — | — | — |
| Romeu Zema | Novo | — | — | — |
| Rui Costa Pimenta | PCO | — | — | — |
| Samara Martins | UP | — | — | — |
| Wilson Grassi | Democrata | — | — | — |
| **Total** | | **100,0%** | | |

**MAE médio no backtest (modelo escolhido):** _a preencher após Checkpoint 3_
**Horário de corte dos dados:** Sábado 03/10/2026 — a confirmar no pré-registro

---

## Sobre o Desafio

O **Desafio de Estatística e Econometria da FGV EPGE** pede que cada grupo preveja, com as ferramentas que julgar mais adequadas, a distribuição de votos válidos entre os 12 candidatos oficiais do 1º turno presidencial de 2026, além da abstenção, votos brancos e votos nulos.

A principal métrica de avaliação é o **MAE (Erro Absoluto Médio)** entre previsto e realizado, com **peso igual para cada candidato** — nanicos pesam tanto quanto Lula e Flávio Bolsonaro. Isso penaliza quem arredonda candidatos com menos de 1% para zero.

> "Uma estratégia simples e bem justificada pode ser superior a um modelo excessivamente complexo." — Edital do Desafio

**Entregáveis obrigatórios:**
1. Planilha `.xlsx` com exatamente 2 abas: votos válidos por candidato (somando 100,0%) e abstenção/brancos/nulos.
2. PDF de até 2 páginas com a metodologia e o horário de corte dos dados.

---

## Nossa Abordagem

### Pipeline de dados

```
Pesquisas históricas (2006-2022)    Dados TSE (2006-2022)
      + pesquisas_2026.csv                  |
              |                      Agregação nacional
              v                      + Sanidade 2022
       Padronização                         |
       + Filtros                            |
              |                             |
              +----------+------------------+
                         |
              Conversão para votos válidos
              (excluir brancos, nulos, indecisos)
                         |
           +-------------+-------------+
           |             |             |
          M0            M1            M2            M3
        (baseline)  (ponderado)  (house effect)  (Ridge)
           |
    Backtest leave-one-out (2006-2022)
    + Expanding window para comparação
           |
    Regra de escolha (menor MAE médio, pré-registrada)
           |
    Previsão 2026 → XLSX + Interface HTML + Figuras do PDF
```

### Modelos testados

| Modelo | Descrição |
|---|---|
| **M0** | Média simples da última pesquisa por instituto (baseline) |
| **M1** | Média ponderada por recência (meia-vida) e tamanho de amostra |
| **M2** | M1 + correção de house effect relativo com shrinkage bayesiano para zero |
| **M3** | Ridge regression: resultado ~ média das pesquisas + features (incumbente, campo ideológico, ranking) |

### Validação e anti-overfitting

- **Backtest leave-one-election-out** em 2006, 2010, 2014, 2018 e 2022.
- **Expanding window** em paralelo (2014 com 2006-2010; 2018 com 2006-2014; 2022 com 2006-2018) para checar se o LOEO inflaciona a performance.
- **Pré-registro** (tag `pre-registro` no Git) antes de qualquer previsão de 2026 entrar no pipeline.
- Máximo de 2 hiperparâmetros por modelo; grade declarada antes do backtest.
- Arredondamento por **método dos maiores restos** — soma exata de 100,0%.

### Candidatos nanicos

Candidatos com historicamente menos de 1% nas pesquisas recebem um **prior a partir do histórico do TSE 2006-2022** combinado com a pesquisa, evitando prever zero e penalizar desnecessariamente o MAE.

### Abstenção, brancos e nulos

Três abordagens comparadas via leave-one-out:
1. Último valor observado
2. Média histórica 2006-2022
3. Tendência linear

Denominadores: abstenção sobre eleitorado apto; brancos e nulos sobre votos registrados (comparecimento).

---

## Como Reproduzir

### Pré-requisitos

- Python 3.11 ou superior
- Git (MinGit funciona)

### Configuração do ambiente

```powershell
git clone https://github.com/pvaluche/trabalho-econometria-a1.git
cd "trabalho-econometria-a1"

# Criar e ativar o ambiente virtual
uv venv .venv
.\.venv\Scripts\activate

# Instalar dependências
uv pip install -r requirements.txt
```

### Pipeline completo (dia da entrega)

1. Atualizar `data/manual/pesquisas_2026.csv` com as pesquisas divulgadas no sábado.
2. Executar:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/rodar_pipeline.ps1
```

O script executa os notebooks 04-06, valida o XLSX e exporta a interface HTML. Tempo estimado: menos de 5 minutos.

### Rodar testes

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
│   ├── config.py          # Parâmetros centrais, candidatos, horário de corte
│   ├── download.py        # Download com hash SHA-256 e registro no manifest
│   ├── tse.py             # Processamento dos dados históricos do TSE
│   ├── pesquisas.py       # Padronização e filtros de pesquisas
│   ├── conversao.py       # Conversão para votos válidos (critério TSE)
│   ├── modelos.py         # Modelos M0-M3
│   ├── backtest.py        # Validação leave-one-election-out + expanding window
│   ├── arredondamento.py  # Método dos maiores restos (soma exata 100,0%)
│   └── export.py          # Geração do XLSX e dados da interface
├── notebooks/             # Orquestração analítica (Jupyter + papermill)
├── tests/                 # Testes unitários (pytest)
├── interface/             # Dashboard HTML autocontido
├── reports/               # Relatórios de checkpoint para auditoria
├── docs/                  # ENTENDIMENTO.md com fundamentação teórica
├── outputs/               # Planilha XLSX final, figuras, tabelas
├── scripts/               # rodar_pipeline.ps1 e validar_entrega.py
├── PRE_REGISTRO.md        # Pré-registro imutável (modelos, grades, regra)
├── DECISOES.md            # Registro cronológico de decisões metodológicas
└── requirements.txt
```

---

## Checkpoints e Auditoria

| # | Conteúdo | Status |
|---|---|---|
| **0 - Entendimento** | `docs/ENTENDIMENTO.md` + módulos base + testes | ✅ Aprovado pelo Claude |
| **1 - Base TSE** | Totais nacionais 2006-2022, sanidade 2022 (Lula 48,43% / Bolsonaro 43,20% / Abstenção 20,95%), Parquet limpos, Leonardo Avalanche verificado | ✅ Concluído |
| **2 - Pesquisas + Pré-registro** | Base histórica padronizada, `pesquisas_2026.csv`, `PRE_REGISTRO.md` | ⏳ Próximo |
| **3 - Backtest** | MAE por modelo e eleição (LOEO + expanding window), ablation, modelo escolhido | ⏳ Pendente |
| **4 - Entrega final** | Previsão 2026, XLSX validado, interface, rascunho do PDF | ⏳ Pendente |

Cada checkpoint é auditado de forma independente antes de avançar.

---

## Limitações Conhecidas

- Apenas 5 eleições históricas disponíveis: janela muito estreita para modelos complexos.
- House effects estimados com shrinkage para zero em institutos com histórico limitado.
- Padrão de subestimação do candidato bolsonarista (2018: -6 p.p.; 2022: -7 p.p.) é tratado como viés comum da eleição: difícil de corrigir sem overfitting ao regime mais recente.
- Voto útil e decisão tardia do eleitor: efeito documentado mas não modelável de forma validável.
- Candidatos nanicos (menos de 1% nas pesquisas): alto ruído relativo; prior histórico do TSE mitiga o risco de prever zero.

---

## Referências Principais

| Referência | DOI verificado |
|---|---|
| Jackman (2005) — *Australian J. Political Science* | `10.1080/10361140500302472` |
| Linzer (2013) — *JASA* | `10.1080/01621459.2012.737735` |
| Shirani-Mehr et al. (2018) — *JASA* | `10.1080/01621459.2018.1460029` |
| Vehtari, Gelman & Gabry (2017) — *Statistics and Computing* | arXiv:1507.04544 |

---

*Projeto acadêmico — Desafio de Estatística e Econometria, FGV EPGE, 2026.*
*Grupo: Pedro Valuche de Andrade.*
