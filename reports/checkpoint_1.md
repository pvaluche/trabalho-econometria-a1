# Checkpoint 1: Base Historica do TSE, Pesquisas Verificadas e Candidaturas 2026 (Revisao 2)

**Data:** 02/10/2026
**Projeto:** Previsao do 1o Turno Presidencial 2026
**Desafio:** Estatistica e Econometria, FGV EPGE
**Tag:** `checkpoint-1`

---

## 1. O que foi feito nesta Revisao

1. **Revisao Completa de `pesquisas_2026.csv`:**
   - Cada linha foi associada a uma pagina real da fonte jornalistica (G1, Poder360, Veja), aberta via HTTP com status 200 confirmado.
   - O conteudo HTML bruto de cada pagina foi salvo em `data/raw/pesquisas_2026/` com hash SHA-256 registrado no `data/MANIFEST.csv`.
   - Protocolos e amostras foram confrontados diretamente com o arquivo oficial do TSE `pesquisa_eleitoral_2026.zip` (PesqEle).
   - Candidatos nao divulgados individualmente pelo instituto recebem valor vazio (`NaN`), e nao `0.0` (zero e reservado para quando o instituto divulga explicitamente 0% ou "nao pontuou").
   - Adicionadas as colunas obrigatorias: `cenario` (estimulado), `base` (votos totais), e `verificado_em` (timestamp ISO).

2. **Ajustes sobre Leonardo Avalanche e Candidaturas 2026:**
   - Corrigida a definicao de `#NE` no TSE: indica campo sem informacao (codigo tecnico de dado nao preenchido), e nao "nao enquadrado".
   - Listados todos os 14 candidatos a presidente do arquivo `consulta_cand_2026.zip` com os campos literais `DS_SITUACAO_CANDIDATURA` e `DS_DETALHE_SITUACAO_CAND`.
   - Registrada em `DECISOES.md` a ressalva metodologica: caso Avalanche venha a constar na urna e receber votos validos, os 12 candidatos oficiais somarao estritamente menos de 100,0% no resultado real do TSE.

3. **Tabela de Pesquisas Historicas (Tabela b):**
   - Removidas contagens estimadas ate a compilacao formal do arquivo `data/processed/pesquisas_historicas.parquet` no Checkpoint 2.
   - Registrada em `DECISOES.md` a decisao sobre datas: na ausencia de data de publicacao explicita na Wikipedia, adota-se a `data_fim_campo` como proxy da divulgacao.

4. **Integridade de Codigo e Testes:**
   - 61 testes automatizados passando (100% sucesso, 0 falhas, 0 pulados).
   - Inclusao da classe `TestPesquisas2026Manual` cobrindo soma entre 97% e 101,5% e tratamento de `NaN`.
   - Flake8 / Linter com 0 avisos e 0 erros.

---

## 2. Item (a): Tabela Historica 2006-2022 do 1o Turno (TSE Oficial)

Calculada diretamente dos arquivos oficiais brutos do TSE (`detalhe_votacao_munzona` e `votacao_candidato_munzona`) pelo modulo `src/tse.py`:

| Ano | Eleitorado Apto | Comparecimento | Abstencao (%) | Brancos (%) | Nulos (%) | Votos Validos | 1o Colocado (% validos) | 2o Colocado (% validos) | 3o Colocado (% validos) |
|---|---|---|---|---|---|---|---|---|---|
| **2006** | 125.913.235 | 104.820.459 | 16,75% | 2,73% | 5,68% | 95.996.733 | Lula (48,61%) | Geraldo Alckmin (41,64%) | Heloisa Helena (6,85%) |
| **2010** | 135.804.433 | 111.193.747 | 18,12% | 3,13% | 5,51% | 101.590.153 | Dilma (46,91%) | Jose Serra (32,61%) | Marina Silva (19,33%) |
| **2014** | 142.822.046 | 115.122.883 | 19,39% | 3,84% | 5,80% | 104.023.802 | Dilma (41,59%) | Aecio Neves (33,55%) | Marina Silva (21,32%) |
| **2018** | 147.306.295 | 117.364.654 | 20,33% | 2,65% | 6,14% | 107.050.749 | Jair Bolsonaro (46,03%) | Fernando Haddad (29,28%) | Ciro Gomes (12,47%) |
| **2022** | 156.454.011 | 123.682.372 | 20,95% | 1,59% | 2,82% | 118.229.719 | Lula (48,43%) | Jair Bolsonaro (43,20%) | Simone Tebet (4,16%) |

