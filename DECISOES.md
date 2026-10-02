# Registro de Decisoes Metodologicas e Tecnicas

Este documento registra todas as decisoes tomadas ao longo do projeto de previsao eleitoral do 1o turno de 2026, com data, alternativas consideradas e motivacao.

---

## 2026-10-02: Inicializacao do Projeto e Estrutura de Repositorio

- **Decisao:** Adotar estrutura modular em Python (`src/`) combinada com notebooks Jupyter headless orquestrados por `papermill`, ambiente virtual isolado com `uv` e controle de versao Git.
- **Alternativas consideradas:**
  1. Utilizar apenas scripts Python em linha de comando.
  2. Utilizar apenas notebooks sem modulos reutilizaveis.
- **Motivo:** A abordagem modular com `src/` permite testes unitarios automatizados via `pytest` e reaproveitamento de logica sem duplicacao, enquanto os notebooks documentam o passo a passo analitico de forma visual e reproduzivel.

---

## 2026-10-02: Gerenciador de Ambientes e Pacotes

- **Decisao:** Uso de `uv` e `pip` para gerenciar dependencias com especificacao em `requirements.txt`.
- **Alternativas consideradas:** Conda/Mamba, Poetry, venv nativo sem uv.
- **Motivo:** O `uv` oferece desempenho significativamente mais rapido em sistemas Windows, facilitando a reproducibilidade e instalacao rapida em pipelines automatizados.
