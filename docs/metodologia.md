# Nota Metodologica: Modelo de Previsao Eleitoral Presidencial 2026
**Desafio de Estatistica e Econometria: FGV EPGE**  
**Grupo:** Joao Pedro Valuche, Arthur Caron Lyra, Lethicia Manfioletti Possamai  
**Data:** Outubro de 2026  
**Status do Codigo:** Congelado formalmente na tag `modelo-congelado`  

---

## 1. Dados, Fontes e Pre-processamento

A base amostral congrega as pesquisas de intencao de voto para a eleicao presidencial de 2026 registradas no sistema PesqEle do Tribunal Superior Eleitoral (TSE), conduzidas por institutos de atuacao nacional (Datafolha, Quaest, AtlasIntel, PoderData e Real Time Big Data).

Para assegurar comparabilidade com o resultado oficial das urnas, os dados brutos passam por tres etapas padronizadas de pre-processamento:
1. **Filtro de Vespera e Corte:** Consideram-se exclusivamente levantamentos concluidos dentro da janela de tres semanas anteriores ao pleito, com corte definitivo as 20h00 do sabado (03/10/2026). Pesquisas sem registro valido no TSE sao descartadas.
2. **Conversao Estrita para Votos Validos:** Em consonancia com a legislacao eleitoral brasileira (art. 211 do Codigo Eleitoral), excluem-se mencoes a votos em branco, nulos e eleitores indecisos ou que nao responderam. Para cada pesquisa $j$ e candidato $i$, a intencao de votos validos e calculada como:
   $$p_{i,j} = \frac{v_{i,j}}{\sum_{k=1}^K v_{k,j}} \times 100\%$$
   onde $v_{i,j}$ e o percentual estimulado total de votos do candidato $i$ e $K=12$ representa os candidatos oficiais do edital FGV EPGE. Candidatos sub judice ou nao homologados sao expurgados.
3. **Arredondamento por Maiores Restos:** Na geracao da planilha oficial, aplica-se o metodo dos maiores restos (algoritmo de Hamilton-Hare) para arredondamento a uma casa decimal, garantindo que o somatorio dos 12 candidatos resulte exatamente em 100,0%.

---

## 2. Formulacao Matematica dos Modelos Base (M0 a M3)

Conforme pre-registrado, foram avaliadas quatro arquiteturas econometricas para agregacao das intencoes de voto na vespera:

- **M0 (Media Simples por Instituto):** Agrega a ultima pesquisa de cada instituto na vespera por media aritmetica simples:
  $$\hat{p}_i^{\text{M0}} = \frac{1}{J} \sum_{j=1}^J p_{i,j}$$
- **M1 (Ponderacao Temporal Exponencial por Recencia):** Pondera as pesquisas $j$ com base na defasagem temporal $\Delta t_j = t_{\text{eleicao}} - t_j$:
  $$\hat{p}_i^{\text{M1}} = \frac{\sum_j w_j p_{i,j}}{\sum_j w_j}, \quad w_j = \exp\left(-\frac{\ln 2}{h} \Delta t_j\right), \quad h \in \{7, 14, 21\} \text{ dias}$$
- **M2 (Ajuste de Efeito de Casa com Regularizacao Ridge / Shrinkage):** Estima o vies historico do instituto $\bar{\delta}_{i,\text{inst}}$ e aplica encolhimento bayesiano em direcao a zero:
  $$\hat{p}_i^{\text{M2}} = \sum_j w_j (p_{i,j} - \hat{\beta}_{i,\text{inst}(j)}), \quad \hat{\beta}_{i,\text{inst}} = \frac{n_{\text{inst}}}{n_{\text{inst}} + k} \bar{\delta}_{i,\text{inst}}, \quad k \in \{1, 3, 10\}$$
