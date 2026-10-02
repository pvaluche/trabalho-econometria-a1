# Checkpoint 1: Base Historica do TSE e Candidaturas 2026

**Data:** 02/10/2026
**Projeto:** Previsao do 1o Turno Presidencial 2026
**Desafio:** Estatistica e Econometria, FGV EPGE
**Tag:** `checkpoint-1`

---

## 1. O que foi feito

1. **Download e Integridade (TSE):**
   - Baixados os arquivos oficiais de `detalhe_votacao_munzona` e `votacao_candidato_munzona` para todas as 5 eleicoes presidenciais (2006, 2010, 2014, 2018 e 2022).
   - Baixado o arquivo oficial `consulta_cand_2026.zip`.
   - Todos os 11 arquivos brutos registrados em `data/MANIFEST.csv` com URL, data/hora exata, tamanho em bytes e hash SHA-256.

2. **Processamento e Parquet:**
   - Extraidos e processados os arquivos `_BR.csv` (totalizacao de todas as zonas eleitorais do pais especificamente para o cargo Presidente, UE Brasil).
   - Filtrados com precisao: `CD_CARGO == 1` e `NR_TURNO == 1`.
   - Salvos em `data/processed/` em formato Parquet limpo:
     - `detalhe_votacao_2006.parquet` (6.292 linhas)
     - `votacao_candidato_2006.parquet` (41.443 linhas)
     - `detalhe_votacao_2010.parquet` (6.459 linhas)
     - `votacao_candidato_2010.parquet` (50.614 linhas)
     - `detalhe_votacao_2014.parquet` (6.548 linhas)
     - `votacao_candidato_2014.parquet` (65.404 linhas)
     - `detalhe_votacao_2018.parquet` (6.273 linhas)
     - `votacao_candidato_2018.parquet` (81.120 linhas)
     - `detalhe_votacao_2022.parquet` (6.283 linhas)
     - `votacao_candidato_2022.parquet` (69.113 linhas)

3. **Sanidade Obrigatoria de 2022:**
   - Lula: **48,43%** dos validos (calculado: 48,4307%)
   - Jair Bolsonaro: **43,20%** dos validos (calculado: 43,1976%)
   - Abstencao: **20,95%** dos aptos (calculado: 20,9461%)
   - Brancos: **1,59%** do comparecimento
   - Nulos: **2,82%** do comparecimento
   - Sanidade conferida contra os numeros oficiais e aprovada com tolerancia < 0,05 pp.

---

## 2. Item (a): Tabela Historica 2006-2022 do 1o Turno (TSE Oficial)

Calculada diretamente dos arquivos do TSE pelo modulo `src/tse.py`:

| Ano | Eleitorado Apto | Comparecimento | Abstencao (%) | Brancos (%) | Nulos (%) | Votos Validos | 1o Colocado (% validos) | 2o Colocado (% validos) | 3o Colocado (% validos) |
|---|---|---|---|---|---|---|---|---|---|
| **2006** | 125.913.235 | 104.820.459 | 16,75% | 2,73% | 5,68% | 95.996.733 | Lula (48,61%) | Geraldo Alckmin (41,64%) | Heloisa Helena (6,85%) |
| **2010** | 135.804.433 | 111.193.747 | 18,12% | 3,13% | 5,51% | 101.590.153 | Dilma (46,91%) | Jose Serra (32,61%) | Marina Silva (19,33%) |
| **2014** | 142.822.046 | 115.122.883 | 19,39% | 3,84% | 5,80% | 104.023.802 | Dilma (41,59%) | Aecio Neves (33,55%) | Marina Silva (21,32%) |
| **2018** | 147.306.295 | 117.364.654 | 20,33% | 2,65% | 6,14% | 107.050.749 | Jair Bolsonaro (46,03%) | Fernando Haddad (29,28%) | Ciro Gomes (12,47%) |
| **2022** | 156.454.011 | 123.682.372 | 20,95% | 1,59% | 2,82% | 118.229.719 | Lula (48,43%) | Jair Bolsonaro (43,20%) | Simone Tebet (4,16%) |

*Denominadores: Abstencao sobre eleitorado apto; Brancos e Nulos sobre total de votos registrados (comparecimento); % dos candidatos sobre o total de votos validos.*

---

## 3. Item (b): Contagem de Pesquisas na Janela Final (Ultimas 3 Semanas)

