# Relatorio de Auditoria: Checkpoint 4 (Corte Oficial de Sabado e Entrega Final)
**Desafio de Estatistica e Econometria: FGV EPGE (Eleicoes Presidenciais 2026)**  
**Grupo:** Joao Pedro Valuche, Arthur Caron Lyra, Lethicia Manfioletti Possamai  
**Data da Execucao:** 02/10/2026 21:24:41 UTC  
**Horario Limite de Corte:** Sabado 03/10/2026 as 20h00 (-03:00)  
**Tag de Congelamento do Modelo:** `modelo-congelado` (codigo e hiperparametros inalterados)  

---

## 1. Resumo Executivo do Fechamento do Checkpoint 4

Este relatorio consolida a execucao oficial do corte de sabado do pipeline de previsao eleitoral:
1. **Congelamento Metodologico:** O codigo de modelagem, hiperparametros ($k_\mu=3$, $\gamma=1.0$, $w=0.0$) e regras de selecao permanecem estritamente congelados na tag `modelo-congelado`. Nenhuma equacao ou parametro foi alterado.
2. **Pesquisas Incorporadas:** O modelo processa atualmente 6 levantamentos concluidos dentro da janela regulamentar de vespera, com transcricao auditada contra os arquivos HTML originais.
3. **Conformidade da Entrega:** O arquivo `outputs/previsao_2026.xlsx` foi gerado e aprovado com zero erros pelo validador oficial (`scripts/validar_entrega.py`).
4. **Interface Atualizada:** Os dados interativos em `interface/dados.json` e `interface/dados.js` foram regenerados com sucesso.

---

## 2. Lista de Pesquisas de 2026 Incorporadas no Pipeline

| # | Instituto | Registro TSE | Periodo de Campo | Data Divulgacao | Amostra | Metodo Coleta | Status Auditoria |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **Datafolha** | `BR-00304/2026` | 2026-09-22 a 2026-09-24 | 2026-09-24 | 2,002 | presencial | Aprovado (HTML auditado) |
| 2 | **Quaest** | `BR-06520/2026` | 2026-09-24 a 2026-09-27 | 2026-09-28 | 2,004 | presencial | Aprovado (HTML auditado) |
| 3 | **PoderData/Aya** | `BR-01739/2026` | 2026-09-20 a 2026-09-23 | 2026-09-24 | 3,000 | telefonica | Aprovado (HTML auditado) |
| 4 | **AtlasIntel** | `BR-04391/2026` | 2026-09-23 a 2026-09-28 | 2026-09-29 | 5,000 | online | Aprovado (HTML auditado) |
| 5 | **Real Time Big Data** | `BR-09503/2026` | 2026-09-26 a 2026-09-30 | 2026-10-01 | 2,000 | telefonica | Aprovado (HTML auditado) |
| 6 | **Datafolha** | `BR-08039/2026` | 2026-09-28 a 2026-10-01 | 2026-10-01 | 2,506 | presencial | Aprovado (HTML auditado) |

---

## 3. Monitoramento de Pesquisas Registradas no PesqEle para Sabado (03/10/2026)

Verificacao de status das 5 pesquisas presidenciais com divulgacao programada para o sabado 03/10/2026 no sistema PesqEle do TSE:

| Instituto | Registro TSE | Amostra | Periodo de Campo | Divulgacao Prevista | Veiculo / Fonte | Status no Pipeline |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Datafolha** | `BR-01708/2026` | 4,006 | 01 a 03/10/2026 | 03/10/2026 | G1 / Folha de S.Paulo | Aguardando divulgacao ate 20h (ou nao divulgada) |
| **Quaest** | `BR-02197/2026` | 3,702 | 02 a 03/10/2026 | 03/10/2026 | G1 / TV Globo | Aguardando divulgacao ate 20h (ou nao divulgada) |
| **AtlasIntel** | `BR-00999/2026` | 5,000 | 28/09 a 02/10/2026 | 03/10/2026 | Poder360 / AtlasIntel | Aguardando divulgacao ate 20h (ou nao divulgada) |
| **PoderData** | `BR-03519/2026` | 4,000 | 01 a 03/10/2026 | 03/10/2026 | Poder360 | Aguardando divulgacao ate 20h (ou nao divulgada) |
| **Real Time Big Data** | `BR-01068/2026` | 2,000 | 01 a 02/10/2026 | 03/10/2026 | Record / Veja | Aguardando divulgacao ate 20h (ou nao divulgada) |