- **M3 (Regressao Linear Regularizada Ridge com Indicador de Incumbencia):** Modela os votos atraves de variaveis de pesquisa e status de incumbencia governista $I_i \in \{0, 1\}$:
  $$\hat{p}_i^{\text{M3}} = \mathbf{x}_i' \hat{\boldsymbol{\beta}}, \quad \hat{\boldsymbol{\beta}} = \arg\min_{\boldsymbol{\beta}} \left\{ \sum_t (y_{i,t} - \mathbf{x}_{i,t}' \boldsymbol{\beta})^2 + \alpha \|\boldsymbol{\beta}\|_2^2 \right\}, \quad \alpha \in \{0.01, 0.1, 1.0, 10.0\}$$

---

## 3. Avaliacao de Backtest Historico e Selecao de Modelos

A calibracao econometrica utilizou a serie historica das eleicoes presidenciais de 2006, 2010, 2014, 2018 e 2022. O protocolo de selecao foi conduzido em duas etapas prospectivas estritas com janela expansiva (*expanding window*), onde o treino na eleicao $t$ emprega unicamente os dados ate $t-1$. O erro e medido pelo Mean Absolute Error (MAE) sobre todos os candidatos da urna oficial apurada pelo TSE.

### Tabela 1: Backtest da Etapa 1 (Modelos Base Puros no Expanding Window)
| Modelo | 2014 (p.p.) | 2018 (p.p.) | 2022 (p.p.) | Media Exp. (p.p.) | Decisao pela Regra Pre-registrada |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **M0 Puro** | **1,3317** | **1,4964** | **0,8341** | **1,2207** | **Vencedor Etapa 1 (Menor Erro e Parcimonia)** |
| M1 (h=7d) | 1,4898 | 2,0585 | 0,9151 | 1,4878 | Rejeitado (MAE superior a M0) |
| M1 (h=14d) | 1,5142 | 2,0585 | 0,9151 | 1,4959 | Rejeitado (MAE superior a M0) |
| M1 (h=21d) | 1,5142 | 2,0585 | 0,9151 | 1,4959 | Rejeitado (MAE superior a M0) |
| M2 (k=1) | 1,4890 | 2,0601 | 0,9180 | 1,4890 | Rejeitado (MAE superior a M0) |
| M2 (k=3) | 1,5004 | 2,0594 | 0,9167 | 1,4922 | Rejeitado (MAE superior a M0) |
| M2 (k=10) | 1,5098 | 2,0588 | 0,9156 | 1,4947 | Rejeitado (MAE superior a M0) |
| M3 (alpha=0.1) | 1,4954 | 2,0585 | 0,9151 | 1,4897 | Rejeitado (MAE superior a M0) |
| M3 (alpha=1.0) | 1,5078 | 2,0585 | 0,9151 | 1,4938 | Rejeitado (MAE superior a M0) |
| M3 (alpha=10.0) | 1,5136 | 2,0585 | 0,9151 | 1,4957 | Rejeitado (MAE superior a M0) |

**Criterio de Parcimonia:** O modelo M0 Puro alcancou o menor MAE medio consolidado (1,2207 p.p. vs 1,4878 p.p. do M1). Sob a hierarquia mandatoria de parcimonia pre-registrada ($M0 \prec M1 \prec M2 \prec M3$), M0 e declarado o Modelo Base Vencedor ($M^*$).

### Avaliacao da Etapa 2: Justificativa dos Ajustes Incorporados e Rejeitados
Sobre o M0, testaram-se tres modulos de correcao comportamental:
1. **Vies Comum de Pesquisa ($k_\mu=3$):** Corrige a subestimacao sistematica de votos do polo adversario ao PT identificada nas vesperas historicas. Reduz o MAE medio em 0,1834 p.p., superando $1 \text{ SE}(\Delta) = 0,1026$ p.p. **Aprovado.**
2. **Transferencia por Voto Util ($\gamma=1.0$):** Modela a desidratacao de 3o e 4o colocados na reta final em favor dos dois ponteiros. Reduz o MAE em 0,1301 p.p., superando $1 \text{ SE}(\Delta) = 0,0889$ p.p. Em 2022, o MAE recuou para 0,5284 p.p. **Aprovado.**
3. **Efeito de Casa (House Effects):** Rejeitado. Na vespera imediata, as divergencias entre institutos decorrem primordialmente de volatilidade amostral; a regularizacao M2 nao superou a media simples.
4. **Prior de Nanicos ($w=0.5$):** Avaliado causalmente por partido historico. Obteve ganho de apenas $\bar{\Delta} = 0,0040$ p.p. com $\text{SE}(\Delta) = 0,0067$ p.p. Como $\bar{\Delta} \le \text{SE}(\Delta)$, o ganho e estatisticamente indistinguivel de zero. Documenta-se a limitacao estrutural dos levantamentos historicos, que agregavam nanicos em "outros". Em cumprimento a governanca do pre-registro, fixa-se compulsoriamente $w=0.0$ no Modelo Oficial, reservando $w=0.5$ para estudo de sensibilidade.

