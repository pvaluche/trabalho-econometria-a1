# PROMPT: Modelo de previsão do 1º turno presidencial de 2026

## 0. PAPEL E FORMA DE TRABALHO

Você é o engenheiro principal de um projeto de previsão eleitoral com padrão de pesquisa quantitativa profissional. Trabalha em conjunto com dois papéis externos:

- **Usuário (JJ):** decide escopo, alimenta pesquisas de 2026 à mão e libera cada etapa.
- **Claude (auditor externo):** revisa métodos, números e código a cada checkpoint. Nenhuma etapa avança sem o OK do Claude repassado pelo usuário.

Seu trabalho é investigar, decidir com critério, implementar com excelência e documentar tudo de forma que um auditor que nunca viu o código entenda e confira. Você tem autonomia para resolver problemas técnicos sem pedir permissão a cada passo, mas **nunca** para alterar regras metodológicas fixadas neste prompt ou no pré-registro.

**Pasta de trabalho (Windows):**
`C:\Users\PedroValuchedeAndrad\Desktop\university\modelagem eleições`
O caminho tem espaço: sempre use aspas no PowerShell e `pathlib.Path` no Python. Nunca hardcode o caminho absoluto no código; defina a raiz uma única vez em `00_config` e derive o resto.

**Repositório GitHub:** `https://github.com/pvaluche/trabalho-econometria-a1` (privado, vazio).

**Prazo duro:** entrega no Eclass sábado 03/10/2026 às 22h. A eleição é domingo 04/10/2026.

---

## 1. O DESAFIO (fonte: edital do Desafio de Estatística e Econometria, FGV EPGE)

### Entregáveis oficiais
1. **Planilha .xlsx com exatamente 2 abas:**
   - **Aba 1:** % de votos válidos de cada um dos 12 candidatos no 1º turno, previsão pontual, somando exatamente 100,0%:
     Augusto Cury (Avante), Clariana Barão (DC), Edmilson Costa (PCB), Flávio Bolsonaro (PL), Hertz Dias (PSTU), Luiz Inácio Lula da Silva (PT), Renan Santos (Missão), Ronaldo Caiado (PSD), Romeu Zema (Novo), Rui Costa Pimenta (PCO), Samara Martins (UP), Wilson Grassi (Democrata).
   - **Aba 2:** abstenção (% do eleitorado apto), votos brancos e votos nulos (ambos % do total de votos registrados nas urnas).
2. **PDF de no máximo 2 páginas** com a metodologia, incluindo o horário de corte dos dados. O usuário escreve o texto; você gera tabelas, figuras e um rascunho técnico de apoio.

### Como será avaliado
- Métrica principal: **MAE** entre previsto e realizado nos 12 candidatos, com peso igual por candidato. Os 6 candidatos com cerca de 0 a 1% contam tanto quanto Lula e Flávio na média.
- Erro absoluto em abstenção, brancos e nulos como informação complementar.
- Critérios qualitativos: clareza da metodologia, justificativa das escolhas, uso adequado dos dados, transparência, respeito ao horário de corte.
- O próprio edital diz: estratégia simples e bem justificada pode superar modelo complexo. Use isso como princípio de projeto.

### Regra fundamental
Só pode entrar informação disponível antes do horário de corte, que fica definido em `00_config` como **sábado 03/10/2026, [HORÁRIO A DEFINIR PELO USUÁRIO]**.

---

## 2. FASE DE ENTENDIMENTO (antes de escrever código de modelo)

Antes de implementar qualquer modelo, pesquise e escreva `docs/ENTENDIMENTO.md` (máximo 2 páginas) cobrindo:

1. **Agregação de pesquisas:** média simples vs ponderada, modelos de espaço de estados. Referências para verificar e resumir: Jackman (2005), "Pooling the polls over an election campaign"; Linzer (2013), "Dynamic Bayesian forecasting of presidential elections in the states" (JASA); metodologia pública de agregadores como FiveThirtyEight e The Economist.
2. **Erro total de pesquisa e house effects:** Shirani-Mehr, Rothschild, Goel e Gelman (2018), "Disentangling bias and variance in election polls" (JASA), que mostra erro histórico bem maior que a margem declarada. Como se estima efeito de instituto e por que shrinkage é necessário com poucas eleições.
3. **Caso brasileiro:** erro das pesquisas no 1º turno de 2018 e 2022 (subestimação do candidato bolsonarista), estudos publicados na revista Opinião Pública (CESOP/Unicamp) sobre precisão de pesquisas e decisão tardia do voto, e voto útil na reta final.
4. **Validação com poucas observações:** por que leave-one-election-out, por que poucos parâmetros, por que regularização.
5. **Conclusão aplicada:** quais escolhas deste projeto decorrem de cada ponto acima.

Regras: cite só o que você conseguiu verificar; marque como "não verificado" o que não conseguiu abrir. Nunca invente referência, número ou URL.

**Isso é o Checkpoint 0** (ver seção 10).

---

## 3. DADOS

Princípios: baixar sempre da fonte original, nunca editar arquivo bruto à mão, registrar tudo no manifest.

### 3.1 Resultados oficiais (gabarito do backtest)
- TSE, Portal de Dados Abertos, 1º turno presidencial de 2006, 2010, 2014, 2018 e 2022:
  - `https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{ANO}.zip`
  - `https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_munzona/detalhe_votacao_munzona_{ANO}.zip`
- CSV com `sep=';'` e `encoding='latin-1'`. Arquivos grandes: filtre cargo Presidente e turno 1 na leitura (use `usecols` e leitura em chunks, ou `polars` com `scan_csv`).
- Agregue em nível nacional: votos por candidato, votos válidos, aptos, comparecimento, abstenção, brancos, nulos.
- Se ajudar o modelo de abstenção/brancos/nulos, inclua 1998 e 2002.
- Recalcule as taxas a partir dos dados; não copie de notícia.

### 3.2 Candidatos 2026
- `https://cdn.tse.jus.br/estatistica/sead/odsele/consulta_cand/consulta_cand_2026.zip`
- Confirme os 12 nomes do edital e verifique a situação de Leonardo Avalanche (PRTB). Se ele estiver na urna como sub judice, reporte ao usuário antes de definir a normalização dos votos válidos.

### 3.3 Pesquisas históricas (2006 a 2022)
- Fonte preferida: tabela de pesquisas eleitorais do Poder360 no Base dos Dados (pacote `basedosdados`, requer projeto no Google Cloud; se a autenticação travar, siga para a reserva sem perder tempo).
- Reserva: Wikipédia PT e EN, páginas de pesquisas de opinião da eleição presidencial de cada ano, via `pandas.read_html` ou API do MediaWiki.
- Atalhos de código (qualidade amadora, conferir antes de usar): repositórios GitHub que já raspam pesquisas de 2018 e 2022.
- Filtros obrigatórios: só cenário estimulado de 1º turno; nunca misturar espontânea ou cenários alternativos; janela das últimas 3 semanas antes de cada eleição para o backtest principal.
- Campos mínimos: instituto, data_inicio_campo, data_fim_campo, data_divulgacao (se não existir, documente a aproximação usada), amostra, % por candidato, brancos/nulos, indecisos, fonte.
- Padronize nomes de institutos (ex: Ibope e Ipec como séries distintas ou ligadas, decisão documentada).

### 3.4 Pesquisas 2026
- Arquivo `data/manual/pesquisas_2026.csv`, alimentado à mão pelo usuário, schema fixo:
  `instituto, data_inicio_campo, data_fim_campo, data_divulgacao, amostra, registro_tse, metodo_coleta, [uma coluna por candidato], brancos_nulos, indecisos, fonte_url`
- Crie o arquivo com esse schema e preencha as pesquisas nacionais de 1º turno de 22/09/2026 em diante que você conseguir verificar em fonte primária ou imprensa confiável, com `fonte_url` em cada linha.
- Divulgações previstas para sábado 03/10 (registradas no TSE): AtlasIntel, Datafolha, Futura, MDA/CNT, Palver, PoderData, Quaest. O pipeline precisa absorver essas linhas em minutos.
- PesqEle (TSE, `pesquisa_eleitoral_2026.zip`) serve só para conferir amostra, datas e registro; não tem resultados.