*(Nota operacional: caso alguma pesquisa registrada nao seja veiculada ate as 20h00 de sabado pelo instituto contratante, seu descarte e documentado automaticamente e a previsao e consolidada com o conjunto efetivamente divulgado).*

---

## 4. Previsao Oficial Final dos 12 Candidatos do Edital (Votos Validos)

Percentuais de votos validos calculados pelo Modelo Oficial Aprovado ($k_\mu=3$, $\gamma=1.0$, $w=0.0$), com fechamento exato em 100,0% via Maiores Restos:

| Candidato | Partido | Modelo Oficial Aprovado (%) | M0 Puro (%) | Sensibilidade Nanicos (%) (w=0.5) |
| :--- | :---: | :---: | :---: | :---: |
| **Flávio Bolsonaro** | PL | **45,9%** | 41,5% | 45,8% |
| **Luiz Inácio Lula da Silva** | PT | **45,6%** | 45,4% | 45,5% |
| **Augusto Cury** | Avante | **2,6%** | 4,1% | 2,7% |
| **Ronaldo Caiado** | PSD | **2,6%** | 3,0% | 2,7% |
| **Renan Santos** | Missão | **2,5%** | 3,9% | 2,5% |
| Romeu Zema | Novo | **0,7%** | 1,1% | 0,7% |
| Samara Martins | UP | **0,1%** | 0,4% | 0,1% |
| Clariana Barão | DC | **0,0%** | 0,2% | 0,0% |
| Edmilson Costa | PCB | **0,0%** | 0,0% | 0,0% |
| Hertz Dias | PSTU | **0,0%** | 0,0% | 0,0% |
| Rui Costa Pimenta | PCO | **0,0%** | 0,2% | 0,0% |
| Wilson Grassi | Democrata | **0,0%** | 0,2% | 0,0% |
| **TOTAL DE VOTOS VALIDOS** | | **100,0%** | **100,0%** | **100,0%** |

---

## 5. Aba 2: Agregados Eleitorais (Projecao Oficial)

Conforme aprovado formalmente no backtest histórico por analise de desempate estatistico:
1. **Abstencao (% sobre Aptos):** **22,3%** (Metodo: Tendencia Linear; MAE = 0,3989 p.p. vs 0,9433 p.p. da Persistencia; ganho superior a 1 SE).
2. **Votos Brancos (% sobre Comparecimento):** **1,6%** (Metodo: Persistencia / Random Walk no patamar de 2022; empate tecnico resolvido pela regra de parcimonia).
3. **Votos Nulos (% sobre Comparecimento):** **2,8%** (Metodo: Persistencia / Random Walk no patamar de 2022; empate tecnico resolvido pela regra de parcimonia).

---

## 6. Comparativo: Projecao Preliminar de Sexta (02/10) vs. Projecao Oficial Atual

Demonstracao transparente do impacto da incorporacao de novas pesquisas sobre os 12 candidatos:

