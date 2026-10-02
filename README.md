# Previsao Eleitoral: 1o Turno Presidencial 2026

Modelo quantitativo de agregacao de pesquisas e previsao de votos validos para o 1o turno da eleicao presidencial de 2026, com estimativas de abstencao, votos brancos e nulos. Desenvolvido para o Desafio de Estatistica e Econometria (FGV EPGE).

## Visao Geral

- **Objetivo:** Prever a porcentagem de votos validos dos 12 candidatos oficiais no 1o turno e estimar taxas de abstencao, brancos e nulos.
- **Metrica Principal:** MAE (Mean Absolute Error) medio entre previsto e realizado nos 12 candidatos, com peso igual por candidato.
- **Horario de Corte:** Sabado 03/10/2026, a ser definido e travado no pre-registro.

## Estrutura do Repositorio

```text
modelagem eleicoes/
  data/
    raw/                 Arquivos brutos baixados (nao versionados)
    processed/           Bases processadas em formato Parquet
    manual/              pesquisas_2026.csv (entrada manual)
    MANIFEST.csv         Registro de procedencia e hashes de arquivos
  src/                   Modulos reutilizaveis e testaveis
    config.py            Parametros centrais e caminhos
    download.py          Download com hash e metadados
    tse.py               Processamento dos dados historicos do TSE
    pesquisas.py         Processamento e padronizacao de pesquisas
    conversao.py         Conversao para votos validos
    modelos.py           Implementacao dos modelos M0 a M3
    backtest.py          Validacao leave-one-election-out
    arredondamento.py    Metodo dos maiores restos para soma exata de 100,0%
    export.py            Geracao da planilha XLSX e dados da interface
  notebooks/             Execucao e orquestracao analitica
  tests/                 Testes unitarios automatizados (pytest)
  interface/             Dashboard interativo autocontido (HTML/JS/CSS)
  reports/               Relatorios formais de checkpoints para auditoria
  docs/                  Documentacao teorica e de entendimento
  outputs/               Planilha XLSX final, figuras e tabelas
  scripts/               Scripts de execucao e validacao
```

## Como Reproduzir

1. Instalar Python 3.11 ou superior e Git.
2. Criar ambiente virtual e instalar dependencias:
   ```bash
   uv venv .venv
   .\.venv\Scripts\activate
   uv pip install -r requirements.txt
   ```
3. Executar o pipeline completo via script:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/rodar_pipeline.ps1
   ```

## Status do Projeto

- **Fase Atual:** Checkpoint 0 (Entendimento e Fundamentacao Teorica).
- **Auditoria:** Submetido a revisao independente e auditoria externa.