### 3.5 Fora do modelo
Polymarket, Google Trends, redes sociais e indicadores macro como regressores livres ficam fora. Regra do projeto: só entra no modelo o que pode ser validado no backtest histórico. Podem aparecer apenas como checagem de sanidade, explicitamente rotulada.

### 3.6 Manifest
`data/MANIFEST.csv` com: arquivo, URL de origem, data e hora do download, tamanho, SHA-256. Gerado automaticamente pelo script de download.

---

## 4. METODOLOGIA

### 4.1 Conversão para votos válidos
Excluir brancos, nulos e indecisos e renormalizar proporcionalmente, mesmo critério do TSE. Tratamento alternativo dos indecisos entra só na análise de sensibilidade.

### 4.2 Backtest leave-one-election-out
Para cada ano entre 2006 e 2022:
- parâmetros estimados apenas com as outras 4 eleições;
- só entram pesquisas com `data_divulgacao` até a véspera daquele 1º turno (o que se sabia na época, não data de campo);
- previsão comparada ao resultado oficial em votos válidos, com MAE calculado como no edital.
Reporte MAE por modelo e por eleição, MAE médio e desvio.

### 4.3 Modelos candidatos (do mais simples ao mais complexo)
- **M0, baseline:** média simples da última pesquisa de cada instituto.
- **M1:** média ponderada por recência (meia-vida em dias) e tamanho de amostra.
- **M2:** M1 com correção de house effect por instituto, estimado nas eleições de treino com shrinkage para zero (efeito de instituto com pouca história fica perto de zero).
- **M3, aprendizado de máquina cabível:** Ridge regression do resultado na urna sobre a média das pesquisas, em nível candidato x eleição, com poucas features (média das pesquisas, house effect agregado, incumbente, campo ideológico, posição no ranking). Alpha escolhido por validação interna dentro das eleições de treino, nunca olhando a eleição de teste. Justifique por que Ridge e não modelos flexíveis (gradient boosting, redes): com 5 eleições, modelo flexível memoriza o regime 2018/2022.

### 4.4 Nanicos
Prior a partir da votação histórica de candidatos de partidos pequenos no TSE (2006 a 2022), combinado com a pesquisa. MAE premia a mediana: calibre os nanicos no histórico em vez de aceitar 0% ou 1% arredondado das pesquisas. Teste no backtest se melhora o MAE.

### 4.5 Abstenção, brancos e nulos
Comparar último valor, média histórica e tendência linear, com leave-one-out. Atenção aos denominadores: abstenção sobre aptos; brancos e nulos sobre votos registrados (comparecimento). Documente fatores de 2026 (eleitorado mais velho, transporte gratuito, biometria) apenas como contexto qualitativo, salvo se houver forma de validar.

### 4.6 Rigor adicional
- **Ablation:** quanto cada componente (recência, house effect, prior dos nanicos) reduz o MAE.
- **Sensibilidade da previsão final:** janela de 2 vs 3 semanas, meia-vida, indecisos proporcional vs ajuste de voto útil para o top 2. Reporte quanto a previsão muda.
- **Incerteza:** faixa por candidato a partir do erro histórico do backtest ou bootstrap das pesquisas. Entrega é pontual, mas a faixa vai para o PDF e para a interface.
- **Arredondamento:** 1 casa decimal somando exatamente 100,0% pelo método dos maiores restos, documentado.

---

## 5. REGRAS ANTI-OVERFITTING (não negociáveis)

1. No máximo 2 hiperparâmetros por modelo, grade pequena e declarada antes.
2. Regra de escolha do modelo fixada antes de qualquer número de 2026: menor MAE médio no backtest; em empate técnico (diferença menor que o desvio entre eleições), fica o modelo mais simples.
3. Proibido calibrar só em 2022 ou ajustar o modelo depois de ver a previsão de 2026.
4. **Pré-registro:** antes de 2026 entrar no pipeline, commite `PRE_REGISTRO.md` com modelos, grades, regra de escolha e regra de arredondamento, e crie a tag `pre-registro`. O arquivo não pode ser editado depois. Qualquer desvio vai em `DECISOES.md` com justificativa.
5. Toda decisão relevante vai em `DECISOES.md`: data, decisão, alternativas consideradas, motivo.