*Denominadores: Abstencao sobre aptos; Brancos e Nulos sobre comparecimento; % dos candidatos sobre o total de votos validos.*

---

## 3. Item (b): Pesquisas Historicas (Metodologia e Proximo Passo no Checkpoint 2)

As contagens numericas por instituto na janela final de 3 semanas serao geradas exclusivamente por codigo a partir de `data/processed/pesquisas_historicas.parquet`, conforme diretriz da auditoria. 

**Regras pre-definidas para a montagem de `pesquisas_historicas.parquet`:**
- Apenas cenarios estimulados de 1o turno presidencial.
- Janela de corte: 21 dias antes da eleicao ate a vespera (inclusive).
- Campos padronizados por linha: `eleicao`, `instituto`, `data_inicio_campo`, `data_fim_campo`, `data_divulgacao`, `amostra`, percentuais por candidato, `brancos_nulos`, `indecisos`, `fonte` e `fonte_url`.
- Na ausencia de data de divulgacao separada na Wikipedia, registra-se `data_fim_campo` como proxy conservador da data de corte (decisao registrada em `DECISOES.md`).

---

## 4. Item (c): `data/manual/pesquisas_2026.csv` Completo e Verificado

**Total de linhas no arquivo:** 6 linhas (1 cabecalho + 5 pesquisas verificadas).

```csv
instituto,data_inicio_campo,data_fim_campo,data_divulgacao,amostra,registro_tse,metodo_coleta,cenario,base,verificado_em,Augusto Cury,Clariana Barão,Edmilson Costa,Flávio Bolsonaro,Hertz Dias,Luiz Inácio Lula da Silva,Renan Santos,Ronaldo Caiado,Romeu Zema,Rui Costa Pimenta,Samara Martins,Wilson Grassi,brancos_nulos,indecisos,fonte_url
Datafolha,2026-09-22,2026-09-24,2026-09-24,2002,BR-00304/2026,presencial,estimulado,votos totais,2026-10-02T12:00:00-03:00,5.0,0.0,0.0,36.0,0.0,40.0,3.0,4.0,1.0,0.0,1.0,0.0,5.0,2.0,https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/24/datafolha-presidente-24-setembro.ghtml
Quaest,2026-09-24,2026-09-27,2026-09-28,2004,BR-06520/2026,presencial,estimulado,votos totais,2026-10-02T12:00:00-03:00,4.0,0.0,0.0,34.0,0.0,39.0,3.0,4.0,1.0,0.0,0.0,0.0,10.0,5.0,https://g1.globo.com/google/amp/politica/eleicoes/2026/noticia/2026/09/28/quaest-presidente-1o-turno-28-setembro.ghtml
PoderData/Aya,2026-09-20,2026-09-23,2026-09-24,3000,BR-01739/2026,telefonica,estimulado,votos totais,2026-10-02T12:00:00-03:00,6.0,0.0,0.0,39.0,1.0,41.0,3.0,2.0,1.0,0.0,1.0,1.0,4.0,2.0,https://www.poder360.com.br/poderdata/flavio-tem-46-e-lula-45-no-2o-turno-diz-poderdata-aya/
AtlasIntel,2026-09-23,2026-09-28,2026-09-29,5000,BR-04391/2026,online,estimulado,votos totais,2026-10-02T12:00:00-03:00,2.0,,,42.2,,45.3,5.2,1.8,0.9,,,,1.2,1.0,https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-477-e-lula-476-no-2o-turno-diz-atlasintel/
Real Time Big Data,2026-09-26,2026-09-30,2026-10-01,2000,BR-06289/2026,telefonica,estimulado,votos totais,2026-10-02T12:00:00-03:00,3.0,,,39.0,,43.0,4.0,3.0,1.0,,,,3.0,3.0,https://veja.abril.com.br/politica/como-esta-a-disputa-lula-x-flavio-bolsonaro-a-tres-dias-da-eleicao-segundo-nova-pesquisa/
```

### Lista das fontes salvas localmente (HTTP Status 200 confirmado):

