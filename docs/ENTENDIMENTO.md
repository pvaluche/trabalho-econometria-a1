# ENTENDIMENTO.md — Fundamentos Metodológicos

**Projeto:** Previsão do 1º Turno Presidencial de 2026
**Data:** 02/10/2026 | **Versão:** Checkpoint 0

---

## 1. Agregação de Pesquisas: Abordagens e Referências

### Média simples vs. ponderada vs. modelos de espaço de estados

A abordagem mais ingênua é a **média simples** das últimas pesquisas disponíveis. Ela ignora que institutos têm vieses sistemáticos distintos e que pesquisas mais antigas carregam mais incerteza sobre o estado atual da opinião.

A **média ponderada** por recência e tamanho de amostra é o passo natural seguinte. O peso por recência usa decaimento exponencial com meia-vida em dias; o peso por amostra é proporcional ao tamanho (com retorno decrescente, idealmente via raiz quadrada).

O estado da arte é o **modelo de espaço de estados** de Jackman (2005), que formaliza o problema em duas equações:

- *Equação de observação:* cada pesquisa é uma medição ruidosa do apoio latente verdadeiro, contaminada pelo erro amostral e pelo *house effect* (viés sistemático do instituto).
- *Equação de transição:* o apoio latente evolui como passeio aleatório, capturando movimentos reais da opinião ao longo da campanha.

> **Referência verificada:** Jackman, S. (2005). "Pooling the Polls Over an Election Campaign." *Australian Journal of Political Science*, 40(4), 499–517. DOI: `10.1080/10361140500302472`.

Linzer (2013) estende essa estrutura para previsão presidencial americana nos 50 estados, adicionando um *prior* de fundamentals econômicos (incumbência, crescimento do PIB) que ancora a previsão no início da campanha e vai cedendo espaço às pesquisas conforme a eleição se aproxima.

> **Referência verificada:** Linzer, D. (2013). "Dynamic Bayesian Forecasting of Presidential Elections in the States." *JASA*, 108(501), 124–134. DOI: `10.1080/01621459.2012.737735`.

FiveThirtyEight (encerrado em 2025) usava três fatores de ponderação públicos: recência (decaimento exponencial), tamanho de amostra e rating histórico do instituto. The Economist (código aberto em github.com/TheEconomist/us-potus-model) usa *partial pooling* hierárquico e *mean-reversion* em vez de passeio aleatório puro.

---

## 2. Erro Total de Pesquisa e House Effects

Shirani-Mehr et al. (2018) analisaram 4.221 pesquisas em 608 eleições americanas (1998–2014) e documentaram que o **RMSE empírico médio é de ~3,5 p.p.** — aproximadamente o dobro do erro implícito pelas margens declaradas.

A decomposição revelou dois componentes:

| Componente | Magnitude |
|---|---|
| Viés em nível de eleição (*election-level bias*) | ~2 p.p. em média |
| Variância amostral excedente | Significativamente > amostragem aleatória simples |

O mecanismo central é a **correlação positiva entre pesquisas de uma mesma eleição**: institutos distintos erram na mesma direção porque compartilham modelos similares de "eleitor provável" e dificuldades comuns em atingir subgrupos (e.g., trabalhadores rurais, celular-only). Isso implica que agregar muitas pesquisas *não* reduz a incerteza tão drasticamente quanto a teoria i.i.d. prevê.

> **Referência verificada:** Shirani-Mehr, H., Rothschild, D., Goel, S., & Gelman, A. (2018). "Disentangling Bias and Variance in Election Polls." *JASA*, 113(522), 607–614. DOI: `10.1080/01621459.2018.1460029`.

**House effects** são vieses sistemáticos de cada instituto, estimáveis a partir de eleições passadas. Com poucas eleições históricas, a estimativa de house effect para institutos com histórico limitado é instável — daí a necessidade de **shrinkage para zero** (prior que puxa o efeito estimado em direção à nulidade).

---

## 3. O Caso Brasileiro: Erros de 2018 e 2022

O Brasil apresenta um padrão documentado de **subestimação do candidato bolsonarista** nos dois últimos 1ºs turnos:

| Eleição | Candidato | Datafolha final | Resultado TSE | Erro |
|---|---|---|---|---|
| 2018 1T | Bolsonaro | 40% | **46,03%** | **−6 p.p.** |
| 2018 1T | Haddad | 25% | **29,28%** | **−4 p.p.** |
| 2022 1T | Bolsonaro | ~36% | **43,20%** | **~−7 p.p.** |
| 2022 1T | Lula | ~48% | **48,43%** | **~0 p.p.** |

*Fontes: TSE (resultados oficiais), Datafolha (pesquisas divulgadas na véspera).*

Os fatores discutidos na literatura e na imprensa especializada incluem: o fenômeno do *shy voter* (eleitores relutantes em declarar preferência a pesquisadores), dificuldades de modelagem do eleitor provável em eleitorados polarizados, subestimação do comparecimento no interior e na zona rural, e migração tardia de voto (voto útil pró-Lula em 2022 esvaziando Ciro Gomes; voto útil pró-Bolsonaro em 2018 drenando candidatos menores da direita).

O *Opinião Pública* (CESOP/Unicamp, SciELO: scielo.br/j/op/) é o principal periódico nacional que publica avaliações de acurácia de pesquisas eleitorais. Artigos usando frameworks como Mosteller's Method 3 e o ESEB (Estudo Eleitoral Brasileiro) estão disponíveis no SciELO, mas títulos e autores específicos dos artigos sobre 2018/2022 não foram verificados diretamente nesta etapa.

**Implicação para o modelo:** o viés histórico sistemático justifica estimar house effects com os dados brasileiros. Dado que o erro de 2022 foi o maior e mais recente, há risco de o modelo superponderar este regime — o que o backtest leave-one-out captura e protege.

---

## 4. Validação com Poucas Observações

Com apenas 5 eleições de treinamento (2006–2022), cada parâmetro adicional no modelo corre alto risco de overfitting. As estratégias adotadas:

**Leave-one-election-out (LOEO):** maximiza o uso dos dados (usa 4 das 5 eleições em cada dobra) e testa previsão genuinamente fora da amostra. Preserva a ordem temporal (a eleição de teste é sempre posterior ou separada das de treino em termos de uso de informação).

**Poucos parâmetros e regularização:** máximo de 2 hiperparâmetros por modelo; Ridge regression no M3 (regularização L2 que não zera coeficientes, adequada quando todas as features são teoricamente relevantes). Modelos flexíveis como gradient boosting são explicitamente excluídos — com N=5, memorizariam o regime 2018/2022.

> **Referência verificada (LOO-CV):** Vehtari, A., Gelman, A., & Gabry, J. (2017). "Practical Bayesian Model Evaluation Using LOO-CV and WAIC." *Statistics and Computing*, 27(5), 1413–1432. arXiv:1507.04544.

**Grade de hiperparâmetros declarada no pré-registro** antes de qualquer dado de 2026 entrar no pipeline — condição necessária para que a validação seja crível.

---

## 5. Conclusão Aplicada: Decisões Derivadas deste Entendimento

| Fundamento teórico | Decisão de implementação |
|---|---|
| Jackman (2005): house effects são estimáveis e relevantes | Modelo M2 com shrinkage para zero |
| Shirani-Mehr et al. (2018): erro real >> margem declarada | Faixa de incerteza inflada além da margem amostral |
| Erros BR 2018/2022: viés sistemático documentado | House effects estimados com dados históricos brasileiros |
| N=5 eleições: alto risco de overfitting | Máximo 2 hiperparâmetros, ridge, backtest LOEO |
| Voto útil e decisão tardia: efeito real mas difícil de quantificar | Não entra no modelo; documentado como limitação |
| MAE igual por candidato (edital): nanicos pesam tanto quanto top-2 | Prior histórico do TSE para nanicos, M4.4 |
| Edital: modelo simples bem justificado pode superar o complexo | Regra de escolha: menor MAE médio no backtest; empate favorece o mais simples |

---

*Documento gerado em 02/10/2026 para o Checkpoint 0. Referências marcadas como "não verificado" neste documento devem ser tratadas como ausentes para fins de citação formal.*