---

## 6. FERRAMENTAS E AMBIENTE

- **Python 3.11 ou superior**, ambiente isolado com `uv` (preferido) ou `venv`. Dependências fixadas em `requirements.txt` com versões.
- **Dados:** `pandas`, `polars` (leitura dos CSVs grandes do TSE), `pyarrow` (salvar processados em Parquet), `requests`.
- **Modelagem:** `numpy`, `scikit-learn` (Ridge, validação), `statsmodels` (se precisar de regressões com inferência).
- **Visualização:** `matplotlib` para as figuras do PDF (estáticas, alta resolução, padrão visual consistente); `plotly` só se agregar na interface.
- **Saída:** `openpyxl` para o xlsx.
- **Notebooks:** Jupyter, com `papermill` para executar o pipeline completo de forma headless e reprodutível.
- **Qualidade:** `pytest` (testes), `ruff` (lint e formatação), `pre-commit` com hooks de ruff e `nbstripout` (notebooks versionados sem outputs, para diffs limpos; os resultados ficam nos relatórios e em `outputs/`).
- **Git:** `git` e, se disponível, `gh` CLI. `.gitattributes` normalizando quebras de linha (Windows), encoding UTF-8 em todos os arquivos de texto.
- **CI:** GitHub Actions rodando `ruff` e `pytest` a cada push.

Lógica reutilizável vai para `src/` (funções testadas); notebooks orquestram e mostram. Nada de lógica crítica duplicada entre notebooks.

---

## 7. ESTRUTURA DO PROJETO

```
modelagem eleições/
  data/
    raw/                 zips e CSVs originais (não versionados)
    processed/           parquet limpos
    manual/              pesquisas_2026.csv
    MANIFEST.csv
  src/
    config.py  download.py  tse.py  pesquisas.py
    conversao.py  modelos.py  backtest.py  arredondamento.py  export.py
  notebooks/
    00_config.ipynb          raiz, horário de corte, candidatos, seeds
    01_tse_historico.ipynb
    02_pesquisas.ipynb
    03_backtest.ipynb
    04_previsao_2026.ipynb
    05_abst_brancos_nulos.ipynb
    06_export.ipynb          xlsx, figuras do PDF, JSON da interface
  tests/
  interface/
    index.html
    dados.json
  reports/                   checkpoint_N.md
  docs/
    ENTENDIMENTO.md
  outputs/                   xlsx final, figuras, tabelas
  scripts/
    rodar_pipeline.ps1       executa 04 a 06 + validação em sequência
    validar_entrega.py
  PRE_REGISTRO.md  DECISOES.md  README.md
  requirements.txt  .gitignore  .gitattributes  .pre-commit-config.yaml
  .github/workflows/ci.yml
```

`scripts/rodar_pipeline.ps1` precisa rodar de ponta a ponta em poucos minutos. No sábado o usuário só atualiza `pesquisas_2026.csv` e executa esse script.

---

## 8. GIT E GITHUB

- Primeiro commit: estrutura de pastas, README inicial, `.gitignore` (Python, `data/raw/`, arquivos acima de 50 MB), `.gitattributes`, `requirements.txt`, configuração de pre-commit.
- **Commits atômicos:** um propósito por commit, código e teste juntos, nunca "atualizações gerais".
- **Mensagens no padrão Conventional Commits, em português, no imperativo:**
  `feat: adiciona coleta TSE 2006-2022`
  `data: inclui pesquisas Datafolha de 30/09`
  `fix: corrige filtro de turno na agregação`
  `test: cobre arredondamento por maiores restos`
  `docs: atualiza README com resultado do backtest`
  `refactor: move conversão para src/conversao.py`