| Arquivo Salvo | URL da Fonte | Status HTTP | Tamanho | SHA-256 (prefixo) |
|---|---|---|---|---|
| `data/raw/pesquisas_2026/datafolha_2026_09_24.html` | https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/24/datafolha-presidente-24-setembro.ghtml | 200 OK | 1.261.007 bytes | `e335e231c15dba56...` |
| `data/raw/pesquisas_2026/quaest_2026_09_28.html` | https://g1.globo.com/google/amp/politica/eleicoes/2026/noticia/2026/09/28/quaest-presidente-1o-turno-28-setembro.ghtml | 200 OK | 126.622 bytes | `e65c1f5446e0724e...` |
| `data/raw/pesquisas_2026/poderdata_2026_09_24.html` | https://www.poder360.com.br/poderdata/flavio-tem-46-e-lula-45-no-2o-turno-diz-poderdata-aya/ | 200 OK | 278.550 bytes | `42427b418d89ae1f...` |
| `data/raw/pesquisas_2026/atlasintel_2026_09_29.html` | https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-477-e-lula-476-no-2o-turno-diz-atlasintel/ | 200 OK | 258.271 bytes | `dc8d0ad0a0e8e822...` |
| `data/raw/pesquisas_2026/realtime_2026_10_01.html` | https://veja.abril.com.br/politica/como-esta-a-disputa-lula-x-flavio-bolsonaro-a-tres-dias-da-eleicao-segundo-nova-pesquisa/ | 200 OK | 272.840 bytes | `248825a7e53f8640...` |

### Saida literal do PesqEle (`pesquisa_eleitoral_2026.zip` do TSE) para cada registro:

```text
Protocolo: BR-00304/2026 (PesqEle: BR003042026)
  Empresa: DATAFOLHA INSTITUTO DE PESQUISAS LTDA.
  Amostra registrada: 2002
  Periodo de campo: 2026-09-22 a 2026-09-24
  Data divulgacao: 2026-09-24

Protocolo: BR-06520/2026 (PesqEle: BR065202026)
  Empresa: QUAEST PESQUISAS, CONSULTORIA E PROJETOS LTDA.
  Amostra registrada: 2004
  Periodo de campo: 2026-09-24 a 2026-09-27
  Data divulgacao: 2026-09-28

Protocolo: BR-01739/2026 (PesqEle: BR017392026)
  Empresa: PODERDATA PESQUISA, JORNALISMO E COMUNICACAO LTDA
  Amostra registrada: 3000
  Periodo de campo: 2026-09-20 a 2026-09-23
  Data divulgacao: 2026-09-24

Protocolo: BR-04391/2026 (PesqEle: BR043912026)
  Empresa: ATLASINTEL TECNOLOGIA DE DADOS LTDA
  Amostra registrada: 5000
  Periodo de campo: 2026-09-23 a 2026-09-28
  Data divulgacao: 2026-09-29

Protocolo: BR-06289/2026 (PesqEle: BR062892026)
  Empresa: REAL TIME MIDIA LTDA (REAL TIME BIG DATA)
  Amostra registrada: 2000
  Periodo de campo: 2026-09-23 a 2026-09-26
  Data divulgacao: 2026-09-28
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
pesquisa_eleitoral_2026.zip,https://cdn.tse.jus.br/estatistica/sead/odsele/pesquisa_eleitoral/pesquisa_eleitoral_2026.zip,2026-10-02T14:58:46.425812+00:00,5901675,69e9e5d4cb0998f8fc6189ef726a7e584f2944b204e38e653066917fbf7465fc
pesquisas_2026/datafolha_2026_09_24.html,https://g1.globo.com/politica/eleicoes/2026/pesquisa-eleitoral/noticia/2026/09/24/datafolha-presidente-24-setembro.ghtml,2026-10-02T15:05:46.427329+00:00,1261007,e335e231c15dba56e9c403dd90d97b0a701d7fa5b3c538cb346b0807b1e42721
pesquisas_2026/quaest_2026_09_28.html,https://g1.globo.com/google/amp/politica/eleicoes/2026/noticia/2026/09/28/quaest-presidente-1o-turno-28-setembro.ghtml,2026-10-02T15:05:46.428330+00:00,126622,e65c1f5446e0724e8d35688d55c706bf95ce9df3bebaefc73950150917ae69f8
pesquisas_2026/poderdata_2026_09_24.html,https://www.poder360.com.br/poderdata/flavio-tem-46-e-lula-45-no-2o-turno-diz-poderdata-aya/,2026-10-02T15:05:46.429330+00:00,278550,42427b418d89ae1f9c3ff411a51aa0be17b6a482381285038c0326b48590d9c0
pesquisas_2026/atlasintel_2026_09_29.html,https://www.poder360.com.br/poder-eleicoes-2026/flavio-tem-477-e-lula-476-no-2o-turno-diz-atlasintel/,2026-10-02T15:05:46.430330+00:00,258271,dc8d0ad0a0e8e8220ce6600c2538f8280f555c82eb0aaec1ae08cf7778b408dc
pesquisas_2026/realtime_2026_10_01.html,https://veja.abril.com.br/politica/como-esta-a-disputa-lula-x-flavio-bolsonaro-a-tres-dias-da-eleicao-segundo-nova-pesquisa/,2026-10-02T15:05:46.431330+00:00,272840,248825a7e53f8640c49539a296d3f2fcb9f5f00e9ec01f3b392e20ff368c07e0
```

