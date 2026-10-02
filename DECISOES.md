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

---

## 2026-10-02: Extracao e Processamento dos Dados Historicos do TSE (2006-2022)

- **Decisao:** Utilizacao dos arquivos `_BR.csv` contidos nos arquivos ZIP de `detalhe_votacao_munzona` e `votacao_candidato_munzona` para todas as 5 eleicoes presidenciais (2006 a 2022), filtrando `CD_CARGO == 1` e `NR_TURNO == 1`, e persistindo os dados limpos em formato Parquet em `data/processed/`.
- **Alternativas consideradas:**
  1. Processar os arquivos estaduais somando UF por UF.
  2. Processar os arquivos `_BRASIL.csv` de mais de 4 GB.
- **Motivo:** Os arquivos `_BR.csv` contem a totalizacao de todas as zonas eleitorais do pais especificamente para o cargo Presidente (UE Brasil), evitando carregar gigabytes de cargos estaduais e proporcionando processamento rapido e exato.

---

## 2026-10-02: Situacao de Leonardo Avalanche (PRTB) e Candidaturas 2026

- **Decisao:** Confirmar a lista de 12 candidatos do edital FGV EPGE como a lista oficial para a previsao e normalizacao de votos validos. No arquivo oficial `consulta_cand_2026.zip` do TSE, o campo `DS_SITUACAO_CANDIDATURA` consta literalmente como `#NE`, codigo tecnico do TSE que indica campo sem informacao (e nao "nao enquadrado"), enquanto `DS_DETALHE_SITUACAO_CAND` esta vazio.
- **Ressalva importante registrada:** Caso Leonardo Avalanche venha a constar na urna eletronica e receber votos validos apurados pelo TSE, a soma dos votos validos dos 12 candidatos do edital sera estritamente inferior a 100,0% no resultado real oficial. Para a entrega do Desafio da FGV EPGE, os votos validos sao normalizados para somar exatamente 100,0% entre os 12 candidatos previstos no edital.

---

## 2026-10-02: Tratamento de Datas de Pesquisas Historicas (Backtest 2006-2022)

- **Decisao:** Para pesquisas eleitorais historicas extraidas de tabelas da Wikipedia ou repositorios que informam apenas o periodo de coleta (datas de inicio e fim de campo), adotar a `data_fim_campo` como proxy da data de divulgacao quando a data exata de publicacao nao estiver disponivel.
- **Alternativas consideradas:**
  1. Estimar uma defasagem fixa de 1 ou 2 dias apos o fim do campo.
  2. Descartar pesquisas que nao apresentem a data de divulgacao explicitamente separada do campo.
- **Motivo:** A utilizacao da data final de campo e a abordagem mais conservadora e reprodutivel para filtros temporais, garantindo que pesquisas cujos dados de campo se encerraram apos a vespera sejam rigorosamente excluidas do backtest.

---

## 2026-10-02: Politica de Integridade do Controle de Versao Git

- **Decisao:** Proibido o uso de `git push --force` na branch `main`. Atualizacoes forcadas sao restritas exclusivamente a movimentacao de tags de checkpoint (`git tag -f <tag> && git push -f origin <tag>`).
- **Motivo:** Preservar a integridade linear do historico do repositorio no GitHub, evitando sobrescrita acidental de commits.