- **Tags:** `checkpoint-0` a `checkpoint-4`, `pre-registro`, `modelo-congelado`, `entrega-final`.
- Antes de cada push: testes passando e ruff limpo.
- Nunca versionar credenciais, tokens, chaves ou dados brutos pesados; versionar os scripts que os baixam.
- Trabalhe direto em `main` com commits pequenos; não crie branches desnecessárias.

---

## 9. INTERFACE HTML (tem que ficar realmente bonita e fluida)

É a vitrine do rigor do projeto.

**Estética:** terminal de IA moderno. Fundo escuro, tipografia monoespaçada no log combinada com uma sans limpa para números e títulos, paleta contida com uma única cor de destaque, animações suaves (texto digitado no log, barras e números que preenchem com transição), microinterações nos hovers. Hierarquia visual clara e espaçamento generoso. Nada de aparência de template genérico de dashboard.

**Conteúdo, alimentado por `interface/dados.json` gerado no notebook 06:**
- Log estilo terminal com cada etapa executada, timestamp, status e link para o arquivo ou commit correspondente.
- Status da base: eleições cobertas, pesquisas por ano e por instituto, descartes e motivos.
- Backtest: tabela MAE modelo x eleição com destaque do modelo escolhido, gráfico do erro por eleição, tabela de ablation.
- Previsão 2026: barras horizontais dos 12 candidatos em votos válidos com faixa de incerteza, abstenção, brancos e nulos, horário de corte em destaque.
- Sensibilidade: quanto a previsão muda em cada variação testada.
- Pesquisas 2026 usadas, por instituto e data de divulgação.
- Status dos testes, do validador da entrega e link para o `PRE_REGISTRO.md`.

**Requisitos técnicos:** um único `index.html` autocontido (CSS e JS inline; bibliotecas só via CDN confiável, como jsdelivr ou cdnjs), funciona abrindo o arquivo direto no navegador, responsivo no celular, acessível (contraste adequado, navegação por teclado). Atualize a interface a cada checkpoint. No final, teste visualmente em larguras de desktop e celular e descreva como validou.

---

## 10. CHECKPOINTS E AUDITORIA PELO CLAUDE

Em cada checkpoint você deve, nesta ordem:
1. Rodar a auditoria do subagente revisor (seção 11).
2. Gerar `reports/checkpoint_N.md` autocontido, escrito para quem nunca viu o código, com: o que foi feito, números principais, tabelas em markdown, decisões e motivos, dúvidas em aberto, resultado da auditoria do revisor, problemas conhecidos, hash do commit.
3. Atualizar README e interface.
4. Commitar, criar a tag `checkpoint-N` e fazer push.
5. **PARAR e escrever literalmente para o usuário:**
   > "Checkpoint N concluído. Envie ao Claude para conferência: `reports/checkpoint_N.md` [e os arquivos extras listados no relatório]. Aguardando o OK do Claude antes de seguir."
6. Quando o usuário trouxer o retorno do Claude, aplique cada correção, registre em `DECISOES.md` o que mudou e por quê, e só então avance.

**Checkpoints:**
- **0. Entendimento:** `docs/ENTENDIMENTO.md` e plano de implementação.
- **1. Base TSE:** totais nacionais por ano. **Sanidade obrigatória para 2022:** Lula 48,43% e Bolsonaro 43,20% dos válidos, abstenção 20,95%. Se não bater, ache o erro antes de reportar. Inclua a série completa de abstenção, brancos e nulos.
- **2. Base de pesquisas:** pesquisas por ano e por instituto, descartes e motivos, exemplos de linhas, cobertura de `data_divulgacao`. Inclua o `pesquisas_2026.csv` inicial. Commite o `PRE_REGISTRO.md` e a tag `pre-registro` aqui, antes de qualquer previsão de 2026.
- **3. Backtest:** MAE modelo x eleição, MAE médio e desvio, ablation, modelo escolhido pela regra pré-registrada, modelo de abstenção/brancos/nulos escolhido.
- **4. Entrega:** previsão final, sensibilidade, faixas de incerteza, validação do xlsx, interface finalizada, rascunho técnico do PDF, figuras finais.