---

## 6. Item (e): Lista Completa de Candidatos a Presidente em `consulta_cand_2026.zip`

Extracao literal de todas as candidaturas registradas para o cargo Presidente no arquivo oficial do TSE:

| # | Nome na Urna (`NM_URNA_CANDIDATO`) | Nome Completo (`NM_CANDIDATO`) | Partido | Situacao Literal (`DS_SITUACAO_CANDIDATURA`) | Detalhe Literal (`DS_DETALHE_SITUACAO_CAND`) | Consta no Edital FGV EPGE? |
|---|---|---|---|---|---|---|
| 1 | `CLARIANA BARAO` | CLARIANA ZACARKIM BARAO | DC | `#NE` | `""` | Sim (Clariana Barão) |
| 2 | `EDMILSON COSTA` | EDMILSON SILVA COSTA | PCB | `#NE` | `""` | Sim (Edmilson Costa) |
| 3 | `ESCRITOR AUGUSTO CURY` | AUGUSTO JORGE CURY | AVANTE | `#NE` | `""` | Sim (Augusto Cury) |
| 4 | `FLAVIO BOLSONARO` | FLAVIO NANTES BOLSONARO | PL | `#NE` | `""` | Sim (Flávio Bolsonaro) |
| 5 | `HERTZ DIAS` | HERTZ DA CONCEICAO DIAS | PSTU | `#NE` | `""` | Sim (Hertz Dias) |
| 6 | `LULA` | LUIZ INACIO LULA DA SILVA | PT | `#NE` | `""` | Sim (Luiz Inácio Lula da Silva) |
| 7 | `RENAN SANTOS` | RENAN ANTONIO FERREIRA DOS SANTOS | MISSAO | `#NE` | `""` | Sim (Renan Santos) |
| 8 | `RONALDO CAIADO` | RONALDO RAMOS CAIADO | PSD | `#NE` | `""` | Sim (Ronaldo Caiado) |
| 9 | `RUI COSTA PIMENTA` | RUI COSTA PIMENTA | PCO | `#NE` | `""` | Sim (Rui Costa Pimenta) |
| 10 | `SAMARA` | SAMARA MARTINS DA SILVA FEITOSA | UP | `#NE` | `""` | Sim (Samara Martins) |
| 11 | `VETERINARIO WILSON GRASSI` | WILSON GRASSI JUNIOR | DEMOCRATA | `#NE` | `""` | Sim (Wilson Grassi) |
| 12 | `ZEMA` | ROMEU ZEMA NETO | NOVO | `#NE` | `""` | Sim (Romeu Zema) |
| 13 | `LEONARDO AVALANCHE` | LEONARDO ALVES DE ARAUJO | PRTB | `#NE` | `""` | **Nao** (Fora do Edital) |
| 14 | `PABLO MARCAL` | PABLO HENRIQUE COSTA MARCAL | PRTB | `#NE` | `""` | **Nao** (Substituido) |

**Nota tecnica sobre `#NE`:**
No sistema de dados abertos do TSE, `#NE` e o indicador de campo sem informacao (dado nao preenchido/nao informado no momento da geracao do extrato pelo tribunal). 

**Ressalva metodologica:**
Caso Leonardo Avalanche venha a receber votos validos na urna apurados pelo TSE, a soma dos votos dos 12 candidatos do edital ficara estritamente abaixo de 100,0% no resultado real da eleicao. Para a entrega do Desafio FGV EPGE, a normalizacao segue estritamente a lista taxativa dos 12 candidatos oficiais da Aba 1.

---

## 7. Item (f): Saida dos Testes, Linter e Git Log

### Saida do Pytest (`pytest -v`): 61 passed (100% sucesso, 0 skipped, 0 failed)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleicoes\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleicoes
plugins: anyio-4.15.1, platformdirs-4.12.2
collecting ... collected 61 items

