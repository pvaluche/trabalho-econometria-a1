# Checkpoint 0 — Entendimento e Estrutura do Repositório (pós-auditoria)

**Data:** 02/10/2026
**Projeto:** Previsão do 1º Turno Presidencial 2026
**Desafio:** Estatística e Econometria — Prof. Valdemar Pinho, FGV EPGE
**Commit:** _a preencher após push_
**Tag:** `checkpoint-0`

---

## O que foi feito

### 1. Ambiente e estrutura do repositório

- Git (MinGit 2.56.0) instalado via winget; ambiente virtual com `uv 0.12.22` e Python 3.12.10.
- 147 pacotes instalados (pandas, polars, scikit-learn, matplotlib, pytest, etc.).
- Estrutura completa de diretórios criada: `data/`, `src/`, `notebooks/`, `tests/`, `interface/`, `reports/`, `docs/`, `outputs/`, `scripts/`, `.github/workflows/`.
- `.gitignore`, `.gitattributes`, `requirements.txt`, `.pre-commit-config.yaml`, `ci.yml`, `README.md`, `DECISOES.md`.
- Repositório conectado ao GitHub (`https://github.com/pvaluche/trabalho-econometria-a1`).

### 2. Fundamentação teórica — `docs/ENTENDIMENTO.md`

Cobre os cinco tópicos exigidos no prompt:

1. **Agregação de pesquisas:** Jackman (2005) — modelo de espaço de estados com house effect e passeio aleatório; Linzer (2013) — prior de fundamentals + rastreamento de pesquisas; metodologias públicas FiveThirtyEight e The Economist.
2. **Erro total de pesquisa:** Shirani-Mehr et al. (2018) — RMSE empírico ~3,5 p.p. (dobro da margem declarada); distinção entre **viés comum da eleição** (todos os institutos erram na mesma direção) e **house effect relativo** (viés sistemático do instituto específico).
3. **Caso brasileiro:** tabela corrigida com dados de votos válidos. Datafolha véspera 2022: Lula **50%** (erro +1,6 p.p.), Bolsonaro **36%** (erro -7,2 p.p.). Padrão de subestimação bolsonarista documentado em 2018 e 2022.
4. **Validação com poucas observações:** LOEO (usa todas as eleições, não preserva ordem temporal) + expanding window em paralelo (mais conservadora). Divergências serão reportadas no Checkpoint 3.
5. **Conclusão aplicada:** tabela relacionando cada fundamento teórico a uma decisão de implementação.

### 3. Módulos `src/` implementados

| Arquivo | Conteúdo principal |
|---|---|
| `src/config.py` | Raiz, candidatos, horário de corte, URLs TSE, grades de hiperparâmetros, sanidade 2022 |
| `src/download.py` | Download com hash SHA-256 e registro automático no MANIFEST.csv |
| `src/conversao.py` | Conversão para votos válidos (critério TSE), tratamento de NaN e sub judice |
| `src/arredondamento.py` | Método dos maiores restos — bug de ponto flutuante corrigido (normalização prévia) |

### 4. Testes unitários — `tests/test_pipeline.py`

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.6.0
collected 45 items

tests/test_pipeline.py::TestConversaoVotosValidos::test_soma_igual_a_100 PASSED
tests/test_pipeline.py::TestConversaoVotosValidos::test_proporcoes_corretas_dois_candidatos PASSED
tests/test_pipeline.py::TestConversaoVotosValidos::test_candidato_sub_judice_fora_da_lista_e_descartado PASSED
tests/test_pipeline.py::TestConversaoVotosValidos::test_nan_tratado_como_zero PASSED
tests/test_pipeline.py::TestConversaoVotosValidos::test_zero_e_nan_sao_distintos_mas_ambos_validos PASSED
tests/test_pipeline.py::TestConversaoVotosValidos::test_raise_quando_todos_zero PASSED
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_1000_decimos PASSED
tests/test_pipeline.py::TestMaioresRestos::test_entrada_que_soma_9997 PASSED
tests/test_pipeline.py::TestMaioresRestos::test_cada_valor_a_menos_de_01_do_original PASSED
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_tres_candidatos PASSED
tests/test_pipeline.py::TestMaioresRestos::test_comprimento_preservado PASSED
tests/test_pipeline.py::TestMaioresRestos::test_uma_casa_decimal PASSED
tests/test_pipeline.py::TestMaioresRestos::test_valor_negativo_lanca_erro PASSED
tests/test_pipeline.py::TestMAE::test_mae_zero_previsao_perfeita PASSED
tests/test_pipeline.py::TestMAE::test_mae_simetrico PASSED
tests/test_pipeline.py::TestMAE::test_nanicos_pesam_igual_ao_top2 PASSED
tests/test_pipeline.py::TestMAE::test_candidato_ausente_lanca_keyerror PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2006] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2010] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2014] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2018] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2022] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_vespera[2026] PASSED
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2006] PASSED
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2010] PASSED
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2014] PASSED
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2018] PASSED
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2022] PASSED
tests/test_pipeline.py::test_filtro_vespera_exclui_dia_da_eleicao[2026] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2006] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2010] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2014] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2018] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2022] PASSED
tests/test_pipeline.py::test_filtro_vespera_inclui_pesquisa_anterior[2026] PASSED
tests/test_pipeline.py::TestSanidade2022::test_sanidade_pass_com_resultados_corretos PASSED
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_lula_errado PASSED
tests/test_pipeline.py::TestSanidade2022::test_sanidade_fail_com_abstencao_errada PASSED
tests/test_pipeline.py::TestDenominadores::test_abstencao_calculada_sobre_aptos PASSED
tests/test_pipeline.py::TestDenominadores::test_brancos_calculados_sobre_comparecimento PASSED
tests/test_pipeline.py::TestDenominadores::test_nulos_calculados_sobre_comparecimento PASSED
tests/test_pipeline.py::TestDenominadores::test_validos_mais_brancos_mais_nulos_igual_comparecimento PASSED
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_valido_passa PASSED
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_com_uma_aba_falha PASSED
tests/test_pipeline.py::TestValidacaoXLSX::test_xlsx_sem_candidato_do_edital_falha PASSED