Filtro obrigatorio: pesquisas estimuladas nacionais de 1o turno com divulgacao ate a vespera da eleicao. Fontes: Wikipedia PT/EN (artigos de pesquisas de opiniao), agregadores historicos e TSE/Poder360.

| Eleicao | Data 1o Turno | Vespera (corte) | Total Pesquisas (3 semanas) | Institutos Principais | Fonte da Base |
|---|---|---|---|---|---|
| **2006** | 01/10/2006 | 30/09/2006 | 12 | Datafolha (4), Ibope (4), Sensus/CNT (2), Vox Populi (2) | Wikipedia PT / Repositorio Eleitoral |
| **2010** | 03/10/2010 | 02/10/2010 | 16 | Datafolha (5), Ibope (5), Sensus/CNT (3), Vox Populi (3) | Wikipedia PT (Tabela 2) |
| **2014** | 05/10/2014 | 04/10/2014 | 19 | Datafolha (6), Ibope (6), MDA/CNT (4), Vox Populi (3) | Wikipedia PT (Tabela 1) |
| **2018** | 07/10/2018 | 06/10/2018 | 26 | Datafolha (7), Ibope (7), MDA/CNT (3), Parana Pesquisas (3), Real Time Big Data (3), BTG/FSB (3) | Wikipedia PT (Tabela 2) |
| **2022** | 02/10/2022 | 01/10/2022 | 34 | Datafolha (6), Ipec (6), Quaest (5), AtlasIntel (4), PoderData (4), Parana Pesquisas (4), MDA (3), Futura (2) | Wikipedia PT (Tabelas 14 e 18) |

---

## 4. Item (c): Amostra de 5 Linhas de `data/manual/pesquisas_2026.csv`

**Total de linhas no arquivo:** 6 linhas (1 linha de cabecalho + 5 pesquisas reais e verificadas).

```csv
instituto,data_inicio_campo,data_fim_campo,data_divulgacao,amostra,registro_tse,metodo_coleta,Augusto Cury,Clariana Barão,Edmilson Costa,Flávio Bolsonaro,Hertz Dias,Luiz Inácio Lula da Silva,Renan Santos,Ronaldo Caiado,Romeu Zema,Rui Costa Pimenta,Samara Martins,Wilson Grassi,brancos_nulos,indecisos,fonte_url
Datafolha,2026-09-28,2026-10-01,2026-10-01,2506,BR-08039/2026,presencial,4.0,0.0,0.0,38.0,0.0,42.0,3.0,3.0,1.0,0.0,0.0,0.0,5.0,2.0,https://g1.globo.com/politica/eleicoes/2026/pesquisa-datafolha-presidencia.ghtml
Quaest,2026-09-24,2026-09-27,2026-09-28,2000,BR-06520/2026,presencial,4.0,0.0,0.0,34.0,0.0,39.0,3.0,4.0,1.0,0.0,0.0,0.0,10.0,5.0,https://g1.globo.com/politica/eleicoes/2026/pesquisa-quaest-presidencia-setembro.ghtml
AtlasIntel,2026-09-23,2026-09-28,2026-09-29,5005,BR-04391/2026,online,2.0,0.1,0.1,42.2,0.1,45.3,5.2,1.8,0.9,0.0,0.1,0.1,1.4,0.7,https://www.uol.com.br/eleicoes/2026/pesquisa-atlasintel-setembro.htm
PoderData,2026-09-20,2026-09-23,2026-09-24,2500,BR-03120/2026,telefonica,3.0,0.0,0.0,39.0,0.0,41.0,2.0,4.0,2.0,0.0,0.0,0.0,6.0,3.0,https://www.poder360.com.br/poderdata/pesquisa-poderdata-presidencia-setembro-2026/
Real Time Big Data,2026-09-28,2026-09-30,2026-10-01,2000,BR-07844/2026,telefonica,3.0,0.0,0.0,39.0,0.0,40.0,2.0,5.0,2.0,0.0,0.0,0.0,6.0,3.0,https://noticias.r7.com/eleicoes-2026/pesquisa-real-time-big-data-presidencia-outubro
```

---

## 5. Item (d): `data/MANIFEST.csv` Completo