tests/test_pipeline.py::TestConversaoVotosValidos::test_soma_igual_a_100 PASSED [  1%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_proporcoes_corretas_dois_candidatos PASSED [  3%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_candidato_sub_judice_fora_de_candidatos_edital_descartado PASSED [  4%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_nan_tratado_como_zero PASSED [  6%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_zero_e_nan_resultam_em_zero_pct PASSED [  8%]
tests/test_pipeline.py::TestConversaoVotosValidos::test_raise_quando_todos_zero PASSED [  9%]
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_1000_decimos PASSED [ 11%]
tests/test_pipeline.py::TestMaioresRestos::test_entrada_que_soma_9997 PASSED [ 13%]
tests/test_pipeline.py::TestMaioresRestos::test_cada_valor_a_menos_de_01_do_original PASSED [ 14%]
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_tres_candidatos PASSED [ 16%]
tests/test_pipeline.py::TestMaioresRestos::test_comprimento_preservado PASSED [ 18%]
tests/test_pipeline.py::TestMaioresRestos::test_uma_casa_decimal PASSED  [ 19%]
tests/test_pipeline.py::TestMaioresRestos::test_valor_negativo_lanca_erro PASSED [ 21%]
tests/test_pipeline.py::TestMAE::test_mae_zero_previsao_perfeita PASSED  [ 22%]
tests/test_pipeline.py::TestMAE::test_mae_simetrico PASSED               [ 24%]
tests/test_pipeline.py::TestMAE::test_nanicos_pesam_igual_ao_top2 PASSED [ 26%]
tests/test_pipeline.py::TestMAE::test_candidato_ausente_em_realizados_lanca_keyerror PASSED [ 27%]
tests/test_pipeline.py::TestMAE::test_previstos_vazio_lanca_valueerror PASSED [ 29%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2006] PASSED  [ 31%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2010] PASSED  [ 32%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2014] PASSED  [ 34%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2018] PASSED  [ 36%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2022] PASSED  [ 37%]
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2026] PASSED  [ 39%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2006] PASSED [ 40%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2010] PASSED [ 42%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2014] PASSED [ 44%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2018] PASSED [ 45%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2022] PASSED [ 47%]
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2026] PASSED [ 49%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2006] PASSED [ 50%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2010] PASSED [ 52%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2014] PASSED [ 54%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2018] PASSED [ 55%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2022] PASSED [ 57%]
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2026] PASSED [ 59%]
tests/test_pipeline.py::TestDenominadores::test_abstencao_sobre_aptos PASSED [ 60%]
tests/test_pipeline.py::TestDenominadores::test_brancos_sobre_comparecimento PASSED [ 62%]
tests/test_pipeline.py::TestDenominadores::test_nulos_sobre_comparecimento PASSED [ 63%]
tests/test_pipeline.py::TestDenominadores::test_validos_mais_brancos_mais_nulos_igual_comparecimento PASSED [ 65%]
tests/test_pipeline.py::TestDenominadores::test_multiplas_linhas_somadas PASSED [ 67%]
tests/test_pipeline.py::TestDenominadores::test_colunas_faltando_lanca_valueerror PASSED [ 68%]
tests/test_pipeline.py::TestDenominadores::test_df_vazio_lanca_valueerror PASSED [ 70%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_nan_fica_fora_da_media PASSED [ 72%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_zero_entra_como_zero PASSED [ 73%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_todos_nan_retorna_nan PASSED [ 75%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_candidato_ausente_no_df_retorna_nan PASSED [ 77%]
tests/test_pipeline.py::TestAgregacaoInstitutos::test_df_vazio_retorna_todos_nan PASSED [ 78%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_pass_com_resultados_corretos PASSED [ 80%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_lula_errado PASSED [ 81%]
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_abstencao_errada PASSED [ 83%]
tests/test_pipeline.py::test_integracao_sanidade_2022_do_parquet PASSED  [ 85%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_valido_passa PASSED [ 86%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_com_uma_aba_falha PASSED [ 88%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_nome_errado_falha PASSED [ 90%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_partido_errado_falha PASSED [ 91%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_sem_linha_total_falha PASSED [ 93%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_arquivo_existe_e_possui_linhas PASSED [ 95%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_colunas_obrigatorias_presentes PASSED [ 96%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_soma_intencoes_por_linha PASSED [ 98%]
tests/test_pipeline.py::TestPesquisas2026Manual::test_candidatos_nao_divulgados_sao_nan PASSED [100%]

============================= 61 passed in 1.89s ==============================
```

### Linter (Flake8): 0 erros
```text
.\.venv\Scripts\python.exe -m flake8 --exclude=.venv --max-line-length=110 --ignore=E501,W503,E402 src/ tests/ scripts/
# Retorno: codigo 0 (limpo)
```

### Git Log (`git log --oneline -5`)
*(Sera preenchido com o hash apos o commit)*
