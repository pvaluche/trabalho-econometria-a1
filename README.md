# Desafio de Estatística e Econometria (FGV EPGE 2026)

**Previsão Eleitoral: 1º Turno Presidencial de 2026**  
**Instituição:** FGV EPGE (Escola Brasileira de Economia e Finanças)  
**Integrantes:** João Pedro Valuche, Arthur Caron Lyra e Lethicia Manfioletti Possamai  
**Horário de corte:** Sábado, 03/10/2026, às 20h00 BRT  

---

## O que é o projeto

Este repositório contém o modelo econométrico quantitativo desenvolvido para o Desafio de Estatística e Econometria da FGV EPGE (2026), cujo objetivo é prever os percentuais de votos válidos para os 12 candidatos oficiais do edital e os agregados eleitorais (abstenção sobre o eleitorado apto, votos brancos sobre o comparecimento e votos nulos sobre o comparecimento) no 1º turno da Eleição Presidencial de 2026. A partir de microdados históricos do Tribunal Superior Eleitoral (2006 a 2022) e de pesquisas eleitorais registradas no PesqEle/TSE, o pipeline combina agregação causal de pesquisas por recência exponencial (modelo M1 com meia-vida calibrada em 7 dias), ajuste de viés comum sistemático, regularização com prior histórico para candidaturas de baixa intensidade amostral, fechamento proporcional estrito a 100,0% pelo método dos maiores restos (Hamilton) e modelagem de agregados via série temporal, tudo ancorado em um protocolo rígido de pré-registro com validação temporal prospectiva (expanding window) para evitar sobreajuste.

---

## Como reproduzir

### 1. Clonar o repositório e preparar o ambiente

```bash
git clone https://github.com/pvaluche/trabalho-econometria-a1.git
cd trabalho-econometria-a1

python -m venv .venv

# No Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# No Linux ou macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Executar a suíte de testes automatizados

Todos os 89 testes unitários e de integração devem passar com sucesso:

```bash
python -m pytest -v
```

### 3. Executar o corte oficial e gerar os artefatos de entrega

Para executar a esteira completa (leitura de dados, estimação do modelo oficial, geração da planilha XLSX, sincronização de macros e geração do PDF de metodologia):

```powershell
powershell -ExecutionPolicy Bypass -File scripts/rodar_corte_sabado.ps1
```

Em ambientes sem PowerShell, cada etapa pode ser executada individualmente via Python:

```bash
# 1. Gera a previsão oficial e a planilha XLSX
python src/export.py

# 2. Sincroniza os números finais para o relatório
python scripts/gerar_numeros_latex.py

# 3. Gera o PDF oficial da nota metodológica (exatamente 2 páginas)
python scripts/gerar_pdf_metodologia.py

# 4. Valida a conformidade da planilha com o edital
python scripts/validar_entrega.py outputs/previsao_2026.xlsx
```

### 4. Validar formalmente a entrega

O validador oficial confere rótulos do edital, tipos numéricos, soma exata de 100,0% e integridade dos arquivos:

```bash
python scripts/validar_entrega.py outputs/previsao_2026.xlsx
```

---

## Mapa das pastas

O repositório está organizado em torno dos quatro pilares metodológicos do projeto:

### 1. Pré-registro
- `PRE_REGISTRO.md`: Documento imutável pré-fixando os modelos candidatos (M0 a M3), grids de hiperparâmetros, função de perda oficial (MAE com peso igual entre os 12 candidatos), regras de desempate por parcimônia e emendas datadas.
- `DECISOES.md`: Caderno cronológico de registro de decisões técnicas e ata de revisões internas do grupo.

### 2. Backtest
- `src/backtest.py`: Motor econométrico de validação temporal por janelas crescentes (expanding window em 2014, 2018 e 2022), leave-one-election-out (LOEO) e cálculo de erros-padrão das diferenças empíricas de MAE.
- `notebooks/`: Cadernos interativos de análise descritiva, diagnósticos de viés institucional (house effects) e simulações.
- `reports/checkpoint_3.md`: Relatório completo com a tabela de seleção dos modelos candidatos de votos válidos e dos métodos para abstenção, brancos e nulos.

### 3. Testes
- `tests/test_pipeline.py`: Suíte de testes com cobertura para validação de formato do edital, integridade SHA-256 dos dados brutos, preservação de monotonicidade do algoritmo de Hamilton, invariância temporal dos filtros causais e verificação de conformidade do PDF de 2 páginas.
- `tests/test_sanity.py`: Teste de sanidade do ambiente de execução e dependências instaladas.

### 4. Entrega
- `outputs/previsao_2026.xlsx`: Planilha oficial pontual do edital com duas abas ("Candidatos" e "Adicionais"), formato numérico '0.0', soma fechada em 100,0% e sem campos vazios.
- `docs/metodologia.pdf`: Nota metodológica oficial em formato PDF com exatamente 2 páginas, contendo formulações matemáticas, tabelas de backtest, sensibilidade e link para o repositório público.
- `docs/metodologia.tex` e `docs/numeros_finais.tex`: Fontes em LaTeX da nota metodológica com injeção automática de macros gerados a partir da planilha oficial.
- `scripts/validar_entrega.py`: Script de validação automática contra as exigências do edital.
- `scripts/rodar_corte_sabado.ps1`: Script de orquestração do corte final de dados de sábado às 20h00 e auditoria estrita dos artefatos.

---

## Dados e rastreabilidade

- `data/raw/`: Microdados eleitorais brutos obtidos diretamente do Repositório de Dados Eleitorais do TSE.
- `data/manual/pesquisas_2026.csv`: Banco de pesquisas de 2026 auditadas com número de registro no PesqEle/TSE, data de campo, tamanho amostral e fonte primária.
- `data/MANIFEST.csv`: Manifesto de integridade com hashes criptográficos SHA-256 e timestamps de download de todas as fontes de dados.