**Modelo Oficial Aprovado:** Combinando M0 com Vies Comum ($k_\mu=3$) e Voto Util ($\gamma=1.0$) com $w=0.0$, o MAE medio recua para **0,9640 p.p.**, alcancando reducao expressiva de $\bar{\Delta} = 0,2568$ p.p. com $\text{SE}(\Delta) = 0,0373$ p.p. (ganho superior a $6 \times \text{SE}$).

---

## 4. Analise de Sensibilidade, Moderacao da Margem e Limitacao Honesta

### Comparacao Preliminar 2026: M0 Puro vs. Modelo Oficial Aprovado
Na simulacao preliminar com as pesquisas disponiveis ate a vespera do corte:
- **M0 Puro:** Lula 45,4%, Flavio Bolsonaro 41,5% (Lula a frente por 3,9 p.p.) -> [NUMERO FINAL APOS CORTE DE SABADO].
- **Modelo Oficial Aprovado:** Flavio Bolsonaro 45,9%, Lula 45,6% (Flavio a frente por 0,3 p.p.) -> [NUMERO FINAL APOS CORTE DE SABADO].

### Por que o Modelo Oficial Modera a Margem?
O modelo oficial atua em duas frentes econometricas complementares:
1. O ajuste de vies comum reconhece que pesquisas de vespera historicamente subestimam o principal opositor ao Partido dos Trabalhadores em cerca de 2 a 3 p.p., corrigindo a pontuacao de Flavio Bolsonaro para cima.
2. O voto util transfere intencoes dos candidatos intermediarios (Augusto Cury, Renan Santos e Ronaldo Caiado) proporcionalmente para os lideres da disputa polarizada.

Como ambos os lideres recebem massa adicional de voto util, a diferenca liquida entre eles e comprimida. A vantagem projetada preliminar de 0,3 p.p. situa-se inteiramente dentro do ruido amostral historico:
- Erro Medio Historico da Margem Top-2 ($n=3$): **4,54 p.p.**
- Percentil 80 (P80) do Erro da Margem: **5,16 p.p.**
- Cota Superior Maxima do Erro: **5,72 p.p.**
Conclui-se tecnicamente que a diferenca projetada entre Lula e Flavio Bolsonaro e inferior ao erro historico da margem, configurando quadro de indefinicao estatistica estrita.

### Relato Econometrico Honesto: Limitacao no Erro da Margem em 2022
Registra-se com total transparencia uma limitacao fundamental do modelo oficial:
- Em 2022, o M0 Puro previa Lula com 46,88% e Bolsonaro com 40,35% (margem prevista de 6,53 p.p. vs. margem real do TSE de 5,23 p.p., gerando erro na margem de **1,29 p.p.**).
- O Modelo Oficial Aprovado, ao aplicar a correcao de vies comum e voto util, elevou a projecao de Bolsonaro para 44,76% (+1,57 p.p. vs. TSE) e reduziu Lula para 45,67% (-2,76 p.p. vs. TSE), resultando em margem projetada de 0,91 p.p.
- Consequentemente, o erro absoluto da margem em 2022 subiu de **1,29 p.p. no M0 para 4,32 p.p. no Modelo Oficial**.
Portanto, embora o modelo oficial reduza significativamente o MAE global de todos os candidatos da urna (de 0,8341 para 0,5819 p.p.), ele introduz o risco de sobrecorrecao na margem do Top-2 em cenarios de polarizacao atipica.

