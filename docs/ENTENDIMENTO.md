# ENTENDIMENTO.md: Fundamentos Metodologicos

**Projeto:** Previsao do 1o Turno Presidencial de 2026
**Desafio:** Estatistica e Econometria, FGV EPGE [confirmar nome do professor]
**Data:** 02/10/2026 | **Versao:** Checkpoint 0 (pos-auditoria, 2a revisao)

---

## 1. Agregacao de Pesquisas: Abordagens e Referencias

A abordagem mais simples e a **media simples** das ultimas pesquisas disponiveis. Ela ignora que institutos tem vieses sistematicos distintos e que pesquisas mais antigas carregam mais incerteza sobre o estado atual da opiniao.

A **media ponderada** por recencia e tamanho de amostra e o passo seguinte. O peso por recencia usa decaimento exponencial com meia-vida em dias; o peso por amostra e proporcional ao tamanho (com retorno decrescente via raiz quadrada).

O estado da arte e o **modelo de espaco de estados** de Jackman (2005), que formaliza o problema em duas equacoes:

- *Equacao de observacao:* cada pesquisa e uma medicao ruidosa do apoio latente verdadeiro, contaminada pelo erro amostral e pelo house effect (vies sistematico do instituto).
- *Equacao de transicao:* o apoio latente evolui como passeio aleatorio, capturando movimentos reais da opiniao ao longo da campanha.

> **Referencia verificada (DOI):** Jackman, S. (2005). "Pooling the Polls Over an Election Campaign." *Australian Journal of Political Science*, 40(4), 499-517. DOI: `10.1080/10361140500302472`.

Linzer (2013) estende essa estrutura para previsao presidencial americana nos 50 estados, adicionando um prior de fundamentals economicos que ancora a previsao no inicio da campanha e vai cedendo espaco as pesquisas conforme a eleicao se aproxima.

> **Referencia verificada (DOI):** Linzer, D. (2013). "Dynamic Bayesian Forecasting of Presidential Elections in the States." *JASA*, 108(501), 124-134. DOI: `10.1080/01621459.2012.737735`.

FiveThirtyEight usava tres fatores de ponderacao publicos: recencia (decaimento exponencial), tamanho de amostra e rating historico do instituto. The Economist usa partial pooling hierarquico e mean-reversion em vez de passeio aleatorio puro (codigo aberto em github.com/TheEconomist/us-potus-model).

---

## 2. Erro Total de Pesquisa: Vies Comum vs. House Effect

Shirani-Mehr et al. (2018) analisaram 4.221 pesquisas em 608 eleicoes americanas (1998-2014) e documentaram que o **RMSE empirico medio e de aproximadamente 3,5 p.p.**, o dobro do erro implicito pelas margens declaradas.

> **Referencia verificada (DOI):** Shirani-Mehr, H., Rothschild, D., Goel, S., e Gelman, A. (2018). "Disentangling Bias and Variance in Election Polls." *JASA*, 113(522), 607-614. DOI: `10.1080/01621459.2018.1460029`.

E fundamental distinguir dois componentes do erro:

| Componente | Definicao | Magnitude (Shirani-Mehr et al.) |
|---|---|---|
| **Vies comum da eleicao** | Todos os institutos erram na mesma direcao numa dada eleicao. Causas: modelo de eleitor provavel compartilhado, dificuldades comuns de cobertura, eventos de ultima hora que afetam todos igualmente. | Aprox. 2 p.p. em media |
| **House effect relativo** | Vies sistematico e persistente de um instituto especifico em relacao ao consenso. Estimavel com historico multi-eleicoes. | Menor; varia por instituto |

O **modelo M2** corrige o **house effect relativo** (vies de instituto em relacao ao consenso), nao o vies comum da eleicao. O vies comum so pode ser corrigido se existir um preditor historico confiavel validavel no backtest; so entra no modelo se essa correcao vencer no backtest leave-one-out.

Com poucas eleicoes historicas, o house effect de institutos com historico limitado e instavel. Usa-se **shrinkage para zero** (prior que puxa o efeito estimado em direcao a nulidade), evitando que institutos com apenas 1 ou 2 aparicoes recebam correcao grande baseada em ruido.

**Ibope e Ipec:** tratados como series separadas (conservador), pois as metodologias dos dois institutos diferem. Decisao documentada em DECISOES.md; pode ser revisada no Checkpoint 3 se o backtest indicar ganho de informacao em unifica-los.

---

## 3. O Caso Brasileiro: Erros em 2018 e 2022

O Brasil exibe padrao documentado de **subestimacao do candidato bolsonarista** nos dois ultimos 1os turnos. A tabela abaixo e em **votos validos** (excluidos brancos, nulos e abstencoes), mesmo criterio do TSE e do edital:

| Eleicao | Candidato | Datafolha (vespera, votos validos) | Resultado TSE (votos validos) | Erro Datafolha |
|---|---|---|---|---|
| 2018 1T | Bolsonaro | 40% | 46,03% | -6,0 p.p. |
| 2018 1T | Haddad | 25% | 29,28% | -4,3 p.p. |
| 2022 1T | Lula | **50%** | 48,43% | +1,6 p.p. |
| 2022 1T | Bolsonaro | 36% | 43,20% | -7,2 p.p. |

*Fontes: TSE (resultados oficiais); Datafolha 01/10/2022 e 06/10/2018 (confirmados via fontes jornalisticas verificadas com DOI ou URL publico).*