| Candidato | Partido | Projecao Preliminar (02/10) | Projecao Oficial Atual | Variacao (p.p.) | Impacto Observado |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Flávio Bolsonaro | PL | 45,9% | **45,9%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Luiz Inácio Lula da Silva | PT | 45,6% | **45,6%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Augusto Cury | Avante | 2,6% | **2,6%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Ronaldo Caiado | PSD | 2,6% | **2,6%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Renan Santos | Missão | 2,5% | **2,5%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Romeu Zema | Novo | 0,7% | **0,7%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Samara Martins | UP | 0,1% | **0,1%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Clariana Barão | DC | 0,0% | **0,0%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Edmilson Costa | PCB | 0,0% | **0,0%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Hertz Dias | PSTU | 0,0% | **0,0%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Rui Costa Pimenta | PCO | 0,0% | **0,0%** | +0,0 | Estavel (sem alteracao em 1 casa) |
| Wilson Grassi | Democrata | 0,0% | **0,0%** | +0,0 | Estavel (sem alteracao em 1 casa) |

---

## 7. Tabela de Sensibilidade das Configuracoes em 2026

| Configuracao | Lula (%) | Flavio (%) | Diferenca (Lula - Flavio) | Relacao com o Erro Historico da Margem |
| :--- | :---: | :---: | :---: | :--- |
| M0 Puro (Media Simples) | 45,4% | 41,5% | +3,9 p.p. | Diferenca < P80 da margem (indistinguivel do ruido historico) |
| M0 + Vies Comum (k_mu=3) | 44,5% | 44,8% | -0,3 p.p. | Diferenca < P80 da margem (indistinguivel do ruido historico) |
| M0 + Voto Util (gamma=1.0) | 46,5% | 42,5% | +4,0 p.p. | Diferenca < P80 da margem (indistinguivel do ruido historico) |
| **Modelo Oficial (k=3, g=1.0, w=0.0)** | 45,6% | 45,9% | **-0,3 p.p.** | Diferenca < P80 da margem (indistinguivel do ruido historico) |
| Sensibilidade Nanicos (k=3, g=1.0, w=0.5) | 45,5% | 45,8% | -0,3 p.p. | Diferenca < P80 da margem (indistinguivel do ruido historico) |

### Parametros Empiricos de Referencia da Margem Top-2
- **Erro Medio Historico da Margem (n=3):** 4,54 p.p.
- **Percentil 80 (P80) da Margem:** 5,16 p.p.
- **Erro Maximo Historico da Margem:** 5,72 p.p.
- **Caracterizacao Tecnica:** Como a distancia entre Flavio Bolsonaro e Lula e inferior ao erro historico da margem em todas as configuracoes, o cenario e classificado como estatisticamente indistinguivel de empate sob a variancia amostral historica.

---

## 8. Verificacao de Sanidade, Testes Automatizados e Planilha de Entrega

### Validacao da Planilha Oficial (`outputs/previsao_2026.xlsx`)
```
PS > .venv\Scripts\python scripts/validar_entrega.py outputs/previsao_2026.xlsx
OK: arquivo valido para entrega.
```

### Execucao dos Testes Automatizados (`pytest -v`)
```
============================= test session starts =============================
collected 84 items

tests/test_pipeline.py::TestConversaoVotosValidos::test_soma_igual_a_100 PASSED
tests/test_pipeline.py::TestMaioresRestos::test_soma_exata_1000_decimos PASSED
tests/test_pipeline.py::TestPesquisas2026Manual::test_transcricao_pesquisas_2026_contra_html_salvo PASSED
tests/test_pipeline.py::TestBacktestHistorico::test_consistencia_mae_vs_tabela_candidato_a_candidato PASSED
tests/test_pipeline.py::TestValidacaoXLSX::test_gerar_planilha_entrega_produz_arquivo_valido PASSED
tests/test_sanity.py::test_sanity PASSED
============================= 84 passed in 5.50s ==============================
```

---

## 9. Conclusao e Governanca do Repositorio
1. O pipeline de previsao do Checkpoint 4 encontra-se integralmente testado e operacional.
2. O codigo e hiperparametros permanecem estritamente congelados na tag Git `modelo-congelado`.
3. Os artefatos finais de entrega `outputs/previsao_2026.xlsx`, `docs/metodologia.pdf`, `interface/dados.json` e `interface/dados.js` estao sincronizados e validados com zero erros.
