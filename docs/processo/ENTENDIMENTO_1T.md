# ENTENDIMENTO.md: Fundamentos Metodológicos

**Projeto:** Previsão do 1º Turno Presidencial de 2026
**Desafio:** Estatística e Econometria, FGV EPGE [confirmar professor]
**Data:** 02/10/2026 | **Versão:** Checkpoint 1 (pós-aprovação da rodada 3)

---

## 1. Agregação de Pesquisas: Abordagens e Referências

A abordagem mais simples é a **média simples** das últimas pesquisas disponíveis. Ela ignora que institutos têm vieses sistemáticos distintos e que pesquisas mais antigas carregam mais incerteza sobre o estado atual da opinião.

A **média ponderada** por recência e tamanho de amostra é o passo seguinte. O peso por recência usa decaimento exponencial com meia-vida em dias; o peso por amostra é proporcional ao tamanho (com retorno decrescente via raiz quadrada).

O estado da arte é o **modelo de espaço de estados** de Jackman (2005), que formaliza o problema em duas equações:

- *Equação de observação:* cada pesquisa é uma medição ruidosa do apoio latente verdadeiro, contaminada pelo erro amostral e pelo house effect (viés sistemático do instituto).
- *Equação de transição:* o apoio latente evolui como passeio aleatório, capturando movimentos reais da opinião ao longo da campanha.

> **Referência verificada (DOI):** Jackman, S. (2005). "Pooling the Polls Over an Election Campaign." *Australian Journal of Political Science*, 40(4), 499-517. DOI: `10.1080/10361140500302472`.

Linzer (2013) estende essa estrutura para previsão presidencial americana nos 50 estados, adicionando um prior de fundamentals econômicos que ancora a previsão no início da campanha e vai cedendo espaço às pesquisas conforme a eleição se aproxima.

> **Referência verificada (DOI):** Linzer, D. (2013). "Dynamic Bayesian Forecasting of Presidential Elections in the States." *JASA*, 108(501), 124-134. DOI: `10.1080/01621459.2012.737735`.

FiveThirtyEight usava três fatores de ponderação públicos: recência (decaimento exponencial), tamanho de amostra e rating histórico do instituto. The Economist usa partial pooling hierárquico e mean-reversion em vez de passeio aleatório puro (código aberto em github.com/TheEconomist/us-potus-model).

---

## 2. Erro Total de Pesquisa: Viés Comum vs. House Effect

Shirani-Mehr et al. (2018) analisaram 4.221 pesquisas em 608 eleições americanas (1998-2014) e documentaram que o **RMSE empírico médio é de aproximadamente 3,5 p.p.**, o dobro do erro implícito pelas margens declaradas.

> **Referência verificada (DOI):** Shirani-Mehr, H., Rothschild, D., Goel, S., e Gelman, A. (2018). "Disentangling Bias and Variance in Election Polls." *JASA*, 113(522), 607-614. DOI: `10.1080/01621459.2018.1460029`.

É fundamental distinguir dois componentes do erro:

| Componente | Definição | Magnitude (Shirani-Mehr et al.) |
|---|---|---|
| **Viés comum da eleição** | Todos os institutos erram na mesma direção numa dada eleição. Causas: modelo de eleitor provável compartilhado, dificuldades comuns de cobertura, eventos de última hora que afetam todos igualmente. | Aprox. 2 p.p. em média |
| **House effect relativo** | Viés sistemático e persistente de um instituto específico em relação ao consenso. Estimável com histórico multi-eleições. | Menor; varia por instituto |

O **modelo M2** corrige o **house effect relativo** (viés de instituto em relação ao consenso), não o viés comum da eleição. O viés comum só pode ser corrigido se existir um preditor histórico confiável validável no backtest; só entra no modelo se essa correção vencer no backtest leave-one-out.

Com poucas eleições históricas, o house effect de institutos com histórico limitado é instável. Usa-se **shrinkage para zero** (prior que puxa o efeito estimado em direção à nulidade), evitando que institutos com apenas 1 ou 2 aparições recebam correção grande baseada em ruído.

**Ibope e Ipec:** tratados como séries separadas (conservador), pois as metodologias dos dois institutos diferem. Decisão documentada em DECISOES.md; pode ser revisada no Checkpoint 3 se o backtest indicar ganho de informação em unificá-los.

---

## 3. O Caso Brasileiro: Erros em 2018 e 2022

O Brasil exibe padrão documentado de **subestimação do candidato bolsonarista** nos dois últimos 1ºs turnos. A tabela abaixo é em **votos válidos** (excluídos brancos, nulos e abstenções), mesmo critério do TSE e do edital:

| Eleição | Candidato | Datafolha (véspera, votos válidos) | Resultado TSE (votos válidos) | Erro Datafolha |
|---|---|---|---|---|
| 2018 1T | Bolsonaro | 40% | 46,03% | -6,0 p.p. |
| 2018 1T | Haddad | 25% | 29,28% | -4,3 p.p. |
| 2022 1T | Lula | **50%** | 48,43% | +1,6 p.p. |
| 2022 1T | Bolsonaro | 36% | 43,20% | -7,2 p.p. |

*Fontes: TSE (resultados oficiais); Datafolha 01/10/2022 e 06/10/2018 (confirmados via fontes jornalísticas verificadas).*