Em 2022, alem do erro na subestimacao de Bolsonaro (-7,2 p.p.), os **demais candidatos foram superestimados em aproximadamente 5,6 p.p. somados** (Ciro Gomes foi o principal, com ~3% a mais do que obteve). Esse fenomeno e consistente com voto util de ultima hora migrando para Lula. Para 2026, a hipotese e que candidatos como Caiado, Cury e Renan Santos podem ser superestimados nas pesquisas por voto util em favor dos candidatos mais competitivos. **Essa hipotese sera testada no backtest, nao aplicada mecanicamente.**

O periodico *Opiniao Publica* (CESOP/Unicamp, SciELO: scielo.br/j/op/) e o principal veiculo nacional para analise de acuracia de pesquisas eleitorais; artigos especificos sobre os erros de 2018 e 2022 estao disponiveis no SciELO mas nao foram verificados diretamente nesta etapa (titulos e autores nao confirmados com DOI).

---

## 4. Validacao com Poucas Observacoes

Com apenas 5 eleicoes de treinamento (2006-2022), o risco de overfitting e alto. Duas estrategias de validacao serao utilizadas em paralelo, e qualquer divergencia entre elas sera reportada no Checkpoint 3:

**Leave-one-election-out (LOEO):** em cada dobra, todos os dados das 4 eleicoes restantes sao usados para treinar, e a eleicao deixada de fora e usada como teste. Nao ha garantia de que o treino seja anterior ao teste em termos de tempo: eleicoes futuras entram no treino. Isso maximiza o uso dos dados mas introduz informacao do futuro.

**Expanding window (validacao mais conservadora, usada para abstencao/brancos/nulos):** so eleicoes anteriores entram no treino, respeitando a ordem temporal:
- Teste 2014: treino com 2006-2010
- Teste 2018: treino com 2006-2014
- Teste 2022: treino com 2006-2018

**Criterio pré-registrado para divergencias:** se o MAE medio do expanding window do modelo escolhido pelo LOEO for maior que o MAE medio do expanding window do M0 (baseline), usa-se M0 como previsao final. Esse criterio sera registrado no PRE_REGISTRO.md antes de qualquer previsao de 2026.

**Modelagem de abstencao/brancos/nulos:** por ser serie temporal com dependencia cronologica, usa-se exclusivamente expanding window (nao LOEO). Tres abordagens comparadas: (a) ultimo valor observado; (b) media historica 2006-2022; (c) tendencia linear. A que minimizar o erro medio no expanding window e escolhida e pre-registrada.

> **Referencia verificada (LOO-CV):** Vehtari, A., Gelman, A., e Gabry, J. (2017). "Practical Bayesian Model Evaluation Using LOO-CV and WAIC." *Statistics and Computing*, 27(5), 1413-1432. arXiv:1507.04544.

**Regularizacao:** maximo de 2 hiperparametros por modelo; Ridge regression no M3 (L2). Modelos flexiveis (gradient boosting, redes neurais) sao excluidos: com N=5, memorizam o regime 2018/2022.

---

## 5. Conclusao Aplicada: Decisoes Derivadas deste Entendimento

| Fundamento | Decisao de implementacao |
|---|---|
| Jackman (2005): house effects sao estimaveis e relevantes | Modelo M2 com house effect relativo e shrinkage para zero |
| Shirani-Mehr et al. (2018): vies comum maior que a margem declarada | Faixa de incerteza construida a partir dos erros empiricos do backtest (nao da margem amostral declarada) |
| Erros BR 2018/2022: subestimacao bolsonarista documentada | House effects estimados com dados historicos brasileiros; correcao do vies comum testada no backtest |
| N=5 eleicoes: alto risco de overfitting | Max. 2 hiperparametros, Ridge, backtest LOEO + expanding window |
| LOEO usa eleicoes futuras no treino | Expanding window reportada em paralelo; divergencias documentadas |
| Voto util e decisao tardia: efeito real mas nao quantificavel | Nao entra no modelo; hipotese testada no backtest para candidatos menores |
| MAE igual por candidato (edital): nanicos pesam tanto quanto o top-2 | Prior historico do TSE para candidatos nanicos |
| Edital: estrategia simples bem justificada pode superar o complexo | Regra de escolha: menor MAE medio no LOEO; empate favorece o mais simples |
| Abstencao/brancos/nulos: denominadores distintos e serie temporal | Expanding window exclusivamente; abstencao sobre aptos; brancos/nulos sobre comparecimento |
| Ibope vs. Ipec: metodologias distintas | Tratados como series separadas (conservador); revisavel no Checkpoint 3 |
| Faixa de incerteza: por grupo de candidatos | Top-2, 3o-4o, nanicos: cada grupo tem dispersao historica propria no backtest |
| Criterio de fallback expanding window | Se MAE_EW(modelo_escolhido) > MAE_EW(M0), usar M0. Pre-registrado. |

**Faixa de incerteza:** construida a partir dos erros empiricos do backtest LOEO, agrupados em tres faixas: (a) top-2 (Lula e Flavio Bolsonaro); (b) 3o-4o (Caiado e Zema); (c) nanicos (demais 8). Cada grupo tem dispersao historica propria. A entrega pontual segue o edital; a faixa consta no PDF e na interface.

---

*Documento gerado em 02/10/2026. Referencias marcadas como "verificada (DOI)" foram conferidas com DOI; itens sem verificacao direta estao explicitamente indicados.*
