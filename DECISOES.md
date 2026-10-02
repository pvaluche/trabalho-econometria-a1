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

---

## 2026-10-02: Tratamento e Transcricao Verificada das Pesquisas de 2026

- **Decisao:** Toda e qualquer linha em `data/manual/pesquisas_2026.csv` deve possuir pagina HTML correspondente salva em `data/raw/pesquisas_2026/`, registrada no `data/MANIFEST.csv` com SHA-256 e timestamp ISO real de download utilizado no campo `verificado_em`.
- **Regra para Nanicos e Agregados:**
  1. Candidatos nao divulgados individualmente pelo instituto recebem valor vazio (`NaN`), e nao `0.0`. O valor `0.0` e estritamente reservado para casos em que o instituto publicou explicitamente 0% ou declarou que o candidato nao pontuou.
  2. Adicionada a coluna `outros_agregado` para acomodar o percentual de institutos que agrupam os demais concorrentes em bloco (ex.: AtlasIntel com 0,5% e Real Time Big Data com 1,0%).
- **Conferencia Pontual dos Institutos:**
  1. **AtlasIntel (29/09, BR-04391/2026):** Votos brancos/nulos ajustados para 0,9% e indecisos para 1,2%. Nanicos individuais nao discriminados como `NaN`, com `outros_agregado = 0.5%`.
  2. **PoderData/Aya (24/09, BR-01739/2026):** Frase literal da reportagem: "Romeu Zema (Novo), Rui Costa Pimenta (PCO), Samara Martins (UP) e Clariana Barão (Democracia Cristã) registram 1% cada um. Wilson Grassi (Democrata), Leonardo Avalanche (PRTB), Hertz Dias (PSTU) e Edmilson Costa (PCB) não pontuam. Outros 4% afirmaram que pretendem votar em branco ou anular, enquanto 2% não souberam responder." Atribuidos: Zema 1%, Rui 1%, Samara 1%, Clariana 1%, Wilson 0%, Hertz 0%, Edmilson 0%, e `outros_agregado` vazio.
  3. **Real Time Big Data (01/10):** Resolucao do numero de registro. A materia da Veja cita textualmente "A pesquisa foi registrada no sistema do Tribunal Superior Eleitoral (TSE) pelo código BR-09503/2026." No PesqEle, `BR095032026` corresponde a REAL TIME BIG DATA, cargo Presidente, campo 26 a 30 de setembro, divulgacao em 01/10/2026 e amostra de 2.000 eleitores. Registrado `outros_agregado = 1.0%` e nanicos individuais como `NaN`.
  4. **Datafolha (01/10, BR-08039/2026):** Inclusa a rodada final de 28/09 a 01/10 com amostra de 2.506 eleitores, mantendo a rodada de 22-24/09 como observacao separada.
- **Teste Automatizado de Transcricao:** Criado teste no pipeline (`test_transcricao_pesquisas_2026_contra_html_salvo`) que valida que cada celula numerica nao-NaN de `pesquisas_2026.csv` existe comprovadamente no texto do arquivo HTML bruto correspondente.

---

### Decisao 7: Auditoria do Checkpoint 2 (Ajustes de Pesquisas Historicas, Transcricao Estrita e Emenda 1)
**Data:** 02/10/2026  
**Contexto:** Parecer da auditoria externa (Claude) exigindo:
1. Endurecimento do teste de transcricao para exigir que o valor numerico apareca em uma janela maxima de 80 caracteres do nome do candidato ou rotulo correspondente, e validacao estrita de zero;
2. Tratamento agregado dos nanicos no PoderData/Aya (coluna outros_agregado = 4.0 e nanicos individuais como NaN);
3. Verificacao da amostra de 2.506 no PesqEle para o Datafolha BR-08039/2026;
4. Padronizacao rigorosa de institutos via dicionario prioritario com criacao de coluna contratante separada (evitando associar parceiros como Globo ou XP ao nome do instituto);
5. Teste de sanidade historica das vesperas do Datafolha sobre votos validos (2014, 2018 e 2022);
6. Documentacao dos revision IDs (oldid) da Wikipedia e da fonte primária de 2006 (UOL Eleicoes 2006);
7. Registro de Emenda 1 ao PRE_REGISTRO.md em commit dedicado antes do backtest.

- **Decisoes Tomadas:**
  1. **Aproximacao Temporal em Pesquisas Historicas:** Nas pesquisas da Wikipedia (2010 a 2022) em que a data exata de divulgacao nao e discriminada em coluna isolada, utiliza-se a data final do periodo de campo (`data_fim_campo`) como aproximacao conservadora da data de divulgacao. Isso garante que nenhuma informacao posterior a vespera seja admitida no backtest, eliminando risco de vazamento temporal.
  2. **PoderData/Aya (BR-01739/2026):** A reportagem informa: "Romeu Zema (Novo), Rui Costa Pimenta (PCO), Samara Martins (UP) e Clariana Barão (Democracia Cristã) registram 1% cada um. Wilson Grassi (Democrata), Leonardo Avalanche (PRTB), Hertz Dias (PSTU) e Edmilson Costa (PCB) não pontuam." Como a mencao e feita em bloco coletivo e nao em cartela individualizada isolada, os 7 candidatos nanicos do edital foram convertidos para `NaN` e o valor total desse grupo (1% x 4 = 4,0%) foi registrado em `outros_agregado = 4.0`. A soma total de intencoes (41 + 39 + 6 + 3 + 2 + 4 + 4 + 2) totaliza 101,0%, perfeitamente conforme ao intervalo [97, 101.5].
  3. **Datafolha BR-08039/2026 e PesqEle:** Confirmado no arquivo oficial do TSE (`pesquisa_eleitoral_2026.zip`, tabela `pesquisa_eleitoral_2026_BRASIL.csv`) que o registro BR080392026 possui literalmente `QT_ENTREVISTADO: 2506`, confirmando o numero utilizado na base.
  4. **Estruturacao de Institutos e Contratantes:** Criada a funcao `padronizar_instituto_e_contratante`, apoiada em um dicionario ordenado de institutos prioritarios e mapeamento de contratantes. No arquivo `pesquisas_historicas.parquet`, as colunas `instituto` e `contratante` coexistem de forma independente.
  5. **Sanidade das Vesperas Datafolha:** Teste implementado em `tests/test_pipeline.py::TestSanidadeVesperasDatafolha` comprovando que os votos validos calculados a partir das pesquisas de vespera do Datafolha conferem com os dados historicos: 2022 (Lula 50,5% ~ 50% / Bolsonaro 35,8% ~ 36%), 2018 (Bolsonaro 40,9% ~ 40% / Haddad 25,0%), 2014 (Dilma 44,9% ~ 44% / Aecio 27,0% ~ 26% / Marina 24,7% ~ 24%), todos a menos de 1,0 p.p. de tolerancia.
  6. **Revision IDs da Wikipedia no MANIFEST:** Identificados os revision IDs exatos nos HTMLs brutos salvos e adicionadas as URLs permanentes no `MANIFEST.csv`: 2010 (`oldid=73055941`), 2014 (`oldid=73055945`), 2018 (`oldid=73055947`), 2022 (`oldid=73055949`).
  7. **Fonte de 2006:** A cobertura de 2006 baseia-se nos relatorios compilados e publicados pelo arquivo historico do UOL Eleicoes 2006 (noticiando Datafolha, Ibope e CNT/Sensus), arquivados em `data/raw/pesquisas_historicas/` com links e hashes no `MANIFEST.csv`.

