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

- **Decisao:** Confirmar a lista de 12 candidatos do edital FGV EPGE como a lista oficial para normalizacao de votos validos. Leonardo Avalanche (PRTB) consta com situacao `#NE` (nao homologado/deferido) no arquivo oficial do TSE e fora da lista do edital; portanto, seus eventuais registros nao entram no denominador de validos da entrega final.
- **Alternativas consideradas:**
  1. Incluir Leonardo Avalanche como 13o candidato com divisao proporcional.
  2. Desconsiderar sem registro formal.
- **Motivo:** O edital do Desafio da FGV EPGE fixa taxativamente os 12 candidatos para a Aba 1 da planilha de entrega. A consulta ao TSE confirma que a candidatura nao esta ativa/deferida.