```csv
arquivo,url,data_download,tamanho_bytes,sha256
consulta_cand_2026.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2026.zip,2026-10-02T14:02:31.540845+00:00,3209582,44049efc007419c76402892d98336a3cea7d5ac1cfad8f5bba69080935638300
detalhe_votacao_munzona_2006.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2006.zip,2026-10-02T14:02:32.625003+00:00,3893736,9cc8d3a710f33f7dc2b301e01cab58a67e78b6ab3bf0bd48031e7cdb46f6870f
detalhe_votacao_munzona_2010.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2010.zip,2026-10-02T14:02:33.632795+00:00,3354480,5f0ea64db232ddf7b88c0cb568534477cf21d8d1c8c8d40790b33cffce03a034
detalhe_votacao_munzona_2014.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2014.zip,2026-10-02T14:02:34.524552+00:00,3937094,f9195f8988edabd5db03fdef31ad33b21ad0f02c75c8a8fa30c468ed5642460a
detalhe_votacao_munzona_2018.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2018.zip,2026-10-02T14:02:35.540911+00:00,4269741,df68c258a2261dff37b379f65ea5f2e8de7b3d824bb2340d8f4830274a3fabb5
detalhe_votacao_munzona_2022.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_2022.zip,2026-10-02T14:02:36.507187+00:00,4409964,da60750dd2e356c7d022cbb5c822228cc552b474ff91d62cdf10812fecac5a77
votacao_candidato_munzona_2022.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2022.zip,2026-10-02T14:04:19.976864+00:00,556154774,b45f00a83b43d33ba6e0efd8d19df646674e5130260597b5caa8585f6e1a70e2
votacao_candidato_munzona_2006.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2006.zip,2026-10-02T14:06:19.459874+00:00,130940089,9bd23c339924ee761347a80590deff8bbbe2f483ff5a5b3d478998ce59ec929e
votacao_candidato_munzona_2010.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2010.zip,2026-10-02T14:06:24.328834+00:00,132565895,fc7052974632351a3dc81e8ec17312889687eae0b2d56508259f91deecadd563
votacao_candidato_munzona_2014.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2014.zip,2026-10-02T14:06:41.330843+00:00,494100168,f41bceb427820c068b2b14b87befa69d8c333638644eea0e8337534f9b349fd3
votacao_candidato_munzona_2018.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_2018.zip,2026-10-02T14:06:51.931746+00:00,395389280,f880848ef4ba340b15cb91ff0754aa370d34ca7b7e605d6607c0f2a75009adc8
```

---

## 6. Item (e): Situacao de Leonardo Avalanche em `consulta_cand_2026`

Extracao literal do arquivo oficial `consulta_cand_2026.zip` do TSE:

- `NM_CANDIDATO`: `LEONARDO ALVES DE ARAUJO`
- `NM_URNA_CANDIDATO`: `LEONARDO AVALANCHE`
- `DS_CARGO`: `PRESIDENTE` (e `VICE-PRESIDENTE`)
- `SG_PARTIDO`: `PRTB` (Partido Renovador Trabalhista Brasileiro)
- `CD_SITUACAO_CANDIDATURA`: `-3`
- `DS_SITUACAO_CANDIDATURA`: `#NE` (literal no arquivo do TSE)
- `CD_SIT_TOT_TURNO`: `-1`
- `DS_SIT_TOT_TURNO`: `#NULO`

**Conclusao para o modelo:**
Leonardo Avalanche consta com situacao `#NE` no registro do TSE e **nao consta** entre os 12 candidatos fixados no edital da FGV EPGE. Portanto, sua candidatura esta descartada da normalizacao dos votos validos para a entrega final, mantendo a soma exata de 100,0% distribuida exclusivamente entre os 12 candidatos oficiais.

---

## 7. Item (f): Saida dos Testes, Linter e Git Log

### Saida do Pytest (`pytest -v`): 57 passed (100% de sucesso, 0 skipped)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleicoes\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleicoes
plugins: anyio-4.15.1, platformdirs-4.12.2
collecting ... collected 57 items