---

## 5. Aba 2: Agregados Eleitorais e Contas Formais de Desempate

Para os tres indicadores adicionais exigidos pelo edital, foram confrontadas tres abordagens em expanding window: Persistencia (Random Walk, $\hat{y}_t = y_{t-1}$), Media Movel Historica e Tendencia Linear via regressao por minimos quadrados.

1. **Abstencao (% sobre Aptos):**
   - MAE Persistencia = 0,9433 p.p. | Media Movel = 2,1669 p.p. | **Tendencia Linear = 0,3989 p.p.**
   - Desempate formal: $\bar{\Delta} = \text{MAE}_{\text{Linear}} - \text{MAE}_{\text{Persist}} = -0,5444$ p.p. com $\text{SE}(\Delta) = 0,3608$ p.p.
   - Como $|\bar{\Delta}| = 0,5444 > \text{SE}(\Delta) = 0,3608$, a superioridade da Tendencia Linear e estatisticamente significativa. Vence sem necessidade da regra de parcimonia.
   - **Projecao Oficial 2026:** **22,3%** sobre o total de eleitores aptos.

2. **Votos Brancos (% sobre Comparecimento):**
   - **MAE Persistencia = 0,9867 p.p.** | Media Movel = 0,9969 p.p. | Tendencia Linear = 1,2061 p.p.
   - Desempate formal: $\bar{\Delta} = \text{MAE}_{\text{Media}} - \text{MAE}_{\text{Persist}} = +0,0103$ p.p. com $\text{SE}(\Delta) = 0,3160$ p.p.
   - Como $|\bar{\Delta}| = 0,0103 \le \text{SE}(\Delta) = 0,3160$, configura-se empate tecnico estrito. Pela regra formal de parcimonia pre-registrada, o modelo mais simples (Persistencia / Random Walk no patamar de 2022) e selecionado.
   - **Projecao Oficial 2026:** **1,6%** sobre o total de votantes.

3. **Votos Nulos (% sobre Comparecimento):**
   - MAE Persistencia = 1,3167 p.p. | **MAE Media Movel = 1,2147 p.p.** | Tendencia Linear = 1,3989 p.p.
   - Desempate formal: $\bar{\Delta} = \text{MAE}_{\text{Media}} - \text{MAE}_{\text{Persist}} = -0,1019$ p.p. com $\text{SE}(\Delta) = 0,1429$ p.p.
   - Como $|\bar{\Delta}| = 0,1019 \le \text{SE}(\Delta) = 0,1429$, a diferenca e estatisticamente indistinguivel de zero. Pela regra mandatoria de parcimonia pre-registrada, seleciona-se a Persistencia (patamar de 2022).
   - **Projecao Oficial 2026:** **2,8%** sobre o total de votantes.

---

## 6. Protocolo de Fechamento do Corte de Sabado (Checkpoint 4)

O modelo estatistico e seus hiperparametros encontram-se congelados de forma irrevogavel na tag Git `modelo-congelado`. O corte definitivo de dados sera executado rigorosamente as **20h00 de sabado (03/10/2026)**.

Pesquisas com registro homologado no PesqEle previstas para divulgacao no sabado:
- **Datafolha:** `BR-01708/2026` (amostra de 4.006 eleitores)
- **Quaest:** `BR-02197/2026` (amostra de 3.702 eleitores)
- **AtlasIntel:** `BR-00999/2026` (amostra de 5.000 eleitores)
- **PoderData:** `BR-03519/2026` (amostra de 4.000 eleitores)
- **Real Time Big Data:** `BR-01068/2026` (amostra de 2.000 eleitores)

Caso qualquer levantamento nao seja publicado ate as 20h00, o motivo sera registrado no relatorio final e o pipeline processara a projecao com as pesquisas efetivamente publicadas. Os numeros finais substituirao os marcadores `[NUMERO FINAL]` na entrega oficial `outputs/previsao_2026.xlsx`.