============================= 45 passed in 8.13s ==============================
```

---

## Decisões e Motivos

Todas registradas em `DECISOES.md`. Principais:

| Decisão | Alternativas | Motivo |
|---|---|---|
| Expanding window em paralelo ao LOEO | Só LOEO | LOEO não preserva ordem temporal; expanding window é mais conservadora e detecta overfitting ao futuro |
| Viés comum da eleição separado do house effect | Corrigir juntos | M2 corrige apenas house effect relativo; correção do viés comum exige preditor validável no backtest |
| Tabela de erros 2022 em votos válidos (Lula 50%, erro +1,6 p.p.) | Intenção de voto bruta | Critério do edital e do TSE é votos válidos; fonte verificada (Datafolha 01/10/2022) |
| Arredondamento com normalização prévia | Floor direto | Bug de ponto flutuante: 0.3*10=2.999... fazia sum=100.3; normalização prévia elimina o problema |
| Ibope e Ipec como séries separadas | Unificar | Conservador; menor risco de introduzir erro de atribuição de house effect entre institutos com metodologias distintas |

---

## Bug Corrigido

**`src/arredondamento.py`:** `math.floor(0.3 * 10) = 2` em vez de 3 (ponto flutuante). Correção: normalização dos valores de entrada para somarem exatamente 100 antes do floor, e `round(..., 10)` para remover ruído residual. Teste `test_soma_exata_1000_decimos` cobre o caso.

---

## Resultado da Auditoria (Checkpoint 0)

**Primeira submissão:** NÃO aprovado pelo Claude (6 correções no ENTENDIMENTO.md, 5 no test_pipeline.py).

**Correções aplicadas:**

| Item | Problema | Ação |
|---|---|---|
| Tabela 2022 | Lula previsto como ~0 p.p. de erro (errado) | Corrigido: Lula 50% Datafolha, erro +1,6 p.p. |
| LOEO preserva ordem temporal | Afirmação falsa | Removida; expanding window adicionada como validação paralela |
| Viés comum vs. house effect | Misturados no texto | Separados: M2 corrige house effect relativo; viés comum só entra se vencer no backtest |
| Travessões (6) | Proibidos pelo prompt | Removidos todos |
| Nota "não verificado" | Referências verificadas não estavam marcadas | Nota final ajustada |
| Faixa de incerteza, abstenção/brancos/nulos, Ibope/Ipec, "M4.4" | Ausentes | Adicionados na seção 5 (Conclusão Aplicada) e no corpo do texto |
| MAE definido no teste em vez de importado | Violava o princípio de testar o código real | MAE importado de `src/`; lança KeyError se candidato ausente |
| Filtro de data não parametrizado | Apenas 2022 testado | Parametrizado: 2006, 2010, 2014, 2018, 2022, 2026 |
| Dia da eleição 2022 errado (2022-10-03) | Data incorreta | Corrigido para 2022-10-02 |
| Sub judice | Teste incompleto | Testa que coluna extra é descartada e os 12 somam 100% |
| Maiores restos | Exigência round*10==1000 ausente | Adicionados 3 novos testes (1000 décimos, entrada somando 99.97, desvio < 0.1) |
| Sanidade 2022, denominadores, 0 vs NaN, validador XLSX | Ausentes | Todos adicionados |

---

## Dúvidas em Aberto

1. **Horário de corte:** ainda a definir pelo usuário. Candidatos a: 20h, 22h ou "antes da divulgação dos últimos Datafolha/Quaest do sábado". Registrar em `config.py` e `PRE_REGISTRO.md`.
2. **Leonardo Avalanche (PRTB):** necessário verificar se está na urna como sub judice antes de definir a normalização dos votos válidos (conforme seção 3.2 do prompt).
3. **Autenticação Base dos Dados:** se travar, usar Wikipedia PT/EN via `pandas.read_html` para pesquisas históricas.

---

## Arquivos para envio ao auditor

- `docs/ENTENDIMENTO.md`
- `tests/test_pipeline.py`
- Este arquivo (`reports/checkpoint_0.md`)
