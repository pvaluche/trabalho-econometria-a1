# Checkpoint 0: Entendimento e Estrutura do Repositorio (Revisao 2)

**Data:** 02/10/2026
**Projeto:** Previsao do 1o Turno Presidencial 2026
**Desafio:** Estatistica e Econometria, FGV EPGE [confirmar professor]
**Commit:** 22461d5
**Tag:** checkpoint-0

---

## O que foi feito

### 1. Ambiente e estrutura do repositorio

- Git (MinGit 2.56.0) instalado via winget; ambiente virtual com `uv 0.12.22` e Python 3.12.10.
- 147 pacotes instalados (pandas, polars, scikit-learn, matplotlib, pytest, etc.).
- Estrutura completa de diretorios criada: `data/`, `src/`, `notebooks/`, `tests/`, `interface/`, `reports/`, `docs/`, `outputs/`, `scripts/`, `.github/workflows/`.
- Repositorio conectado e sincronizado no GitHub: `https://github.com/pvaluche/trabalho-econometria-a1`.

### 2. Fundamentacao teorica: `docs/ENTENDIMENTO.md`

- Todos os travessoes removidos.
- Referencias conferidas com DOI (Jackman 2005, Linzer 2013, Shirani-Mehr et al. 2018, Vehtari et al. 2017).
- Vies comum da eleicao explicitamente separado do house effect relativo de cada instituto.
- LOEO vs. Expanding Window documentados com regra de fallback numerica no pre-registro.
- Faixas de incerteza por grupo (top-2, 3o-4o, nanicos).
- Estimativa do efeito de voto util em 2022 (~5,6 p.p. somados) registrada como hipotese a testar.

### 3. Modulos em `src/` e `scripts/` (arquitetura sem duplicacao)

- `src/config.py`: CANDIDATOS_EDITAL como fonte unica com acentos exatos do edital; PARTIDOS_EDITAL.
- `src/metricas.py`: `calcular_mae` e `calcular_mae_por_candidato`.
- `src/filtros.py`: `filtrar_por_vespera` e dicionarios `VESPERAS` e `DIAS_ELEICAO` (2006-2026).
- `src/tse.py`: `calcular_denominadores` lendo DataFrame no formato do TSE.
- `src/pesquisas.py`: `agregar_institutos` (NaN fora da media, 0 dentro).
- `src/conversao.py`: conversao para votos validos com descarte de sub judice nao listado.
- `src/arredondamento.py`: maiores restos com normalizacao previa (sem bug de ponto flutuante).
- `scripts/validar_entrega.py`: funcao importavel `validar_xlsx` com todas as checagens do edital.

---

## Saida do Git Log (`git log --oneline -5`)

```text
22461d5 test: testes chamam src -- metricas, filtros, tse, pesquisas, validar_entrega importados de src/
9890991 docs: corrige entendimento apos auditoria -- sem travessoes, criterio expanding window, faixa por grupo
249f2a1 test: testes chamam src e cobrem casos reais -- sanidade TSE, denominadores, sub judice, XLSX, filtro parametrizado 2006-2026
c92b477 docs: corrige entendimento apos auditoria -- tabela 2022, LOEO vs expanding window, vies comum vs house effect
e975098 feat: checkpoint 0 -- entendimento, modulos base e testes unitarios
```

---

## Saida do Linter (zero erros)

```text
.\.venv\Scripts\python.exe -m flake8 --exclude=.venv --max-line-length=110 --ignore=E501,W503,E402 src/ tests/ scripts/
# Retorno: codigo de saida 0 (nenhum aviso ou erro)
```

---

## Saida do Pytest (`pytest -v`)

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
tests/test_pipeline.py::test_integracao_sanidade_2022_do_parquet SKIPPED [ 91%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_valido_passa PASSED [ 92%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_com_uma_aba_falha PASSED [ 94%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_nome_errado_falha PASSED [ 96%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_partido_errado_falha PASSED [ 98%]
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_sem_linha_total_falha PASSED [100%]

======================== 56 passed, 1 skipped in 2.50s ========================
```