Arquivos extras pequenos que ajudam a auditoria (CSV de tabelas, PNG de figuras) devem ser listados no relatório para o usuário enviar junto.

---

## 11. SUBAGENTES

Use subagentes para paralelizar e para revisão independente:
- **Coleta TSE:** download, manifest, agregação nacional, sanidade de 2022.
- **Coleta de pesquisas históricas:** fonte, raspagem, padronização, filtros.
- **Pesquisas 2026 e candidatos:** `consulta_cand_2026`, `pesquisas_2026.csv`, conferência no PesqEle.
- **Interface:** design e implementação do `index.html`.
- **Revisor independente:** não escreve código do pipeline. Antes de cada checkpoint audita: vazamento de informação futura (pesquisa divulgada depois da véspera entrando no backtest), soma de 100,0%, denominadores de abstenção/brancos/nulos, respeito ao pré-registro, testes passando, consistência entre relatório e dados. Relatório da auditoria vai dentro do `checkpoint_N.md`.

Você integra o trabalho dos subagentes e responde pela qualidade final.

---

## 12. TESTES E VALIDAÇÃO DA ENTREGA

**pytest cobrindo no mínimo:**
- conversão para votos válidos;
- soma exata de 100,0% após arredondamento por maiores restos;
- cálculo do MAE igual ao do edital;
- filtro por `data_divulgacao` no backtest (teste com pesquisa posterior à véspera que deve ser excluída);
- normalização com e sem candidato sub judice.

**`scripts/validar_entrega.py`** abre o xlsx gerado e checa: exatamente 2 abas; nomes dos 12 candidatos idênticos ao edital; soma 100,0%; valores entre 0 e 100; abstenção, brancos e nulos presentes e plausíveis. Roda automaticamente no fim de `rodar_pipeline.ps1`.

---

## 13. README.md (atualizado a cada checkpoint)

- Resumo do projeto em 3 linhas e resultado final (previsão e MAE do modelo escolhido no backtest).
- Print ou GIF da interface no topo.
- Metodologia resumida: dados, conversão para válidos, modelos M0 a M3, backtest, regra de escolha, pré-registro.
- Como reproduzir do zero no Windows: criar ambiente, baixar dados, ordem dos notebooks, comando do pipeline final.
- Estrutura de pastas comentada.
- Horário de corte.
- Limitações conhecidas.

---

## 14. CRONOGRAMA

- **Sexta 02/10, manhã:** Checkpoint 0 e estrutura do repositório.
- **Sexta 02/10, tarde:** Checkpoints 1 e 2 (com pré-registro).
- **Sexta 02/10, noite:** Checkpoint 3, ensaio geral rodando o pipeline completo com as pesquisas disponíveis (xlsx, validação, interface), tag `modelo-congelado`.
- **Sábado 03/10:** só atualização do `pesquisas_2026.csv` conforme as pesquisas saem, execução do pipeline, Checkpoint 4. Meta: tudo pronto até 20h, entrega até 21h, uma hora de folga antes do prazo.

---

## 15. FIGURAS DO PDF

Planeje desde o início, em padrão visual único e legível impresso em preto e branco:
1. MAE por modelo x eleição no backtest (com o modelo escolhido em destaque).
2. Previsão final dos 12 candidatos com faixas de incerteza.
3. (Opcional, se couber) série histórica de abstenção, brancos e nulos com a previsão de 2026.

---

## 16. ESTILO E INTEGRIDADE

- Código limpo, tipado quando fizer sentido, comentado em português.
- **Sem travessão (—) em nenhum texto, comentário, gráfico, relatório ou na interface.**
- Se um dado não existir, não for acessível ou não puder ser verificado, diga claramente. **Nunca invente número, URL ou referência.**
- Quando houver dúvida metodológica que não esteja resolvida neste prompt, registre a dúvida no relatório do checkpoint e proponha alternativas em vez de decidir silenciosamente.

Comece pela Fase de Entendimento (Checkpoint 0) e pela estrutura do repositório.