Em 2022, além do erro na subestimação de Bolsonaro (-7,2 p.p.), os **demais candidatos foram superestimados em aproximadamente 5,6 p.p. somados** (Ciro Gomes e Simone Tebet absorveram parte das intenções que migraram no voto útil). Esse fenômeno é consistente com voto útil de última hora migrando para os polos. Para 2026, a hipótese é que candidatos colocados em posições intermediárias podem sofrer perdas por voto útil em favor dos mais competitivos. **Essa hipótese será testada no backtest, não aplicada mecanicamente.**

O periódico *Opinião Pública* (CESOP/Unicamp, SciELO: scielo.br/j/op/) é o principal veículo nacional para análise de acurácia de pesquisas eleitorais; artigos específicos sobre os erros de 2018 e 2022 estão disponíveis no SciELO mas não foram verificados diretamente nesta etapa (títulos e autores não confirmados com DOI).

---

## 4. Validação com Poucas Observações

Com apenas 5 eleições de treinamento (2006-2022), o risco de overfitting é alto. Duas estratégias de validação serão utilizadas em paralelo, e qualquer divergência entre elas será reportada no Checkpoint 3:

**Leave-one-election-out (LOEO):** em cada dobra, todos os dados das 4 eleições restantes são usados para treinar, e a eleição deixada de fora é usada como teste. Não há garantia de que o treino seja anterior ao teste em termos de tempo: eleições futuras entram no treino. Isso maximiza o uso dos dados mas introduz informação do futuro.

**Expanding window (validação mais conservadora, usada para abstenção/brancos/nulos):** só eleições anteriores entram no treino, respeitando a ordem temporal:
- Teste 2014: treino com 2006-2010
- Teste 2018: treino com 2006-2014
- Teste 2022: treino com 2006-2018

**Critério pré-registrado para divergências:** se o MAE médio do expanding window do modelo escolhido pelo LOEO for maior que o MAE médio do expanding window do M0 (baseline), usa-se M0 como previsão final. Esse critério será registrado no PRE_REGISTRO.md antes de qualquer previsão de 2026.

**Modelagem de abstenção/brancos/nulos:** por ser série temporal com dependência cronológica, usa-se exclusivamente expanding window (não LOEO). Três abordagens comparadas: (a) último valor observado; (b) média histórica 2006-2022; (c) tendência linear. A que minimizar o erro médio no expanding window é escolhida e pré-registrada.

> **Referência verificada (DOI):** Vehtari, A., Gelman, A., e Gabry, J. (2017). "Practical Bayesian Model Evaluation Using LOO-CV and WAIC." *Statistics and Computing*, 27(5), 1413-1432. arXiv:1507.04544.

**Regularização:** máximo de 2 hiperparâmetros por modelo; Ridge regression no M3 (L2). Modelos flexíveis (gradient boosting, redes neurais) são excluídos: com N=5, memorizam o regime 2018/2022.

---

## 5. Conclusão Aplicada: Decisões Derivadas deste Entendimento

| Fundamento | Decisão de implementação |
|---|---|
| Jackman (2005): house effects são estimáveis e relevantes | Modelo M2 com house effect relativo e shrinkage para zero |
| Shirani-Mehr et al. (2018): viés comum maior que a margem declarada | Faixa de incerteza construída a partir dos erros empíricos do backtest (não da margem amostral declarada) |
| Erros BR 2018/2022: subestimação bolsonarista documentada | House effects estimados com dados históricos brasileiros; correção do viés comum testada no backtest |
| N=5 eleições: alto risco de overfitting | Max. 2 hiperparâmetros, Ridge, backtest LOEO + expanding window |
| LOEO usa eleições futuras no treino | Expanding window reportada em paralelo; divergências documentadas |
| Voto útil e decisão tardia: efeito real mas não quantificável | Não entra no modelo; hipótese testada no backtest para candidatos intermediários |
| MAE igual por candidato (edital): nanicos pesam tanto quanto o top-2 | Prior histórico do TSE para candidatos nanicos |
| Edital: estratégia simples bem justificada pode superar o complexo | Regra de escolha: menor MAE médio no LOEO; empate favorece o mais simples |
| Abstenção/brancos/nulos: denominadores distintos e série temporal | Expanding window exclusivamente; abstenção sobre aptos; brancos/nulos sobre comparecimento |
| Ibope vs. Ipec: metodologias distintas | Tratados como séries separadas (conservador); revisável no Checkpoint 3 |
| Faixa de incerteza: por posição relativa nas pesquisas | Grupos definidos dinamicamente pela média das pesquisas no corte: top-2, 3º-4º colocados, demais |
| Critério de fallback expanding window | Se MAE_EW(modelo_escolhido) > MAE_EW(M0), usar M0. Pré-registrado. |

**Faixa de incerteza:** construída a partir dos erros empíricos do backtest LOEO, agrupados por posição relativa na média das pesquisas na data de corte: (a) top-2 colocados; (b) 3º e 4º colocados; (c) demais candidatos (nanicos). Cada grupo tem dispersão histórica própria observada no backtest. A entrega pontual segue o edital; a faixa de incerteza consta no PDF e na interface.

---

*Documento gerado em 02/10/2026. Referências marcadas como "verificada (DOI)" foram conferidas com DOI; itens sem verificação direta estão explicitamente indicados.*