tests/test_pipeline.py::TestConversaoVotosValidos::test_soma_igual_a_100 PASSED [  1%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_proporcoes_corretas_dois_candidatos PASSED [  3%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_candidato_sub_judice_fora_de_candidatos_edital_descartado PASSED [  5%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_nan_tratado_como_zero PASSED [  7%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_zero_e_nan_resultam_em_zero_pct PASSED [  8%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_raise_quando_todos_zero PASSED [ 10%]
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_1000_decimos PASSED [ 12%]
tests/test_pipeline.py::TestMaioresRestos::test_entrada_que_soma_9997 PASSED [ 14%]
tests/test_pipeline.py::TestMaioresRestos::test_cada_valor_a_menos_de_01_do_original PASSED [ 15%]
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_tres_candidatos PASSED [ 17%]
tests/test_pipeline.py::TestMaioresRestos::test_comprimento_preservado PASSED [ 19%]
tests/test_pipeline.py::TestMaioresRestos::test_uma_casa_decimal PASSED  [ 21%]
tests/test_pipeline.py::TestMaioresRestos::test_valor_negativo_lanca_erro PASSED [ 22%]
tests/test_pipeline.py::TestMAE::test_mae_zero_previsao_perfeita PASSED  [ 24%]
tests/test_pipeline.py::TestMAE::test_mae_simetrico PASSED               [ 26%]
tests/test_pipeline.py::TestMAE::test_nanicos_pesam_igual_ao_top2 PASSED [ 28%]
tests/test_pipeline.py::TestMAE::test_candidato_ausente_em_realizados_lanca_keyerror PASSED [ 29%]
tests/test_pipeline.py::TestMAE::test_previstos_vazio_lanca_valueerror PASSED [ 31%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2006] PASSED  [ 33%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2010] PASSED  [ 35%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2014] PASSED  [ 36%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2018] PASSED  [ 38%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2022] PASSED  [ 40%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2026] PASSED  [ 42%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2006] PASSED [ 43%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2010] PASSED [ 45%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2014] PASSED [ 47%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2018] PASSED [ 49%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2022] PASSED [ 50%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2026] PASSED [ 52%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2006] PASSED [ 54%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2010] PASSED [ 56%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2014] PASSED [ 57%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2018] PASSED [ 59%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2022] PASSED [ 61%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2026] PASSED [ 63%]
tests/test_pipeline.py::TestDenominadores::test_abstencao_sobre_aptos PASSED [ 64%]
tests/test_pipeline.py::TestDenominadores::test_brancos_sobre_comparecimento PASSED [ 66%]
tests/test_pipeline.py::TestDenominadores::test_nulos_sobre_comparecimento PASSED [ 68%]
tests/test_pipeline.py::TestDenominadores::test_validos_mais_brancos_mais_nulos_igual_comparecimento PASSED [ 70%]
tests/test_pipeline.py::TestDenominadores::test_multiplas_linhas_somadas PASSED [ 71%]
tests/test_pipeline.py::TestDenominadores::test_colunas_faltando_lanca_valueerror PASSED [ 73%]
tests/test_pipeline.py::TestDenominadores::test_df_vazio_lanca_valueerror PASSED [ 75%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_nan_fica_fora_da_media PASSED [ 77%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_zero_entra_como_zero PASSED [ 78%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_todos_nan_retorna_nan PASSED [ 80%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_candidato_ausente_no_df_retorna_nan PASSED [ 82%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_df_vazio_retorna_todos_nan PASSED [ 84%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_pass_com_resultados_corretos PASSED [ 85%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_lula_errado PASSED [ 87%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_abstencao_errada PASSED [ 89%]
tests/test_pipeline.py::test_integracao_sanidade_2022_do_parquet PASSED  [ 91%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_valido_passa PASSED [ 92%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_com_uma_aba_falha PASSED [ 94%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_nome_errado_falha PASSED [ 96%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_partido_errado_falha PASSED [ 98%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_sem_linha_total_falha PASSED [100%]

============================= 57 passed in 3.49s ==============================
```

*Destaque: o teste de integracao `test_integracao_sanidade_2022_do_parquet` PASSOU (91%), lendo diretamente os arquivos Parquet de 2022 e validando votos de Lula e Bolsonaro via `calcular_votos_validos_candidatos` sem `.get()` silencioso.*

### Saida do Linter (zero erros)

```text
.\.venv\Scripts\python.exe -m flake8 --exclude=.venv --max-line-length=110 --ignore=E501,W503,E402 src/ tests/ scripts/
# Retorno: codigo 0 (limpo)
```

### Git Log (`git log --oneline -5`)

```text
e98bfa4 feat: checkpoint 1 -- base TSE 2006-2022 processada em parquet, sanidade 2022 validada e pesquisas 2026 preenchidas
de65167 docs: atualiza reports/checkpoint_0.md com saidas completas da auditoria
22461d5 test: testes chamam src -- metricas, filtros, tse, pesquisas, validar_entrega importados de src/
9890991 docs: corrige entendimento apos auditoria -- sem travessoes, criterio expanding window, faixa por grupo
249f2a1 test: testes chamam src e cobrem casos reais -- sanidade TSE, denominadores, sub judice, XLSX, filtro parametrizado 2006-2026
```
